-- Snapshot más reciente por moneda desde coin_markets (1 fila por coin_id).
WITH ranked AS (
  SELECT
    payload,
    ingestion_time,
    ROW_NUMBER() OVER (
      PARTITION BY JSON_VALUE(payload, '$.id')
      ORDER BY ingestion_time DESC
    ) AS rn
  FROM `${raw}.coin_markets`
)
SELECT
  JSON_VALUE(payload, '$.id')                                          AS coin_id,
  JSON_VALUE(payload, '$.symbol')                                      AS symbol,
  JSON_VALUE(payload, '$.name')                                        AS name,
  CAST(JSON_VALUE(payload, '$.current_price') AS FLOAT64)              AS current_price_usd,
  CAST(JSON_VALUE(payload, '$.market_cap') AS FLOAT64)                 AS market_cap_usd,
  CAST(JSON_VALUE(payload, '$.market_cap_rank') AS INT64)              AS market_cap_rank,
  CAST(JSON_VALUE(payload, '$.total_volume') AS FLOAT64)              AS total_volume_usd,
  CAST(JSON_VALUE(payload, '$.price_change_percentage_24h') AS FLOAT64) AS price_change_pct_24h,
  CAST(JSON_VALUE(payload, '$.circulating_supply') AS FLOAT64)         AS circulating_supply,
  SAFE.TIMESTAMP(JSON_VALUE(payload, '$.last_updated'))                AS last_updated,
  ingestion_time
FROM ranked
WHERE rn = 1
