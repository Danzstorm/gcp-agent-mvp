variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "image" {
  type = string
}

variable "ingest_sa_email" {
  type = string
}

variable "landing_bucket" {
  type = string
}

variable "raw_dataset" {
  type    = string
  default = "coingecko_raw"
}

variable "ohlc_top_n" {
  type    = number
  default = 50
}

variable "secret_id" {
  type    = string
  default = "coingecko-api-key"
}

locals {
  modes = {
    hourly = "hourly"
    daily  = "daily"
  }
}

resource "google_cloud_run_v2_job" "ingest" {
  for_each = local.modes

  name                = "coingecko-ingest-${each.key}"
  location            = var.region
  project             = var.project_id
  deletion_protection = false

  template {
    template {
      service_account = var.ingest_sa_email
      max_retries     = 1
      timeout         = "1800s"

      containers {
        image = var.image
        args  = ["--mode", each.value]

        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
        env {
          name  = "LANDING_BUCKET"
          value = var.landing_bucket
        }
        env {
          name  = "RAW_DATASET"
          value = var.raw_dataset
        }
        env {
          name  = "OHLC_TOP_N"
          value = tostring(var.ohlc_top_n)
        }
        env {
          name = "COINGECKO_API_KEY"
          value_source {
            secret_key_ref {
              secret  = var.secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }
}

output "job_names" {
  value = { for k, j in google_cloud_run_v2_job.ingest : k => j.name }
}
