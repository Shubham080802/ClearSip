"""FastAPI application exported for Vercel's Python runtime."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from api.database import connection, placeholder

app = FastAPI(
    title="ClearSip API",
    version="0.1.0",
    description="Versioned, sourced beverage-label information. Educational only; not medical advice.",
)


def rows_to_product(rows: list[dict]) -> dict:
    first = rows[0]
    return {
        "id": first["product_id"],
        "name": first["name"],
        "brand": first["brand"],
        "region": first["region"],
        "serving": first["serving"],
        "calories": first["calories"],
        "added_sugar_g": first["added_sugar_g"],
        "caffeine_mg": first["caffeine_mg"],
        "verification_status": first["verification_status"],
        "last_reviewed": first["last_reviewed"],
        "source_url": first["source_url"],
        "ingredients": [
            {
                "name": row["ingredient_name"],
                "role": row["role"],
                "assessment": row["assessment"],
                "evidence_status": row["evidence_status"],
                "source_url": row["ingredient_source_url"],
            }
            for row in rows if row["ingredient_name"]
        ],
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "clearsip-api"}


@app.get("/api/products")
def search_products(query: str = Query(min_length=2, max_length=120)) -> list[dict]:
    marker = placeholder()
    statement = f"""
        SELECT p.id, p.name, p.brand, p.region, p.serving, p.calories,
               p.added_sugar_g, p.caffeine_mg, p.verification_status, p.last_reviewed,
               p.source_url
        FROM products p
        WHERE LOWER(p.name) LIKE LOWER({marker}) OR LOWER(p.brand) LIKE LOWER({marker})
        ORDER BY p.name
        LIMIT 10
    """
    with connection() as conn:
        records = conn.execute(statement, (f"%{query}%", f"%{query}%")).fetchall()
    return [dict(record) for record in records]


@app.get("/api/products/{product_id}")
def product_detail(product_id: str) -> dict:
    marker = placeholder()
    statement = f"""
        SELECT p.id AS product_id, p.name, p.brand, p.region, p.serving, p.calories,
               p.added_sugar_g, p.caffeine_mg, p.verification_status, p.last_reviewed,
               p.source_url, i.name AS ingredient_name, pi.role, pi.assessment,
               pi.evidence_status, pi.source_url AS ingredient_source_url
        FROM products p
        LEFT JOIN product_ingredients pi ON pi.product_id = p.id
        LEFT JOIN ingredients i ON i.id = pi.ingredient_id
        WHERE p.id = {marker}
        ORDER BY pi.position
    """
    with connection() as conn:
        records = [dict(row) for row in conn.execute(statement, (product_id,)).fetchall()]
    if not records:
        raise HTTPException(status_code=404, detail="Product not found")
    return rows_to_product(records)
