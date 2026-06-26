# Imagen del Cloud Run Job de ingesta. Build vía Cloud Build (sin Docker local).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instalar dependencias primero (capa cacheable)
COPY pyproject.toml ./
COPY src ./src
RUN pip install .

# Entrypoint: el módulo de orquestación. El --mode lo fija cada Cloud Run Job.
ENTRYPOINT ["python", "-m", "coingecko_mvp.main"]
CMD ["--mode", "hourly"]
