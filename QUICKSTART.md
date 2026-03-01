# repo-intel Quick Reference

## Installation & Setup

```bash
# Install
cd /path/to/repo-intel
pip install -e .

# That's it! Just run any tool command
cd your-project
repo-intel tool list-symbols --json  # Auto-creates DB and indexes
```

## Common Commands

### Query Tools (auto-index if stale)
```bash
repo-intel tool list-symbols --json               # List all symbols
repo-intel tool find-symbol --name <name> --json  # Find specific symbol
repo-intel tool get-callers --name <name> --json   # What calls this?
repo-intel tool get-callees --name <name> --json   # What does this call?
```

### Manual Indexing (usually not needed)
```bash
repo-intel index --project <name>    # Index all files
repo-intel index --verbose           # Index with progress
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
# Just run any tool - auto-indexes on first use
repo-intel tool list-symbols --kind endpoint --json
```

### Python Package
```bash
cd my-python-package
# Auto-indexes and returns all functions
repo-intel tool list-symbols --kind function --json
```

### Monorepo
```bash
cd my-monorepo
# Index each subproject manually (optional)
repo-intel index --project frontend
repo-intel index --project backend
```

## Tips

1. **No init needed** - tools auto-create DB and index on first use
2. **Add `| jq`** for pretty JSON filtering
3. **Use `--json`** flag for structured output
4. **Lazy indexing** - auto-reindexes when stale (>1hr old or file count changed)
5. **Incremental** - only reindexes changed files (SHA-256 hashing)
6. **Database**: `.repo-intel/index.db` (SQLite, auto-created)

## Supported Languages

- ✅ Python
- ✅ JavaScript
- ✅ TypeScript
- ✅ Java
- ✅ Rust
- ✅ Go
- ✅ PHP
