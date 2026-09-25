# ClearSip project handoff

**Last updated:** 2026-09-24  
**Repository:** `Shubham080802/ClearSip` (private; `main` is pushed)
**Local path:** `/Users/shubhamkumar/Documents/GITHUB Projects/ClearSip`

## Current state

The initial Vite MVP builds with `npm run build`; it supports text, image OCR, selected-video-frame OCR, and browser speech recognition. A FastAPI/SQL foundation is now also in place and has been validated against locally seeded SQLite. The only seed products are US Coca-Cola Zero Sugar and Monster Energy Zero Sugar.

## Important implementation choices

- `src/data.js` is a deliberately small, versioned seed dataset.
- `api/index.py` exports the Vercel-compatible FastAPI app; `data/schema.sql` models products, ingredients, and product-specific assessments.
- The catalog is normalized as manufacturer → family → variant → package → label version → ingredient assessment. Read `CONTEXT.md` before changing those terms.
- [US beverage catalog source research](docs/research/us-beverage-catalog-sources.md) selects USDA FoodData Central Branded Foods as the lawful nationwide discovery baseline. Do not bulk scrape manufacturer pages.
- `scripts/bootstrap_db.py` seeds local SQLite. Production must use a PostgreSQL `DATABASE_URL` from a Vercel Marketplace database integration; never depend on SQLite persistence in a Vercel Function.
- OCR is processed in the browser with Tesseract.js; uploads are not persisted by this app.
- Voice recognition relies on `SpeechRecognition`/`webkitSpeechRecognition`, which is browser-dependent.
- Video scanning extracts one central/early frame. It is a useful MVP, not a guarantee that every frame is read.
- Monster’s full ingredient panel is marked provisional in the dataset because only core facts came from the manufacturer product page. Verify with an in-hand label or a manufacturer label source before public release.

## Non-negotiable guardrails

- Never call a beverage or ingredient universally healthy, unhealthy, safe, unsafe, insulin-spiking, or non-insulin-spiking.
- Keep product facts separate from sourced general context and from unknowns.
- Keep the PKU/phenylalanine label notice for Coca-Cola Zero Sugar.
- Never compute sweetener ADI percentages without a disclosed sweetener amount.
- Record market, package size, source URL, accessed date, verification state, and label version for every future item.

## Next recommended task

Connect the browser lookup to `GET /api/products` and `GET /api/products/{id}`, then build a separate FoodData Central ETL worker into production PostgreSQL. It must retain FDC ID, source release, fetch time, source hash, package/GTIN, market, label version, and verification state. Do not run nationwide import inside Vercel Functions or collect/retain consumer uploads without explicit consent and documented retention/deletion controls.

## Usage-limit continuation instruction

When a Codex five-hour window is below 5% and the active task reaches a clean stopping point: make sure `npm run build` passes, commit all completed changes in a focused commit, push the branch, update this file with status and next task, then create a concise task handover citing this file. Do not claim a background continuation is automatic—the next agent must be explicitly started after the usage window allows it.
