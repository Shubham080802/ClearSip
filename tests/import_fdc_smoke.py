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
        refresh_assessments(conn)
        package = conn.execute("SELECT fdc_id, package_description FROM product_packages WHERE id = ?", ("fdc-987654",)).fetchone()
        label = conn.execute("SELECT verification_status, is_current FROM label_versions WHERE package_id = ?", ("fdc-987654",)).fetchone()
        assessment = conn.execute(
            """SELECT overall_status FROM label_assessments
            WHERE label_version_id = (SELECT id FROM label_versions WHERE package_id = ?)""",
            ("fdc-987654",),
        ).fetchone()

assert package["fdc_id"] == "987654"
assert package["package_description"] == "12 fl oz can"
assert label["verification_status"] == "catalog_label_match"
assert label["is_current"] == 1
assert assessment["overall_status"] == "caffeine_context"

print("FDC importer smoke tests passed")
