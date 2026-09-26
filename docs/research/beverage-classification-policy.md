# Packaged-beverage label classification policy (United States)

**Research date:** September 25, 2026  
**Purpose:** A defensible, consumer-facing policy for classifying a *specific, dated US package label*. This is a label-information tool, not medical advice, a laboratory analysis, or a legal determination of whether a manufacturer is compliant.

## Policy decision

ClearSip must not give a beverage an unqualified **“healthy,” “unhealthy,” “harmful,” “safe in large amounts,”** or disease-causation verdict. Those labels suggest a certainty that an ingredient statement and Nutrition Facts panel cannot provide. Instead, every result should contain three independent outputs:

| Output | Allowed values | Meaning |
| --- | --- | --- |
| **Label-claim check** | `matches disclosed label data`, `needs review`, `cannot assess` | A transparent comparison of a *manufacturer’s displayed claim* with the available, package-specific label data. It is not a regulatory ruling. |
| **Nutrition flags per labeled serving and per container** | `high`, `low`, `present`, `not declared`, `not applicable` | Facts based on the Nutrition Facts panel and FDA %DV conventions. Both serving and whole-container totals must be shown when the container has more than one serving. |
| **Consumption context** | `routine-intake caution`, `caffeine context`, `no label-based concern identified`, `insufficient data` | Plain-language context tied to a disclosed nutrient/amount; never a diagnosis or a promise of benefit/safety. |

Use “**more often choose lower in added sugars, sodium, and saturated fat**” rather than calling an individual beverage healthy or unhealthy. That tracks FDA’s consumer label guidance, which also emphasizes that %DV is for one serving and dietary trade-offs happen across the day ([FDA: %DV lows and highs](https://www.fda.gov/food/nutrition-facts-label/lows-and-highs-percent-daily-value-nutrition-facts-label)).

The app may show **“manufacturer uses FDA ‘healthy’ claim”** only when it is visible on the exact package/label version; do not independently award a “healthy” badge. FDA’s updated rule requires qualifying foods to contain a specified amount from a recommended food group and meet limits for added sugars, saturated fat, and sodium ([FDA: use of the “healthy” claim](https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/use-healthy-claim-food-labeling)). A beverage cannot be evaluated against that complete standard from an ingredient list alone.

## Required record before a result can be rated

Rating requires an exact US product, package/GTIN if available, market, label-image or authorized source URL, source/access date, and label-version date. Capture the verbatim ingredient statement, front claims, serving size, servings per container, calories, total sugars, added sugars and %DV, sodium and %DV, saturated fat and %DV, plus caffeine milligrams **only when the label or manufacturer declares a quantity**. Store unknown values as `null`, never zero.

If OCR is uncertain, a product is only a name-level match, the package differs, or the nutrition panel is missing, return **“cannot assess / verify the current package”** rather than a category. USDA/FDC data are useful discovery data but do not replace a current package-specific label.

## Rules for consumer-visible classifications

### 1. “Sugar-free” and “no sugar”

FDA defines the nutrient-content claim “sugar free” as less than 0.5 g sugars per reference amount customarily consumed and per labeled serving. The product generally cannot contain an ingredient that is a sugar or is generally understood to contain sugars, except where the ingredient is marked and linked to an allowed “trivial/negligible/dietarily insignificant amount” statement. A product that is not low/reduced calorie also needs the required calorie-profile claim or disclaimer ([FDA sugar-free claim letter, summarizing 21 CFR 101.60(c)](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/guidance-industry-and-fda-dear-manufacturer-letter-regarding-sugar-free-claims)).

ClearSip rule:

- Show the exact front claim and `matches disclosed label data` only when the Nutrition Facts panel reports **less than 0.5 g total sugars per serving**, the available ingredients do not show an apparent sugar ingredient without the permitted qualification, and any required calorie context is visible. If the applicable RACC cannot be established, retain `needs review`, because the legal standard also applies per RACC. Label every positive screen **“screening result—not a legal compliance finding.”**
- Show `needs review` if total sugars are 0.5 g or more per serving, an apparent sugar-containing ingredient is present without the allowed qualifier, the applicable RACC is unknown, or required claim/disclaimer information is unavailable.
- Do **not** treat “0 g” on the panel as proof of absolute zero; FDA rounding/claim rules matter. Do **not** equate sugar-free with calorie-free, low-calorie, caffeine-free, insulin-neutral, or beneficial for a particular person.
- Keep **“no added sugar”** separate. It does not mean sugar-free: total sugars can still be present. Display total and added sugars distinctly; total sugars have no %DV, while added sugars do ([FDA: %DV guidance](https://www.fda.gov/food/nutrition-facts-label/lows-and-highs-percent-daily-value-nutrition-facts-label)).

### 2. “Preservative-free” / “no preservatives”

There is no FDA nutrient-content threshold comparable to “sugar free” that ClearSip can apply to make a “preservative-free certified” determination. FDA’s labeling material characterizes “contains no preservatives” as a statement about a non-nutritive substance, rather than a nutrient-content claim when it is not used in a nutrient context ([FDA labeling Q&A](https://www.fda.gov/food/dietary-supplements-guidance-documents-regulatory-information/dietary-supplement-labeling-guide-chapter-vi-claims)).

FDA describes preservatives by **function**: they can prevent spoilage or delay changes/rancidity, and notes that an additive may have more than one purpose. Its examples include sodium benzoate, potassium/calcium sorbate, BHA, BHT, EDTA, citric acid, and ascorbic acid ([FDA: types of food ingredients](https://www.fda.gov/food/food-additives-and-gras-ingredients-information-consumers/types-food-ingredients)).

ClearSip rule:

- Use the narrow display phrase **“No known preservative-function ingredient identified in the disclosed statement”** only after the verbatim statement has been parsed against a versioned FDA-context taxonomy. It does **not** validate the marketing claim or establish that no preservative was used anywhere in production.
- If a known preservative-function ingredient is disclosed, show **“preservative-function ingredient disclosed: [name]”** and its label/function—not “harmful chemical.”
- If the statement contains collective terms (for example, flavor) or is incomplete, show **“cannot determine from this label.”** Never infer that an undisclosed substance is present.

### 3. Added sugars and sodium

For each nutrient with a displayed %DV, use FDA’s general convention: **5% DV or less = low** and **20% DV or more = high**, *per serving*. FDA specifically applies this to added sugars and sodium, and says the daily value for sodium is less than 2,300 mg/day ([FDA: added sugars](https://www.fda.gov/food/nutrition-facts-label/added-sugars-nutrition-facts-label); [FDA: sodium](https://www.fda.gov/food/nutrition-facts-label/sodium-your-diet)).

ClearSip rule:

- Flag `high added sugars` at >=20% DV per serving and `low added sugars` at <=5% DV per serving. Show grams and %DV; do not infer a disease outcome from one drink.
- Flag `high sodium` at >=20% DV per serving and `low sodium` at <=5% DV per serving. Show milligrams and %DV.
- For multi-serving containers, calculate and prominently display **per-container** grams/milligrams and summed %DV as an arithmetic aid, clearly marked “if the whole container is consumed.” Do not call the result a personalized daily limit.
- Do not invent a %DV for total sugars, caffeine, or ingredients with no declared quantity.

### 4. Caffeine and “large intake”

Only calculate caffeine-per-container and daily-context comparisons where caffeine milligrams are declared by the manufacturer or an equally package-specific source. FDA says most adults can generally consume 400 mg/day without negative effects, but sensitivity varies by body weight, medicines, medical conditions, and individual factors. FDA advises people who are pregnant, trying to become pregnant, or breastfeeding to consult a health professional; medical experts advise against energy drinks for children and teens ([FDA caffeine guidance](https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much)).

ClearSip rule:

- For a typical adult context only, show the disclosed caffeine amount and its arithmetic share of 400 mg/day. Phrase it: **“[X] mg per container; this is [Y]% of FDA’s cited 400 mg/day context for most adults—not a personal limit.”**
- Add `caffeine context` when the product contains disclosed caffeine; add `routine-intake caution` when the stated number of whole containers would reach or exceed 400 mg. A one-container amount may also be shown as a percentage of 400 mg, without inventing a separate FDA “high caffeine” cutoff. These are product-information flags, not a safety clearance or diagnosis.
- For children/teens, pregnancy/breastfeeding, medication use, a medical condition, or undisclosed caffeine quantity: do not calculate a “safe number of cans.” Direct the user to a clinician/manufacturer as appropriate.
- Caffeine listed in ingredients without a quantity is `caffeine present; amount not declared`, not low or high. FDA notes added caffeine must be in the ingredient list, while quantity disclosure is often voluntary.

### 5. Ingredient roles, benefits, and disease statements

Classify an observed ingredient by **label function**, not moral value: sweetener/sugar source, non-nutritive sweetener, acidulant, preservative-function ingredient, color additive, flavor, stabilizer/emulsifier, caffeine source, vitamin/mineral fortificant, or other/unknown. Cite the ingredient-profile evidence and distinguish “ingredient present” from “amount known.” FDA notes that all ingredients must meet the same safety standard whether naturally or artificially derived ([FDA: types of food ingredients](https://www.fda.gov/food/food-additives-and-gras-ingredients-information-consumers/types-food-ingredients)).

Permitted language:

- “Listed as a sweetener / acidulant / color additive / preservative-function ingredient.”
- “Provides [declared nutrient] at [amount and %DV] per serving.”
- “High added sugars per FDA %DV convention; consider it in the context of the rest of the day.”
- “Evidence/quantity insufficient to assess this product-specific effect.”

Prohibited language unless the exact claim is FDA-authorized/qualified and its conditions and qualifying language are captured:

- “This ingredient causes/prevents/treats [disease].”
- “This drink spikes insulin,” “is toxic,” “damages the body,” or “is safe in unlimited quantities.”
- “The ingredient makes this drink healthy” or “the ingredient benefits every drinker.”

FDA says food health claims are disease-risk-reduction claims requiring premarket review; authorized claims require significant scientific agreement, and qualified claims require FDA-reviewed qualifying language ([FDA: health-claim Q&A](https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/questions-and-answers-health-claims-food-labeling)). Therefore, ClearSip should display a manufacturer’s properly sourced claim verbatim with its qualifier, not generate novel disease claims.

## What a label can and cannot establish

| A package label can support | It cannot support |
| --- | --- |
| The disclosed ingredients, their order by weight, declared nutrient values, serving information, and claims for that dated package. | Exact ingredient amounts (except declared nutrients), full formula, dose-response, absorption, glycemic/insulin response, disease risk for an individual, or whether a product is universally “healthy.” |
| Ingredient functions as contextual education when tied to an authoritative source. | That an FDA-regulated ingredient is “harmful” merely because it is synthetic or hard to pronounce; FDA says naturally and artificially derived ingredients share the same safety standard. |
| A transparent consistency screen for a front claim against visible label facts. | Legal compliance, laboratory purity, contaminants, recalls, manufacturing cross-contact, or undocumented processing aids. |
| A likely relative order by weight for declared ingredients. | Exact ratios or every component: FDA permits exemptions such as incidental additives and permits some collective declarations, including flavors; an observed list is not a complete recipe. ([FDA: ingredient-list requirements](https://www.fda.gov/food/food-additives-and-gras-ingredients-information-consumers/types-food-ingredients)) |

## Data-model requirements for implementation

1. Version all classification rules and ingredient-profile sources. Save `rule_version`, `source_url`, access date, evidence grade, matched label text, and a human-review status with each result.
2. Separate `front_claim` from `claim_screen_result`; use `unknown`, not `pass`, when a required field is absent.
3. Record nutrients both per serving and calculated per package, preserving source values and calculation inputs. Never calculate a quantity from ingredient order.
4. Give each product an `assessment_scope`: `exact_package_verified`, `catalog_label_match`, `name_only`, or `insufficient_data`. Only the first two can show a claim-screen result.
5. Include a visible correction/report path for changed labels, OCR errors, or source conflicts; labels and formulations change.

## Recommended UI wording

Use “**Label facts & context**” as the main section title. Put any caution beside the precise trigger: “Added sugars: 20% DV per serving (high by FDA’s general %DV guide)” or “Caffeine: 160 mg per can; amount is 40% of FDA’s 400 mg/day context for most adults.” Place this disclaimer immediately below: **“This screen explains the current label. It is not medical advice or a determination of product legality. Personal needs vary.”**
