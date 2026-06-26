-- Dimensión de moneda: metadata más reciente por coin_id desde coin_metadata.
WITH ranked AS (
  SELECT
    payload,
    ingestion_time,
    ROW_NUMBER() OVER (
      PARTITION BY JSON_VALUE(payload, '$.id')
      ORDER BY ingestion_time DESC
    ) AS rn
  FROM `${raw}.coin_metadata`
)
SELECT
  JSON_VALUE(payload, '$.id')                              AS coin_id,
  JSON_VALUE(payload, '$.symbol')                          AS symbol,
  JSON_VALUE(payload, '$.name')                            AS name,
  CAST(JSON_VALUE(payload, '$.market_cap_rank') AS INT64)  AS market_cap_rank,
  ARRAY(
    SELECT c
    FROM UNNEST(JSON_EXTRACT_STRING_ARRAY(payload, '$.categories')) AS c
    WHERE c IS NOT NULL
  )                                                        AS categories,
  ingestion_time                                           AS metadata_ingested_at
FROM ranked
WHERE rn = 1
