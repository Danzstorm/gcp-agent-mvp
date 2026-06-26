# Fase 3 — Agente (Conversational Analytics API)

Objetivo: agente Gemini/Vertex nativo que responde preguntas NL sobre `coingecko_curated`.

## Qué se construyó (`agent/`)

Paquete `coingecko_agent` (Python, SDK `google-cloud-geminidataanalytics`):
- `config.py` — proyecto, location (`global`), dataset, AGENT_ID `coingecko-analyst`, las 4 vistas
  curated y el **system_instruction** con contexto de dominio cripto (qué es cada tabla,
  market cap, OHLC, dominancia, reglas de top-N, todo en USD, responder en español).
- `client_factory.py` — construye `DataAgentServiceClient` / `DataChatServiceClient` con el
  endpoint correcto según location.
- `create_agent.py` — crea/actualiza el Data Agent apuntando a las 4 vistas (published_context
  con `DatasourceReferences.bq.table_references`).
- `ask.py` — CLI: pregunta NL → `chat()` con `data_agent_context` → imprime respuesta + SQL.

## API / arquitectura

- API: `geminidataanalytics.googleapis.com` (v1), location `global`.
- El agente traduce NL → SQL contra BigQuery y ejecuta sobre las vistas curated.
- Auth vía ADC. Sin servidor propio: el runtime es managed por Google.

## Verificación ✅ (2026-06-26)

Preguntas NL probadas (SQL correcto + respuesta en español):
1. *"¿Top 5 monedas por market cap y su precio?"* → `ORDER BY market_cap_rank LIMIT 5` sobre
   `latest_prices`. BTC $59,861 (mcap $1.19T), ETH, USDT, BNB, USDC.
2. *"¿Qué categorías hay y cuántas monedas cada una?"* → `UNNEST(categories)` + `COUNT(DISTINCT)`
   sobre `dim_coin`. 31 categorías, FTX Holdings 3, etc.

El agente además sugiere preguntas de seguimiento (serie temporal OHLC, volumen por categoría).

## Uso

```bash
cd agent
export GCP_PROJECT=airflow-pipeline-project PYTHONUTF8=1
uv run python -m coingecko_agent.create_agent          # crear/actualizar agente
uv run python -m coingecko_agent.ask "tu pregunta"      # preguntar
```

## Notas / mejoras
- `ask.py` imprime también el "razonamiento" del modelo (verboso). La respuesta final va al
  final del stream; se puede filtrar para una salida más limpia.
- El agente se puede consumir igual desde BigQuery Studio / consola (mismo Data Agent).
