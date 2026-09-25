CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  brand TEXT NOT NULL,
  region TEXT NOT NULL,
  serving TEXT NOT NULL,
  calories INTEGER,
  added_sugar_g REAL,
  caffeine_mg INTEGER,
  verification_status TEXT NOT NULL CHECK (verification_status IN ('manufacturer_verified', 'needs_package_verification')),
  last_reviewed TEXT NOT NULL,
  source_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ingredients (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS product_ingredients (
  product_id TEXT NOT NULL REFERENCES products(id),
  ingredient_id TEXT NOT NULL REFERENCES ingredients(id),
  position INTEGER NOT NULL,
  role TEXT NOT NULL,
  assessment TEXT NOT NULL,
  evidence_status TEXT NOT NULL CHECK (evidence_status IN ('label_context', 'context_matters', 'worth_watching', 'not_fully_specified')),
  source_url TEXT,
  PRIMARY KEY (product_id, ingredient_id)
);
