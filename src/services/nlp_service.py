"""AI interpretation layer using local Ollama model."""

import json
import os
from typing import Any, Dict, Optional

import requests


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

_PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "prompt", "cp02-v1.txt")
with open(_PROMPT_FILE, "r", encoding="utf-8") as _f:
    SYSTEM_PROMPT = _f.read()


def interpret_message(message: str) -> Dict[str, Any]:
    """Interpret a natural-language inventory message into structured JSON.

    Args:
        message: The shopkeeper's natural-language input.

    Returns:
        Dictionary with keys: action, product, quantity.

    Raises:
        ConnectionError: If Ollama is unreachable.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": message,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0,
            "num_ctx": 2048,
        },
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=60,
            proxies={"http": None, "https": None},
        )
        response.raise_for_status()
    except requests.ConnectionError as exc:
        raise ConnectionError(
            f"Cannot connect to Ollama at {OLLAMA_URL}. Is it running?"
        ) from exc
    except requests.Timeout as exc:
        raise ConnectionError(
            f"Ollama request timed out after 60s."
        ) from exc

    result = response.json()
    raw_text = result.get("response", "").strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "action": "UNKNOWN",
            "product": None,
            "quantity": None,
        }

    action = data.get("action", "UNKNOWN")
    if action not in ("ADD", "REMOVE", "CHECK", "LIST", "UNKNOWN"):
        action = "UNKNOWN"

    return {
        "action": action,
        "product": data.get("product"),
        "quantity": data.get("quantity"),
    }
