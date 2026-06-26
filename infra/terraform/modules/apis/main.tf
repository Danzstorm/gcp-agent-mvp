variable "project_id" {
  type = string
}

# APIs necesarias para todo el stack del MVP.
locals {
  services = [
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "run.googleapis.com",
    "cloudscheduler.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "aiplatform.googleapis.com",          # Vertex AI
    "geminidataanalytics.googleapis.com", # Conversational Analytics API
    "iam.googleapis.com",
  ]
}

resource "google_project_service" "enabled" {
  for_each = toset(local.services)

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

output "enabled_services" {
  value = [for s in google_project_service.enabled : s.service]
}
