variable "project_id" {
  type = string
}

variable "curated_dataset" {
  type = string
}

variable "raw_dataset" {
  type = string
}

variable "sql_dir" {
  description = "Ruta al directorio con los .sql de las vistas curated"
  type        = string
}

locals {
  raw_ref = "${var.project_id}.${var.raw_dataset}"
  views   = ["dim_coin", "latest_prices", "ohlc_timeseries", "market_global_daily"]
}

# Cada vista lee su .sql (parametrizado con la ref del dataset raw).
resource "google_bigquery_table" "view" {
  for_each = toset(local.views)

  project             = var.project_id
  dataset_id          = var.curated_dataset
  table_id            = each.value
  deletion_protection = false

  view {
    query          = templatefile("${var.sql_dir}/${each.value}.sql", { raw = local.raw_ref })
    use_legacy_sql = false
  }
}

output "view_ids" {
  value = [for v in google_bigquery_table.view : v.table_id]
}
