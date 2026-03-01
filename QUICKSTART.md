# repo-intel Quick Reference

## Installation & Setup

```bash
# Install
cd /path/to/repo-intel
pip install -e .

# Initialize in your project
cd your-project
repo-intel init

# Index your code
repo-intel index --project myproject
```

## Common Commands

### Indexing
```bash
repo-intel init                                    # Initialize
repo-intel index --project <name>                 # Index repository
```

### Query Tools
```bash
repo-intel tool list-symbols --json               # List all symbols
repo-intel tool find-symbol --name <name> --json  # Find specific symbol
repo-intel tool get-callers --name <name> --json   # What calls this?
repo-intel tool get-callees --name <name> --json   # What does this call?
```

### Filtering
```bash
repo-intel tool list-symbols --kind function --json   # Only functions
repo-intel tool list-symbols --kind class --json      # Only classes
repo-intel tool list-symbols --kind endpoint --json   # Only HTTP endpoints
```

## Real-World Examples

### Flask/FastAPI App
```bash
cd my-flask-app
repo-intel init
repo-intel index --project flask-app

# Find all endpoints
repo-intel tool list-symbols --kind endpoint --json
```

### Python Package
```bash
cd my-python-package
repo-intel init
repo-intel index --project mypackage

# List all functions
repo-intel tool list-symbols --kind function --json
```

### Monorepo
```bash
cd my-monorepo
repo-intel init

# Index each subproject
repo-intel index --project frontend
repo-intel index --project backend
```

## Tips

1. **Add `| jq`** for pretty JSON filtering
2. **Use `--json`** flag for structured output
3. **Reindex after code changes** (incremental, fast)
4. **Database**: `.repo-intel/index.db` (SQLite)
5. **Config**: `.repo-intel/config.json`

## Supported Languages

- ✅ Python
- ✅ JavaScript
- ✅ TypeScript
- ✅ Java
- ✅ Rust
- ✅ Go
- ✅ PHP
