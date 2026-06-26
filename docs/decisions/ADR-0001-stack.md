# ADR-0001 — Stack y decisiones de arquitectura

- **Estado**: Aceptado
- **Fecha**: 2026-06-26

## Contexto

MVP práctico: ingestar datos de CoinGecko, llevarlos a BigQuery y permitir preguntas en
lenguaje natural sobre ellos. Usuario con cuenta GCP existente, en Windows. Objetivo
secundario: trabajar ordenado con MCP/agents/skills y documentar para generar PPTs.

## Decisiones

### 1. Agente = Conversational Analytics API (CA API) data agent
- **Por qué**: el usuario quiere agente Gemini/Vertex **nativo**. La CA API es purpose-built para
  Q&A NL→SQL sobre BigQuery, mínimo código, integración nativa.
- **Alternativas**: ADK + BigQuery Toolset (más control, más código); BigQuery data agents
  embebidos. Se prefiere CA API por encaje directo con "hacer preguntas".

### 2. Ingesta = batch programado (Cloud Run Job + Cloud Scheduler)
- **Por qué**: datos de mercado no requieren streaming; batch es simple, barato y cabe en el
  free tier de CoinGecko. Cloud Run Job escala a cero.
- **Alternativa**: near real-time con Pub/Sub (descartado por complejidad/costo innecesarios).

### 2b. Landing en GCS antes de BigQuery (bronze → silver)
- **Por qué**: patrón pipeline/medallion. El job escribe NDJSON crudo a GCS, luego `bq load` a tablas
  nativas. Da **replay** (recargar BQ sin re-llamar CoinGecko → ahorra rate limit), desacopla
  ingesta de carga, y deja audit trail inmutable.
- **Variante elegida**: GCS + **load jobs** a tablas nativas (queries rápidas para el agente), sobre
  tablas externas/BigLake (más baratas pero más lentas).
- **Bucket**: `force_destroy=true`, versioning OFF, lifecycle 90d — desmontable y sin acumulación.

### 3. IaC = Terraform (+ gcloud para ops puntuales)
- **Por qué**: declarativo, versionado, reproducible → orden y precisión. gcloud para bootstrap
  y tareas one-off (auth, ejecuciones manuales).

### 4. Build = Cloud Build (sin Docker local)
- **Por qué**: usuario en Windows; evita dependencia de Docker Desktop. Imagen a Artifact Registry.

### 5. Región = us-central1, BigQuery US multi-región
- **Por qué**: mejor disponibilidad de CA API / Vertex / Cloud Run.

### 6. Capa curated = vistas (MVP)
- **Por qué**: simple y sin costo de materialización. Migrar a tablas si el volumen/latencia lo pide.

### 7. Convenciones de teardown (poder desmontar limpio)
- **Backend Terraform local** (no GCS). Más simple para MVP; sin bucket de state que gestionar.
- **`delete_contents_on_destroy = true`** en datasets BigQuery → `terraform destroy` funciona aunque
  tengan tablas/datos.
- Si en el futuro se añade un bucket GCS: **`force_destroy = true`** y **versioning desactivado**
  (con versioning ON, el destroy falla por objetos versionados).
- **Toda la IaC vive en `infra/`** (nada en la raíz del repo). Un solo `terraform apply`/`destroy`.

## Consecuencias

- Stack 100% serverless/managed → bajo mantenimiento.
- Dependencia de disponibilidad de CA API en la región elegida (verificar en Fase 3).
- Free tier CoinGecko impone límites de cadencia (ver `architecture.md`).
