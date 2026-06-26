# Fase 5 — Agente ADK en Vertex AI Agent Engine

Objetivo: desplegar un segundo agente sobre `coingecko_curated` usando **ADK + BigQuery Toolset**
en **Vertex AI Agent Engine** (Agent Platform).

## Por qué un segundo agente

| | CA API (`agent/`) | ADK Engine (`adk_agent/`) |
|---|---|---|
| Runtime | Managed por BigQuery | Reasoning Engine (Vertex AI) |
| Extensible | Solo datos BQ | Multi-tool, código Python propio |
| Consola | BigQuery Studio | Vertex AI → Agent Engine |
| Ideal para | Analytics puro | Agentes extensibles, productivos |

El CA API data agent es más simple de crear; el ADK en Agent Engine es más extensible y vive
dentro del ecosistema de Agent Platform / Gemini Enterprise.

## Qué se construyó (`adk_agent/`)

Paquete `coingecko_adk` (Python, ADK v1) con **tres tools**:

- `src/coingecko_adk/agent.py` — `root_agent` con:
  - `BigQueryToolset` (read-only, `WriteMode.BLOCKED`) — consulta historial en `coingecko_curated`
  - `get_live_price(coin_ids, vs_currencies)` — precio en tiempo real desde CoinGecko (sin esperar el job hourly)
  - `get_crypto_news(category, per_page)` — noticias cripto recientes desde CoinGecko `/news`
  - El agente elige solo cuál tool usar según la pregunta
- `run_local.py` — prueba local vía `InMemoryRunner` (sin desplegar, útil para dev).
- `deploy.py` — empaqueta en `AdkApp`, sube a GCS staging y crea el Agent Engine via LRO.
- `query_remote.py` — crea sesión en el engine desplegado y hace `stream_query`.

**Nota**: `google_search` (built-in ADK) no puede mezclarse con otros tools en Gemini
(`INVALID_ARGUMENT: Multiple tools supported only when all are search tools`). Por eso se usa
`get_crypto_news` como tool Python custom en su lugar.

## Dependencias clave

```
google-adk>=1.0.0
google-cloud-aiplatform[agent_engines,adk]>=1.95
google-cloud-bigquery>=3.25
google-cloud-dataplex>=2.20   # requerido por BigQueryToolset internamente
cloudpickle>=3.0
pydantic==2.13.4              # auto-detectado y añadido por el SDK
```

## Deploy

```bash
cd adk_agent
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=airflow-pipeline-project
export GOOGLE_CLOUD_LOCATION=us-central1
export GCP_PROJECT=airflow-pipeline-project
export PYTHONUTF8=1

uv run python deploy.py   # ~5-10 min, crea LRO → imprime RESOURCE_NAME
```

Requiere bucket staging `gs://airflow-pipeline-project-agent-staging` y que el service agent
de Vertex AI tenga roles `bigquery.dataViewer` + `bigquery.jobUser`.

## Verificación ✅ (2026-06-26)

Agente desplegado:
`projects/739408986854/locations/us-central1/reasoningEngines/8014708041498755072`

Pregunta probada:
> *"¿Cuáles son las top 5 monedas por market cap?"*

Respuesta del agente:
1. Bitcoin (BTC): $1,198,496,118,577 USD
2. Ethereum (ETH): $188,997,335,354 USD
3. Tether (USDT): $186,075,414,099 USD
4. BNB (BNB): $75,570,624,166 USD
5. USDC (USDC): $73,550,705,429 USD

Consulta BigQuery ejecutada correctamente, respuesta en español, datos reales de `latest_prices`.

## Uso

### CLI (terminal)

```bash
cd adk_agent

# Probar local (dev, sin desplegar):
uv run python run_local.py "¿Qué monedas están trending?"

# Consultar el agente desplegado:
export AGENT_ENGINE_RESOURCE=projects/739408986854/locations/us-central1/reasoningEngines/8014708041498755072
uv run python query_remote.py "¿Top 5 por market cap?"
uv run python query_remote.py "¿OHLC de bitcoin última semana?"
uv run python query_remote.py "¿Qué categorías dominan el mercado?"
```

### GCP Console (demo visual)

1. Ir a **Vertex AI → Agent Engine** (o Agent Platform → Agent Engine).
2. Seleccionar `coingecko-adk`.
3. Click "Test agent" → interfaz de chat en el browser.
4. Escribir preguntas en lenguaje natural directamente.

URL directa: `https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=airflow-pipeline-project`

## Notas

- El agente usa ADC para autenticar BigQuery — mismas credenciales del ambiente local.
- `WriteMode.BLOCKED` impide que el agente ejecute queries destructivos (INSERT/DELETE/UPDATE).
- El engine se puede actualizar con `agent_engines.update()` sin re-crear la sesión.
- Para producción: agregar más tools Python propias (alertas, cálculos custom, etc.).
