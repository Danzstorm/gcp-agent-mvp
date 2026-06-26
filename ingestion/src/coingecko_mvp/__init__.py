"""Ingesta batch de CoinGecko hacia BigQuery.

Módulos (se implementan en Fase 1, TDD):
- config:     carga de configuración y secreto (Secret Manager).
- client:     cliente HTTP CoinGecko (Demo API), retries, rate-limit aware.
- transform:  normalización de respuestas a NDJSON (filas tipadas).
- gcs_writer: escribe NDJSON a GCS landing (endpoint/dt=fecha/ts.ndjson).
- bq_loader:  bq load del NDJSON de GCS a tablas nativas de coingecko_raw.
- main:       orquestación por modo (hourly / daily).
"""

__version__ = "0.1.0"
