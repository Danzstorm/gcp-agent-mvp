"""Define el agente ADK (root_agent) con BigQuery toolset + tools live.

Tools disponibles:
- BigQueryToolset: consulta historial en coingecko_curated (solo lectura)
- get_live_price: precio en tiempo real desde CoinGecko (no espera el job hourly)
- google_search: noticias, contexto y sentimiento de mercado
"""

from __future__ import annotations

import functools
import os
from typing import Any

import google.auth
import httpx
from google.adk.agents import Agent
from google.adk.integrations.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.integrations.bigquery.config import BigQueryToolConfig, WriteMode

PROJECT = os.environ.get("GCP_PROJECT", "airflow-pipeline-project")
DATASET = os.environ.get("CURATED_DATASET", "coingecko_curated")
MODEL = os.environ.get("ADK_MODEL", "gemini-2.5-flash")
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
SECRET_NAME = f"projects/{PROJECT}/secrets/coingecko-api-key/versions/latest"


@functools.lru_cache(maxsize=1)
def _api_key() -> str:
    """Lee API key de env var o Secret Manager (cacheado)."""
    key = os.environ.get("COINGECKO_API_KEY")
    if key:
        return key
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    resp = client.access_secret_version(request={"name": SECRET_NAME})
    return resp.payload.data.decode("UTF-8")


def get_crypto_news(per_page: int = 5) -> list[dict[str, Any]]:
    """Obtiene noticias recientes del mercado cripto desde CoinGecko.

    Úsalo cuando pregunten por noticias, eventos, novedades o contexto del mercado.

    Args:
        per_page: Cantidad de noticias a devolver (1-20). Default 5.

    Returns:
        Lista de noticias con title, description, url, published_at, source.
    """
    try:
        resp = httpx.get(
            f"{COINGECKO_BASE}/news",
            params={"per_page": min(per_page, 20)},
            headers={"x-cg-demo-api-key": _api_key()},
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        articles = data if isinstance(data, list) else data.get("data", [])
        return [
            {
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url"),
                "published_at": a.get("published_at"),
                "source": a.get("news_site") or a.get("author"),
            }
            for a in articles[:per_page]
        ]
    except Exception as exc:
        return [{"error": str(exc)}]


def get_live_price(coin_ids: str, vs_currencies: str = "usd") -> dict[str, Any]:
    """Obtiene precio actual de una o más monedas directamente desde CoinGecko.

    Úsalo cuando el usuario pregunte por precio ACTUAL o en tiempo real.
    Para análisis histórico o tendencias, usa BigQuery.

    Args:
        coin_ids: ID(s) de moneda separados por coma. Ej: "bitcoin", "bitcoin,ethereum,solana"
        vs_currencies: Monedas fiat separadas por coma. Default "usd". Ej: "usd,eur"

    Returns:
        Dict con precio, market_cap, volumen 24h por moneda. Ej:
        {"bitcoin": {"usd": 65000, "usd_market_cap": 1.2e12, "usd_24h_vol": 30e9, "usd_24h_change": 1.5}}
    """
    try:
        resp = httpx.get(
            f"{COINGECKO_BASE}/simple/price",
            params={
                "ids": coin_ids,
                "vs_currencies": vs_currencies,
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
            },
            headers={"x-cg-demo-api-key": _api_key()},
            timeout=15.0,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        return {"error": str(exc)}


INSTRUCTION = f"""\
Eres un analista experto en criptomonedas con acceso a tres fuentes de información:

1. **BigQuery (datos históricos)**: vistas `{PROJECT}.{DATASET}.*` con historial de precios,
   OHLC, dominancia de mercado y dimensiones de monedas. Ideal para tendencias, rankings
   históricos, comparaciones y análisis de categorías.

2. **get_live_price (precio en tiempo real)**: llama CoinGecko directamente para el precio
   ACTUAL de cualquier moneda. Úsalo cuando pregunten "precio ahora", "precio actual" o
   necesiten datos más frescos que 1 hora.

3. **get_crypto_news (noticias cripto)**: trae las últimas noticias del mercado desde CoinGecko.
   Úsalo para contexto, eventos, novedades o sentimiento. Solo acepta `per_page` (cantidad).

Vistas BigQuery disponibles:
- `{PROJECT}.{DATASET}.latest_prices`: snapshot más reciente por moneda (coin_id, symbol, name,
  current_price_usd, market_cap_usd, market_cap_rank, total_volume_usd, price_change_pct_24h,
  circulating_supply). Para rankings, top N, comparaciones históricas.
- `{PROJECT}.{DATASET}.dim_coin`: coin_id, symbol, name, market_cap_rank, categories (ARRAY).
  Para filtrar por categoría (UNNEST).
- `{PROJECT}.{DATASET}.ohlc_timeseries`: coin_id, open_time, open, high, low, close.
  Velas diarias para evolución y volatilidad.
- `{PROJECT}.{DATASET}.market_global_daily`: day, active_cryptocurrencies, total_market_cap_usd,
  total_volume_usd, btc_dominance_pct, eth_dominance_pct. Visión macro diaria.

Reglas:
- Nombres de tabla siempre totalmente calificados (proyecto.dataset.vista).
- Valores monetarios en USD salvo que pidan otra moneda.
- Para "top N" ordena por market_cap_rank ASC (1 = mayor market cap).
- Combina fuentes si aporta valor: p.ej. precio live + contexto de noticias + tendencia histórica.
- Responde en español, claro y con cifras formateadas.
"""


def _build_toolset() -> BigQueryToolset:
    credentials, _ = google.auth.default()
    cred_config = BigQueryCredentialsConfig(credentials=credentials)
    tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)
    return BigQueryToolset(credentials_config=cred_config, bigquery_tool_config=tool_config)


root_agent = Agent(
    name="coingecko_adk",
    model=MODEL,
    description=(
        "Analista cripto con datos históricos (BigQuery), precio live (CoinGecko) "
        "y noticias (Google Search). Responde en español."
    ),
    instruction=INSTRUCTION,
    tools=[_build_toolset(), get_live_price, get_crypto_news],
)
