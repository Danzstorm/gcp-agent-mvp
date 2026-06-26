# agent — Data Agent (Conversational Analytics API)

Agente Gemini nativo que responde preguntas en lenguaje natural sobre `coingecko_curated`.

## Setup

```bash
cd agent
uv venv && uv pip install -e .
export GCP_PROJECT=airflow-pipeline-project
export PYTHONUTF8=1   # acentos correctos en Windows
```

## Crear / actualizar el agente

```bash
uv run python -m coingecko_agent.create_agent
```

Crea el Data Agent `coingecko-analyst` (location `global`) apuntando a las 4 vistas curated,
con un system_instruction de dominio cripto.

## Preguntar

```bash
uv run python -m coingecko_agent.ask "Cuales son las 5 monedas con mayor market cap?"
uv run python -m coingecko_agent.ask "Como evoluciono el precio de bitcoin esta semana?"
uv run python -m coingecko_agent.ask "Que categorias de monedas dominan el mercado?"
```

El agente genera SQL sobre BigQuery y responde en español. La salida incluye el SQL ejecutado.

## Config (env)

| Var | Default |
|---|---|
| `GCP_PROJECT` | `airflow-pipeline-project` |
| `CA_LOCATION` | `global` |
| `CURATED_DATASET` | `coingecko_curated` |
| `CA_AGENT_ID` | `coingecko-analyst` |
