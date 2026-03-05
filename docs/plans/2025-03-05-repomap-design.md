# Repomap Tool Design

**Date:** 2025-03-05
**Status:** Approved
**Approach:** Minimal Extension (Approach 1)

## Overview

Transform repo-intel into a standalone repomap tool that generates token-efficient repository maps for AI coding assistants (OpenCode, Claude Code, Cursor, etc.).

## Goals

- **Primary user:** AI agents (programmatic use)
- **Output format:** TOON (default), JSON (optional)
- **Feature parity:** Match Aider's repomap capabilities
- **Simplicity:** Minimal CLI, auto-detection, zero-config

## Architecture

### Module Structure

```
repomap/                          # Rename from repo-intel
├── cli.py                        # Refactored CLI (hybrid structure)
├── core/
│   ├── storage.py                # Existing (add references table)
│   ├── indexer.py                # Existing (extend for refs)
│   ├── pagerank.py               # NEW: PageRank scoring
│   ├── token_optimizer.py        # NEW: Binary search for token fit
│   ├── context_detector.py       # NEW: Auto-detect git context
│   └── repomap_generator.py      # NEW: Orchestrates generation
├── parsers/
│   ├── base.py                   # Existing (add extract_references())
│   ├── python_parser.py          # Extend to extract refs
│   ├── javascript_parser.py      # Extend to extract refs
│   └── ... (all 7 parsers)
├── formatters/
│   ├── toon_formatter.py         # NEW: TOON format output (PRIMARY)
│   └── json_formatter.py         # NEW: JSON output (via --json flag)
└── utils/
    ├── token_counter.py          # NEW: Token counting
    └── ... (existing utils)
```

### Key Components

1. **Reference Extractor** - Extends parsers to track symbol usages
2. **PageRank Scorer** - Ranks symbols by importance using graph algorithm
3. **Token Optimizer** - Binary search to fit within token budget
4. **Context Detector** - Auto-detect relevant files from git status
5. **TOON Formatter** - Generate token-efficient output

## Database Schema

### New Table: references

```sql
CREATE TABLE references (
  id TEXT PRIMARY KEY,
  symbol_id TEXT,           -- Which symbol is referenced
  file_id TEXT,             -- In which file
  line_number INTEGER,      -- At which line
  context_snippet TEXT,     -- Optional: surrounding code
  FOREIGN KEY (symbol_id) REFERENCES symbols(id),
  FOREIGN KEY (file_id) REFERENCES files(id)
);
```

### Extended: symbols table

```sql
ALTER TABLE symbols ADD COLUMN signature TEXT;
```

## Core Algorithm

### PageRank Scoring

**Per-request computation** (uses cached definitions/references):

1. **Build graph**: Files as nodes, edges = symbol references
2. **Weight edges**:
   - Base: `sqrt(num_references)`
   - Boost `10x`: mentioned identifiers
   - Boost `10x`: snake_case/kebab-case/camelCase ≥8 chars
   - Penalty `0.1x`: private symbols (`_` prefix)
   - Penalty `0.1x`: symbols in >5 files
3. **Personalization**: Git modified files get higher rank
4. **Run PageRank**: NetworkX `pagerank()` with weighted edges

**Performance:** ~200-500ms for 10k symbols

### Token Budget Optimization

Binary search to fit map within token budget (default 1024):

```
lower = 0
upper = len(ranked_symbols)

while lower <= upper:
    middle = (lower + upper) // 2
    candidate = ranked_symbols[:middle]
    tokens = count_tokens(format(candidate))
    
    if tokens <= max_tokens:
        best = candidate
        lower = middle + 1
    else:
        upper = middle - 1
```

**Auto-expansion:** If no modified files, expand to 8x budget

### Auto-Context Detection

Detect relevant files without manual flags:

1. **Git modified files**: `git diff --name-only`
2. **Extract identifiers**: Parse `git diff` for changed symbols
3. **Fallback**: Empty context (neutral ranking)

## CLI Design

### Primary Command (Default)

```bash
repomap                    # Auto-detect context, generate TOON
repomap --max-tokens 2048  # Adjust token budget
repomap --json            # JSON output instead of TOON
```

### Advanced Subcommands

```bash
repomap list --type class         # List symbols
repomap find --name getUser       # Find symbol
repomap callers --name processPayment
repomap callees --name validateUser
repomap index --verbose           # Manual indexing
```

### CLI Structure

```python
@click.group(invoke_without_command=True)
@click.option('--max-tokens', default=1024)
@click.option('--json', is_flag=True)
@click.pass_context
def cli(ctx, max_tokens, json):
    if ctx.invoked_subcommand is None:
        return generate_repomap(max_tokens, json)
```

## Output Format

### TOON (Default)

```toon
repo_map{
  project: "my-app",
  tokens_used: 987,
  max_tokens: 1024
}
symbols[15]{name,kind,file,start_line,end_line,signature}:
  Coder,class,src/coder.py,42,156,def create(self, model, io, **kwargs)
  RepoMap,class,src/repomap.py,38,89,def get_ranked_tags(...)
  get_tags,function,src/repomap.py,233,264,def get_tags(fname, rel_fname)
  ...
files[8]{path,symbol_count,language}:
  src/coder.py,12,python
  src/repomap.py,8,python
  ...
```

### JSON (Optional)

```json
{
  "repo_map": {
    "project": "my-app",
    "tokens_used": 987
  },
  "symbols": [
    {
      "name": "Coder",
      "kind": "class",
      "file": "src/coder.py",
      "start_line": 42,
      "end_line": 156,
      "signature": "def create(self, model, io, **kwargs)"
    }
  ]
}
```

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Initial index (1k files) | < 5s | One-time, cached |
| Incremental reindex (10 files) | < 500ms | Only changed files |
| Generate repomap | < 1s | Uses cached data |
| PageRank (10k symbols) | < 500ms | NetworkX is fast |
| Token optimization | < 200ms | Binary search |

## Error Handling

- **No git repo** → Fall back to full repo scan
- **No modified files** → Expand token budget 8x
- **Parse errors** → Skip file, continue
- **Large repos** → Show progress bar

## Migration Plan

1. Rename package: `repo-intel` → `repomap`
2. Update CLI binary name
3. Keep database at `.repo-intel/` (backwards compatible)
4. Extend database schema (add references table)
5. All existing commands work unchanged

## Success Criteria

- ✅ TOON output ~40% fewer tokens than JSON
- ✅ PageRank ranks modified files higher
- ✅ Binary search fits within token budget
- ✅ CLI simple enough for AI agents (3 flags max)
- ✅ Performance < 1s for typical repos

## References

- Aider repomap: https://aider.chat/docs/repomap.html
- Aider source: `.aider/aider/repomap.py`
- TOON format: https://github.com/toon-format/toon
- Current repo-intel: `src/repo_intel/`
