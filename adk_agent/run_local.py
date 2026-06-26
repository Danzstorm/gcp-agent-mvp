"""Prueba local del agente ADK (sin desplegar). Ejecuta una pregunta NL."""

from __future__ import annotations

import asyncio
import sys

from google.adk.runners import InMemoryRunner
from google.genai import types

from coingecko_adk.agent import root_agent

APP = "coingecko"
USER = "local-user"


async def ask(question: str) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP)
    session = await runner.session_service.create_session(app_name=APP, user_id=USER)
    content = types.Content(role="user", parts=[types.Part(text=question)])

    print(f"\nPregunta: {question}\n{'-' * 60}")
    async for event in runner.run_async(
        user_id=USER, session_id=session.id, new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    print(part.text, end="")
    print()


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "¿Top 5 monedas por market cap y su precio?"
    asyncio.run(ask(q))
