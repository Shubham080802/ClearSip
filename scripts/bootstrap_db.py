"""Create the local SQLite database and insert intentionally small, reviewed seed data."""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "clearsip.db"
SCHEMA = ROOT / "data" / "schema.sql"
FDA_SWEETENER_SOURCE = "https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food"
FDA_CAFFEINE_SOURCE = "https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much"

PRODUCTS = [
    ("coca-cola-zero-sugar", "Coca-Cola Zero Sugar", "Coca-Cola", "United States", "12 fl oz (355 mL)", 0, 0, 34, "manufacturer_verified", "2026-09-24", "https://www.coca-cola.com/us/en/brands/coca-cola/products/zero"),
    ("monster-zero-sugar", "Monster Energy Zero Sugar", "Monster Energy", "United States", "16 fl oz (473 mL)", 10, 0, 160, "needs_package_verification", "2026-09-24", "https://www.monsterenergy.com/en-us/energy-drinks/monster-energy/zero-sugar/"),
]

INGREDIENTS = [
    ("caffeine", "Caffeine"), ("aspartame", "Aspartame"), ("ace-k", "Acesulfame potassium"),
    ("sucralose", "Sucralose"), ("erythritol", "Erythritol"), ("taurine", "Taurine"),
]

PRODUCT_INGREDIENTS = [
    ("coca-cola-zero-sugar", "aspartame", 1, "High-intensity sweetener", "FDA lists an ADI of 50 mg/kg/day. The label amount is not disclosed, so an intake comparison is unavailable.", "context_matters", FDA_SWEETENER_SOURCE),
    ("coca-cola-zero-sugar", "ace-k", 2, "High-intensity sweetener", "FDA lists an ADI of 15 mg/kg/day. The label amount is not disclosed, so an intake comparison is unavailable.", "context_matters", FDA_SWEETENER_SOURCE),
    ("coca-cola-zero-sugar", "caffeine", 3, "Stimulant", "34 mg per listed serving. FDA's 400 mg/day reference applies to most healthy adults, not every person.", "worth_watching", FDA_CAFFEINE_SOURCE),
    ("monster-zero-sugar", "erythritol", 1, "Sugar alcohol sweetener", "The provisional package transcription lists 2 g per 16 fl oz. A single ingredient does not establish a personalized effect.", "context_matters", None),
    ("monster-zero-sugar", "taurine", 2, "Amino-sulfonic compound", "Common in energy drinks. Do not treat it as a substitute for sleep or nutrition.", "context_matters", None),
    ("monster-zero-sugar", "sucralose", 3, "High-intensity sweetener", "FDA lists an ADI of 5 mg/kg/day. The label amount is not disclosed, so an intake comparison is unavailable.", "context_matters", FDA_SWEETENER_SOURCE),
    ("monster-zero-sugar", "ace-k", 4, "High-intensity sweetener", "FDA lists an ADI of 15 mg/kg/day. The label amount is not disclosed, so an intake comparison is unavailable.", "context_matters", FDA_SWEETENER_SOURCE),
    ("monster-zero-sugar", "caffeine", 5, "Stimulant", "160 mg per listed serving. FDA's 400 mg/day reference applies to most healthy adults, not every person.", "worth_watching", FDA_CAFFEINE_SOURCE),
]


def main() -> None:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE) as conn:
        conn.executescript(SCHEMA.read_text())
        conn.executemany("INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", PRODUCTS)
        conn.executemany("INSERT OR REPLACE INTO ingredients VALUES (?, ?)", INGREDIENTS)
        conn.executemany("INSERT OR REPLACE INTO product_ingredients VALUES (?, ?, ?, ?, ?, ?, ?)", PRODUCT_INGREDIENTS)
    print(f"Seeded {DATABASE}")


if __name__ == "__main__":
    main()
