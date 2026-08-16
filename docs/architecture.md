# AI Inventory Agent - Version 0 Architecture

## Six-Part Workflow Mapping

### 1. Trigger
Shopkeeper enters a natural-language inventory request via the CLI (future: WhatsApp, Telegram, or web UI).

### 2. Context
- **User message**: raw natural-language text
- **Inventory state**: current stock levels, product names, units
- **Transaction history**: past ADD/REMOVE records
- **Business rules**: minimum stock levels, non-negative stock constraint

### 3. Decision
Local Ollama instance running **Qwen 2.5 7B Instruct** interprets the message and produces structured JSON:

```json
{
  "action": "REMOVE",
  "product": "Coke",
  "quantity": 5
}
```

Allowed actions: `ADD`, `REMOVE`, `CHECK`, `LIST`, `UNKNOWN`

### 4. Action
Based on the interpreted action:
- **ADD**: create product if new, increase stock, record transaction
- **REMOVE**: decrease stock, record transaction
- **CHECK**: return current stock level
- **LIST**: return full inventory
- **UNKNOWN**: no database changes, return error message

### 5. State
SQLite database (`database/inventory.db`) persists:
- `inventory` table: items, quantities, categories, prices, timestamps
- `transactions` table: audit log of all stock changes

### 6. Control
- **AI output validation**: schema and constraint checks on interpreted JSON
- **Business-rule validation**: positive quantities, sufficient stock, valid actions
- **Human approval**: shopkeeper reviews confirmation before action is finalized
- **Error handling**: clear messages for unknown actions, missing products, insufficient stock

---

## ASCII Architecture Diagram

```
+-------------------+     +-------------------+     +-------------------+
|     Trigger       |     |     Context       |     |    Decision       |
|                   |     |                   |     |                   |
|  Shopkeeper input |---->|  User message     |---->|  Ollama / Qwen    |
|  "I sold 5 Coke"  |     |  Inventory state  |     |  2.5 7B Instruct  |
+-------------------+     |  Business rules   |     +-------------------+
                          +-------------------+               |
                                    |                         |
                                    v                         v
                          +---------------------------------------+
                          |           Control                     |
                          |  - AI output validation               |
                          |  - Business-rule validation           |
                          |  - Human approval                     |
                          |  - Error handling                     |
                          +---------------------------------------+
                                    |
                                    v
                          +-------------------+
                          |      Action       |
                          |                   |
                          |  ADD / REMOVE /   |
                          |  CHECK / LIST     |
                          +-------------------+
                                    |
                                    v
                          +-------------------+
                          |      State        |
                          |                   |
                          |   SQLite DB       |
                          |  - inventory      |
                          |  - transactions   |
                          +-------------------+
```

---

## Happy-Path Example

**Input**: `"I sold 5 Coke"`

1. **Trigger**: Shopkeeper types the message.
2. **Context**: System captures the text; current inventory shows Coke with 20 units.
3. **Decision**: Ollama returns `{"action": "REMOVE", "product": "Coke", "quantity": 5}`.
4. **Control**: Validator confirms action is valid; business logic checks stock (20 >= 5).
5. **Action**: Remove 5 Coke; new stock = 15. Record transaction.
6. **State**: SQLite updates `inventory.quantity` to 15 and inserts a `REMOVE` transaction record.
7. **Output**: `"Removed 5 Coke. New stock: 15."`

---

## Failure-Path Example

**Input**: `"I sold 500 Coke"` (only 20 available)

1. **Trigger**: Shopkeeper types the message.
2. **Context**: Current inventory shows Coke with 20 units.
3. **Decision**: Ollama returns `{"action": "REMOVE", "product": "Coke", "quantity": 500}`.
4. **Control**: Validator confirms action is valid; business logic checks stock (20 < 500).
5. **Action**: Rejected at business-rule layer. No database changes.
6. **State**: SQLite remains unchanged.
7. **Output**: `"Insufficient stock for 'Coke'. Current: 20, Requested: 500."`

---

## Implementation Status

### Already Implemented
- SQLite database layer (`src/database/`)
  - Connection factory with WAL mode
  - Schema for `inventory` and `transactions` tables
  - Repository methods: `find_item`, `add_item`, `update_stock`, `record_transaction`, `list_inventory`
  - Negative stock prevention at schema and business-logic levels
- AI interpretation layer (`src/services/nlp_service.py`)
  - Ollama API integration with Qwen 2.5 7B
  - Structured JSON output with few-shot prompting
- AI output validation layer (`src/validators/`)
  - Schema validation for all 5 actions
  - Constraint checking (positive quantity, non-empty product, null checks)
- Inventory service layer (`src/services/inventory_service.py`)
  - Business logic for ADD, REMOVE, CHECK, LIST, UNKNOWN
  - Auto-create products on first ADD
  - Transaction recording
- Unit tests
  - `test/test_nlp_service.py` (5 tests)
  - `test/test_validators.py` (17 tests)
  - `test/test_inventory_service.py` (10 tests)

### Still To Be Built
- CLI entry point (`src/main.py`) for shopkeeper interaction
- Human approval flow before executing REMOVE actions
- Error handling and user-friendly message formatting
- Configuration management (`.env` support)
- README with setup and usage instructions
- n8n integration (future, not in Version 0)

---

## Version 0 Scope

Version 0 is a **single-user CLI assistant** for a small shop. It demonstrates the full six-part workflow with local AI, SQLite persistence, and strict validation. n8n orchestration and multi-channel triggers are deferred to future versions.
