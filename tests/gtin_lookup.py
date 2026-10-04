"""Exact package lookups accept equivalent UPC/EAN/GTIN representations."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.index import product_by_gtin
from scripts.migrate_db import apply_migrations

with tempfile.TemporaryDirectory(prefix="clearsip-gtin-test-") as directory:
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(directory) / 'catalog.db'}"
    apply_migrations()
    for code in ("00052000324815", "0052000324815", "052000324815"):
        assert product_by_gtin(code)["id"] == "gatorade-cool-blue-20oz-us", code
    assert [item["name"] for item in product_by_gtin("00052000324815")["ingredients"]] == [
        "Water", "Sugar", "Dextrose", "Citric acid", "Natural and artificial flavor",
        "Salt", "Sodium citrate", "Monopotassium phosphate", "Modified food starch",
        "Glycerol ester of rosin", "Blue 1",
    ]

print("Equivalent package GTIN lookup passed")
