// apps.tf
// Fem resurser, ordningen under är för MIG som reader att läsa, Terraform läser dom ur referenserna och INTE ur filen.


// ===== IDENTITETEN =====
// Identitet utan lösenord, fristående.
// appen behöver rollen för att starta, rollen behöver identiteten.
resource "azurerm_user_assigned_identity" "apps" {
  name                = "id-eclipsebord"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

// ===== ROLL TILLDELNING =====
// den här identiteten får dra images ur det HÄR registret. Inget mer.
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.apps.principal_id
}

// ===== MILJÖ =====
// Motsvarighet till compose. Ingen log_analytics_workspace_id
// utan den blir logg läget 'streaming only', dvs en resurs mindre och NOLL kostnad.
resource "azurerm_container_app_environment" "main" {
  name                = "cae-eclipsebord"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

// ===== BACKEND =====
resource "azurerm_container_app" "backend" {
  name                         = "backend"
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id

  # Single = all trafik går direkt till senaste revisionen.
  revision_mode = "Single"
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.apps.id]
  }

  registry {
    server   = azurerm_container_registry.acr.login_server
    identity = azurerm_user_assigned_identity.apps.id
  }

  template {
    container {
      name   = "backend"
      image  = "${azurerm_container_registry.acr.login_server}/backend:v1"
      cpu    = 0.5
      memory = "1Gi"
    }
    # Inga repliker när ingen använder appen = ingen kostnad.
    min_replicas = 0
    max_replicas = 1
  }

  ingress {
    external_enabled = true
    target_port      = 8000

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
  depends_on = [azurerm_role_assignment.acr_pull]
}


// ===== FRONTEND =====
resource "azurerm_container_app" "frontend" {
  name                         = "frontend"
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.apps.id]
  }

  registry {
    server   = azurerm_container_registry.acr.login_server
    identity = azurerm_user_assigned_identity.apps.id
  }

  template {
    container {
      name   = "frontend"
      image  = "${azurerm_container_registry.acr.login_server}/frontend:v1"
      cpu    = 0.5
      memory = "1Gi"

      // Den här ENV raden är kritiskt och ÄR HELA DEPLOYEN
      // Samma image som används i compose, samma image som lokalt. Enda skillnaden
      // DEN ENDA SKILLNADEN: är värdet här. Och eftersom den LÄSER backends fqdn,
      // backend skapas före frontend, utan att någon sagt det tack vare att terraform är smart.
      env {
        name  = "BACKEND_URL"
        value = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
      }
    }

    min_replicas = 0
    max_replicas = 1
  }

  ingress {
    external_enabled = true
    target_port      = 8501

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  depends_on = [azurerm_role_assignment.acr_pull]
}
