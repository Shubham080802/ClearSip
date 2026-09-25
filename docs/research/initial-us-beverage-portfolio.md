# Initial US beverage portfolio — source-backed catalog plan

**Researched:** 2026-09-24  
**Scope:** packaged, non-alcoholic beverages sold in the United States. This is a
prioritized *discovery and verification queue*, not a claim that it is a complete
list of every drink ever produced or available in the United States. New products,
regional distribution, formula revisions, and package changes occur continually.

The unit that ClearSip must eventually publish is a **specific package label**:
brand + product/variant + flavor + net contents + GTIN/UPC + US market + label
revision. A brand, flavor, or "zero sugar" product name must never be treated as
one universal formula.

## Non-negotiable data boundary

The request to include ingredients that are "not listed but available to the
public" has an important limit: an app may record a manufacturer-disclosed
ingredient or a publicly supported regulatory/technical fact, but it must not
invent a confidential recipe or hidden chemical. US food labels normally list
ingredients in descending order of predominance by weight, but they do not
generally disclose the amount of each ingredient or the composition of terms such
as `natural flavors`. See FDA's [food-ingredient overview](https://www.fda.gov/food/food-additives-and-gras-ingredients-information-consumers/types-food-ingredients).

Therefore, each imported field needs one of these statuses:

| Status | Meaning |
| --- | --- |
| `label_declared` | Exact wording/amount appears on a current US package or an official product-facts page. |
| `manufacturer_disclosed` | A producer has publicly supplied the fact, but it is not a complete package panel. |
| `not_disclosed` | The label/source does not disclose an amount or composition. Do not estimate it. |
| `needs_package_verification` | A discovery source found the candidate, but the exact US package label has not yet been reviewed. |

The app should classify a declared item by **function** (for example, sweetener,
source of added sugars, acidulant, preservative, color, caffeine, electrolyte,
vitamin, botanical, or flavor), followed by evidence-based general context. It
must not label an ingredient simply "good," "bad," or "harmful," claim that a
zero-sugar drink changes insulin, or promise that a drink causes/prevents a
disease. The product-language rules and FDA-backed sweetener/caffeine context are
in [seed-data-sources.md](seed-data-sources.md).

## Recommended source model

Use the [USDA FoodData Central Branded Foods dataset](https://fdc.nal.usda.gov/data-documentation/)
as the broad, lawful discovery baseline, then match a record to a currently
observed package or the manufacturer's product-facts service. FDC records are
valuable but voluntary manufacturer submissions, so they are not a current,
complete national census. The acquisition, licensing, and update policy is in
[us-beverage-catalog-sources.md](us-beverage-catalog-sources.md).

Do not scrape manufacturer pages or bulk-copy their imagery/marketing copy. The
following links are verification sources and human-review queues. Record a URL,
source/publisher, access date, GTIN where supplied, and label version/hash. When
the source itself warns that formula/packaging can change, retain that warning.

## Priority 1: nationally prominent families with official, package-level paths

The list below is intentionally organized first by family, then by variant/flavor
and available *source-supported* package sizes. Entries marked **queue** are valid
catalog candidates but not yet verified as every active flavor or every regional
SKU. A package size is only carried into the production dataset after it is tied
to that specific item and GTIN/label.

| Manufacturer/family | Candidate variants or flavor lines to seed/discover | Official evidence and currently reported packages | Import confidence |
| --- | --- | --- | --- |
| Coca-Cola — Coca-Cola | Original; Zero Sugar; Diet Coke; Caffeine Free; Cherry; Vanilla; seasonal/limited variants (**queue each separately**) | [Coca-Cola Original US page](https://www.coca-cola.com/us/en/brands/coca-cola/products/original) reports Original in 7.5, 8, 12, 16, 16.9 and 20 fl oz plus 1.25 L and 2 L. [Coca-Cola Zero Sugar](https://www.coca-cola.com/us/en/brands/coca-cola/products/zero) reports the same size set; it is the exact 12 fl oz label source used by the existing seed. The official [flavor page](https://www.coca-cola.com/us/en/brands/coca-cola/products/coca-cola-flavors) reports Cherry (7.5, 12, 16.9 fl oz, 2 L), Cherry Zero (7.5, 12, 16.9, 20 fl oz, 2 L), Vanilla (12, 16.9, 20 fl oz), and Cherry Float/Cherry Float Zero (12, 20 fl oz). Its Vanilla Zero detail and comparison table disagree on its available sizes, so that variant is `needs_package_verification`. | Manufacturer label pages; per-variant/package verification still required. |
| Coca-Cola — Sprite | Sprite original; Sprite Zero Sugar; Sprite Chill; Sprite + Tea Peach; other limited variants (**queue**) | [Sprite US products](https://www.coca-cola.com/us/en/brands/sprite/products) reports original Sprite in 7.5, 8, 12, 13.2, 16.9 and 20 fl oz plus 1 L, 1.25 L, 2 L and 3 L. The same page reports Sprite + Tea Peach 12 fl oz and 20 fl oz (Kroger exclusive). | Manufacturer page shows that flavor and retailer exclusivity alter the SKU set. |
| Coca-Cola — Powerade | Powerade; Powerade Zero Sugar; Powerade Mountain Berry Blast, Fruit Punch, Grape, Orange, Lemon Lime and other current labeled flavors (**queue**) | The official [Powerade product page](https://powerade-us-en.beta.cep.coca-cola.com/products/powerade) lists Grape/Lemon Lime in 20/28 oz, Orange in 12/20/28 oz, and Strawberry Lemonade in 28 oz. [Powerade Zero](https://powerade-us-en.alpha.cep.coca-cola.com/products/powerade-zero) lists Mixed Berry in 12/20/28 oz and Orange in 28 oz. These pages supply nutrition/ingredient detail but flavors vary. | Verify each size/GTIN from package page/FDC; the manufacturer subdomains are an official source but live pages can change. |
| Coca-Cola — water | Dasani Purified Water | [Dasani US](https://www.coca-cola.com/us/en/brands/dasani) lists purified water, magnesium sulfate and potassium chloride, with 10, 12, 16.9 and 20 fl oz, 1 L, and 1.5 L packages. | Manufacturer verified for this item; check current bottle label on import. |
| PepsiCo — Pepsi | Pepsi; Diet Pepsi; Pepsi Zero Sugar; Pepsi Wild Cherry; Pepsi Zero Sugar Wild Cherry; Pepsi Zero Sugar Mango; Pepsi Wild Cherry & Cream; Pepsi Prebiotic Cola (**each flavor/package is a queue**) | [Pepsi Zero Sugar 20 fl oz](https://www.pepsicoproductfacts.com/Home/product?gtin=00012000018800) reports 7.5, 12, 13, 16, 16.9, 20, 24, 33.8, 42.3 and 67 fl oz, 16 fl oz can, and fountain. It reports 63 mg caffeine for that 20 fl oz package. The [67 fl oz page](https://www.pepsicoproductfacts.com/Home/Product?gtin=00012000018817) reports 38 mg caffeine per 12 fl oz serving. The brand's [Pepsi](https://www.pepsi.com/products/pepsi), [Pepsi Zero Sugar](https://www.pepsi.com/products/pepsi-zero-sugar), and [Diet Pepsi](https://www.pepsi.com/products/diet-pepsi) pages are another current US cross-check: each lists 7.5, 12, 16, 16.9, 20 and 24 fl oz plus 1 L, 1.25 L and 2 L. | Official GTIN-specific product facts; PepsiCo explicitly says formulation/packaging can change and packaging is current authority. |
| PepsiCo — Mountain Dew | Mountain Dew; Diet; Zero Sugar; Code Red; Voltage; Baja Blast; Major Melon; seasonal/collaboration flavors (**queue each**) | PepsiCo's [Mountain Dew Product Facts search](https://www.pepsicoproductfacts.com/Home/Search?productName=mountain+dew) enumerates current variants/sizes, including retailer and fountain products. The [original 12 fl oz GTIN page](https://www.pepsicoproductfacts.com/Home/product?gtin=00012000000850) reports original in 7.5, 12, 13, 16, 16.9, 20, 24, 33.8, 42.3 and 67 fl oz plus fountain/freeze. | Product Facts discovery only until each GTIN result is imported. Retain channel status: for example, Baja Blast is Taco Bell-only and Purple Thunder is Circle K-exclusive, so neither supports a national-availability claim. |
| PepsiCo — Gatorade | Thirst Quencher: Cool Blue, Fruit Punch, Lemon-Lime, Orange, Glacier Freeze/Cherry, Fierce, Frost; G Zero; G2; Gatorlyte; Gatorade Fit; Gatorade Water (**separate lines**) | [Gatorade Cool Blue 20 fl oz](https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815) reports 12, 20, 24 and 28 fl oz packages. [Gatorade Strawberry Lemonade](https://www.pepsicoproductfacts.com/Home/product?gtin=00052000104257) is an official 20 fl oz example. [Gatorade Water](https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000054903) reports 20, 23.7 and 33.8 fl oz. | Official GTIN facts; electrolyte/sugar and flavor formula must be item-specific. |
| PepsiCo — water | Aquafina | [Aquafina 16.9 fl oz](https://www.pepsicoproductfacts.com/Home/Product?gtin=00012000001086) links to the official fact sheet and identifies 12 fl oz can/bottle, 16, 16.9, 20, 33.8, 42.3 and 50.7 fl oz package candidates. | Import GTIN-specific facts, not a generic water record. |
| Monster | Monster Original; Zero Sugar; Lo-Carb; Ultra Zero; Ultra Red/Blue/Violet/Sunrise/Paradise/Fiesta Mango/Watermelon/Rosá/Peachy Keen/Strawberry Dreams; Juice Monster; Java Monster; Rehab (**each product page is a queue**) | [Monster's US catalog](https://www.monsterenergy.com/en-us/energy-drinks/) identifies the active product lines. [Monster Zero Sugar](https://www.monsterenergy.com/en-us/energy-drinks/monster-energy/zero-sugar/) reports 16 and 24 oz, 160 mg caffeine/16 oz, 0 g sugar and 10 calories. [Ultra Zero](https://www.monsterenergy.com/en-us/energy-drinks/zero-sugar/zero-ultra/) reports 12, 16, 19.2 and 24 oz, 150 mg caffeine and 0 g sugar. | Manufacturer summary. Full ordered ingredient panel/package facts need label or FDC verification. |
| Red Bull | Original; Sugarfree; Zero; Editions, including each color/flavor (**queue each**) | [Red Bull Original US](https://www.redbull.com/energydrink/red-bull-energy-drink) reports 8.4, 12, 16 and 20 fl oz. [Red Bull's US caffeine Q&A](https://www.redbull.com/us-en/energydrink/questions/how-much-caffeine-is-in-a-can-of-red-bull-energy-drink) reports respectively 80, 114, 151 and 198 mg. The [ingredients page](https://www.redbull.com/us-en/energydrink/products/red-bull-energy-drink-ingredients-list) reports, for original 8.4 fl oz, 80 mg caffeine and 26 g sugars in its nutrition declaration. | Original only is source-supported here; do not transfer it to Sugarfree/Zero/editions. |
| Keurig Dr Pepper — Dr Pepper | Dr Pepper; Diet Dr Pepper; Dr Pepper Zero Sugar; Cherry; Cherry Zero Sugar; Cream Soda; Strawberries & Cream; Blackberry; Creamy Coconut where active (**queue each**) | [KDP's brand directory](https://www.keurigdrpepper.com/brands/) links Dr Pepper to its Product Facts catalog. KDP's [2025 US innovation announcement](https://www.keurigdrpepper.com/keurig-dr-pepper-unveils-bold-new-flavors-across-iconic-u-s-cold-beverages-portfolio-27/) supports Dr Pepper Blackberry as an active 2025 permanent variety; it is not a current package-label source. | Use KDP Product Facts / a package label for every flavor and size. |
| Keurig Dr Pepper — adjacent high-demand drinks | 7UP / 7UP Zero Sugar; A&W / A&W Zero Sugar; Canada Dry; Snapple / Snapple Zero Sugar; Bai; Core Hydration; Squirt; Sunkist; Hawaiian Punch; Clamato; Mott's (**queue by product/flavor/package**) | KDP's [brand directory](https://www.keurigdrpepper.com/brands/) is a first-party discovery list and links many brands to Product Facts. It says the portfolio includes carbonated drinks, still/sparkling waters, tea, juice and mixers. | Discovery source only; variations can be regional. |
| Starbucks ready-to-drink | Frappuccino coffee drink flavor line; Doubleshot/Espresso; cold brew; iced coffee; Refreshers (**queue exact licensed US bottles/cans**) | KDP's official [brand directory](https://www.keurigdrpepper.com/brands/) lists Starbucks among ready-to-brew brands, not a reliable complete US RTD label catalog. The source owner/licensing and present US retail label must be established per RTD SKU. | Do not import as verified until an official RTD facts source, FDC record, or package is attached. |
| LaCroix | Core fruit flavors plus Cúrate, NiCola, Hi-Biscus or seasonal lines **only when a current package/official page is observed** | [LaCroix's official site](https://www.lacroixwater.com/) exposes the brand's Flavors and Nutrition & FAQ navigation, but this research did not find an accessible first-party current package-size index suitable for bulk import. | Discovery only; do not use historical media clips/retailer pages to assert availability. |

## What belongs in the first actual dataset release

1. Keep the two existing fully/partially sourced seeds, then add only package-level
   records reachable via the official PepsiCo Product Facts catalogue and
   manufacturer US label pages with a captured GTIN/FDC ID.
2. Prioritize the exact products listed above that have explicit package facts:
   Coca-Cola Original, Coca-Cola Zero Sugar, Sprite Original, Dasani, Pepsi Zero
   Sugar, Gatorade Cool Blue, Gatorade Strawberry Lemonade, Gatorade Water,
   Aquafina, Monster Zero Sugar, Monster Ultra Zero, and Red Bull Original.
   This is a defensible *initial verified set*, not a statement that other brands
   are unavailable.
3. In parallel, load eligible FDC Branded Foods beverage records as
   `catalog_match`/`needs_package_verification`, not `manufacturer_verified`.
   Deduplicate by GTIN and preserve the FDC ID, source release, original values,
   and observed date.
4. Expand one manufacturer family at a time using official or in-hand US package
   evidence; preserve discontinued and superseded label versions instead of
   overwriting them.

## Ingredient and health display rules for this portfolio

- **Sugar source:** show the exact declared label term (for example, sugar or
  high-fructose corn syrup) and labeled total/added sugar per serving. Do not
  convert a flavor name or calorie count into a sugar claim.
- **Sweeteners:** show the exact sweetener listed. If milligrams are absent,
  mark them `not_disclosed`; an acceptable-daily-intake comparison cannot be
  calculated. FDA's [high-intensity sweetener overview](https://www.fda.gov/food/food-additives-petitions/high-intensity-sweeteners)
  and [ingredient explainer](https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food)
  support general regulatory context, not product-specific medical outcomes.
- **Caffeine:** report the labelled/manufacturer-disclosed amount and serving
  basis, not a personal safe limit. FDA says 400 mg/day is an amount not generally
  associated with negative effects for most adults, while sensitivity and health
  context differ; it advises against energy drinks for children and teens. See
  [FDA caffeine guidance](https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much).
- **Other declared items:** classify acids, preservatives, colors, electrolytes,
  vitamins, amino acids, botanicals, and flavors by function. State "amount not
  disclosed" when applicable. Ingredient presence alone does not establish a
  product benefit, harm, or disease risk.
- **Persistent notice:** "Educational label information, not medical advice.
  Allergies, age, pregnancy, conditions, medicines, and total intake can change
  what is appropriate for an individual. Check your package for the current US
  label."

## Limitations and next verification pass

- "Popular" is not an objective, stable national product list. This report uses
  prominent families requested for the project and source availability; it makes
  no sales-rank claim.
- Availability and package ranges vary by flavor, channel, state, promotion, and
  time. A source-supported size range is not proof that every variant comes in
  every size.
- No public source reveals proprietary flavor composition or validates every
  formula currently on shelf. An OCR scan can surface a mismatch; it must create
  a new review/version candidate rather than silently modify an existing record.
- Before a mass import, confirm each source's terms and obtain the required data
  rights. Use a licensed GS1/GDSN source for production-scale GTIN identity
  matching, as described in [us-beverage-catalog-sources.md](us-beverage-catalog-sources.md).
