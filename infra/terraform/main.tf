# Orquestación raíz. Cada bloque de infra vive en un módulo bajo modules/.
# En Fase 0 solo se habilitan las APIs; el resto se va activando por fase.

module "apis" {
  source     = "./modules/apis"
  project_id = var.project_id
}

# --- Activar por fase (descomentar a medida que se avanza) ---

module "artifact_registry" {
  source     = "./modules/artifact_registry"
  project_id = var.project_id
  region     = var.region
  depends_on = [module.apis]
}

module "iam" {
  source         = "./modules/iam"
  project_id     = var.project_id
  landing_bucket = var.landing_bucket_name
  depends_on     = [module.apis, module.gcs, module.secrets]
}

module "gcs" {
  source              = "./modules/gcs"
  project_id          = var.project_id
  bucket_location     = var.bq_location
  landing_bucket_name = var.landing_bucket_name
  raw_retention_days  = var.raw_retention_days
  depends_on          = [module.apis]
}

module "bigquery" {
  source          = "./modules/bigquery"
  project_id      = var.project_id
  bq_location     = var.bq_location
  raw_dataset     = var.raw_dataset
  curated_dataset = var.curated_dataset
  depends_on      = [module.apis]
}

module "secrets" {
  source     = "./modules/secrets"
  project_id = var.project_id
  depends_on = [module.apis]
}

module "curated" {
  source          = "./modules/curated"
  project_id      = var.project_id
  curated_dataset = var.curated_dataset
  raw_dataset     = var.raw_dataset
  sql_dir         = "${path.root}/../../transform/sql"
  depends_on      = [module.bigquery]
}

module "cloudrun_job" {
  source          = "./modules/cloudrun_job"
  project_id      = var.project_id
  region          = var.region
  image           = "${module.artifact_registry.image_base}/ingest:latest"
  ingest_sa_email = module.iam.ingest_sa_email
  landing_bucket  = var.landing_bucket_name
  raw_dataset     = var.raw_dataset
  ohlc_top_n      = var.ohlc_top_n
  depends_on      = [module.apis, module.artifact_registry, module.iam]
}

module "scheduler" {
  source             = "./modules/scheduler"
  project_id         = var.project_id
  region             = var.region
  scheduler_sa_email = module.iam.scheduler_sa_email
  job_names          = module.cloudrun_job.job_names
  depends_on         = [module.apis, module.cloudrun_job]
}
