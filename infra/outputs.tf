// outputs.tf
// Värden som Azure bestämmer.

output "frontend_url" {
  description = "Public Address To Dashboard."
  value       = "https://${azurerm_container_app.frontend.ingress[0].fqdn}"
}

output "backend_url" {
  description = "Public Address to API. /docs and /health is here."
  value       = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
}
