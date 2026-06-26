variable "project_id" {
  type = string
}

variable "secret_id" {
  type    = string
  default = "coingecko-api-key"
}

variable "landing_bucket" {
  type = string
}

# --- Service account de runtime del Cloud Run Job (ingesta) ---
resource "google_service_account" "ingest" {
  project      = var.project_id
  account_id   = "ingest-sa"
  display_name = "CoinGecko ingest job runtime"
}

# Cargar a BigQuery (escribir tablas + lanzar load jobs)
resource "google_project_iam_member" "ingest_bq_data" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.ingest.email}"
}

resource "google_project_iam_member" "ingest_bq_jobs" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.ingest.email}"
}

# Escribir NDJSON al bucket de landing (scoped al bucket)
resource "google_storage_bucket_iam_member" "ingest_gcs" {
  bucket = var.landing_bucket
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.ingest.email}"
}

# Leer la API key del secreto (scoped al secreto)
resource "google_secret_manager_secret_iam_member" "ingest_secret" {
  project   = var.project_id
  secret_id = var.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ingest.email}"
}

# --- Service account para Cloud Scheduler (dispara la ejecución del job) ---
resource "google_service_account" "scheduler" {
  project      = var.project_id
  account_id   = "scheduler-sa"
  display_name = "Cloud Scheduler → Cloud Run Job invoker"
}

# Permite ejecutar Cloud Run Jobs (run.jobs.run)
resource "google_project_iam_member" "scheduler_run" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.scheduler.email}"
}

output "ingest_sa_email" {
  value = google_service_account.ingest.email
}

output "scheduler_sa_email" {
  value = google_service_account.scheduler.email
}
