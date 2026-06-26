"""Tests del cliente CoinGecko (mockeando httpx con pytest-httpx)."""

import httpx
import pytest

from coingecko_mvp.client import CoinGeckoClient, CoinGeckoError

BASE = "https://api.coingecko.com/api/v3"


@pytest.fixture
def client():
    return CoinGeckoClient(api_key="CG-test", base_url=BASE, timeout=5.0, max_retries=2)


def test_sends_demo_api_key_header(client, httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/ping", json={"gecko_says": "ok"})
    client.ping()
    req = httpx_mock.get_request()
    assert req.headers["x-cg-demo-api-key"] == "CG-test"


def test_get_markets_returns_list(client, httpx_mock):
    payload = [
        {"id": "bitcoin", "symbol": "btc", "current_price": 65000, "market_cap": 1_200_000_000_000},
        {"id": "ethereum", "symbol": "eth", "current_price": 3500, "market_cap": 420_000_000_000},
    ]
    httpx_mock.add_response(
        url=f"{BASE}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1",
        json=payload,
    )
    rows = client.get_markets(per_page=250, page=1)
    assert len(rows) == 2
    assert rows[0]["id"] == "bitcoin"


def test_get_global_returns_data(client, httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/global",
        json={"data": {"active_cryptocurrencies": 12000, "market_cap_percentage": {"btc": 52.1}}},
    )
    data = client.get_global()
    assert data["active_cryptocurrencies"] == 12000


def test_get_trending_returns_coins(client, httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/search/trending",
        json={"coins": [{"item": {"id": "pepe", "market_cap_rank": 30}}]},
    )
    coins = client.get_trending()
    assert coins[0]["item"]["id"] == "pepe"


def test_get_ohlc_returns_candles(client, httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/coins/bitcoin/ohlc?vs_currency=usd&days=7",
        json=[[1719360000000, 64000, 65000, 63500, 64800]],
    )
    candles = client.get_ohlc("bitcoin", days=7)
    assert candles[0][1] == 64000


def test_retries_on_429_then_succeeds(client, httpx_mock):
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429)
        return httpx.Response(200, json={"gecko_says": "ok"})

    httpx_mock.add_callback(handler, url=f"{BASE}/ping", is_reusable=True)
    assert client.ping() == {"gecko_says": "ok"}
    assert calls["n"] == 2


def test_raises_after_exhausting_retries(client, httpx_mock):
    httpx_mock.add_callback(
        lambda request: httpx.Response(500), url=f"{BASE}/ping", is_reusable=True
    )
    with pytest.raises(CoinGeckoError):
        client.ping()
