-- First package-specific web-label snapshot. Not an in-hand bottle inspection.
-- First-party audit: docs/research/package-identity-first-batch.md
INSERT INTO manufacturers (id, name, website_url)
VALUES ('pepsico', 'PepsiCo', 'https://www.pepsico.com/')
ON CONFLICT DO NOTHING;

INSERT INTO beverage_families (id, manufacturer_id, name)
VALUES ('gatorade', (SELECT id FROM manufacturers WHERE name = 'PepsiCo'), 'Gatorade')
ON CONFLICT DO NOTHING;

INSERT INTO beverage_variants (id, family_id, display_name, flavor_name, category)
VALUES ('gatorade-cool-blue', 'gatorade', 'Gatorade Cool Blue', 'Cool Blue', 'sports drink')
ON CONFLICT DO NOTHING;

INSERT INTO product_packages (id, variant_id, gtin, fdc_id, market, package_description, lifecycle_status)
VALUES ('gatorade-cool-blue-20oz-us', 'gatorade-cool-blue', '00052000324815', NULL,
        'United States', '20 fl oz bottle (591 mL)', 'unknown')
ON CONFLICT DO NOTHING;

INSERT INTO source_records (id, publisher, url, market, accessed_on, source_type, content_hash)
VALUES ('pepsico-gatorade-cool-blue-20oz-2026-09-30', 'PepsiCo Product Facts',
        'https://www.pepsicoproductfacts.com/services/labels/index?backgroundcolor=%23ffffff&color=%23000000&gtin=00052000324815&url=https://www.pepsicoproductfacts.com&wp=PPF',
        'United States', '2026-09-30', 'manufacturer_label', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO label_versions
  (id, package_id, source_id, serving, servings_per_container, calories, saturated_fat_g,
   total_sugar_g, added_sugar_g, sodium_mg, caffeine_mg, ingredient_statement,
   contains_statement, front_label_claims, verification_status, label_observed_on, is_current)
VALUES
  ('gatorade-cool-blue-20oz-label-2026-09-12', 'gatorade-cool-blue-20oz-us',
   'pepsico-gatorade-cool-blue-20oz-2026-09-30', '1 bottle (591 mL)', 1, 140, NULL,
   35, 35, 270, 0,
   'WATER, SUGAR, DEXTROSE, CITRIC ACID, NATURAL AND ARTIFICIAL FLAVOR, SALT, SODIUM CITRATE, MONOPOTASSIUM PHOSPHATE, MODIFIED FOOD STARCH, GLYCEROL ESTER OF ROSIN, BLUE 1.',
   NULL, NULL, 'package_verified', '2026-09-12', 1)
ON CONFLICT DO NOTHING;
