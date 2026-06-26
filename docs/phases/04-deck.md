# Fase 4 — Documentación → PPT

Objetivo: dejar la documentación lista para generar presentaciones.

## Estructura de docs (fuente del deck)

```
docs/
├── architecture.md              # arquitectura + diagrama + flujo de datos
├── decisions/ADR-0001-stack.md  # decisiones razonadas
├── phases/
│   ├── 00-foundations.md
│   ├── 01-ingestion.md
│   ├── 02-curated.md
│   ├── 03-agent.md
│   └── 04-deck.md               # este archivo
└── deck/
    └── coingecko-pipeline-deck.md  # DECK en formato Marp (1 slide por sección)
```

El deck (`docs/deck/coingecko-pipeline-deck.md`) está en **Marp**: cada `---` separa una slide,
con front-matter `marp: true`. Cubre: problema, arquitectura, stack, patrón de datos, curated,
agente, demo con resultados reales, ingeniería, teardown y próximos pasos.

## Convertir el markdown a PPT

### Opción A — Marp (offline, genera .pptx / .pdf)
```bash
# Requiere Node. Genera PowerPoint:
npx @marp-team/marp-cli docs/deck/coingecko-pipeline-deck.md --pptx -o coingecko-deck.pptx
# o PDF:
npx @marp-team/marp-cli docs/deck/coingecko-pipeline-deck.md --pdf
```
También hay extensión "Marp for VS Code" para previsualizar y exportar.

### Opción B — Gamma (IA, diseño automático)
Pegar el contenido del deck en Gamma (gamma.app) → genera slides con diseño automático.
Hay un MCP de Gamma disponible para automatizarlo.

### Opción C — Google Slides
Importar el .pptx generado por Marp a Google Slides (Archivo → Importar).

## Recomendación

Para iterar rápido y mantener el deck **versionado en git**: editar el markdown Marp y exportar
con Marp CLI. Para una versión "bonita" de presentación ejecutiva: pasar por Gamma.

## Estado ✅
- Deck Marp completo con datos reales del MVP + slides de ambos agentes (CA API + ADK Engine).
- Documentación por fase completa (00–05) — fuente reutilizable para cualquier formato.
- Fase 05 cubre ADK Agent Engine: deploy, verificación, uso desde CLI y consola GCP.
