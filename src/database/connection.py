"""Database connection factory for SQLite."""

import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a SQLite database connection.

    Configures the connection with:
    - Row factory for dict-like access via column names
    - WAL mode for better read/write concurrency
    - Foreign key enforcement
    """
    if db_path is None:
        db_path = "database/inventory.db"

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database transactions.

    Commits on success, rolls back on exception.

    Usage:
        with transaction(conn) as c:
            c.execute(...)
            c.execute(...)
    """
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
