const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (character) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);

export function displayPackageEvidence(product) {
  const record = product.package_evidence || {};
  const verified = record.label_verified === true && record.label_scope === "package";
  return {
    scope: verified ? "package" : "variant",
    gtinLinked: Boolean(product.gtin && record.gtin_linked),
    labelVersionId: record.label_version_id || "",
    observedOn: product.label_observed_on || "",
    sourceType: record.source_type || "",
  };
}

export function renderPackageEvidence(drink, matchedFrom = "") {
  const evidence = drink.packageEvidence || { scope:"variant", gtinLinked:false };
  const verified = evidence.scope === "package";
  const barcodeMatch = /barcode/i.test(matchedFrom) && evidence.gtinLinked;
  const identity = barcodeMatch ? "Barcode matched this stored package record" :
    evidence.gtinLinked ? "A GTIN is linked to this package record; this selection was not a barcode scan" :
    "Selected by name and size; no GTIN is linked to this record";
  const reviewedScope = evidence.sourceType === "manufacturer_label" ?
    "The manufacturer's GTIN-specific online label was reviewed for this size. No physical bottle was inspected; compare it with the container in your hand because packaging and formulas can change." :
    "A dated label version is attached to this specific package record. Compare it with the container in your hand because packaging and formulas can change.";
  return `<section class="package-evidence ${verified ? "package-verified" : "package-unverified"}" aria-label="Package evidence">
    <p class="eyebrow">PACKAGE EVIDENCE</p>
    <h3>${verified ? "Exact package label reviewed" : "Exact package label not yet verified"}</h3>
    <p>${verified ? reviewedScope :
      "The ingredient and nutrition information comes from a manufacturer variant or other unconfirmed label record. Selecting a size does not prove it matches that bottle or can."}</p>
    <dl><div><dt>Package identity</dt><dd>${escape(identity)}</dd></div>
      <div><dt>Label evidence</dt><dd>${verified ? "Reviewed package label" : "Variant-level or package-unconfirmed information"}${evidence.observedOn ? ` · source label dated ${escape(evidence.observedOn)}` : ""}</dd></div></dl>
  </section>`;
}
