"""Web backend wrapper for the AI Inventory Agent.

Provides a clean interface between the Streamlit UI and the existing
backend services. Manages the database connection lifecycle.
"""

from typing import Any, Dict, Optional

from src.database.connection import get_connection
from src.database.schema import create_tables
from src.services import interpret_message, process_inventory_action
from src.validators import validate_ai_output, ValidationError


class InventoryWebBackend:
    """Backend wrapper that manages DB connection and orchestrates the
    interpret → validate → confirm → execute flow.
    """

    def __init__(self, db_path: str = "database/inventory.db"):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = get_connection(self.db_path)
        create_tables(self.conn)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def interpret(self, message: str) -> Dict[str, Any]:
        """Interpret a natural-language message and validate the output.

        Returns:
            {
                "status": "success" | "error",
                "step": "interpret" | "validate",
                "raw": dict or None,
                "validated": dict or None,
                "message": str,
                "error": str or None
            }
        """
        try:
            raw = interpret_message(message)
        except ConnectionError as exc:
            return {
                "status": "error",
                "step": "interpret",
                "raw": None,
                "validated": None,
                "message": str(exc),
                "error": "ollama_connection",
            }
        except ValueError as exc:
            return {
                "status": "error",
                "step": "interpret",
                "raw": None,
                "validated": None,
                "message": str(exc),
                "error": "invalid_json",
            }

        try:
            validated = validate_ai_output(raw)
        except ValidationError as exc:
            return {
                "status": "error",
                "step": "validate",
                "raw": raw,
                "validated": None,
                "message": str(exc),
                "error": "validation",
            }

        return {
            "status": "success",
            "step": "validated",
            "raw": raw,
            "validated": validated,
            "message": "Interpreted successfully.",
            "error": None,
        }

    def confirm_and_execute(self, validated_output: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a validated inventory action against the database.

        Returns:
            {
                "status": "success" | "error",
                "action": str,
                "message": str,
                "data": dict or None
            }
        """
        try:
            result = process_inventory_action(self.conn, validated_output)
        except Exception as exc:
            return {
                "status": "error",
                "action": validated_output.get("action", "UNKNOWN"),
                "message": f"System error: {exc}",
                "data": None,
            }
        return result

    def get_inventory(self) -> list:
        """Return all inventory items ordered by name."""
        from src.database.repositories.inventory_repo import list_inventory
        return list_inventory(self.conn)

    def get_transactions(self, limit: int = 20) -> list:
        """Return recent transactions ordered by timestamp desc."""
        cur = self.conn.execute(
            """
            SELECT t.*, i.name as item_name
            FROM transactions t
            LEFT JOIN inventory i ON t.item_id = i.id
            ORDER BY t.timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()]
