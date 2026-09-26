const configuredApiBase = import.meta.env?.VITE_API_BASE_URL;
const API_BASE = (configuredApiBase || "/api").replace(/\/$/, "");

const evidenceStatus = {
  worth_watching: "watch",
  context_matters: "context",
  label_context: "neutral",
  not_fully_specified: "unknown",
};

export function normalizeName(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function displayValue(value, unit = "") {
  return value === null || value === undefined ? null : `${value}${unit}`;
}

function claimTitle(context) {
  switch (context?.sugar_free_claim_status) {
    case "appears_label_aligned":
      return "The visible sugar claim appears aligned with the disclosed label facts.";
    case "needs_review":
      return "The visible sugar claim needs package-level review.";
    case "appears_inconsistent":
      return "The visible sugar claim needs urgent package-level review.";
    case "not_assessable":
      return "There is not enough disclosed label data to assess the visible claim.";
    default:
      return "This result summarizes the disclosed package label facts.";
  }
}

export function toDisplayProduct(product) {
  const context = product.label_context || {};
  const facts = [
    ["Calories", displayValue(product.calories)],
    ["Total sugar", displayValue(product.total_sugar_g, " g")],
    ["Added sugar", displayValue(product.added_sugar_g, " g")],
    ["Saturated fat", displayValue(product.saturated_fat_g, " g")],
    ["Sodium", displayValue(product.sodium_mg, " mg")],
    ["Caffeine", displayValue(product.caffeine_mg, " mg")],
  ].filter(([, value]) => value !== null).map(([label, value]) => ({ label, value }));

  return {
    id: product.id,
    name: product.name,
    region: product.market || "Market not specified",
    serving: product.serving || product.package || "Package size not specified",
    facts,
    assessment: {
      title: claimTitle(context),
      context: context.frequent_intake_context || context.summary || "No assessment is available for this label version.",
    },
    source: {
      title: product.source?.publisher || "Package-label source",
      url: product.source?.url || "#",
      note: `${product.verification_status?.replaceAll("_", " ") || "source status not specified"} · label observed ${product.label_observed_on || "date not specified"}.`,
    },
    ingredients: (product.ingredients || []).map((ingredient) => ({
      name: ingredient.name,
      role: ingredient.role || ingredient.functional_class || "Declared ingredient",
      context: ingredient.assessment || ingredient.plain_language_summary || "Declared on the available label.",
      status: evidenceStatus[ingredient.evidence_status] || "unknown",
      evidence: ingredient.source_url ? { url: ingredient.source_url } : null,
    })),
    dataVersion: product.label_observed_on || "current label",
  };
}

function selectPackage(matches, query) {
  const normalizedQuery = normalizeName(query);
  return matches.find((match) => normalizeName(match.display_name) === normalizedQuery)
    || matches.find((match) => normalizeName(match.display_name).includes(normalizedQuery))
    || matches[0]
    || null;
}

async function fetchJson(path, fetchFn) {
  const response = await fetchFn(`${API_BASE}${path}`, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`Catalog request failed with ${response.status}`);
  return response.json();
}

export function getCatalogSummary(fetchFn = fetch) {
  return fetchJson("/catalog-summary", fetchFn);
}

export async function findCatalogProduct(query, fetchFn = fetch) {
  const trimmed = query.trim().slice(0, 120);
  if (normalizeName(trimmed).length < 2) return null;
  const matches = await fetchJson(`/products?query=${encodeURIComponent(trimmed)}`, fetchFn);
  const selected = selectPackage(matches, trimmed);
  if (!selected) return null;
  return toDisplayProduct(await fetchJson(`/products/${encodeURIComponent(selected.id)}`, fetchFn));
}
