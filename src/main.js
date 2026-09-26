import { createWorker } from "tesseract.js";
import { dataVersion, findDrink } from "./data.js";
import { findCatalogProduct, getCatalogSummary } from "./catalog-api.js";
import { validateScanFile } from "./scan-guardrails.js";
import "./style.css";

const form = document.querySelector("#search-form");
const query = document.querySelector("#drink-query");
const imageInput = document.querySelector("#image-input");
const videoInput = document.querySelector("#video-input");
const voiceButton = document.querySelector("#voice-button");
const scanStatus = document.querySelector("#scan-status");
const result = document.querySelector("#result");
const emptyState = document.querySelector("#empty-state");
const reviewedCount = document.querySelector("#catalog-reviewed-count");
const discoveryCount = document.querySelector("#catalog-discovery-count");

const statusLabels = { watch: "Worth watching", context: "Context matters", neutral: "Label context", unknown: "Not fully specified" };

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
}

function showResult(drink, matchedFrom = "typed search") {
  emptyState.classList.add("hidden");
  result.classList.remove("hidden");
  const facts = drink.facts.map((fact) => `<li><span>${escapeHtml(fact.label)}</span><strong>${escapeHtml(fact.value)}</strong></li>`).join("");
  const ingredients = drink.ingredients.map((ingredient) => `<article class="ingredient ${ingredient.status}"><div class="ingredient-top"><div><p class="ingredient-role">${escapeHtml(ingredient.role)}</p><h3>${escapeHtml(ingredient.name)}</h3></div><span>${statusLabels[ingredient.status]}</span></div><p>${escapeHtml(ingredient.context)}</p>${ingredient.evidence ? `<a href="${ingredient.evidence.url}" target="_blank" rel="noreferrer">Read source ↗</a>` : ""}</article>`).join("");
  result.innerHTML = `
    <div class="result-heading"><div><p class="eyebrow">MATCHED FROM ${escapeHtml(matchedFrom).toUpperCase()}</p><h2>${escapeHtml(drink.name)}</h2><p>${escapeHtml(drink.region)} formulation · ${escapeHtml(drink.serving)}</p></div><span class="verified">Dataset ${escapeHtml(drink.dataVersion || dataVersion)}</span></div>
    <div class="summary-grid"><section class="facts"><h3>At a glance</h3><ul>${facts}</ul></section><section class="takeaway"><p class="eyebrow">LABEL SCREEN</p><h3>${escapeHtml(drink.assessment.title)}</h3><p>${escapeHtml(drink.assessment.context)}</p></section></div>
    <div class="source-line"><strong>Package source:</strong> <a href="${drink.source.url}" target="_blank" rel="noreferrer">${escapeHtml(drink.source.title)} ↗</a> <span>${escapeHtml(drink.source.note)}</span></div>
    <div class="ingredient-heading"><div><p class="eyebrow">INGREDIENT BY INGREDIENT</p><h2>What the label tells us</h2></div><p>“Worth watching” signals a possible intake or sensitivity consideration—not that an ingredient is inherently unsafe.</p></div>
    <div class="ingredient-grid">${ingredients}</div>
    <aside class="disclaimer"><strong>Important:</strong> This is educational context, not a diagnosis or personalized medical advice. Ask a qualified clinician about pregnancy, health conditions, medications, allergies, or individual dietary needs.</aside>`;
  result.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function handleQuery(raw, origin = "typed search") {
  let drink = null;
  try {
    drink = await findCatalogProduct(raw);
  } catch (error) {
    console.warn("Catalog API is unavailable; using the reviewed local seed only.", error);
  }
  drink ||= findDrink(raw);
  if (drink) {
    scanStatus.textContent = "";
    showResult(drink, origin);
    return true;
  } else {
    result.classList.add("hidden");
    emptyState.classList.remove("hidden");
    emptyState.innerHTML = `<div class="empty-badge">?</div><div><p class="eyebrow">NOT IN THE REVIEWED SET YET</p><h2>We couldn’t make a confident match.</h2><p>Try the brand and full drink name. We’d rather show no result than guess from an incomplete label match.</p></div><div class="empty-arrow" aria-hidden="true">↗</div>`;
    return false;
  }
}

async function loadCatalogSummary() {
  try {
    const summary = await getCatalogSummary();
    reviewedCount.textContent = summary.reviewed_package_labels;
    discoveryCount.textContent = summary.catalog_discoveries;
  } catch (error) {
    console.warn("Catalog summary is unavailable; showing the bundled coverage figures.", error);
  }
}

loadCatalogSummary();

form.addEventListener("submit", async (event) => { event.preventDefault(); await handleQuery(query.value); });
document.querySelectorAll("[data-drink]").forEach((button) => {
  button.addEventListener("click", async () => {
    query.value = button.dataset.drink;
    await handleQuery(query.value, "quick search");
  });
});

async function ocrFile(file, origin) {
  scanStatus.textContent = `Reading ${origin}… this can take a moment.`;
  try {
    const worker = await createWorker("eng");
    const { data } = await worker.recognize(file);
    await worker.terminate();
    const recognized = data.text.replace(/\s+/g, " ").trim();
    query.value = recognized;
    const matched = await handleQuery(recognized, origin);
    if (matched) {
      scanStatus.textContent = "Label text read and a drink matched. Confirm it matches your package.";
    } else {
      scanStatus.textContent = "I read the label, but couldn’t confidently match it to the beta dataset. Edit the search field with the brand and product name.";
      query.focus();
    }
  } catch (error) {
    console.error(error);
    scanStatus.textContent = "The label could not be read. Try a well-lit, front-facing photo or search by name.";
  }
}

imageInput.addEventListener("change", () => {
  const file = imageInput.files?.[0];
  const problem = validateScanFile(file, "image");
  if (problem) { scanStatus.textContent = problem; return; }
  ocrFile(file, "image label");
});

videoInput.addEventListener("change", async () => {
  const file = videoInput.files?.[0];
  const problem = validateScanFile(file, "video");
  if (problem) { scanStatus.textContent = problem; return; }
  scanStatus.textContent = "Finding a readable video frame…";
  const video = document.createElement("video");
  video.muted = true;
  const fileUrl = URL.createObjectURL(file);
  video.src = fileUrl;
  try {
    await new Promise((resolve, reject) => { video.onloadedmetadata = resolve; video.onerror = reject; });
    video.currentTime = Math.min(Math.max(video.duration / 2, 0), 2);
    await new Promise((resolve) => { video.onseeked = resolve; });
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    const frame = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
    if (!frame) throw new Error("No readable video frame was produced.");
    await ocrFile(frame, "video frame");
  } catch (error) {
    console.error(error);
    scanStatus.textContent = "The video frame could not be scanned. Try a clear still image or search by name.";
  } finally { URL.revokeObjectURL(fileUrl); }
});

voiceButton.addEventListener("click", () => {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) { scanStatus.textContent = "Voice recognition is not supported by this browser. Please type the drink name."; return; }
  const recognition = new Recognition();
  recognition.lang = "en-US"; recognition.interimResults = false; recognition.maxAlternatives = 1;
  scanStatus.textContent = "Listening—say the drink name.";
  recognition.onresult = async (event) => { const heard = event.results[0][0].transcript; query.value = heard; await handleQuery(heard, "voice"); };
  recognition.onerror = () => { scanStatus.textContent = "I couldn’t hear a drink name. Please try again or type it."; };
  recognition.start();
});
