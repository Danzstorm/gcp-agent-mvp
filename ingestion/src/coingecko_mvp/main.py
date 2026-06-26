"""Orquestación de la ingesta CoinGecko → GCS → BigQuery.

Modos:
- hourly: coin_markets, market_global, trending  (3 calls)
- daily:  coin_ohlc + coin_metadata para top N monedas (≈2*N calls)
- all:    ambos (útil en local)

Para cada endpoint: fetch → transform → NDJSON → GCS → bq load.
"""

from __future__ import annotations

import argparse
import logging
import sys
import uuid
from datetime import datetime, timezone

from . import transform
from .client import CoinGeckoClient
from .config import Settings

log = logging.getLogger("coingecko_mvp")


def _emit(endpoint: str, table: str, rows: list[dict], ts, run_id, writer, loader) -> int:
    ndjson = transform.to_ndjson(rows)
    uri = writer.write(endpoint, ts, run_id, ndjson)
    if not uri:
        log.info("endpoint=%s sin filas, se omite", endpoint)
        return 0
    n = loader.load_ndjson_uri(table, uri)
    log.info("endpoint=%s uri=%s filas=%s", endpoint, uri, n)
    return n


def _top_ids(client: CoinGeckoClient, settings: Settings) -> list[str]:
    markets = client.get_markets(per_page=settings.ohlc_top_n, page=1, vs_currency=settings.vs_currency)
    return [m["id"] for m in markets]


def run(
    mode: str,
    settings: Settings,
    client: CoinGeckoClient,
    writer,
    loader,
    now: datetime | None = None,
    run_id: str | None = None,
) -> dict[str, int]:
    ts = now or datetime.now(tz=timezone.utc)
    run_id = run_id or uuid.uuid4().hex[:8]
    summary: dict[str, int] = {}

    if mode in ("hourly", "all"):
        markets = client.get_markets(per_page=settings.top_n, page=1, vs_currency=settings.vs_currency)
        summary["coin_markets"] = _emit(
            "coin_markets", "coin_markets", transform.document_rows(markets, ts), ts, run_id, writer, loader
        )
        summary["market_global"] = _emit(
            "market_global", "market_global", transform.document_rows(client.get_global(), ts), ts, run_id, writer, loader
        )
        summary["trending"] = _emit(
            "trending", "trending", transform.document_rows(client.get_trending(), ts), ts, run_id, writer, loader
        )

    if mode in ("daily", "all"):
        ids = _top_ids(client, settings)
        ohlc_rows: list[dict] = []
        meta_rows: list[dict] = []
        for coin_id in ids:
            ohlc_rows.extend(transform.ohlc_rows(coin_id, client.get_ohlc(coin_id, days=settings.ohlc_days, vs_currency=settings.vs_currency), ts))
            meta_rows.extend(transform.document_rows(client.get_coin(coin_id), ts))
        summary["coin_ohlc"] = _emit("coin_ohlc", "coin_ohlc", ohlc_rows, ts, run_id, writer, loader)
        summary["coin_metadata"] = _emit("coin_metadata", "coin_metadata", meta_rows, ts, run_id, writer, loader)

    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingesta CoinGecko → BigQuery")
    parser.add_argument("--mode", choices=("hourly", "daily", "all"), default="hourly")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = Settings.from_env()

    from .bq_loader import BqLoader
    from .gcs_writer import GcsWriter

    client = CoinGeckoClient(
        api_key=settings.api_key, timeout=settings.timeout, max_retries=settings.max_retries
    )
    writer = GcsWriter(settings.landing_bucket)
    loader = BqLoader(settings.project_id, settings.raw_dataset)

    try:
        summary = run(args.mode, settings, client, writer, loader)
        log.info("ingesta completa mode=%s summary=%s", args.mode, summary)
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
