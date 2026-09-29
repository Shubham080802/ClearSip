import knowledge from "../data/ingredient-effects.json" with { type: "json" };

export const effectsVersion = knowledge.version;
const profiles = knowledge.profiles.map((row) => ({ ...row, matcher: new RegExp(row.pattern, "i"),
  exclusion: row.exclude_pattern ? new RegExp(row.exclude_pattern, "i") : null }));
const sourcesFor = (ids) => ids.map((id) => knowledge.sources[id]);

// Keep compound ingredients together. Commas inside parentheses are not new
// top-level ingredients, and the full original statement remains on screen.
export function parseDeclaredIngredients(statement) {
  const input = statement.replace(/\.\s*Contains\s+(?:less than\s+)?\d+(?:\.\d+)?%\s*(?:or less)?\s*of\s*:/gi, ", ");
  let depth = 0, start = 0;
  const rows = [];
  for (let index = 0; index < input.length; index++) {
    if (input[index] === "(") depth++;
    if (input[index] === ")") depth = Math.max(0, depth - 1);
    if ((input[index] === "," || input[index] === ";") && depth === 0) {
      rows.push(input.slice(start, index));
      start = index + 1;
    }
  }
  rows.push(input.slice(start));
  return rows.flatMap((row) => {
    const name = row.trim().replace(/^(?:contains\s+)?(?:(?:less than|up to)\s+\d+(?:\.\d+)?%|\d+%\s+or less)\s*(?:of)?\s*:?\s*/i, "")
      .split(/\.\s*\*/)[0].replace(/\.$/, "").trim();
    const waterAndFlavor = name.match(/^((?:purified|filtered)?\s*water)\s+and\s+(natural flavors?)$/i);
    return waterAndFlavor ? waterAndFlavor.slice(1).map((part) => part.trim()) : name ? [name] : [];
  });
}

export function explainIngredients(statement, declaredNames = []) {
  const names = statement ? parseDeclaredIngredients(statement) : declaredNames;
  return names.map((name) => {
    const matches = profiles.filter((profile) => profile.matcher.test(name) && !profile.exclusion?.test(name));
    return { name, role: matches.map((profile) => profile.role).join(" · ") || "Declared component",
      status: matches.length ? (matches.some((profile) => profile.evidence_level === "limited") ? "limited" : "general") : "unreviewed",
      effects: matches.map((profile) => ({ id: profile.id, role: profile.role,
        function: profile.function,
        bodyEffect: profile.body_effect, intakeContext: profile.intake_context,
        disclosure: profile.disclosure || "", sources: sourcesFor(profile.source_ids) })),
      note: matches.length ? "General ingredient evidence, not a measured effect of this exact drink." :
        "A specific bodily-effect profile has not been reviewed for this component. It remains visible rather than being omitted." };
  });
}

function quantityNote(card, drink) {
  const ids = new Set(card.effects.map((effect) => effect.id));
  const nutrients = drink.nutrients || {};
  const serving = drink.serving || "listed serving";
  const value = (key) => number(nutrients[key]);
  if (["caffeine", "coffee-tea", "guarana"].some((id) => ids.has(id)) && value("caffeine_mg") !== null)
    return `Drink total: ${value("caffeine_mg")} mg caffeine per ${serving}. This does not separate contributions from individual caffeine sources.`;
  if ((ids.has("sugar") || ids.has("juice")) && value("total_sugar_g") !== null)
    return `Drink total: ${value("total_sugar_g")} g total sugar${value("added_sugar_g") !== null ? `, including ${value("added_sugar_g")} g added sugar` : ""} per ${serving}. The amount of this individual ingredient is not given.`;
  if (ids.has("sodium") && value("sodium_mg") !== null)
    return `Drink total: ${value("sodium_mg")} mg sodium per ${serving}, from all sodium-containing ingredients combined.`;
  return "The amount of this individual component is not provided in this record; no dose or safe-can allowance is inferred.";
}

function number(value) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : null;
}

export function drinkingContexts(drink, cards = []) {
  const nutrients = drink.nutrients || {};
  const sugar = number(nutrients.total_sugar_g), added = number(nutrients.added_sugar_g);
  const calories = number(nutrients.calories), caffeine = number(nutrients.caffeine_mg);
  const source = knowledge.sources;
  const ids = new Set(cards.flatMap((card) => card.effects.map((effect) => effect.id)));
  const contexts = [{ id: "sugar-goal", label: "Low-sugar goals", status: sugar === null ? "unknown" : sugar === 0 ? "context" : "watch",
    title: sugar === null ? "Sugar amount not confirmed" : sugar === 0 ? "0 g total sugar is disclosed" : `${sugar} g total sugar to account for`,
    reason: sugar === null ? "The available source does not state total sugar, so a low-sugar fit cannot be determined." :
      `The source lists ${sugar} g per serving. ${sugar === 0 ? "This may fit a goal of avoiding sugar in drinks, but it is not a diabetes, insulin-response, or weight-loss guarantee." : "Naturally occurring sugar still counts toward total sugar; use your own dietary plan rather than the drink's marketing name."}`,
    basis: "Uses the source's total sugar per serving; no total-sugar Daily Value is assumed.", sources: [source.sugar] }];
  contexts.push({ id: "occasional", label: "Casual / occasional use", status: added === null ? "unknown" : added >= 10 ? "watch" : "context",
    title: added === null ? "Added-sugar comparison unavailable" : added >= 10 ? "High added sugar: consider an occasional drink" : added <= 2.5 ? "Low disclosed added sugar" : "Added sugar to budget",
    reason: added === null ? "Added sugar is not disclosed here. A sugar-source ingredient does not reveal its amount." :
      `${added} g added sugar per serving is ${Math.round(added / 50 * 100)}% of the 50 g labeling Daily Value. ${added >= 10 ? "Frequent sugary-drink intake is associated with weight gain, type 2 diabetes and tooth decay; this is not a prediction that one drink causes disease." : "This describes added sugar only; it does not make unlimited intake appropriate."}`,
    basis: "FDA label comparison: ≤5% DV is low; ≥20% DV is high. The DV is not your personal intake target.", sources: [source.sugar, source.sugaryDrinks] });
  contexts.push({ id: "calories", label: "Calorie budget", status: calories === null ? "unknown" : "context",
    title: calories === null ? "Calories not disclosed" : `${calories} calories per listed serving`,
    reason: "A weight-management fit depends on your overall intake and needs, not on a healthy/unhealthy badge. The selected bottle size is not used to invent a whole-container total.",
    basis: "Uses disclosed calories only. No keto, fasting, or weight-loss certification.", sources: [source.label] });
  const caffeineIngredient = ids.has("caffeine") || ids.has("coffee-tea") || ids.has("guarana");
  contexts.push({ id: "caffeine", label: "Caffeine awareness", status: caffeine === null ? "unknown" : caffeine > 0 ? "watch" : "context",
    title: caffeine === null ? caffeineIngredient ? "Caffeine source; amount not disclosed" : "Caffeine amount not confirmed" : `${caffeine} mg caffeine per listed serving`,
    reason: caffeine === null ? `${caffeineIngredient ? "Coffee, tea, guarana or caffeine is declared, but no exact dose is available." : "Absence of a caffeine amount is not a verified caffeine-free claim."} Decaf does not necessarily mean zero caffeine.` :
      caffeine === 0 ? "The source declares 0 mg. Compare it with the package in your hand; other cautions still apply." :
        "Caffeine may increase alertness, but can disrupt sleep or cause jitters and a faster heartbeat. Count caffeine from other drinks too.",
    basis: "FDA's 400 mg/day context applies to most adults, not everyone and not a recommended target. Pregnancy, medications and sensitivity require individual advice.", sources: [source.caffeine] });
  const plainWater = cards.length > 0 && cards.every((card) => card.effects.length > 0 &&
    card.effects.every((effect) => ["water", "carbonation"].includes(effect.id)));
  contexts.push({ id:"hydration", label:"Frequent sipping / hydration", status:"context",
    title:plainWater ? "Plain-water ingredient pattern" : "Water is the default hydration alternative",
    reason:plainWater ? "The declared ingredients are water/carbonation only. Water contributes to hydration; carbonation may cause gas in some people. This is not a purity test or a personal unlimited-intake recommendation." :
      "Water supports hydration without the sugar of sweetened drinks. This drink's extra ingredients should be considered separately rather than treating its water base as an all-day drinking recommendation.",
    basis:"The positive plain-water context requires only water/carbonation declarations. Flavoring, coffee, sweeteners or unreviewed components do not qualify.", sources:[source.water] });
  const sodium = number(nutrients.sodium_mg);
  if ((sodium !== null && sodium > 0) || ids.has("sodium")) contexts.push({ id:"sodium", label:"Sodium budget", status:sodium === null ? "unknown" : sodium >= 460 ? "watch" : "context",
    title:sodium === null ? "Sodium amount not disclosed" : `${sodium} mg sodium per listed serving`,
    reason:sodium === null ? "Sodium-containing salts are declared, but the available record does not quantify total sodium." :
      `${Math.round(sodium / 2300 * 100)}% of the 2,300 mg labeling DV. ${sodium >= 460 ? "This is high under FDA's ≥20% DV comparison." : "Consider sodium from the rest of your diet too."}`,
    basis:"Label comparison, not a personal restriction or permission. Kidney/heart conditions and your care plan can change appropriate intake.", sources:[source.sodium] });
  if (ids.has("aspartame")) contexts.push({ id:"pku", label:"Specific caution", status:"watch", title:"Aspartame / PKU notice",
    reason:"Aspartame provides phenylalanine. People with phenylketonuria (PKU) should avoid or restrict it according to their care plan; check the package notice.",
    basis:"Triggered by declared aspartame, not by a general diet badge.", sources:[source.sweeteners] });
  if (ids.has("milk") || ids.has("soy")) contexts.push({ id:"allergens", label:"Specific caution", status:"watch", title:"Declared milk / soy ingredient",
    reason:`${[ids.has("milk") ? "Milk" : null, ids.has("soy") ? "Soy" : null].filter(Boolean).join(" and ")} is declared. Avoid a drink containing your allergen. Lactase treatment does not remove milk proteins. This is not a complete allergen or cross-contact check.`,
    basis:"Ingredient match only. Always inspect the full label and facility statements.", sources:[source.allergens] });
  if (ids.has("acids")) contexts.push({ id:"dental", label:"Frequent-sipping caution", status:"watch", title:"Acids are declared, including in sugar-free drinks",
    reason:"Frequent acidic-drink exposure can erode tooth enamel. Do not hold or swish it in your mouth; water is the default alternative for frequent sipping.",
    basis:"Acid names do not reveal measured pH or quantify this drink's erosion risk.", sources:[source.dental] });
  return contexts;
}

export function buildIngredientContext(drink) {
  const cards = explainIngredients(drink.ingredientStatement || "",
    (drink.ingredients || []).filter((row) => row.role !== "Required label notice").map((row) => row.name));
  cards.forEach((card) => { card.quantityNote = quantityNote(card, drink); });
  return { version: effectsVersion, cards, contexts: drinkingContexts(drink, cards) };
}
