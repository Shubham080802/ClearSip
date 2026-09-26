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
assert len(catalog_discoveries(limit=100)) == 29
assert catalog_summary() == {"reviewed_package_labels": 2, "catalog_discoveries": 29}

print("API smoke tests passed")
