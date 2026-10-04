import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

// Exercise the real handler with deferred API responses, without requiring a DOM runtime.
const source = readFileSync(new URL("../src/main.js", import.meta.url), "utf8");
const start = source.indexOf("async function handleQuery(");
const end = source.indexOf("\nasync function loadCatalogSummary", start);
assert.ok(start >= 0 && end > start);

let finishOld;
const oldResponse = new Promise((resolve) => { finishOld = resolve; });
const shown = [];
const classList = { add() {}, remove() {} };
const context = {
  selectionRevision: 0,
  recognitionCandidates: { classList }, packagePicker: { classList },
  result: { classList }, emptyState: { classList, innerHTML: "" },
  scanStatus: { textContent: "" }, console,
  findCatalogProductByGtin: async () => null,
  findCatalogProduct: (name) => name === "old drink" ? oldResponse : Promise.resolve({ name: "new drink" }),
  findDrink: () => null, findCatalogDiscovery: async () => null,
  showResult: (drink) => shown.push(drink.name), showDiscoveryResult() {},
};
const handleQuery = runInNewContext(`${source.slice(start, end)}\nhandleQuery`, context);
const oldSearch = handleQuery("old drink");
await handleQuery("new drink");
finishOld({ name: "old drink" });
await oldSearch;
assert.deepEqual(shown, ["new drink"], "a slow earlier lookup must not replace the latest drink");

let finishBarcode;
context.findCatalogProductByGtin = () => new Promise((resolve) => { finishBarcode = resolve; });
const barcodeSearch = handleQuery("012345678905");
await handleQuery("new drink");
finishBarcode({ name: "old barcode" });
await barcodeSearch;
assert.deepEqual(shown, ["new drink", "new drink"], "a slow barcode response must not replace a later search");

context.findCatalogProductByGtin = async () => null;
context.findCatalogProduct = (name) => Promise.resolve(name === "old discovery" ? null : { name: "new drink" });
let finishDiscovery, enteredDiscovery;
const discoveryStarted = new Promise((resolve) => { enteredDiscovery = resolve; });
context.findCatalogDiscovery = () => {
  enteredDiscovery();
  return new Promise((resolve) => { finishDiscovery = resolve; });
};
const discoverySearch = handleQuery("old discovery");
await discoveryStarted;
await handleQuery("new drink");
finishDiscovery({ variant_name: "old discovery" });
await discoverySearch;
assert.deepEqual(shown, ["new drink", "new drink", "new drink"], "a slow discovery response must not replace a later search");
console.log("Out-of-order direct query test passed");
