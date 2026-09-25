CREATE TABLE IF NOT EXISTS manufacturers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  website_url TEXT
);

CREATE TABLE IF NOT EXISTS beverage_families (
  id TEXT PRIMARY KEY,
  manufacturer_id TEXT NOT NULL REFERENCES manufacturers(id),
  name TEXT NOT NULL,
  UNIQUE (manufacturer_id, name)
);

CREATE TABLE IF NOT EXISTS beverage_variants (
  id TEXT PRIMARY KEY,
  family_id TEXT NOT NULL REFERENCES beverage_families(id),
  display_name TEXT NOT NULL,
  flavor_name TEXT,
  category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS product_packages (
  id TEXT PRIMARY KEY,
  variant_id TEXT NOT NULL REFERENCES beverage_variants(id),
  gtin TEXT UNIQUE,
  fdc_id TEXT UNIQUE,
  market TEXT NOT NULL,
  package_description TEXT NOT NULL,
  lifecycle_status TEXT NOT NULL DEFAULT 'unknown' CHECK (lifecycle_status IN ('active', 'discontinued', 'unknown'))
);

CREATE TABLE IF NOT EXISTS source_records (
  id TEXT PRIMARY KEY,
  publisher TEXT NOT NULL,
  url TEXT NOT NULL,
  market TEXT NOT NULL,
  accessed_on TEXT NOT NULL,
  source_type TEXT NOT NULL CHECK (source_type IN ('manufacturer_page', 'manufacturer_label', 'package_observation', 'regulatory', 'retailer_lead')),
  content_hash TEXT,
  UNIQUE (url, market, accessed_on)
);

CREATE TABLE IF NOT EXISTS label_versions (
  id TEXT PRIMARY KEY,
  package_id TEXT NOT NULL REFERENCES product_packages(id),
  source_id TEXT NOT NULL REFERENCES source_records(id),
  serving TEXT NOT NULL,
  calories INTEGER,
  added_sugar_g REAL,
  caffeine_mg INTEGER,
  ingredient_statement TEXT,
  contains_statement TEXT,
  front_label_claims TEXT,
  verification_status TEXT NOT NULL CHECK (verification_status IN ('manufacturer_verified', 'package_verified', 'needs_package_verification')),
  label_observed_on TEXT NOT NULL,
  is_current INTEGER NOT NULL DEFAULT 1 CHECK (is_current IN (0, 1))
);

CREATE UNIQUE INDEX IF NOT EXISTS one_current_label_per_package ON label_versions(package_id) WHERE is_current = 1;

CREATE TABLE IF NOT EXISTS ingredients (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS label_ingredients (
  label_version_id TEXT NOT NULL REFERENCES label_versions(id),
  ingredient_id TEXT NOT NULL REFERENCES ingredients(id),
  position INTEGER NOT NULL,
  role TEXT NOT NULL,
  assessment TEXT NOT NULL,
  evidence_status TEXT NOT NULL CHECK (evidence_status IN ('label_context', 'context_matters', 'worth_watching', 'not_fully_specified')),
  source_url TEXT,
  PRIMARY KEY (label_version_id, ingredient_id)
);
