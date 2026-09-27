import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { buildPackageChoices, hasExplanation } from "../src/package-options.js";
import { toDisplaySourceLabel } from "../src/catalog-api.js";

// Run after the Python bootstrap in CI. Exercise the complete real catalog
// through the same option-building and display functions used by the browser.
const python = process.env.CLEARSIP_TEST_PYTHON || "python";
const rows = JSON.parse(execFileSync(python, ["-c", "import json; from api.index import catalog_discoveries; print(json.dumps(catalog_discoveries(limit=500)))"], { encoding: "utf8" }));
let checked = 0;
for (const row of rows) {
  const groups = buildPackageChoices([], [row]);
  for (const option of groups[0].options) {
    checked++;
    assert.equal(hasExplanation(option), Boolean(row.source_label?.ingredients), row.id);
    const display = toDisplaySourceLabel(row, option.label);
    if (!row.source_label) {
      assert.equal(display, null, `${row.id} must remain pending`);
      continue;
    }
    assert.equal(display.ingredientStatement, row.source_label.ingredients);
    assert.equal(display.package, option.label);
    assert.equal(display.source.url, row.source_label.source_url);
    assert.ok(display.scopeNote.includes("Manufacturer information"));
    assert.ok(display.assessment.context);
  }
}
const future = { id:"future", variant_name:"Future flavor", beverage_family_name:"Future", market:"US", observed_package_sizes:"20 fl oz", package_size_scope:"variant" };
assert.equal(hasExplanation(buildPackageChoices([], [future])[0].options[0]), false, "new unreviewed entries cannot become explanation choices");
const emptyPackage = { id: "empty-package", display_name: "Future flavor", market: "US", package_description: "20 fl oz", has_ingredients: 0 };
assert.equal(hasExplanation(buildPackageChoices([emptyPackage], [future])[0].options[0]), false, "package IDs alone do not establish ingredient availability");
assert.equal(hasExplanation(buildPackageChoices([{ ...emptyPackage, has_ingredients: 1 }], [future])[0].options[0]), true);
console.log(`${rows.length} drinks and ${checked} size choices passed the explanation availability check`);
