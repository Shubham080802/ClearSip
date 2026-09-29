"""Print full-catalog photo readiness, including new SQL/catalog records."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.recognition import recognition_catalog
from ml.dataset import load_manifest, preparation_report, readiness, validate_samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--image-root", type=Path)
    parser.add_argument("--preparation", action="store_true", help="Report train-only readiness and per-target collection gaps, without ML imports")
    args = parser.parse_args()
    if bool(args.manifest) != bool(args.image_root):
        parser.error("Supply both --manifest and --image-root")
    catalog = recognition_catalog()
    samples = validate_samples(load_manifest(args.manifest), args.image_root, catalog) if args.manifest else []
    report = preparation_report(catalog, samples) if args.preparation else readiness(catalog, samples)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
