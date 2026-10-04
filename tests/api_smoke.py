"""Small end-to-end check of the seeded API catalog and label classifier."""

from __future__ import annotations

import atexit
import os
import subprocess
import sys
from tempfile import TemporaryDirectory
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
temporary_catalog = TemporaryDirectory(prefix="clearsip-api-smoke-")
atexit.register(temporary_catalog.cleanup)
database = Path(temporary_catalog.name) / "catalog.db"
os.environ["DATABASE_URL"] = f"sqlite:///{database}"
subprocess.run([sys.executable, "scripts/bootstrap_db.py", "--database", str(database)], cwd=ROOT, check=True)

sys.path.insert(0, str(ROOT))
from api.index import catalog_discoveries, catalog_summary, product_by_gtin, product_detail, search_products

coke = product_detail("coca-cola-zero-sugar-12oz-us")
monster = product_detail("monster-zero-sugar-16oz-us")

assert coke["total_sugar_g"] == 0
assert coke["label_context"]["sugar_free_claim_status"] == "appears_label_aligned"
assert coke["label_context"]["overall_status"] == "caffeine_context"
assert monster["label_context"]["overall_status"] == "caffeine_context"
assert "40% of FDA" in monster["label_context"]["frequent_intake_context"]
assert len(search_products("Coca")) == 1
assert search_products("Monster Zero Sugar")[0]["display_name"] == "Monster Energy Zero Sugar"
assert search_products("Powerade Grape")[0]["display_name"] == "Powerade Grape"
powerade = product_detail("powerade-grape-20oz-us")
assert powerade["label_context"]["overall_status"] == "routine_intake_caution"
assert powerade["added_sugar_g"] == 21
assert any(item["name"] == "High fructose corn syrup" for item in powerade["ingredients"])
assert len(catalog_discoveries(limit=100)) == 85
assert len(catalog_discoveries(query="Pepsi", limit=100)) == 8
assert catalog_discoveries(query="Pepsi Zero", limit=100)[0]["variant_name"] == "Pepsi Zero Sugar"
coffee = catalog_discoveries(query="La Colombe Triple", limit=100)[0]
assert coffee["variant_name"] == "La Colombe Triple Draft Latte"
assert coffee["observed_package_sizes"] == "9 fl oz can"
energy = catalog_discoveries(query="V8 Energy Peach", limit=100)[0]
assert energy["variant_name"] == "Peach Mango"
assert energy["observed_package_sizes"] == "8 fl oz can (237 mL)"
gatorade = product_by_gtin("00052000324815")
assert gatorade["id"] == "gatorade-cool-blue-20oz-us"
assert gatorade["package_evidence"]["label_verified"]
assert gatorade["servings_per_container"] == 1
assert gatorade["total_sugar_g"] == 35 and gatorade["added_sugar_g"] == 35
assert gatorade["sodium_mg"] == 270 and gatorade["caffeine_mg"] == 0
assert gatorade["label_context"]["overall_status"] == "routine_intake_caution"
assert not coke["package_evidence"]["label_verified"]
summary = catalog_summary()
assert summary["reviewed_package_labels"] == 6
assert summary["verified_package_labels"] == 1
assert summary["gtin_linked_packages"] == 1
assert summary["catalog_discoveries"] == 85
assert summary["source_ingredient_panels"] + summary["pending_ingredient_panels"] == 85

print("API smoke tests passed")
