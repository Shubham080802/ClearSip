# US packaged-beverage catalog: lawful sources and coverage plan

**Decision:** ClearSip can build a large, legally reusable US packaged-beverage *baseline* from USDA FoodData Central (FDC) Branded Foods, then improve match confidence and freshness with per-manufacturer label records and licensed product-data partnerships. It cannot honestly promise a complete list of every beverage ever produced or sold in the US: no public, comprehensive, continually current registry exists, products and labels change, and barcode/product registration is incomplete for some items.

**Scope:** packaged, non-alcoholic US retail beverages first. Treat each record as a particular **product + flavor/variant + package/GTIN + market + label version**, not merely a brand name. Alcoholic beverages should be a separately reviewed future scope because their regulation and labeling regime differs. This is an engineering/research recommendation, not legal advice; obtain counsel and written licences before redistributing any non-CC0 source at scale.

## Recommended source hierarchy

| Priority | Source | What it is good for | Use and limitation |
| --- | --- | --- |
| 1 | [USDA FoodData Central (FDC) Branded Foods](https://fdc.nal.usda.gov/data-documentation/) | Initial nationwide discovery; label-derived product name, brand owner/name, GTIN/UPC where submitted, ingredients, serving data, and declared nutrient data. | The appropriate legally reusable baseline. Branded Foods submissions are voluntary and data providers are responsible for the fields, so it is not a complete or error-free census. Use its FDC ID as an external identifier, never as proof that a package currently matches. |
| 2 | The product's in-hand US package / a manufacturer-supplied label feed | The scan-result authority: ordered ingredients, Nutrition Facts, allergen statement, package-specific net contents, and front-label claims. | Keep the user upload private by default. OCR is an extraction method, not verification; show the source status and ask for correction/review when it conflicts with a current version. |
| 3 | Official manufacturer product/label pages | Current products and variants from a brand; a human verification lead and label source. | Link to the page and capture narrow factual fields with provenance. Do **not** bulk scrape, republish page copy, page selections, logos, pack images, or marketing assets without written permission/licence. |
| 4 | [Verified by GS1](https://www2.gs1.org/services/verified-by-gs1) / a licensed GS1 US or GDSN data-pool service | Verify a scanned GTIN's issuer/identity and improve matching. | Public Verified by GS1 is a thin identity service, not a free national nutrition database. GS1 says the public service is limited to 30 queries per IP/day; enterprise batch/API access requires contacting a local GS1 organization. Use a paid/licensed agreement for production-scale lookup and retain only what that agreement permits. |
| 5 | Retailer listings and reputable user reports | Discovery leads or a fallback for a product whose label cannot yet be sourced. | Mark `needs_package_verification`; do not treat a retailer transcription as definitive or build a redistributed database from it without rights review. |

## What FDC permits and how to use it

FDC says its data are public domain, not copyrighted, and published under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/); it requests attribution to FoodData Central but does not require permission for use. Its [API guide](https://fdc.nal.usda.gov/api-guide/) documents product search and detail endpoints, requires a data.gov API key, and sets a default 1,000 requests/hour/IP limit. Keep the key server-side: FDC says publicly exposed keys can be deactivated.

Use API search/detail for user-driven matching and scheduled delta checks. For initial backfill, run a separate ETL worker against FDC's [download releases](https://fdc.nal.usda.gov/download-datasets/) rather than trying to ingest its large downloads inside a Vercel request/function. FDC documents monthly Branded Foods web/API updates and twice-yearly download releases; record `fdc_id`, source dataset/release, `fetched_at`, original source payload hash, and a normalized version row so reformulations can be audited.

FDC's [Branded Foods documentation](https://fdc.nal.usda.gov/GBFPD_Documentation/) cautions that manufacturer submissions are voluntary and that label values can be rounded. Consequently, a missing field must remain **unknown**, not zero, and an on-label 0 should retain the reported value plus `label_declared` status rather than become a lab-analysis claim.

Suggested normalized fields:

- identity: `gtin_upc`, `fdc_id`, brand owner, brand, product name, flavor/variety, package net contents, market/country, category;
- label facts: serving size/unit, servings/container, raw ingredient statement in label order, declared allergen/Contains statement, declared nutrition values and `%DV`, explicitly stated caffeine amount, exact front-label claims;
- provenance: source type/URL, publisher, observed/fetched time, image hash or source-payload hash, label revision/effective date when known, source confidence, reviewer;
- lifecycle: `active`, `discontinued`, or `unknown`; an immutable version history and last successful verification date.

Do not infer undisclosed quantities (for example milligrams of a sweetener), proprietary flavor composition, or a universal physiological outcome from this data.

## Major manufacturer sources

Official pages are excellent for manual review and a future opt-in/licensed import. They demonstrate that flavors and package sizes need separate rows:

- [Coca-Cola US product pages](https://www.coca-cola.com/us/en/brands/coca-cola/products/original) expose ingredients, Nutrition Facts, and multiple package sizes; [Powerade](https://www.powerade.com/products/powerade) and [Powerade Zero](https://www.powerade.com/products/powerade-zero) similarly expose variant-level US label facts.
- [PepsiCo Product Facts](https://www.pepsicoproductfacts.com/) offers search, product fact sheets, and nutrition/ingredient spreadsheets for its portfolio; a [GTIN-specific Pepsi example](https://www.pepsicoproductfacts.com/Home/Product?gtin=00012000000133) shows the package-level lookup model. Confirm its current terms and obtain permission before programmatic bulk download or redistribution.
- [Monster Energy US Zero Sugar](https://www.monsterenergy.com/en-us/energy-drinks/monster-energy/zero-sugar/) is useful for a current product/variant check, but its public page does not guarantee a complete machine-readable ingredient panel for every SKU. Seek an authorized feed or rely on the package/FDC for full label data.

Do not treat access to a webpage as a data licence. For example, Coca-Cola's [US Terms of Service](https://www.coca-cola.com/us/en/legal/terms-of-service) say its content is protected, prohibit creating/publishing a database featuring parts of the service without prior written consent, and prohibit automated scraping/indexing. The safe approach is to preserve source links and independently stored, attributable facts only where rights allow; do not copy marketing prose, product photography, logos, webpage HTML, or branded UI. Apply the same review to every source's current terms; facts may be different from copyrightable expression, but terms, database rights, trademark, and contract issues still require counsel's decision.

## FDA label guardrails

For most FDA-regulated packaged beverages, the [Nutrition Facts label](https://www.fda.gov/food/nutrition-facts-label/whats-nutrition-facts-label) provides serving and nutrient declarations. Ingredients generally appear in descending predominance by weight, but that is not a formula or an ingredient-dose disclosure; preserve the exact order and label text. FDA's [food-ingredient overview](https://www.fda.gov/food/food-additives-and-gras-ingredients-information-consumers/types-food-ingredients) explains this order requirement and exceptions.

FDA identifies nine major allergens and requires their food source to appear in the ingredient list or a `Contains` statement when applicable; a `Contains` statement is not guaranteed to appear in every product, so store both the raw ingredient statement and the raw adjacent statement. See [FDA food-allergy information](https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies).

Keep exact regulated/marketing claim text and its label evidence. In particular, do not turn `zero sugar` into a claim about insulin, healthfulness, benefit, or harm. FDA has distinct rules for [sugar-free claims](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/guidance-industry-and-fda-dear-manufacturer-letter-regarding-sugar-free-claims) and for use of the [`healthy` claim](https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/use-healthy-claim-food-labeling). Caffeine amount is often not declared; store it as unknown unless the producer or label explicitly provides it, consistent with FDA's [caffeine guidance](https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much).

## Staged coverage plan

1. **Foundation — all discoverable FDC US beverages.** In a local/managed PostgreSQL ETL job, ingest FDC Branded Foods records classified as beverages; deduplicate by GTIN and retain every source version. Expose them as `catalog_match` rather than “fully verified.” This provides broad lawful coverage, not a completeness promise.
2. **High-demand accuracy — top brands and scans.** Prioritize Coca-Cola, PepsiCo, Monster, Keurig Dr Pepper, Red Bull, water, sports drink, juice, coffee, tea, dairy/non-dairy drink, and emerging functional-drink brands. Review each flavor/package with an official page or package image; queue unknown barcodes/OCR mismatches for review.
3. **Product identity — barcode confidence.** At scan time, validate check digits locally; query FDC first, then a licensed GS1/GDSN service if needed. Store the mapping and source date, respect quotas/terms, and never assume a company prefix proves an exact package formulation.
4. **Freshness and corrections.** Run a monthly FDC delta ingest; re-check high-traffic or manufacturer-verified records quarterly and every user-reported mismatch. Publish the observed date and version; retire rather than overwrite prior label versions.
5. **Scale through permission.** Ask manufacturers and distributors for a documented data licence/API/feed covering fields, update cadence, image/trademark rights, caching, and redistribution. A GS1/GDSN subscription can address product-master-data scale, but does not replace label verification.

## Product-language policy

Classify ingredients by declared function and evidence/provenance, not as simply “good” or “bad.” Facts (ingredient presence, labelled sugar, sodium, or caffeine) should be clearly separated from general educational context. Avoid diagnosis, personalized safe-dose advice, and claims that a beverage ingredient will cause or prevent a condition. The user should always see the package/market/version and a concise notice that label information is educational and not medical advice.
