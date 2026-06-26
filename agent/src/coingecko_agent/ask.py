"""Hace una pregunta en lenguaje natural al Data Agent y muestra la respuesta."""

from __future__ import annotations

import argparse
import sys

from google.cloud import geminidataanalytics

from . import config
from .client_factory import chat_client


def _print_system_message(msg) -> None:
    """Imprime las partes relevantes de un SystemMessage (texto, SQL, datos)."""
    # Texto en lenguaje natural
    if msg.text and msg.text.parts:
        print("".join(msg.text.parts), end="")
    # SQL generado / resultado de datos
    data = getattr(msg, "data", None)
    if data is not None:
        sql = getattr(data, "generated_sql", "")
        if sql:
            print(f"\n[SQL]\n{sql}")


def ask(question: str) -> int:
    client = chat_client()
    parent = f"projects/{config.BILLING_PROJECT}/locations/{config.LOCATION}"

    agent_ctx = geminidataanalytics.DataAgentContext()
    agent_ctx.data_agent = f"{parent}/dataAgents/{config.AGENT_ID}"

    message = geminidataanalytics.Message()
    message.user_message.text = question

    request = geminidataanalytics.ChatRequest(
        parent=parent,
        messages=[message],
        data_agent_context=agent_ctx,
    )

    print(f"\nPregunta: {question}\n{'-' * 60}")
    stream = client.chat(request=request, timeout=300)
    for response in stream:
        sm = getattr(response, "system_message", None)
        if sm is not None:
            _print_system_message(sm)
    print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pregunta al Data Agent de cripto")
    parser.add_argument("question", help="Pregunta en lenguaje natural")
    args = parser.parse_args(argv)
    return ask(args.question)


if __name__ == "__main__":
    sys.exit(main())
