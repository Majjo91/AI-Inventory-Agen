"""Validation layer for AI interpretation output."""

from typing import Any, Dict

ALLOWED_ACTIONS = {"ADD", "REMOVE", "CHECK", "LIST", "UNKNOWN"}


class ValidationError(Exception):
    """Raised when AI output fails validation."""


def validate_ai_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the structured JSON returned by the AI interpreter.

    Args:
        data: Dictionary with keys: action, product, quantity.

    Returns:
        The validated dictionary.

    Raises:
        ValidationError: If the output violates validation rules.
    """
    if not isinstance(data, dict):
        raise ValidationError("Output must be a dictionary.")

    required_keys = {"action", "product", "quantity"}
    actual_keys = set(data.keys())
    if actual_keys != required_keys:
        missing = required_keys - actual_keys
        extra = actual_keys - required_keys
        parts = []
        if missing:
            parts.append(f"missing keys: {sorted(missing)}")
        if extra:
            parts.append(f"unexpected keys: {sorted(extra)}")
        raise ValidationError("Output must contain exactly action, product, quantity. " + "; ".join(parts))

    action = data.get("action")
    product = data.get("product")
    quantity = data.get("quantity")

    if action not in ALLOWED_ACTIONS:
        raise ValidationError(
            f"Invalid action: {action!r}. Allowed: {sorted(ALLOWED_ACTIONS)}"
        )

    if action == "ADD":
        _require_non_empty_product(product)
        _require_positive_int_quantity(quantity)

    elif action == "REMOVE":
        _require_non_empty_product(product)
        _require_positive_int_quantity(quantity)

    elif action == "CHECK":
        _require_non_empty_product(product)
        if quantity is not None:
            raise ValidationError("CHECK requires quantity to be null.")

    elif action == "LIST":
        if product is not None:
            raise ValidationError("LIST requires product to be null.")
        if quantity is not None:
            raise ValidationError("LIST requires quantity to be null.")

    elif action == "UNKNOWN":
        if product is not None:
            raise ValidationError("UNKNOWN requires product to be null.")
        if quantity is not None:
            raise ValidationError("UNKNOWN requires quantity to be null.")

    return {"action": action, "product": product, "quantity": quantity}


def _require_non_empty_product(product: Any) -> None:
    if not product or not isinstance(product, str) or not product.strip():
        raise ValidationError("Action requires a non-empty product name.")


def _require_positive_int_quantity(quantity: Any) -> None:
    if not isinstance(quantity, int) or quantity <= 0:
        raise ValidationError("Action requires a positive integer quantity.")
