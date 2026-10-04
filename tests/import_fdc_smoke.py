"""Exercise the FDC importer without downloading or writing production data."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.classification import refresh_assessments
from api.database import connection
from api.index import product_by_gtin
from scripts.import_fdc import import_food
from scripts.migrate_db import apply_migrations

sample = {
    "fdcId": 987654,
    "description": "Example Energy Zero Sugar",
    "brandOwner": "Example Beverage Co.",
    "brandName": "Example Energy",
    "foodCategory": "Energy Drinks",
    "marketCountry": "United States",
    "gtinUpc": "012345678905",
    "householdServingFullText": "12 fl oz can",
    "ingredients": "Carbonated water, caffeine, sucralose",
    "modifiedDate": "2026-09-26",
    "labelNutrients": {"calories": {"value": 10}, "sugars": {"value": 0}, "sodium": {"value": 35}},
}

with tempfile.TemporaryDirectory() as directory:
    database = Path(directory) / "fdc-import.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{database}"
    apply_migrations()
    with connection() as conn:
        assert import_food(conn, sample)
        # The migrated catalog already owns these names under stable IDs.
        assert import_food(conn, {
            **sample, "fdcId": 987655, "brandOwner": "PepsiCo",
            "brandName": "Gatorade", "description": "Gatorade Test Flavor",
            "gtinUpc": "099999999999",
        })
        reused = conn.execute(
            "SELECT bf.manufacturer_id, bv.family_id FROM beverage_variants bv "
            "JOIN beverage_families bf ON bf.id = bv.family_id WHERE bv.id = ?",
            ("variant-fdc-987655",),
        ).fetchone()
        assert dict(reused) == {"manufacturer_id": "pepsico", "family_id": "gatorade"}
        # A new FDC record must never replace or duplicate a reviewed package.
        reviewed_before = conn.execute(
            "SELECT id, variant_id, gtin FROM product_packages WHERE id = ?",
            ("gatorade-cool-blue-20oz-us",),
        ).fetchone()
        assert not import_food(conn, {
            **sample, "fdcId": 987656, "description": "Wrong Gatorade Match",
            "gtinUpc": "052000324815",  # UPC form of the reviewed GTIN-14.
        })
        reviewed_after = conn.execute(
            "SELECT id, variant_id, gtin FROM product_packages WHERE id = ?",
            ("gatorade-cool-blue-20oz-us",),
        ).fetchone()
        assert dict(reviewed_after) == dict(reviewed_before)
        assert conn.execute("SELECT id FROM product_packages WHERE id = ?", ("fdc-987656",)).fetchone() is None
        refresh_assessments(conn)
        package = conn.execute("SELECT fdc_id, package_description FROM product_packages WHERE id = ?", ("fdc-987654",)).fetchone()
        label = conn.execute("SELECT verification_status, is_current FROM label_versions WHERE package_id = ?", ("fdc-987654",)).fetchone()
        assessment = conn.execute(
            """SELECT overall_status FROM label_assessments
            WHERE label_version_id = (SELECT id FROM label_versions WHERE package_id = ?)""",
            ("fdc-987654",),
        ).fetchone()
    barcode_match = product_by_gtin("012345678905")

assert package["fdc_id"] == "987654"
assert package["package_description"] == "12 fl oz can"
assert label["verification_status"] == "catalog_label_match"
assert label["is_current"] == 1
assert assessment["overall_status"] == "caffeine_context"
assert barcode_match["id"] == "fdc-987654"
assert barcode_match["package_evidence"]["gtin_linked"]
assert not barcode_match["package_evidence"]["label_verified"]

print("FDC importer smoke tests passed")
