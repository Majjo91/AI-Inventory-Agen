"""Tests for the NLP interpretation layer."""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.nlp_service import interpret_message


class TestInterpretMessage(unittest.TestCase):
    """Unit tests for interpret_message using mocked Ollama responses."""

    def _mock_ollama_response(self, action, product, quantity):
        """Build a fake Ollama JSON response."""
        response_data = {"action": action, "product": product, "quantity": quantity}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": json.dumps(response_data)}
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    @patch("src.services.nlp_service.requests.post")
    def test_received_stock(self, mock_post):
        mock_post.return_value = self._mock_ollama_response("ADD", "Coke", 20)
        result = interpret_message("I received 20 Coke")
        self.assertEqual(result["action"], "ADD")
        self.assertEqual(result["product"], "Coke")
        self.assertEqual(result["quantity"], 20)

    @patch("src.services.nlp_service.requests.post")
    def test_sold_stock(self, mock_post):
        mock_post.return_value = self._mock_ollama_response("REMOVE", "Pepsi", 5)
        result = interpret_message("I sold 5 Pepsi")
        self.assertEqual(result["action"], "REMOVE")
        self.assertEqual(result["product"], "Pepsi")
        self.assertEqual(result["quantity"], 5)

    @patch("src.services.nlp_service.requests.post")
    def test_check_stock(self, mock_post):
        mock_post.return_value = self._mock_ollama_response("CHECK", "biscuits", None)
        result = interpret_message("How many biscuits do I have?")
        self.assertEqual(result["action"], "CHECK")
        self.assertEqual(result["product"], "biscuits")
        self.assertIsNone(result["quantity"])

    @patch("src.services.nlp_service.requests.post")
    def test_list_inventory(self, mock_post):
        mock_post.return_value = self._mock_ollama_response("LIST", None, None)
        result = interpret_message("Show me my inventory")
        self.assertEqual(result["action"], "LIST")
        self.assertIsNone(result["product"])
        self.assertIsNone(result["quantity"])

    @patch("src.services.nlp_service.requests.post")
    def test_unknown_action_from_model(self, mock_post):
        mock_post.return_value = self._mock_ollama_response("UNKNOWN", None, None)
        result = interpret_message("What is the weather today?")
        self.assertEqual(result["action"], "UNKNOWN")
        self.assertIsNone(result["product"])
        self.assertIsNone(result["quantity"])

    @patch("src.services.nlp_service.requests.post")
    def test_unrelated_message_returns_unknown(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": "The weather is sunny today."}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        result = interpret_message("What is the weather?")
        self.assertEqual(result["action"], "UNKNOWN")
        self.assertIsNone(result["product"])
        self.assertIsNone(result["quantity"])

    @patch("src.services.nlp_service.requests.post")
    def test_joke_message_returns_unknown(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": "Why did the computer catch a cold? It had a virus!"}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        result = interpret_message("Tell me a joke about a computer")
        self.assertEqual(result["action"], "UNKNOWN")
        self.assertIsNone(result["product"])
        self.assertIsNone(result["quantity"])


if __name__ == "__main__":
    unittest.main()
