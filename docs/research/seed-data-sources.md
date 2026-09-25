# ClearSip seed data: sources and health-language guardrails

**Scope:** United States, initial beverages dataset. Researched 2026-09-24. Product recipes, package sizes, and labels can change, so retain a `market`, `package_size`, `source_url`, `label_observed_at`, and `verification_status` for every product record. The package itself is the final source of truth for a scan result.

## Verified product seed records

### Coca-Cola Zero Sugar — US, 12 fl oz can

The Coca-Cola Company’s current US product page lists: 0 calories; 0 g total sugars; 0 g added sugars; 40 mg sodium; 60 mg potassium; and **34 mg caffeine** per 12 fl oz can. It lists these ingredients, in order:

> Carbonated water, caramel color, phosphoric acid, aspartame, potassium benzoate (to protect taste), natural flavors, potassium citrate, acesulfame potassium, caffeine, stevia extract.

The same label states: “Phenylketonurics: Contains phenylalanine.” Preserve this as a high-priority factual notice for people with phenylketonuria (PKU); do not convert it into a general-population danger label. Source: [Coca-Cola US product and Nutrition Facts page](https://www.coca-cola.com/us/en/brands/coca-cola/products/zero).

Suggested seed facets: `zero_added_sugar: true`, `caffeine_mg_per_serving: 34`, `sweeteners: [aspartame, acesulfame_potassium, stevia_extract]`, `contains_phenylalanine_notice: true`, `preservative: potassium_benzoate`, `label_status: manufacturer_verified`.

### Monster Energy Zero Sugar — US, 16 fl oz

Monster’s US product page identifies a 16 fl oz serving as **160 mg caffeine**, **0 g sugar**, and **10 calories**; it also sells a 24 oz size. Source: [Monster Energy US product page](https://www.monsterenergy.com/en-us/energy-drinks/monster-energy/zero-sugar/).

Monster’s public US product page does **not** expose the full ingredient panel as text. A current retailer transcription of the package (useful only as a provisional scan seed; verify against the can before publishing) lists: carbonated water, citric acid, erythritol, natural flavors, taurine, sodium citrate, Panax ginseng flavor, L-carnitine L-tartrate, caffeine, sucralose, sorbic acid (preservative), benzoic acid (preservative), fruit juice (color), niacinamide (vitamin B3), acesulfame potassium, salt, D-glucuronolactone, guarana extract, inositol, pyridoxine hydrochloride (vitamin B6), riboflavin (vitamin B2), cyanocobalamin (vitamin B12). It reports 10 calories, 380 mg sodium, 6 g total carbohydrate, 0 g sugars, 0 g added sugars, and 2 g erythritol per 16 fl oz. Source: [Target’s package-label transcription](https://www.target.com/p/-/A-13370157).

Suggested seed facets: `zero_added_sugar: true`, `caffeine_mg_per_16_fl_oz: 160`, `sweeteners: [erythritol, sucralose, acesulfame_potassium]`, `caffeine_sources_named: [caffeine, guarana_extract]`, `label_status: needs_package_verification`. Do **not** assume the ingredient panel or amounts apply to 24 oz, another country, another flavour, or a later package revision.

## Ingredient interpretation: safe, useful wording

ClearSip should classify an ingredient by **function and evidence status**, not as “good” or “bad.” Recommended display fields: `role`, `what_the_label_supports`, `regulatory_status`, `quantity_known`, `personal_context_flag`, `evidence_level`, `source`, and `last_reviewed`.

| Ingredient/category | Supported consumer-facing statement | Important boundary |
| --- | --- | --- |
| Added caffeine | “This serving has 34 mg / 160 mg caffeine.” FDA cites 400 mg/day as an amount not generally associated with negative effects for *most adults*; sensitivity varies with body weight, medicines, medical conditions, and individual response. | Present it as a general reference, never a personal maximum. Prompt users who are pregnant, trying to conceive, breastfeeding, have a condition, take medication, or have symptoms to speak with a clinician. FDA says medical experts advise against energy drinks for children and teens. |
| Sucralose and acesulfame potassium (Ace-K) | FDA lists both as approved food-additive sweeteners under conditions of use. FDA says high-intensity sweeteners generally do not raise blood sugar levels. | Do **not** claim “does not spike insulin,” “harms the body,” or “safe for everyone.” A product label normally does not reveal the sweetener dose, so no product-level comparison with an ADI is valid without a manufacturer quantity. |
| Aspartame | FDA lists aspartame as an approved food-additive sweetener. Coca-Cola’s own label carries the phenylalanine/PKU notice. | Never suppress the PKU notice; do not portray it as a general disease warning. |
| Stevia extract | FDA distinguishes high-purity steviol glycosides (FDA has not questioned GRAS conclusions under notified conditions) from whole stevia leaf/crude extracts, which FDA does not consider GRAS for use as sweeteners. | The label’s phrase “stevia extract” alone may not identify the chemical form or dose; use the manufacturer label as written and avoid over-specific claims. |
| Erythritol / taurine / ginseng / L-carnitine / vitamins / flavours / preservatives | Identify the declared ingredient and, if supported by an authoritative source, its technical label function. | Presence in an energy drink is not proof of a health benefit or harm. Do not infer that a “vitamin” makes the beverage healthy, or that an unfamiliar chemical name is dangerous. |

FDA sources: [caffeine guidance](https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much), [high-intensity sweeteners](https://www.fda.gov/food/food-additives-petitions/high-intensity-sweeteners), and [FDA’s ingredient-specific sweetener explainer](https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food).

FDA describes an acceptable daily intake (ADI) as an amount considered safe to consume daily over a lifetime. Its listed ADIs include: aspartame 50 mg/kg body weight/day, Ace-K 15 mg/kg/day, and sucralose 5 mg/kg/day. These are **ingredient exposure limits**, not recommended targets or product serving limits. Because the product labels above do not provide sweetener milligrams, the app must show “amount not disclosed—ADI comparison unavailable,” rather than calculate a percentage. See [FDA’s sweetener explainer](https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food).

## Product and claim policy

1. Say **“0 g sugar per labeled serving”** rather than “sugar-free means no metabolic effect.” The claim reports the labeled nutrient, not an individualized physiological outcome.
2. Attribute product facts to a specific manufacturer label/page, package size, market, and date. Re-check sources on a scheduled cadence and whenever a user’s package OCR differs.
3. Keep “facts” separate from “context.” For example: show caffeine amount as a fact; show FDA’s 400 mg/day reference as context; do not use a red/green score to diagnose healthfulness.
4. Do not state or imply that a conventional beverage diagnoses, treats, cures, prevents, or reduces a user’s risk of a disease. FDA says a health claim links a substance to reduced risk of a disease/health-related condition and is subject to specific FDA pathways; unauthorized disease claims are not permitted on foods. Sources: [FDA label-claims overview](https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/label-claims-conventional-foods-and-dietary-supplements) and [FDA food-labeling compliance program](https://www.fda.gov/media/71690/download?attachment=).
5. Avoid calling a product “healthy,” “harmful,” “insulin-spiking,” “non-insulin-spiking,” or “beneficial” unless the exact statement is supported for that product and use case. FDA’s regulated “healthy” claim has product-specific criteria, including food-group content and limits for added sugar, saturated fat, and sodium; zero sugar alone does not establish it. Source: [FDA: use of “healthy” on food labeling](https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/use-term-healthy-food-labeling).
6. Display a short persistent disclaimer: “Educational label information, not medical advice. Allergies, conditions, medicines, pregnancy, age, and total daily intake can change what is appropriate for you.” Route urgent symptoms or poison-exposure concerns to local emergency/poison resources, rather than attempting triage.

## Data provenance and lawful collection

- Prefer manufacturer product pages, manufacturer-supplied label PDFs, and regulator records. Store source URL, publisher, access date, country, package size, and a content hash/label version.
- OCR user-supplied package images for personal lookup; make the user-facing result clearly state whether it is “OCR extracted,” “manufacturer verified,” or “needs review.” Never fabricate a missing quantity.
- Store factual label transcriptions and short summaries, not copied marketing copy or unlicensed product images. Keep the original user upload private unless the user expressly authorizes retention.
- Treat retailer listings as a lead or provisional transcription, not the authority when they conflict with an in-hand label or manufacturer source.

