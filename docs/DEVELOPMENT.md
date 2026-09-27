# Development and deployment

For installation and basic commands, start with the [README](../README.md).
Run commands below from the repository root.

## Configuration

| Setting | Used by | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Python API and migration/import processes | Managed PostgreSQL URL in production; local API defaults to `data/clearsip.db` when unset |
| `VITE_API_BASE_URL` | Frontend build | Optional API base; defaults to `/api`. This value is public, so never put secrets in it |
| `FDC_API_KEY` | Import process / GitHub secret | Personal Data.gov key for focused FoodData Central imports |
| `CLEARSIP_DATABASE_URL` | GitHub repository secret | Production database URL used by the manual refresh workflow |
| `CLEARSIP_TEST_PYTHON` | Catalog JavaScript integration test | Python executable; use `.venv/bin/python` locally |

Keep credentials out of committed files, browser code, logs, and screenshots.
Supply backend settings through the process environment or the hosting provider's
secret configuration. The backend does not automatically load a plain `.env` file.
Check the diff before committing; this repository's ignore rules are not a
secret scanner.

## Production migrations

`migrations/` is the immutable schema history. The migration runner verifies
checksums of applied migrations and uses a PostgreSQL advisory lock to prevent
simultaneous runs from racing.

With the intended production `DATABASE_URL` already set securely:

```bash
.venv/bin/python scripts/migrate_db.py
```

Take an appropriate database backup and review each migration before applying it.
Add a new numbered migration for each schema change; never edit an applied one.
`scripts/bootstrap_db.py` deliberately rebuilds the local development database
and is not a production migration or production seed workflow.

## Vercel and Chrome-first workflow

GitHub is the source of truth. Use GitHub's browser editor (`github.dev`) for
simple edits, GitHub Actions for checks, and the Vercel dashboard for environment
variables and deployment status. Keep changes in small meaningful commits.

- Configure a managed PostgreSQL database such as Neon and set `DATABASE_URL`
  for the intended Vercel environment.
- Deploy the Vite frontend and FastAPI function using [vercel.json](../vercel.json).
  `/api/*` reaches Python; other application routes load the frontend.
- The Python build includes `data/reviewed-labels-*.json`; these are read-only
  release snapshots, not mutable serverless storage.
- Check `/api/health`, `/api/catalog-summary`, and `/api/catalog-coverage`
  after deployment, then test a known drink and package size in the browser.
- Do not assume preview deployments should share the production database;
  configure and review environment isolation.

Security headers restrict framing, resource origins, and browser permissions.
Camera access is requested only after the user chooses camera scanning.
Image/video OCR runs in the browser. Speech recognition may use the browser
vendor's service. Fonts and OCR resources require external network requests.

## Label assessments and source snapshots

The assessment policy covers disclosed sugar, saturated fat, sodium, caffeine,
and visible claims. It is not a diagnosis, personal intake limit, or legal
compliance certification. Read the [classification policy](research/beverage-classification-policy.md).

```bash
.venv/bin/python scripts/rebuild_assessments.py
.venv/bin/python scripts/audit_catalog.py
```

Source snapshots retain flavor, publisher, source URL, date, full ingredients,
serving, and limitations. Unknown values remain null. A variant-level panel
must not be silently presented as an exact UPC/package match. Restart the local
API or deploy a new release after updating cached source snapshots.

## Controlled FoodData Central refresh

Set `FDC_API_KEY` securely in the import process, then run a focused import:

```bash
.venv/bin/python scripts/import_fdc.py --query "Pepsi Zero Sugar" --page-size 20
```

The importer rejects non-beverage categories, retains FDC provenance, and uses
`catalog_label_match`; an FDC hit is not package verification. The `--demo`
option is only for small experiments.

For the manual **Refresh FoodData Central catalog** GitHub Action, configure
`CLEARSIP_DATABASE_URL` and `FDC_API_KEY` repository secrets first. In
**Actions → Refresh FoodData Central catalog → Run workflow**, provide one
focused beverage query. The workflow migrates, imports at most 50 search hits,
and recalculates assessments. It does not upload scans.

A nationwide backfill needs a dedicated worker and source-release process,
not a Vercel request. Read the [acquisition plan](research/us-beverage-catalog-sources.md)
and [license scope](../LICENSE_SCOPE.md) before redistributing source-derived data.

## Release checks

Run the README's client/API/catalog/importer checks. The API smoke check
rebuilds disposable local data. CI additionally tests repeatable migrations.
Confirm the deployed ingredient count and the selected-size serving disclaimer.
Refresh [third-party notices](../THIRD_PARTY_NOTICES.md) when dependencies change.

Before broader release, arrange source-rights and clinical/regulatory review,
choose a reviewer/authentication model before adding production write endpoints,
and choose a support channel before collecting mismatch reports or personal data.
