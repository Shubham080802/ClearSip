# Open Food Facts image-collection API audit

Checked 2026-09-28 against official documentation and source schemas. This is an integration note, not a legal opinion or proof that any particular photo is suitable. No product photos were downloaded or uploaded for this note.

## Metadata discovery

The current API introduction recommends v3.6 for new integrations, but structured search is still available only through `/api/v2/search`. V2 has no full-text name search; do not send a drink name as `search_terms` and assume it filters results. Reads require a custom identifying User-Agent, not an account. The introduction requests registration of API usage; submit that form as a separate user-approved external action. The documented limits are **10 search requests/minute/IP** and **15 product reads/minute/IP**; global throttles can return 503. Cache responses, pause/back off on failures, and use an export rather than API crawling for more than a few hundred products. [API introduction](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/)

Schema-verified request shape for a bounded first-page brand audit (example brand, not proof of complete brand coverage):

```http
GET https://world.openfoodfacts.org/api/v2/search?brands_tags=powerade&countries_tags_en=united-states&page=1&page_size=12&fields=code,product_name,product_name_en,brands,brands_tags,countries_tags,quantity,images,selected_images,last_modified_t
User-Agent: ClearSip-ImageAudit/0.1 (https://github.com/Shubham080802/ClearSip)
```

`brands_tags` and `countries_tags_en` are documented filter names. Use canonical taxonomy tags or known synonyms; resolve unfamiliar brand spellings against OFF taxonomy data rather than guessing all brands from a first token. Country data is a search lead, not independent proof that the pictured packaging is the US formulation. [Tag parameters](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/docs/api/ref/schemas/tags_parameters.yaml)

`fields` is a comma-separated projection. `count` is the total matches, but **`page_count` is the number of products on this page**, not the number of pages. Compute total pages from `count/page_size`; distinguish “first page audited” from “no photos exist.” The schema supports comma AND, pipe OR, and minus exclusion in tag filters. Fetching a brand once and matching exact ClearSip variants locally reduces repeated searches. [Search and pagination schema](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/docs/api/ref/api.yaml), [Fields parameter](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/docs/api/ref/parameters/product_available_fields.yaml)

For a known barcode, the documented backward-compatible metadata shape is:

```http
GET https://world.openfoodfacts.org/api/v2/product/{barcode}?fields=code,product_name,product_name_en,brands,brands_tags,countries_tags,quantity,images,selected_images,last_modified_t
```

Keep v2 reads consistent with the v2 search parser for this first audit. V3.3 changed image structure, and v3.6 changed tags; a migration must explicitly adapt `images.uploaded`/`images.selected`, not reuse a numeric-key parser silently. [Product endpoint](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/docs/api/ref/api.yaml), [Schema change log](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/docs/api/ref-api-and-product-schema-change-log.md)

## Image provenance and retrieval

In v2, numeric keys in `images` describe original uploads; a selected role such as `front_en` has `imgid` pointing to the original upload. Read `uploader`, `uploaded_t`, and available `sizes` from that numeric record. These identify the contributing account/upload time, **not a verified photographer, physical bottle, capture session, or manufacture date**. Preserve the product-page link, code, raw image ID, selected role/revision, uploader, upload timestamp, retrieval date, license, and transformations. Missing provenance should remain explicitly missing. [Raw image schema](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/docs/api/ref/schemas/image.yaml), [Role schema](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/docs/api/ref/schemas/image_role.yaml)

`selected_images` supplies role/size/language URLs. Prefer front images for packaging recognition; ingredient and nutrition crops are not automatically additional front-label examples. Raw numeric uploads need visual inspection. Selected crops, resized versions, and augmentations of one raw image are **one source group**, not independent training/test photographs. [Product image schema](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/docs/api/ref/schemas/product_images.yaml)

OFF recommends its server for up to about ten images, sequentially and at the required resolution, and **AWS for larger collections**. Barcode folders pad short barcodes to 13 digits and split as `AAA/BBB/CCC/remainder`; raw filenames are `{imgid}.jpg` or `{imgid}.400.jpg`. [Download guide](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/how-to-download-images/)

AWS example shape:

```text
https://openfoodfacts-images.s3.eu-west-3.amazonaws.com/data/401/235/911/4303/1.400.jpg
```

The bucket is `openfoodfacts-images`, region `eu-west-3`, under `data/`. It syncs monthly, so a metadata entry does not guarantee that its image currently exists there. An index is available at `data/data_keys.gz`; do not download the entire collection for an 83-class audit. [Official AWS guide source](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/docs/api/aws-images-dataset.md)

## Rights gates

The OFF Terms source specifies ODbL for the database, DbCL for individual data, and **CC BY-SA 3.0 for photos**. Re-users must credit OFF with an appropriate link and mention the license; contributors accept product-page-link credit. The photo license does not clear packaging artwork, trademarks, or pictured people. Re-users must assess other rights and applicable exceptions. The English terms are informational; French terms prevail. [Official Terms source](https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-web/main/lang/en/texts/terms-of-use.html)

CC BY-SA permits sharing/adaptation subject to its conditions, including attribution and ShareAlike for distributed adaptations; it gives no blanket warranty of all necessary permissions. Do not mark photo/model-distribution rights approved merely because an OFF URL exists. [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)

Creative Commons explains that AI-training obligations depend on whether copyright permission is required; attribution/ShareAlike can concern publicly shared models or outputs when applicable. Its conservative approach preserves those conditions. Therefore keep acquired photos and OFF-derived metadata separate from MIT code, and review the eventual model's distribution terms before browser deployment. This is a release gate, not a claim that every classifier weight is necessarily a derivative work. [Creative Commons AI-training guidance](https://creativecommons.org/using-cc-licensed-works-for-ai-training-2/)

## ClearSip decision

Audit every concrete recognition target, record candidate metadata without automatic acceptance, then visually verify exact flavor, regular/zero/diet formulation, package market and label version. Broad family targets still require exact variants. Report missing, partial-search, identity-review-pending and rights-review-pending states separately. Online images may seed training, but independent real-camera validation remains necessary; never turn multiple sizes/crops of one upload into claimed photo diversity or fabricate capture-session/bottle identities.
