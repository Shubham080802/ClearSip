"""Keep package identity separate from verification of its dated label."""

PACKAGE_LABEL_SOURCES = {"package_observation", "manufacturer_label", "usda_fdc_branded"}


def package_evidence(row: dict) -> dict:
    """Describe only recorded evidence; a package row alone is not verification."""
    status = row["verification_status"]
    source_type = row["source_type"]
    verified = status == "package_verified" and source_type in PACKAGE_LABEL_SOURCES
    return {
        "label_scope": "package" if verified else "variant_or_unconfirmed",
        "label_verified": verified,
        "gtin_linked": bool(row["gtin"]),
        "label_version_id": row["label_version_id"],
        "verification_status": status,
        "source_type": source_type,
    }
