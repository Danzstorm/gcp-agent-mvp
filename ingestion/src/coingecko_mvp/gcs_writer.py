"""Escritura de NDJSON crudo a la landing zone de GCS.

Layout: gs://<bucket>/<endpoint>/dt=YYYY-MM-DD/<YYYYMMDDTHHMMSS>_<run_id>.ndjson
Particionar por fecha facilita el bq load y el lifecycle/retención.
"""

from __future__ import annotations

from datetime import datetime, timezone


def build_object_path(endpoint: str, ts: datetime, run_id: str) -> str:
    ts = ts.astimezone(timezone.utc)
    return f"{endpoint}/dt={ts:%Y-%m-%d}/{ts:%Y%m%dT%H%M%S}_{run_id}.ndjson"


class GcsWriter:
    def __init__(self, bucket: str, client=None) -> None:
        self._bucket_name = bucket
        if client is None:
            from google.cloud import storage  # import perezoso (no requerido en tests)

            client = storage.Client()
        self._client = client

    def write(self, endpoint: str, ts: datetime, run_id: str, ndjson: str) -> str:
        """Sube el NDJSON y devuelve el URI gs:// del objeto. Si está vacío, no sube y devuelve ''."""
        if not ndjson:
            return ""
        path = build_object_path(endpoint, ts, run_id)
        bucket = self._client.bucket(self._bucket_name)
        blob = bucket.blob(path)
        blob.upload_from_string(ndjson, content_type="application/x-ndjson")
        return f"gs://{self._bucket_name}/{path}"
