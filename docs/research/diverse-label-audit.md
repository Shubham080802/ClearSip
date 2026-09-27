# Diverse beverage ingredient-label audit

Accessed **2026-09-26**. Scope: all 35 discovery IDs in the diverse non-coffee batch. All 35 now have an explicit ingredient declaration from an official manufacturer variant page or a label asset linked in that page's public data. This is **variant-level evidence**, not verification of each discovered package, UPC, production batch, or current store availability. The machine-readable result is [reviewed-labels-diverse.json](../../data/reviewed-labels-diverse.json).

## Evidence rules

- Read the ingredient declaration for each exact named variant; do not transfer a brand-level ingredient claim across flavors.
- Retain unknown values as null. No caffeine-free inference was made from an ingredient list. V8 Zero Sugar product pages name tea caffeine but do not state an amount in the reviewed text.
- Hint's exact variant pages declare Zero Sugar; their nutrition table gives 0 calories (with an erroneous “g” suffix), 0 mg sodium, and a 16 fl oz (474ml) serving. Added sugars are not separately stated. The stored 0 g total sugar follows the variant's Zero Sugar declaration.
- Waterloo's exact variant nutrition panels give calories, total sugars, and sodium but no serving or package size. Those missing fields remain unknown.
- Oatly's declared added sugars are retained even where the ingredient list has no named added sweetener; its pages explain the production process. No medical or suitability conclusion is attached.
- OLIPOP rows use only the shelf-stable **6 g fiber** formula pages. Their refrigerated 9 g formulas are separate. Packaging and availability can vary.
- The Ocean Spray website is too large for the web reader. Public page HTML was read directly, the exact product object's nutritionalInfoImage association was extracted, and its manufacturer-hosted image was visually reviewed. Asset links appear below.

## Package mismatches and caveats

Ocean Spray's 64 oz 100% Cranberry page currently points to a 10 oz Nutrition Facts image with no ingredient statement. The same named variant's official 96 oz product page supplies a full combined label. The row therefore cites that 96 oz page and explicitly records the 96 oz evidence; it does not verify a 64 oz formula or package.

The 64 oz Diet Cranberry page currently links a 10 oz multipack label. The ingredients are retained only at variant scope, and serving/nutrition are withheld because that linked label says 10 calories per bottle while the 64 oz page says 5 calories per 8 fl oz. Do not merge those serving bases. Cran x Cherry and Diet Cranberry With Lime link images with “2018” in their filenames; they were available on the current manufacturer page, but their package revision is unknown.

V8 Original uses the foodservice 11.5 fl oz can page and its own nutrient values, rather than the consumer page's 8 fl oz values.

## Every scoped discovery

“Reviewed variant” means a confirmed ingredient statement, with package verification still outstanding.

| Discovery ID | Status and limitation | Primary source |
| --- | --- | --- |
| `hint-water-blackberry` | Reviewed variant; added sugar not separately stated | [Hint Water Blackberry](https://www.drinkhint.com/products/blackberry-hint-water) |
| `hint-water-cherry` | Reviewed variant; added sugar not separately stated | [Hint Water Cherry](https://www.drinkhint.com/products/cherry-hint-water) |
| `hint-water-crisp-apple` | Reviewed variant; added sugar not separately stated | [Hint Water Crisp Apple](https://www.drinkhint.com/products/crisp-apple-hint-water) |
| `hint-water-georgia-peach` | Reviewed variant; added sugar not separately stated | [Hint Water Georgia Peach](https://www.drinkhint.com/products/georgia-peach-hint-water) |
| `hint-water-pineapple` | Reviewed variant; added sugar not separately stated | [Hint Water Pineapple](https://www.drinkhint.com/products/pineapple-hint-water) |
| `hint-water-watermelon` | Reviewed variant; added sugar not separately stated | [Hint Water Watermelon](https://www.drinkhint.com/products/watermelon-hint-water) |
| `oatly-full-fat` | Reviewed variant | [Oatly Chilled Oatmilk Full Fat](https://www.oatly.com/en-us/products/chilled-oatmilk/chilled-oatmilk-full-fat-64-oz) |
| `oatly-low-fat` | Reviewed variant | [Oatly Chilled Oatmilk Low Fat](https://www.oatly.com/en-us/products/chilled-oatmilk/chilled-oatmilk-low-fat-64-oz) |
| `oatly-original` | Reviewed variant | [Oatly Chilled Oatmilk Original](https://www.oatly.com/en-us/products/chilled-oatmilk/chilled-oatmilk-64-oz) |
| `oatly-unsweetened` | Reviewed variant | [Oatly Chilled Oatmilk Unsweetened](https://www.oatly.com/en-us/products/chilled-oatmilk/chilled-oatmilk-unsweetened-64-oz) |
| `ocean-spray-100-juice-cranberry` | Reviewed variant; 96 oz evidence, original 64 oz package pending | [Ocean Spray 100% Juice Blend Cranberry](https://www.oceanspray.com/products/100-juice-blend-cranberry-2-96-oz) · [label image](https://images.ctfassets.net/fk5croonv4b3/2GAKOt1nbJfSgfD1nmsh9u/4cf5afe081f70b44aa045e16b4a9cb5e/96oz_OS_100-_Cranberry_Combo.png) |
| `ocean-spray-cran-cherry` | Reviewed variant; linked image filename dated 2018 | [Ocean Spray Cran x Cherry](https://www.oceanspray.com/products/cran-cherry-cranberry-cherry-juice-drink-64-oz) · [label image](https://images.ctfassets.net/fk5croonv4b3/3zKyhZMQhJSrPBT8SBwaXc/cc546c86194539dd6f10b66d9d0cdf2b/2018_OS_64oz_CranCherry_Nutrition_Facts.jpg) |
| `ocean-spray-cran-lemonade` | Reviewed variant | [Ocean Spray Cran x Lemonade](https://www.oceanspray.com/products/cran-lemonade-cranberry-lemonade-juice-drink-64-oz) · [label image](https://images.ctfassets.net/fk5croonv4b3/1K6KJNNi52kMmmSnRz53WG/8177ef12d45e6d680caf38f1a2d6c294/64oz_OS_CranLemonade_CMB_00002_0000032240__7862_.png) |
| `ocean-spray-cranberry-calcium` | Reviewed variant | [Ocean Spray Cranberry Juice Cocktail With Calcium](https://www.oceanspray.com/products/cranberry-juice-cocktail-with-calcium-64-oz) · [label image](https://images.ctfassets.net/fk5croonv4b3/7oKXXUITD398Tgwo0ELtkw/de2cebfe8871ccbb24e1f812dd4161a4/64oz_OS_Cranberry_Calcium_ING_00002_0000018681__5368_.png) |
| `ocean-spray-cranberry-lime` | Reviewed variant | [Ocean Spray Cranberry Juice Cocktail With Lime](https://www.oceanspray.com/products/cranberry-juice-cocktail-with-lime-64-oz) · [label image](https://images.ctfassets.net/fk5croonv4b3/4HDyTDPR2fXFrHp0zPyeCW/3d2bc2e5d3522181793a1072a4eafb1f/64oz_OS_Cranberry_Lime_NutFacts.png) |
| `ocean-spray-diet-cranberry` | Reviewed variant; linked package mismatch, nutrition withheld | [Ocean Spray Diet Cranberry](https://www.oceanspray.com/products/diet-cranberry-juice-drink-64-oz) · [label image](https://images.ctfassets.net/fk5croonv4b3/7MamAxguyeQv0OCulycEmJ/121b5f2878e4456625b8ba38702cf6b8/10oz_Multipack_OS_DietCran_Combo.png) |
| `ocean-spray-diet-cranberry-lime` | Reviewed variant; linked image filename dated 2018 | [Ocean Spray Diet Cranberry With Lime](https://www.oceanspray.com/products/diet-cranberry-juice-drink-with-lime-64-oz) · [label image](https://images.ctfassets.net/fk5croonv4b3/2BWpYHkgz7rl2xzXcyc9qr/84b49d1d5f57429173e712164fb99046/2018_OS_64oz_Diet_Cranberry_Lime_Nutrition_Facts.jpg) |
| `ocean-spray-zero-sugar-cranberry` | Reviewed variant | [Ocean Spray ZERO Sugar Cranberry](https://www.oceanspray.com/products/zero-sugar-cranberry-64-oz) · [label image](https://images.ctfassets.net/fk5croonv4b3/25MZTPPdKvocRKgJpJ4Vry/447b93f2814f2e521f6bbb24275ea9b3/Zero_Sugar_Cranberry_NutFacts.jpg) |
| `olipop-classic-root-beer-6g` | Reviewed variant; shelf-stable 6 g formula only | [OLIPOP Classic Root Beer 6 g Fiber](https://drinkolipop.com/products/classic-root-beer-6g-fiber) |
| `olipop-cream-soda-6g` | Reviewed variant; shelf-stable 6 g formula only | [OLIPOP Cream Soda 6 g Fiber](https://drinkolipop.com/products/cream-soda-6g-fiber) |
| `olipop-vintage-cola-6g` | Reviewed variant; shelf-stable 6 g formula only | [OLIPOP Vintage Cola 6 g Fiber](https://drinkolipop.com/products/vintage-cola-6g-fiber) |
| `v8-energy-black-cherry` | Reviewed variant | [V8 Energy Black Cherry](https://www.campbells.com/v8/products/v8-energy/black-cherry/) |
| `v8-energy-orange-pineapple` | Reviewed variant | [V8 Energy Orange Pineapple](https://www.campbells.com/v8/products/v8-energy/orange-pineapple/) |
| `v8-energy-peach-mango` | Reviewed variant | [V8 Energy Peach Mango](https://www.campbells.com/v8/products/v8-energy/peach-mango/) |
| `v8-energy-pomegranate-blueberry` | Reviewed variant | [V8 Energy Pomegranate Blueberry](https://www.campbells.com/v8/products/v8-energy/pomegranate-blueberry/) |
| `v8-energy-zero-sugar-blueberry-raspberry` | Reviewed variant | [V8 Energy Zero Sugar Blueberry Raspberry](https://www.campbells.com/v8/products/v8-energy-zero-sugar/blueberry-raspberry/) |
| `v8-energy-zero-sugar-cherry-lime` | Reviewed variant | [V8 Energy Zero Sugar Cherry Lime](https://www.campbells.com/v8/products/v8-energy-zero-sugar/cherry-lime/) |
| `v8-energy-zero-sugar-strawberry-lemonade` | Reviewed variant | [V8 Energy Zero Sugar Strawberry Lemonade](https://www.campbells.com/v8/products/v8-energy-zero-sugar/strawberry-lemonade/) |
| `v8-original-vegetable-juice` | Reviewed variant | [V8 Original 100% Vegetable Juice](https://www.campbellsfoodservice.com/product/original-100-vegetable-juice-12/) |
| `waterloo-black-cherry` | Reviewed variant; serving and size unknown | [Waterloo Black Cherry](https://www.drinkwaterloo.com/products/black-cherry) |
| `waterloo-grape` | Reviewed variant; serving and size unknown | [Waterloo Grape](https://www.drinkwaterloo.com/products/grape) |
| `waterloo-lemon-lime` | Reviewed variant; serving and size unknown | [Waterloo Lemon Lime](https://www.drinkwaterloo.com/products/lemon-lime) |
| `waterloo-ruby-red-tangerine` | Reviewed variant; serving and size unknown | [Waterloo Ruby Red Tangerine](https://www.drinkwaterloo.com/products/ruby-red-tangerine) |
| `waterloo-strawberry` | Reviewed variant; serving and size unknown | [Waterloo Strawberry](https://www.drinkwaterloo.com/products/strawberry) |
| `waterloo-tropical-fruit` | Reviewed variant; serving and size unknown | [Waterloo Tropical Fruit](https://www.drinkwaterloo.com/products/tropical-fruit) |
# Display integration note

For the Waterloo records, the source does not identify a nutrition serving.
Although it shows general zero declarations, per-serving numeric fields in the
published snapshot are withheld (null). The full ingredient statement remains
available. No serving size or whole-container amount is inferred.

