# repo-intel Usage Guide for AI Coding Agents

## What is repo-intel?

repo-intel is a **structural code intelligence tool** that helps you understand codebases without reading entire files. It extracts symbols, call graphs, dependencies, and relationships.

**Key benefit**: Query code structure in milliseconds instead of reading thousands of lines.

## When to Use repo-intel

### ✅ USE repo-intel when:

1. **Finding function/class definitions**
   - "Where is the `UserService` class defined?"
   - "Find all functions named `handleAuth`"

2. **Understanding call relationships**
   - "What functions call `processPayment`?"
   - "What does `main()` call?"

3. **Exploring codebases quickly**
   - "List all API endpoints in this project"
   - "Show me all database models"
   - "What classes exist in this codebase?"

4. **Finding impact of changes**
   - "If I change `getUserById`, what will break?"
   - "What depends on the `Config` class?"

5. **Cross-language analysis**
   - Works with Python, JavaScript, TypeScript, Java, Rust, Go, PHP
   - Same query interface for all languages

### ❌ DON'T use repo-intel for:

1. **Reading implementation details**
   - "What does this function do?" → Use Read tool
   - "Show me the code" → Use Read tool

2. **Text-based search**
   - "Find where 'password' is mentioned" → Use Grep tool
   - "Search for comments" → Use Grep tool

3. **Semantic understanding**
   - "Explain this algorithm" → Read and analyze
   - "Does this handle errors?" → Read the code

## Setup (One-time per project)

```bash
# Initialize repo-intel (creates .repo-intel/ directory)
repo-intel init

# Index the codebase (takes 1-30 seconds depending on size)
repo-intel index --project myproject

# For detailed output during indexing
repo-intel index --project myproject -v
```

## Quick Reference

### List All Symbols
```bash
repo-intel tool list-symbols --json
```

**When to use**: Get overview of entire codebase

**Example output**:
```json
[
  {"name": "UserService", "kind": "class", "language": "python"},
  {"name": "get_users", "kind": "function", "language": "python"},
  {"name": "/api/users", "kind": "endpoint", "http_method": "GET"}
]
```

### Find Specific Symbol
```bash
repo-intel tool find-symbol --name UserService --json
```

**When to use**: Locate a specific function/class

**Example output**:
```json
{
  "name": "UserService",
  "kind": "class",
  "file_id": "abc123",
  "start_line": 15,
  "end_line": 45
}
```

### Filter Symbols by Kind
```bash
# Find all functions
repo-intel tool list-symbols --kind function --json

# Find all classes
repo-intel tool list-symbols --kind class --json

# Find all API endpoints
repo-intel tool list-symbols --kind endpoint --json
```

**When to use**: Explore specific types of symbols

### Call Graph Analysis
```bash
# What calls this function?
repo-intel tool get-callers --name processPayment --json

# What does this function call?
repo-intel tool get-callees --name main --json
```

**When to use**: Understand dependencies and impact

## Common Workflows

### Workflow 1: Understanding a New Codebase

```bash
# Step 1: Initialize and index
repo-intel init
repo-intel index --project codebase -v

# Step 2: Get overview
repo-intel tool list-symbols --json | jq 'group_by(.kind) | map({kind: .[0].kind, count: length})'

# Step 3: Find entry points
repo-intel tool list-symbols --kind endpoint --json

# Step 4: Understand structure
repo-intel tool list-symbols --kind class --json
```

### Workflow 2: Finding Impact of Changes

```bash
# Question: "What happens if I change the AuthService class?"

# Step 1: Find the class
repo-intel tool find-symbol --name AuthService --json

# Step 2: Find what uses it (callers)
repo-intel tool get-callers --name AuthService --json

# Step 3: Find what it provides (callees)
repo-intel tool get-callees --name AuthService --json
```

### Workflow 3: Locating API Endpoints

```bash
# List all HTTP endpoints
repo-intel tool list-symbols --kind endpoint --json

# Filter by method
repo-intel tool list-symbols --kind endpoint --json | jq '.[] | select(.http_method == "GET")'

# Find specific endpoint
repo-intel tool find-symbol --name get_users --json
```

### Workflow 4: Exploring Module Structure

```bash
# List all symbols from a file (requires JSON processing)
repo-intel tool list-symbols --json | jq '.[] | select(.file_id == "<file_id>")'

# Find all exported/public symbols
repo-intel tool list-symbols --json | jq '.[] | select(.exported == 1)'

# Group by language (for multi-language projects)
repo-intel tool list-symbols --json | jq 'group_by(.language)'
```

## Response Format

repo-intel always returns JSON. Use `jq` or parse with JSON tools.

**Symbol structure**:
```json
{
  "id": "unique-uuid",
  "name": "symbol_name",
  "kind": "function|class|method|interface|endpoint",
  "language": "python|javascript|java|rust|go|php",
  "file_id": "file-uuid",
  "project": "project_name",
  "start_line": 10,
  "end_line": 25,
  "exported": true
}
```

## Symbol Types

| Kind | Description | Languages |
|------|-------------|-----------|
| `function` | Standalone function | All |
| `class` | Class/struct/definition | All |
| `method` | Class method | All |
| `interface` | Interface/trait | Java, TS, Go, Rust |
| `endpoint` | HTTP endpoint | Python (Flask/FastAPI), JS (Express), Java (Spring) |

## Working with Different Languages

### Python (Flask/FastAPI)
```bash
# Find all route handlers
repo-intel tool list-symbols --kind endpoint --json

# Find all request handlers
repo-intel tool list-symbols --kind function --json | jq '.[] | select(.name | contains("handle"))'
```

### JavaScript/TypeScript
```bash
# Find React components (classes)
repo-intel tool list-symbols --kind class --json

# Find Express routes
repo-intel tool list-symbols --kind endpoint --json
```

### Java (Spring Boot)
```bash
# Find Spring controllers
repo-intel tool list-symbols --kind class --json | jq '.[] | select(.name | endswith("Controller"))'

# Find REST endpoints
repo-intel tool list-symbols --kind endpoint --json
```

## Performance Characteristics

- **Indexing speed**: ~1000-5000 LOC per second
- **Query speed**: <100ms for most queries
- **Database size**: ~1-2KB per symbol
- **Memory usage**: Minimal (SQLite-based)

## Best Practices for AI Agents

### 1. Always Index First
```bash
# Before querying, ensure the codebase is indexed
repo-intel index --project myproject --verbose
```

### 2. Use JSON Output
```bash
# Always use --json for machine-readable output
repo-intel tool list-symbols --json
```

### 3. Combine with Other Tools

**Good pattern**:
```bash
# 1. Use repo-intel to find location
file_info=$(repo-intel tool find-symbol --name MyFunction --json)
file_id=$(echo "$file_info" | jq -r '.file_id')
start_line=$(echo "$file_info" | jq -r '.start_line')

# 2. Use Read tool to get actual code
# Read file at start_line
```

### 4. Filter Early
```bash
# Filter by kind to reduce result size
repo-intel tool list-symbols --kind class --json
```

### 5. Progress Monitoring
```bash
# Use --verbose to see progress on large codebases
repo-intel index --project myproject -v
```

## Limitations

1. **No semantic analysis**: Can't tell you what code *does*, only *where* it is
2. **No text search**: Use Grep tool for searching comments/strings
3. **No refactoring**: Use Edit tool to modify code
4. **Static analysis only**: No runtime information
5. **Incremental updates**: Re-run `index` after significant code changes

## Integration Pattern

```bash
# Pattern: repo-intel → Read tool → Edit tool

# 1. Find symbol location
symbol=$(repo-intel tool find-symbol --name MyFunction --json)
file=$(echo "$symbol" | jq -r '.file_id')  # Map to actual file path
line=$(echo "$symbol" | jq -r '.start_line')

# 2. Read the code
# Use Read tool on file at line

# 3. Modify the code
# Use Edit tool to make changes

# 4. Re-index if needed
repo-intel index --project myproject
```

## Example Agent Workflow

**User**: "Where is the authentication logic in this codebase?"

**Agent should**:
1. Index or verify index exists
2. Search for relevant symbols
3. Use repo-intel intelligently

```bash
# Step 1: Check if indexed (look for .repo-intel directory)
ls .repo-intel 2>/dev/null || repo-intel init && repo-intel index --project codebase

# Step 2: Find auth-related symbols
repo-intel tool list-symbols --json | jq '.[] | select(.name | test("auth|login|user"; "i"))'

# Step 3: Get specific details
repo-intel tool find-symbol --name AuthService --json

# Step 4: Understand call graph
repo-intel tool get-callers --name login --json
repo-intel tool get-callees --name login --json
```

## Summary Decision Tree

```
User question about code?
├─ "Where is X defined?" → repo-intel find-symbol
├─ "What calls X?" → repo-intel get-callers
├─ "What does X call?" → repo-intel get-callees
├─ "List all X" → repo-intel list-symbols --kind X
├─ "How does X work?" → Read tool (not repo-intel)
└─ "Search for X in code" → Grep tool (not repo-intel)
```

## Quick Command Reference

| Goal | Command |
|------|---------|
| Setup | `repo-intel init && repo-intel index --project NAME` |
| List all symbols | `repo-intel tool list-symbols --json` |
| Find symbol by name | `repo-intel tool find-symbol --name NAME --json` |
| Filter by kind | `repo-intel tool list-symbols --kind CLASS --json` |
| Find callers | `repo-intel tool get-callers --name NAME --json` |
| Find callees | `repo-intel tool get-callees --name NAME --json` |
| List endpoints | `repo-intel tool list-symbols --kind endpoint --json` |
| Verbose indexing | `repo-intel index --project NAME -v` |

## Troubleshooting

**Problem**: "unable to open database file"
**Solution**: Run `repo-intel init` or just `repo-intel index` (auto-creates directory)

**Problem**: Empty results
**Solution**: Run `repo-intel index --project NAME` first

**Problem**: Outdated results
**Solution**: Re-run `repo-intel index --project NAME` after code changes

**Problem**: "No symbols found"
**Solution**: Check if language is supported (Python, JS, TS, Java, Rust, Go, PHP)

---

**Remember**: repo-intel is for *finding* code, not *reading* it. Use it to locate symbols quickly, then use Read tool to understand implementation.
