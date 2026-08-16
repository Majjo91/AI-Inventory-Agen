# Project Schema - AI Inventory Agent Version 0

## 1. Database Schema

### 1.1 `inventory` Table
Stores product master data and current stock levels.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique item identifier |
| `name` | TEXT | NOT NULL | Product name |
| `category` | TEXT | NOT NULL | Product category |
| `unit` | TEXT | NOT NULL DEFAULT 'pcs' | Unit of measurement |
| `quantity` | INTEGER | NOT NULL DEFAULT 0 CHECK(quantity >= 0) | Current stock quantity |
| `minimum_stock_level` | INTEGER | NOT NULL DEFAULT 0 | Low-stock threshold |
| `price` | REAL | NOT NULL DEFAULT 0.0 | Unit price |
| `created_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Record creation timestamp |
| `updated_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Last update timestamp |

**Indexes:**
- `idx_inventory_name` on `name`

### 1.2 `transactions` Table
Audit log for all stock changes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique transaction ID |
| `item_id` | INTEGER | NOT NULL | Foreign key to `inventory.id` |
| `type` | TEXT | NOT NULL CHECK(type IN ('ADD', 'REMOVE')) | Transaction direction |
| `quantity` | INTEGER | NOT NULL CHECK(quantity > 0) | Quantity moved |
| `note` | TEXT | NULL | Optional description |
| `timestamp` | TEXT | NOT NULL DEFAULT (datetime('now')) | When the transaction occurred |

**Indexes:**
- `idx_transactions_item_id` on `item_id`
- `idx_transactions_timestamp` on `timestamp`

**Foreign Keys:**
- `item_id` → `inventory(id)` ON DELETE CASCADE

### 1.3 Entity Relationship

```
inventory (1) ────< transactions (*)
   id                    item_id
```

Each inventory item can have zero or more transaction records. Deleting an item cascades to its transactions.

---

## 2. Application Architecture Schema

### 2.1 Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI (main.py)                        │
│  - User input loop                                          │
│  - Exit / quit handling                                     │
│  - Human confirmation for ADD / REMOVE                      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Services Layer                            │
│  ┌──────────────────┐          ┌────────────────────────┐  │
│  │ nlp_service.py   │          │ inventory_service.py   │  │
│  │ - interpret_msg  │          │ - process_inventory_   │  │
│  │   ()             │          │   action()             │  │
│  │ - calls Ollama   │          │ - business logic       │  │
│  └────────┬─────────┘          │ - calls repositories   │  │
│           │                    └───────────┬────────────┘  │
│           ▼                                │                │
│  ┌──────────────────┐                     │                │
│  │ validators/      │                     │                │
│  │ - validate_      │                     │                │
│  │   ai_output()    │                     │                │
│  └──────────────────┘                     │                │
└────────────────────────────────────────────┼────────────────┘
                                             │
                                             ▼
                              ┌────────────────────────┐
                              │ Repositories           │
                              │ inventory_repo.py      │
                              │ - SQL queries only     │
                              └───────────┬────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │ Database Layer         │
                              │ connection.py          │
                              │ schema.py              │
                              └───────────┬────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │ SQLite                 │
                              │ database/inventory.db  │
                              │ - inventory table      │
                              │ - transactions table   │
                              └────────────────────────┘
```

### 2.2 Data Flow Schema

```
User Input (natural language)
    │
    ▼
interpret_message() ──────► Ollama (qwen2.5:7b-instruct)
    │                           │
    │  structured JSON          │
    ◄───────────────────────────┘
    │
    ▼
validate_ai_output() ──► ValidationError? (yes → reject)
    │
    ▼
process_inventory_action()
    │
    ├── ADD ──► find_item() / add_item() ──► update_stock() ──► record_transaction()
    ├── REMOVE ──► find_item() ──► update_stock() ──► record_transaction()
    ├── CHECK ──► find_item() ──► return stock level
    ├── LIST ──► list_inventory() ──► return all items
    └── UNKNOWN ──► return error message (no DB changes)
    │
    ▼
SQLite (inventory.db)
```

### 2.3 Module Dependency Schema

```
src/
├── main.py
│   ├── imports: database.connection
│   ├── imports: database.schema
│   ├── imports: services.nlp_service (interpret_message)
│   ├── imports: validators (validate_ai_output, ValidationError)
│   └── imports: services.inventory_service (process_inventory_action)
│
├── services/
│   ├── nlp_service.py
│   │   └── imports: requests (external)
│   └── inventory_service.py
│       └── imports: database.repositories.inventory_repo
│
├── validators/
│   └── ai_output_validator.py
│       └── imports: typing (stdlib)
│
└── database/
    ├── connection.py
    │   └── imports: sqlite3 (stdlib)
    ├── schema.py
    │   └── imports: database.connection
    └── repositories/
        └── inventory_repo.py
            └── imports: database.connection
```

---

## 3. Test Schema

| Module | File | Tests | Status |
|--------|------|-------|--------|
| NLP Service | `test/test_nlp_service.py` | 7 | Pass |
| Validators | `test/test_validators.py` | 17 | Pass |
| Inventory Service | `test/test_inventory_service.py` | 10 | Pass |
| CLI | `test/test_main.py` | 13 | Pass |
| **Total** | | **47** | **All pass** |

---

## 4. Configuration Schema

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `qwen2.5:7b-instruct` | Model name for interpretation |

---

## 5. Version 0 Scope Boundary

```
IN SCOPE:
  - Single-user CLI
  - Natural-language interpretation via Ollama
  - SQLite persistence
  - ADD / REMOVE / CHECK / LIST / UNKNOWN
  - Human confirmation for state changes
  - AI output validation
  - Unit tests

OUT OF SCOPE (future versions):
  - n8n workflow orchestration
  - Web / mobile UI
  - Multi-user authentication
  - Barcode / image recognition
  - Advanced analytics
```
