import assert from "node:assert/strict";
import { findCatalogDiscovery, findCatalogProduct, findCatalogProductByGtin, getCatalogDiscoveries, getCatalogSummary, normalizeName, toDisplayProduct, toDisplaySourceLabel } from "../src/catalog-api.js";
import { renderPackageEvidence } from "../src/package-evidence.js";
import { MAX_IMAGE_BYTES, MAX_VIDEO_BYTES, validateScanFile } from "../src/scan-guardrails.js";
import { findDrink } from "../src/data.js";

const product = {
  id: "cola-12",
  name: "Cola Zero",
  market: "United States",
  serving: "12 fl oz",
  calories: 0,
  total_sugar_g: 0,
  added_sugar_g: 0,
  saturated_fat_g: 0,
  sodium_mg: 40,
  caffeine_mg: 34,
  verification_status: "manufacturer_verified",
  package_evidence: { label_scope:"variant_or_unconfirmed", label_verified:false, gtin_linked:false,
    label_version_id:"cola-v1", verification_status:"manufacturer_verified", source_type:"manufacturer_page" },
  label_observed_on: "2026-09-24",
  label_context: {
    sugar_free_claim_status: "appears_label_aligned",
    frequent_intake_context: "Caffeine: 34 mg.",
  },
  source: { publisher: "Example source", url: "https://example.test" },
  ingredients: [{
    name: "Caffeine",
    role: "Stimulant",
    assessment: "Declared on the label.",
    evidence_status: "worth_watching",
    source_url: null,
  }],
};

assert.equal(normalizeName("Coca-Cola Zero!"), "coca cola zero");

const calls = [];
const fetchFn = async (url) => {
  calls.push(url);
  const response = url.includes("/catalog-summary")
    ? { reviewed_package_labels: 2, catalog_discoveries: 85 }
    : url.includes("/catalog-discoveries")
    ? [{ id: "cola-discovery", variant_name: "Cola Zero" }]
    : url.includes("/products?")
    ? [{ id: "cola-12", display_name: "Cola Zero" }]
    : product;
  return { ok: true, status: 200, json: async () => response };
};

const display = await findCatalogProduct("Cola Zero", fetchFn);
assert.equal(display.name, "Cola Zero");
assert.equal(display.ingredients[0].status, "watch");
assert.equal(display.assessment.title, "The variant's disclosed sugar facts align with the claim; this package is unverified.");
assert.equal(display.packageEvidence.scope, "variant");
assert.match(renderPackageEvidence(display), /Exact package label not yet verified/);
const divergentPanel = { ...product, ingredient_statement:"Water, caffeine", source_label:{
  name:"Cola Zero", ingredients:"Water, DIFFERENT VARIANT", source_url:"https://example.test/other",
  publisher:"Example", serving:"8 fl oz", accessed_on:"2026-09-01" } };
assert.equal(toDisplayProduct(divergentPanel).ingredientStatement, "Water, caffeine",
  "an attached variant panel must not override this package record's ingredient statement");
assert.equal(toDisplayProduct(divergentPanel).serving, "12 fl oz");
const variantOnly = toDisplaySourceLabel({ id:"candidate", market:"United States", source_label:{
  name:"Cola Zero", ingredients:"Water, flavors", source_url:"https://example.test/variant",
  publisher:"Example", serving:"8 fl oz", accessed_on:"2026-09-01" } }, "20 fl oz");
assert.equal(variantOnly.packageEvidence.scope, "variant");
assert.match(variantOnly.assessment.title, /selected package is unverified/);
assert.match(variantOnly.scopeNote, /not a match to the selected package/);
assert.match(renderPackageEvidence(variantOnly), /Selecting a size does not prove/);
assert.match(renderPackageEvidence(variantOnly), /source record dated 2026-09-01/);
const packageReviewed = toDisplayProduct({ ...product, gtin:"012345678905", package_evidence:{
  ...product.package_evidence, label_scope:"package", label_verified:true, gtin_linked:true,
  source_type:"package_observation" } });
assert.equal(packageReviewed.packageEvidence.scope, "package");
assert.equal(toDisplayProduct({ ...product, label_context:{}, gtin:"012345678905", package_evidence:{
  ...product.package_evidence, label_scope:"package", label_verified:true, gtin_linked:true,
  source_type:"package_observation" } }).assessment.title, "This result summarizes the reviewed package label facts.");
assert.match(renderPackageEvidence(packageReviewed, "catalog barcode from image"), /Barcode matched this stored package record/);
assert.match(renderPackageEvidence(packageReviewed), /this selection was not a barcode scan/);
assert.match(renderPackageEvidence(packageReviewed), /Exact package label reviewed/);
assert.equal(calls.length, 2);
assert.equal(toDisplayProduct(product).facts.length, 6);
assert.deepEqual(await getCatalogSummary(fetchFn), { reviewed_package_labels: 2, catalog_discoveries: 85 });
assert.deepEqual(await getCatalogDiscoveries("", fetchFn), [{ id: "cola-discovery", variant_name: "Cola Zero" }]);
assert.deepEqual(await findCatalogDiscovery("Cola Zero", fetchFn), { id: "cola-discovery", variant_name: "Cola Zero" });
assert.equal((await findCatalogProductByGtin("012345678905", fetchFn)).name, "Cola Zero");
assert.equal(await findCatalogProductByGtin("123", fetchFn), null);
assert.equal(validateScanFile({ type: "image/jpeg", size: MAX_IMAGE_BYTES }, "image"), null);
assert.match(validateScanFile({ type: "image/jpeg", size: MAX_IMAGE_BYTES + 1 }, "image"), /12 MB/);
assert.equal(validateScanFile({ type: "video/mp4", size: MAX_VIDEO_BYTES }, "video"), null);
assert.match(validateScanFile({ type: "text/plain", size: 1 }, "video"), /supported video/);

assert.equal(findDrink("diet coke")?.name ?? null, null, "a partial alias must not turn Diet Coke into Coke Zero");
assert.equal(findDrink("monster")?.name ?? null, null, "a brand alone must not select a particular flavor");
const ambiguousFetch = async (url) => ({ ok:true, status:200, json:async() =>
  url.includes("/products?") ? [
    { id:"powerade-grape", display_name:"Powerade Grape" },
    { id:"powerade-orange", display_name:"Powerade Orange" },
  ] : url.includes("/catalog-discoveries?") ? [
    { id:"powerade-grape", variant_name:"Powerade Grape" },
    { id:"powerade-orange", variant_name:"Powerade Orange" },
  ] : { ...product, name:"Powerade Grape" } });
assert.equal(await findCatalogProduct("Powerade", ambiguousFetch), null,
  "a family name must not silently select the first package");
assert.equal(await findCatalogDiscovery("Powerade", ambiguousFetch), null,
  "a family name must not silently select the first discovery");

console.log("catalog API adapter tests passed");
