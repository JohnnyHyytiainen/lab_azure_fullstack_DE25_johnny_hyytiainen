// providers.tf - Terraform kan ingenting om Azure, eller resource groups
// En provider är menat vara den som översätter. azurerm är ett separat program som terraform tankar ner
// som vet hur azurerm_resource_group blir anrop mot Azures API. Byter jag provider(AWS eller GCP) byter jag 
// bara ut providern och inte Terraform.

terraform {
  required_version = ">= 1.9"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.0"
    }
  }
}

// TOMT features-block är obligatorskt
provider "azurerm" {
  features {}
}
