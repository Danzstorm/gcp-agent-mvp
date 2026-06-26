# Arquitectura — gcp-agent-mvp

## Visión

Pipeline batch que ingesta datos de mercado cripto desde **CoinGecko**, los almacena en
**BigQuery** en dos capas (raw → curated) y los expone a **dos agentes Gemini/Vertex nativos**
para preguntas en lenguaje natural: Conversational Analytics API (Data Agent) y ADK en
Vertex AI Agent Engine.

## Diagrama

```
CoinGecko API (Demo, header x-cg-demo-api-key)
        │  batch HTTP (Python httpx)
        ▼
Cloud Run Job  ◄──gatillo cron──  Cloud Scheduler
  (coingecko-ingest)               · hourly: markets, global, trending
        │                          · daily:  ohlc (top 50), metadata
        │  lee secreto
        ▼
   Secret Manager (coingecko-api-key)
        │  escribe NDJSON
        ▼
GCS landing  gs://<project>-coingecko-raw/<endpoint>/dt=YYYY-MM-DD/<ts>.ndjson
  (force_destroy=true, versioning OFF, lifecycle 90d) — archivo crudo, replayable
        │  bq load (load jobs)
        ▼
BigQuery — coingecko_raw  (tablas NATIVAS, append, particionado por ingestion_time)
  · coin_markets · coin_ohlc · coin_metadata · trending · market_global
        │  SQL (vistas en MVP)
        ▼
BigQuery — coingecko_curated  (tipado, limpio, servido al agente)
  · dim_coin · latest_prices · ohlc_timeseries · market_global_daily
        │
        ├─────────────────────────────────────────────────────┐
        ▼                                                     ▼
Conversational Analytics API                    Vertex AI Agent Engine
  Data Agent "coingecko-analyst"                  ADK "coingecko-adk"
  (NL → SQL, managed by BigQuery)                 (BigQuery Toolset, reasoning engine)
        │                                                     │
        └────────────────────┬────────────────────────────────┘
                             ▼
              Preguntas del usuario en lenguaje natural
```

## Componentes

| Componente | Servicio GCP | Rol |
|---|---|---|
| Ingesta | Cloud Run Job (Python) | Llama CoinGecko, escribe NDJSON a GCS, carga a BQ |
| Orquestación | Cloud Scheduler | Dispara el job (hourly / daily) |
| Secreto | Secret Manager | API key CoinGecko |
| Landing | GCS (bucket) | NDJSON crudo, archivo replayable (bronze) |
| Build | Cloud Build + Artifact Registry | Imagen del job (sin Docker local) |
| Almacén | BigQuery (raw / curated) | Tablas nativas y capa servida |
| Agente CA API | Conversational Analytics API | Q&A NL → SQL, managed runtime |
| Agente ADK | Vertex AI Agent Engine (ADK) | Q&A NL → SQL, extensible, deployable |
| IaC | Terraform | Infra persistente reproducible |
| Dev MCP | MCP Toolbox (BigQuery) | Inspección de esquemas/queries en dev |

## Flujo de datos

1. Scheduler dispara Cloud Run Job según cron.
2. El job lee la API key de Secret Manager, llama los endpoints CoinGecko correspondientes al modo.
3. Escribe la respuesta como **NDJSON a GCS** (`<endpoint>/dt=YYYY-MM-DD/<ts>.ndjson`) — archivo crudo replayable.
4. Lanza **bq load** del NDJSON a tablas **nativas** particionadas en `coingecko_raw`.
5. SQL de la capa curated (vistas) tipa y deduplica para consumo del agente.
6. El Data Agent traduce preguntas NL a SQL sobre `coingecko_curated`.

**Replay**: si se pierde una tabla BQ, se recarga desde GCS con `bq load` sin volver a llamar a CoinGecko
(ahorra rate limit del free tier).

## Presupuesto de rate limit (Demo = 100/min, 10k/mes)

- Hourly: markets + global + trending = 3 calls × 24 × 30 ≈ **2 160/mes**.
- Daily: ohlc + metadata top-50 ≈ 100 calls × 30 ≈ **3 000/mes**.
- Total ≈ **5 160/mes** < 10 000. Holgura para reintentos.

## Agentes: comparativa

| | CA API (`agent/`) | ADK Engine (`adk_agent/`) |
|---|---|---|
| Producto | Conversational Analytics API | Agent Development Kit + Agent Engine |
| Runtime | Managed por BigQuery/Google | Reasoning Engine (Vertex AI) |
| Consola | BigQuery Studio | Vertex AI → Agent Engine |
| Extensible | Solo datos | Multi-tool, código propio |
| Demo CLI | `uv run python -m coingecko_agent.ask "pregunta"` | `uv run python query_remote.py "pregunta"` |
| Resource | `coingecko-analyst` (global) | `reasoningEngines/8014708041498755072` (us-central1) |

## Decisiones clave

Ver `docs/decisions/` (ADRs). Resumen: agente = CA API (nativo) + ADK en Agent Engine; ingesta = batch; IaC = Terraform;
build = Cloud Build; región = us-central1; BQ = US multi-región.
