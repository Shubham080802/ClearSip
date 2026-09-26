"""Create the local SQLite catalog and insert intentionally small, reviewed seed data."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATABASE = ROOT / "data" / "clearsip.db"
SCHEMA = ROOT / "data" / "schema.sql"
FDA_SWEETENER_SOURCE = "https://www.fda.gov/food/food-additives-petitions/aspartame-and-other-sweeteners-food"
FDA_CAFFEINE_SOURCE = "https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much"


def main() -> None:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE) as conn:
        # This is a development bootstrap, deliberately rebuilding its disposable local database.
        for table in ("label_assessments", "label_ingredients", "ingredient_profiles", "label_versions", "source_records", "catalog_discoveries", "product_packages", "ingredients", "beverage_variants", "beverage_families", "manufacturers", "product_ingredients", "products"):
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
        conn.executemany("INSERT INTO catalog_discoveries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            ("coca-cola-original", "The Coca-Cola Company", "Coca-Cola", "Coca-Cola Original", "carbonated soft drink", "United States", "7.5, 8, 12, 16, 16.9, 20 fl oz; 1.25, 2 L", "variant", None, "https://www.coca-cola.com/us/en/brands/coca-cola/products/original", "2026-09-24", "needs_package_verification"),
            ("coca-cola-zero", "The Coca-Cola Company", "Coca-Cola", "Coca-Cola Zero Sugar", "carbonated soft drink", "United States", "7.5, 8, 12, 16, 16.9, 20 fl oz; 1.25, 2 L", "variant", None, "https://www.coca-cola.com/us/en/brands/coca-cola/products/zero", "2026-09-24", "needs_package_verification"),
            ("coca-cola-cherry", "The Coca-Cola Company", "Coca-Cola", "Coca-Cola Cherry", "carbonated soft drink", "United States", "7.5, 12, 16.9 fl oz; 2 L", "variant", None, "https://www.coca-cola.com/us/en/brands/coca-cola/products/coca-cola-flavors", "2026-09-24", "discovery_candidate"),
            ("coca-cola-cherry-zero", "The Coca-Cola Company", "Coca-Cola", "Coca-Cola Cherry Zero Sugar", "carbonated soft drink", "United States", "7.5, 12, 16.9, 20 fl oz; 2 L", "variant", None, "https://www.coca-cola.com/us/en/brands/coca-cola/products/coca-cola-flavors", "2026-09-24", "discovery_candidate"),
            ("coca-cola-vanilla", "The Coca-Cola Company", "Coca-Cola", "Coca-Cola Vanilla", "carbonated soft drink", "United States", "12, 16.9, 20 fl oz", "variant", None, "https://www.coca-cola.com/us/en/brands/coca-cola/products/coca-cola-flavors", "2026-09-24", "discovery_candidate"),
            ("sprite-original", "The Coca-Cola Company", "Sprite", "Sprite", "carbonated soft drink", "United States", "7.5, 8, 12, 13.2, 16.9, 20 fl oz; 1, 1.25, 2, 3 L", "variant", None, "https://www.coca-cola.com/us/en/brands/sprite/products", "2026-09-24", "needs_package_verification"),
            ("sprite-zero", "The Coca-Cola Company", "Sprite", "Sprite Zero Sugar", "carbonated soft drink", "United States", None, "unknown", None, "https://www.coca-cola.com/us/en/brands/sprite/products", "2026-09-24", "discovery_candidate"),
            ("sprite-chill", "The Coca-Cola Company", "Sprite", "Sprite Chill", "carbonated soft drink", "United States", None, "unknown", None, "https://www.coca-cola.com/us/en/brands/sprite/products", "2026-09-24", "discovery_candidate"),
            ("sprite-tea-peach", "The Coca-Cola Company", "Sprite", "Sprite + Tea Peach", "carbonated soft drink", "United States", "12, 20 fl oz", "variant", "Kroger exclusive", "https://www.coca-cola.com/us/en/brands/sprite/products", "2026-09-24", "discovery_candidate"),
            ("powerade-grape", "The Coca-Cola Company", "Powerade", "Powerade Grape", "sports drink", "United States", "20, 28 fl oz", "variant", None, "https://powerade-us-en.beta.cep.coca-cola.com/products/powerade", "2026-09-24", "needs_package_verification"),
            ("powerade-lemon-lime", "The Coca-Cola Company", "Powerade", "Powerade Lemon Lime", "sports drink", "United States", "20, 28 fl oz", "variant", None, "https://powerade-us-en.beta.cep.coca-cola.com/products/powerade", "2026-09-24", "needs_package_verification"),
            ("powerade-orange", "The Coca-Cola Company", "Powerade", "Powerade Orange", "sports drink", "United States", "12, 20, 28 fl oz", "variant", None, "https://powerade-us-en.beta.cep.coca-cola.com/products/powerade", "2026-09-24", "needs_package_verification"),
            ("powerade-zero-mixed-berry", "The Coca-Cola Company", "Powerade Zero", "Powerade Zero Sugar Mixed Berry", "sports drink", "United States", "12, 20, 28 fl oz", "variant", None, "https://powerade-us-en.alpha.cep.coca-cola.com/products/powerade-zero", "2026-09-24", "needs_package_verification"),
            ("dasani", "The Coca-Cola Company", "Dasani", "Dasani Purified Water", "bottled water", "United States", "10, 12, 16.9, 20 fl oz; 1, 1.5 L", "variant", None, "https://www.coca-cola.com/us/en/brands/dasani", "2026-09-24", "needs_package_verification"),
            ("pepsi", "PepsiCo", "Pepsi", "Pepsi", "carbonated soft drink", "United States", "7.5, 12, 16, 16.9, 20, 24 fl oz; 1, 1.25, 2 L", "variant", None, "https://www.pepsi.com/products/pepsi", "2026-09-24", "needs_package_verification"),
            ("diet-pepsi", "PepsiCo", "Pepsi", "Diet Pepsi", "carbonated soft drink", "United States", "7.5, 12, 16, 16.9, 20, 24 fl oz; 1, 1.25, 2 L", "variant", None, "https://www.pepsi.com/products/diet-pepsi", "2026-09-24", "needs_package_verification"),
            ("pepsi-zero", "PepsiCo", "Pepsi", "Pepsi Zero Sugar", "carbonated soft drink", "United States", "7.5, 12, 13, 16, 16.9, 20, 24, 33.8, 42.3, 67 fl oz; fountain", "variant", None, "https://www.pepsicoproductfacts.com/Home/product?gtin=00012000018800", "2026-09-24", "needs_package_verification"),
            ("mountain-dew-original", "PepsiCo", "Mountain Dew", "Mountain Dew", "carbonated soft drink", "United States", "7.5, 12, 13, 16, 16.9, 20, 24, 33.8, 42.3, 67 fl oz; fountain/freeze", "variant", None, "https://www.pepsicoproductfacts.com/Home/product?gtin=00012000000850", "2026-09-24", "needs_package_verification"),
            ("gatorade-cool-blue", "PepsiCo", "Gatorade", "Gatorade Cool Blue", "sports drink", "United States", "12, 20, 24, 28 fl oz", "variant", None, "https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000324815", "2026-09-24", "needs_package_verification"),
            ("gatorade-strawberry-lemonade", "PepsiCo", "Gatorade", "Gatorade Strawberry Lemonade", "sports drink", "United States", "20 fl oz", "variant", None, "https://www.pepsicoproductfacts.com/Home/product?gtin=00052000104257", "2026-09-24", "needs_package_verification"),
            ("gatorade-water", "PepsiCo", "Gatorade", "Gatorade Water", "bottled water", "United States", "20, 23.7, 33.8 fl oz", "variant", None, "https://www.pepsicoproductfacts.com/Home/Product?gtin=00052000054903", "2026-09-24", "needs_package_verification"),
            ("aquafina", "PepsiCo", "Aquafina", "Aquafina Purified Water", "bottled water", "United States", "12, 16, 16.9, 20, 33.8, 42.3, 50.7 fl oz", "family", "Exact bottle/package label required", "https://www.pepsicoproductfacts.com/Home/Product?gtin=00012000001086", "2026-09-24", "discovery_candidate"),
            ("monster-ultra-zero", "Monster Energy", "Monster Ultra", "Monster Ultra Zero", "energy drink", "United States", "12, 16, 19.2, 24 oz", "variant", None, "https://www.monsterenergy.com/en-us/energy-drinks/zero-sugar/zero-ultra/", "2026-09-24", "needs_package_verification"),
            ("red-bull-original", "Red Bull", "Red Bull", "Red Bull Original", "energy drink", "United States", "8.4, 12, 16, 20 fl oz", "variant", None, "https://www.redbull.com/energydrink/red-bull-energy-drink", "2026-09-24", "needs_package_verification"),
            ("dr-pepper-blackberry", "Keurig Dr Pepper", "Dr Pepper", "Dr Pepper Blackberry", "carbonated soft drink", "United States", None, "unknown", "Package facts must be verified", "https://www.keurigdrpepper.com/keurig-dr-pepper-unveils-bold-new-flavors-across-iconic-u-s-cold-beverages-portfolio-27/", "2026-09-24", "discovery_candidate"),
            ("seven-up", "Keurig Dr Pepper", "7UP", "7UP", "carbonated soft drink", "United States", None, "unknown", "Brand-directory discovery; package facts required", "https://www.keurigdrpepper.com/brands/", "2026-09-24", "discovery_candidate"),
            ("snapple", "Keurig Dr Pepper", "Snapple", "Snapple Tea and Juice Drinks", "tea and juice drink", "United States", None, "unknown", "Brand-directory discovery; flavor/package facts required", "https://www.keurigdrpepper.com/brands/", "2026-09-24", "discovery_candidate"),
            ("bai", "Keurig Dr Pepper", "Bai", "Bai Flavored Drinks", "flavored drink", "United States", None, "unknown", "Brand-directory discovery; flavor/package facts required", "https://www.keurigdrpepper.com/brands/", "2026-09-24", "discovery_candidate"),
            ("lacroix", "National Beverage Corp.", "LaCroix", "LaCroix Sparkling Water", "sparkling water", "United States", None, "unknown", "Current package-size index requires direct label/FDC verification", "https://www.lacroixwater.com/", "2026-09-24", "discovery_candidate"),
        ])
        conn.executemany("INSERT INTO source_records VALUES (?, ?, ?, ?, ?, ?, ?)", [
            ("coca-cola-zero-source", "The Coca-Cola Company", "https://www.coca-cola.com/us/en/brands/coca-cola/products/zero", "United States", "2026-09-24", "manufacturer_page", None),
            ("monster-zero-source", "Monster Energy", "https://www.monsterenergy.com/en-us/energy-drinks/monster-energy/zero-sugar/", "United States", "2026-09-24", "manufacturer_page", None),
        ])
        conn.executemany("INSERT INTO label_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            ("coca-cola-zero-2026-09-24", "coca-cola-zero-sugar-12oz-us", "coca-cola-zero-source", "12 fl oz (355 mL)", 1, 0, 0, 0, 0, 40, 34, "Carbonated water, caramel color, phosphoric acid, aspartame, potassium benzoate (to protect taste), natural flavors, potassium citrate, acesulfame potassium, caffeine, stevia extract.", "Phenylketonurics: Contains phenylalanine.", "Zero Sugar", "manufacturer_verified", "2026-09-24", 1),
            ("monster-zero-2026-09-24", "monster-zero-sugar-16oz-us", "monster-zero-source", "16 fl oz (473 mL)", 1, 10, 0, 0, 0, 380, 160, "Carbonated water, citric acid, erythritol, natural flavors, taurine, sodium citrate, Panax ginseng flavor, L-carnitine L-tartrate, caffeine, sucralose, sorbic acid, benzoic acid, fruit juice (color), niacinamide, acesulfame potassium, salt, D-glucuronolactone, guarana extract, inositol, pyridoxine hydrochloride, riboflavin, cyanocobalamin.", None, "Zero Sugar", "needs_package_verification", "2026-09-24", 1),
        ])
        conn.executemany("INSERT INTO ingredients VALUES (?, ?)", [
            ("caffeine", "Caffeine"), ("aspartame", "Aspartame"), ("ace-k", "Acesulfame potassium"), ("sucralose", "Sucralose"), ("erythritol", "Erythritol"), ("taurine", "Taurine"),
        ])
        conn.executemany("INSERT INTO ingredient_profiles VALUES (?, ?, ?, ?, ?, ?)", [
            ("caffeine", "stimulant", "A stimulant that can increase alertness.", "The label amount should be considered alongside all caffeine consumed that day. FDA's 400 mg/day reference is for most healthy adults, not an individual recommendation.", "established_guidance", FDA_CAFFEINE_SOURCE),
            ("aspartame", "high-intensity sweetener", "A low- or no-calorie sweetener used in place of sugar.", "FDA lists an acceptable daily intake of 50 mg/kg/day. Product labels generally do not disclose the amount, so a per-drink comparison is unavailable.", "established_guidance", FDA_SWEETENER_SOURCE),
            ("ace-k", "high-intensity sweetener", "A low- or no-calorie sweetener, also called acesulfame potassium.", "FDA lists an acceptable daily intake of 15 mg/kg/day. Product labels generally do not disclose the amount.", "established_guidance", FDA_SWEETENER_SOURCE),
            ("sucralose", "high-intensity sweetener", "A low- or no-calorie sweetener used in place of sugar.", "FDA lists an acceptable daily intake of 5 mg/kg/day. Product labels generally do not disclose the amount.", "established_guidance", FDA_SWEETENER_SOURCE),
            ("erythritol", "sugar alcohol sweetener", "A sugar alcohol used to provide sweetness with fewer calories than sugar.", "A label amount, when present, is a fact; the ingredient name alone does not establish a personalized health effect.", "limited_or_contextual", None),
            ("taurine", "amino-sulfonic compound", "A compound often added to energy drinks.", "Its presence is not evidence that a drink will improve health or offset sleep loss.", "limited_or_contextual", None),
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
    from api.classification import refresh_assessments

    refresh_assessments(DATABASE)
    print(f"Seeded {DATABASE}")


if __name__ == "__main__":
    main()
