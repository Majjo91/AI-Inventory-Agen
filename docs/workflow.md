# AI Inventory Agent — V0 Workflow

## 1. Purpose

The AI Inventory Agent is a simple L3 AI-assisted automation workflow for managing shop inventory through natural-language commands.

The shopkeeper can enter requests such as:

> I received 20 Coke

The AI interprets the request, the system validates the AI output, and a human approves inventory-changing actions before the database is modified.

---

## 2. V0 Scope

The goal of Version 0 is to demonstrate a simple and practical AI-assisted automation workflow.

The project intentionally avoids unnecessary complexity:

- No fancy UI
- No complex APIs
- No webhooks
- No cloud AI
- No n8n
- No autonomous L4 behavior

The V0 uses:

- Python
- Ollama
- Qwen 2.5 7B
- SQLite
- Human approval
- Automated tests

The focus is on demonstrating AI judgment, validation, human approval, automated action, persistent state, and failure handling.

---

## 3. Six-Part Architecture

### 3.1 Trigger

The workflow starts when the shopkeeper enters a natural-language message through the Python CLI.

Example:

> I received 20 Coke

### 3.2 Context

The system receives the shopkeeper's message.

When required, the workflow also uses the current inventory state stored in SQLite.

Example input:

```text
I received 20 Coke
```

### 3.3 Decision

The local Qwen 2.5 7B model running through Ollama interprets the natural-language request.

The AI converts the request into structured information.

Example:

```json
{
  "action": "ADD",
  "product": "Coke",
  "quantity": 20
}
```

Supported actions are:

- ADD
- REMOVE
- CHECK
- LIST
- UNKNOWN

The AI is responsible for interpretation, not directly changing the database.

### 3.4 Action

After validation and human approval where required, the inventory service performs the requested operation.

Possible operations include:

- Adding stock
- Removing stock
- Checking product stock
- Listing inventory

Example:

```text
ADD | product=Coke | quantity=20
```

The inventory service then updates the database.

### 3.5 State

The persistent inventory state is stored in a local SQLite database.

Database:

```text
database/inventory.db
```

Main tables:

- `inventory`
- `transactions`

The `inventory` table stores the current stock.

The `transactions` table records inventory changes.

### 3.6 Control

Inventory-changing actions require human confirmation before the database is modified.

Example:

```text
[AI] Interpreted: ADD | product=Coke | quantity=20

Confirm this action? (y/n):
```

If the user enters:

```text
y
```

the action is executed.

If the user enters:

```text
n
```

the action is cancelled and the database is not changed.

This creates an L3 workflow:

```text
AI proposes
     ↓
Human approves
     ↓
System acts
```

---

## 4. Complete Data Flow

```text
Shopkeeper
    |
    | Natural-language message
    v
Python CLI
    |
    v
Ollama / Qwen 2.5 7B
    |
    | Structured AI output
    v
AI Output Validator
    |
    | Validated action
    v
Human Approval
    |
    +------ No ------> Stop
    |
    | Yes
    v
Inventory Service
    |
    v
SQLite Repository
    |
    v
database/inventory.db
```

---

## 5. Happy Path Example

### Step 1 — Shopkeeper input

```text
I received 20 Coke
```

### Step 2 — AI interpretation

```text
[AI] Interpreted: ADD | product=Coke | quantity=20
```

### Step 3 — Human approval

```text
Confirm this action? (y/n): y
```

### Step 4 — Inventory action

The inventory service adds 20 Coke to the inventory.

### Step 5 — Result

```text
[OK] Added 20 Coke. New stock: 20.
```

### Step 6 — State

The updated stock is stored in:

```text
database/inventory.db
```

---

## 6. Remove Stock Example

### Input

```text
I sold 5 Coke
```

### AI interpretation

```text
[AI] Interpreted: REMOVE | product=Coke | quantity=5
```

### Human approval

```text
Confirm this action? (y/n): y
```

### Result

```text
[OK] Removed 5 Coke. New stock: 15.
```

The transaction is recorded in the SQLite database.

---

## 7. Failure Path — Insufficient Stock

Example:

```text
I sold 500 Coke
```

If the inventory contains only 20 Coke, the inventory service rejects the operation.

Example result:

```text
[Error] Insufficient stock.
```

The system does not allow the inventory quantity to become negative.

No invalid inventory state is written to the database.

---

## 8. Failure Path — Unrelated Request

The agent is designed specifically for inventory operations.

Example:

```text
Tell me a joke about computers
```

The AI does not identify this as an inventory operation.

Result:

```text
[AI] Request not understood. Please try again.
```

No inventory operation is performed.

Another example:

```text
What is the weather?
```

Result:

```text
[AI] Request not understood. Please try again.
```

---

## 9. Validation

The AI output is validated before reaching the inventory business logic.

The validator checks:

- The action is valid
- The product is valid when required
- The quantity is present when required
- The quantity is a positive integer
- CHECK and LIST actions do not contain an invalid quantity

This prevents malformed AI output from directly reaching the database layer.

---

## 10. Safety Boundary

The AI does not directly modify SQLite.

The workflow separates AI interpretation from deterministic execution:

```text
Natural Language
       ↓
AI Interpretation
       ↓
Validation
       ↓
Business Rules
       ↓
Human Approval
       ↓
Database Action
```

This reduces the risk of an incorrect AI interpretation causing an unwanted inventory change.

---

## 11. Components

| Component | Responsibility |
|---|---|
| Python CLI | Receives user input and displays results |
| Ollama | Runs the local AI model |
| Qwen 2.5 7B | Interprets natural-language inventory requests |
| AI Output Validator | Validates the structured AI response |
| Inventory Service | Applies inventory business rules |
| SQLite Repository | Performs database operations |
| SQLite Database | Stores persistent inventory state |
| Automated Tests | Verify normal and failure scenarios |

---

## 12. Testing

The project contains automated tests for:

- Adding inventory
- Removing inventory
- Checking stock
- Listing inventory
- Unknown requests
- Invalid AI output
- Negative quantities
- Zero quantities
- Insufficient stock
- Human cancellation
- Database protection

Current test result:

```text
Ran 47 tests

OK
```

Evidence screenshots are stored in:

```text
test/Evidence/
```

---

## 13. Autonomy Level

The Version 0 system follows an L3 approval model.

```text
L3 — AI proposes, human approves, system acts
```

The AI is not given unrestricted authority to modify inventory.

The human remains the final approval boundary for inventory-changing actions.

---

## 14. V0 Design Principle

The project intentionally keeps the automation simple.

The objective is not to build a large production platform. The objective is to demonstrate a complete AI-assisted automation workflow with:

- Natural-language interaction
- AI interpretation
- Structured output
- Deterministic validation
- Business rules
- Human approval
- Automated action
- Persistent state
- Failure handling
- Automated testing

This provides a small but complete example of an L3 AI-assisted automation workflow.