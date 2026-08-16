"""Tests for the AI output validation layer."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.validators import validate_ai_output, ValidationError


class TestValidateAiOutput(unittest.TestCase):
    """Unit tests for validate_ai_output."""

    # Valid cases
    def test_valid_add(self):
        result = validate_ai_output({"action": "ADD", "product": "Coke", "quantity": 20})
        self.assertEqual(result["action"], "ADD")
        self.assertEqual(result["product"], "Coke")
        self.assertEqual(result["quantity"], 20)

    def test_valid_remove(self):
        result = validate_ai_output({"action": "REMOVE", "product": "Pepsi", "quantity": 5})
        self.assertEqual(result["action"], "REMOVE")
        self.assertEqual(result["product"], "Pepsi")
        self.assertEqual(result["quantity"], 5)

    def test_valid_check(self):
        result = validate_ai_output({"action": "CHECK", "product": "biscuits", "quantity": None})
        self.assertEqual(result["action"], "CHECK")
        self.assertEqual(result["product"], "biscuits")
        self.assertIsNone(result["quantity"])

    def test_valid_list(self):
        result = validate_ai_output({"action": "LIST", "product": None, "quantity": None})
        self.assertEqual(result["action"], "LIST")
        self.assertIsNone(result["product"])
        self.assertIsNone(result["quantity"])

    def test_valid_unknown(self):
        result = validate_ai_output({"action": "UNKNOWN", "product": None, "quantity": None})
        self.assertEqual(result["action"], "UNKNOWN")

    # Invalid action
    def test_invalid_action(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "DELETE", "product": "Coke", "quantity": 5})

    # Key structure
    def test_missing_action_key(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"product": "Coke", "quantity": 5})

    def test_missing_product_key(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "ADD", "quantity": 5})

    def test_missing_quantity_key(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "ADD", "product": "Coke"})

    def test_extra_unexpected_key(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "ADD", "product": "Coke", "quantity": 5, "note": "extra"})

    def test_multiple_extra_keys(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "ADD", "product": "Coke", "quantity": 5, "note": "a", "source": "b"})

    # ADD invalid cases
    def test_add_empty_product(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "ADD", "product": "", "quantity": 5})

    def test_add_whitespace_product(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "ADD", "product": "   ", "quantity": 5})

    def test_add_non_integer_quantity(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "ADD", "product": "Coke", "quantity": "5"})

    def test_add_zero_quantity(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "ADD", "product": "Coke", "quantity": 0})

    def test_add_negative_quantity(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "ADD", "product": "Coke", "quantity": -5})

    # REMOVE invalid cases
    def test_remove_empty_product(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "REMOVE", "product": "", "quantity": 5})

    def test_remove_non_integer_quantity(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "REMOVE", "product": "Pepsi", "quantity": 5.5})

    def test_remove_zero_quantity(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "REMOVE", "product": "Pepsi", "quantity": 0})

    # CHECK invalid cases
    def test_check_empty_product(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "CHECK", "product": "   ", "quantity": None})

    def test_check_quantity_not_null(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "CHECK", "product": "Coke", "quantity": 5})

    # LIST invalid cases
    def test_list_quantity_not_null(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "LIST", "product": None, "quantity": 10})

    def test_list_product_not_null(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "LIST", "product": "Coke", "quantity": None})

    # UNKNOWN invalid cases
    def test_unknown_product_not_null(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "UNKNOWN", "product": "Coke", "quantity": None})

    def test_unknown_quantity_not_null(self):
        with self.assertRaises(ValidationError):
            validate_ai_output({"action": "UNKNOWN", "product": None, "quantity": 10})


if __name__ == "__main__":
    unittest.main()
