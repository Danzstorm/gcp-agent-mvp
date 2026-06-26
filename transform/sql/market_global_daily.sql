-- Resumen global del mercado por día (última ingesta de cada día).
WITH ranked AS (
  SELECT
    payload,
    ingestion_time,
    DATE(ingestion_time) AS day,
    ROW_NUMBER() OVER (
      PARTITION BY DATE(ingestion_time)
      ORDER BY ingestion_time DESC
    ) AS rn
  FROM `${raw}.market_global`
)
SELECT
  day,
  CAST(JSON_VALUE(payload, '$.active_cryptocurrencies') AS INT64)      AS active_cryptocurrencies,
  CAST(JSON_VALUE(payload, '$.total_market_cap.usd') AS FLOAT64)       AS total_market_cap_usd,
  CAST(JSON_VALUE(payload, '$.total_volume.usd') AS FLOAT64)           AS total_volume_usd,
  CAST(JSON_VALUE(payload, '$.market_cap_percentage.btc') AS FLOAT64)  AS btc_dominance_pct,
  CAST(JSON_VALUE(payload, '$.market_cap_percentage.eth') AS FLOAT64)  AS eth_dominance_pct,
  ingestion_time
FROM ranked
WHERE rn = 1
