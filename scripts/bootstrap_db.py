"""Create the local SQLite catalog and insert intentionally small, reviewed seed data."""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "clearsip.db"
SCHEMA = ROOT / "data" / "schema.sql"
FDA_SWEETENER_SOURCE = "https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food"
FDA_CAFFEINE_SOURCE = "https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much"


def main() -> None:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE) as conn:
        # This is a development bootstrap, deliberately rebuilding its disposable local database.
        for table in ("label_ingredients", "label_versions", "source_records", "product_packages", "ingredients", "beverage_variants", "beverage_families", "manufacturers", "product_ingredients", "products"):
            conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.executescript(SCHEMA.read_text())
        conn.executemany("INSERT INTO manufacturers VALUES (?, ?, ?)", [
            ("coca-cola-company", "The Coca-Cola Company", "https://www.coca-colacompany.com/"),
            ("monster-energy", "Monster Energy", "https://www.monsterenergy.com/"),
        ])
        conn.executemany("INSERT INTO beverage_families VALUES (?, ?, ?)", [
            ("coca-cola", "coca-cola-company", "Coca-Cola"), ("monster-energy", "monster-energy", "Monster Energy"),
        ])
        conn.executemany("INSERT INTO beverage_variants VALUES (?, ?, ?, ?, ?)", [
            ("coca-cola-zero-sugar", "coca-cola", "Coca-Cola Zero Sugar", None, "carbonated soft drink"),
            ("monster-zero-sugar", "monster-energy", "Monster Energy Zero Sugar", None, "energy drink"),
        ])
        conn.executemany("INSERT INTO product_packages VALUES (?, ?, ?, ?, ?, ?, ?)", [
            ("coca-cola-zero-sugar-12oz-us", "coca-cola-zero-sugar", None, None, "United States", "12 fl oz can", "active"),
            ("monster-zero-sugar-16oz-us", "monster-zero-sugar", None, None, "United States", "16 fl oz can", "active"),
        ])
        conn.executemany("INSERT INTO source_records VALUES (?, ?, ?, ?, ?, ?, ?)", [
            ("coca-cola-zero-source", "The Coca-Cola Company", "https://www.coca-cola.com/us/en/brands/coca-cola/products/zero", "United States", "2026-09-24", "manufacturer_page", None),
            ("monster-zero-source", "Monster Energy", "https://www.monsterenergy.com/en-us/energy-drinks/monster-energy/zero-sugar/", "United States", "2026-09-24", "manufacturer_page", None),
        ])
        conn.executemany("INSERT INTO label_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            ("coca-cola-zero-2026-09-24", "coca-cola-zero-sugar-12oz-us", "coca-cola-zero-source", "12 fl oz (355 mL)", 0, 0, 34, None, None, "Zero Sugar", "manufacturer_verified", "2026-09-24", 1),
            ("monster-zero-2026-09-24", "monster-zero-sugar-16oz-us", "monster-zero-source", "16 fl oz (473 mL)", 10, 0, 160, None, None, "Zero Sugar", "needs_package_verification", "2026-09-24", 1),
        ])
        conn.executemany("INSERT INTO ingredients VALUES (?, ?)", [
            ("caffeine", "Caffeine"), ("aspartame", "Aspartame"), ("ace-k", "Acesulfame potassium"), ("sucralose", "Sucralose"), ("erythritol", "Erythritol"), ("taurine", "Taurine"),
        ])
        conn.executemany("INSERT INTO label_ingredients VALUES (?, ?, ?, ?, ?, ?, ?)", [
            ("coca-cola-zero-2026-09-24", "aspartame", 1, "High-intensity sweetener", "FDA lists an ADI of 50 mg/kg/day. The label amount is not disclosed, so an intake comparison is unavailable.", "context_matters", FDA_SWEETENER_SOURCE),
            ("coca-cola-zero-2026-09-24", "ace-k", 2, "High-intensity sweetener", "FDA lists an ADI of 15 mg/kg/day. The label amount is not disclosed, so an intake comparison is unavailable.", "context_matters", FDA_SWEETENER_SOURCE),
            ("coca-cola-zero-2026-09-24", "caffeine", 3, "Stimulant", "34 mg per listed serving. FDA's 400 mg/day reference applies to most healthy adults, not every person.", "worth_watching", FDA_CAFFEINE_SOURCE),
            ("monster-zero-2026-09-24", "erythritol", 1, "Sugar alcohol sweetener", "The provisional package transcription lists 2 g per 16 fl oz. A single ingredient does not establish a personalized effect.", "context_matters", None),
            ("monster-zero-2026-09-24", "taurine", 2, "Amino-sulfonic compound", "Common in energy drinks. Do not treat it as a substitute for sleep or nutrition.", "context_matters", None),
            ("monster-zero-2026-09-24", "sucralose", 3, "High-intensity sweetener", "FDA lists an ADI of 5 mg/kg/day. The label amount is not disclosed, so an intake comparison is unavailable.", "context_matters", FDA_SWEETENER_SOURCE),
            ("monster-zero-2026-09-24", "ace-k", 4, "High-intensity sweetener", "FDA lists an ADI of 15 mg/kg/day. The label amount is not disclosed, so an intake comparison is unavailable.", "context_matters", FDA_SWEETENER_SOURCE),
            ("monster-zero-2026-09-24", "caffeine", 5, "Stimulant", "160 mg per listed serving. FDA's 400 mg/day reference applies to most healthy adults, not every person.", "worth_watching", FDA_CAFFEINE_SOURCE),
        ])
    print(f"Seeded {DATABASE}")


if __name__ == "__main__":
    main()
