"""Inventory service layer.

Bridges validated AI output and the database repository.
Handles business logic for ADD, REMOVE, CHECK, LIST, and UNKNOWN actions.
"""

from typing import Any, Dict

from ..database.repositories.inventory_repo import (
    add_item,
    find_item_by_name,
    list_inventory,
    record_transaction,
    update_stock,
)


def process_inventory_action(conn, validated_output: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an inventory action based on validated AI output.

    Args:
        conn: SQLite database connection.
        validated_output: Dictionary with keys: action, product, quantity.
                          Expected to be pre-validated by the validation layer.

    Returns:
        A result dictionary with keys:
        - status: "success" or "error"
        - action: the action performed
        - message: human-readable description
        - data: optional payload (new quantity, inventory list, etc.)
    """
    action = validated_output.get("action")
    product = validated_output.get("product")
    quantity = validated_output.get("quantity")

    if action == "ADD":
        return _handle_add(conn, product, quantity)
    if action == "REMOVE":
        return _handle_remove(conn, product, quantity)
    if action == "CHECK":
        return _handle_check(conn, product)
    if action == "LIST":
        return _handle_list(conn)
    if action == "UNKNOWN":
        return {
            "status": "error",
            "action": "UNKNOWN",
            "message": "Request not understood. Please try again.",
            "data": None,
        }

    return {
        "status": "error",
        "action": action,
        "message": f"Unsupported action: {action}",
        "data": None,
    }


def _handle_add(conn, product: str, quantity: int) -> Dict[str, Any]:
    item = find_item_by_name(conn, product)
    if item is None:
        item_id = add_item(
            conn,
            name=product,
            category="Uncategorized",
            unit="pcs",
            quantity=0,
            minimum_stock_level=0,
            price=0.0,
        )
        item = {"id": item_id, "quantity": 0}

    new_quantity = update_stock(conn, item["id"], quantity)
    record_transaction(conn, item["id"], "ADD", quantity, note="Added via AI")

    return {
        "status": "success",
        "action": "ADD",
        "message": f"Added {quantity} {product}. New stock: {new_quantity}.",
        "data": {"product": product, "quantity": quantity, "new_quantity": new_quantity},
    }


def _handle_remove(conn, product: str, quantity: int) -> Dict[str, Any]:
    item = find_item_by_name(conn, product)
    if item is None:
        return {
            "status": "error",
            "action": "REMOVE",
            "message": f"Product '{product}' not found in inventory.",
            "data": None,
        }

    current_quantity = item["quantity"]
    if current_quantity < quantity:
        return {
            "status": "error",
            "action": "REMOVE",
            "message": (
                f"Insufficient stock for '{product}'. "
                f"Current: {current_quantity}, Requested: {quantity}."
            ),
            "data": {"current_quantity": current_quantity, "requested_quantity": quantity},
        }

    new_quantity = update_stock(conn, item["id"], -quantity)
    record_transaction(conn, item["id"], "REMOVE", quantity, note="Removed via AI")

    return {
        "status": "success",
        "action": "REMOVE",
        "message": f"Removed {quantity} {product}. New stock: {new_quantity}.",
        "data": {"product": product, "quantity": quantity, "new_quantity": new_quantity},
    }


def _handle_check(conn, product: str) -> Dict[str, Any]:
    item = find_item_by_name(conn, product)
    if item is None:
        return {
            "status": "error",
            "action": "CHECK",
            "message": f"Product '{product}' not found in inventory.",
            "data": None,
        }

    return {
        "status": "success",
        "action": "CHECK",
        "message": f"{product} stock: {item['quantity']} {item['unit']}.",
        "data": {"product": product, "quantity": item["quantity"], "unit": item["unit"]},
    }


def _handle_list(conn) -> Dict[str, Any]:
    items = list_inventory(conn)
    return {
        "status": "success",
        "action": "LIST",
        "message": f"Inventory contains {len(items)} item(s).",
        "data": {"inventory": items},
    }
