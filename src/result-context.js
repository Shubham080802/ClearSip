import { buildIngredientContext } from "./ingredient-context.js";

const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (character) =>
  ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" })[character]);
function url(value) {
  try { const parsed = new URL(value); return parsed.protocol === "https:" ? parsed.href : "#"; }
  catch { return "#"; }
}
function links(sources) {
  return [...new Map(sources.map((source) => [source.url, source])).values()].map((source) =>
    `<a href="${escape(url(source.url))}" target="_blank" rel="noreferrer">${escape(source.title)} ↗</a>`).join("");
}

export function renderIngredientContext(drink) {
  const { cards, contexts, version } = buildIngredientContext(drink);
  const labels = { general:"General evidence", limited:"Evidence / disclosure limits", unreviewed:"Review pending" };
  const ingredients = cards.map((card) => `<article class="body-ingredient ${card.status}">
    <div class="body-ingredient-heading"><p class="ingredient-role">${escape(card.role)}</p><span>${labels[card.status]}</span></div>
    <h3>${escape(card.name)}</h3>
    ${card.effects.map((effect) => `<div class="effect-note"><p><strong>In the drink</strong>${escape(effect.function)}</p><p><strong>In your body</strong>${escape(effect.bodyEffect)}</p></div>`).join("") || `<p class="profile-pending">${escape(card.note)}</p>`}
    ${card.effects.length ? `<details class="effect-evidence"><summary>Amount, cautions & sources</summary><p class="disclosure-note">${escape(card.quantityNote)}</p>${card.effects.map((effect) => `<p>${escape(effect.intakeContext)}</p>${effect.disclosure ? `<p class="disclosure-note">${escape(effect.disclosure)}</p>` : ""}`).join("")}<div class="effect-sources">${links(card.effects.flatMap((effect) => effect.sources))}</div><p class="effect-scope">${escape(card.note)}</p></details>` : ""}
  </article>`).join("");
  const contextCards = contexts.map((item) => `<article class="drinking-card ${item.status}"><p class="ingredient-role">${escape(item.label)}</p><h3>${escape(item.title)}</h3><p>${escape(item.reason)}</p><details class="effect-evidence"><summary>Why this context?</summary><p>${escape(item.basis)}</p><div class="effect-sources">${links(item.sources)}</div></details></article>`).join("");
  return `<div class="result-tablist" role="tablist" aria-label="Drink explanation">
    <button type="button" role="tab" id="ingredients-tab" aria-controls="ingredients-panel" aria-selected="true" tabindex="0">Ingredients & body effects <span>${cards.length}</span></button>
    <button type="button" role="tab" id="drinking-context-tab" aria-controls="drinking-context-panel" aria-selected="false" tabindex="-1">Drinking context <span>Diet goals & cautions</span></button>
  </div>
  <section id="ingredients-panel" role="tabpanel" aria-labelledby="ingredients-tab" tabindex="0">
    <div class="context-section-heading"><div><p class="eyebrow">DECLARED COMPONENTS, EXPLAINED</p><h2>What these ingredients do</h2></div><p>Each name comes from the available ingredient statement. We separate its job in the drink from general bodily effects. These are not measurements of what this exact drink does to you.</p></div>
    <div class="body-ingredient-grid">${ingredients || "<p>No declared ingredient statement is available to explain.</p>"}</div>
    <p class="context-version">Evidence dataset ${escape(version)} · Source-backed educational draft; clinical review pending. Expand a card for its sources and limitations.</p>
  </section>
  <section id="drinking-context-panel" role="tabpanel" aria-labelledby="drinking-context-tab" tabindex="0" hidden>
    <div class="context-section-heading"><div><p class="eyebrow">DIET GOALS, NOT A SAFETY SCORE</p><h2>Where this drink fits</h2></div><p>Based on the source's listed serving: <strong>${escape(drink.serving)}</strong>. These contexts can coexist. A low-sugar label does not cancel caffeine, allergy or dental cautions.</p></div>
    <div class="context-boundary">No “safe for every diet” or unlimited-intake verdict. Your overall intake, allergies, medicines, pregnancy and medical conditions can change what is appropriate.</div>
    <div class="drinking-grid">${contextCards}</div>
    <p class="context-version">Unknown amounts remain unassessed. Nutrition from a variant source is not silently scaled to your selected bottle size.</p>
  </section>`;
}

export function bindResultTabs(container) {
  const tabs = [...container.querySelectorAll('[role="tab"]')];
  function activate(tab, focus = false) {
    for (const item of tabs) {
      const selected = item === tab;
      item.setAttribute("aria-selected", String(selected));
      item.tabIndex = selected ? 0 : -1;
      container.querySelector(`#${item.getAttribute("aria-controls")}`).hidden = !selected;
    }
    if (focus) tab.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => activate(tab));
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); activate(tabs[next], true); }
    });
  });
}
