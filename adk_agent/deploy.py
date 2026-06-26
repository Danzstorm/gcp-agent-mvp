"""Despliega el agente ADK a Vertex AI Agent Engine."""

from __future__ import annotations

import os

import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp

from coingecko_adk.agent import root_agent

PROJECT = os.environ.get("GCP_PROJECT", "airflow-pipeline-project")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING = os.environ.get("STAGING_BUCKET", f"gs://{PROJECT}-agent-staging")

REQUIREMENTS = [
    "google-cloud-aiplatform[agent_engines,adk]>=1.95",
    "google-adk>=1.0.0",
    "google-cloud-bigquery>=3.25",
    "google-cloud-secret-manager>=2.20",
    "google-cloud-dataplex>=2.20",
    "httpx>=0.27",
    "cloudpickle>=3.0",
]


def main() -> None:
    vertexai.init(project=PROJECT, location=LOCATION, staging_bucket=STAGING)
    app = AdkApp(agent=root_agent)
    remote = agent_engines.create(
        agent_engine=app,
        display_name="coingecko-adk",
        description="Analista cripto ADK sobre coingecko_curated (BigQuery toolset).",
        requirements=REQUIREMENTS,
        extra_packages=["src/coingecko_adk"],
    )
    print("RESOURCE_NAME:", remote.resource_name)


if __name__ == "__main__":
    main()
