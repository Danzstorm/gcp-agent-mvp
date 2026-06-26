# Fase 1 — Ingestión MVP (TDD)

Objetivo: pipeline batch CoinGecko → GCS → BigQuery, programado y desplegado.

## Componentes construidos

### Código (`ingestion/`, TDD, 15 tests verde)
- `config.py` — Settings desde env (project, bucket, dataset, top_n, ohlc_top_n, días).
- `client.py` — `CoinGeckoClient`: header `x-cg-demo-api-key`, retries (tenacity) en 429/5xx,
  endpoints markets/global/trending/ohlc/coin. Errores → `CoinGeckoError`.
- `transform.py` — `document_rows` (payload JSON + ingestion_time), `ohlc_rows` (estructurado),
  `to_ndjson`.
- `gcs_writer.py` — `GcsWriter`: sube NDJSON a `gs://<bucket>/<endpoint>/dt=YYYY-MM-DD/<ts>_<run>.ndjson`.
- `bq_loader.py` — `BqLoader`: `bq load` NDJSON de GCS a tablas nativas (WRITE_APPEND).
- `main.py` — orquesta por modo (`hourly` | `daily` | `all`).

### Infra (`infra/terraform/`)
- `bigquery` — 5 tablas raw particionadas por día: coin_markets, market_global, trending,
  coin_metadata (payload JSON) y coin_ohlc (estructurada).
- `artifact_registry` — repo Docker `coingecko`.
- `iam` — `ingest-sa` (bigquery.dataEditor + jobUser, storage.objectAdmin en bucket,
  secretAccessor en secret) y `scheduler-sa` (run.developer).
- `cloudrun_job` — 2 jobs: `coingecko-ingest-hourly` (`--mode hourly`),
  `coingecko-ingest-daily` (`--mode daily`, OHLC top 50). Secret inyectado como env.
- `scheduler` — `coingecko-ingest-hourly` (`0 * * * *`) y `coingecko-ingest-daily` (`0 6 * * *` UTC).

### Imagen
- `ingestion/Dockerfile` (python:3.12-slim) → Cloud Build → Artifact Registry
  `us-central1-docker.pkg.dev/airflow-pipeline-project/coingecko/ingest:latest`.

## Cadencia y rate limit
- hourly: 3 calls. daily: ~100 calls (OHLC top 50 + metadata). Total ≈ 5k/mes < 10k Demo.

## Verificación ✅ (2026-06-26)
- Smoke test local: hourly → coin_markets 250, market_global 1, trending 15; daily (top 3) →
  coin_ohlc 126, coin_metadata 3. Datos reales en GCS + BQ.
- JSON parseado en BQ (`JSON_VALUE`) correcto (bitcoin, ethereum, …).
- **Cloud Run Job ejecutado en la nube** (`coingecko-ingest-hourly`) → nueva partición en BQ.
- Schedulers ENABLED. `pytest` 15/15 verde.

## Notas / deuda
- OHLC_TOP_N del job daily = 50 (var Terraform `ohlc_top_n`).
- Rotar la API key (quedó en chat) cuando se pueda.
