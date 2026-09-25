export const dataVersion = "2026.09.24-us-seed";

const source = (title, url, note) => ({ title, url, note });

export const drinks = [
  {
    id: "coca-cola-zero-sugar",
    name: "Coca-Cola Zero Sugar",
    aliases: ["coke zero", "coca cola zero", "coke zero sugar", "diet coke zero"],
    region: "United States",
    verifiedOn: "2026-09-24",
    serving: "12 fl oz (355 mL)",
    facts: [{ label: "Calories", value: "0" }, { label: "Added sugar", value: "0 g" }, { label: "Caffeine", value: "34 mg" }],
    formulationNote: "US product formulation. Ingredient lists and caffeine can vary by country, package size, and time; compare the package in your hand.",
    source: source("Coca-Cola Zero Sugar product page", "https://www.coca-cola.com/us/en/brands/coca-cola/products/zero", "Manufacturer product page; checked September 2026."),
    ingredients: [
      { name: "Carbonated water", role: "Base", context: "Water with dissolved carbon dioxide. It contributes carbonation; it is not a sweetener.", status: "neutral" },
      { name: "Caramel color", role: "Color", context: "Adds the familiar cola color. FDA regulates color additives used in foods and drinks.", status: "neutral" },
      { name: "Phosphoric acid", role: "Acidulant", context: "Provides tartness and helps preserve flavor. This ingredient alone does not determine a drink’s healthfulness.", status: "context" },
      { name: "Aspartame", role: "High-intensity sweetener", context: "Provides sweetness with little or no energy. FDA lists an acceptable daily intake (ADI) of 50 mg per kg of body weight per day; the ADI is not a recommended target.", status: "context", evidence: source("FDA: Aspartame and Other Sweeteners in Food", "https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food", "FDA safety and ADI information.") },
      { name: "Acesulfame potassium", role: "High-intensity sweetener", context: "Often blended with another sweetener to shape taste. FDA lists an ADI of 15 mg/kg/day; amount per can is not usually disclosed on labels.", status: "context", evidence: source("FDA: Aspartame and Other Sweeteners in Food", "https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food", "FDA safety and ADI information.") },
      { name: "Stevia extract", role: "High-intensity sweetener", context: "The label identifies stevia extract, but does not disclose the specific steviol glycoside or amount. Ingredient name alone does not establish a personalized health effect.", status: "context" },
      { name: "Potassium benzoate", role: "Preservative", context: "Used to help maintain freshness. It is a regulated food additive when used within approved conditions.", status: "neutral" },
      { name: "Natural flavors", role: "Flavor", context: "A broad label term rather than a single chemical. The label does not provide the individual flavor compounds.", status: "unknown" },
      { name: "Caffeine", role: "Stimulant", context: "34 mg per listed 12 fl oz serving. FDA says up to 400 mg/day is not generally associated with dangerous, negative effects for most healthy adults—but pregnancy, medications, sensitivity, and conditions can change what is appropriate.", status: "watch", evidence: source("FDA: Spilling the Beans: How Much Caffeine is Too Much?", "https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much", "FDA consumer caffeine guidance.") },
      { name: "Phenylalanine notice", role: "Required label notice", context: "The manufacturer label states “Phenylketonurics: Contains phenylalanine.” This is especially relevant for people with phenylketonuria (PKU); it is not a general-population danger label.", status: "watch" }
    ]
  },
  {
    id: "monster-zero-sugar",
    name: "Monster Energy Zero Sugar",
    aliases: ["monster zero", "monster zero sugar", "zero sugar monster", "monster energy zero"],
    region: "United States",
    verifiedOn: "2026-09-24",
    serving: "16 fl oz (473 mL) can",
    facts: [{ label: "Calories", value: "10" }, { label: "Added sugar", value: "0 g" }, { label: "Caffeine", value: "160 mg" }],
    formulationNote: "US product facts are manufacturer verified. The full ingredient panel in this seed record is a provisional package transcription, so compare your can’s Nutrition Facts and ingredient statement.",
    source: source("Monster Energy Zero Sugar product page", "https://www.monsterenergy.com/en-us/energy-drinks/monster-energy/zero-sugar/", "Manufacturer product page; checked September 2026."),
    ingredients: [
      { name: "Carbonated water", role: "Base", context: "Water with dissolved carbon dioxide. It contributes carbonation; it is not a sweetener.", status: "neutral" },
      { name: "Citric acid", role: "Acidulant", context: "Adds tartness and helps stabilize flavor. It is widely used in beverages.", status: "neutral" },
      { name: "Erythritol", role: "Sugar alcohol sweetener", context: "The provisional package transcription lists 2 g per 16 fl oz. Presence of a sweetener does not by itself show that a product will have a particular effect for every person.", status: "context" },
      { name: "Taurine", role: "Amino-sulfonic compound", context: "Common in energy drinks. More research is needed to characterize effects of combinations in energy drinks; it should not be treated as a substitute for sleep or nutrition.", status: "context" },
      { name: "Caffeine", role: "Stimulant", context: "160 mg per listed 16 fl oz can. That is 40% of FDA’s 400 mg/day reference for most healthy adults. It may be inappropriate for children, people who are pregnant, or people sensitive to caffeine.", status: "watch", evidence: source("FDA: Spilling the Beans: How Much Caffeine is Too Much?", "https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much", "FDA consumer caffeine guidance.") },
      { name: "Sucralose", role: "High-intensity sweetener", context: "Provides sweetness with little or no energy. FDA lists an ADI of 5 mg/kg/day; the ADI is a safety benchmark, not a recommended intake goal.", status: "context", evidence: source("FDA: Aspartame and Other Sweeteners in Food", "https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food", "FDA safety and ADI information.") },
      { name: "Acesulfame potassium", role: "High-intensity sweetener", context: "Often used with sucralose. FDA lists an ADI of 15 mg/kg/day; exact amount per can is not usually on the label.", status: "context", evidence: source("FDA: Aspartame and Other Sweeteners in Food", "https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food", "FDA safety and ADI information.") },
      { name: "Panax ginseng / guarana extracts", role: "Botanical ingredients", context: "These ingredients are part of the beverage’s energy-drink blend. Guarana can naturally contain caffeine, so total stimulant exposure matters more than a single ingredient name.", status: "context" },
      { name: "B vitamins", role: "Vitamin additives", context: "Support normal metabolic functions when needed, but they do not neutralize sleep loss or make an energy drink inherently health-promoting.", status: "neutral" },
      { name: "Sorbic and benzoic acids", role: "Preservatives", context: "Help maintain shelf stability. They are regulated food additives when used within approved conditions.", status: "neutral" }
    ]
  }
];

export function findDrink(query) {
  const normal = query.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  if (!normal) return null;
  return drinks.find((drink) => [drink.name.toLowerCase(), ...drink.aliases].some((alias) => normal.includes(alias) || alias.includes(normal))) ?? null;
}
