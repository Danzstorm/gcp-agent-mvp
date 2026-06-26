"""Tests de la normalización a filas NDJSON."""

import json
from datetime import datetime, timezone

from coingecko_mvp import transform

TS = datetime(2026, 6, 26, 12, 0, 0, tzinfo=timezone.utc)


def test_document_rows_wrap_payload_with_ingestion_time():
    markets = [{"id": "bitcoin"}, {"id": "ethereum"}]
    rows = transform.document_rows(markets, ts=TS)
    assert len(rows) == 2
    assert rows[0]["ingestion_time"] == "2026-06-26T12:00:00+00:00"
    assert rows[0]["payload"] == {"id": "bitcoin"}


def test_document_rows_accepts_single_object():
    rows = transform.document_rows({"active_cryptocurrencies": 12000}, ts=TS)
    assert len(rows) == 1
    assert rows[0]["payload"]["active_cryptocurrencies"] == 12000


def test_ohlc_rows_structured():
    candles = [[1719403200000, 64000.0, 65000.0, 63500.0, 64800.0]]
    rows = transform.ohlc_rows("bitcoin", candles, ts=TS)
    assert rows[0]["coin_id"] == "bitcoin"
    assert rows[0]["open"] == 64000.0
    assert rows[0]["close"] == 64800.0
    # open_time convertido de epoch ms a ISO UTC (1719403200000 ms = 2024-06-26 12:00 UTC)
    assert rows[0]["open_time"] == "2024-06-26T12:00:00+00:00"
    assert rows[0]["ingestion_time"] == "2026-06-26T12:00:00+00:00"


def test_to_ndjson_is_one_json_per_line():
    rows = [{"a": 1}, {"b": 2}]
    text = transform.to_ndjson(rows)
    lines = text.splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"a": 1}


def test_to_ndjson_empty_is_empty_string():
    assert transform.to_ndjson([]) == ""
