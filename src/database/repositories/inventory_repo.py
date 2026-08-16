"""Repository for inventory and transaction data access."""

from typing import List, Optional

from ..connection import get_connection


def find_item(conn, item_id: int) -> Optional[dict]:
    """Find an inventory item by its ID."""
    cur = conn.execute(
        "SELECT * FROM inventory WHERE id = ?",
        (item_id,),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def find_item_by_name(conn, name: str) -> Optional[dict]:
    """Find an inventory item by name (case-insensitive)."""
    cur = conn.execute(
        "SELECT * FROM inventory WHERE lower(name) = lower(?)",
        (name,),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def add_item(
    conn,
    name: str,
    category: str,
    unit: str = "pcs",
    quantity: int = 0,
    minimum_stock_level: int = 0,
    price: float = 0.0,
) -> int:
    """Add a new inventory item and return its generated ID."""
    cur = conn.execute(
        """
        INSERT INTO inventory (name, category, unit, quantity, minimum_stock_level, price)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, category, unit, quantity, minimum_stock_level, price),
    )
    conn.commit()
    return cur.lastrowid


def update_stock(conn, item_id: int, quantity_delta: int) -> int:
    """Update stock quantity for an item.

    Args:
        conn: Database connection.
        item_id: Target item ID.
        quantity_delta: Positive to add stock, negative to remove.

    Returns:
        The new quantity after the update.

    Raises:
        ValueError: If the item does not exist or stock would go negative.
    """
    cur = conn.execute(
        "SELECT quantity FROM inventory WHERE id = ?",
        (item_id,),
    )
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Item with id {item_id} does not exist.")

    current_quantity = row["quantity"]
    new_quantity = current_quantity + quantity_delta

    if new_quantity < 0:
        raise ValueError(
            f"Cannot reduce stock below zero. Current: {current_quantity}, "
            f"Requested change: {quantity_delta}, Result: {new_quantity}"
        )

    conn.execute(
        """
        UPDATE inventory
        SET quantity = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (new_quantity, item_id),
    )
    conn.commit()
    return new_quantity


def record_transaction(
    conn,
    item_id: int,
    txn_type: str,
    quantity: int,
    note: Optional[str] = None,
) -> int:
    """Record an inventory transaction.

    Args:
        conn: Database connection.
        item_id: Item involved in the transaction.
        txn_type: Either 'ADD' or 'REMOVE'.
        quantity: Quantity involved (must be positive).
        note: Optional description.

    Returns:
        The transaction ID.

    Raises:
        ValueError: If transaction type is invalid or quantity is not positive.
    """
    if txn_type not in ("ADD", "REMOVE"):
        raise ValueError(
            f"Invalid transaction type: {txn_type}. Use 'ADD' or 'REMOVE'."
        )

    if quantity <= 0:
        raise ValueError("Transaction quantity must be positive.")

    cur = conn.execute(
        """
        INSERT INTO transactions (item_id, type, quantity, note)
        VALUES (?, ?, ?, ?)
        """,
        (item_id, txn_type, quantity, note),
    )
    conn.commit()
    return cur.lastrowid


def list_inventory(conn) -> List[dict]:
    """Return all inventory items ordered by name."""
    cur = conn.execute(
        "SELECT * FROM inventory ORDER BY name ASC"
    )
    return [dict(row) for row in cur.fetchall()]
