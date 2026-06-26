-- Serie temporal OHLC limpia: deduplica por (coin_id, open_time) quedándose con la
-- ingesta más reciente.
WITH ranked AS (
  SELECT
    coin_id,
    open_time,
    open,
    high,
    low,
    close,
    ingestion_time,
    ROW_NUMBER() OVER (
      PARTITION BY coin_id, open_time
      ORDER BY ingestion_time DESC
    ) AS rn
  FROM `${raw}.coin_ohlc`
)
SELECT
  coin_id,
  open_time,
  open,
  high,
  low,
  close
FROM ranked
WHERE rn = 1
