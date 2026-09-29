"""Photo manifest validation and full-catalog readiness; no ML dependency needed."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

UNKNOWN_CLASS = "__unknown__"
SPLITS = ("train", "validation", "test")
# Initial project collection gates, not an accuracy guarantee.
MIN_IMAGES = {"train": 100, "validation": 20, "test": 30}
ONLINE_LICENSES = {
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC-BY-SA-3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
    "CC-BY-SA-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
}


def validate_online_rights(row):
    """Check documented review, not the legal truth of a person's declaration."""
    from urllib.parse import urlparse
    if row.get("license_id") not in ONLINE_LICENSES or row.get("license_url") != ONLINE_LICENSES[row["license_id"]]:
        raise ValueError("Missing supported online license/version evidence")
    for field in ("source_url", "license_source_url"):
        parsed = urlparse(row.get(field, ""))
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError(f"Missing online provenance: {field}")
    for field in ("creator", "attribution", "retrieved_at", "source_image_id", "source_group",
                  "rights_reviewed_by", "rights_review_reference", "model_distribution_review_reference",
                  "identity_reviewed_by", "identity_review_reference"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError(f"Missing online provenance/review: {field}")
    if row.get("identity_reviewed") is not True or row.get("capture_kind") != "online_reference":
        raise ValueError("Online photos require exact-identity review and honest capture provenance")
    # Deployment is a camera task: web packshots cannot establish its holdout accuracy.
    if row["split"] != "train":
        raise ValueError("Online reference photos may seed training, not real-camera holdouts")


def validate_samples(manifest: dict, image_root: Path, catalog: list[dict]) -> list[dict]:
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("samples"), list):
        raise ValueError("Expected schema_version 1 and samples array")
    root = image_root.resolve()
    allowed = {row["id"] for row in catalog if row["trainable"]} | {UNKNOWN_CLASS}
    sessions, bottles, source_groups, source_classes, hashes, paths = {}, {}, {}, {}, set(), set()
    for row in manifest["samples"]:
        identifier = row.get("class_id")
        split = row.get("split")
        if identifier not in allowed or split not in SPLITS:
            raise ValueError("Unknown/non-specific class ID or invalid split")
        if row.get("rights_basis") not in ("self_photographed", "written_authorization", "licensed_online") or not row.get("rights_reference"):
            raise ValueError("Missing documented image rights")
        online = row.get("rights_basis") == "licensed_online"
        if online:
            validate_online_rights(row)
        elif row.get("capture_kind", "real_camera") != "real_camera":
            raise ValueError("Only independent real-camera samples can fill camera holdouts")
        if row.get("training_permitted") is not True or row.get("model_distribution_permitted") is not True:
            raise ValueError("Training and model distribution must be permitted")
        relative = Path(row.get("path", ""))
        candidate = (root / relative).resolve()
        if relative.is_absolute() or not relative.parts or not candidate.is_relative_to(root) or candidate.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            raise ValueError("Image paths must stay inside the private image root")
        if not candidate.is_file():
            raise ValueError(f"Image missing: {relative}")
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest != row.get("sha256") or digest in hashes or candidate in paths:
            raise ValueError("Image checksum mismatch or duplicate image")
        hashes.add(digest)
        paths.add(candidate)
        provenance = [("source_group", source_groups)] if online else [("capture_session", sessions), ("bottle_id", bottles)]
        if not online and row.get("source_group"):
            provenance.append(("source_group", source_groups))
        for field, assignments in provenance:
            key = row.get(field)
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"Missing {field}")
            if key in assignments and assignments[key] != split:
                raise ValueError(f"Leakage: {field} appears in multiple splits")
            assignments[key] = split
            if field == "source_group":
                if key in source_classes and source_classes[key] != identifier:
                    raise ValueError("One source image group cannot have conflicting drink labels")
                source_classes[key] = identifier
    return manifest["samples"]


def readiness(catalog: list[dict], samples: list[dict]) -> dict:
    counts = {row["id"]: {split: 0 for split in SPLITS} for row in catalog}
    counts[UNKNOWN_CLASS] = {split: 0 for split in SPLITS}
    for row in samples:
        counts[row["class_id"]][row["split"]] += 1
    results = []
    for row in catalog:
        current = counts[row["id"]]
        ready = row["trainable"] and all(current[split] >= MIN_IMAGES[split] for split in SPLITS)
        results.append({**row, "image_counts": current,
                        "status": "ready_to_train" if ready else "awaiting_photos" if row["trainable"] else "needs_variant_definition"})
    return {"total_targets": len(results), "ready_to_train": sum(row["status"] == "ready_to_train" for row in results),
            "unknown_counts": counts[UNKNOWN_CLASS], "collection_minima": MIN_IMAGES, "records": results}


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())
