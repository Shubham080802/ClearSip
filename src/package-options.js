import { normalizeName } from "./catalog-api.js";

export function hasExplanation(option) {
  return Boolean((option?.packageId && option.ingredientsAvailable) || option?.localDrink || option?.discovery?.source_label?.ingredients);
}

// Only parse explicit net-size lists. Serving/prepared-volume notes must never
// become selectable packages (especially for concentrates).
export function parsePackageSizes(discovery) {
  if (discovery.package_size_scope !== "variant") return [];
  return (discovery.observed_package_sizes || "").split(";").flatMap((part) => {
    const match = part.trim().match(/^(\d+(?:\.\d+)?(?:\s*,\s*\d+(?:\.\d+)?)*)\s*(fl\s*oz|oz|ml|l)\b(?:\s+(bottle|can|carton))?(?:\s*\(\d+(?:\.\d+)?\s*ml\))?$/i);
    if (!match) return [];
    const unit = match[2].replace(/\s+/g, " ").toLowerCase();
    return match[1].split(",").map((number) => `${Number(number.trim())} ${unit === "l" ? "L" : unit === "ml" ? "mL" : unit}${match[3] ? ` ${match[3].toLowerCase()}` : ""}`);
  });
}

function sizeIdentity(size) {
  const match = size.match(/^(\d+(?:\.\d+)?)\s*(fl\s*oz|oz|ml|l)\b/i);
  if (!match) return normalizeName(size);
  const unit = match[2].replace(/\s+/g, "").toLowerCase();
  return unit === "l" ? `${Number(match[1]) * 1000}ml` : `${Number(match[1])}${unit}`;
}

export function buildPackageChoices(packages, discoveries) {
  const groups = new Map();
  const groupFor = (name, market) => {
    const key = `${normalizeName(name)}|${market}`;
    if (!groups.has(key)) groups.set(key, { name, market, options: [] });
    return groups.get(key);
  };
  for (const item of packages) {
    groupFor(item.display_name, item.market).options.push({
      label: item.package_description, packageId: item.id, ingredientsAvailable: Boolean(item.has_ingredients),
      labelVerified: item.label_verified === true || item.label_verified === 1,
      gtinLinked: Boolean(item.gtin),
    });
  }
  for (const discovery of discoveries) {
    const family = discovery.beverage_family_name || "";
    const familyWords = family.split(/\s+/);
    const variantWords = discovery.variant_name.split(/\s+/);
    let name = discovery.variant_name;
    if (family && !normalizeName(name).split(" ").includes(normalizeName(familyWords[0]))) {
      let overlap = Math.min(familyWords.length, variantWords.length);
      while (overlap && normalizeName(familyWords.slice(-overlap).join(" ")) !== normalizeName(variantWords.slice(0, overlap).join(" "))) overlap--;
      name = [...familyWords, ...variantWords.slice(overlap)].join(" ");
    }
    const group = groupFor(name, discovery.market);
    group.discovery = discovery;
    // Keep the manufacturer panel available on existing package options too.
    for (const option of group.options) option.discovery ||= discovery;
    const sizes = parsePackageSizes(discovery);
    for (const label of sizes) {
      if (!group.options.some((option) => sizeIdentity(option.label) === sizeIdentity(label))) {
        group.options.push({ label, discovery });
      }
    }
    if (!sizes.length && !group.options.length) {
      group.options.push({ label: "Size not confirmed — manufacturer information", discovery });
    }
  }
  return [...groups.values()].sort((a, b) => a.name.localeCompare(b.name));
}
