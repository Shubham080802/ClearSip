"""Train all ready photo classes cumulatively and export an UNAPPROVED candidate.

No training occurs without permission-cleared, provenance-reviewed photos.
Research-only training may precede camera holdouts, but cannot be released.
Use an isolated Linux Python 3.11 environment; do not add TF to the API runtime.
"""
from __future__ import annotations

import argparse
import json
import os
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from api.recognition import recognition_catalog
from ml.dataset import MIN_IMAGES, UNKNOWN_CLASS, load_manifest, preparation_report, readiness, validate_samples
from ml.metrics import evaluate_predictions, require_previous_classes


TRAINING_MODES = ("camera-evaluated", "research-only")


def training_plan(catalog, samples, previous_labels=(), mode="camera-evaluated"):
    if mode not in TRAINING_MODES:
        raise ValueError("Unknown training mode")
    audit = readiness(catalog, samples)
    if mode == "research-only":
        audit = preparation_report(catalog, samples)
        labels = audit["training_ready_classes"]
    else:
        labels = sorted(row["id"] for row in audit["records"] if row["status"] == "ready_to_train")
    require_previous_classes(labels + [UNKNOWN_CLASS], previous_labels)
    if len(labels) < 2:
        if mode == "research-only":
            raise ValueError("At least two specific classes need 100 approved training photos each; quarantine does not count")
        raise ValueError("At least two specific classes need 100 train / 20 validation / 30 test photos each")
    if mode == "research-only" and not audit["unknown_training_minimum_met"]:
        raise ValueError("Collect 100 approved unknown/no-drink training photos first")
    if mode == "camera-evaluated" and any(audit["unknown_counts"][split] < minimum for split, minimum in MIN_IMAGES.items()):
        raise ValueError("Collect unknown drinks and no-drink scenes in each independent split first")
    return labels + [UNKNOWN_CLASS], audit


def deferred_evaluation():
    return {"status": "deferred", "passed": False, "per_class": {}, "unknown_samples": 0,
            "unknown_false_accept_rate": None,
            "reason": "Research-only run: camera validation/test not evaluated; thresholds are not calibrated. Not eligible for deployment."}


def fit_and_evaluate(model, dataset, split_rows, labels, epochs, mode, validation_callbacks=()):
    """Research runs never fit/evaluate on holdouts, even when listed in the manifest."""
    if mode == "research-only":
        model.fit(dataset("train"), epochs=epochs)
        return None, None, deferred_evaluation()
    if mode != "camera-evaluated":
        raise ValueError("Unknown training mode")
    model.fit(dataset("train"), validation_data=dataset("validation"), epochs=epochs,
              callbacks=list(validation_callbacks))
    validation_scores = model.predict(dataset("validation"), verbose=0).tolist()
    validation_truth = [row["class_id"] for row in split_rows["validation"]]
    viable = []
    for threshold in (0.6, 0.7, 0.8, 0.9, 0.95):
        for margin in (0.1, 0.15, 0.2, 0.3):
            report = evaluate_predictions(labels, validation_truth, validation_scores, threshold, margin, minimum=20)
            if report["passed"]:
                viable.append((sum(row["recall"] for row in report["per_class"].values()), threshold, margin))
    if not viable:
        raise ValueError("Validation rejection/quality gates failed; gather better data before evaluating the test set")
    _, threshold, margin = max(viable)
    test_scores = model.predict(dataset("test"), verbose=0).tolist()
    test_truth = [row["class_id"] for row in split_rows["test"]]
    return threshold, margin, evaluate_predictions(labels, test_truth, test_scores, threshold, margin)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--image-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--previous-release", type=Path, default=ROOT / "public/models/drink-recognizer/release.json")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--training-mode", choices=TRAINING_MODES, default="camera-evaluated")
    args = parser.parse_args()
    catalog = recognition_catalog()
    try:
        samples = validate_samples(load_manifest(args.manifest), args.image_root, catalog)
        previous = json.loads(args.previous_release.read_text()) if args.previous_release.exists() else {"labels": []}
        labels, audit = training_plan(catalog, samples, previous["labels"], args.training_mode)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    if args.plan_only:
        print(json.dumps({"training_mode": args.training_mode, "labels": labels, "coverage": audit,
                          "deployment_approved": False}, indent=2))
        return
    if args.output.resolve().is_relative_to((ROOT / "public").resolve()):
        parser.error("Training cannot write directly to deployed public assets; use ml-artifacts/a-new-run")
    if args.output.exists():
        parser.error("Output must be a new directory; keep previous runs for regression review")
    if not 1 <= args.epochs <= 100:
        parser.error("epochs must be between 1 and 100")

    os.environ["TF_USE_LEGACY_KERAS"] = "1"
    import numpy as np
    import tensorflow as tf
    import tf_keras as keras
    import tensorflowjs as tfjs
    from PIL import Image, ImageOps

    tf.random.set_seed(42)
    np.random.seed(42)
    rows = [row for row in samples if row["class_id"] in labels]
    label_index = {label: index for index, label in enumerate(labels)}

    def image_array(row):
        with Image.open(args.image_root / row["path"]) as source:
            pixels = np.asarray(ImageOps.exif_transpose(source).convert("RGB"), dtype=np.float32)
        # Matches browser resizeBilinear(..., false, true) and [-1, 1] scaling.
        return (tf.image.resize(pixels, (224, 224), method="bilinear").numpy() / 127.5) - 1

    split_rows = {split: [row for row in rows if row["split"] == split] for split in MIN_IMAGES}

    def dataset(split):
        def generator():
            for row in split_rows[split]:
                yield image_array(row), label_index[row["class_id"]]
        result = tf.data.Dataset.from_generator(generator, output_signature=(tf.TensorSpec((224, 224, 3), tf.float32), tf.TensorSpec((), tf.int32)))
        if split == "train":
            result = result.shuffle(1000, seed=42)
        return result.batch(16).prefetch(tf.data.AUTOTUNE)

    # Start each expanded run with all ready classes, not just the new burst.
    base = keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights="imagenet")
    base.trainable = False
    output = keras.layers.GlobalAveragePooling2D()(base.output)
    output = keras.layers.Dense(len(labels), activation="softmax")(output)
    model = keras.Model(base.input, output)
    model.compile(optimizer=keras.optimizers.Adam(0.001), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    callbacks = [keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)] if args.training_mode == "camera-evaluated" else []
    threshold, margin, report = fit_and_evaluate(model, dataset, split_rows, labels, args.epochs,
                                               args.training_mode, callbacks)
    args.output.mkdir(parents=True)
    tfjs.converters.save_keras_model(model, str(args.output))
    model_files = sorted(path for path in args.output.iterdir() if path.name == "model.json" or path.suffix == ".bin")
    digest = hashlib.sha256()
    for artifact in model_files:
        digest.update(artifact.name.encode())
        digest.update(artifact.read_bytes())
    release = {"schema_version": 1, "status": "candidate", "version": args.output.name,
               "training_mode": args.training_mode,
               "evaluation_status": "deferred" if args.training_mode == "research-only" else "completed",
               "model_sha256": digest.hexdigest(),
               "runtime": "tfjs-layers", "labels": labels, "input_size": 224,
               "preprocessing": "rgb-bilinear-half-pixel-minus-one-to-one",
               "score_threshold": threshold, "margin_threshold": margin, "validation_passed": False,
               "held_out_gates_passed": report["passed"]}
    (args.output / "release.json").write_text(json.dumps(release, indent=2) + "\n")
    (args.output / "evaluation.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "coverage.json").write_text(json.dumps(audit, indent=2) + "\n")
    # Deterministic numerical reference for the actual TF.js/browser importer.
    pixels = np.linspace(-1, 1, 224 * 224 * 3, dtype=np.float32).reshape(1, 224, 224, 3)
    (args.output / "parity.json").write_text(json.dumps({"input": "linear-minus-one-to-one", "shape": [1, 224, 224, 3],
                                                        "scores": model.predict(pixels, verbose=0)[0].tolist()}, indent=2) + "\n")
    print(f"Candidate exported for {len(labels)-1} drinks ({args.training_mode}). NOT approved or deployed. Test gates: {report['passed']}")


if __name__ == "__main__":
    main()
