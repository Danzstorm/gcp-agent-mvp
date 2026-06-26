---
marp: true
title: CoinGecko → BigQuery → Agente Q&A en GCP
author: Daniel Santos
theme: default
paginate: true
---

# CoinGecko → BigQuery → Agente Q&A
## Pipeline de datos cripto en Google Cloud Platform

Ingesta batch · Lakehouse · Agente Gemini nativo

*MVP construido con Claude Code + superpowers · 2026-06-26*

---

## El problema

- Datos de mercado cripto (precios, OHLC, dominancia) **dispersos y volátiles**.
- Queremos **preguntar en lenguaje natural**: *"¿top 5 por market cap?"*, *"¿categorías que dominan?"*.
- Necesitamos un pipeline **ordenado, reproducible y barato** que cargue datos y los sirva a un agente.

**Objetivo:** CoinGecko → BigQuery → agente Q&A, todo serverless en GCP.

---

## Arquitectura

```
CoinGecko API (Demo)
   │  batch HTTP (Python)
   ▼
Cloud Run Job ◄── Cloud Scheduler (hourly + daily)
   │   API key ← Secret Manager
   ▼
GCS landing (NDJSON crudo, replayable)
   │  bq load
   ▼
BigQuery raw  ──vistas SQL──►  BigQuery curated
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
          CA API Data Agent              Vertex AI Agent Engine
          "coingecko-analyst"              "coingecko-adk" (ADK)
                     │                             │
                     └──────────────┬──────────────┘
                                    ▼
                         Preguntas lenguaje natural
```

---

## Stack tecnológico

| Capa | Servicio GCP | Por qué |
|---|---|---|
| Ingesta | Cloud Run Job (Python) | Serverless, escala a cero |
| Orquestación | Cloud Scheduler | Cron managed |
| Secreto | Secret Manager | API key fuera del código |
| Landing | Cloud Storage | Archivo crudo → **replay** |
| Almacén | BigQuery (raw → curated) | SQL + escala |
| Agente 1 | Conversational Analytics API | Gemini nativo, NL → SQL |
| Agente 2 | Vertex AI Agent Engine (ADK) | Extensible, Agent Platform |
| IaC | Terraform | Reproducible, desmontable |

---

## Patrón de datos: bronze → silver

- **GCS landing (bronze):** NDJSON crudo, particionado `dt=YYYY-MM-DD`. Inmutable, replayable.
- **BigQuery raw:** tablas nativas (payload JSON + `ingestion_time`), particionadas por día.
- **BigQuery curated (silver):** vistas tipadas listas para el agente.

**Replay:** si se pierde una tabla, se recarga desde GCS **sin re-llamar a CoinGecko**
(ahorra rate limit del free tier: 100/min, 10k/mes).

---

## Capa curated (4 vistas)

| Vista | Da |
|---|---|
| `latest_prices` | Snapshot por moneda: precio, market cap, rank, %24h |
| `dim_coin` | Símbolo, nombre, `categories` (ARRAY) |
| `ohlc_timeseries` | Velas diarias O/H/L/C por moneda |
| `market_global_daily` | Activos, market cap total, dominancia BTC/ETH |

Patrón: `ROW_NUMBER() OVER (PARTITION BY clave ORDER BY ingestion_time DESC)` → fila más reciente.

---

## Dos agentes sobre los mismos datos

| | CA API Data Agent | ADK + Agent Engine |
|---|---|---|
| Runtime | Managed por BigQuery | Vertex AI Agent Engine |
| Consola | BigQuery Studio | **Vertex AI → Agent Engine** |
| Extensible | Solo datos | Multi-tool, código Python |
| Demo | `ask.py "pregunta"` | `query_remote.py "pregunta"` |

Mismas vistas curated → dos experiencias de agente.

---

## Agente 1 — Conversational Analytics API

- Data Agent **`coingecko-analyst`** sobre las 4 vistas curated.
- `system_instruction` con contexto de dominio cripto (qué es market cap, OHLC, dominancia…).
- Traduce **lenguaje natural → SQL** y ejecuta sobre BigQuery.
- Runtime **100% managed** por Google (sin servidor propio).

---

## Agente 2 — ADK en Vertex AI Agent Engine

- **`coingecko-adk`** en Agent Engine (`reasoningEngines/8014708041498755072`).
- Usa `BigQueryToolset` (ADK v1) en modo lectura (`WriteMode.BLOCKED`).
- Desplegable, versionable, extensible con herramientas Python propias.
- Visible en consola: **Vertex AI → Agent Engine → Test agent**.

---

## Demo: preguntas reales (ADK Agent Engine)

**P:** *"¿Cuáles son las top 5 monedas por market cap?"*
→ Agente consulta `latest_prices` vía BigQuery Toolset
→ BTC $1.19T, ETH $189B, USDT $186B, BNB $75B, USDC $73B ✅

**P:** *"¿Cuáles son las 5 monedas con mayor market cap y su precio?"* (CA API)
→ `ORDER BY market_cap_rank LIMIT 5` sobre `latest_prices`
→ BTC $59,861 (mcap $1.19T), ETH, USDT, BNB, USDC ✅

---

## Resultados

- Pipeline **corriendo solo** cada hora (markets/global/trending) y diario (OHLC/metadata top 50).
- **15 tests** unitarios verde (cliente, transform, loaders, orquestación — TDD).
- Datos reales en BigQuery; **dos agentes** responden en español con NL → SQL.
- ADK Agent Engine desplegado en `us-central1`, accesible desde consola GCP y CLI.
- Costo ≈ **$0** (free tier GCP + CoinGecko Demo).

---

## Ingeniería: cómo se construyó

- **Workflow superpowers:** brainstorm → spec → plan → ejecución TDD → verificación.
- **Terraform modular:** apis, gcs, bigquery, secrets, iam, artifact_registry, cloudrun_job,
  scheduler, curated. Un `terraform destroy` lo desmonta todo.
- **IAM mínimo privilegio:** `ingest-sa` y `scheduler-sa` con solo sus roles.
- **MCP BigQuery** para inspeccionar datos durante el desarrollo.

---

## Desmontaje limpio (teardown)

- Backend Terraform **local** (sin bucket de state).
- BigQuery `delete_contents_on_destroy = true`.
- GCS `force_destroy = true`, versioning **off**, lifecycle 90 días.

→ `terraform destroy` borra todo sin pasos manuales.

---

## Próximos pasos

- **Demo live**: Vertex AI → Agent Engine → `coingecko-adk` → "Test agent" (chat en browser).
- Materializar vistas curated a tablas si crece el volumen.
- Alertas / dashboard (Looker Studio sobre curated).
- Extender ADK agent con más tools (alertas de precio, comparaciones históricas).
- Más fuentes (DEX, NFT) reusando el mismo patrón landing → raw → curated.
- Rotar la API key y migrar state a GCS para CI.

---

# Gracias

**Pipeline CoinGecko → BigQuery → Agente Q&A**
Serverless · Reproducible · Lenguaje natural

`airflow-pipeline-project` · us-central1
