# Ingredient effects and drinking contexts

ClearSip explains the actual component names in the available ingredient
statement instead of replacing them with a few generic ingredient groups. The
original statement and its manufacturer source remain visible above the tabs.

## Ingredients & body effects

Each declared component has separate explanations for its function **in the
drink** and its general effects **in the body**. Expand a card for amount
limitations, intake cautions, and primary-source links. Compound declarations
retain their parenthesized components; multiple applicable profiles can appear
on one card. Unmatched components remain visible as **Review pending**.

The versioned reference is `data/ingredient-effects.json`, also exposed read-only
at `/api/ingredient-effect-profiles`. Version `2026.09.28-body-context-v1` contains
42 profiles. It is a source-backed educational draft, not clinically reviewed
personal advice. Research and citations are in
[the ingredient evidence note](research/ingredient-body-effects.md).

Ingredient matching is explanation coverage, not recognition accuracy, a safety
assessment, or proof that a specific drink causes a physiological effect.
Manufacturer formula/nutrition records are not overwritten by this reference.

### Disclosure limits

- “Natural flavors” and “artificial flavors” are grouped declarations. Public
  research can explain their function and labeling rules, but cannot identify an
  undisclosed proprietary blend. “Natural” does not guarantee superior safety.
- Individual ingredient quantities usually are not stated. A drink's total sugar,
  caffeine or sodium is explicitly identified as a **drink total**, not an
  individual ingredient dose. No sweetener ADI percentage or safe-can allowance
  is calculated from an unknown dose.
- Approved uses, physiological functions and effects of high supplemental doses
  are different kinds of evidence. A vitamin's normal role is not proof of a
  benefit from consuming more of this drink.
- Missing nutrient amounts stay unknown, not zero. Selecting a larger package
  does not silently scale a variant source's serving facts.

## Drinking context

The second tab describes overlapping contexts, not a single healthy/unhealthy
score or “safe on any diet” badge:

- **Low-sugar goals:** disclosed total sugar; 0 g is not an insulin-response,
  diabetes-management, or weight-loss guarantee.
- **Casual / occasional use:** added sugar compared with the FDA labeling Daily
  Value of 50 g. At most 2.5 g is low (5% DV); at least 10 g is high (20% DV).
  This label comparison is not a personal daily intake target.
- **Calorie budget:** actual disclosed calories, without keto/fasting clearance.
- **Caffeine awareness:** known dose or unknown amount, with individual-sensitivity
  cautions. Coffee, tea and decaf are not assumed caffeine-free.
- **Hydration:** a plain-water pattern requires only water/carbonation declarations.
  A water base does not qualify a flavored or sweetened drink for that pattern.
- **Specific cautions:** disclosed sodium, aspartame/PKU, milk/soy allergens and
  acidic-drink dental exposure where applicable. This is not a complete allergen,
  interaction, cross-contact, or medical-condition audit.

Each context exposes its rule and sources. The source's serving remains the
comparison basis; several cautions may coexist with a low-sugar declaration.

## Maintenance and verification

Research high-trust primary sources, write original educational summaries, retain
source URLs/access dates, and review changes before publishing. Do not bulk scrape
or infer a manufacturer's undisclosed formula. Public availability does not itself
grant redistribution rights; see [license scope](../LICENSE_SCOPE.md).

Run `npm run test:client`, `npm run build`,
`.venv/bin/python tests/catalog_coverage.py` and
`CLEARSIP_TEST_PYTHON=.venv/bin/python node tests/catalog-coverage.test.mjs`.
Tests cover ingredient-name preservation, false-match boundaries, unknown amounts,
source-serving scope, HTML escaping, and keyboard-accessible tabs across the catalog.
Qualified clinical/regulatory review remains required before a broad health launch.
