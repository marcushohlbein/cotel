# repo-intel

Local-first structural intelligence for code repositories.

## Features

- **7 Languages**: Python, JavaScript, TypeScript, Java, Rust, Go, PHP
- **Symbol Extraction**: Functions, classes, methods, interfaces, structs
- **Call Graphs**: Track function/method calls across codebase
- **HTTP Endpoints**: Detect Flask/FastAPI, Express, Spring MVC, Laravel routes
- **Incremental Indexing**: Only reindex changed files (SHA-256 hashing)
- **Lazy Indexing**: Auto-reindex when stale (zero-config, on-demand)
- **Zero Setup**: No init needed, database auto-created
- **Monorepo Support**: Auto-detect and handle multi-package projects

## Installation

### From PyPI
```bash
pip install repo-intel
```

### System-wide (macOS/Linux)
```bash
# Install
pip install --user repo-intel

# Add to PATH (one-time setup)
echo 'export PATH="$HOME/Library/Python/3.14/bin:$PATH"' >> ~/.zshrc  # macOS
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc               # Linux

# Reload shell
source ~/.zshrc  # macOS
source ~/.bashrc # Linux
```

### From Source
```bash
git clone https://github.com/yourorg/repo-intel
cd repo-intel
pip install -e . --user
```

## Quick Start

```bash
cd your-project
repo-intel tool list-symbols --json  # That's it! Auto-indexes if needed
```

**Zero setup required!** Just run any tool command - it will automatically:
1. Create `.repo-intel/` directory
2. Initialize the database
3. Index your code (using SHA-256 incremental hashing)
4. Return results

## Typical Workflow

```bash
# 1. Navigate to your project
cd my-project

# 2. Query symbols (auto-indexes on first use)
repo-intel tool list-symbols --json

# 3. Find specific symbols
repo-intel tool find-symbol --name getUser --json

# 4. Analyze call graphs
repo-intel tool get-callers --name getUser --json  # What calls getUser?
repo-intel tool get-callees --name getUser --json  # What does getUser call?

# 5. Filter by symbol type
repo-intel tool list-symbols --kind endpoint --json  # HTTP endpoints only

# 6. Work continues... (index auto-refreshes when stale)
```

## CLI Commands

```bash
# Query tools (auto-index if stale)
repo-intel tool list-symbols [--kind function|class|method|endpoint]
repo-intel tool find-symbol --name myFunction
repo-intel tool get-callers --name myFunction
repo-intel tool get-callees --name myFunction
repo-intel tool list-symbols --no-auto-index  # Skip auto-indexing

# Manual indexing (usually not needed)
repo-intel index             # Index all source files
repo-intel index --verbose   # Index with progress feedback
```

## Lazy Indexing

**Zero-config, on-demand indexing.**

Tool commands automatically reindex when:

1. **No index exists** (first run)
2. **Index is old** (>1 hour)
3. **File count changed** (files added/deleted)

**How it works:**
- Uses SHA-256 hashing to detect changes
- Only reindexes changed files (incremental)
- Silent background reindex (shows brief status)
- Stores last index timestamp in metadata

**Example:**
```bash
repo-intel tool list-symbols  # Auto-indexes (first time)

# Make changes to files...

repo-intel tool list-symbols  # Uses existing index (still fresh)

# 2 hours later...

repo-intel tool list-symbols  # Auto-reindexes (index stale)
```

**Disable auto-indexing:**
```bash
repo-intel tool list-symbols --no-auto-index
```

## Database

**Location:** `.repo-intel/index.db` (SQLite)

**Auto-created on first use** - no setup required.

**What's stored:**
- **files**: File paths, languages, SHA-256 hashes
- **symbols**: Functions, classes, methods, interfaces
- **relations**: Call graph (calls), inheritance (extends/implements)
- **metadata**: Last index timestamp

**To reset:**
```bash
rm -rf .repo-intel/  # Delete and rebuild on next query
```

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Detailed usage guide
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Running tests
- [prd.md](prd.md) - Product requirements
- [CHANGELOG.md](CHANGELOG.md) - Version history

## AI Agent Integration

repo-intel includes a skill for coding agents (OpenCode, Claude Code):

```bash
.agents/skills/repo-intel/SKILL.md
```

The skill teaches agents when/how to use repo-intel for codebase exploration.

## Architecture

```
.repo-intel/
└── index.db                 # SQLite database (symbols, relations, metadata)

src/repo_intel/
├── cli.py                   # CLI entry point
├── core/
│   ├── config.py            # Config management
│   ├── indexer.py           # Indexing orchestration
│   └── storage.py           # SQLite abstraction
├── parsers/                 # Tree-sitter parsers (7 languages)
└── tools/                   # Query tools
```

## Development

```bash
# Run tests
source venv/bin/activate
pytest tests/ -v

# Run all 73 tests
pytest tests/ -v
```

## License

MIT
