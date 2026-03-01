# Architecture

## Overview

repo-intel provides a structural intelligence layer over code repositories using static analysis.

## Components

### Core
- **indexer.py**: Orchestrates file parsing and symbol extraction
- **storage.py**: SQLite abstraction for symbols, files, and relations
- **config.py**: Configuration management

### Parsers
Language-specific parsers using Tree-sitter:
- `python_parser.py`: Python
- `javascript_parser.py`: JavaScript/TypeScript
- Additional parsers for Java, Rust, Go, PHP (planned)

### Tools
Query interfaces for exploring code:
- `list_symbols`: List all symbols
- `find_symbol`: Find specific symbol
- `get_callers`: Get callers of a symbol
- `get_callees`: Get symbols called by a symbol

## Data Model

### Symbol
- id, name, kind, language, file_id, project, start_line, end_line, exported
- Optional: http_method, path (for HTTP endpoints)

### Relation
- from_symbol_id, to_symbol_id, relation_type (calls, extends, implements, imports)

## Incremental Indexing

- SHA-256 hash per file
- Reindex only changed files
- Update only affected graph edges

## Monorepo Support

- Detect subprojects via marker files (package.json, pom.xml, etc.)
- Tag symbols with project scope
- Filter queries by project
