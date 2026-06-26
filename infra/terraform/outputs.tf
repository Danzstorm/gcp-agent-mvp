output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "enabled_services" {
  value = module.apis.enabled_services
}
