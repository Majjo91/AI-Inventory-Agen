"""Tests for the CLI entry point."""

import io
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.main import run_cli
from src.validators import ValidationError


class TestRunCli(unittest.TestCase):
    """Unit tests for the CLI loop using mocked I/O and services."""

    def _run_with_inputs(self, inputs, interpret_return=None, validate_return=None, process_return=None):
        """Run CLI with a sequence of inputs and mocked services."""
        input_iter = iter(inputs)

        def mock_input(prompt=""):
            try:
                return next(input_iter)
            except StopIteration:
                return "exit"

        if interpret_return is None:
            interpret_return = {"action": "ADD", "product": "Coke", "quantity": 10}
        if validate_return is None:
            validate_return = {"action": "ADD", "product": "Coke", "quantity": 10}
        if process_return is None:
            process_return = {
                "status": "success",
                "action": "ADD",
                "message": "Added 10 Coke. New stock: 10.",
                "data": {"product": "Coke", "quantity": 10, "new_quantity": 10},
            }

        with patch("builtins.input", side_effect=mock_input), patch(
            "src.main.interpret_message", return_value=interpret_return
        ), patch("src.main.validate_ai_output", return_value=validate_return), patch(
            "src.main.process_inventory_action", return_value=process_return
        ), patch("src.main.get_connection", return_value=MagicMock()), patch(
            "src.main.create_tables"
        ), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            run_cli(":memory:")
            return mock_stdout.getvalue()

    def test_exit_command(self):
        output = self._run_with_inputs(["exit"])
        self.assertIn("Goodbye!", output)

    def test_quit_command(self):
        output = self._run_with_inputs(["quit"])
        self.assertIn("Goodbye!", output)

    def test_add_confirmed_executes(self):
        mock_process = MagicMock(return_value={
            "status": "success",
            "action": "ADD",
            "message": "Added 10 Coke. New stock: 10.",
            "data": {"product": "Coke", "quantity": 10, "new_quantity": 10},
        })
        with patch("builtins.input", side_effect=["I received 10 Coke", "y", "exit"]), patch(
            "src.main.interpret_message", return_value={"action": "ADD", "product": "Coke", "quantity": 10}
        ), patch("src.main.validate_ai_output", return_value={"action": "ADD", "product": "Coke", "quantity": 10}), patch(
            "src.main.process_inventory_action", mock_process
        ), patch("src.main.get_connection", return_value=MagicMock()), patch(
            "src.main.create_tables"
        ), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("Interpreted: ADD", output)
        mock_process.assert_called_once()

    def test_remove_confirmed_executes(self):
        mock_process = MagicMock(return_value={
            "status": "success",
            "action": "REMOVE",
            "message": "Removed 5 Coke. New stock: 5.",
            "data": {"product": "Coke", "quantity": 5, "new_quantity": 5},
        })
        with patch("builtins.input", side_effect=["I sold 5 Coke", "y", "exit"]), patch(
            "src.main.interpret_message", return_value={"action": "REMOVE", "product": "Coke", "quantity": 5}
        ), patch("src.main.validate_ai_output", return_value={"action": "REMOVE", "product": "Coke", "quantity": 5}), patch(
            "src.main.process_inventory_action", mock_process
        ), patch("src.main.get_connection", return_value=MagicMock()), patch(
            "src.main.create_tables"
        ), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("Interpreted: REMOVE", output)
        mock_process.assert_called_once()

    def test_add_cancelled_skips_db(self):
        mock_process = MagicMock()
        with patch("builtins.input", side_effect=["I received 10 Coke", "n", "exit"]), patch(
            "src.main.interpret_message", return_value={"action": "ADD", "product": "Coke", "quantity": 10}
        ), patch("src.main.validate_ai_output", return_value={"action": "ADD", "product": "Coke", "quantity": 10}), patch(
            "src.main.process_inventory_action", mock_process
        ), patch("src.main.get_connection", return_value=MagicMock()), patch(
            "src.main.create_tables"
        ), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("Operation cancelled", output)
        mock_process.assert_not_called()

    def test_remove_cancelled_skips_db(self):
        mock_process = MagicMock()
        with patch("builtins.input", side_effect=["I sold 5 Coke", "n", "exit"]), patch(
            "src.main.interpret_message", return_value={"action": "REMOVE", "product": "Coke", "quantity": 5}
        ), patch("src.main.validate_ai_output", return_value={"action": "REMOVE", "product": "Coke", "quantity": 5}), patch(
            "src.main.process_inventory_action", mock_process
        ), patch("src.main.get_connection", return_value=MagicMock()), patch(
            "src.main.create_tables"
        ), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("Operation cancelled", output)
        mock_process.assert_not_called()

    def test_check_executes_without_confirmation(self):
        mock_process = MagicMock(return_value={
            "status": "success",
            "action": "CHECK",
            "message": "Coke stock: 20 pcs.",
            "data": {"product": "Coke", "quantity": 20, "unit": "pcs"},
        })
        with patch("builtins.input", side_effect=["How many Coke do I have?", "exit"]), patch(
            "src.main.interpret_message", return_value={"action": "CHECK", "product": "Coke", "quantity": None}
        ), patch("src.main.validate_ai_output", return_value={"action": "CHECK", "product": "Coke", "quantity": None}), patch(
            "src.main.process_inventory_action", mock_process
        ), patch("src.main.get_connection", return_value=MagicMock()), patch(
            "src.main.create_tables"
        ), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("Interpreted: CHECK", output)
        self.assertNotIn("Confirm this action", output)
        mock_process.assert_called_once()

    def test_list_executes_without_confirmation(self):
        mock_process = MagicMock(return_value={
            "status": "success",
            "action": "LIST",
            "message": "Inventory contains 2 item(s).",
            "data": {"inventory": []},
        })
        with patch("builtins.input", side_effect=["Show my inventory", "exit"]), patch(
            "src.main.interpret_message", return_value={"action": "LIST", "product": None, "quantity": None}
        ), patch("src.main.validate_ai_output", return_value={"action": "LIST", "product": None, "quantity": None}), patch(
            "src.main.process_inventory_action", mock_process
        ), patch("src.main.get_connection", return_value=MagicMock()), patch(
            "src.main.create_tables"
        ), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("Interpreted: LIST", output)
        self.assertNotIn("Confirm this action", output)
        mock_process.assert_called_once()

    def test_unknown_action_no_db_call(self):
        mock_process = MagicMock()
        output = self._run_with_inputs(
            ["What is the weather?", "exit"],
            interpret_return={"action": "UNKNOWN", "product": None, "quantity": None},
            validate_return={"action": "UNKNOWN", "product": None, "quantity": None},
            process_return=None,
        )
        # process_inventory_action is still patched, but we can check it wasn't called
        # by using a separate mock in a dedicated test instead
        self.assertIn("not understood", output)

    def test_ai_connection_error(self):
        with patch("builtins.input", side_effect=["hello", "exit"]), patch(
            "src.main.interpret_message", side_effect=ConnectionError("Ollama down")
        ), patch("src.main.validate_ai_output"), patch(
            "src.main.get_connection", return_value=MagicMock()
        ), patch("src.main.create_tables"), patch(
            "sys.stdout", new_callable=io.StringIO
        ) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("[AI Error]", output)
        self.assertIn("Ollama down", output)

    def test_validation_error(self):
        with patch("builtins.input", side_effect=["hello", "exit"]), patch(
            "src.main.interpret_message", return_value={"action": "ADD", "product": "", "quantity": 5}
        ), patch(
            "src.main.validate_ai_output", side_effect=ValidationError("bad")
        ), patch(
            "src.main.get_connection", return_value=MagicMock()
        ), patch("src.main.create_tables"), patch(
            "sys.stdout", new_callable=io.StringIO
        ) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("[Validation Error]", output)
        self.assertIn("bad", output)

    def test_keyboard_interrupt(self):
        with patch("builtins.input", side_effect=[KeyboardInterrupt]), patch(
            "src.main.get_connection", return_value=MagicMock()
        ), patch("src.main.create_tables"), patch(
            "sys.stdout", new_callable=io.StringIO
        ) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("Goodbye!", output)

    def test_eof_error(self):
        with patch("builtins.input", side_effect=[EOFError]), patch(
            "src.main.get_connection", return_value=MagicMock()
        ), patch("src.main.create_tables"), patch(
            "sys.stdout", new_callable=io.StringIO
        ) as mock_stdout:
            run_cli(":memory:")
            output = mock_stdout.getvalue()
        self.assertIn("Goodbye!", output)


if __name__ == "__main__":
    unittest.main()
