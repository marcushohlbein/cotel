---
name: repo-intel
description: Structural code analysis - query symbols, trace call graphs, map dependencies across 7 languages without reading files. Use for exploring codebases, finding relationships, impact analysis.
allowed-tools: Bash(repo-intel:*)
---

# Code Structure Analysis with repo-intel

## Core Workflow

Every analysis follows this pattern:

1. **Index**: `repo-intel index --project <name> -v`
2. **Query**: `repo-intel tool <command> --json`
3. **Parse**: Use `jq` to filter/transform JSON

```bash
repo-intel index --project myapp -v
repo-intel tool list-symbols --json
# Output: [{"name": "User", "kind": "class", "language": "python", ...}]

repo-intel tool find-symbol --name User --json | jq '.start_line'
# Output: 15

repo-intel tool get-callers --name login --json
# Output: [{"name": "handleSubmit", "kind": "function", ...}]
```

## Essential Commands

```bash
# Indexing
repo-intel index --project <name>              # Index repository
repo-intel index --project <name> -v            # Verbose (show files)

# Discovery
repo-intel tool list-symbols --json            # All symbols
repo-intel tool list-symbols --kind class --json
repo-intel tool list-symbols --kind function --json
repo-intel tool list-symbols --kind endpoint --json

# Finding
repo-intel tool find-symbol --name <name> --json

# Call Graphs
repo-intel tool get-callers --name <func> --json  # What calls this?
repo-intel tool get-callees --name <func> --json  # What does this call?

# Dependencies
repo-intel tool get-dependencies --name <module> --json
```

## Symbol Types

| Kind | Description | Detected Languages |
|------|-------------|-------------------|
| `function` | Standalone functions | All |
| `class` | Classes, structs | All |
| `method` | Class methods | Python, JS, Java, PHP |
| `interface` | Interfaces, traits | Java, TS, Rust, Go |
| `endpoint` | HTTP routes | Python (Flask), JS (Express), Java (Spring), PHP (Laravel) |

## Common Patterns

### Explore Codebase

```bash
repo-intel index --project myapp -v
repo-intel tool list-symbols --json | jq 'group_by(.kind) | map({kind: .[0].kind, count: length})'
repo-intel tool list-symbols --kind class --json | jq '.[].name'
```

### Find API Endpoints

```bash
repo-intel tool list-symbols --kind endpoint --json | \
  jq -r '.[] | "\(.http_method) \(.path) - \(.name)"'

# Output:
# GET /api/users - getUsers
# POST /api/users - createUser
```

### Impact Analysis

```bash
# What will break if I change processPayment?
repo-intel tool find-symbol --name processPayment --json
repo-intel tool get-callers --name processPayment --json

# Result: All functions that call processPayment
```

### Trace Call Chain

```bash
# Who calls validateUser?
repo-intel tool get-callers --name validateUser --json

# What does validateUser call?
repo-intel tool get-callees --name validateUser --json

# Trace upward
repo-intel tool get-callers --name $(repo-intel tool get-callers --name validateUser --json | jq -r '.[0].name') --json
```

### Find Implementations

```bash
# Find all classes that implement an interface
repo-intel tool list-symbols --kind class --json | \
  jq '.[] | select(.name | contains("Service"))'
```

### Language-Specific Query

```bash
# All Python symbols
repo-intel tool list-symbols --json | jq '.[] | select(.language == "python")'

# All Java classes
repo-intel tool list-symbols --kind class --json | jq '.[] | select(.language == "java")'
```

## HTTP Endpoint Detection

**Python (Flask/FastAPI):**
```python
@app.route('/api/users', methods=['GET'])
def get_users(): pass
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

## Best Practices

1. **Always use `--json`** - Structured output for parsing
2. **Combine with `jq`** - Filter and transform: `| jq '.[] | select(.kind == "class")'`
3. **Re-index after big changes** - `repo-intel index --project <name>`
4. **Use project names** - For monorepos: `--project frontend`, `--project backend`
5. **Check freshness** - If results seem stale, re-index

## When to Use

### ✅ Use For
- Exploring new codebases
- Finding symbol definitions
- Tracing call chains
- Impact analysis (what will break)
- Understanding relationships
- Finding HTTP endpoints
- Dependency mapping

### ❌ Don't Use For
- File content → Use `Read`
- Text search → Use `grep`
- Git operations → Use `git`
- Running code → Use `Bash`

## Output Format

All tools return JSON:
```json
{
  "id": "uuid",
  "name": "symbolName",
  "kind": "function|class|method|endpoint",
  "language": "python|java|javascript|...",
  "file_id": "file-uuid",
  "start_line": 10,
  "end_line": 25,
  "http_method": "GET|POST",  // endpoints only
  "path": "/api/path"         // endpoints only
}
```

## Quick Reference

| Task | Command |
|------|---------|
| Index | `repo-intel index --project <name> -v` |
| List all | `repo-intel tool list-symbols --json` |
| Find class | `repo-intel tool find-symbol --name <name> --json` |
| Callers | `repo-intel tool get-callers --name <func> --json` |
| Callees | `repo-intel tool get-callees --name <func> --json` |
| Endpoints | `repo-intel tool list-symbols --kind endpoint --json` |

## Monorepo Support

```bash
# Index each subproject
cd frontend && repo-intel index --project frontend -v
cd ../backend && repo-intel index --project backend -v
cd ../shared && repo-intel index --project shared -v

# Query across all
repo-intel tool list-symbols --json | jq 'group_by(.project)'

# Filter by project
repo-intel tool list-symbols --json | jq '.[] | select(.project == "frontend")'
```

## Language Support

| Language | Functions | Classes | Methods | Endpoints | Imports |
|----------|-----------|---------|---------|-----------|---------|
| Python | ✅ | ✅ | ✅ | ✅ Flask/FastAPI | ✅ |
| JavaScript | ✅ | ✅ | ✅ | ✅ Express | ✅ |
| TypeScript | ✅ | ✅ | ✅ | ✅ Express | ✅ |
| Java | ✅ | ✅ | ✅ | ✅ Spring MVC | ✅ |
| Rust | ✅ | ✅ (structs) | ✅ | ❌ | ✅ |
| Go | ✅ | ✅ (structs) | ✅ | ❌ | ✅ |
| PHP | ✅ | ✅ | ✅ | ✅ Laravel | ✅ |

## Ref Lifecycle (Important)

Indexes are **incremental** - unchanged files skip reprocessing. After major refactoring:

```bash
# Force full reindex
rm -rf .repo-intel
repo-intel index --project myapp -v
```

## Advanced Filters with jq

```bash
# Count by language
repo-intel tool list-symbols --json | jq 'group_by(.language) | map({lang: .[0].language, count: length})'

# Large functions (heuristic)
repo-intel tool list-symbols --json | jq '.[] | select((.end_line - .start_line) > 50)'

# Exported/public symbols
repo-intel tool list-symbols --json | jq '.[] | select(.exported == 1)'

# Find specific pattern
repo-intel tool list-symbols --json | jq '.[] | select(.name | contains("Service"))'
```

## Integration with Read Tool

```bash
# Find symbol, then read it
SYMBOL=$(repo-intel tool find-symbol --name MyClass --json)
FILE=$(echo $SYMBOL | jq -r '.file_id')
START=$(echo $SYMBOL | jq -r '.start_line')
END=$(echo $SYMBOL | jq -r '.end_line')

# Use Read tool with line numbers
Read file=$FILE offset=$START limit=$((END - START))
```

---

**Pro tip:** repo-intel provides **structural intelligence** - understand relationships and architecture, not text search. Always pair with `jq` for powerful queries.
