# repo-intel

Local-first structural intelligence for code repositories.

## Features

- Multi-language symbol indexing (Python, JS/TS, Java, Rust, Go, PHP)
- Call graph generation
- Dependency modeling
- Inheritance tracking
- HTTP boundary detection
- Incremental reindexing
- Monorepo awareness

## Installation

```bash
pip install repo-intel
```

## Usage

```bash
# Initialize in a repository
repo-intel init

# Index the repository
repo-intel index

# Watch for changes
repo-intel watch

# Query via stdio
repo-intel stdio

# Run tools
repo-intel tool list-symbols --json
```
