"""Versioned reference evidence, separate from manufacturer formula/nutrition facts."""
import json
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse


@lru_cache(maxsize=1)
def ingredient_effect_profiles():
    payload = json.loads((Path(__file__).resolve().parents[1] / "data/ingredient-effects.json").read_text())
    if payload.get("schema_version") != 1 or not payload.get("version") or not payload.get("review_status"):
        raise ValueError("Missing ingredient-effect version/scope")
    identifiers = set()
    for row in payload["profiles"]:
        if row["id"] in identifiers or not all(row.get(key) for key in ("id", "pattern", "role", "function", "body_effect", "intake_context", "source_ids")):
            raise ValueError("Incomplete or duplicate ingredient-effect profile")
        identifiers.add(row["id"])
        re.compile(row["pattern"])
        if row.get("exclude_pattern"):
            re.compile(row["exclude_pattern"])
        if row["evidence_level"] not in ("guidance", "limited"):
            raise ValueError("Invalid evidence scope")
        for source_id in row["source_ids"]:
            source = payload["sources"][source_id]
            parsed = urlparse(source["url"])
            if parsed.scheme != "https" or not parsed.hostname or not source.get("title") or not source.get("accessed_on"):
                raise ValueError("Incomplete source provenance")
    return payload
