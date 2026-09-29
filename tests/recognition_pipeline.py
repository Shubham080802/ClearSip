"""Coverage, data permissions, split leakage, incremental retention, and gates."""
import copy
import hashlib
import sys
import tempfile
import shutil
import os
import sqlite3
import json
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.recognition import recognition_catalog, recognition_summary
from api.index import catalog_discoveries, discovery_detail
from ml.dataset import UNKNOWN_CLASS, readiness, validate_samples
from ml.metrics import evaluate_predictions, require_previous_classes
from scripts.train_recognizer import training_plan
from scripts.check_recognizer_release import check_release


class RecognitionTests(unittest.TestCase):
    def test_new_entries_are_registered_automatically(self):
        from api.database import LOCAL_DATABASE
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "catalog.db"
            shutil.copyfile(LOCAL_DATABASE, destination)
            with sqlite3.connect(destination) as conn:
                conn.execute("INSERT INTO catalog_discoveries VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                             ("future-test", "Test", "Test", "New flavor", "water", "United States", "20 fl oz", "variant", None, "https://example.com", "2026-09-28", "needs_package_verification"))
                conn.executemany("INSERT INTO catalog_discoveries VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                 [(f"more-{index}", "A Test", "A Test", f"Flavor {index}", "water", "United States", "20 fl oz", "variant", None, "https://example.com", "2026-09-28", "needs_package_verification") for index in range(501)])
            with patch.dict(os.environ, {"DATABASE_URL": f"sqlite:///{destination}"}):
                row = next(row for row in recognition_catalog() if row["id"] == "future-test")
                self.assertEqual(row["status"], "awaiting_photos")
                self.assertTrue(row["trainable"])
                self.assertEqual(discovery_detail("future-test")["id"], "future-test", "Exact identity lookup must not stop at a list-page limit")

    def test_candidate_or_false_coverage_cannot_activate(self):
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory) / "release.json"
            release.write_text(json.dumps({"status":"candidate","labels":["pepsi"],"validation_passed":False}))
            with self.assertRaises(ValueError): check_release(Path(directory))
            release.write_text(json.dumps({"status":"awaiting_training_images","labels":["pepsi"],"validation_passed":False}))
            with self.assertRaises(ValueError): check_release(Path(directory))

    def test_every_catalog_entry_is_registered(self):
        rows = recognition_catalog()
        identifiers = {row["discovery_id"] for row in rows}
        self.assertTrue({row["id"] for row in catalog_discoveries(limit=500)} <= identifiers)
        self.assertEqual(len(rows), len({row["id"] for row in rows}))
        self.assertIn("variant:monster-zero-sugar", {row["id"] for row in rows})
        self.assertEqual(sum(row["collection_priority"] == 1 for row in rows), 12)
        self.assertFalse(next(row for row in rows if row["id"] == "snapple")["trainable"])
        self.assertEqual(readiness(rows, [])["ready_to_train"], 0)
        self.assertEqual(recognition_summary()["visual_classes_deployed"], 0)
        self.assertEqual(discovery_detail("powerade-zero-mixed-berry")["id"], "powerade-zero-mixed-berry")

    def test_photo_permissions_duplicates_and_split_leakage(self):
        catalog = recognition_catalog()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.jpg"
            second = root / "second.jpg"
            first.write_bytes(b"test-photo-one")
            second.write_bytes(b"test-photo-two")
            row = {"path": first.name, "class_id": "powerade-zero-mixed-berry", "split": "train",
                   "capture_session": "s1", "bottle_id": "b1", "sha256": hashlib.sha256(first.read_bytes()).hexdigest(),
                   "rights_basis": "self_photographed", "rights_reference": "owner capture record",
                   "training_permitted": True, "model_distribution_permitted": True}
            manifest = {"schema_version": 1, "samples": [row]}
            self.assertEqual(len(validate_samples(manifest, root, catalog)), 1)
            for field, value in (("training_permitted", False), ("model_distribution_permitted", False),
                                 ("sha256", "wrong"), ("path", "../escape.jpg"), ("class_id", "snapple")):
                invalid = copy.deepcopy(manifest)
                invalid["samples"][0][field] = value
                with self.assertRaises(ValueError): validate_samples(invalid, root, catalog)
            with self.assertRaises(ValueError): validate_samples({"schema_version": 1, "samples": [row, row]},root,catalog)
            for field in ("capture_session", "bottle_id"):
                other = {**row, "path": second.name, "sha256": hashlib.sha256(second.read_bytes()).hexdigest(),
                         "split": "test", "capture_session": "s2", "bottle_id": "b2", field: row[field]}
                with self.assertRaises(ValueError): validate_samples({"schema_version":1,"samples":[row,other]},root,catalog)

    def test_training_never_invents_images_or_forgets_previous_classes(self):
        with self.assertRaises(ValueError): training_plan(recognition_catalog(), [])
        with self.assertRaises(ValueError): require_previous_classes(["new",UNKNOWN_CLASS],["old",UNKNOWN_CLASS])
        require_previous_classes(["new","old",UNKNOWN_CLASS],["old",UNKNOWN_CLASS])

    def test_evaluation_is_per_class_and_requires_unknowns(self):
        labels = ["regular", "zero", UNKNOWN_CLASS]
        truth = [label for label in labels for _ in range(30)]
        scores = [[0.99 if index == labels.index(label) else 0.005 for index in range(3)] for label in truth]
        self.assertTrue(evaluate_predictions(labels,truth,scores)["passed"])
        bad = copy.deepcopy(scores)
        bad[30:60] = [[0.99,0.005,0.005]] * 30
        self.assertFalse(evaluate_predictions(labels,truth,bad)["passed"],"a failed flavor cannot hide in aggregate accuracy")
        self.assertFalse(evaluate_predictions(labels,truth[:60],scores[:60])["passed"])
        bad[-30:] = [[0.99,0.005,0.005]] * 30
        self.assertEqual(evaluate_predictions(labels,truth,bad)["unknown_false_accept_rate"],1)


if __name__ == "__main__":
    unittest.main()
