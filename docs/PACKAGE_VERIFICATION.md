# Package identity and label verification

An observed package size is not an exact label match. ClearSip now separates
three questions: Is the drink/flavor known? Is a GTIN linked to the particular
product package? Has a dated source label for that package been reviewed?

The `package_evidence` field on `/api/products/{id}` and
`/api/products/by-gtin/{gtin}` answers the last two questions separately.
`/api/catalog-summary` reports package records, linked GTINs and verified
package labels as separate counts. Product search carries `label_verified` so
the size picker does not call a variant panel a reviewed package label.

## First reviewed package

`migrations/0002_gatorade_cool_blue_20oz.sql` adds **Gatorade Cool Blue,
20 fl oz / 591 mL bottle, GTIN 00052000324815**. Its one-container serving,
ingredient statement and nutrition facts are tied to PepsiCo's GTIN-specific
online label. The label states an update date of 2026-09-12; ClearSip accessed
it on 2026-09-30. [The primary-source audit](research/package-identity-first-batch.md)
records the evidence and source links. The manufacturer cautions that packaging
and formulations can change. This record is **not** an inspection of a physical
bottle and does not validate the 12, 24 or 28 fl oz versions.

After the migration, coverage is six SQL package records with label data,
one reviewed exact-package web label and one linked GTIN. The other five SQL
labels remain package-unconfirmed. The 79 curated manufacturer variant panels
remain useful but must not be promoted to exact-package status.

## Review gate for future packages

Before setting `verification_status = 'package_verified'`, review a first-party
package label or authorized package observation that identifies the same US
variant, net contents/container, and (when available) GTIN. Record the source
publisher, URL, source type, access date, label version/date, exact ingredient
statement, serving and servings per container. Resolve conflicting label facts
before publishing; keep missing values null. A GTIN alone verifies identity,
**not** the ingredients. FoodData Central imports remain
`catalog_label_match` until independently reviewed.

Only `manufacturer_label`, `package_observation` or independently reviewed
`usda_fdc_branded` sources with `package_verified` status display the reviewed
badge. This is an evidence gate, not a guarantee that every bottle now on a
shelf matches the snapshot. In-app scans should still ask users to compare their
current package. Do not reuse product photos for model training without a
separate rights and identity review.

Production applies immutable migrations through `scripts/migrate_db.py` using
the intended `DATABASE_URL`. Local bootstrap reuses the same package batch in a
disposable SQLite database. Back up production before migrations; never run
`scripts/bootstrap_db.py` against it. See [deployment guidance](DEVELOPMENT.md).
