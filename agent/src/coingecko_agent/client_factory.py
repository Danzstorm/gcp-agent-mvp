"""Construcción de clientes CA API con el endpoint correcto según la location."""

from __future__ import annotations

from google.api_core import client_options as client_options_lib
from google.cloud import geminidataanalytics

from .config import LOCATION


def _endpoint(location: str) -> str:
    if not location or location == "global":
        return "geminidataanalytics.googleapis.com"
    if "-" in location:
        return f"geminidataanalytics-{location}.googleapis.com"
    return f"geminidataanalytics.{location}.rep.googleapis.com"


def _opts():
    return client_options_lib.ClientOptions(api_endpoint=_endpoint(LOCATION))


def agent_client() -> geminidataanalytics.DataAgentServiceClient:
    return geminidataanalytics.DataAgentServiceClient(client_options=_opts())


def chat_client() -> geminidataanalytics.DataChatServiceClient:
    return geminidataanalytics.DataChatServiceClient(client_options=_opts())
