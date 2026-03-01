# Changelog

## [0.1.0] - 2026-03-01

### Added
- Multi-language symbol indexing (Python, JavaScript, TypeScript)
- Call graph generation and querying
- Dependency tracking via import analysis
- Inheritance tracking (extends, implements)
- HTTP endpoint detection for Flask/FastAPI (Python) and Express (JS)
- Incremental reindexing with file hashing
- Monorepo project detection and support
- CLI with init, index, and tool commands
- SQLite-based storage with full schema
- Tree-sitter parser integration
- Query tools: list_symbols, find_symbol, get_callers, get_callees

### Tools
- `repo-intel init`: Initialize in a repository
- `repo-intel index`: Index the codebase
- `repo-intel tool list-symbols`: List all symbols
- `repo-intel tool find-symbol --name <name>`: Find symbol by name
- `repo-intel tool get-callers --name <name>`: Get callers of a function
- `repo-intel tool get-callees --name <name>`: Get functions called by a symbol
