# Focused energy-drink and Dr Pepper label audit

Accessed September 26, 2026. Follow-up scope: `monster-ultra-zero`, `red-bull-original`, and `dr-pepper-blackberry`. The data filename follows the requested follow-up batch name; its one accepted record is a soda.

| Discovery ID | Outcome | Evidence |
| --- | --- | --- |
| `dr-pepper-blackberry` | **Reviewed exact US regular variant** | [Official product page](https://www.kdpproductfacts.com/product/a0eWP000000sWfdYAE) and its [public product-details API](https://www.kdpproductfacts.com/lwr/apex/v66.0/PF_ProductAPI/getProductDetail?methodParams=%7B%22locale%22%3A%22en_US%22%2C%22productId%22%3A%22a0eWP000000sWfdYAE%22%7D) supply the full ingredient sequence, serving, nutrition, caffeine, and size variants. |
| `monster-ultra-zero` | **Excluded: full ingredients not found** | [US manufacturer page](https://www.monsterenergy.com/en-us/energy-drinks/zero-sugar/zero-ultra/) provides product identity, sizes and highlights, not a full ordered ingredient statement. [NSF's official US certification listing](https://www.nsfsport.com/certified-products/listing-detail.php?id=1788029) links an actual Nutrition Facts image, but that image omits ingredients. |
| `red-bull-original` | **Excluded: full ingredients not found** | [US manufacturer ingredients page](https://www.redbull.com/us-en/energydrink/products/red-bull-energy-drink-ingredients-list) contains explanatory ingredient categories and Nutrition Facts, not the complete ordered statement. [Manufacturer FAQ](https://www.redbull.com/us-en/energydrink/questions/what-are-the-ingredients-of-red-bull-energy-drink) directs readers to the can label. |

## Dr Pepper Blackberry provenance and transcription

KDP's US public product-facts endpoint identifies record `a0eWP000000sWfdYAE` as active **Dr Pepper® Blackberry Flavored Soda - 12 fl oz - US**. This distinguishes it from the separately listed fountain and Zero Sugar variants. It reports 150 calories, 39 g total sugars, 39 g added sugars, 55 mg sodium and 41 mg caffeine per 12 fl oz. Related product variations are 12 and 20 fl oz; the imported nutrition is only the 12 fl oz serving. [Source](https://www.kdpproductfacts.com/lwr/apex/v66.0/PF_ProductAPI/getProductDetail?methodParams=%7B%22locale%22%3A%22en_US%22%2C%22productId%22%3A%22a0eWP000000sWfdYAE%22%7D)

The API returns two ordered ingredient arrays. Its public [product-detail frontend bundle](https://www.kdpproductfacts.com/webruntime/view/dd9d69f0cfc47e03525f50855a682451/prod/en-US/pF_Product_Detail_1_view) exposes `pfProductService`, which concatenates the main array with the literal heading “Contains less than 2% of:” and the `otherIngredients` array. The reviewed statement retains that grouping and order; commas and sentence punctuation are normalized from the structured rows. Ingredient definitions, promotional statements and nutritional interpretations were not folded into the label.

Main ingredients: CARBONATED WATER; HIGH FRUCTOSE CORN SYRUP. Less-than-2% ingredients: CARAMEL COLOR; NATURAL AND ARTIFICIAL FLAVORS; SODIUM BENZOATE (PRESERVATIVE); PHOSPHORIC ACID; CAFFEINE; SODIUM PHOSPHATE. [Source](https://www.kdpproductfacts.com/lwr/apex/v66.0/PF_ProductAPI/getProductDetail?methodParams=%7B%22locale%22%3A%22en_US%22%2C%22productId%22%3A%22a0eWP000000sWfdYAE%22%7D)

The product ID was discovered through the site's public `PF_ProductAPI.getProductsFiltered` API for the Ready-to-Drink category `a0d3h000000vdYNAAY`, not guessed from a retailer. It is a manufacturer-hosted data source, but no UPC or package-version match has been established; reviewed scope remains `variant`.

## Rejected or incomplete leads

NSF explicitly identifies Monster Zero Ultra as sold in the United States, 16 fl oz (473 mL), serving one can. Its linked [label image](https://info.nsf.org/Certified/Common/cfs/C0894145/C0894146/Monster%20Energy%20Zero%20Ultra/Monster/1788029/Label_01.PNG) was downloaded and visually read: 10 calories, 380 mg sodium, 6 g carbohydrate, 0 g total/added sugars and 2 g erythritol. The image is only Nutrition Facts and its footnotes. These facts do not establish the full formulation, so no Monster ingredient record is created. No certification claim is interpreted as an overall health rating.

Red Bull's US page is itself inconsistent about total sugar: the explanatory prose says 27 g, while its 8.4 fl oz nutrition table says 26 g. No full declared statement was found to resolve a current exact label. Foreign-market labels, retailer listings, user-submitted labels, old research-paper reproductions and ingredient highlight lists were not used as replacements.

KDP and Dr Pepper product-page rendering was not available through web text extraction; the official public JSON API supplied the successful source. Browser fallback was unavailable in the environment. Focused official/SmartLabel/PDF searches did not produce usable full US statements for Monster or Red Bull. This is a research gap, not a claim that no such official label exists.

## Deliverable

`data/reviewed-labels-energy.json` contains one complete, source-supported variant record for `dr-pepper-blackberry`. The other two discovery IDs remain excluded pending a complete official US ingredient statement.

