import assert from "node:assert/strict";
import { findCatalogProduct, normalizeName, toDisplayProduct } from "../src/catalog-api.js";

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
  const response = url.includes("/products?")
    ? [{ id: "cola-12", display_name: "Cola Zero" }]
    : product;
  return { ok: true, status: 200, json: async () => response };
};

const display = await findCatalogProduct("Cola Zero", fetchFn);
assert.equal(display.name, "Cola Zero");
assert.equal(display.ingredients[0].status, "watch");
assert.equal(display.assessment.title, "The visible sugar claim appears aligned with the disclosed label facts.");
assert.equal(calls.length, 2);
assert.equal(toDisplayProduct(product).facts.length, 6);

console.log("catalog API adapter tests passed");
