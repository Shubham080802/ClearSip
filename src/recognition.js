import { normalizeName } from "./catalog-api.js";

export const UNKNOWN_CLASS = "__unknown__";
const RELEASE_URL = "/models/drink-recognizer/release.json";
let runtimePromise;

function words(value) {
  return normalizeName(value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
    .replace(/power\s+ade/gi, "powerade")).split(" ").filter(Boolean);
}

export function contradictsLabel(name, text) {
  const named = new Set(words(name));
  const seen = new Set(words(text));
  return (seen.has("zero") && !named.has("zero")) || (seen.has("diet") && !named.has("diet"));
}

export function rankOcrCandidates(text, catalog) {
  const observed = new Set(words(text));
  if (!observed.size) return [];
  const generic = new Set(["drink", "drinks", "water", "coffee", "cold", "brew", "sugar", "juice", "flavored", "flavour", "energy", "original", "the"]);
  return catalog.filter((row) => row.trainable && !contradictsLabel(row.name, text)).map((row) => {
    const tokens = [...new Set(words(row.name))];
    const brand = tokens.find((token) => !generic.has(token));
    if (!brand || !observed.has(brand)) return null;
    const matched = tokens.filter((token) => observed.has(token));
    const distinctive = matched.filter((token) => !generic.has(token));
    return { ...row, evidence: "label text", score: (matched.length / tokens.length) + distinctive.length * 0.05 };
  }).filter(Boolean).sort((a, b) => b.score - a.score || a.id.localeCompare(b.id)).slice(0, 5);
}

export function selectVisualCandidates(scores, release, catalog, text = "") {
  if (release.status !== "validated" || release.validation_passed !== true) return [];
  if (!Array.isArray(scores) || scores.length !== release.labels.length ||
      scores.some((score) => !Number.isFinite(score) || score < 0 || score > 1)) return [];
  const ordered = scores.map((score, index) => ({ id: release.labels[index], score })).sort((a, b) => b.score - a.score);
  const first = ordered[0];
  if (!first || first.id === UNKNOWN_CLASS || first.score < release.score_threshold ||
      first.score - (ordered[1]?.score || 0) < release.margin_threshold) return [];
  const target = catalog.find((row) => row.id === first.id && row.trainable);
  if (!target || contradictsLabel(target.name, text)) return [];
  return [{ ...target, score: first.score, evidence: "visual model suggestion" }];
}

export function mergeCandidates(visual, ocr) {
  const rows = new Map();
  for (const row of [...visual, ...ocr]) {
    const previous = rows.get(row.id);
    rows.set(row.id, previous ? { ...previous, evidence: "visual model and label text" } : row);
  }
  return [...rows.values()].slice(0, 5);
}

export async function readBarcode(image) {
  if (!globalThis.BarcodeDetector) return null;
  try {
    const supported = await BarcodeDetector.getSupportedFormats();
    const formats = ["ean_13", "ean_8", "upc_a", "upc_e"].filter((format) => supported.includes(format));
    if (!formats.length) return null;
    const codes = await new BarcodeDetector({ formats }).detect(image);
    const values = [...new Set(codes.map((code) => code.rawValue).filter((value) => /^\d{8}$|^\d{12,14}$/.test(value)))];
    return values.length === 1 ? values[0] : null;
  } catch {
    return null; // Native barcode support is optional; OCR/manual remain available.
  }
}

async function loadRuntime() {
  const response = await fetch(RELEASE_URL);
  if (!response.ok) throw new Error("Visual model release unavailable");
  const release = await response.json();
  if (release.status !== "validated" || release.validation_passed !== true) return { release, model: null };
  if (release.schema_version !== 1 || release.input_size !== 224 ||
      release.preprocessing !== "rgb-bilinear-half-pixel-minus-one-to-one" ||
      !Array.isArray(release.labels) || !release.labels.includes(UNKNOWN_CLASS) ||
      new Set(release.labels).size !== release.labels.length ||
      !Number.isFinite(release.score_threshold) || release.score_threshold < 0.5 || release.score_threshold > 1 ||
      !Number.isFinite(release.margin_threshold) || release.margin_threshold < 0 || release.margin_threshold > 1) {
    throw new Error("Unsupported visual model release");
  }
  const tf = await import("@tensorflow/tfjs");
  await tf.ready();
  const model = await tf.loadLayersModel("/models/drink-recognizer/model.json");
  if (model.inputs.length !== 1 || model.inputs[0].shape.slice(1).join(",") !== "224,224,3" ||
      model.outputs.length !== 1 || model.outputs[0].shape.at(-1) !== release.labels.length) {
    model.dispose();
    throw new Error("Visual class mapping mismatch");
  }
  return { release, model, tf };
}

export async function classifyImage(image, catalog, text = "") {
  try {
    runtimePromise ||= loadRuntime().catch((error) => { runtimePromise = null; throw error; });
    const { release, model, tf } = await runtimePromise;
    if (!model) return { candidates: [], status: "awaiting_training_images" };
    const input = tf.tidy(() => tf.image.resizeBilinear(tf.browser.fromPixels(image, 3), [224, 224], false, true)
      .toFloat().div(127.5).sub(1).expandDims(0));
    let output;
    try {
      output = model.predict(input);
      const scores = Array.from(await output.data());
      return { candidates: selectVisualCandidates(scores, release, catalog, text), status: "validated" };
    } finally {
      input.dispose();
      output?.dispose();
    }
  } catch (error) {
    console.warn("Visual recognition unavailable; label text remains available.", error);
    return { candidates: [], status: "unavailable" };
  }
}
