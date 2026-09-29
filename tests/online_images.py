"""Offline tests: source provenance, bounded discovery, and no automatic approval."""
import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.recognition import recognition_catalog
from ml.dataset import validate_samples
from ml.online_images import NoRedirect, audit_catalog, brand_for, candidate_score, download_candidate, front_image, search_url, summary


def product(name="Powerade Grape"):
    return {"code": "0049000079401", "product_name": name, "brands": "Powerade", "countries_tags": ["en:united-states"],
            "quantity": "28oz", "images": {"1": {"uploader": "test-contributor", "uploaded_t": 100,
                "sizes": {"400": {"w": 250, "h": 400}}}, "front_en": {"imgid": "1", "rev": "2"}}}


class OnlineImagesTests(unittest.TestCase):
    def setUp(self):
        self.catalog = recognition_catalog()
        self.target = next(row for row in self.catalog if row["id"] == "powerade-grape")

    def test_all_specific_drinks_have_a_brand_search_and_queries_are_bounded(self):
        self.assertEqual(sum(row["trainable"] for row in self.catalog), 83)
        self.assertTrue(all(brand_for(row) for row in self.catalog if row["trainable"]))
        params = parse_qs(urlparse(search_url("powerade")).query)
        self.assertEqual(params["countries_tags_en"], ["united-states"])
        self.assertEqual(params["page_size"], ["12"])
        self.assertNotIn("search_terms", params)
        for brand, count in (("arbitrary-host", 12), ("powerade", 100)):
            with self.assertRaises(ValueError): search_url(brand, count)

    def test_front_uses_original_provenance_not_multiple_crops(self):
        row = product()
        row["images"]["front_es"] = {"imgid": "1", "rev": "3"}
        image = front_image(row)
        self.assertEqual(image["source_group"], "off:0049000079401:1")
        self.assertEqual(image["creator"], "test-contributor")
        self.assertTrue(image["image_url"].endswith("/004/900/007/9401/1.400.jpg"))
        row["images"]["1"].pop("uploader")
        self.assertIsNone(front_image(row))
        row["code"] = "../../escape"
        self.assertIsNone(front_image(row))

    def test_regular_zero_and_country_conflicts_are_rejected(self):
        self.assertEqual(candidate_score(self.target, product()), 1)
        self.assertIsNone(candidate_score(self.target, product("Powerade ZERO Grape")))
        self.assertIsNone(candidate_score(self.target, product("Powerade Free Grape")))
        foreign = product()
        foreign["countries_tags"] = ["en:france"]
        self.assertIsNone(candidate_score(self.target, foreign))

    def test_audit_includes_every_target_but_never_approves_labels(self):
        result = audit_catalog(self.catalog, {"powerade": {"retrieved_at": "2026-09-28", "data": {"count": 35, "products": [product()]}}})
        self.assertEqual(len(result["records"]), 86)
        row = next(row for row in result["records"] if row["class_id"] == "powerade-grape")
        self.assertFalse(row["source_search_complete"])
        self.assertEqual(row["status"], "metadata_candidates_need_review")
        self.assertFalse(row["candidates"][0]["identity_reviewed"])
        self.assertFalse(row["candidates"][0]["training_permitted"])
        self.assertFalse(row["candidates"][0]["model_distribution_permitted"])
        published = summary(result)
        self.assertEqual(published["approved_training_images"], 0)
        self.assertEqual(published["trained_classes"], 0)
        self.assertNotIn("creator", published["records"][0])
        self.assertEqual(next(r for r in published["records"] if r["class_id"] == "bai")["status"], "needs_variant_definition")

    def test_licensed_images_require_actual_reviews_and_cannot_fill_camera_holdouts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "photo.jpg").write_bytes(b"metadata-unit-test-not-a-training-photo")
            row = {"path": "photo.jpg", "sha256": hashlib.sha256((root / "photo.jpg").read_bytes()).hexdigest(),
                   "class_id": "powerade-grape", "split": "train", "capture_kind": "online_reference",
                   "rights_basis": "licensed_online", "rights_reference": "fixture", "training_permitted": True,
                   "model_distribution_permitted": True, "source_url": "https://world.openfoodfacts.org/product/0049000079401",
                   "license_id": "CC-BY-SA-3.0", "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
                   "license_source_url": "https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/",
                   "creator": "test-contributor", "attribution": "fixture credit", "retrieved_at": "2026-09-28",
                   "source_group": "off:0049000079401:1", "source_image_id": "1", "identity_reviewed": True,
                   "rights_reviewed_by": "test reviewer", "rights_review_reference": "fixture rights review",
                   "model_distribution_review_reference": "fixture intended-distribution review",
                   "identity_reviewed_by": "test reviewer", "identity_review_reference": "fixture exact-variant review"}
            self.assertEqual(len(validate_samples({"schema_version": 1, "samples": [row]}, root, self.catalog)), 1)
            for field, value in (("identity_reviewed", False), ("license_id", "MIT"), ("license_url", "https://example.com"),
                                 ("creator", ""), ("rights_review_reference", ""), ("model_distribution_review_reference", ""),
                                 ("source_group", ""), ("split", "test"), ("split", "validation"), ("training_permitted", False)):
                invalid = {**row, field: value}
                with self.assertRaises(ValueError): validate_samples({"schema_version": 1, "samples": [invalid]}, root, self.catalog)
            (root / "crop.jpg").write_bytes(b"different-unit-test-crop")
            crop = {**row, "path": "crop.jpg", "class_id": "powerade-orange",
                    "sha256": hashlib.sha256((root / "crop.jpg").read_bytes()).hexdigest()}
            with self.assertRaises(ValueError): validate_samples({"schema_version": 1, "samples": [row, crop]}, root, self.catalog)

    def test_unapproved_origins_rejected_before_network(self):
        with self.assertRaises(ValueError): NoRedirect().redirect_request(None, None, 302, "redirect", {}, "http://localhost/private")
        for url in ("https://example.com/photo.jpg", "http://openfoodfacts-images.s3.eu-west-3.amazonaws.com/data/004/900/007/9401/1.400.jpg",
                    "https://openfoodfacts-images.s3.eu-west-3.amazonaws.com/private/secret.jpg"):
            with self.assertRaises(ValueError): download_candidate({"image_url": url}, Path("unused.jpg"))


if __name__ == "__main__":
    unittest.main()
