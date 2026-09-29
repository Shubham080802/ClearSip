import assert from "node:assert/strict";
import knowledge from "../data/ingredient-effects.json" with { type:"json" };
import { parseDeclaredIngredients, explainIngredients, buildIngredientContext, drinkingContexts } from "../src/ingredient-context.js";
import { renderIngredientContext, bindResultTabs } from "../src/result-context.js";
import { toDisplaySourceLabel } from "../src/catalog-api.js";

assert.equal(knowledge.schema_version, 1);
assert.equal(new Set(knowledge.profiles.map((row) => row.id)).size, knowledge.profiles.length);
for (const row of knowledge.profiles) {
  assert.ok(row.function && row.body_effect && row.intake_context && row.source_ids.length);
  for (const id of row.source_ids) assert.ok(knowledge.sources[id]?.url.startsWith("https://"), `${row.id}: missing source ${id}`);
}
assert.deepEqual(parseDeclaredIngredients("Coffee (Water, Coffee), Cane Sugar, Natural Flavor."), ["Coffee (Water, Coffee)","Cane Sugar","Natural Flavor"]);
assert.deepEqual(parseDeclaredIngredients("Oat base (water, oats). Contains 2% or less of: sea salt, vitamin B12."), ["Oat base (water, oats)","sea salt","vitamin B12"]);
assert.deepEqual(parseDeclaredIngredients("WATER, LESS THAN 0.5% OF: CITRIC ACID, ELECTROLYTES (SALT, SODIUM CITRATE), NATURAL FLAVORS"), ["WATER","CITRIC ACID","ELECTROLYTES (SALT, SODIUM CITRATE)","NATURAL FLAVORS"]);
assert.deepEqual(parseDeclaredIngredients("Purified water and natural flavors."), ["Purified water","natural flavors"]);
const getIds = (text) => explainIngredients(text).flatMap((row) => row.effects.map((effect) => effect.id));
assert.ok(getIds("Sucralose").includes("intense-sweeteners"));
assert.ok(!getIds("Sucralose").includes("sugar"));
assert.ok(getIds("Allulose Syrup").includes("allulose"));
assert.ok(!getIds("Allulose Syrup").includes("sugar"));
assert.ok(!getIds("Sucrose acetate isobutyrate").includes("sugar"));
assert.ok(!getIds("Acesulfame potassium").includes("potassium"));
assert.ok(!getIds("Potassium benzoate").includes("potassium"));
assert.ok(!getIds("Calcium disodium EDTA").includes("sodium"));
assert.ok(!getIds("Calcium disodium EDTA").includes("calcium"));
assert.ok(!getIds("Nitrous Oxide").includes("carbonation"));
assert.ok(!getIds("Gellan Gum").includes("fiber"));
assert.ok(getIds("Calcium Lactate Gluconate").includes("calcium"));
assert.ok(getIds("Oatmilk (Water, Oats)").includes("oats"));
assert.ok(!getIds("Oatmilk (Water, Oats)").includes("milk"));
assert.ok(!getIds("Citric Acid").includes("vitamin-c"));
assert.ok(getIds("VITAMINS B12 AND C (CYANOCOBALAMIN AND ASCORBIC ACID)").includes("vitamin-b12"));
assert.ok(getIds("VITAMINS B12 AND C (CYANOCOBALAMIN AND ASCORBIC ACID)").includes("vitamin-c"));
const flavors = explainIngredients("Natural and artificial flavors")[0];
assert.match(flavors.effects[0].function, /taste and aroma/);
assert.match(flavors.effects[0].disclosure, /not disclosed/);
assert.equal(explainIngredients("Unresearched extract")[0].status, "unreviewed");

const drink = { name:"Cola", serving:"12 fl oz", ingredientStatement:"Carbonated Water, Aspartame, Phosphoric Acid, Natural Flavors, Caffeine", nutrients:{total_sugar_g:0,added_sugar_g:0,calories:0,caffeine_mg:34,sodium_mg:40} };
const context = buildIngredientContext(drink);
assert.match(context.cards.find((row) => row.name === "Caffeine").quantityNote, /34 mg.*12 fl oz/);
assert.ok(context.contexts.some((row) => row.id === "pku"));
assert.ok(context.contexts.some((row) => row.id === "dental"));
assert.ok(context.contexts.some((row) => row.id === "sugar-goal" && row.title.includes("0 g")));
assert.ok(context.contexts.some((row) => row.id === "hydration" && !row.title.includes("Plain-water")));
const unknown = drinkingContexts({nutrients:{}});
assert.equal(unknown.find((row) => row.id === "sugar-goal").status, "unknown");
assert.equal(unknown.find((row) => row.id === "occasional").status, "unknown");
assert.equal(drinkingContexts({nutrients:{added_sugar_g:10}}).find((row) => row.id === "occasional").status,"watch");
assert.match(drinkingContexts({nutrients:{added_sugar_g:2.5}}).find((row) => row.id === "occasional").title,/Low disclosed/);
assert.ok(buildIngredientContext({ingredientStatement:"Decaffeinated Coffee (Water, Decaffeinated Coffee)"}).contexts.find((row) => row.id === "caffeine").title.includes("amount not disclosed"));
assert.ok(!buildIngredientContext({ingredientStatement:"Oatmilk (Water, Oats), Lactase"}).contexts.some((row) => row.id === "allergens"));
assert.ok(buildIngredientContext({ingredientStatement:"Whole Milk, Lactase"}).contexts.some((row) => row.id === "allergens"));
assert.match(buildIngredientContext({ingredientStatement:"Purified Water"}).contexts.find((row) => row.id === "hydration").title,/Plain-water/);
const sourceDisplay = toDisplaySourceLabel({id:"test",market:"US",source_label:{name:"Test", ingredients:"Water, Sugar", calories:100,total_sugar_g:25,added_sugar_g:25,serving:"8 fl oz",publisher:"Manufacturer",source_url:"https://example.com",accessed_on:"2026-09-28"}}, "28 fl oz");
assert.equal(sourceDisplay.nutrients.total_sugar_g,25);
assert.match(buildIngredientContext(sourceDisplay).contexts[0].reason,/25 g per serving/);
assert.equal(sourceDisplay.serving,"8 fl oz");

const html = renderIngredientContext({...drink,ingredientStatement:'<script>alert(1)</script>, Caffeine'});
assert.ok(!html.includes("<script>"));
assert.ok(html.includes("&lt;script&gt;"));
assert.ok(html.includes('role="tablist"'));
assert.ok(html.includes('id="drinking-context-panel"'));
assert.ok(html.includes("No “safe for every diet”"));
const panels = {"#ingredients-panel":{hidden:false},"#drinking-context-panel":{hidden:true}};
const tabs = ["ingredients-panel","drinking-context-panel"].map((panel) => ({
  attributes:{"aria-controls":panel}, listeners:{}, tabIndex:0,
  setAttribute(key,value){this.attributes[key]=value;}, getAttribute(key){return this.attributes[key];},
  addEventListener(event,callback){this.listeners[event]=callback;}, focus(){this.focused=true;}
}));
bindResultTabs({querySelectorAll(){return tabs;},querySelector(selector){return panels[selector];}});
tabs[1].listeners.click();
assert.equal(tabs[1].attributes["aria-selected"],"true");
assert.equal(tabs[0].tabIndex,-1);
assert.equal(panels["#ingredients-panel"].hidden,true);
assert.equal(panels["#drinking-context-panel"].hidden,false);
tabs[1].listeners.keydown({key:"ArrowRight",preventDefault(){}});
assert.equal(tabs[0].attributes["aria-selected"],"true");
assert.equal(tabs[0].focused,true);
tabs[0].listeners.keydown({key:"End",preventDefault(){}});
assert.equal(tabs[1].attributes["aria-selected"],"true");
console.log(`${knowledge.profiles.length} evidence profiles: identity, diet-context limits, rendering, and keyboard tabs passed`);
