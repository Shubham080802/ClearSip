"""Small database boundary for local SQLite and production PostgreSQL."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCAL_DATABASE = ROOT / "data" / "clearsip.db"


def database_url() -> str:
    return os.getenv("DATABASE_URL", f"sqlite:///{LOCAL_DATABASE}")


def is_sqlite() -> bool:
    return database_url().startswith("sqlite:///")


@contextmanager
def connection() -> Iterator[Any]:
    """Yield a connection with dictionary-like rows for either supported SQL engine."""
    url = database_url()
    if url.startswith("sqlite:///"):
        local_path = Path(url.removeprefix("sqlite:///"))
        local_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(local_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
        return

    if url.startswith("postgres://"):
        url = "postgresql://" + url.removeprefix("postgres://")
    if not url.startswith("postgresql://"):
        raise RuntimeError("DATABASE_URL must be a sqlite:/// or PostgreSQL connection URL")

    import psycopg
    from psycopg.rows import dict_row

    with psycopg.connect(url, row_factory=dict_row) as conn:
        yield conn


def placeholder() -> str:
    return "?" if is_sqlite() else "%s"
