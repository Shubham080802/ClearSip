# ClearSip

ClearSip is an early, educational beverage-label awareness app. A user can type a product name, scan a label image, scan a frame from a video, or say a drink name. The app matches a versioned dataset and explains each declared ingredient in plain language, with source links and clear uncertainty.

## What is in this MVP

- Text lookup for Coca-Cola Zero Sugar and Monster Energy Zero Sugar (US seed records)
- Local, in-browser OCR for a product image and a selected video frame
- Browser-native speech recognition for a spoken drink name
- Product facts separated from interpretive context
- Ingredient roles, amount/context caveats, FDA sources, source dates, and formulation-region notes
- A research note documenting approved sources and health-language guardrails

## Run locally

```bash
npm install
npm run dev
```

Then open the local Vite address shown in the terminal. For a production check, run `npm run build`.

## Data safety and provenance

The seed dataset is intentionally small. See [the research note](docs/research/seed-data-sources.md) before adding records. In particular:

- Use a manufacturer product page, manufacturer label PDF, or the package itself as the product source; a retailer transcription is only a provisional lead.
- Record market, package size, source URL, access date, verification state, and formulation/version with every item.
- Do not classify ingredients as universally “good,” “bad,” “harmful,” or “beneficial.” Present a label fact, its function, the known quantity, applicable authoritative context, and uncertainty separately.
- Do not calculate an ADI percentage unless the label or manufacturer actually discloses the ingredient amount.
- Do not retain user images or videos in this MVP. OCR occurs in the browser and the upload is not sent to an application server.

## Recommended next steps

1. Move the seed data into a database with `products`, `product_labels`, `ingredients`, `ingredient_assessments`, and `sources` tables.
2. Add barcode lookup (for exact package-size matching) and a reviewed “unmatched label” queue.
3. Add auth, consent, retention controls, and a moderation/review workflow before retaining any uploads.
4. Have qualified regulatory and nutrition reviewers approve user-facing assessment language before public release.
5. Add food products only after the beverage source/provenance workflow is stable.

## Scope statement

ClearSip provides educational label information, not medical advice. Food suitability can change with allergies, medications, pregnancy, age, health conditions, and total dietary intake.
