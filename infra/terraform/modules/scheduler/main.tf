variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "scheduler_sa_email" {
  type = string
}

variable "job_names" {
  description = "Mapa modo → nombre del Cloud Run Job"
  type        = map(string)
}

locals {
  # Cron en UTC. Hourly al minuto 0; daily a las 06:00 UTC.
  crons = {
    hourly = "0 * * * *"
    daily  = "0 6 * * *"
  }
}

resource "google_cloud_scheduler_job" "trigger" {
  for_each = var.job_names

  name      = "coingecko-ingest-${each.key}"
  project   = var.project_id
  region    = var.region
  schedule  = local.crons[each.key]
  time_zone = "Etc/UTC"

  attempt_deadline = "320s"

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/v2/projects/${var.project_id}/locations/${var.region}/jobs/${each.value}:run"

    oauth_token {
      service_account_email = var.scheduler_sa_email
    }
  }
}
