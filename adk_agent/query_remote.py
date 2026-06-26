"""Consulta el agente ADK ya desplegado en Agent Engine.

Busca el agent engine por display_name 'coingecko-adk' (o usa AGENT_ENGINE_RESOURCE),
crea una sesión y hace streaming de la respuesta a una pregunta NL.
"""

from __future__ import annotations

import os
import sys

import vertexai
from vertexai import agent_engines

PROJECT = os.environ.get("GCP_PROJECT", "airflow-pipeline-project")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
DISPLAY_NAME = "coingecko-adk"
USER = "remote-user"


def _resolve_engine():
    res = os.environ.get("AGENT_ENGINE_RESOURCE")
    if res:
        return agent_engines.get(res)
    for e in agent_engines.list():
        if getattr(e, "display_name", None) == DISPLAY_NAME:
            return e
    raise SystemExit(f"No se encontró un Agent Engine '{DISPLAY_NAME}'. Despliega primero (deploy.py).")


def main() -> None:
    question = sys.argv[1] if len(sys.argv) > 1 else "¿Top 5 monedas por market cap y su precio?"
    vertexai.init(project=PROJECT, location=LOCATION)

    engine = _resolve_engine()
    session = engine.create_session(user_id=USER)
    session_id = session["id"] if isinstance(session, dict) else session.id

    print(f"\nPregunta: {question}\n{'-' * 60}")
    for event in engine.stream_query(user_id=USER, session_id=session_id, message=question):
        parts = (event or {}).get("content", {}).get("parts", [])
        for part in parts:
            text = part.get("text")
            if text:
                print(text, end="")
    print()


if __name__ == "__main__":
    main()
