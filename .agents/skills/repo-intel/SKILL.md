---
name: repo-intel
description: Structural intelligence for code repositories. Use repo-intel when you need to understand code structure, find symbols, trace call graphs, analyze dependencies, or explore inheritance hierarchies across multiple languages (Python, JavaScript, TypeScript, Java, Rust, Go, PHP). Auto-activates when analyzing code architecture, finding function definitions, understanding code relationships, or exploring large codebases.
activation-triggers:
  - Find all classes in this codebase
  - What functions call this function
  - Show me all HTTP endpoints
  - Where is this function defined
  - What calls this method
  - Find dependencies of this module
  - Show call graph for this function
  - List all classes that inherit from
  - What functions are defined in this file
  - Find all endpoints in the API
  - Trace the call hierarchy
  - What other files depend on this
  - Show me the inheritance chain
  - Find implementations of this interface
  - Analyze the code structure
  - Map out the dependencies
  - What uses this class
  - Find the definition of
  - Explore the codebase structure
---

# repo-intel: Structural Intelligence Skill

repo-intel provides **structural intelligence** over code repositories. It enables you to reason about code without reading entire files, making analysis faster and more accurate.

## Quick Start

```bash
# Initialize (optional - auto-creates if needed)
repo-intel init

# Index the codebase
repo-intel index --project myproject --verbose

# Query symbols
repo-intel tool list-symbols --json
repo-intel tool find-symbol --name MyClass --json
repo-intel tool get-callers --name myFunction --json
repo-intel tool get-callees --name myFunction --json
```

## What repo-intel Provides

### 1. Symbol Extraction
Extract functions, classes, methods, interfaces, and endpoints from code:

**Supported Languages:**
- ✅ Python (Flask, FastAPI)
- ✅ JavaScript (Express)
- ✅ TypeScript (Express)
- ✅ Java (Spring Boot)
- ✅ Rust
- ✅ Go
- ✅ PHP (Laravel)

**Symbol Types:**
- `function` - Standalone functions
- `class` - Classes and structs
- `method` - Class methods
- `interface` - Interfaces and traits
- `endpoint` - HTTP endpoints (detected automatically)

### 2. Call Graph Analysis
Trace function call relationships:

```
Function A calls → Function B, Function C
Function B calls → Function D
```

Useful for:
- Understanding execution flow
- Finding impact of changes
- Tracing bugs to their source
- Analyzing complexity

### 3. Dependency Tracking
Track what imports what:

```
moduleA.py imports → moduleB, moduleC
MyClass.java imports → OtherClass, List, Map
```

### 4. Inheritance Graph
Trace class hierarchies:

```
SubClass extends → BaseClass
MyInterface implements → OtherInterface
```

### 5. HTTP Endpoints
Automatically detect API endpoints:

**Python (Flask/FastAPI):**
```python
@app.route('/api/users', methods=['GET'])
def get_users():
    pass
```
→ Detected as: `GET /api/users`

**JavaScript (Express):**
```javascript
app.get('/users', (req, res) => { });
```
→ Detected as: `GET /users`

**Java (Spring):**
```java
@GetMapping("/api/data")
public List<Data> getData() { }
```
→ Detected as: `GET /api/data`

## When to Use repo-intel

### ✅ Use When:

1. **Exploring a new codebase**
   - "What does this codebase contain?"
   - "Show me all classes in this project"
   - "What endpoints are exposed?"

2. **Understanding code relationships**
   - "What calls this function?"
   - "What does this function call?"
   - "Where is this class used?"

3. **Analyzing impact**
   - "What will break if I change this?"
   - "Who depends on this module?"
   - "What uses this function?"

4. **Finding definitions**
   - "Where is this function defined?"
   - "Show me the class definition"
   - "Find all implementations of this"

5. **Tracing execution flow**
   - "How does this request get handled?"
   - "Trace the call chain for this"
   - "What's the execution path?"

6. **Understanding architecture**
   - "Show me the class hierarchy"
   - "What are the main components?"
   - "Map the dependencies"

### ❌ Don't Use For:

1. **Reading file contents** → Use `Read` tool
2. **Searching for text patterns** → Use `grep` or `Glob`
3. **Running code** → Use `Bash` to execute
4. **Git operations** → Use `git` commands
5. **File operations** → Use standard file tools

## The 5 Key Tools

### 1. `list-symbols` - Discover What Exists

List all symbols, optionally filtered by kind:

```bash
# List everything
repo-intel tool list-symbols --json

# Filter by kind
repo-intel tool list-symbols --kind function --json
repo-intel tool list-symbols --kind class --json
repo-intel tool list-symbols --kind endpoint --json
repo-intel tool list-sycles --kind interface --json
```

**Use when:**
- "What's in this codebase?"
- "Show me all classes"
- "What endpoints exist?"
- "List all functions"

**Example output:**
```json
[
  {
    "name": "UserService",
    "kind": "class",
    "language": "java",
    "start_line": 15,
    "end_line": 45
  },
  {
    "name": "getUsers",
    "kind": "endpoint",
    "http_method": "GET",
    "path": "/api/users"
  }
]
```

### 2. `find-symbol` - Locating Specific Definitions

Find a specific symbol by name:

```bash
repo-intel tool find-symbol --name MyClass --json
repo-intel tool find-symbol --name processPayment --json
```

**Use when:**
- "Where is this function?"
- "Find the class definition"
- "Show me this symbol"

**Example output:**
```json
{
  "name": "UserService",
  "kind": "class",
  "language": "java",
  "file_id": "abc-123",
  "start_line": 15,
  "end_line": 45
}
```

### 3. `get-callers` - What Calls This?

Find symbols that call a given function:

```bash
repo-intel tool get-callers --name myFunction --json
```

**Use when:**
- "Who calls this function?"
- "What uses this method?"
- "Where is this called from?"

**Example output:**
```json
[
  {
    "name": "handleRequest",
    "kind": "function",
    "file_id": "def-456"
  }
]
```

### 4. `get-callees` - What Does This Call?

Find what a function calls:

```bash
repo-intel tool get-callees --name myFunction --json
```

**Use when:**
- "What does this function call?"
- "What are the dependencies?"
- "Trace execution flow"

### 5. `get-dependencies` - Import Tracking

Track file dependencies (imports):

```bash
repo-intel tool get-dependencies --name MyModule --json
```

**Use when:**
- "What does this import?"
- "What are the module dependencies?"
- "Show the import chain"

## Practical Examples

### Example 1: Exploring a New Codebase

**Scenario:** You just joined a project and need to understand its structure.

```bash
# Step 1: Index the codebase
repo-intel index --project myproject -v

# Step 2: Get overview
repo-intel tool list-symbols --json | jq 'group_by(.kind) | map({kind: .[0].kind, count: length})'

# Output:
# [{"kind": "class", "count": 45}, {"kind": "function", "count": 120}]

# Step 3: Find main classes
repo-intel tool list-symbols --kind class --json | jq '.[].name'

# Step 4: Find all API endpoints
repo-intel tool list-symbols --kind endpoint --json | jq '.[] | {name, path, http_method}'
```

### Example 2: Understanding Impact of Changes

**Scenario:** You need to modify a critical function and want to know what will break.

```bash
# Step 1: Find the function
repo-intel tool find-symbol --name processPayment --json

# Step 2: Find all callers
repo-intel tool get-callers --name processPayment --json

# Output shows 5 functions call processPayment:
# - handleCheckout
# - processRefund
# - validateTransaction
# - ... etc

# Step 3: Decision: Need to test all these callers after changes
```

### Example 3: Tracing a Bug

**Scenario:** A bug in `validateUser` - need to trace where it's called from.

```bash
# Step 1: Find the function
repo-intel tool find-symbol --name validateUser --json

# Step 2: Find callers
repo-intel tool get-callers --name validateUser --json

# Output:
# [
#   {"name": "login", "file": "auth.py"},
#   {"name": "register", "file": "auth.py"},
#   {"name": "updateProfile", "file": "user.py"}
# ]

# Step 3: Check what those callers do
repo-intel tool get-callers --name login --json
# ... trace the chain upward
```

### Example 4: Understanding API Structure

**Scenario:** Document all API endpoints in a backend service.

```bash
# Index the project
repo-intel index --project backend -v

# List all endpoints
repo-intel tool list-symbols --kind endpoint --json > api-endpoints.json

# Generate documentation
repo-intel tool list-symbols --kind endpoint --json | \
  jq -r '.[] | "\(.http_method) \(.path) - \(.name)"'

# Output:
# GET /api/users - getUsers
# POST /api/users - createUser
# GET /api/users/:id - getUserById
# DELETE /api/users/:id - deleteUser
```

### Example 5: Finding Class Hierarchies

**Scenario:** Understand inheritance in a Java codebase.

```bash
# Find the base class
repo-intel tool find-symbol --name BaseService --json

# Look for extends/implements relations
repo-intel tool get-children --name BaseService --json

# Find what it implements
repo-intel tool get-parents --name BaseService --json
```

## Advanced Patterns

### Pattern 1: Full Call Chain Analysis

```bash
# Find what calls A
repo-intel tool get-callers --name functionA --json > callers_a.json

# For each caller, find what calls it
for caller in $(cat callers_a.json | jq -r '.[].name'); do
  echo "=== $caller ==="
  repo-intel tool get-callers --name $caller --json | jq '.[].name'
done
```

### Pattern 2: Dependency Mapping

```bash
# List all imports in a file
repo-intel tool get-imports --file src/main.py --json

# Build dependency graph
repo-intel tool get-dependencies --name main --json

# Find circular dependencies
repo-intel tool list-symbols --json | \
  jq -r '.[] | select(.kind == "module") | .name' | \
  while read module; do
    deps=$(repo-intel tool get-dependencies --name "$module" --json)
    # Check if any dep depends back on module
  done
```

### Pattern 3: Multi-Language Projects (Monorepo)

```bash
# Index each subproject
cd frontend && repo-intel index --project frontend
cd ../backend && repo-intel index --project backend
cd ../shared && repo-intel index --project shared

# Query across all
repo-intel tool list-symbols --json | jq 'group_by(.project)'

# Filter by project
repo-intel tool list-symbols --json | jq '.[] | select(.project == "frontend")'
```

## Integration with Development Workflow

### Before Making Changes

1. **Understand impact:**
   ```bash
   repo-intel tool get-callers --name targetFunction --json
   ```

2. **Check dependencies:**
   ```bash
   repo-intel tool get-dependencies --name targetModule --json
   ```

3. **Verify architecture:**
   ```bash
   repo-intel tool list-symbols --kind class --json
   ```

### During Implementation

1. **Find similar patterns:**
   ```bash
   repo-intel tool list-symbols --kind endpoint --json | \
     jq '.[] | select(.path | contains("/api/"))'
   ```

2. **Understand existing code:**
   ```bash
   repo-intel tool find-symbol --name similarFunction --json
   repo-intel tool get-callees --name similarFunction --json
   ```

### After Changes

1. **Verify nothing broke:**
   ```bash
   repo-intel tool get-callers --name modifiedFunction --json
   ```

2. **Re-index if structure changed:**
   ```bash
   repo-intel index --project myproject -v
   ```

## Best Practices

### 1. Keep Index Fresh

```bash
# Re-index after significant changes
repo-intel index --project myproject

# Use incremental indexing (automatic)
# Only changed files are reindexed
```

### 2. Use jq for Powerful Queries

```bash
# Count symbols by language
repo-intel tool list-symbols --json | \
  jq 'group_by(.language) | map({lang: .[0].language, count: length})'

# Find exported functions
repo-intel tool list-symbols --json | \
  jq '.[] | select(.exported == 1)'

# Find large functions (heuristic)
repo-intel tool list-symbols --json | \
  jq '.[] | select((.end_line - .start_line) > 50)'
```

### 3. Combine with Other Tools

```bash
# Find symbol, then read its code
SYMBOL=$(repo-intel tool find-symbol --name MyClass --json)
FILE=$(echo $SYMBOL | jq -r '.file_id')
LINE=$(echo $SYMBOL | jq -r '.start_line')

# Read the actual code
Read file=$FILE line=$LINE
```

### 4. Use Project Names Wisely

```bash
# Good project names
repo-intel index --project frontend-app
repo-intel index --project payment-service
repo-intel index --project shared-libs

# Filter queries by project
repo-intel tool list-symbols --json | \
  jq '.[] | select(.project == "payment-service")'
```

## Language-Specific Features

### Python

**Detects:**
- Functions and methods
- Classes with inheritance
- Flask/FastAPI endpoints
- Decorators

**Example:**
```python
@app.route('/api/users', methods=['GET'])
def get_users():
    return User.query.all()
```
↓ Indexed as: `GET /api/users`

### JavaScript/TypeScript

**Detects:**
- Functions (regular and arrow)
- Classes and methods
- Express endpoints
- ES6 imports

**Example:**
```javascript
app.get('/users', (req, res) => {
  res.json(users);
});
```
↓ Indexed as: `GET /users`

### Java

**Detects:**
- Classes and interfaces
- Methods
- Spring MVC endpoints
- Implements/extends relationships

**Example:**
```java
@GetMapping("/api/data")
public List<Data> getData() {
    return dataService.findAll();
}
```
↓ Indexed as: `GET /api/data`

### Rust

**Detects:**
- Functions and methods
- Structs (as classes)
- Traits (as interfaces)
- impl blocks
- pub visibility

### Go

**Detects:**
- Functions
- Structs (as classes)
- Interfaces
- Exported (capitalized) symbols
- Methods (receiver functions)

### PHP

**Detects:**
- Functions and methods
- Classes
- Interfaces
- Laravel-style endpoints (index → GET, store → POST, etc.)

## Troubleshooting

### No symbols found

```bash
# Check if indexed
ls -la .repo-intel/index.db

# Re-index with verbose output
repo-intel index --project myproject -v
```

### Wrong language detected

```bash
# Check file extensions
file some-file

# Manual language check
repo-intel tool list-symbols --json | jq '.[].language'
```

### Database issues

```bash
# Start fresh
rm -rf .repo-intel
repo-intel index --project myproject -v
```

## Summary

**repo-intel is your go-to tool for:**

| Task | Command | Example |
|------|---------|---------|
| Discover structure | `list-symbols` | "What exists?" |
| Find definition | `find-symbol` | "Where is it?" |
| Trace callers | `get-callers` | "Who calls this?" |
| Trace callees | `get-callees` | "What does this call?" |
| Map dependencies | `get-dependencies` | "What imports this?" |

**Workflow:**
1. **Index** → `repo-intel index --project myproject -v`
2. **Query** → `repo-intel tool <command> --json`
3. **Analyze** → Use `jq` or process JSON output

**Pro tip:** Always use `--json` for structured, parseable output!

---

## Quick Reference Card

```bash
# INDEXING
repo-intel index --project <name>              # Index project
repo-intel index --project <name> -v           # Verbose (show files)

# DISCOVERY
repo-intel tool list-symbols --json            # List all
repo-intel tool list-symbols --kind class --json
repo-intel tool list-symbols --kind function --json
repo-intel tool list-symbols --kind endpoint --json

# FINDING
repo-intel tool find-symbol --name <name> --json

# CALL GRAPHS
repo-intel tool get-callers --name <func> --json
repo-intel tool get-callees --name <func> --json

# DEPENDENCIES
repo-intel tool get-dependencies --name <module> --json

# WITH JQ
repo-intel tool list-symbols --json | jq 'group_by(.kind)'
repo-intel tool list-symbols --json | jq '.[] | select(.language == "python")'
```

Remember: **repo-intel provides STRUCTURAL intelligence, not text search!** Use it to understand *relationships* and *architecture*, not to search for strings.
