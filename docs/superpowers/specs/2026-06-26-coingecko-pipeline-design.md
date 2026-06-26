# Spec de diseño — Pipeline CoinGecko → BigQuery → Agente Q&A

- **Fecha**: 2026-06-26
- **Estado**: Aprobado (plan ejecutándose)
- **Plan completo**: `~/.claude/plans/mighty-drifting-ullman.md`

Este spec resume el diseño aprobado. Para detalle de arquitectura ver
[`docs/architecture.md`](../../architecture.md); decisiones en
[`docs/decisions/ADR-0001-stack.md`](../../decisions/ADR-0001-stack.md).

## Objetivo

Ingestar CoinGecko (batch) → BigQuery (raw → curated) → agente Gemini/Vertex nativo
(Conversational Analytics API) para Q&A en lenguaje natural.

## Alcance (MVP)

- **Datos**: precios spot top coins, OHLC histórico (top 50), metadata, trending, market global.
- **Cadencia**: hourly (markets/global/trending), daily (ohlc/metadata).
- **No incluye**: streaming, alertas, dashboards, frontend propio.

## Fases

0. Fundaciones (GCP + scaffold + Terraform skeleton + MCP).
1. Ingestión MVP (TDD): cliente CoinGecko, loaders BQ, Cloud Run Job, Scheduler.
2. Capa curated (vistas SQL).
3. Agente CA API sobre curated.
4. Documentación → PPT.

## Criterios de éxito

- Datos reales fluyendo a `coingecko_raw` y visibles en `coingecko_curated`.
- Data Agent responde ≥5 preguntas NL con SQL correcto.
- `pytest` verde; infra reproducible con `terraform apply`.
- Documentación por fase lista para generar deck.

## Decisiones abiertas (resolver en ejecución)

- PROJECT_ID del proyecto existente.
- Nº de monedas OHLC en MVP (default top 50).
- Curated vistas vs tablas (default vistas).
