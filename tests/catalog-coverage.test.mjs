import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { buildPackageChoices, hasExplanation } from "../src/package-options.js";
import { toDisplaySourceLabel, toDisplayProduct } from "../src/catalog-api.js";
import { buildIngredientContext, parseDeclaredIngredients } from "../src/ingredient-context.js";
import { renderIngredientContext } from "../src/result-context.js";
import { renderPackageEvidence } from "../src/package-evidence.js";

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
    const effects = buildIngredientContext(display);
    assert.deepEqual(effects.cards.map((card) => card.name), parseDeclaredIngredients(row.source_label.ingredients), `${row.id}: every declared component stays reachable`);
    assert.ok(effects.cards.length);
    assert.ok(effects.contexts.some((context) => context.id === "sugar-goal"));
    const html = renderIngredientContext(display);
    assert.ok(html.includes("What these ingredients do"));
    assert.ok(html.includes("Drinking context"));
    assert.equal(display.nutrients.total_sugar_g, row.source_label.total_sugar_g ?? null);
  }
}
const coolBlue = rows.find((row) => row.id === "gatorade-cool-blue");
assert.ok(coolBlue?.source_label);
const reviewed = JSON.parse(execFileSync(python, ["-c",
  "import json; from api.index import search_products, product_by_gtin; print(json.dumps({'choices':search_products('Gatorade Cool Blue'),'detail':product_by_gtin('00052000324815')}))"], { encoding:"utf8" }));
const coolBlueChoices = buildPackageChoices(reviewed.choices, [coolBlue])[0].options;
assert.equal(coolBlueChoices.filter((option) => option.labelVerified).length, 1);
assert.equal(coolBlueChoices.find((option) => option.labelVerified)?.packageId, "gatorade-cool-blue-20oz-us");
assert.equal(coolBlueChoices.filter((option) => !option.labelVerified).length, 3,
  "other sizes retain variant-only ingredient evidence");
const exactDisplay = toDisplayProduct(reviewed.detail);
assert.equal(exactDisplay.packageEvidence.scope, "package");
assert.equal(exactDisplay.nutrients.added_sugar_g, 35);
assert.equal(exactDisplay.ingredientStatement, reviewed.detail.ingredient_statement);
assert.match(renderPackageEvidence(exactDisplay, "catalog barcode from image"), /No physical bottle was inspected/);
const future = { id:"future", variant_name:"Future flavor", beverage_family_name:"Future", market:"US", observed_package_sizes:"20 fl oz", package_size_scope:"variant" };
assert.equal(hasExplanation(buildPackageChoices([], [future])[0].options[0]), false, "new unreviewed entries cannot become explanation choices");
const emptyPackage = { id: "empty-package", display_name: "Future flavor", market: "US", package_description: "20 fl oz", has_ingredients: 0 };
assert.equal(hasExplanation(buildPackageChoices([emptyPackage], [future])[0].options[0]), false, "package IDs alone do not establish ingredient availability");
assert.equal(hasExplanation(buildPackageChoices([{ ...emptyPackage, has_ingredients: 1 }], [future])[0].options[0]), true);
console.log(`${rows.length} drinks and ${checked} size choices passed the explanation availability check`);
