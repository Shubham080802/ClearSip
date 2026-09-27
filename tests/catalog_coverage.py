"""Exercise every published discovery and source panel, including the reported gap."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from api.index import catalog_discoveries, catalog_coverage, search_products, product_detail
from api.source_labels import source_labels

rows = catalog_discoveries(limit=500)
labels = source_labels()
assert rows
assert set(labels).issubset({row["id"] for row in rows})
for row in rows:
    label = row["source_label"]
    if label:
        assert label["ingredients"].strip()
        assert label["source_url"].startswith("https://")
        assert label["scope"] == "variant"
        assert label["accessed_on"] and label["publisher"]
        assert label["label_context"]["summary"]
        assert label["discovery_id"] == row["id"]

powerade = next(row for row in rows if row["id"] == "powerade-zero-mixed-berry")
assert powerade["source_label"], "Powerade Zero Mixed Berry must have an explanation"
assert "sucralose" in powerade["source_label"]["ingredients"].lower()
assert powerade["source_label"]["total_sugar_g"] == 0
assert powerade["source_label"]["label_context"]["sugar_free_claim_status"] == "appears_label_aligned"
assert catalog_coverage()["total_discoveries"] == len(rows)
for query in ("Coca", "Monster", "Powerade"):
    for package in search_products(query):
        detail = product_detail(package["id"])
        assert bool(package["has_ingredients"]) == bool(detail["ingredient_statement"].strip())
        assert detail["ingredient_statement"].strip()
assert "phenylalanine" in product_detail("coca-cola-zero-sugar-12oz-us")["source_label"]["notes"].lower()
assert "natural and artificial flavors" not in product_detail("powerade-orange-20oz-us")["source_label"]["ingredients"].lower()
print(f"All {len(rows)} catalog entries audited; {len(labels)} source panels validated")
