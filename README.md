# ClearSip

ClearSip is an early, educational beverage-label awareness app. A user can type a product name, scan a label image, scan a frame from a video, or say a drink name. The app matches a versioned dataset and explains each declared ingredient in plain language, with source links and clear uncertainty.

## What is in this MVP

- Text lookup for Coca-Cola Zero Sugar and Monster Energy Zero Sugar (US seed records)
- Local, in-browser OCR for a product image and a selected video frame
- Browser-native speech recognition for a spoken drink name
- Product facts separated from interpretive context
- Ingredient roles, amount/context caveats, FDA sources, source dates, and formulation-region notes
- A research note documenting approved sources and health-language guardrails

## Architecture

```text
Chrome browser UI  →  FastAPI `/api`  →  PostgreSQL (production)
       │                    │
       └── OCR / voice      └── SQLite (local-only development)
```

- The frontend is a small Vite application. It stays browser-first for scanning and voice capture.
- [`api/index.py`](api/index.py) exports the FastAPI app that Vercel can deploy as a Python Function.
- [`data/schema.sql`](data/schema.sql) is the relational source of truth for products, ingredients, and their product-specific assessments.
- The catalog keeps **manufacturer → beverage family → variant/flavor → market-specific package → dated label version** separate. A 12 oz can and a 20 oz bottle are never silently treated as one item.
- SQLite is deliberately local-only. Vercel functions have no durable local disk, so production must receive a PostgreSQL `DATABASE_URL` from a managed provider.

## Run locally

```bash
npm install
npm run dev
```

Then open the local Vite address shown in the terminal. For a production check, run `npm run build`.

For the API and local SQL seed:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/bootstrap_db.py
.venv/bin/uvicorn api.index:app --reload
```

The API is then available at `http://127.0.0.1:8000/api/health` and its interactive docs at `http://127.0.0.1:8000/docs`.

## Chrome-first and Vercel workflow

Chrome can be your primary working surface: use GitHub's web editor (`github.dev`) for simple source changes, the Vercel dashboard for deployments and environment variables, and Vercel preview URLs to test each pushed commit. The Git repository remains the authoritative source, so browser-made edits should still be committed to GitHub.

When you are ready to deploy, import the GitHub repository into Vercel from Chrome. Vercel can deploy FastAPI as a Python Function. Add a Marketplace PostgreSQL integration (for example, Neon) and set its injected `DATABASE_URL`; do not deploy with the local SQLite database. No Vercel project or database has been created by this repository.

## Data safety and provenance

The seed dataset is intentionally small. See [the research note](docs/research/seed-data-sources.md) before adding records. In particular:

- Use a manufacturer product page, manufacturer label PDF, or the package itself as the product source; a retailer transcription is only a provisional lead.
- Record market, package size, source URL, access date, verification state, and formulation/version with every item.
- Do not classify ingredients as universally “good,” “bad,” “harmful,” or “beneficial.” Present a label fact, its function, the known quantity, applicable authoritative context, and uncertainty separately.
- Do not calculate an ADI percentage unless the label or manufacturer actually discloses the ingredient amount.
- Do not retain user images or videos in this MVP. OCR occurs in the browser and the upload is not sent to an application server.

## Nationwide catalog coverage

The goal is **all discoverable, currently sold packaged non-alcoholic beverages in the United States**, not an unprovable claim that every beverage ever produced is included. The lawful nationwide baseline will be USDA FoodData Central's public-domain Branded Foods data, then verified and refreshed with package observations, authorized manufacturer label sources, and licensed barcode/product-data sources where required.

The full acquisition, licensing, and update plan is in [the US beverage catalog research note](docs/research/us-beverage-catalog-sources.md). It establishes these rules:

- FoodData Central provides broad coverage, but manufacturer submissions are voluntary, so every record retains a source and verification state.
- A GTIN/UPC identifies a **package**, not automatically a formula. GS1-scale lookup needs the appropriate commercial access/licence.
- Do not bulk-scrape or republish manufacturer pages, product images, logos, or marketing copy. Manufacturer facts are used for review and provenance only where permitted.
- A Vercel Function is not the place for a nationwide bulk import. Run FoodData Central import/update jobs in a dedicated worker, then connect the resulting PostgreSQL database to Vercel.

## Recommended next steps

1. Connect the browser UI to the FastAPI read endpoints, replacing its temporary client-side seed lookup.
2. Build the external FoodData Central ETL worker and its PostgreSQL migration, beginning with current US branded beverage records.
3. Add barcode lookup (for exact package-size matching) and a reviewed “unmatched label” queue.
4. Add auth, consent, retention controls, and a moderation/review workflow before retaining any uploads.
5. Have qualified regulatory and nutrition reviewers approve user-facing assessment language before public release.
6. Add food products only after the beverage source/provenance workflow is stable.

## Scope statement

ClearSip provides educational label information, not medical advice. Food suitability can change with allergies, medications, pregnancy, age, health conditions, and total dietary intake.
