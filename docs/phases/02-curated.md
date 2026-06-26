# Fase 2 — Capa curated (BigQuery)

Objetivo: vistas limpias y tipadas sobre `coingecko_raw` para que el agente consulte.

## Vistas creadas (`coingecko_curated`, vía Terraform módulo `curated`)

SQL parametrizado en `transform/sql/`, inyectado con `templatefile` (var `${raw}`).

| Vista | Fuente raw | Qué da |
|---|---|---|
| `latest_prices` | coin_markets | Snapshot más reciente por moneda: precio, market cap, rank, volumen, %24h, supply |
| `dim_coin` | coin_metadata | Dimensión: símbolo, nombre, rank, `categories` (ARRAY) |
| `ohlc_timeseries` | coin_ohlc | Serie OHLC deduplicada por (coin_id, open_time) |
| `market_global_daily` | market_global | Resumen diario: activos, market cap, volumen, dominancia BTC/ETH |

Patrón común: `ROW_NUMBER() OVER (PARTITION BY <clave> ORDER BY ingestion_time DESC)` → fila más
reciente. Las vistas son MVP (sin materializar); migrar a tablas si se necesita rendimiento.

## Verificación ✅ (2026-06-26)
- `latest_prices`: BTC $59,861 (rank 1), ETH, USDT, BNB, USDC ordenados por rank.
- `dim_coin`: categorías parseadas (BTC 8, ETH 15, USDT 17).
- `ohlc_timeseries`: 42 velas/moneda (7 días), rango de fechas correcto.
- `market_global_daily`: 17,449 monedas activas, BTC dom 55.7%, market cap $2.14T.

## Notas
- Las vistas se recalculan al consultarse (siempre frescas respecto a raw).
- Si CoinGecko cambia campos del payload, solo se ajusta el SQL (raw queda intacto → replay).
