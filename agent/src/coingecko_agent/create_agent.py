"""Crea (o recrea) el Data Agent de Conversational Analytics sobre coingecko_curated."""

from __future__ import annotations

import sys

from google.api_core import exceptions
from google.cloud import geminidataanalytics

from . import config
from .client_factory import agent_client


def _build_datasources() -> geminidataanalytics.DatasourceReferences:
    refs = []
    for view in config.CURATED_VIEWS:
        t = geminidataanalytics.BigQueryTableReference()
        t.project_id = config.BILLING_PROJECT
        t.dataset_id = config.CURATED_DATASET
        t.table_id = view
        refs.append(t)
    ds = geminidataanalytics.DatasourceReferences()
    ds.bq.table_references = refs
    return ds


def _build_agent() -> geminidataanalytics.DataAgent:
    ctx = geminidataanalytics.Context()
    ctx.system_instruction = config.SYSTEM_INSTRUCTION
    ctx.datasource_references = _build_datasources()

    agent = geminidataanalytics.DataAgent()
    agent.data_analytics_agent.published_context = ctx
    agent.description = "Analista de datos cripto (CoinGecko) sobre coingecko_curated"
    return agent


def main() -> int:
    client = agent_client()
    parent = f"projects/{config.BILLING_PROJECT}/locations/{config.LOCATION}"
    agent = _build_agent()

    req = geminidataanalytics.CreateDataAgentRequest(
        parent=parent,
        data_agent_id=config.AGENT_ID,
        data_agent=agent,
    )

    try:
        client.create_data_agent_sync(request=req)
        print(f"Agente creado: {config.AGENT_ID} (vistas: {', '.join(config.CURATED_VIEWS)})")
    except exceptions.AlreadyExists:
        # Actualizar el contexto si ya existe.
        agent.name = f"{parent}/dataAgents/{config.AGENT_ID}"
        update = geminidataanalytics.UpdateDataAgentRequest(data_agent=agent)
        client.update_data_agent(request=update)
        print(f"Agente actualizado: {config.AGENT_ID}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
