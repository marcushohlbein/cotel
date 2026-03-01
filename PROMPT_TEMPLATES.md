# Quick Prompt Templates for AI Agents

## Template 1: Onboarding to New Codebase

```
I'm starting work on a new codebase. Help me understand its structure:

1. Run: repo-intel init && repo-intel index --project [project-name] --verbose
2. Run: repo-intel tool list-symbols --json | jq 'group_by(.kind) | map({kind: .[0].kind, count: length})'
3. Run: repo-intel tool list-symbols --kind endpoint --json
4. Run: repo-intel tool list-symbols --kind class --json

Then summarize:
- How many files/symbols?
- What are the main entry points?
- What are the core domain classes?
- What languages are used?
```

## Template 2: Finding Function Definition

```
User asks: "Where is [function-name] defined?"

Steps:
1. repo-intel tool find-symbol --name [function-name] --json
2. Extract: file_id, start_line, end_line
3. Map file_id to actual file path (use repo-intel tool list-symbols if needed)
4. Use Read tool to show the code at that location

Response format:
"The function [name] is defined in [file] at line [X]. Here's the code:
[code snippet]"
```

## Template 3: Understanding Dependencies

```
User asks: "What does [function-name] depend on?" or "What calls [function-name]?"

Steps:
1. repo-intel tool find-symbol --name [function-name] --json
2. repo-intel tool get-callees --name [function-name] --json
   - Shows what [function-name] calls
3. repo-intel tool get-callers --name [function-name] --json
   - Shows what calls [function-name]

Response format:
"[function-name] is called by:
- [caller1] in [file1]
- [caller2] in [file2]

[function-name] calls:
- [callee1] in [file3]
- [callee2] in [file4]"
```

## Template 4: Finding API Endpoints

```
User asks: "What API endpoints exist?" or "Find all routes"

Steps:
1. repo-intel tool list-symbols --kind endpoint --json
2. Format as table or list:
   - HTTP Method
   - Path
   - Handler function
   - File location

Response format:
"Found [N] API endpoints:
- GET /api/users → get_users() in users.py:15
- POST /api/users → create_user() in users.py:45
- GET /api/users/:id → get_user() in users.py:65"
```

## Template 5: Impact Analysis

```
User asks: "What happens if I change [class/function]?" or "What depends on X?"

Steps:
1. repo-intel tool find-symbol --name [X] --json
2. repo-intel tool get-callers --name [X] --json
3. repo-intel tool get-callees --name [X] --json

Response format:
"Changing [X] would affect:
Direct callers ([N] functions):
- [caller1] in [file1]
- [caller2] in [file2]

[X] uses these ([M] functions):
- [callee1] in [file3]
- [callee2] in [file4]

Recommendation: Review these [N+M] locations before modifying [X]."
```

## Template 6: Exploring Domain Model

```
User asks: "What are the main classes/models?" or "Show me the domain model"

Steps:
1. repo-intel tool list-symbols --kind class --json
2. Group by file or module
3. Identify core domain classes (User, Order, Product, etc.)
4. Show inheritance patterns (if supported)

Response format:
"Domain classes found:
User (users/models.py:15)
Order (orders/models.py:20)
Product (products/models.py:10)

Inheritance:
- AdminUser extends User
- PremiumOrder extends Order"
```

## Template 7: Finding Unused Code

```
User asks: "Is [function] used anywhere?" or "Find dead code"

Steps:
1. repo-intel tool find-symbol --name [function] --json
2. repo-intel tool get-callers --name [function] --json

Response:
- If callers is empty: "[function] appears unused (no callers found)"
- If callers exist: "[function] is used by [N] functions: [list]"
```

## Template 8: Multi-Language Projects

```
User asks: "What languages are in this codebase?" or "Show me the tech stack"

Steps:
1. repo-intel tool list-symbols --json | jq 'group_by(.language) | map({lang: .[0].language, count: length})'

Response format:
"Languages detected:
- Python: [N] symbols
- JavaScript: [M] symbols
- TypeScript: [K] symbols

Backend: Python (Flask API)
Frontend: TypeScript (React)"
```

## Template 9: Finding Tests

```
User asks: "Find tests for [function/class]"

Steps:
1. repo-intel tool find-symbol --name [function] --json
2. repo-intel tool list-symbols --json | jq '.[] | select(.name | test("test|Test|spec|Spec"))'

Alternative: Search for test files
repo-intel tool list-symbols --json | jq '.[] | select(.file_id | contains("test"))'
```

## Template 10: Locating Configuration

```
User asks: "Where is the config/database setup?"

Steps:
1. repo-intel tool list-symbols --json | jq '.[] | select(.name | test("config|Config|settings|Settings|database|Database"; "i"))'
2. repo-intel tool find-symbol --name Config --json

Response format:
"Configuration found:
- Config class in config/settings.py:10
- Database class in db/connection.py:5
- Settings in app/config.py:20"
```

## Template 11: Verifying Index is Current

```
Always check before querying:

Check: ls .repo-intel/index.db exists
If not exists: repo-intel index --project NAME
If modified code recently: repo-intel index --project NAME (updates incrementally)
```

## Template 12: Error Handling Patterns

```
Pattern: "No symbols found"

Error message: "[]"

Possible causes:
1. Not indexed → Solution: repo-intel index --project NAME
2. Language not supported → Check list: Python, JS, TS, Java, Rust, Go, PHP
3. Different symbol name → Search: repo-intel tool list-symbols --json | jq '.[].name'
```

## Context for Agent Memory

Add to agent's context:

```
<repo-intel-capabilities>
I have access to repo-intel, a structural code intelligence tool.

Capabilities:
- Symbol extraction (functions, classes, methods, interfaces)
- Call graph analysis (who calls what)
- Dependency tracking
- HTTP endpoint detection
- Multi-language support (Python, JS, TS, Java, Rust, Go, PHP)

Best uses:
- Finding where code is defined
- Understanding code relationships
- Exploring codebases quickly
- Impact analysis before changes

NOT for:
- Reading implementation details (use Read tool)
- Text search (use Grep tool)
- Semantic understanding (read and analyze)

Always:
1. Ensure codebase is indexed first
2. Use --json flag for output
3. Combine with Read/Edit tools as needed
</repo-intel-capabilities>
```

## Example Conversation Flow

**User**: "I need to understand the payment processing flow"

**Agent**:
```bash
# Index if needed
repo-intel index --project myapp

# Find payment-related symbols
repo-intel tool list-symbols --json | \
  jq '.[] | select(.name | test("payment|Payment"; "i"))'

# Find the main payment processor
repo-intel tool find-symbol --name PaymentService --json

# Understand the call graph
repo-intel tool get-callees --name PaymentService --json
repo-intel tool get-callers --name processPayment --json
```

**Response**:
"I found the payment processing flow:

**PaymentService** (services/payment.py:15)
- Called by: CheckoutController, AdminController
- Calls: StripeGateway, PayPalGateway, PaymentValidator

**Main entry points**:
- POST /api/payments → processPayment()
- GET /api/payments/:id → getPaymentStatus()

Would you like me to read the implementation of any of these?"
```
