# ClearSip project handoff

**Last updated:** 2026-09-28
**Repository:** `Shubham080802/ClearSip` (public; `main` is pushed)
**Local path:** `/Users/shubhamkumar/Documents/GITHUB Projects/ClearSip`

## Current state

The Vite MVP builds with `npm run build`; it supports text, live browser-camera label capture, image OCR, selected-video-frame OCR, browser speech recognition, source-backed lookup, and typed GTIN/UPC lookup. Production is live at `https://clear-sip-gules.vercel.app/` with managed PostgreSQL. SQL has five package records and 85 catalog entries (overlapping, not additive). The latest all-entry audit supplies manufacturer variant ingredient panels for 79 entries; six remain pending and are marked before selection.

## Important implementation choices

- Visual recognition preparation (2026-09-28): `api/recognition.py` registers every catalog discovery plus package-only variants; currently 86 targets, 83 concrete drinks, three family leads. `/api/recognition-coverage` exposes status. No trained model/images exist. `ml/`, `scripts/train_recognizer.py`, and `docs/VISUAL_RECOGNITION.md` define permission-cleared photo manifests, leakage audits, cumulative classes, and evaluation/export gates. Training dependencies are isolated, proposed, and not installed/validated; do not install them in Vercel's API environment.
- Image scans now offer confirmable stable-ID candidates using OCR, optional browser-native barcode detection, and a lazy TensorFlow.js runtime only for an approved model. `public/models/drink-recognizer/release.json` stays inactive until genuine tests/device review pass. Ordinary user scans are not silently saved or uploaded for training. The next meaningful step is collecting authorized photos for the 12 priority-one variants plus unknown scenes; all other variants remain tracked, not falsely marked trained.

- `src/data.js` is a deliberately small reviewed fallback; `src/catalog-api.js` adapts sourced API records to the browser UI.
- `api/source_labels.py` validates committed `data/reviewed-labels-*.json` snapshots and supplements SQL with source panels. Vercel bundles them through `includeFiles`. A variant panel is NOT certification of each selectable package; nutrition stays per source serving, never silently scaled to bottle volume. Missing amounts remain null. Powerade Zero Mixed Berry now has a complete source statement.
- `docs/research/catalog-availability-audit.md` audits all 85 entries. Pending: Monster Zero Ultra, Red Bull Original, STōK Extra Bold, Snapple, Bai, LaCroix. Do not substitute another flavor or repair malformed source text by guessing. CI runs `tests/catalog_coverage.py` and `tests/catalog-coverage.test.mjs` across all entries and size options.
- `api/index.py` exports the Vercel-compatible FastAPI app. `migrations/` is the immutable production schema history; `data/schema.sql` remains the local-bootstrap schema.
- The catalog is normalized as manufacturer → family → variant → package → label version → ingredient assessment. Read `CONTEXT.md` before changing those terms.
- [US beverage catalog source research](docs/research/us-beverage-catalog-sources.md) selects USDA FoodData Central Branded Foods as the lawful nationwide discovery baseline. Do not bulk scrape manufacturer pages.
- [Initial portfolio research](docs/research/initial-us-beverage-portfolio.md) provides public source links and package-size evidence for the original 29 discoveries. [Coffee label starter research](docs/research/coffee-label-starter-batch.md) documents the 21 coffee additions, and [diverse non-coffee expansion research](docs/research/diverse-noncoffee-expansion-batch.md) documents the 35 additional discoveries. A candidate has no inferred ingredients; only reviewed label versions receive assessments.
- `scripts/bootstrap_db.py` seeds local SQLite and is destructive. Production must use a PostgreSQL `DATABASE_URL` and `scripts/migrate_db.py`; never depend on SQLite persistence in a Vercel Function or run the bootstrap against production.
- OCR is processed in the browser with Tesseract.js; uploads and camera frames are not persisted by this app. Camera access is requested only after the user presses **Scan with camera**.
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
