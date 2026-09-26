# ClearSip project handoff

**Last updated:** 2026-09-26
**Repository:** `Shubham080802/ClearSip` (public; `main` is pushed)
**Local path:** `/Users/shubhamkumar/Documents/GITHUB Projects/ClearSip`

## Current state

The Vite MVP builds with `npm run build`; it supports text, image OCR, selected-video-frame OCR, browser speech recognition, source-backed discovery lookup, and exact typed GTIN/UPC lookup. The browser queries the FastAPI/SQL catalog through Vite's local `/api` proxy, with a reviewed static fallback only if the API is unavailable. Production is live at `https://clear-sip-gules.vercel.app/` with managed PostgreSQL. There are two detailed US package-label seed products and 85 source-backed catalog discoveries awaiting exact label verification, for 87 total records across 23 categories.

## Important implementation choices

- `src/data.js` is a deliberately small reviewed fallback; `src/catalog-api.js` adapts sourced API records to the browser UI.
- `api/index.py` exports the Vercel-compatible FastAPI app. `migrations/` is the immutable production schema history; `data/schema.sql` remains the local-bootstrap schema.
- The catalog is normalized as manufacturer → family → variant → package → label version → ingredient assessment. Read `CONTEXT.md` before changing those terms.
- [US beverage catalog source research](docs/research/us-beverage-catalog-sources.md) selects USDA FoodData Central Branded Foods as the lawful nationwide discovery baseline. Do not bulk scrape manufacturer pages.
- [Initial portfolio research](docs/research/initial-us-beverage-portfolio.md) provides public source links and package-size evidence for the original 29 discoveries. [Coffee label starter research](docs/research/coffee-label-starter-batch.md) documents the 21 coffee additions, and [diverse non-coffee expansion research](docs/research/diverse-noncoffee-expansion-batch.md) documents the 35 additional discoveries. A candidate has no inferred ingredients; only reviewed label versions receive assessments.
- `scripts/bootstrap_db.py` seeds local SQLite and is destructive. Production must use a PostgreSQL `DATABASE_URL` and `scripts/migrate_db.py`; never depend on SQLite persistence in a Vercel Function or run the bootstrap against production.
- OCR is processed in the browser with Tesseract.js; uploads are not persisted by this app.
- Voice recognition relies on `SpeechRecognition`/`webkitSpeechRecognition`, which is browser-dependent.
- Video scanning extracts one central/early frame. It is a useful MVP, not a guarantee that every frame is read.
- Monster’s full ingredient panel is marked provisional in the dataset because only core facts came from the manufacturer product page. Verify with an in-hand label or a manufacturer label source before public release.
- `src/scan-guardrails.js` rejects unsupported, empty, and oversized media before browser OCR. `vercel.json` also contains the deployed content-security and browser-permissions policy.
- `.github/workflows/refresh-fdc.yml` is a manual, controlled FoodData Central importer for PostgreSQL or SQLite. It must not run until `CLEARSIP_DATABASE_URL` and `FDC_API_KEY` are configured as GitHub repository secrets.

## Non-negotiable guardrails

- Never call a beverage or ingredient universally healthy, unhealthy, safe, unsafe, insulin-spiking, or non-insulin-spiking.
- Keep product facts separate from sourced general context and from unknowns.
- Keep the PKU/phenylalanine label notice for Coca-Cola Zero Sugar.
- Never compute sweetener ADI percentages without a disclosed sweetener amount.
- Record market, package size, source URL, accessed date, verification state, and label version for every future item.

## Remaining work requiring external authority

1. Add `CLEARSIP_DATABASE_URL` and `FDC_API_KEY` in GitHub, then run the manual FDC workflow with focused queries. A nationwide import requires a dedicated, reviewed external worker—not a Vercel Function.
2. Choose an authentication/reviewer model before implementing write APIs for discovery → reviewed → published states. Do not expose production write endpoints without it.
3. Obtain qualified nutrition, clinical, and regulatory review of consumer-facing assessment language before a broad public health launch.
4. Choose a support/contact channel before adding label-mismatch reporting; do not invent or publish a personal email address.

## Usage-limit continuation instruction

When a Codex five-hour window is below 5% and the active task reaches a clean stopping point: make sure `npm run build` passes, commit all completed changes in a focused commit, push the branch, update this file with status and next task, then create a concise task handover citing this file. Do not claim a background continuation is automatic—the next agent must be explicitly started after the usage window allows it.
