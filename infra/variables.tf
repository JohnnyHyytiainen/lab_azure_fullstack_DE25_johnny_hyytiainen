// variables.tf
// En variabel är ett namngivet värde med en TYP.
// Värdet är menat stå på ETT ställe och att fel typ upptäcks direkt vid PLAN
// istället för att upptäcka det felet halvvägs in i apply.


variable "location" {
  description = "Azure-region MÅSTE vara en av mina fem regioner som mitt student account tillåter."
  type        = string
  default     = "swedencentral"
}

variable "resource_group_name" {
  description = "Resursgruppen som äger ALLT annat."
  type        = string
  default     = "rg-eclipsebord"
}

variable "registry_name" {
  description = "ACR namnet. Blir ett 'värdnamn'(hostname) som är globalt unikt och inte bara alfanumeriskt."
  type        = string
  default     = "eclipsebordjh"
}
