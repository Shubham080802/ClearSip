"""Import a small, reviewable batch of USDA FDC Branded Foods into local ClearSip SQL.

Use the bulk FDC release for a national backfill; this API importer is for
targeted discovery and incremental refreshes. It intentionally imports label
facts as `catalog_label_match`, not package-verified facts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.classification import refresh_assessments

API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
TODAY = date.today().isoformat()
BEVERAGE_CATEGORY_TERMS = ("beverage", "drink", "soda", "water", "coffee", "tea", "juice", "energy", "sports")


def ssl_context() -> ssl.SSLContext:
    """Use certifi when present, avoiding macOS framework-Python CA gaps."""
    try:
        import certifi
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")[:96] or "unknown"


def split_ingredients(statement: str) -> list[str]:
    """Split top-level comma-separated ingredients without pretending to know a formula."""
    parts, current, depth = [], [], 0
    for char in statement:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(depth - 1, 0)
        if char == "," and depth == 0:
            token = "".join(current).strip(" .")
            if token:
                parts.append(token)
            current = []
        else:
            current.append(char)
    token = "".join(current).strip(" .")
    if token:
        parts.append(token)
    return parts


def nutrient(food: dict, key: str) -> float | None:
    value = (food.get("labelNutrients") or {}).get(key, {}).get("value")
    return float(value) if value is not None else None


def is_likely_non_alcoholic_beverage(food: dict) -> bool:
    """Reject brand-adjacent foods such as candy, gum, and mints."""
    category = (food.get("foodCategory") or "").casefold()
    if not any(term in category for term in BEVERAGE_CATEGORY_TERMS):
        return False
    return "alcohol" not in category or "non alcoholic" in category


def fetch_foods(api_key: str, query: str, page_size: int) -> list[dict]:
    payload = json.dumps({"query": query, "dataType": ["Branded"], "pageSize": page_size}).encode()
    url = f"{API_URL}?{urllib.parse.urlencode({'api_key': api_key})}"
    request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "ClearSip/0.1 research importer"})
    with urllib.request.urlopen(request, timeout=30, context=ssl_context()) as response:
        return json.load(response).get("foods", [])


def import_food(conn: sqlite3.Connection, food: dict) -> bool:
    fdc_id = str(food.get("fdcId") or "")
    description = (food.get("description") or "").strip()
    if not fdc_id or not description:
        return False
    if not is_likely_non_alcoholic_beverage(food):
        return False

    market = food.get("marketCountry") or "Unknown"
    if market not in ("United States", "US", "USA"):
        return False

    manufacturer = (food.get("brandOwner") or food.get("brandName") or "Unknown manufacturer").strip()
    brand = (food.get("brandName") or manufacturer).strip()
    ingredients = (food.get("ingredients") or "").strip()
    gtin = (food.get("gtinUpc") or "").strip() or None
    package_id = f"fdc-{fdc_id}"
    manufacturer_id, family_id, variant_id = f"manufacturer-{slug(manufacturer)}", f"family-{slug(manufacturer)}-{slug(brand)}", f"variant-fdc-{fdc_id}"
    source_id = f"fdc-source-{fdc_id}-{TODAY}"
    label_hash = hashlib.sha256(json.dumps(food, sort_keys=True).encode()).hexdigest()
    label_id = f"fdc-label-{fdc_id}-{label_hash[:12]}"
    package_description = food.get("householdServingFullText") or f"{food.get('servingSize') or 'unknown'} {food.get('servingSizeUnit') or ''}".strip()

    conn.execute("INSERT OR IGNORE INTO manufacturers VALUES (?, ?, ?)", (manufacturer_id, manufacturer, None))
    conn.execute("INSERT OR IGNORE INTO beverage_families VALUES (?, ?, ?)", (family_id, manufacturer_id, brand))
    conn.execute("INSERT OR REPLACE INTO beverage_variants VALUES (?, ?, ?, ?, ?)", (variant_id, family_id, description, None, food.get("foodCategory") or "branded beverage"))
    # FDC's ID is always retained; GTIN is nullable because some records omit it.
    conn.execute("INSERT OR REPLACE INTO product_packages VALUES (?, ?, ?, ?, ?, ?, ?)", (package_id, variant_id, gtin, fdc_id, "United States", package_description, "unknown"))
    conn.execute("INSERT OR REPLACE INTO source_records VALUES (?, ?, ?, ?, ?, ?, ?)", (source_id, "USDA FoodData Central", f"https://fdc.nal.usda.gov/food-details/{fdc_id}/nutrients", "United States", TODAY, "usda_fdc_branded", label_hash))

    current = conn.execute("SELECT id FROM label_versions WHERE package_id = ? AND is_current = 1", (package_id,)).fetchone()
    if current and current[0] != label_id:
        conn.execute("UPDATE label_versions SET is_current = 0 WHERE id = ?", (current[0],))
    conn.execute(
        "INSERT OR REPLACE INTO label_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (label_id, package_id, source_id, package_description, None, nutrient(food, "calories"), nutrient(food, "saturatedFat"), nutrient(food, "sugars"), nutrient(food, "addedSugar"), nutrient(food, "sodium"), None, ingredients or None, None, None, "catalog_label_match", food.get("modifiedDate") or food.get("publishedDate") or TODAY, 1),
    )
    for position, token in enumerate(split_ingredients(ingredients), start=1):
        ingredient_id = f"ingredient-{slug(token)}"
        conn.execute("INSERT OR IGNORE INTO ingredients VALUES (?, ?)", (ingredient_id, token))
        conn.execute("INSERT OR REPLACE INTO label_ingredients VALUES (?, ?, ?, ?, ?, ?, ?)", (label_id, ingredient_id, position, "Declared ingredient", "Declared on the source label. Amount and product-specific effect are not disclosed.", "label_context", None))
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="A focused beverage or brand query, e.g. 'Pepsi Zero Sugar'.")
    parser.add_argument("--page-size", type=int, default=10, choices=range(1, 51))
    parser.add_argument("--api-key", default=os.getenv("FDC_API_KEY"))
    parser.add_argument("--demo", action="store_true", help="Use FDC's low-rate DEMO_KEY for a small exploration only.")
    parser.add_argument("--database", type=Path, default=ROOT / "data" / "clearsip.db")
    args = parser.parse_args()
    api_key = "DEMO_KEY" if args.demo else args.api_key
    if not api_key:
        raise SystemExit("Set FDC_API_KEY or use --demo only for a small exploration. Never commit the key.")
    with sqlite3.connect(args.database) as conn:
        imported = sum(import_food(conn, food) for food in fetch_foods(api_key, args.query, args.page_size))
    refresh_assessments(args.database)
    print(f"Imported {imported} FDC Branded Foods records as catalog_label_match.")


if __name__ == "__main__":
    main()
