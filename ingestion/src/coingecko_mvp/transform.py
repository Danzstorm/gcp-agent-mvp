"""Normalización de respuestas CoinGecko a filas listas para NDJSON.

Estrategia de capa raw (bronze):
- Tablas "documento" (markets, global, trending, metadata): cada fila es
  {ingestion_time, payload} donde payload es el objeto JSON crudo. Robusto ante
  cambios de esquema de la API.
- Tabla OHLC: estructurada (coin_id, open_time, open, high, low, close) porque la
  respuesta es un array de números sin nombres.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def _iso(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat()


def document_rows(payload: Any, ts: datetime) -> list[dict]:
    """Envuelve uno o varios objetos crudos con su ingestion_time.

    Si `payload` es una lista, genera una fila por elemento; si es un objeto, una sola fila.
    """
    iso = _iso(ts)
    items = payload if isinstance(payload, list) else [payload]
    return [{"ingestion_time": iso, "payload": item} for item in items]


def ohlc_rows(coin_id: str, candles: list[list], ts: datetime) -> list[dict]:
    """Convierte velas [open_time_ms, o, h, l, c] en filas estructuradas."""
    iso = _iso(ts)
    rows: list[dict] = []
    for c in candles:
        open_time = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc).isoformat()
        rows.append(
            {
                "ingestion_time": iso,
                "coin_id": coin_id,
                "open_time": open_time,
                "open": c[1],
                "high": c[2],
                "low": c[3],
                "close": c[4],
            }
        )
    return rows


def to_ndjson(rows: list[dict]) -> str:
    """Serializa filas a NDJSON (un JSON por línea, sin línea final vacía)."""
    return "\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows)
