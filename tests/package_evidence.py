"""Package records and barcode links must not silently certify a formula."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.package_evidence import package_evidence

row = {"verification_status": "manufacturer_verified", "source_type": "manufacturer_page",
       "gtin": None, "label_version_id": "v1"}
assert package_evidence(row) == {
    "label_scope": "variant_or_unconfirmed", "label_verified": False, "gtin_linked": False,
    "label_version_id": "v1", "verification_status": "manufacturer_verified", "source_type": "manufacturer_page",
}
assert not package_evidence({**row, "gtin": "012345678905"})["label_verified"]
assert not package_evidence({**row, "verification_status": "package_verified"})["label_verified"]
assert package_evidence({**row, "verification_status": "package_verified",
                         "source_type": "package_observation"})["label_verified"]
assert package_evidence({**row, "verification_status": "package_verified",
                         "source_type": "manufacturer_label"})["label_verified"]
assert not package_evidence({**row, "verification_status": "catalog_label_match",
                             "source_type": "usda_fdc_branded"})["label_verified"]
print("package evidence scope tests passed")
