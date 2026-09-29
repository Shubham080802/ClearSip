"""Refuse activated artifacts without coverage, held-out, parity, and device evidence."""
import json
import hashlib
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from api.recognition import recognition_catalog
from ml.dataset import UNKNOWN_CLASS


def check_release(directory: Path):
    release = json.loads((directory / "release.json").read_text())
    if release["status"] == "awaiting_training_images":
        if release.get("labels") or release.get("validation_passed") is not False:
            raise ValueError("Untrained releases cannot claim class coverage")
        return "No trained model deployed; OCR and manual lookup remain available"
    if release.get("status") != "validated" or release.get("validation_passed") is not True:
        raise ValueError("Only reviewed, validated releases can be activated")
    if release.get("training_mode") == "research-only" or release.get("evaluation_status") == "deferred":
        raise ValueError("Research-only/deferred-evaluation artifacts cannot be activated; create a camera-evaluated run")
    labels = release["labels"]
    known = {row["id"] for row in recognition_catalog() if row["trainable"]}
    if len(labels) < 3 or len(set(labels)) != len(labels) or UNKNOWN_CLASS not in labels or set(labels) - {UNKNOWN_CLASS} - known:
        raise ValueError("Model labels do not map to concrete catalog targets")
    report = json.loads((directory / "evaluation.json").read_text())
    if set(report["per_class"]) != set(labels) - {UNKNOWN_CLASS}:
        raise ValueError("Every deployed class needs its own held-out report")
    for row in report["per_class"].values():
        if not all(math.isfinite(row[key]) for key in ("samples", "precision", "recall")) or row["samples"] < 30 or not 0.95 <= row["precision"] <= 1 or not 0.8 <= row["recall"] <= 1 or row["passed"] is not True:
            raise ValueError("Held-out per-class release gate failed")
    if report["passed"] is not True or report["unknown_samples"] < 30 or not 0 <= report["unknown_false_accept_rate"] <= 0.05:
        raise ValueError("Unknown-image rejection gate failed")
    browser = json.loads((directory / "browser-review.json").read_text())
    if browser.get("model_version") != release["version"] or browser.get("passed") is not True or not browser.get("reviewer"):
        raise ValueError("Missing version-matched browser review")
    if not browser.get("devices") or not 0 <= browser.get("max_python_js_score_difference", 1) <= 0.01:
        raise ValueError("Missing device/parity evidence")
    model = json.loads((directory / "model.json").read_text())
    model_files = {directory / "model.json"}
    for group in model["weightsManifest"]:
        for filename in group["paths"]:
            artifact = (directory / filename).resolve()
            if not artifact.is_relative_to(directory.resolve()) or not artifact.is_file():
                raise ValueError("Weight shards must exist inside the model directory")
            model_files.add(artifact)
    digest = hashlib.sha256()
    for artifact in sorted(model_files, key=lambda path: path.name):
        digest.update(artifact.name.encode())
        digest.update(artifact.read_bytes())
    if release.get("model_sha256") != digest.hexdigest() or browser.get("model_sha256") != digest.hexdigest():
        raise ValueError("Artifact hash must match the release and browser review")
    if release.get("preprocessing") != "rgb-bilinear-half-pixel-minus-one-to-one" or release.get("input_size") != 224:
        raise ValueError("Training/browser preprocessing mismatch")
    return f"Validated model artifact for {len(labels)-1} concrete drink variants"


if __name__ == "__main__":
    print(check_release(ROOT / "public/models/drink-recognizer"))
