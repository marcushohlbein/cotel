---
name: repo-intel
description: Structural code analysis - find symbols, trace calls, map dependencies across 7 languages. Use when exploring codebases, finding relationships, or analyzing architecture.
activation-triggers:
  - Find all classes/functions
  - What calls this function
  - Show HTTP endpoints
  - Trace call graph
  - Where is this defined
  - What depends on this
  - Analyze code structure
  - Find implementations
  - Map dependencies
---

# repo-intel: Quick Reference

**What:** SQLite-based code structure analyzer for Python, JS/TS, Java, Rust, Go, PHP.

**Key capability:** Query code relationships without reading files.

## Quick Start

```bash
# Index repository
repo-intel index --project myproject -v

# Query symbols
repo-intel tool list-symbols --json
repo-intel tool find-symbol --name MyClass --json
repo-intel tool get-callers --name func --json
```

## The 5 Tools

### 1. `list-symbols` - Discover
```bash
repo-intel tool list-symbols --json                        # All symbols
repo-intel tool list-symbols --kind class --json           # Classes only
repo-intel tool list-symbols --kind endpoint --json         # HTTP endpoints
```

**Use:** "What's in this codebase?", "Show all classes", "List endpoints"

### 2. `find-symbol` - Locate
```bash
repo-intel tool find-symbol --name MyClass --json
```

**Use:** "Where is this defined?", "Find MyClass"

### 3. `get-callers` - Upward Trace
```bash
repo-intel tool get-callers --name myFunc --json
```

**Use:** "What calls this?", "Who uses this?"

### 4. `get-callees` - Downward Trace
```bash
repo-intel tool get-callees --name myFunc --json
```

**Use:** "What does this call?", "Trace execution"

### 5. `get-dependencies` - Imports
```bash
repo-intel tool get-dependencies --name MyModule --json
```

**Use:** "What imports this?", "Show dependencies"

## When to Use

### ✅ Use For:
- Exploring new codebases
- Finding symbol definitions
- Tracing call chains
- Impact analysis (what will break)
- Understanding relationships
- Finding HTTP endpoints
- Dependency mapping

### ❌ Don't Use For:
- File content reading → Use `Read`
- Text search → Use `grep`
- Git operations → Use `git`

## Common Patterns

### Explore Codebase
```bash
repo-intel index --project app -v
repo-intel tool list-symbols --json | jq 'group_by(.kind) | map({kind: .[0].kind, count: length})'
repo-intel tool list-symbols --kind endpoint --json | jq '.[] | {method: .http_method, path: .path}'
```

### Find Impact
```bash
repo-intel tool find-symbol --name targetFunction --json
repo-intel tool get-callers --name targetFunction --json
# Result: All functions that call targetFunction
```

### Debug Call Chain
```bash
repo-intel tool get-callers --name buggyFunction --json
# Who calls buggyFunction?
repo-intel tool get-callees --name buggyFunction --json
# What does buggyFunction call?
```

### API Documentation
```bash
repo-intel tool list-symbols --kind endpoint --json | \
  jq -r '.[] | "\(.http_method) \(.path) - \(.name)"'
```

## Symbol Types

- `function` - Standalone functions
- `class` - Classes and structs
- `method` - Class methods
- `interface` - Interfaces/traits
- `endpoint` - HTTP endpoints (auto-detected)

## Language Detection

Auto-detects:
- **Python**: Flask/FastAPI endpoints
- **JavaScript**: Express routes
- **TypeScript**: Express routes
- **Java**: Spring MVC endpoints
- **Rust**: Functions, structs, traits
- **Go**: Functions, structs, interfaces
- **PHP**: Laravel routes

## Best Practices

1. **Always use `--json`** for structured, parseable output
2. **Combine with `jq`** for filtering: `| jq '.[] | select(.language=="python")'`
3. **Re-index after structural changes**: `repo-intel index --project X`
4. **Use project names** for monorepos: `--project frontend`, `--project backend`

## Quick Examples

**"Find all classes"**
```bash
repo-intel tool list-symbols --kind class --json | jq '.[].name'
```

**"What calls processPayment?"**
```bash
repo-intel tool get-callers --name processPayment --json
```

**"Show all API endpoints"**
```bash
repo-intel tool list-symbols --kind endpoint --json | \
  jq '.[] | {method: .http_method, path: .path}'
```

**"Find function definition"**
```bash
repo-intel tool find-symbol --name myFunction --json | jq '.start_line'
```

## Output Format

All tools return JSON with common fields:
```json
{
  "id": "uuid",
  "name": "symbolName",
  "kind": "function|class|method|interface|endpoint",
  "language": "python|java|...",
  "file_id": "file-uuid",
  "start_line": 10,
  "end_line": 25,
  "http_method": "GET|POST|...",   // for endpoints
  "path": "/api/path"              // for endpoints
}
```

## Essential Commands

| Task | Command |
|------|---------|
| Index | `repo-intel index --project <name> -v` |
| List all | `repo-intel tool list-symbols --json` |
| Find specific | `repo-intel tool find-symbol --name <name> --json` |
| Callers | `repo-intel tool get-callers --name <func> --json` |
| Callees | `repo-intel tool get-callees --name <func> --json` |

---

**Remember:** repo-intel provides STRUCTURAL intelligence. Use it to understand relationships and architecture, not to search for text.
