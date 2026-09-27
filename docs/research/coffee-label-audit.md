# Coffee label audit

Accessed September 26, 2026. Scope: all **21 coffee discovery rows** currently present in `scripts/bootstrap_db.py` (7 STōK, 7 La Colombe, 3 Dunkin', 4 Starbucks). The task's initial count of 23 does not match the file. This audit supplies 20 exact-variant ingredient records in `data/reviewed-labels-coffee.json`; one malformed source remains excluded.

## Evidence rules

These are dated manufacturer-page label snapshots at **variant scope**, not exact UPC/package verification. Ingredient order and subingredient groupings are retained. Unknown or ambiguously labeled nutrition fields remain `null`, never inferred as zero. `observed_sizes` records page evidence only and does not establish a package version. Front-label claims remain null because this pass transcribed the product pages, not matched front-panel artwork. Concentrate serving strings preserve the as-sold amount and the amount prepared with water; caffeine values from Starbucks are explicitly approximate.

Direct Starbucks product-page opens returned HTTP 403. Their complete first-party indexed page content was available in web search and supports the imported statements; the JSON notes disclose this access route and index freshness (two weeks for Signature Black, Caramel Dolce, Madagascar Vanilla; three days for Brown Sugar Cinnamon). This does not establish that today's live page or a particular package is unchanged.

## Row-by-row outcome

| Discovery ID | Status | Source and limitations |
| --- | --- | --- |
| `stok-unsweet-black-cold-brew` | Reviewed | [STōK UN-SWEET Black Cold Brew Coffee](https://www.stokbrew.com/cold-brew/cold-brew-coffee/unsweetened-cold-brew-coffee-48oz/). Complete ingredients and relevant Nutrition Facts; exact-variant caffeine not captured. |
| `stok-not-too-sweet-black-cold-brew` | Reviewed | [STōK NOT TOO SWEET Black Cold Brew Coffee](https://www.stokbrew.com/cold-brew/cold-brew-coffee/not-too-sweet-cold-brew-coffee-48oz/). Complete ingredients and relevant Nutrition Facts; exact-variant caffeine not captured. |
| `stok-espresso-blend-black-cold-brew` | Reviewed | [STōK Espresso Blend Black Cold Brew Coffee](https://www.stokbrew.com/cold-brew/cold-brew-coffee/unsweetened-black-espresso-cold-brew-coffee-48oz/). Complete ingredients and relevant Nutrition Facts; exact-variant caffeine not captured. |
| `stok-bright-mellow-cold-brew` | Reviewed; total sugars ambiguous | [STōK UN-SWEET Bright & Mellow Black Cold Brew Coffee](https://www.stokbrew.com/cold-brew/cold-brew-coffee/bright-mellow-cold-brew-coffee-48oz/). Complete ingredients; source says “Trans Sugars 0g”, so total sugar is null. |
| `stok-decaf-unsweet-cold-brew` | Reviewed | [STōK DECAF UN-SWEET Black Cold Brew Coffee](https://www.stokbrew.com/cold-brew/cold-brew-coffee/unsweetened-decaf-cold-brew-coffee-48oz/). Complete ingredients and relevant Nutrition Facts; exact-variant caffeine not captured. |
| `stok-decaf-not-too-sweet-cold-brew` | Reviewed | [STōK DECAF NOT TOO SWEET Black Cold Brew Coffee](https://www.stokbrew.com/cold-brew/cold-brew-coffee/not-too-sweet-decaf-cold-brew-coffee-48oz). Complete ingredients and relevant Nutrition Facts; exact-variant caffeine not captured. |
| `la-colombe-everyday-draft-latte` | Reviewed | [La Colombe Everyday Draft Latte](https://www.lacolombe.com/products/draft-latte). Complete ingredients, relevant Nutrition Facts and product-page caffeine declaration. |
| `la-colombe-vanilla-draft-latte` | Reviewed | [La Colombe Vanilla Draft Latte](https://www.lacolombe.com/products/vanilla-draft-latte). Complete ingredients, relevant Nutrition Facts and product-page caffeine declaration. |
| `la-colombe-triple-draft-latte` | Reviewed | [La Colombe Triple Draft Latte](https://www.lacolombe.com/products/triple-draft-latte). Complete ingredients, relevant Nutrition Facts and product-page caffeine declaration. |
| `la-colombe-mocha-draft-latte` | Reviewed | [La Colombe Mocha Draft Latte](https://www.lacolombe.com/products/mocha-draft-latte). Complete ingredients, relevant Nutrition Facts and product-page caffeine declaration. |
| `la-colombe-caramel-draft-latte` | Reviewed | [La Colombe Caramel Draft Latte](https://www.lacolombe.com/products/caramel-draft-latte). Complete ingredients, relevant Nutrition Facts and product-page caffeine declaration. |
| `la-colombe-oatmilk-vanilla-draft-latte` | Reviewed | [La Colombe Oatmilk Vanilla Draft Latte](https://www.lacolombe.com/products/oatmilk-draft-latte-vanilla). Complete ingredients, relevant Nutrition Facts and product-page caffeine declaration. |
| `la-colombe-oatmilk-everyday-draft-latte` | Reviewed | [La Colombe Oatmilk Everyday Draft Latte](https://www.lacolombe.com/products/oatmilk-draft-latte). Complete ingredients, relevant Nutrition Facts and product-page caffeine declaration. |
| `dunkin-cold-brew-concentrate` | Reviewed | [Dunkin' Cold Brew Concentrate](https://www.dunkinathome.com/products/concentrates/cold-concentrates-black). Complete ingredients and relevant Nutrition Facts; caffeine not stated. |
| `dunkin-caramel-cold-brew-concentrate` | Reviewed | [Dunkin' Caramel Cold Brew Concentrate](https://www.dunkinathome.com/products/concentrates/cold-concentrates-caramel). Complete ingredients and relevant Nutrition Facts; caffeine not stated. |
| `dunkin-pumpkin-spice-cold-brew-concentrate` | Reviewed | [Dunkin' Pumpkin Spice Cold Brew Concentrate](https://www.dunkinathome.com/products/concentrates/cold-concentrates-pumpkin). Complete ingredients and relevant Nutrition Facts; caffeine not stated. |
| `starbucks-signature-black-cold-brew-concentrate` | Reviewed via first-party index; sugar fields partial | [Starbucks Cold Brew Multi-Serve Concentrate Signature Black](https://athome.starbucks.com/products/cold-brew-multi-serve-concentrate-signature-black). Ingredients, serving, calories, sodium and approximate caffeine captured. No total/added sugar declaration shown. |
| `starbucks-caramel-dolce-cold-brew-concentrate` | Reviewed via first-party index; sugar fields partial | [Starbucks Flavored Cold Brew Multi-Serve Concentrate Caramel Dolce](https://athome.starbucks.com/products/cold-brew-flavored-multi-serve-concentrate-caramel-dolce). Ingredients, serving, calories, sodium and approximate caffeine captured. No total/added sugar declaration shown. |
| `starbucks-madagascar-vanilla-cold-brew-concentrate` | Reviewed via first-party index; sugar fields partial | [Starbucks Flavored Cold Brew Multi-Serve Concentrate Madagascar Vanilla](https://athome.starbucks.com/products/cold-brew-flavored-multi-serve-concentrate-madagascar-vanilla). Ingredients, serving, calories, sodium and approximate caffeine captured. No total/added sugar declaration shown. |
| `starbucks-brown-sugar-cinnamon-cold-brew-concentrate` | Reviewed via first-party index; sugar fields partial | [Starbucks Flavored Cold Brew Multi-Serve Concentrate Brown Sugar Cinnamon](https://athome.starbucks.com/products/starbucks-cold-brew-multi-serve-concentrate-Brown-Sugar-Cinnamon). Ingredients, serving, calories, sodium, total sugars and approximate caffeine captured. Added sugars not separately declared. |
| `stok-extra-bold-black-cold-brew` | **Excluded: incomplete ingredient statement** | [STōK Extra Bold](https://www.stokbrew.com/cold-brew/cold-brew-coffee/extra-bold-cold-brew-coffee-48oz/). Manufacturer HTML and indexed page both show the malformed statement quoted below. Requires a corrected manufacturer statement or legible matching package label. |

## Corrections to the starter research

The [Extra Bold page](https://www.stokbrew.com/cold-brew/cold-brew-coffee/extra-bold-cold-brew-coffee-48oz/) literally publishes `COFFEE (FILTERED WATER, NATURAL FLAVOR.` with an unclosed parenthesis. Both slash/no-slash URLs and direct raw HTML confirm the defect. The starter document's complete parenthetical cannot be substantiated from this source and is not imported. The page also labels its sugar row “Trans Sugars”; that is not silently relabeled total sugars. It lists 20 calories, 10 mg sodium and 0 g added sugar per 12 fl oz, but those do not make the incomplete ingredients suitable for ingestion.

The [Bright & Mellow page](https://www.stokbrew.com/cold-brew/cold-brew-coffee/bright-mellow-cold-brew-coffee-48oz/) likewise says “Trans Sugars 0g”; its complete ingredient statement is usable, with total sugar left unknown. Its asterisk identifies Rainforest Alliance Certified coffee; that footnote and facility statement are retained in notes.

The La Colombe pages now explicitly declare caffeine for [Vanilla](https://www.lacolombe.com/products/vanilla-draft-latte) (155 mg), [Mocha](https://www.lacolombe.com/products/mocha-draft-latte) (155 mg), and [Oatmilk Vanilla](https://www.lacolombe.com/products/oatmilk-draft-latte-vanilla) (120 mg), filling gaps in the starter table. Their ingredient statements include the less-than-1% / less-than-2% groupings, which must not be dropped. Mocha's page displays 4 g added sugar and 12% DV; this snapshot keeps declared grams and does not import the inconsistent DV.

The [Madagascar Vanilla first-party page](https://athome.starbucks.com/products/cold-brew-flavored-multi-serve-concentrate-madagascar-vanilla) indexed content supplies 15 calories, 0 mg sodium and approximately 220 mg caffeine per 6 fl oz concentrate making 12 fl oz prepared. It omits total and added sugars. [Brown Sugar Cinnamon](https://athome.starbucks.com/products/starbucks-cold-brew-multi-serve-concentrate-Brown-Sugar-Cinnamon) shows 11 g total sugars with 22% DV, without a distinct added-sugars row; the latter therefore remains unknown.

[Dunkin' Pumpkin Spice](https://www.dunkinathome.com/products/concentrates/cold-concentrates-pumpkin) has “Artificially Flavored” in its title, but lists only water, coffee and natural flavor in its ingredient statement. The source inconsistency is recorded without adding an undeclared ingredient. All three Dunkin' concentrates specify a 6 fl oz / 180 mL concentrate serving yielding 12 fl oz prepared and a 31 fl oz bottle.

## Validation

The JSON contains 20 unique discovery IDs, all mapped to this scoped bootstrap batch. Every record has a nonempty exact-variant ingredient statement, first-party URL, access date and explicit variant scope. No reviewed record claims package verification. No data is supplied for the one excluded discovery row.

