# CLAUDE.md — gcp-agent-mvp

Guía para trabajar en este repo de forma ordenada y precisa.

## Qué es

Pipeline CoinGecko → BigQuery → Agente Q&A (Gemini/Vertex nativo). Ver `README.md` y el plan
en `docs/superpowers/specs/`.

## Convenciones GCP

- **PROJECT_ID**: `airflow-pipeline-project` (definido en `infra/terraform/terraform.tfvars`)
- **REGION**: `us-central1`
- **BigQuery location**: `US` (multi-región)
- **GCS landing**: `gs://airflow-pipeline-project-coingecko-raw` (NDJSON crudo, replay)
- **Datasets**: `coingecko_raw` (tablas nativas, cargadas vía bq load desde GCS), `coingecko_curated` (servido al agente)
- **Flujo**: CoinGecko → NDJSON a GCS → `bq load` → `coingecko_raw` → vistas `coingecko_curated`
- **Service accounts**: `ingest-sa` (Cloud Run Job), `agent-sa` (lectura BQ para el agente)
- **Naming**: recursos prefijados `coingecko-` / `cg-`

## Reglas de seguridad (estrictas)

- NUNCA commitear credenciales, keys, ni `*.tfvars` (ver `.gitignore`).
- La API key de CoinGecko va SOLO a Secret Manager. Jamás en código, env de repo, ni chat.
- Auth GCP vía ADC: `gcloud auth application-default login`.
- IAM con mínimo privilegio: cada SA solo los roles que necesita.

## Convenciones de teardown (desmontar limpio)

- Backend Terraform **local** (sin bucket de state).
- BigQuery datasets con `delete_contents_on_destroy = true`.
- Cualquier bucket GCS futuro: `force_destroy = true` y **versioning desactivado**.
- Toda la IaC dentro de `infra/` → un solo `terraform apply` / `terraform destroy`.

## Flujo de trabajo (superpowers)

brainstorm → spec → plan → ejecución TDD → verificación. Documentar cada fase en `docs/phases/`.
- Tests primero en `ingestion/` (`pytest`, vía `uv`).
- Verificar cada fase antes de marcarla completa (datos reales en BQ, no solo "corre").

## Comandos

```bash
# Auth (interactivo — correr en terminal del usuario)
gcloud auth login
gcloud auth application-default login
gcloud config set project <PROJECT_ID>

# Infra
cd infra/terraform && terraform init && terraform plan && terraform apply

# Tests ingesta
cd ingestion && uv run pytest

# Build imagen (sin Docker local)
gcloud builds submit ingestion --tag <REGION>-docker.pkg.dev/<PROJECT_ID>/coingecko/ingest

# Ejecutar job manual
gcloud run jobs execute coingecko-ingest --region us-central1
```

## MCP

`.mcp.json` expone el server `bigquery` (MCP Toolbox prebuilt) para inspeccionar esquemas y
validar queries durante el desarrollo. Requiere ADC y `BIGQUERY_PROJECT` = PROJECT_ID.

## Tooling instalado

gcloud SDK 574, Terraform 1.15.7, Python 3.12.8, uv 0.11.6, git 2.52. Tras instalar gcloud/terraform
hay que **reiniciar la terminal/Claude Code** para refrescar PATH.
