"""Report ingredient availability for every catalog entry and validate sources."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.index import catalog_discoveries, catalog_coverage
from api.source_labels import source_labels


def main():
    rows = catalog_discoveries(limit=500)
    labels = source_labels()
    unknown_ids = set(labels) - {row["id"] for row in rows}
    if unknown_ids:
        raise ValueError(f"Source labels do not match catalog IDs: {sorted(unknown_ids)}")
    coverage = catalog_coverage()
    print("# Catalog ingredient availability audit\n")
    print("All catalog discoveries are checked below. A manufacturer variant panel is distinct from an exact package label.\n")
    print(f"{coverage['total_discoveries']} entries audited; {coverage['with_source_ingredients']} have sourced ingredients; {coverage['missing_source_ingredients']} remain pending.\n")
    print("Pending entries stay visible as catalog leads, but their sizes cannot open an ingredient explanation. Newly added entries use the same rule.\n")
    print("| Catalog ID | Drink | Ingredients | Source |")
    print("| --- | --- | --- | --- |")
    for row in rows:
        label = row["source_label"]
        url = label["source_url"] if label else row["source_url"]
        print(f"| {row['id']} | {row['beverage_family_name']} / {row['variant_name']} | {'Available: manufacturer variant panel' if label else 'Pending: no complete verified ingredient statement'} | [Source]({url}) |")


if __name__ == "__main__":
    main()
