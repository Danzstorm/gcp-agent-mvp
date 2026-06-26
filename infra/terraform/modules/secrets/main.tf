variable "project_id" {
  type = string
}

variable "secret_id" {
  type    = string
  default = "coingecko-api-key"
}

# Contenedor del secreto. El VALOR (versión) lo inyecta el usuario fuera de Terraform
# para que la API key nunca quede en el código ni en el state:
#   printf '%s' 'CG-xxxx' | gcloud secrets versions add coingecko-api-key --data-file=-
resource "google_secret_manager_secret" "coingecko" {
  project   = var.project_id
  secret_id = var.secret_id

  replication {
    auto {}
  }
}

output "secret_id" {
  value = google_secret_manager_secret.coingecko.secret_id
}
