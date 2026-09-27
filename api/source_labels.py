"""Curated manufacturer variant labels shipped with each catalog release.

These source snapshots supplement SQL package records. A manufacturer variant
panel is useful without certifying that every container size has that label.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from api.classification import POLICY_VERSION, assessment_for

DATA = Path(__file__).resolve().parents[1] / "data"
NUTRIENTS = ("calories", "total_sugar_g", "added_sugar_g", "sodium_mg", "caffeine_mg")


@lru_cache(maxsize=1)
def source_labels() -> dict[str, dict]:
    records = {}
    for path in sorted(DATA.glob("reviewed-labels-*.json")):
        for row in json.loads(path.read_text()):
            identifier = row["discovery_id"]
            if identifier in records:
                raise ValueError(f"Duplicate source label: {identifier}")
            if row.get("scope") != "variant" or not row.get("ingredients", "").strip():
                raise ValueError(f"Missing scoped ingredients: {identifier}")
            if not row.get("source_url", "").startswith("https://") or not row.get("publisher"):
                raise ValueError(f"Missing source provenance: {identifier}")
            for key in NUTRIENTS:
                value = row.get(key)
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0):
                    raise ValueError(f"Invalid {key}: {identifier}")
            if any(row.get(key) is not None for key in NUTRIENTS) and not row.get("serving"):
                raise ValueError(f"Nutrients without a serving: {identifier}")
            records[identifier] = row
    return records


def explain_source(row: dict) -> dict:
    label = {**{key: row.get(key) for key in NUTRIENTS}, "saturated_fat_g": None,
             "ingredient_statement": row["ingredients"], "front_label_claims": row.get("front_label_claims")}
    overall, sugar, preservative, healthy, context, summary = assessment_for(label)
    return {**row, "label_context": {
        "overall_status": overall, "sugar_free_claim_status": sugar,
        "preservative_free_claim_status": preservative, "healthy_claim_status": healthy,
        "frequent_intake_context": context, "summary": summary, "policy_version": POLICY_VERSION,
    }, "ingredient_functions": ingredient_functions(row["ingredients"])}


def ingredient_functions(statement: str) -> list[dict]:
    # Describe only declared functions; amounts and personal health effects are
    # not inferred from the ingredient name. The full statement remains visible.
    roles = [
        (r"high fructose corn syrup|cane sugar|\bsugar\b|\bhoney\b|\bglucose\b", "Sugar sources", "The ingredient statement names a sugar source. Use the declared total and added sugar amounts for intake context."),
        (r"sucralose|acesulfame|aspartame|stevia|steviol|monk fruit", "Sweeteners", "The statement names a sweetener used in place of or alongside sugar. Its presence alone does not disclose the amount or predict an individual response."),
        (r"\bcaffeine\b", "Caffeine", "Caffeine is declared. Where the source provides an amount, it is shown per listed serving above."),
        (r"natural[^,;]*flavor|artificial[^,;]*flavor", "Flavorings", "The source uses a collective flavoring name; it does not identify every flavor compound or its amount."),
        (r"citric acid|malic acid|phosphoric acid", "Acidity ingredients", "These declared acids contribute tartness or acidity. Their names alone do not establish a health effect."),
        (r"sodium benzoate|potassium benzoate|potassium sorbate|sorbic acid|benzoic acid", "Preservatives", "The statement includes a preservative ingredient. An ingredient name does not disclose its concentration."),
        (r"\bedta\b", "Color-protection ingredient", "Calcium disodium EDTA is declared in this statement. Check the source for its stated function and any disclosed amount."),
        (r"\b(?:red|blue|yellow)\s*\d+|caramel color", "Color additives", "The source declares color additives. The ingredient statement does not by itself quantify exposure."),
        (r"\belectrolytes\b|sodium citrate|potassium phosphate|magnesium chloride", "Mineral salts", "Mineral salts are declared. Check the nutrition panel for the amount of sodium and other disclosed minerals."),
    ]
    return [{"name": name, "context": context} for pattern, name, context in roles if re.search(pattern, statement, re.I)]
