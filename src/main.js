import { createWorker } from "tesseract.js";
import { dataVersion, findDrink, drinks } from "./data.js";
import { findCatalogDiscovery, findCatalogProduct, findCatalogProductByGtin, getCatalogDiscoveries, getCatalogSummary, getCatalogProducts, getCatalogProduct, normalizeName, toDisplaySourceLabel } from "./catalog-api.js";
import { buildPackageChoices, hasExplanation } from "./package-options.js";
import { resetCaptureButton, setCaptureProcessing } from "./camera-ui.js";
import { validateScanFile } from "./scan-guardrails.js";
import "./style.css";
import "./camera.css";
import "./package-picker.css";

const form = document.querySelector("#search-form");
const query = document.querySelector("#drink-query");
const imageInput = document.querySelector("#image-input");
const videoInput = document.querySelector("#video-input");
const voiceButton = document.querySelector("#voice-button");
const cameraButton = document.querySelector("#camera-button");
const cameraDialog = document.querySelector("#camera-dialog");
const cameraPreview = document.querySelector("#camera-preview");
const cameraCapture = document.querySelector("#camera-capture");
const cameraStatus = document.querySelector("#camera-status");
const cameraClose = document.querySelector("#camera-close");
const cameraCancel = document.querySelector("#camera-cancel");
const scanStatus = document.querySelector("#scan-status");
const result = document.querySelector("#result");
const emptyState = document.querySelector("#empty-state");
const reviewedCount = document.querySelector("#catalog-reviewed-count");
const discoveryCount = document.querySelector("#catalog-discovery-count");
const sourceCount = document.querySelector("#catalog-source-count");
const discoveryList = document.querySelector("#discovery-list");
const packagePicker = document.querySelector("#package-picker");
const variantSelect = document.querySelector("#drink-variant");
const sizeSelect = document.querySelector("#drink-size");
const packageSubmit = document.querySelector("#package-submit");
const packageHint = document.querySelector("#package-hint");
let packageChoices = [];
let selectionRevision = 0;
let cameraStream = null;
const OCR_TIMEOUT_MS = 45_000;

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
    <div class="result-heading"><div><p class="eyebrow">MATCHED FROM ${escapeHtml(matchedFrom).toUpperCase()}</p><h2>${escapeHtml(drink.name)}</h2><p>${escapeHtml(drink.region)}${drink.package ? ` · Package: ${escapeHtml(drink.package)}` : ""}</p><p>Nutrition per listed serving: ${escapeHtml(drink.serving)}</p></div><span class="verified">Dataset ${escapeHtml(drink.dataVersion || dataVersion)}</span></div>
    ${drink.scopeNote ? `<p class="source-scope">${escapeHtml(drink.scopeNote)}</p>` : ""}
    <div class="summary-grid"><section class="facts"><h3>Per listed serving</h3>${facts ? `<ul>${facts}</ul>` : "<p>Nutrition amounts are not provided in this source record. See the declared ingredients below.</p>"}</section><section class="takeaway"><p class="eyebrow">LABEL SCREEN</p><h3>${escapeHtml(drink.assessment.title)}</h3><p>${escapeHtml(drink.assessment.context)}</p></section></div>
    <div class="source-line"><strong>Label information source:</strong> <a href="${escapeHtml(safeExternalUrl(drink.source.url))}" target="_blank" rel="noreferrer">${escapeHtml(drink.source.title)} ↗</a> <span>${escapeHtml(drink.source.note)}</span></div>
    ${drink.ingredientStatement ? `<section class="ingredient-statement"><h3>Full declared ingredient list</h3><p>${escapeHtml(drink.ingredientStatement)}</p></section>` : ""}
    ${ingredients ? `<div class="ingredient-heading"><div><p class="eyebrow">INGREDIENT CONTEXT</p><h2>What the label tells us</h2></div><p>These notes cover selected declared ingredients or groups. They do not establish personal safety or an undisclosed ingredient amount.</p></div>` : ""}
    <div class="ingredient-grid">${ingredients}</div>
    <aside class="disclaimer"><strong>Important:</strong> This is educational context, not a diagnosis or personalized medical advice. Ask a qualified clinician about pregnancy, health conditions, medications, allergies, or individual dietary needs.</aside>`;
  result.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showDiscoveryResult(drink, matchedFrom = "typed search", selectedSize = "") {
  const sourceDrink = toDisplaySourceLabel(drink, selectedSize);
  if (sourceDrink) return showResult(sourceDrink, matchedFrom);
  emptyState.classList.add("hidden");
  result.classList.remove("hidden");
  const packageSizes = drink.observed_package_sizes || "No package-size evidence has been recorded yet.";
  const status = drink.verification_status === "needs_package_verification" ? "Needs package-label verification" : "Source-backed discovery candidate";
  result.innerHTML = `
    <div class="result-heading"><div><p class="eyebrow">MATCHED FROM ${escapeHtml(matchedFrom).toUpperCase()}</p><h2>${escapeHtml(drink.variant_name)}</h2><p>${escapeHtml(drink.market)} · ${escapeHtml(drink.category)}</p>${selectedSize ? `<p>Selected package: ${escapeHtml(selectedSize)}</p>` : ""}</div><span class="verified">DISCOVERY RECORD</span></div>
    <section class="discovery-result-card"><p class="eyebrow">WHAT WE CAN CONFIRM</p><h3>This product is in the source-backed discovery catalog, but an exact package label has not been reviewed yet.</h3><dl><div><dt>Manufacturer</dt><dd>${escapeHtml(drink.manufacturer_name)}</dd></div><div><dt>Available size evidence</dt><dd>${escapeHtml(packageSizes)}</dd></div><div><dt>Review status</dt><dd>${escapeHtml(status)}</dd></div></dl><p>ClearSip intentionally does not guess ingredients, nutrition facts, or health context until a specific US package label is attached.</p><a href="${escapeHtml(safeExternalUrl(drink.source_url))}" target="_blank" rel="noreferrer">Check the public source ↗</a></section>`;
  result.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function handleQuery(raw, origin = "typed search") {
  selectionRevision++;
  packagePicker.classList.add("hidden");
  let drink = null;
  const gtin = raw.replace(/\D/g, "");
  if ([8, 12, 13, 14].includes(gtin.length)) {
    try {
      drink = await findCatalogProductByGtin(gtin);
      if (drink) origin = "exact barcode lookup";
    } catch (error) {
      console.warn("No exact package was found for this barcode.", error);
    }
  }
  try {
    drink ||= await findCatalogProduct(raw);
  } catch (error) {
    console.warn("Catalog API is unavailable; using the reviewed local seed only.", error);
  }
  drink ||= findDrink(raw);
  if (drink) {
    scanStatus.textContent = "";
    showResult(drink, origin);
    return true;
  }

  try {
    const discovery = await findCatalogDiscovery(raw);
    if (discovery) {
      scanStatus.textContent = discovery.source_label ? "Manufacturer ingredient information found. Compare it with your package." : "This drink is listed, but ingredient information is not available yet.";
      showDiscoveryResult(discovery, origin);
      return true;
    }
  } catch (error) {
    console.warn("Catalog discovery lookup is unavailable.", error);
  }

  result.classList.add("hidden");
  emptyState.classList.remove("hidden");
  emptyState.innerHTML = `<div class="empty-badge">?</div><div><p class="eyebrow">NOT IN THE REVIEWED SET YET</p><h2>We couldn’t make a confident match.</h2><p>Try the brand and full drink name. We’d rather show no result than guess from an incomplete label match.</p></div><div class="empty-arrow" aria-hidden="true">↗</div>`;
  return false;
}

async function loadCatalogSummary() {
  try {
    const summary = await getCatalogSummary();
    reviewedCount.textContent = summary.reviewed_package_labels;
    discoveryCount.textContent = summary.catalog_discoveries;
    sourceCount.textContent = `${summary.source_ingredient_panels ?? 0} drink entries have manufacturer ingredient information. ${summary.pending_ingredient_panels ?? summary.catalog_discoveries} are still awaiting ingredient information.`;
  } catch (error) {
    console.warn("Catalog summary is unavailable; showing the bundled coverage figures.", error);
  }
}

function safeExternalUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:" ? url.href : "#";
  } catch {
    return "#";
  }
}

async function loadCatalogDiscoveries() {
  try {
    const discoveries = await getCatalogDiscoveries();
    discoveryList.innerHTML = discoveries.map((drink) => `
      <article class="discovery-card">
        <div><p>${escapeHtml(drink.category)}</p><h3>${escapeHtml(drink.variant_name)}</h3><span>${escapeHtml(drink.manufacturer_name)} · ${escapeHtml(drink.beverage_family_name)}</span></div>
        <div class="discovery-meta"><strong>${drink.source_label ? "Manufacturer ingredients available" : "Ingredients pending"}</strong><span>${escapeHtml(drink.observed_package_sizes || "Package size not yet verified")}</span></div>
        <a href="${escapeHtml(safeExternalUrl(drink.source_url))}" target="_blank" rel="noreferrer">View source ↗</a>
      </article>`).join("");
  } catch (error) {
    console.warn("Catalog discovery list is unavailable.", error);
    discoveryList.textContent = "The discovery list is temporarily unavailable. Reviewed package-label results are still searchable above.";
  }
}

loadCatalogSummary();
loadCatalogDiscoveries();

function clearSelectionResult() {
  selectionRevision++;
  result.classList.add("hidden");
}

function populateSizes() {
  clearSelectionResult();
  const group = variantSelect.value === "" ? null : packageChoices[Number(variantSelect.value)];
  sizeSelect.replaceChildren(new Option(group ? "Choose package size" : "Choose a drink first", ""));
  sizeSelect.disabled = !group;
  packageSubmit.disabled = true;
  packageHint.textContent = "Choose the size printed on your can or bottle. Label details are available only for the sizes marked below.";
  group?.options.forEach((option, index) => {
    const available = hasExplanation(option);
    const suffix = option.discovery?.source_label ? " — manufacturer ingredients" : available ? " — label available" : " — ingredients not available yet";
    const entry = new Option(`${option.label}${suffix}`, String(index));
    entry.disabled = !available;
    sizeSelect.add(entry);
  });
  if (group && !group.options.some(hasExplanation)) {
    sizeSelect.disabled = true;
    packageHint.innerHTML = `Ingredient information for this drink is not available in ClearSip yet. ${group.discovery ? `<a href="${escapeHtml(safeExternalUrl(group.discovery.source_url))}" target="_blank" rel="noreferrer">Open the manufacturer's source ↗</a>` : ""}`;
  }
}

async function searchPackageChoices(raw) {
  const revision = ++selectionRevision;
  packagePicker.classList.add("hidden");
  result.classList.add("hidden");
  const term = raw.trim();
  if (term.length < 2) {
    scanStatus.textContent = "Enter at least two characters of the drink name.";
    return;
  }
  // A barcode already identifies a package; it does not need a size picker.
  if (/^\d{8}$|^\d{12,14}$/.test(term)) return handleQuery(term);
  scanStatus.textContent = "Finding drinks and available sizes…";
  const alias = drinks.find((drink) => [drink.name, ...drink.aliases].some((name) => normalizeName(name) === normalizeName(term)));
  const searchTerm = alias?.name || term;
  const responses = await Promise.allSettled([getCatalogProducts(searchTerm), getCatalogDiscoveries(searchTerm)]);
  if (revision !== selectionRevision) return;
  packageChoices = buildPackageChoices(
    responses[0].status === "fulfilled" ? responses[0].value : [],
    responses[1].status === "fulfilled" ? responses[1].value : [],
  );
  if (!packageChoices.length && alias) {
    packageChoices = [{ name: alias.name, market: alias.region, options: [{
      label: alias.id === "coca-cola-zero-sugar" ? "12 fl oz can" : "16 fl oz can",
      localDrink: alias,
    }] }];
  }
  if (!packageChoices.length) {
    scanStatus.textContent = responses.some((response) => response.status === "rejected")
      ? "The catalog is temporarily unavailable. Please try again."
      : "No drink found. Try its brand and flavor name.";
    emptyState.classList.remove("hidden");
    return;
  }
  variantSelect.replaceChildren(new Option("Choose a drink / flavor", ""));
  packageChoices.forEach((group, index) => variantSelect.add(new Option(`${group.name} · ${group.market}${group.options.some(hasExplanation) ? "" : " · ingredients pending"}`, String(index))));
  if (packageChoices.length === 1) variantSelect.value = "0";
  populateSizes();
  emptyState.classList.add("hidden");
  packagePicker.classList.remove("hidden");
  scanStatus.textContent = responses.some((response) => response.status === "rejected")
    ? "Some size information could not load. Showing the available results." : "";
  (packageChoices.length === 1 && !sizeSelect.disabled ? sizeSelect : variantSelect).focus();
}

query.addEventListener("input", () => {
  clearSelectionResult();
  packagePicker.classList.add("hidden");
  scanStatus.textContent = "";
});
variantSelect.addEventListener("change", populateSizes);
sizeSelect.addEventListener("change", () => {
  clearSelectionResult();
  const option = packageChoices[Number(variantSelect.value)]?.options[Number(sizeSelect.value)];
  packageSubmit.disabled = sizeSelect.value === "" || !hasExplanation(option);
  packageHint.textContent = option?.discovery?.source_label
    ? "Manufacturer ingredients and the source's stated nutrition serving are available. Confirm these against your package."
    : "Select Show this size to open its available information.";
});
packagePicker.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (variantSelect.value === "" || sizeSelect.value === "") return;
  const option = packageChoices[Number(variantSelect.value)]?.options[Number(sizeSelect.value)];
  if (!hasExplanation(option)) return;
  const revision = ++selectionRevision;
  packageSubmit.disabled = true;
  packageHint.textContent = "Loading your selected package…";
  try {
    const drink = (option.discovery && toDisplaySourceLabel(option.discovery, option.label))
      || (option.packageId ? await getCatalogProduct(option.packageId) : option.localDrink);
    if (revision !== selectionRevision) return;
    if (drink) showResult({ ...drink, package: option.label }, "drink and size selection");
    packageHint.textContent = "Showing available ingredients. Nutrition values below are per listed serving.";
  } catch (error) {
    if (revision === selectionRevision) packageHint.textContent = "This package could not load. Please try again.";
  } finally {
    if (revision === selectionRevision) packageSubmit.disabled = false;
  }
});

form.addEventListener("submit", async (event) => { event.preventDefault(); await searchPackageChoices(query.value); });
document.querySelectorAll("[data-drink]").forEach((button) => {
  button.addEventListener("click", async () => {
    query.value = button.dataset.drink;
    await searchPackageChoices(query.value);
  });
});

function withTimeout(promise, message) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = window.setTimeout(() => reject(new Error(message)), OCR_TIMEOUT_MS);
  });
  return Promise.race([promise, timeout]).finally(() => window.clearTimeout(timer));
}

async function ocrFile(file, origin) {
  scanStatus.textContent = `Reading ${origin}… this can take a moment.`;
  let worker;
  try {
    worker = await withTimeout(createWorker("eng"), "The label reader took too long to start. Check your connection and try again.");
    const { data } = await withTimeout(worker.recognize(file), "The label reader took too long. Try a closer, well-lit label photo.");
    const recognized = data.text.replace(/\s+/g, " ").trim();
    query.value = recognized;
    const matched = await handleQuery(recognized, origin);
    if (matched) {
      scanStatus.textContent = "Label text read and a drink matched. Confirm it matches your package.";
    } else {
      scanStatus.textContent = "I read the label, but couldn’t confidently match it to the beta dataset. Edit the search field with the brand and product name.";
      query.focus();
    }
    return matched;
  } catch (error) {
    console.error(error);
    scanStatus.textContent = error.message || "The label could not be read. Try a well-lit, front-facing photo or search by name.";
    return false;
  } finally {
    await worker?.terminate().catch((error) => console.warn("Could not stop the label reader.", error));
  }
}

function stopCamera() {
  cameraStream?.getTracks().forEach((track) => track.stop());
  cameraStream = null;
  cameraPreview.srcObject = null;
  if (cameraDialog.open) cameraDialog.close();
}

async function openCamera() {
  if (!navigator.mediaDevices?.getUserMedia) {
    scanStatus.textContent = "Camera scanning is not supported in this browser. Choose a photo instead.";
    return;
  }

  resetCaptureButton(cameraCapture);
  cameraStatus.textContent = "Starting camera…";
  cameraButton.disabled = true;
  scanStatus.textContent = "Opening your camera…";
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: { facingMode: { ideal: "environment" }, width: { ideal: 1920 }, height: { ideal: 1080 } },
    });
    cameraPreview.srcObject = cameraStream;
    cameraDialog.showModal();
    await cameraPreview.play();
    cameraStatus.textContent = "Ready to capture the front label.";
    scanStatus.textContent = "";
  } catch (error) {
    console.error(error);
    stopCamera();
    scanStatus.textContent = "Camera access was unavailable. Allow camera access, then try again, or choose a photo instead.";
  } finally {
    cameraButton.disabled = false;
  }
}

async function captureCameraFrame() {
  if (!cameraPreview.videoWidth || !cameraPreview.videoHeight) {
    scanStatus.textContent = "The camera is still starting. Try capture again in a moment.";
    return;
  }

  setCaptureProcessing(cameraCapture);
  cameraStatus.textContent = "Reading the label. This can take up to 45 seconds.";
  const canvas = document.createElement("canvas");
  const longestEdge = 1920;
  const scale = Math.min(1, longestEdge / Math.max(cameraPreview.videoWidth, cameraPreview.videoHeight));
  canvas.width = Math.round(cameraPreview.videoWidth * scale);
  canvas.height = Math.round(cameraPreview.videoHeight * scale);
  const context = canvas.getContext("2d");
  if (!context) {
    resetCaptureButton(cameraCapture);
    cameraStatus.textContent = "This browser could not prepare the camera image. Try choosing a photo instead.";
    return;
  }
  context.drawImage(cameraPreview, 0, 0, canvas.width, canvas.height);

  try {
    const frame = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.92));
    const problem = validateScanFile(frame, "image");
    if (problem) throw new Error(problem);
    await ocrFile(frame, "camera label");
    stopCamera();
  } catch (error) {
    console.error(error);
    scanStatus.textContent = error.message || "The camera image could not be captured. Try again or choose a photo.";
    cameraStatus.textContent = "Capture failed. Try again with the label centered and well lit.";
  } finally {
    resetCaptureButton(cameraCapture);
  }
}

imageInput.addEventListener("change", () => {
  const file = imageInput.files?.[0];
  const problem = validateScanFile(file, "image");
  if (problem) { scanStatus.textContent = problem; return; }
  ocrFile(file, "image label");
});

cameraButton.addEventListener("click", openCamera);
cameraCapture.addEventListener("click", captureCameraFrame);
cameraClose.addEventListener("click", stopCamera);
cameraCancel.addEventListener("click", stopCamera);
cameraDialog.addEventListener("close", stopCamera);

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
