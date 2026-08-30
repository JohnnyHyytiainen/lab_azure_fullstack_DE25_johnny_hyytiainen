// registry.tf
// tf script för mina resource groups och registrys

// RESURSGRUPPEN
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

// CONTAINER REGISTRY
// inget admin password, körmiljön får en egen identitet i apps.tf istället så admin pw behövs ej här.
resource "azurerm_container_registry" "acr" {
  name                = var.registry_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  sku = "Basic"

  admin_enabled = false
}
