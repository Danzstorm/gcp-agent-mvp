"""Tests de orquestación con fakes (sin tocar GCP)."""

from datetime import datetime, timezone

from coingecko_mvp import main
from coingecko_mvp.config import Settings

TS = datetime(2026, 6, 26, 12, 0, 0, tzinfo=timezone.utc)


class FakeClient:
    def get_markets(self, per_page, page, vs_currency):
        return [{"id": f"coin{i}"} for i in range(per_page)]

    def get_global(self):
        return {"active_cryptocurrencies": 12000}

    def get_trending(self):
        return [{"item": {"id": "pepe"}}]

    def get_ohlc(self, coin_id, days, vs_currency):
        return [[1719403200000, 1.0, 2.0, 0.5, 1.5]]

    def get_coin(self, coin_id):
        return {"id": coin_id, "categories": ["layer-1"]}


class FakeWriter:
    def __init__(self):
        self.writes = []

    def write(self, endpoint, ts, run_id, ndjson):
        self.writes.append((endpoint, ndjson))
        return "" if not ndjson else f"gs://bucket/{endpoint}/x.ndjson"


class FakeLoader:
    def __init__(self):
        self.loads = []

    def load_ndjson_uri(self, table, uri):
        self.loads.append((table, uri))
        return 1


def _settings():
    return Settings(project_id="p", api_key="k", landing_bucket="b", top_n=3, ohlc_top_n=2)


def test_hourly_mode_ingests_three_endpoints():
    writer, loader = FakeWriter(), FakeLoader()
    summary = main.run("hourly", _settings(), FakeClient(), writer, loader, now=TS, run_id="r1")
    assert set(summary) == {"coin_markets", "market_global", "trending"}
    tables = {t for t, _ in loader.loads}
    assert tables == {"coin_markets", "market_global", "trending"}


def test_daily_mode_ingests_ohlc_and_metadata_for_top_n():
    writer, loader = FakeWriter(), FakeLoader()
    summary = main.run("daily", _settings(), FakeClient(), writer, loader, now=TS, run_id="r1")
    assert set(summary) == {"coin_ohlc", "coin_metadata"}
    # ohlc_top_n=2 → 2 monedas, cada una 1 vela → tabla coin_ohlc cargada una vez
    assert ("coin_ohlc", "gs://bucket/coin_ohlc/x.ndjson") in loader.loads


def test_empty_payload_is_not_loaded():
    class EmptyClient(FakeClient):
        def get_trending(self):
            return []

    writer, loader = FakeWriter(), FakeLoader()
    summary = main.run("hourly", _settings(), EmptyClient(), writer, loader, now=TS, run_id="r1")
    assert summary["trending"] == 0
    assert ("trending", None) not in [(t, None) for t, _ in loader.loads]
