"""Release gates evaluated per class, not just a misleading aggregate accuracy."""
from __future__ import annotations

from ml.dataset import UNKNOWN_CLASS


def evaluate_predictions(labels, truth, probabilities, threshold=0.8, margin=0.15, minimum=30):
    if len(truth) != len(probabilities) or len(set(labels)) != len(labels) or UNKNOWN_CLASS not in labels:
        raise ValueError("Invalid evaluation label/sample mapping")
    counts = {label: {"samples": 0, "predicted": 0, "correct": 0} for label in labels}
    false_unknown_accepts = 0
    for actual, scores in zip(truth, probabilities):
        if actual not in counts or len(scores) != len(labels):
            raise ValueError("Evaluation class is absent or score dimensions differ")
        from math import isfinite
        if any(not isfinite(score) or score < 0 or score > 1 for score in scores):
            raise ValueError("Invalid model scores")
        ordered = sorted(range(len(labels)), key=lambda index: scores[index], reverse=True)
        first, second = ordered[:2]
        predicted = labels[first] if scores[first] >= threshold and scores[first] - scores[second] >= margin else None
        if predicted == UNKNOWN_CLASS:
            predicted = None
        counts[actual]["samples"] += 1
        if predicted:
            counts[predicted]["predicted"] += 1
            counts[predicted]["correct"] += predicted == actual
        false_unknown_accepts += actual == UNKNOWN_CLASS and predicted is not None
    per_class = {}
    for label, row in counts.items():
        if label == UNKNOWN_CLASS:
            continue
        precision = row["correct"] / row["predicted"] if row["predicted"] else 0
        recall = row["correct"] / row["samples"] if row["samples"] else 0
        per_class[label] = {**row, "precision": precision, "recall": recall,
                            "passed": row["samples"] >= minimum and precision >= 0.95 and recall >= 0.8}
    unknown_total = counts[UNKNOWN_CLASS]["samples"]
    rate = false_unknown_accepts / unknown_total if unknown_total else 1
    return {"per_class": per_class, "unknown_samples": unknown_total,
            "unknown_false_accepts": false_unknown_accepts, "unknown_false_accept_rate": rate,
            "passed": bool(per_class) and all(row["passed"] for row in per_class.values()) and unknown_total >= minimum and rate <= 0.05}


def require_previous_classes(labels, previous_labels):
    missing = set(previous_labels) - set(labels)
    if missing:
        raise ValueError(f"Previously trained classes cannot be dropped: {sorted(missing)}")
