"""CLI entry point for the AI Inventory Agent."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.database.connection import get_connection
from src.database.schema import create_tables
from src.services import interpret_message, process_inventory_action
from src.validators import validate_ai_output, ValidationError


def run_cli(db_path="database/inventory.db"):
    """Start the interactive CLI loop."""
    conn = get_connection(db_path)
    create_tables(conn)

    print("AI Inventory Agent - Version 0")
    print("Type 'exit' or 'quit' to leave.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        try:
            raw = interpret_message(user_input)
        except ConnectionError as exc:
            print(f"[AI Error] {exc}")
            continue
        except ValueError as exc:
            print(f"[AI Error] {exc}")
            continue

        try:
            validated = validate_ai_output(raw)
        except ValidationError as exc:
            print(f"[Validation Error] {exc}")
            continue

        action = validated["action"]
        product = validated.get("product")
        quantity = validated.get("quantity")

        if action == "UNKNOWN":
            print("[AI] Request not understood. Please try again.")
            continue

        print(f"[AI] Interpreted: {action} | product={product} | quantity={quantity}")

        if action in ("ADD", "REMOVE"):
            try:
                confirm = input("Confirm this action? (y/n): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nOperation cancelled.")
                continue

            if confirm != "y":
                print("Operation cancelled.")
                continue

        try:
            result = process_inventory_action(conn, validated)
        except Exception as exc:
            print(f"[System Error] {exc}")
            continue

        if result["status"] == "success":
            print(f"[OK] {result['message']}")
            if action == "LIST" and result.get("data", {}).get("inventory"):
                _print_inventory(result["data"]["inventory"])
        else:
            print(f"[Error] {result['message']}")


def _print_inventory(items):
    """Print a simple table of inventory items."""
    if not items:
        print("  (no items)")
        return

    header = f"{'Name':<20} {'Category':<15} {'Qty':>5} {'Unit':<6} {'Price':>8}"
    print(header)
    print("-" * len(header))
    for item in items:
        name = item.get("name", "")
        category = item.get("category", "")
        qty = item.get("quantity", 0)
        unit = item.get("unit", "")
        price = item.get("price", 0.0)
        print(f"{name:<20} {category:<15} {qty:>5} {unit:<6} {price:>8.2f}")


def main():
    """Package entry point."""
    try:
        run_cli()
    finally:
        pass


if __name__ == "__main__":
    main()
