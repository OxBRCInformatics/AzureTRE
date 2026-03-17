terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 4.57.0"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "= 2.3.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "= 2.6.1"
    }
  }
  backend "azurerm" {
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy               = false
      purge_soft_deleted_secrets_on_destroy      = false
      purge_soft_deleted_certificates_on_destroy = false
      purge_soft_deleted_keys_on_destroy         = false
      recover_soft_deleted_key_vaults   = true
      recover_soft_deleted_secrets      = true
      recover_soft_deleted_certificates = true
      recover_soft_deleted_keys         = true
    }
  }
  storage_use_azuread = true
}

module "terraform_azurerm_environment_configuration" {
  source          = "git::https://github.com/microsoft/terraform-azurerm-environment-configuration.git?ref=0.2.0"
  arm_environment = var.arm_environment
}