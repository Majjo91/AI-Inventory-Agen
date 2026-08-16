"""Tests for the inventory service layer."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.database.connection import get_connection
from src.database.schema import create_tables
from src.services.inventory_service import process_inventory_action


class TestInventoryService(unittest.TestCase):
    """Unit tests for process_inventory_action with a real in-memory SQLite DB."""

    @classmethod
    def setUpClass(cls):
        cls.conn = get_connection(":memory:")
        create_tables(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.conn.execute("DELETE FROM transactions")
        self.conn.execute("DELETE FROM inventory")
        self.conn.commit()

    def _valid(self, action, product=None, quantity=None):
        return {"action": action, "product": product, "quantity": quantity}

    # ADD
    def test_add_new_product(self):
        result = process_inventory_action(self.conn, self._valid("ADD", "Coke", 20))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "ADD")
        self.assertIn("New stock: 20", result["message"])
        self.assertEqual(result["data"]["new_quantity"], 20)

    def test_add_existing_product(self):
        self.conn.execute(
            "INSERT INTO inventory (name, category, unit, quantity, minimum_stock_level, price) VALUES (?, ?, ?, ?, ?, ?)",
            ("Pepsi", "Drinks", "pcs", 10, 5, 1.5),
        )
        self.conn.commit()
        result = process_inventory_action(self.conn, self._valid("ADD", "Pepsi", 5))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["new_quantity"], 15)

    # REMOVE
    def test_remove_success(self):
        self.conn.execute(
            "INSERT INTO inventory (name, category, unit, quantity, minimum_stock_level, price) VALUES (?, ?, ?, ?, ?, ?)",
            ("Biscuits", "Snacks", "pcs", 50, 10, 2.0),
        )
        self.conn.commit()
        result = process_inventory_action(self.conn, self._valid("REMOVE", "Biscuits", 10))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["new_quantity"], 40)

    def test_remove_product_not_found(self):
        result = process_inventory_action(self.conn, self._valid("REMOVE", "Water", 5))
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])

    def test_remove_insufficient_stock(self):
        self.conn.execute(
            "INSERT INTO inventory (name, category, unit, quantity, minimum_stock_level, price) VALUES (?, ?, ?, ?, ?, ?)",
            ("Chips", "Snacks", "pcs", 3, 2, 1.0),
        )
        self.conn.commit()
        result = process_inventory_action(self.conn, self._valid("REMOVE", "Chips", 5))
        self.assertEqual(result["status"], "error")
        self.assertIn("Insufficient stock", result["message"])

    # CHECK
    def test_check_existing_product(self):
        self.conn.execute(
            "INSERT INTO inventory (name, category, unit, quantity, minimum_stock_level, price) VALUES (?, ?, ?, ?, ?, ?)",
            ("Coke", "Drinks", "pcs", 100, 20, 1.5),
        )
        self.conn.commit()
        result = process_inventory_action(self.conn, self._valid("CHECK", "Coke"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["quantity"], 100)

    def test_check_product_not_found(self):
        result = process_inventory_action(self.conn, self._valid("CHECK", "Juice"))
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])

    # LIST
    def test_list_empty_inventory(self):
        result = process_inventory_action(self.conn, self._valid("LIST"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["data"]["inventory"]), 0)

    def test_list_with_items(self):
        self.conn.execute(
            "INSERT INTO inventory (name, category, unit, quantity, minimum_stock_level, price) VALUES (?, ?, ?, ?, ?, ?)",
            ("Coke", "Drinks", "pcs", 10, 5, 1.5),
        )
        self.conn.execute(
            "INSERT INTO inventory (name, category, unit, quantity, minimum_stock_level, price) VALUES (?, ?, ?, ?, ?, ?)",
            ("Pepsi", "Drinks", "pcs", 20, 5, 1.5),
        )
        self.conn.commit()
        result = process_inventory_action(self.conn, self._valid("LIST"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["data"]["inventory"]), 2)

    # UNKNOWN
    def test_unknown_action(self):
        result = process_inventory_action(self.conn, self._valid("UNKNOWN"))
        self.assertEqual(result["status"], "error")
        self.assertIn("not understood", result["message"])
        self.assertIsNone(result["data"])


if __name__ == "__main__":
    unittest.main()
