# Runbook - AI Inventory Agent Version 0

## Purpose
This runbook provides step-by-step operational instructions for running, testing, and troubleshooting the AI Inventory Agent in a local development environment.

---

## 1. Prerequisites

| Component | Requirement |
|-----------|-------------|
| Python | 3.9+ |
| Ollama | Installed and running |
| Model | `qwen2.5:7b-instruct` pulled |
| OS | Windows, macOS, or Linux |

---

## 2. Environment Setup

```bash
# Clone / open the project
cd C:\Users\syedm\Desktop\AI-Inventory-Agent

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 3. Start Ollama

```bash
# Start Ollama service (if not already running)
ollama serve

# In a separate terminal, verify the model is available
ollama list
```

Expected output includes:
```
qwen2.5:7b-instruct
```

---

## 4. Initialize Database

```bash
python -c "from src.database.schema import create_tables; create_tables()"
```

This creates `database/inventory.db` with the `inventory` and `transactions` tables.

---

## 5. Run the Application

```bash
python src/main.py
```

Expected output:
```
AI Inventory Agent - Version 0
Type 'exit' or 'quit' to leave.

> 
```

---

## 6. Example Session

```
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

---

## 7. Run Tests

```bash
python -m unittest discover -s test -v
```

Expected result: **47 tests pass**.

Individual test modules:
```bash
python -m unittest test.test_nlp_service -v
python -m unittest test.test_validators -v
python -m unittest test.test_inventory_service -v
python -m unittest test.test_main -v
```

---

## 8. Troubleshooting

### 8.1 Ollama Connection Timeout
**Symptom**: `[AI Error] Ollama request timed out after 60s.`

**Resolution**:
- Verify Ollama is running: `curl http://localhost:11434`
- Verify model is pulled: `ollama list`
- Check firewall allows port 11434
- If using a VPN or proxy, ensure localhost traffic is excluded

### 8.2 Model Not Found
**Symptom**: `model "qwen2.5:7b-instruct" not found`

**Resolution**:
```bash
ollama pull qwen2.5:7b-instruct
```

### 8.3 ModuleNotFoundError: No module named 'src'
**Symptom**: Python cannot find the `src` package.

**Resolution**: Run from the project root:
```bash
cd C:\Users\syedm\Desktop\AI-Inventory-Agent
python src/main.py
```

Or use the module syntax:
```bash
python -m src.main
```

### 8.4 Database Locked / Permission Denied
**Symptom**: `sqlite3.OperationalError: database is locked`

**Resolution**:
- Close any other processes accessing `database/inventory.db`
- Delete `database/inventory.db` and re-run schema initialization

### 8.5 Slow First Inference
**Symptom**: First AI response takes 30-60 seconds.

**Resolution**: Normal behavior. The model loads into memory on first request. Subsequent requests are faster.

---

## 9. Quick Reference Commands

| Task | Command |
|------|---------|
| Run app | `python src/main.py` |
| Run all tests | `python -m unittest discover -s test -v` |
| Init DB | `python -c "from src.database.schema import create_tables; create_tables()"` |
| Pull model | `ollama pull qwen2.5:7b-instruct` |
| Start Ollama | `ollama serve` |
| Check Ollama | `curl http://localhost:11434` |
