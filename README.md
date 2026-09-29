# ClearSip

### Know what’s in your next sip.

A source-backed beverage-label explorer for the US market. Search a drink, choose
a package size, or scan a label to see declared ingredients, nutrition facts,
and plain-language context—with the source and uncertainty kept visible.

[![Verify ClearSip](https://github.com/Shubham080802/ClearSip/actions/workflows/verify.yml/badge.svg)](https://github.com/Shubham080802/ClearSip/actions/workflows/verify.yml)
[![Code license: MIT](https://img.shields.io/badge/Code_license-MIT-blue.svg)](LICENSE)

[Live demo](https://clear-sip-gules.vercel.app/) · [Report an issue](https://github.com/Shubham080802/ClearSip/issues) · [Data audit](docs/research/catalog-availability-audit.md) · [Licensing](LICENSE_SCOPE.md)

> Educational information, not medical advice. ClearSip explains disclosed label
> facts; it does not detect undisclosed chemicals, certify a product’s safety, or
> assign a universal “healthy/unhealthy” score.

## Contents

- [Features](#features)
- [Catalog coverage](#catalog-coverage)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project structure](#project-structure)
- [Data and privacy](#data-and-privacy)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Name and size lookup:** choose a drink/flavor and an available package size.
- **Camera and media input:** capture a label, upload an image, or read one frame from a video using browser-side OCR.
- **Voice search:** speak a drink name in browsers that support speech recognition.
- **Typed barcode lookup:** resolve known UPC/EAN/GTIN values to catalog packages.
- **Ingredient body effects:** exact declared component names, their jobs in the drink, general bodily effects, dose limitations, and primary-source links.
- **Drinking context:** a separate tab for low-sugar goals, casual use, calorie/caffeine awareness, and relevant cautions—not a universal safety score.
- **Visible evidence:** manufacturer sources, dates, unknown amounts, and distinct variant-versus-package scope.

The [ingredient-effects guide](docs/INGREDIENT_EFFECTS.md) explains the 42-profile
educational reference and its classification rules. Proprietary flavor blends
are not guessed, and qualified clinical review remains pending.

Camera input currently reads visible text and suggests catalog matches for
confirmation; native barcode scanning is used when the browser supports it.
A full-catalog visual-model workflow is prepared, but **no visual classes have
been trained yet**. An exact flavor or package may still require manual selection.
See the [image collection and training guide](docs/VISUAL_RECOGNITION.md).
Online-image collection is a separate, review-gated workflow. The
[coverage audit](data/recognition/online-image-coverage.json) reports bounded
searches and pending candidates—not trained recognition or verified labels.
Camera evaluation is currently deferred. Research-only training preparation can
continue, but experimental models remain blocked from production until separate
camera evaluation and release review pass.

## Catalog coverage

Snapshot: **September 26, 2026**. Check the app or [coverage API](https://clear-sip-gules.vercel.app/api/catalog-coverage) for current counts.

| Coverage | Count |
| --- | ---: |
| US catalog entries | 85 |
| Entries with manufacturer ingredient panels | 79 |
| Entries awaiting complete ingredient evidence | 6 |
| Existing SQL package-label records | 5 |

Package records overlap with catalog entries; these counts are **not additive**.
A manufacturer variant panel does not verify every bottle size. Nutrition remains
per the source’s stated serving, not automatically the selected container.

Coverage includes soda, sports and energy drinks, coffee, water, sparkling water,
juice, oat beverages, and functional soda. Pending entries are identified before
selection rather than opening an empty ingredient explanation.
See the [complete audit and sources](docs/research/catalog-availability-audit.md).

## Tech stack

| Layer | Technology |
| --- | --- |
| Frontend | JavaScript, HTML/CSS, Vite |
| Label OCR | Tesseract.js, browser camera/media APIs |
| API | Python, FastAPI |
| Database | PostgreSQL in production; SQLite for local development |
| Hosting | Vercel |
| Checks | GitHub Actions, Python smoke checks, Node.js tests |

The SQL model separates manufacturer → family → flavor → market-specific package
→ dated label. Curated manufacturer snapshots supplement it without turning a
variant source into an exact-package certification.

## Getting started

Use **Node.js 22** and **Python 3.12+**. CI currently runs Python 3.14.
The commands below are for macOS/Linux.

### 1. Clone and install

```bash
git clone https://github.com/Shubham080802/ClearSip.git
cd ClearSip
npm ci
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Initialize local data and start the API

**Warning:** bootstrap recreates `data/clearsip.db`. Use it only with disposable
local development data. Back up any local work you need to keep first.

```bash
.venv/bin/python scripts/bootstrap_db.py
.venv/bin/uvicorn api.index:app --reload
```

### 3. Start the frontend in a second terminal

From the same repository directory:

```bash
npm run dev
```

Open [localhost:5173](http://localhost:5173). Vite forwards `/api` requests to
the local API. Explore the API at [localhost:8000/docs](http://localhost:8000/docs).
No API key is required for the bundled local catalog.

## Testing

```bash
npm run test:client
npm run build
.venv/bin/python tests/api_smoke.py
.venv/bin/python tests/catalog_coverage.py
CLEARSIP_TEST_PYTHON=.venv/bin/python node tests/catalog-coverage.test.mjs
.venv/bin/python tests/import_fdc_smoke.py
.venv/bin/python tests/recognition_pipeline.py
.venv/bin/python tests/online_images.py
.venv/bin/python scripts/recognition_audit.py --preparation
CLEARSIP_TEST_PYTHON=.venv/bin/python node tests/recognition.test.mjs
.venv/bin/python scripts/check_recognizer_release.py
```

The API smoke test rebuilds the disposable local database. Catalog checks cover
every catalog entry and parsed size choice, including missing-label cases.
GitHub Actions also checks repeatable database migrations.

## Deployment

The live application deploys from GitHub to Vercel with a managed PostgreSQL
database. `vercel.json` routes the static frontend and Python API.

Set the server-side `DATABASE_URL` in Vercel and apply the versioned migrations;
do not run the local bootstrap against production or rely on local SQLite
persistence inside a serverless function.

See the [development and deployment guide](docs/DEVELOPMENT.md) for configuration,
migrations, catalog refreshes, and the Chrome-first workflow.

## Project structure

```text
ClearSip/
├── api/                    # FastAPI, database access, assessments, source panels
├── src/                    # Browser UI, OCR, lookup, and package selection
├── data/                   # SQL schema and dated manufacturer snapshots
├── migrations/             # Immutable production schema migrations
├── scripts/                # Bootstrap, imports, audits, and maintenance
├── tests/                  # Client, API, catalog, and importer checks
├── docs/                   # Research, architecture, and operating guides
├── .github/workflows/      # Verification and manual catalog refresh
├── index.html              # Application entry
├── vercel.json             # Deployment routes and security headers
└── LICENSE                 # MIT license for original code and documentation
```

## Data and privacy

- Every source-backed result retains provenance; missing nutrient amounts stay unknown.
- Source availability does not imply permission to redistribute manufacturer content. Read [data rights and license scope](LICENSE_SCOPE.md).
- Images, video frames, and camera captures are processed in the browser and are not uploaded to ClearSip’s API or retained by the app.
- Voice recognition is browser-dependent and may use the browser vendor’s remote service; do not assume it is on-device.
- The browser contacts third-party font/OCR resource hosts. This is not a claim of zero network traffic.
- OCR, source data, and labels can be incomplete or outdated. Always compare with the current package.

Read the [classification policy](docs/research/beverage-classification-policy.md)
for how label facts, interpretation, and uncertainty are kept separate.

## Roadmap

- Expand coverage through attributable, rights-reviewed data sources.
- Add reviewer-controlled label updates and a correction/reporting workflow.
- Improve camera/barcode matching and mobile accessibility.
- Collect permission-cleared packaging photos for all 83 specific recognition
  targets, train in cumulative batches, and define the three broad family leads.
- Obtain qualified nutrition/regulatory review before a broader health-focused release.
- Extend to food products once the beverage workflow is stable.

The [detailed roadmap](docs/ROADMAP.md) distinguishes completed work from planned work.

## Contributing

Open an [issue](https://github.com/Shubham080802/ClearSip/issues) for a bug,
feature suggestion, or source correction. For code changes, use a focused branch,
include tests, and describe the expected behavior in your pull request.

For data changes, include the exact product/flavor, market, source URL, access
date, serving, and evidence scope. Do not invent missing values, copy proprietary
marketing assets, or imply source-rights clearance from a public URL. Do not
include credentials, private scans, or personal information in issues or commits.

## License

Original ClearSip code and documentation are licensed under the
[MIT License](LICENSE). Copyright © 2026 Shubham Kumar.

**Manufacturer-derived data, third-party assets, dependencies, and trademarks
are not relicensed under MIT.** See [license scope and data rights](LICENSE_SCOPE.md)
and [third-party notices](THIRD_PARTY_NOTICES.md).
