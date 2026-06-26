variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "repo_id" {
  type    = string
  default = "coingecko"
}

resource "google_artifact_registry_repository" "repo" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repo_id
  format        = "DOCKER"
  description   = "Imágenes del job de ingesta CoinGecko"
}

output "repo_id" {
  value = google_artifact_registry_repository.repo.repository_id
}

# URL base para taggear imágenes: <region>-docker.pkg.dev/<project>/<repo>
output "image_base" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}"
}
