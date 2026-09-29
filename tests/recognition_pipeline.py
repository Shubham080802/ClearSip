"""Coverage, data permissions, split leakage, incremental retention, and gates."""
import copy
import hashlib
import sys
import tempfile
import shutil
import os
import sqlite3
import json
import subprocess
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.recognition import recognition_catalog, recognition_summary
from api.index import catalog_discoveries, discovery_detail
from ml.dataset import UNKNOWN_CLASS, preparation_report, readiness, validate_samples
from ml.metrics import evaluate_predictions, require_previous_classes
from scripts.train_recognizer import fit_and_evaluate, training_plan
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

    def test_research_preparation_covers_all_targets_without_claiming_evaluation(self):
        catalog = recognition_catalog()
        report = preparation_report(catalog, [])
        self.assertEqual({row["id"] for row in report["records"]}, {row["id"] for row in catalog} | {UNKNOWN_CLASS})
        self.assertFalse(report["research_training_data_ready"])
        self.assertEqual(report["camera_data_ready_classes"], 0)
        self.assertIsNone(next(row for row in report["records"] if row["id"] == "snapple")["missing_images"])
        self.assertEqual(next(row for row in report["records"] if row["id"] == "pepsi")["missing_images"], {"train":100,"validation":20,"test":30})

    def test_research_training_keeps_permissions_minima_unknowns_and_previous_classes(self):
        catalog = recognition_catalog()
        # These count fixtures test planning only, not accepted photo manifests.
        samples = [{"class_id": label, "split": "train", "source_group": f"{label}:{index}"}
                   for label in ("pepsi", "coca-cola-original", UNKNOWN_CLASS) for index in range(100)]
        labels, audit = training_plan(catalog, samples, mode="research-only")
        self.assertEqual(set(labels), {"pepsi", "coca-cola-original", UNKNOWN_CLASS})
        self.assertTrue(audit["research_training_data_ready"])
        self.assertEqual(audit["camera_data_ready_classes"], 0)
        self.assertEqual(next(row for row in audit["records"] if row["id"] == "pepsi")["source_or_session_groups"]["train"], 100)
        with self.assertRaises(ValueError): training_plan(catalog, samples)
        with self.assertRaises(ValueError): training_plan(catalog, samples[:-1], mode="research-only")
        with self.assertRaises(ValueError): training_plan(catalog, samples, ["sprite", UNKNOWN_CLASS], mode="research-only")
        with self.assertRaises(ValueError): training_plan(catalog, [], mode="research-only")
        with self.assertRaises(ValueError): training_plan(catalog, samples, mode="unsupported")

    def test_research_run_never_reads_holdouts_or_invents_accuracy(self):
        model = Mock()
        def dataset(split):
            self.assertEqual(split, "train", "Deferred camera data must stay untouched")
            return "training dataset"
        threshold, margin, report = fit_and_evaluate(model, dataset, {}, ["pepsi", UNKNOWN_CLASS], 2, "research-only")
        model.fit.assert_called_once_with("training dataset", epochs=2)
        model.predict.assert_not_called()
        self.assertIsNone(threshold)
        self.assertIsNone(margin)
        self.assertFalse(report["passed"])
        self.assertEqual(report["status"], "deferred")
        self.assertEqual(report["per_class"], {})
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory) / "release.json"
            for fields in ({"training_mode":"research-only"}, {"evaluation_status":"deferred"}):
                release.write_text(json.dumps({"status":"validated","validation_passed":True, **fields}))
                with self.assertRaisesRegex(ValueError, "cannot be activated"):
                    check_release(Path(directory))

    def test_empty_research_plan_stops_before_training_dependencies_or_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"schema_version":1,"samples":[]}))
            result = subprocess.run([sys.executable, "scripts/train_recognizer.py", "--manifest", str(manifest),
                                     "--image-root", str(root), "--output", str(root / "candidate"),
                                     "--training-mode", "research-only", "--plan-only"],
                                    cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("quarantine does not count", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertNotIn("tensorflow", result.stderr.lower())
            self.assertFalse((root / "candidate").exists())

    def test_default_training_still_requires_validation_before_test(self):
        labels = ["regular", "zero", UNKNOWN_CLASS]
        truth = [label for label in labels for _ in range(30)]
        scores = [[0.99 if index == labels.index(label) else 0.005 for index in range(3)] for label in truth]
        model = Mock()
        predictions = Mock()
        predictions.tolist.return_value = scores
        model.predict.return_value = predictions
        requested = []
        def dataset(split):
            requested.append(split)
            return split
        split_rows = {split:[{"class_id":label} for label in truth] for split in ("validation","test")}
        threshold, margin, report = fit_and_evaluate(model, dataset, split_rows, labels, 2, "camera-evaluated")
        self.assertTrue(report["passed"])
        self.assertIsNotNone(threshold)
        self.assertIsNotNone(margin)
        self.assertEqual(requested, ["train","validation","validation","test"])
        requested.clear()
        predictions.tolist.return_value = [[0.34,0.33,0.33]] * len(truth)
        with self.assertRaisesRegex(ValueError, "Validation rejection/quality gates failed"):
            fit_and_evaluate(model, dataset, split_rows, labels, 2, "camera-evaluated")
        self.assertNotIn("test", requested, "Failed validation must not consume untouched test data")

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
