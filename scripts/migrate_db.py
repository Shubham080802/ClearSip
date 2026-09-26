"""Apply immutable, ordered schema migrations to SQLite or PostgreSQL."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.database import connection, is_sqlite, placeholder

MIGRATIONS = ROOT / "migrations"
MIGRATION_NAME = re.compile(r"^(\d{4}_[a-z0-9_]+)\.sql$")


def migration_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for path in MIGRATIONS.glob("*.sql"):
        match = MIGRATION_NAME.match(path.name)
        if not match:
            raise RuntimeError(f"Invalid migration filename: {path.name}")
        files.append((match.group(1), path))
    return sorted(files)


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def statements(script: str) -> list[str]:
    """Split the repository's simple DDL files without supporting procedural SQL."""
    return [statement.strip() for statement in script.split(";") if statement.strip()]


def ensure_migration_table(conn) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS schema_migrations (
        version TEXT PRIMARY KEY,
        checksum TEXT NOT NULL,
        applied_at TEXT NOT NULL
        )"""
    )


def apply_migrations() -> list[str]:
    applied_now: list[str] = []
    marker = placeholder()
    with connection() as conn:
        if not is_sqlite():
            # Serializes deploy-time migrations without relying on Vercel process state.
            conn.execute("SELECT pg_advisory_xact_lock(679459360721)")
        ensure_migration_table(conn)
        completed = {
            row["version"]: row["checksum"]
            for row in conn.execute("SELECT version, checksum FROM schema_migrations").fetchall()
        }
        for version, path in migration_files():
            digest = checksum(path)
            if version in completed:
                if completed[version] != digest:
                    raise RuntimeError(f"Migration {version} was changed after being applied; create a new migration instead.")
                continue
            for statement in statements(path.read_text()):
                conn.execute(statement)
            conn.execute(
                f"INSERT INTO schema_migrations (version, checksum, applied_at) VALUES ({marker}, {marker}, {marker})",
                (version, digest, datetime.now(UTC).isoformat()),
            )
            applied_now.append(version)
    return applied_now


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", help="Override DATABASE_URL for this migration run.")
    args = parser.parse_args()
    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url
    applied = apply_migrations()
    print("Applied: " + ", ".join(applied) if applied else "Database is already up to date.")


if __name__ == "__main__":
    main()
