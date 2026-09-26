"""Small end-to-end check of the seeded API catalog and label classifier."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, "scripts/bootstrap_db.py"], cwd=ROOT, check=True)

sys.path.insert(0, str(ROOT))
from api.index import catalog_discoveries, catalog_summary, product_detail, search_products

coke = product_detail("coca-cola-zero-sugar-12oz-us")
monster = product_detail("monster-zero-sugar-16oz-us")

assert coke["total_sugar_g"] == 0
assert coke["label_context"]["sugar_free_claim_status"] == "appears_label_aligned"
assert coke["label_context"]["overall_status"] == "caffeine_context"
assert monster["label_context"]["overall_status"] == "caffeine_context"
assert "40% of FDA" in monster["label_context"]["frequent_intake_context"]
assert len(search_products("Coca")) == 1
assert search_products("Monster Zero Sugar")[0]["display_name"] == "Monster Energy Zero Sugar"
assert len(catalog_discoveries(limit=100)) == 85
assert len(catalog_discoveries(query="Pepsi", limit=100)) == 8
assert catalog_discoveries(query="Pepsi Zero", limit=100)[0]["variant_name"] == "Pepsi Zero Sugar"
coffee = catalog_discoveries(query="La Colombe Triple", limit=100)[0]
assert coffee["variant_name"] == "La Colombe Triple Draft Latte"
assert coffee["observed_package_sizes"] == "9 fl oz can"
energy = catalog_discoveries(query="V8 Energy Peach", limit=100)[0]
assert energy["variant_name"] == "Peach Mango"
assert energy["observed_package_sizes"] == "8 fl oz can (237 mL)"
assert catalog_summary() == {"reviewed_package_labels": 2, "catalog_discoveries": 85}

print("API smoke tests passed")
