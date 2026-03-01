# repo-intel

Local-first structural intelligence for code repositories.

## Features

- **7 Languages**: Python, JavaScript, TypeScript, Java, Rust, Go, PHP
- **Symbol Extraction**: Functions, classes, methods, interfaces, structs
- **Call Graphs**: Track function/method calls across codebase
- **HTTP Endpoints**: Detect Flask/FastAPI, Express, Spring MVC, Laravel routes
- **Incremental Indexing**: Only reindex changed files
- **Monorepo Support**: Auto-detect and handle multi-package projects

## Installation

### From PyPI
```bash
pip install repo-intel
```

### System-wide (macOS/Linux)
```bash
pip install --user repo-intel
export PATH="$HOME/.local/bin:$PATH"  # Linux
export PATH="$HOME/Library/Python/3.14/bin:$PATH"  # macOS
```

### From Source
```bash
git clone https://github.com/yourorg/repo-intel
cd repo-intel
pip install -e .
```

## Quick Start

```bash
cd your-project
repo-intel init      # Initialize .repo-intel/ database
repo-intel index     # Index all files
repo-intel tool list-symbols --kind function --json
```

## CLI Commands

```bash
repo-intel init              # Initialize project database
repo-intel index             # Index all source files
repo-intel index --verbose   # Index with progress feedback

# Query tools
repo-intel tool list-symbols [--kind function|class|method|endpoint]
repo-intel tool find-symbol --name myFunction
repo-intel tool get-callers --name myFunction
repo-intel tool get-callees --name myFunction
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
├── config.json              # Project configuration
└── repo-intel.db            # SQLite database (symbols, relations)

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

# Run all 66 tests
pytest tests/ -v
```

## License

MIT
