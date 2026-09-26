# ClearSip roadmap

## Now — make the existing product real

1. **Connect the UI to FastAPI.** Replace `src/data.js` lookup with `GET /api/products` and `GET /api/products/{packageId}`. Display the source, package size, market, review date, and verification status from SQL.
2. **Show catalog discovery honestly.** Add a browse/search screen for the 29 source-backed candidates. A candidate must show “label not yet reviewed” and never borrow ingredients from another size or flavor.
3. **Deploy a preview.** Import the public GitHub repository into Vercel, add a managed PostgreSQL provider, set `DATABASE_URL`, and create separate preview/production environments.
4. **Add automated checks.** Test API search, product detail, source/verification labels, and the no-match state in CI.

## Next — expand the catalog safely

1. **Build an FDC import worker outside Vercel Functions.** Import USDA FoodData Central Branded Foods data into PostgreSQL, retain source release/FDC ID/source hash, and run monthly updates.
2. **Barcode-first matching.** Use a barcode to resolve an exact GTIN/package before falling back to name/OCR search. Queue unknown codes for review.
3. **Review workflow.** Add staff-only approval states: discovery candidate → package label reviewed → published → superseded. Preserve prior label versions instead of overwriting them.
4. **Ingredient profiles.** Expand the current reusable ingredient profiles with an editorial review process and primary-source citations.

## Before a public health launch

1. **Clinical/regulatory review.** Have qualified reviewers approve all consumer-facing nutrition, caffeine, sweetener, allergy, pregnancy, and disease-related wording.
2. **Privacy controls.** Publish retention/deletion rules and explicit consent before storing any user images, videos, voice samples, or search history. The current MVP keeps scans in the browser.
3. **Accessibility and localization.** Test keyboard navigation, contrast, screen readers, mobile cameras, and Spanish-language labeling needs.
4. **Trust and corrections.** Add a visible “report label mismatch” route and publish source/review timestamps on every result.

## Product rule

ClearSip does not produce a universal “healthy/unhealthy” score. It shows a label fact, an ingredient’s role, the disclosed amount, sourced context, and what remains unknown.
