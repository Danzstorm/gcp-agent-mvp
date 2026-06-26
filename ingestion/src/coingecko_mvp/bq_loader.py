"""Carga de NDJSON desde GCS a tablas nativas de BigQuery (load jobs).

Las tablas raw se crean por Terraform (módulo bigquery). Aquí solo se hace el load
con WRITE_APPEND. El esquema de cada tabla se define al crearla; el load respeta el
esquema existente.
"""

from __future__ import annotations

# Tablas "documento": columna payload JSON + ingestion_time.
DOCUMENT_TABLES = ("coin_markets", "market_global", "trending", "coin_metadata")
OHLC_TABLE = "coin_ohlc"


class BqLoader:
    def __init__(self, project: str, dataset: str, client=None) -> None:
        self._project = project
        self._dataset = dataset
        if client is None:
            from google.cloud import bigquery  # import perezoso

            client = bigquery.Client(project=project)
        self._client = client

    def load_ndjson_uri(self, table: str, gcs_uri: str) -> int:
        """Carga un objeto NDJSON de GCS a `dataset.table`. Devuelve filas cargadas."""
        from google.cloud import bigquery

        table_ref = f"{self._project}.{self._dataset}.{table}"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            ignore_unknown_values=False,
        )
        job = self._client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
        job.result()  # espera a que termine
        return job.output_rows or 0
