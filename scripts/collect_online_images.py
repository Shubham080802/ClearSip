"""Audit every recognition target using a bounded OFF search; optionally quarantine photos.

This never approves identity/rights, produces training samples, or trains a model.
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from api.recognition import recognition_catalog
from ml.online_images import SourceClient, audit_catalog, brand_for, download_candidate, summary


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "training-data/off-discovery")
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--download-limit", type=int, default=0)
    parser.add_argument("--offline", action="store_true", help="Only use existing source caches")
    parser.add_argument("--only-brand", help="Resume one registered brand; still audit all targets from available caches")
    args = parser.parse_args()
    if not 0 <= args.download_limit <= 30:
        parser.error("Quarantine downloads are capped at 30 per run")
    if not args.output.resolve().is_relative_to((ROOT / "training-data").resolve()):
        parser.error("Source metadata/photos must stay inside ignored training-data/")
    client = SourceClient(args.output / "cache")
    catalog = recognition_catalog()
    searches = {}
    previous_audit = args.output / "audit.json"
    previous_errors = json.loads(previous_audit.read_text()).get("search_errors", {}) if previous_audit.exists() else {}
    access_stopped = False
    brands = sorted({brand_for(target) for target in catalog if target["trainable"]} - {None})
    if args.only_brand and args.only_brand not in brands:
        parser.error("only-brand must be a registered catalog brand")
    for brand in brands:
        from hashlib import sha256
        from ml.online_images import search_url
        cached = client.cache_dir / (sha256(search_url(brand).encode()).hexdigest() + ".json")
        if cached.is_file():
            searches[brand] = json.loads(cached.read_text())
            continue
        if access_stopped:
            searches[brand] = {"not_searched": True}
            continue
        if args.offline or (args.only_brand and brand != args.only_brand):
            if brand in previous_errors:
                searches[brand] = previous_errors[brand]
            continue
        try:
            searches[brand] = client.search(brand)
            data = searches[brand]["data"]
            print(f"{brand}: {len(data['products'])} products inspected of {data.get('count', '?')}", flush=True)
        except Exception as error:
            searches[brand] = {"error": type(error).__name__, "http_status": getattr(error, "code", None)}
            if isinstance(error, HTTPError) and error.code in (401, 403, 429, 503):
                access_stopped = True
            print(f"{brand}: source unavailable ({type(error).__name__}, HTTP {getattr(error, 'code', 'n/a')}); no absence claim", flush=True)
            # No retries/alternative domains to bypass access restrictions.
    audit = audit_catalog(catalog, searches)
    audit["search_errors"] = {brand: result for brand, result in searches.items() if result.get("error")}
    previous_inventory = args.output / "quarantine.json"
    existing_images = json.loads(previous_inventory.read_text()).get("images", []) if previous_inventory.exists() else []
    inventory_records = {row["source_group"]: row for row in existing_images}
    downloads, seen_groups = [], set(inventory_records)
    seen_hashes = {row["sha256"] for row in existing_images}
    for row in sorted(audit["records"], key=lambda row: (row["collection_priority"], row["class_id"])):
        if len(downloads) >= args.download_limit:
            break
        for candidate in row["candidates"][:1]:
            if candidate["source_group"] in seen_groups:
                continue
            seen_groups.add(candidate["source_group"])
            path = args.output / "quarantine" / (candidate["source_group"].replace(":", "-") + ".jpg")
            try:
                if not path.resolve().is_relative_to(args.output.resolve()):
                    raise ValueError("Quarantine paths cannot escape the collection directory")
                result = download_candidate(candidate, path, client.context)
                duplicate = result["sha256"] in seen_hashes
                seen_hashes.add(result["sha256"])
                record = {"suggested_class_id": row["class_id"], **candidate, **result,
                          "exact_duplicate": duplicate, "approved_for_training": False}
                downloads.append(record)
                inventory_records[candidate["source_group"]] = record
                print(f"Quarantined: {row['class_id']} (not approved)", flush=True)
            except Exception as error:
                candidate["download_error"] = type(error).__name__
                print(f"Image unavailable: {row['class_id']} ({type(error).__name__})", flush=True)
            time.sleep(1)
    active_groups = {candidate["source_group"] for row in audit["records"] for candidate in row["candidates"]}
    inventory = {"schema_version": 1,
                 "images": [{**row, "candidate_currently_eligible": group in active_groups} for group, row in inventory_records.items()],
                 "approved_training_images": 0}
    # Retain runs for review/traceability; never overwrite a previously approved manifest.
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    write_json(args.output / "runs" / (run_id + ".json"), {"audit": audit, "quarantine": inventory})
    write_json(args.output / "audit.json", audit)
    write_json(args.output / "quarantine.json", inventory)
    # Deliberately empty: quarantined photos must never flow straight into training.
    manifest = args.output / "manifest.json"
    if not manifest.exists():
        write_json(manifest, {"schema_version": 1, "samples": []})
    result = summary(audit)
    result["source_searches_completed"] = sum("data" in value for value in searches.values())
    result["source_searches_unavailable"] = sum("error" in value for value in searches.values())
    result["quarantined_images"] = len(inventory_records)
    result["new_downloads_this_run"] = len(downloads)
    if args.summary:
        write_json(args.summary, result)
    print(json.dumps({key: value for key, value in result.items() if key != "records"}), flush=True)


if __name__ == "__main__":
    main()
