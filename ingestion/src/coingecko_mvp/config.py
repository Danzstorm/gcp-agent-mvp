"""Configuración de la ingesta. Lee de variables de entorno con defaults sensatos.

En Cloud Run el secreto de la API key se inyecta como variable de entorno
(`COINGECKO_API_KEY`) desde Secret Manager; en local se exporta a mano.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Endpoints lógicos → particiones en GCS y tablas en BigQuery.
ENDPOINTS = ("coin_markets", "market_global", "trending", "coin_ohlc", "coin_metadata")


@dataclass(frozen=True)
class Settings:
    project_id: str
    api_key: str
    landing_bucket: str
    raw_dataset: str = "coingecko_raw"
    vs_currency: str = "usd"
    top_n: int = 250          # monedas a traer en /coins/markets (1 sola call)
    ohlc_top_n: int = 50      # monedas para OHLC/metadata (1 call por moneda)
    ohlc_days: int = 7
    timeout: float = 30.0
    max_retries: int = 4
    extra: dict = field(default_factory=dict)

    @staticmethod
    def from_env() -> "Settings":
        def req(name: str) -> str:
            val = os.environ.get(name)
            if not val:
                raise RuntimeError(f"Falta variable de entorno requerida: {name}")
            return val

        return Settings(
            project_id=req("GCP_PROJECT"),
            api_key=req("COINGECKO_API_KEY"),
            landing_bucket=req("LANDING_BUCKET"),
            raw_dataset=os.environ.get("RAW_DATASET", "coingecko_raw"),
            vs_currency=os.environ.get("VS_CURRENCY", "usd"),
            top_n=int(os.environ.get("TOP_N", "250")),
            ohlc_top_n=int(os.environ.get("OHLC_TOP_N", "50")),
            ohlc_days=int(os.environ.get("OHLC_DAYS", "7")),
        )
