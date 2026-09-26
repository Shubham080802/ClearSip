# ClearSip

ClearSip is an early, educational beverage-label awareness app. A user can type a product name, scan a label image, scan a frame from a video, or say a drink name. The app matches a versioned dataset and explains each declared ingredient in plain language, with source links and clear uncertainty.

## What is in this MVP

- API-backed text lookup against the versioned local SQL catalog, with reviewed seed-label fallback when the API is unavailable
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

For the API, local SQL seed, and browser app:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/bootstrap_db.py
.venv/bin/uvicorn api.index:app --reload
npm install
npm run dev
```

The API is available at `http://127.0.0.1:8000/api/health` and its interactive docs at `http://127.0.0.1:8000/docs`. Vite proxies `/api` to that local server, so the browser application reads the same catalog that will be deployed on Vercel. For a production check, run `npm run build`.

### Production database migrations

[`migrations/`](migrations) is the immutable production schema history. Apply
it as a separate deployment step using the Production `DATABASE_URL`; it is
idempotent, verifies the checksum of every already-applied migration, and
uses a PostgreSQL advisory lock to prevent simultaneous deploys from racing.

```bash
DATABASE_URL=postgresql://... .venv/bin/python scripts/migrate_db.py
```

Never run `scripts/bootstrap_db.py` against production: it deliberately drops
and recreates the local development database. Add a new numbered migration for
each production schema change; never edit an applied migration.

### Label assessment and dataset refresh

Each current package label receives a transparent assessment of the disclosed
facts: added sugar, saturated fat, sodium, caffeine context, and any visible
`Zero Sugar` / `sugar-free`, `preservative-free`, or `healthy` claim. It does
not assign a universal "healthy" or "unhealthy" label, make a disease claim,
or certify legal compliance. The full rules and language safeguards are in
[the classification policy](docs/research/beverage-classification-policy.md).

Recalculate all local assessments after changing labels or rules:

```bash
.venv/bin/python scripts/rebuild_assessments.py
```

For a focused, reviewable USDA FoodData Central Branded Foods discovery import,
provide a personal Data.gov API key (never commit it):

```bash
FDC_API_KEY=your-key .venv/bin/python scripts/import_fdc.py --query "Pepsi Zero Sugar" --page-size 20
```

`--demo` is only suitable for tiny local experiments. The importer rejects
non-beverage categories, retains the raw FDC ingredient statement and ID, and
marks records `catalog_label_match`; it never turns an FDC search hit into a
package-verified label. Use the offline FDC Branded Foods release in a worker
for a nationwide backfill, not a Vercel request.

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

### Current catalog status

The local development dataset now has two **package-label records** with ingredient assessments and 29 **source-backed catalog discoveries** across Coca-Cola, Sprite, Powerade, Dasani, Pepsi, Mountain Dew, Gatorade, Aquafina, Monster, Red Bull, Keurig Dr Pepper brands, and LaCroix. Discovery records retain available size evidence and a source link, but intentionally have no guessed ingredient panel. They graduate to package-label records only after the exact US package/label is verified.

See [the initial portfolio list](docs/research/initial-us-beverage-portfolio.md) for the beverage families, flavors, package-size evidence, and verification status.

## Recommended next steps

1. Add a result-selection step when a search returns multiple packages, then add barcode lookup for exact package-size matching.
2. Build the external FoodData Central ETL worker and PostgreSQL migration, beginning with current US branded beverage records.
3. Add auth, consent, retention controls, and a moderation/review workflow before retaining any uploads.
4. Have qualified regulatory and nutrition reviewers approve user-facing assessment language before public release.
5. Add food products only after the beverage source/provenance workflow is stable.

## Scope statement

ClearSip provides educational label information, not medical advice. Food suitability can change with allergies, medications, pregnancy, age, health conditions, and total dietary intake.
