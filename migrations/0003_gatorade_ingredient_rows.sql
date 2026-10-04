-- Normalize only the eleven ingredients declared in the exact-GTIN manufacturer label
-- already captured by migration 0002. The statement remains the source of truth.
INSERT INTO ingredients (id, name) VALUES
  ('water', 'Water'), ('sugar', 'Sugar'), ('dextrose', 'Dextrose'),
  ('citric-acid', 'Citric acid'), ('natural-artificial-flavor', 'Natural and artificial flavor'),
  ('salt', 'Salt'), ('sodium-citrate', 'Sodium citrate'),
  ('monopotassium-phosphate', 'Monopotassium phosphate'),
  ('modified-food-starch', 'Modified food starch'),
  ('glycerol-ester-of-rosin', 'Glycerol ester of rosin'), ('blue-1', 'Blue 1')
ON CONFLICT DO NOTHING;

INSERT INTO label_ingredients
  (label_version_id, ingredient_id, position, role, assessment, evidence_status, source_url)
VALUES
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Water'), 1,
   'Base liquid', 'Declared first on this package label, with no separate amount stated.', 'label_context',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Sugar'), 2,
   'Added sugar source', 'One of two declared sugars. The bottle reports 35 g added sugar in total, not an amount for this ingredient alone.', 'context_matters',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Dextrose'), 3,
   'Added sugar source', 'One of two declared sugars. The bottle reports 35 g added sugar in total, not an amount for this ingredient alone.', 'context_matters',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Citric acid'), 4,
   'Acidulant', 'Declared on the label, with no concentration disclosed.', 'label_context',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Natural and artificial flavor'), 5,
   'Flavoring', 'A grouped label term. The individual flavor substances and their amounts are not disclosed.', 'not_fully_specified',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Salt'), 6,
   'Mineral salt', 'The bottle reports 270 mg sodium overall, but the label does not assign an amount to this ingredient.', 'label_context',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Sodium citrate'), 7,
   'Mineral salt', 'The bottle reports 270 mg sodium overall, but the label does not assign an amount to this ingredient.', 'label_context',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Monopotassium phosphate'), 8,
   'Mineral salt', 'Declared on this label, with no individual amount disclosed.', 'label_context',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Modified food starch'), 9,
   'Stabilizer', 'Declared on this label, with no individual amount disclosed.', 'label_context',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Glycerol ester of rosin'), 10,
   'Stabilizer', 'Declared on this label, with no individual amount disclosed.', 'label_context',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815'),
  ('gatorade-cool-blue-20oz-label-2026-09-12', (SELECT id FROM ingredients WHERE name = 'Blue 1'), 11,
   'Color additive', 'Declared on this label, with no individual amount disclosed.', 'label_context',
   'https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815')
ON CONFLICT DO NOTHING;
