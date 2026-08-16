# AI Inventory Agent - Version 0

## Project Title
AI Inventory Agent for Small Shops

## Project Description
A lightweight, local-first inventory management assistant that lets shopkeepers manage stock using natural-language commands. The system uses a locally running LLM to interpret user intent, validates the output, and persists changes to SQLite.

## Project Objective
Enable a single shopkeeper to track inventory (add stock, remove stock, check levels, view full inventory) through simple conversational messages—without needing a complex UI or cloud services.

## Key Features
- **Natural-language inventory commands**: Type messages like "I sold 5 Coke" or "How many Pepsi do I have?"
- **ADD stock**: Receive new inventory and update quantities
- **REMOVE stock**: Record sales or usage and decrease quantities
- **CHECK stock**: Query the current quantity of a specific product
- **LIST inventory**: View all items currently in the database
- **UNKNOWN / non-inventory handling**: Out-of-scope messages are safely classified as UNKNOWN and do not modify state
- **AI output validation**: Strict schema and constraint checks on every model response before any database operation
- **Human confirmation**: State-changing operations (ADD / REMOVE) require explicit "y" approval before execution
- **SQLite persistence**: All inventory and transaction history is stored locally in `database/inventory.db`

## Six-Part Workflow Architecture

| Component | Role in This Project |
|-----------|---------------------|
| **Trigger** | Shopkeeper enters a natural-language inventory request in the CLI |
| **Context** | User message + current inventory state + business rules (minimum stock, non-negative stock) |
| **Decision** | Local Ollama model (`qwen2.5:7b-instruct`) interprets the message and returns structured JSON |
| **Action** | ADD, REMOVE, CHECK, or LIST operation executed against the database |
| **State** | SQLite (`inventory` and `transactions` tables) stores persistent inventory data |
| **Control** | AI output validation → business-rule validation → human confirmation → error handling |

## Technology Stack
- **Python 3**: Core language, standard library only (no extra runtime dependencies)
- **Ollama**: Local LLM runtime
- **Qwen2.5 7B Instruct**: Local model for natural-language interpretation
- **SQLite**: Embedded database for inventory and transaction history
- **VS Code**: Development environment
- **Kilo Code**: AI-assisted coding tool used during development

## Project Structure

```
AI-Inventory-Agent/
├── database/
│   └── inventory.db               # SQLite database file
├── docs/
│   └── architecture.md            # Version 0 architecture document
├── src/
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   ├── web_app.py                 # Streamlit web dashboard
│   ├── web_backend.py             # Web backend wrapper
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py          # SQLite connection factory
│   │   ├── schema.py              # Table DDL and migration helper
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── inventory_repo.py  # Data-access methods
│   ├── services/
│   │   ├── __init__.py
│   │   ├── nlp_service.py         # Ollama / Qwen interpretation layer
│   │   └── inventory_service.py   # Business logic for ADD / REMOVE / CHECK / LIST
│   └── validators/
│       ├── __init__.py
│       └── ai_output_validator.py # AI output schema and constraint validation
├── test/
│   ├── test_main.py
│   ├── test_nlp_service.py
│   ├── test_inventory_service.py
│   └── test_validators.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Python Environment
```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Ollama
Download and install Ollama from [ollama.com](https://ollama.com).

### 3. Qwen 2.5 7B Instruct
```bash
ollama pull qwen2.5:7b-instruct
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/generate -d "{\"model\":\"qwen2.5:7b-instruct\",\"prompt\":\"hi\",\"stream\":false}"
```

## How to Run

### CLI
```bash
python src/main.py
```

The CLI will display:
```
AI Inventory Agent - Version 0
Type 'exit' or 'quit' to leave.

> 
```

Type natural-language commands at the prompt. Type `exit` or `quit` to close.

### Web Dashboard
```bash
streamlit run src/web_app.py
```

This starts the Streamlit web interface locally. The dashboard will open in your browser (usually at `http://localhost:8501`).

From the web dashboard you can:
- Open the **Dashboard** page and type natural-language inventory commands in the AI Command box.
- View **Inventory** to see all products and stock levels.
- View **Transactions** to see the audit log of stock movements.
- Confirm or cancel ADD / REMOVE actions before they are applied.

## How to Run Tests

```bash
python -m unittest discover -s test -v
```

Expected output: **47 tests pass**.

## Example Interaction

```
AI Inventory Agent - Version 0
Type 'exit' or 'quit' to leave.

> I received 20 Coke
[AI] Interpreted: ADD | product=Coke | quantity=20
Confirm this action? (y/n): y
[OK] Added 20 Coke. New stock: 20.

> I sold 5 Coke
[AI] Interpreted: REMOVE | product=Coke | quantity=5
Confirm this action? (y/n): y
[OK] Removed 5 Coke. New stock: 15.

> How many Coke do I have?
[AI] Interpreted: CHECK | product=Coke | quantity=None
[OK] Coke stock: 15 pcs.

> show my inventory
[AI] Interpreted: LIST | product=None | quantity=None
[OK] Inventory contains 1 item(s).
Name                 Category          Qty Unit      Price
----------------------------------------------------------
Coke                 Uncategorized      15 pcs        0.00

> What is the weather?
[AI] Request not understood. Please try again.

> exit
Goodbye!
```

## Testing Summary
- **Total tests**: 47
- **Status**: All pass
- **Coverage**: NLP interpretation, AI output validation, inventory service business logic, and CLI flow

## Version 0 Limitations
- Single-user, single-machine operation
- No user authentication or multi-shop support
- No barcode scanning or image recognition
- No advanced reporting or analytics
- Ollama must be running locally with the model pulled
- First inference may be slow due to model loading into memory
- No n8n workflow orchestration (planned for future versions)
