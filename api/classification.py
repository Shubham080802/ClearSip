"""Transparent, label-limited beverage assessment rules.

These rules screen disclosed package facts; they do not diagnose, certify legal
compliance, or make an individual health recommendation.
"""

from __future__ import annotations

import sqlite3
import re
from datetime import date
from pathlib import Path

POLICY_VERSION = "2026.09-us-label-context-v1"
SUGAR_INGREDIENT_PATTERN = re.compile(r"\b(?:sugar|syrup|honey|glucose|fructose|sucrose)\b", re.IGNORECASE)
PRESERVATIVE_TERMS = ("sodium benzoate", "potassium benzoate", "benzoic acid", "potassium sorbate", "calcium sorbate", "sorbic acid", "bha", "bht", "edta")


def claim_status(label: dict) -> tuple[str, str, str]:
    claims = (label["front_label_claims"] or "").casefold()
    ingredients = (label["ingredient_statement"] or "").casefold()
    total_sugar = label["total_sugar_g"]

    if not any(term in claims for term in ("sugar free", "sugar-free", "zero sugar")):
        sugar_free = "not_claimed"
    elif total_sugar is None or not ingredients:
        sugar_free = "not_assessable"
    elif total_sugar >= 0.5 or SUGAR_INGREDIENT_PATTERN.search(ingredients):
        sugar_free = "needs_review"
    else:
        sugar_free = "appears_label_aligned"

    if "preservative free" not in claims and "preservative-free" not in claims and "no preservatives" not in claims:
        preservative_free = "not_claimed"
    elif not ingredients:
        preservative_free = "not_assessable"
    elif any(term in ingredients for term in PRESERVATIVE_TERMS):
        preservative_free = "declared_preservative_detected"
    else:
        preservative_free = "no_declared_preservative_detected"

    healthy = "not_assessable_from_label_alone" if "healthy" in claims else "not_claimed"
    return sugar_free, preservative_free, healthy


def assessment_for(label: dict) -> tuple[str, str, str, str, str, str]:
    sugar_free, preservative_free, healthy = claim_status(label)
    contexts: list[str] = []
    routine_caution = False
    has_caffeine_context = False

    added_sugar = label["added_sugar_g"]
    if added_sugar is not None:
        percent = added_sugar / 50 * 100
        if percent >= 20:
            routine_caution = True
            contexts.append(f"Added sugars: {added_sugar:g} g per serving ({percent:.0f}% of the 50 g Daily Value; high by FDA's general %DV convention).")
        else:
            contexts.append(f"Added sugars: {added_sugar:g} g per serving ({percent:.0f}% of the 50 g Daily Value).")
    else:
        contexts.append("Added sugars: not declared in the available label record.")

    saturated_fat = label["saturated_fat_g"]
    if saturated_fat is not None:
        percent = saturated_fat / 20 * 100
        if percent >= 20:
            routine_caution = True
            contexts.append(f"Saturated fat: {saturated_fat:g} g per serving ({percent:.0f}% of the 20 g Daily Value; high by FDA's general %DV convention).")
        else:
            contexts.append(f"Saturated fat: {saturated_fat:g} g per serving ({percent:.0f}% of the 20 g Daily Value).")

    sodium = label["sodium_mg"]
    if sodium is not None:
        percent = sodium / 2300 * 100
        if percent >= 20:
            routine_caution = True
            contexts.append(f"Sodium: {sodium:g} mg per serving ({percent:.0f}% of the 2,300 mg Daily Value; high by FDA's general %DV convention).")
        else:
            contexts.append(f"Sodium: {sodium:g} mg per serving ({percent:.0f}% of the 2,300 mg Daily Value).")

    caffeine = label["caffeine_mg"]
    if caffeine is not None:
        has_caffeine_context = caffeine > 0
        percent = caffeine / 400 * 100
        contexts.append(f"Caffeine: {caffeine:g} mg per serving ({percent:.0f}% of FDA's 400 mg/day context for most adults, not a personal limit).")
        if caffeine >= 400:
            routine_caution = True
    elif "caffeine" in (label["ingredient_statement"] or "").casefold():
        has_caffeine_context = True
        contexts.append("Caffeine is declared as an ingredient; its amount is not disclosed in the available label record.")

    if added_sugar is None and saturated_fat is None and sodium is None and caffeine is None:
        overall = "more_label_data_needed"
    elif routine_caution:
        overall = "routine_intake_caution"
    elif has_caffeine_context:
        overall = "caffeine_context"
    else:
        overall = "no_label_based_concern_identified"

    summary = "This screen summarizes disclosed package facts and is not medical advice or a legal-compliance finding. " + " ".join(contexts)
    return overall, sugar_free, preservative_free, healthy, " ".join(contexts), summary


def refresh_assessments(database: Path) -> None:
    with sqlite3.connect(database) as conn:
        conn.row_factory = sqlite3.Row
        labels = conn.execute("SELECT * FROM label_versions WHERE is_current = 1").fetchall()
        for row in labels:
            overall, sugar_free, preservative_free, healthy, context, summary = assessment_for(dict(row))
            conn.execute(
                """INSERT OR REPLACE INTO label_assessments
                (label_version_id, overall_status, sugar_free_claim_status, preservative_free_claim_status,
                 healthy_claim_status, frequent_intake_context, summary, policy_version, assessed_on)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (row["id"], overall, sugar_free, preservative_free, healthy, context, summary, POLICY_VERSION, date.today().isoformat()),
            )
