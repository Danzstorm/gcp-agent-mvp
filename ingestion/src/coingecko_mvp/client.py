"""Cliente HTTP de la API CoinGecko (plan Demo).

- Autentica con el header `x-cg-demo-api-key`.
- Reintenta en 429 (rate limit) y 5xx con backoff exponencial (tenacity).
- Convierte fallos definitivos en `CoinGeckoError`.
"""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import COINGECKO_BASE_URL

# Status que justifican reintento.
_RETRY_STATUS = {429, 500, 502, 503, 504}


class CoinGeckoError(RuntimeError):
    """Error definitivo al hablar con CoinGecko (tras agotar reintentos)."""


class _Retryable(Exception):
    """Marca interna para que tenacity reintente."""


class CoinGeckoClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = COINGECKO_BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 4,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._http = httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            headers={"x-cg-demo-api-key": api_key, "accept": "application/json"},
        )

    # --- transporte ---

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        @retry(
            reraise=True,
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=0.5, max=8),
            retry=retry_if_exception_type(_Retryable),
        )
        def _do() -> Any:
            try:
                resp = self._http.get(path, params=params)
            except httpx.TransportError as exc:
                raise _Retryable(str(exc)) from exc
            if resp.status_code in _RETRY_STATUS:
                raise _Retryable(f"status {resp.status_code}")
            if resp.status_code >= 400:
                raise CoinGeckoError(f"{resp.status_code} en {path}: {resp.text[:200]}")
            return resp.json()

        try:
            return _do()
        except _Retryable as exc:
            raise CoinGeckoError(f"Reintentos agotados en {path}: {exc}") from exc

    # --- endpoints ---

    def ping(self) -> dict[str, Any]:
        return self._get("/ping")

    def get_markets(self, per_page: int = 250, page: int = 1, vs_currency: str = "usd") -> list[dict]:
        return self._get(
            "/coins/markets",
            params={
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": per_page,
                "page": page,
            },
        )

    def get_global(self) -> dict[str, Any]:
        return self._get("/global")["data"]

    def get_trending(self) -> list[dict]:
        return self._get("/search/trending")["coins"]

    def get_ohlc(self, coin_id: str, days: int = 7, vs_currency: str = "usd") -> list[list]:
        return self._get(
            f"/coins/{coin_id}/ohlc",
            params={"vs_currency": vs_currency, "days": days},
        )

    def get_coin(self, coin_id: str) -> dict[str, Any]:
        return self._get(
            f"/coins/{coin_id}",
            params={
                "localization": "false",
                "tickers": "false",
                "market_data": "false",
                "community_data": "false",
                "developer_data": "false",
            },
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "CoinGeckoClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
