"""FastAPI application exported for Vercel's Python runtime."""

from __future__ import annotations

import re

from fastapi import FastAPI, HTTPException, Query

from api.database import connection, placeholder

app = FastAPI(
    title="ClearSip API",
    version="0.2.0",
    description="Versioned, sourced beverage-label information. Educational only; not medical advice.",
)


def rows_to_package(rows: list[dict]) -> dict:
    first = rows[0]
    return {
        "id": first["package_id"],
        "name": first["display_name"],
        "manufacturer": first["manufacturer_name"],
        "family": first["family_name"],
        "flavor": first["flavor_name"],
        "category": first["category"],
        "market": first["market"],
        "package": first["package_description"],
        "gtin": first["gtin"],
        "fdc_id": first["fdc_id"],
        "serving": first["serving"],
        "servings_per_container": first["servings_per_container"],
        "calories": first["calories"],
        "saturated_fat_g": first["saturated_fat_g"],
        "total_sugar_g": first["total_sugar_g"],
        "added_sugar_g": first["added_sugar_g"],
        "sodium_mg": first["sodium_mg"],
        "caffeine_mg": first["caffeine_mg"],
        "verification_status": first["verification_status"],
        "label_observed_on": first["label_observed_on"],
        "source": {"publisher": first["publisher"], "url": first["source_url"], "accessed_on": first["accessed_on"]},
        "label_context": {
            "overall_status": first["overall_status"],
            "sugar_free_claim_status": first["sugar_free_claim_status"],
            "preservative_free_claim_status": first["preservative_free_claim_status"],
            "healthy_claim_status": first["healthy_claim_status"],
            "frequent_intake_context": first["frequent_intake_context"],
            "summary": first["assessment_summary"],
            "policy_version": first["policy_version"],
        },
        "ingredients": [
            {"name": row["ingredient_name"], "role": row["role"], "assessment": row["assessment"], "evidence_status": row["evidence_status"], "functional_class": row["functional_class"], "plain_language_summary": row["plain_language_summary"], "intake_context": row["intake_context"], "profile_evidence_level": row["profile_evidence_level"], "source_url": row["ingredient_source_url"] or row["profile_source_url"]}
            for row in rows if row["ingredient_name"]
        ],
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "clearsip-api", "catalog_model": "versioned-package-label"}


@app.get("/api/products")
def search_products(query: str = Query(min_length=2, max_length=120)) -> list[dict]:
    marker = placeholder()
    terms = re.findall(r"[a-z0-9]+", query.lower())[:12]
    if not terms:
        return []
    searchable_name = "LOWER(bv.display_name || ' ' || m.name || ' ' || bf.name)"
    term_filters = " AND ".join(f"{searchable_name} LIKE {marker}" for _ in terms)
    statement = f"""
        SELECT pp.id, bv.display_name, m.name AS manufacturer, bf.name AS family,
               pp.market, pp.package_description, pp.gtin, pp.fdc_id, lv.caffeine_mg, lv.verification_status
        FROM product_packages pp
        JOIN beverage_variants bv ON bv.id = pp.variant_id
        JOIN beverage_families bf ON bf.id = bv.family_id
        JOIN manufacturers m ON m.id = bf.manufacturer_id
        JOIN label_versions lv ON lv.package_id = pp.id AND lv.is_current = 1
        WHERE {term_filters}
        ORDER BY bv.display_name, pp.package_description
        LIMIT 25
    """
    with connection() as conn:
        records = conn.execute(statement, tuple(f"%{term}%" for term in terms)).fetchall()
    return [dict(record) for record in records]


@app.get("/api/catalog-discoveries")
def catalog_discoveries(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    """Source-backed public product candidates awaiting exact package-label review."""
    marker = placeholder()
    statement = f"""
        SELECT id, manufacturer_name, beverage_family_name, variant_name, category, market,
               observed_package_sizes, package_size_scope, availability_note, source_url,
               discovered_on, verification_status
        FROM catalog_discoveries
        ORDER BY manufacturer_name, beverage_family_name, variant_name
        LIMIT {marker}
    """
    with connection() as conn:
        records = conn.execute(statement, (limit,)).fetchall()
    return [dict(record) for record in records]


@app.get("/api/catalog-summary")
def catalog_summary() -> dict[str, int]:
    """Return the current public coverage counts without returning catalog rows."""
    with connection() as conn:
        record = conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM label_versions WHERE is_current = 1) AS reviewed_package_labels,
                (SELECT COUNT(*) FROM catalog_discoveries) AS catalog_discoveries
            """
        ).fetchone()
    return dict(record)


@app.get("/api/products/{package_id}")
def product_detail(package_id: str) -> dict:
    marker = placeholder()
    statement = f"""
        SELECT pp.id AS package_id, pp.market, pp.package_description, pp.gtin, pp.fdc_id,
               bv.display_name, bv.flavor_name, bv.category, bf.name AS family_name,
               m.name AS manufacturer_name, lv.serving, lv.servings_per_container, lv.calories, lv.saturated_fat_g, lv.total_sugar_g,
               lv.added_sugar_g, lv.sodium_mg, lv.caffeine_mg, lv.verification_status, lv.label_observed_on,
               s.publisher, s.url AS source_url, s.accessed_on,
               la.overall_status, la.sugar_free_claim_status, la.preservative_free_claim_status,
               la.healthy_claim_status, la.frequent_intake_context, la.summary AS assessment_summary,
               la.policy_version,
               i.name AS ingredient_name, li.role, li.assessment, li.evidence_status,
               li.source_url AS ingredient_source_url, ip.functional_class,
               ip.plain_language_summary, ip.intake_context,
               ip.evidence_level AS profile_evidence_level, ip.source_url AS profile_source_url
        FROM product_packages pp
        JOIN beverage_variants bv ON bv.id = pp.variant_id
        JOIN beverage_families bf ON bf.id = bv.family_id
        JOIN manufacturers m ON m.id = bf.manufacturer_id
        JOIN label_versions lv ON lv.package_id = pp.id AND lv.is_current = 1
        JOIN source_records s ON s.id = lv.source_id
        LEFT JOIN label_assessments la ON la.label_version_id = lv.id
        LEFT JOIN label_ingredients li ON li.label_version_id = lv.id
        LEFT JOIN ingredients i ON i.id = li.ingredient_id
        LEFT JOIN ingredient_profiles ip ON ip.ingredient_id = i.id
        WHERE pp.id = {marker}
        ORDER BY li.position
    """
    with connection() as conn:
        records = [dict(row) for row in conn.execute(statement, (package_id,)).fetchall()]
    if not records:
        raise HTTPException(status_code=404, detail="Product package not found")
    return rows_to_package(records)
