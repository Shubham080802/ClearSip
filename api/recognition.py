"""Catalog-wide visual recognition targets; registration is not model coverage."""
from __future__ import annotations

import re
import json
from pathlib import Path

from api.database import connection
from api.source_labels import source_labels

FAMILY_LEADS = {"snapple", "bai", "lacroix"}
PILOT_IDS = {
    "coca-cola-original", "coca-cola-zero", "coca-cola-cherry", "pepsi", "diet-pepsi",
    "pepsi-zero", "sprite-original", "powerade-grape", "powerade-orange",
    "powerade-zero-mixed-berry", "gatorade-cool-blue", "variant:monster-zero-sugar",
}


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def recognition_catalog() -> list[dict]:
    """Include discoveries and package-only variants, deduplicated by name/market."""
    labels = source_labels()
    with connection() as conn:
        discoveries = [dict(row) for row in conn.execute("SELECT id, beverage_family_name, variant_name, market, source_url FROM catalog_discoveries ORDER BY id").fetchall()]
        packages = [dict(row) for row in conn.execute("""
            SELECT bv.id AS variant_id, bv.display_name, pp.id AS package_id,
                   pp.market, pp.gtin, pp.package_description
            FROM product_packages pp JOIN beverage_variants bv ON bv.id = pp.variant_id
            ORDER BY bv.id, pp.id
        """).fetchall()]
    records = {}
    identities = {}
    for row in discoveries:
        identifier = row["id"]
        source = labels.get(identifier)
        name = source["name"] if source else row["variant_name"]
        if not source and normalized(row["beverage_family_name"]).split()[0] not in normalized(name).split():
            name = f"{row['beverage_family_name']} {name}"
        record = {"id": identifier, "name": name, "market": row["market"],
                  "discovery_id": identifier, "package_ids": [], "gtins": [],
                  "trainable": identifier not in FAMILY_LEADS,
                  "collection_priority": 1 if identifier in PILOT_IDS else 2,
                  "status": "needs_variant_definition" if identifier in FAMILY_LEADS else "awaiting_photos",
                  "source_url": row["source_url"]}
        records[identifier] = record
        identities[(normalized(name), row["market"])] = identifier
        identities[(normalized(row["variant_name"]), row["market"])] = identifier
    for row in packages:
        key = (normalized(row["display_name"]), row["market"])
        identifier = identities.get(key, f"variant:{row['variant_id']}")
        if identifier not in records:
            records[identifier] = {"id": identifier, "name": row["display_name"], "market": row["market"],
                                   "discovery_id": None, "package_ids": [], "gtins": [], "trainable": True,
                                   "collection_priority": 1 if identifier in PILOT_IDS else 2,
                                   "status": "awaiting_photos", "source_url": None}
            identities[key] = identifier
        records[identifier]["package_ids"].append(row["package_id"])
        if row["gtin"]:
            records[identifier]["gtins"].append(row["gtin"])
    return sorted(records.values(), key=lambda row: row["id"])


def recognition_summary() -> dict:
    rows = recognition_catalog()
    path = Path(__file__).resolve().parents[1] / "public/models/drink-recognizer/release.json"
    try:
        release = json.loads(path.read_text())
    except (OSError, ValueError):
        release = {}
    trained = set(release.get("labels", [])) - {"__unknown__"} if release.get("status") == "validated" and release.get("validation_passed") is True else set()
    eligible = {row["id"] for row in rows if row["trainable"]}
    trained &= eligible
    for row in rows:
        if row["id"] in trained:
            row["status"] = "visual_model_ready"
    return {"total_targets": len(rows), "concrete_variants": sum(row["trainable"] for row in rows),
            "family_leads": sum(not row["trainable"] for row in rows),
            "visual_model_status": "validated" if trained else "awaiting_training_images", "visual_classes_deployed": len(trained),
            "records": rows}
