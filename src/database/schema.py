"""Database schema definitions and migration helpers."""

from .connection import get_connection


def create_tables(conn=None) -> None:
    """Create all tables if they do not exist.

    If no connection is provided, a new one is created and closed.
    """
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit TEXT NOT NULL DEFAULT 'pcs',
                quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
                minimum_stock_level INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('ADD', 'REMOVE')),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                note TEXT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (item_id) REFERENCES inventory(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_inventory_name ON inventory(name);
            CREATE INDEX IF NOT EXISTS idx_transactions_item_id ON transactions(item_id);
            CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
        """)
        conn.commit()
    finally:
        if should_close:
            conn.close()
