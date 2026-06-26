# Fase 0 — Fundaciones

Objetivo: dejar el proyecto listo para construir, con infra base y scaffold.

## Hecho

- **Tooling local**: gcloud SDK 574, Terraform 1.15.7, Python 3.12.8, uv 0.11.6, git 2.52.
- **Repo scaffold**: estructura `infra/ ingestion/ transform/ agent/ docs/ .claude/`, git init.
- **Docs base**: `architecture.md`, `ADR-0001-stack.md`, spec de diseño.
- **Terraform skeleton**: `providers.tf`, `variables.tf`, `main.tf`, módulo `apis` (habilita APIs).
- **MCP**: `.mcp.json` con server `bigquery` (MCP Toolbox prebuilt).
- **Subagents**: `gcp-infra`, `gcp-data`, `gcp-agent`.
- **Config**: PROJECT_ID = `airflow-pipeline-project`, REGION = `us-central1`, BQ = `US`.

## Completado (2026-06-26)

- **Auth**: `gcloud auth login` + ADC + `config set project airflow-pipeline-project` + quota project.
- **toolbox.exe** v1.1.0 en raíz (gitignored).
- **terraform apply** (14 recursos): 10 APIs, bucket GCS `airflow-pipeline-project-coingecko-raw`,
  datasets `coingecko_raw` + `coingecko_curated`, secret `coingecko-api-key`.
- **API key** CoinGecko cargada (versión 1) y validada (ping HTTP 200).

## Verificación de la fase ✅

- `terraform apply` OK, APIs habilitadas (output `enabled_services`).
- `bq ls` muestra ambos datasets.
- `gcloud secrets versions list` → versión 1 enabled.
- CoinGecko `/ping` con la key → 200.

## Pendiente menor

- **Rotar la API key**: quedó expuesta en el chat. Regenerar en dashboard CoinGecko y
  `gcloud secrets versions add coingecko-api-key --data-file=-` con la nueva.
