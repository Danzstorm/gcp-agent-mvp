# adk_agent — Agente ADK en Vertex AI Agent Engine

Segundo agente (además del CA API): **ADK + BigQuery toolset**, desplegable a **Agent Engine**
(Agent Platform / Gemini Enterprise). Consulta las vistas `coingecko_curated` vía BigQuery.

## Diferencia con el agente CA API

| | CA API (`agent/`) | ADK (`adk_agent/`) |
|---|---|---|
| Producto | Conversational Analytics | Agent Development Kit |
| Vive en | BigQuery → Agent Catalog | Vertex AI **Agent Engine** |
| Runtime | Managed por BigQuery | Reasoning Engine (Vertex) |
| Extensible | Limitado a datos | Multi-tool, código propio |

## Setup local

```bash
cd adk_agent
uv venv && uv pip install -e .
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=airflow-pipeline-project
export GOOGLE_CLOUD_LOCATION=us-central1
export GCP_PROJECT=airflow-pipeline-project
export PYTHONUTF8=1
```

## Probar local (sin desplegar)

```bash
uv run python run_local.py "Cuales son las 5 monedas con mayor market cap?"
```

## Desplegar a Agent Engine

```bash
uv run python deploy.py        # build remoto ~5-10 min, imprime RESOURCE_NAME
```

Requiere bucket de staging (`gs://<project>-agent-staging`) y que el service agent de
Vertex tenga roles `bigquery.dataViewer` + `bigquery.jobUser`.

## Consultar el agente desplegado

```bash
uv run python query_remote.py "Que categorias dominan el mercado?"
```

También aparece en consola: **Vertex AI → Agent Engine** (Agent Platform).

## Config (env)

| Var | Default |
|---|---|
| `GCP_PROJECT` | `airflow-pipeline-project` |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` |
| `ADK_MODEL` | `gemini-2.5-flash` |
| `STAGING_BUCKET` | `gs://<project>-agent-staging` |
