# Online packaging photos for visual recognition

Researched 2026-09-28. Research only: no images downloaded, imported, or used to train a model.

## Conclusion

Yes: properly licensed online photos can seed ClearSip's image training. They must be matched to exact catalog variants and supplemented with independent camera photos. Finding an image online does not establish reuse rights, sufficient training diversity, or full catalog coverage.

## Candidate sources and limits

| Source | Useful capability | Required checks |
| --- | --- | --- |
| Open Food Facts | Barcode-linked raw images and selected front/ingredient/nutrition images; official guidance recommends its AWS image dataset for larger collections. | Its image-license link points to CC BY-SA 3.0, while database rights are ODbL and individual database contents use the Database Contents License. Preserve exact license/version and attribution; review depicted packaging rights. The image license does not erase those other rights. [License guidance](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/tutorials/license-be-on-the-legal-side/), [image license](https://creativecommons.org/licenses/by-sa/3.0/), [image access](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/how-to-download-images/). |
| Wikimedia Commons | Possible supplementary packaging photographs. | Inspect each file's creator, source, license/version, and restrictions. Commons does not warrant licensing correctness; trademarks and other rights may remain. No verified all-catalog coverage. [Reuse guidance](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia). |
| Manufacturer/retailer sites | Current product imagery could fill gaps if permission is obtained. | Do not treat public display as a training grant. Coca-Cola's US terms restrict copying, scraping and database creation without authorization; Walmart expressly restricts using its materials for AI/ML training without prior written consent. These are examples, not a blanket assessment of every site. [Coca-Cola terms](https://www.coca-cola.com/us/en/legal/terms-of-service), [Walmart terms](https://www.walmart.com/help/article/walmart-com-terms-of-use/3b75080af40340d6bbd596f116fae5a0/). |
| Existing recognition benchmarks | Useful for evaluating approaches, not necessarily ClearSip's US variants. | RPC publishes CC BY-NC-SA 4.0 and asks users to contact its author for nonacademic uses. It is not an unrestricted production dataset. Exact US flavor/size overlap has not been verified. [RPC project and license](https://rpc-dataset.github.io/). |

## Model and dataset licensing are separate decisions

ClearSip's MIT code license cannot relicense third-party photos or databases. Whether training or distributed model weights constitute adaptations depends on facts and applicable law. Creative Commons explicitly describes the uncertainty; its conservative guidance recommends preserving attribution and applying ShareAlike to publicly shared models based on SA material. Do not assume the browser-distributed model can automatically be MIT. Resolve the model's license before deployment, and obtain specific permission or legal advice where needed. [Creative Commons AI-training primer](https://creativecommons.org/using-cc-licensed-works-for-ai-training-2/).

## Proposed collection and testing workflow

1. Audit every concrete catalog target against online sources. Match brand, exact flavor, regular/diet/zero formulation, US market, package type/size, barcode where available, and packaging revision. OFF supplies barcode and image metadata, but those fields do not independently prove a correct match. [Product schema](https://openfoodfacts.github.io/documentation/docs/Product-Opener/schemas/schemas/product/).
2. Record source URL, creator, license/version and URL, attribution, retrieval date, identity evidence, original image ID, hash, source group, and approved training/model-distribution basis. Keep unresolved items out of training.
3. Human-review labels, deduplicate originals and near-duplicates, and keep crops/augmentations of the same original in one split. Multiple resized copies are not independent samples.
4. Use permitted web photos plus diverse camera training captures. Reserve separate real-camera validation and test sessions, with different physical packages/backgrounds/devices. White-background product images alone do not demonstrate live-camera performance; this is a project recommendation, not an accuracy guarantee.
5. Measure precision, recall and unknown rejection for every exact variant, retaining old classes when adding batches. Keep OCR/barcode/manual confirmation as fallbacks. Recognition identifies a database record, not hidden ingredients or medical safety.

## Unresolved before implementation

- No source has been verified to cover all 83 specific targets or all their US package sizes; three family leads still need exact variants.
- OFF's AWS mirror is monthly and may omit recent images. [AWS dataset documentation](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/aws-images-dataset/).
- Rights for packaging artwork, photo modifications, derived datasets, and browser-distributed model weights require the actual intended-use review.
- Current `ml/dataset.py` accepts only `self_photographed` or `written_authorization`; licensed online material needs a provenance-aware manifest extension, not relabeling as self-photographed.
- Authorized independent camera holdouts and evidence of per-variant performance are still missing. No bulk ingestion or training has been performed.
