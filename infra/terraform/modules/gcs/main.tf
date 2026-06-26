variable "project_id" {
  type = string
}

variable "bucket_location" {
  description = "Ubicación del bucket. Debe ser compatible con la location del dataset BQ (US)."
  type        = string
  default     = "US"
}

variable "landing_bucket_name" {
  description = "Nombre del bucket de landing (global único)."
  type        = string
}

variable "raw_retention_days" {
  description = "Días antes de borrar objetos raw del landing (0 = sin lifecycle)."
  type        = number
  default     = 90
}

# Landing zone: NDJSON crudo de CoinGecko antes de cargar a BigQuery.
# force_destroy=true + versioning OFF → terraform destroy borra el bucket aunque tenga objetos.
resource "google_storage_bucket" "landing" {
  project                     = var.project_id
  name                        = var.landing_bucket_name
  location                    = var.bucket_location
  force_destroy               = true
  uniform_bucket_level_access = true

  versioning {
    enabled = false
  }

  dynamic "lifecycle_rule" {
    for_each = var.raw_retention_days > 0 ? [1] : []
    content {
      condition {
        age = var.raw_retention_days
      }
      action {
        type = "Delete"
      }
    }
  }
}

output "landing_bucket" {
  value = google_storage_bucket.landing.name
}

output "landing_bucket_url" {
  value = google_storage_bucket.landing.url
}
