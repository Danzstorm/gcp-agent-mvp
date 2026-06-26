variable "project_id" {
  type = string
}

variable "bq_location" {
  type    = string
  default = "US"
}

variable "raw_dataset" {
  type    = string
  default = "coingecko_raw"
}

variable "curated_dataset" {
  type    = string
  default = "coingecko_curated"
}

# delete_contents_on_destroy = true → permite `terraform destroy` aunque el dataset
# tenga tablas/datos. Imprescindible para desmontar el MVP sin pasos manuales.

resource "google_bigquery_dataset" "raw" {
  project                    = var.project_id
  dataset_id                 = var.raw_dataset
  location                   = var.bq_location
  description                = "Landing de CoinGecko (raw, append, particionado)."
  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "curated" {
  project                    = var.project_id
  dataset_id                 = var.curated_dataset
  location                   = var.bq_location
  description                = "Capa curated servida al agente (vistas en MVP)."
  delete_contents_on_destroy = true
}

# --- Tablas raw ---

# Tablas "documento": payload JSON crudo + ingestion_time. Particionadas por día.
locals {
  document_tables = ["coin_markets", "market_global", "trending", "coin_metadata"]
  document_schema = jsonencode([
    { name = "ingestion_time", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "payload", type = "JSON", mode = "NULLABLE" },
  ])
}

resource "google_bigquery_table" "documents" {
  for_each = toset(local.document_tables)

  project             = var.project_id
  dataset_id          = google_bigquery_dataset.raw.dataset_id
  table_id            = each.value
  schema              = local.document_schema
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "ingestion_time"
  }
}

# Tabla OHLC: estructurada.
resource "google_bigquery_table" "coin_ohlc" {
  project             = var.project_id
  dataset_id          = google_bigquery_dataset.raw.dataset_id
  table_id            = "coin_ohlc"
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "ingestion_time"
  }

  schema = jsonencode([
    { name = "ingestion_time", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "coin_id", type = "STRING", mode = "REQUIRED" },
    { name = "open_time", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "open", type = "FLOAT64", mode = "NULLABLE" },
    { name = "high", type = "FLOAT64", mode = "NULLABLE" },
    { name = "low", type = "FLOAT64", mode = "NULLABLE" },
    { name = "close", type = "FLOAT64", mode = "NULLABLE" },
  ])
}

output "raw_dataset_id" {
  value = google_bigquery_dataset.raw.dataset_id
}

output "curated_dataset_id" {
  value = google_bigquery_dataset.curated.dataset_id
}
