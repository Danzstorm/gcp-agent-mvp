variable "project_id" {
  description = "ID del proyecto GCP existente"
  type        = string
}

variable "region" {
  description = "Región para Cloud Run, Scheduler, Artifact Registry"
  type        = string
  default     = "us-central1"
}

variable "bq_location" {
  description = "Ubicación de los datasets BigQuery"
  type        = string
  default     = "US"
}

variable "raw_dataset" {
  description = "Dataset de landing (raw)"
  type        = string
  default     = "coingecko_raw"
}

variable "curated_dataset" {
  description = "Dataset servido al agente (curated)"
  type        = string
  default     = "coingecko_curated"
}

variable "landing_bucket_name" {
  description = "Bucket GCS de landing (global único). Default deriva del project_id."
  type        = string
  default     = "airflow-pipeline-project-coingecko-raw"
}

variable "raw_retention_days" {
  description = "Días antes de borrar NDJSON crudo del landing (0 = nunca)"
  type        = number
  default     = 90
}

variable "ohlc_top_n" {
  description = "Nº de monedas para OHLC/metadata en el job daily"
  type        = number
  default     = 50
}
