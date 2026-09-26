# ClearSip roadmap

## Completed — make the existing product real

1. **FastAPI catalog lookup.** The UI reads versioned package records from `/api`, displays source/package/review information, and retains a small local fallback only when the API is unavailable.
2. **Honest discovery coverage.** Users can browse and search 85 source-backed candidates across 23 categories, including a packaged-coffee starter batch and diverse juice, energy, water, sparkling-water, oat-beverage, and functional-soda records. Discovery results deliberately withhold ingredient and health panels until a package label is reviewed.
3. **Public Vercel deployment.** The public GitHub repository deploys to Vercel with a managed PostgreSQL database, immutable schema migrations, and production-safe static/API routing.
4. **Automated checks.** Client, API, migration, and FDC-import smoke checks run in CI.
5. **Input and browser safeguards.** OCR and live camera capture stay in the browser; image/video sizes are bounded, content security headers are active, and camera/microphone access is requested only for voluntary scan/search actions.

## Next — expand the catalog safely

1. **Run the controlled FDC refresh.** The manual GitHub Action and PostgreSQL-compatible importer are ready. Add `CLEARSIP_DATABASE_URL` and `FDC_API_KEY` repository secrets, then import focused reviewable batches. A nationwide backfill still requires a dedicated worker and source-release process outside Vercel.
2. **Barcode-first matching.** Done for typed UPC/EAN/GTIN values: an exact catalog code resolves its specific package before name/OCR matching. Camera barcode scanning and unknown-code review remain future work.
3. **Review workflow.** Add staff-only approval states: discovery candidate → package label reviewed → published → superseded. Preserve prior label versions instead of overwriting them.
4. **Ingredient profiles.** Expand the current reusable ingredient profiles with an editorial review process and primary-source citations.

## Before a public health launch

1. **Clinical/regulatory review.** Have qualified reviewers approve all consumer-facing nutrition, caffeine, sweetener, allergy, pregnancy, and disease-related wording.
2. **Privacy controls.** Publish retention/deletion rules and explicit consent before storing any user images, videos, voice samples, or search history. The current MVP keeps scans in the browser.
3. **Accessibility and localization.** Test keyboard navigation, contrast, screen readers, mobile cameras, and Spanish-language labeling needs.
4. **Trust and corrections.** Add a visible “report label mismatch” route and publish source/review timestamps on every result.

## Product rule

ClearSip does not produce a universal “healthy/unhealthy” score. It shows a label fact, an ingredient’s role, the disclosed amount, sourced context, and what remains unknown.
