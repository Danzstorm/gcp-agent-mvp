terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  # MVP: estado local. Migrar a backend GCS cuando se quiera colaboración/CI.
  # backend "gcs" {
  #   bucket = "<PROJECT_ID>-tfstate"
  #   prefix = "gcp-agent-mvp"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
