"""Bounded OFF discovery. Metadata matches are candidates, never training labels."""
from __future__ import annotations

import hashlib
import json
import re
import ssl
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

import certifi

API = "https://world.openfoodfacts.org/api/v2/search"
AWS = "https://openfoodfacts-images.s3.eu-west-3.amazonaws.com/data"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/3.0/"
LICENSE_SOURCE = "https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/"
USER_AGENT = "ClearSip/0.1 (https://github.com/Shubham080802/ClearSip)"
FIELDS = "code,product_name,product_name_en,brands,countries_tags,quantity,images"
BRANDS = {
    "aquafina": "aquafina", "dasani": "dasani", "coca-cola": "coca-cola",
    "diet-pepsi": "pepsi", "pepsi": "pepsi", "dr-pepper": "dr-pepper",
    "dunkin": "dunkin", "gatorade": "gatorade", "hint": "hint",
    "la-colombe": "la-colombe", "monster": "monster", "variant:monster": "monster",
    "mountain-dew": "mountain-dew", "oatly": "oatly", "ocean-spray": "ocean-spray",
    "olipop": "olipop", "powerade": "powerade", "red-bull": "red-bull",
    "seven-up": "7up", "sprite": "sprite", "starbucks": "starbucks",
    "stok": "stok", "v8": "v8", "waterloo": "waterloo",
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Collection redirects require explicit source review")


def fetch(url, context, limit, timeout):
    opener = build_opener(HTTPSHandler(context=context), NoRedirect())
    with opener.open(Request(url, headers={"User-Agent": USER_AGENT}), timeout=timeout) as response:
        content = response.read(limit + 1)
    if len(content) > limit:
        raise ValueError("Source response exceeds the collection bound")
    return content


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def tokens(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return set(re.findall(r"[a-z0-9]+", text))


def brand_for(target):
    return next((brand for prefix, brand in BRANDS.items()
                 if target["id"] == prefix or target["id"].startswith(prefix + "-")), None)


def search_url(brand, page_size=12):
    if brand not in set(BRANDS.values()) or not 1 <= page_size <= 12:
        raise ValueError("Use a registered brand and at most 12 products per query")
    return API + "?" + urlencode({"brands_tags": brand, "countries_tags_en": "united-states",
                                  "page": 1, "page_size": page_size, "fields": FIELDS})


class SourceClient:
    def __init__(self, cache_dir: Path, interval=7.0):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.interval = max(7.0, interval)  # Below the documented 10 searches/minute.
        self.last_request = 0.0
        self.context = ssl.create_default_context(cafile=certifi.where())

    def search(self, brand):
        url = search_url(brand)
        cache = self.cache_dir / (hashlib.sha256(url.encode()).hexdigest() + ".json")
        if cache.exists():
            return json.loads(cache.read_text())
        time.sleep(max(0, self.interval - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        payload = fetch(url, self.context, 5_000_000, 30)
        data = json.loads(payload)
        if not isinstance(data.get("products"), list) or len(data["products"]) > 12:
            raise ValueError("Unexpected search response; no candidate labels accepted")
        result = {"retrieved_at": utc_now(), "request_url": url, "data": data}
        cache.write_text(json.dumps(result, indent=2) + "\n")
        return result


def front_image(product):
    """Use one raw original behind a selected front; never count its crops twice."""
    code = str(product.get("code", ""))
    if not re.fullmatch(r"\d{8}|\d{12,14}", code):
        return None
    images = product.get("images") or {}
    selected = images.get("front_en") or next((v for k, v in sorted(images.items()) if k.startswith("front_")), {})
    raw_id = str(selected.get("imgid", ""))
    raw = images.get(raw_id, {})
    size = (raw.get("sizes") or {}).get("400") or {}
    if not raw_id.isdigit() or not raw.get("uploader") or min(size.get("w", 0), size.get("h", 0)) < 80:
        return None
    padded = code.zfill(13)
    folder = "/".join((padded[:3], padded[3:6], padded[6:9], padded[9:]))
    return {"source_group": f"off:{code}:{raw_id}", "source_image_id": raw_id,
            "image_url": f"{AWS}/{folder}/{raw_id}.400.jpg",
            "creator": raw["uploader"], "uploaded_t": raw.get("uploaded_t"),
            "width": size["w"], "height": size["h"]}


def candidate_score(target, product):
    if "en:united-states" not in (product.get("countries_tags") or []):
        return None
    name = product.get("product_name_en") or product.get("product_name") or ""
    expected, actual = tokens(target["name"]), tokens(name + " " + product.get("brands", ""))
    # Don't substitute regular for zero/diet or decaf for caffeinated coffee.
    for flag in ("zero", "diet", "decaf", "unsweetened"):
        if (flag in expected) != (flag in actual):
            return None
    if actual & {"free", "light", "sugarless"} and not expected & {"zero", "diet", "free", "light", "sugarless"}:
        return None
    if "ultra" in expected and "ultra" not in actual:
        return None
    optional = {"original", "purified", "water", "sugar", "chilled", "flavored", "multi", "serve", "6", "g", "fiber"}
    distinctive = expected - optional
    overlap = len(distinctive & actual) / max(1, len(distinctive))
    return overlap if overlap >= 0.65 else None


def audit_catalog(catalog, searches):
    rows = []
    for target in catalog:
        brand = brand_for(target)
        search = searches.get(brand, {})
        data = search.get("data", {})
        candidates = []
        for product in data.get("products", []):
            score = candidate_score(target, product)
            image = front_image(product)
            if score is None or image is None:
                continue
            code = str(product["code"])
            page = f"https://world.openfoodfacts.org/product/{code}"
            candidates.append({**image, "code": code, "product_name": product.get("product_name_en") or product.get("product_name"),
                "quantity": product.get("quantity"), "metadata_similarity": score,
                "source_url": page, "retrieved_at": search["retrieved_at"],
                "license_id": "CC-BY-SA-3.0", "license_url": LICENSE_URL,
                "license_source_url": LICENSE_SOURCE,
                "attribution": f"Open Food Facts / {image['creator']} — {page} — CC BY-SA 3.0",
                "identity_reviewed": False, "training_permitted": False,
                "model_distribution_permitted": False, "review_status": "pending_identity_and_rights_review"})
        candidates.sort(key=lambda row: (-row["metadata_similarity"], row["code"]))
        status = ("needs_variant_definition" if not target["trainable"] else "unsupported_brand" if not brand
                  else "not_searched_source_unavailable" if search.get("not_searched")
                  else "source_unavailable" if search.get("error") else "not_searched" if not data
                  else "metadata_candidates_need_review" if candidates else "no_candidate_in_bounded_search")
        rows.append({"class_id": target["id"], "name": target["name"], "collection_priority": target["collection_priority"],
                     "status": status, "source_search_complete": bool(data) and data.get("count", 0) <= len(data.get("products", [])),
                     "source_total_products": data.get("count"), "candidates": candidates[:3]})
    return {"schema_version": 1, "audited_at": utc_now(), "source": "Open Food Facts",
            "metadata_license": "ODbL-1.0", "image_license": "CC-BY-SA-3.0",
            "source_url": LICENSE_SOURCE, "trained_classes": 0, "records": rows}


def summary(audit):
    # Publish our audit outcomes, not the third-party product database or photos.
    rows = [{"class_id": row["class_id"], "status": row["status"], "candidate_count": len(row["candidates"]),
             "source_search_complete": row["source_search_complete"]} for row in audit["records"]]
    return {"schema_version": 1, "audited_at": audit["audited_at"], "source": audit["source"],
            "source_url": audit["source_url"], "target_count": len(rows),
            "targets_with_metadata_candidates": sum(row["candidate_count"] > 0 for row in rows),
            "approved_training_images": 0, "trained_classes": 0,
            "notice": "Bounded first-page discovery only. Candidates are not verified labels or legal clearance. No-match is not proof of no available photos.",
            "records": rows}


def download_candidate(candidate, destination: Path, context=None):
    """Quarantine a bounded JPEG from the documented AWS host, not arbitrary URLs."""
    url = candidate["image_url"]
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "openfoodfacts-images.s3.eu-west-3.amazonaws.com" or not re.fullmatch(r"/data/\d{3}/\d{3}/\d{3}/\d{4,5}/\d+\.400\.jpg", parsed.path):
        raise ValueError("Unapproved image origin/path")
    content = fetch(url, context or ssl.create_default_context(cafile=certifi.where()), 2_000_000, 20)
    if not content.startswith(b"\xff\xd8\xff"):
        raise ValueError("Image is not a bounded JPEG")
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(content).hexdigest()
    if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
        raise ValueError("Never overwrite changed source images; use a new collection run")
    destination.write_bytes(content)
    return {"path": str(destination), "sha256": digest, "bytes": len(content)}
