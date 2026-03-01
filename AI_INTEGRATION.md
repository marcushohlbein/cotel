# repo-intel Integration for AI Tools

## Integration Overview

This guide shows how to integrate repo-intel into AI coding tools (Claude Code, Cursor, Continue, etc.).

## System Prompt Addition

Add this to your AI tool's system prompt:

```markdown
# repo-intel Tool Access

You have access to `repo-intel`, a structural code intelligence tool.

## Commands Available

### Setup (one-time per project)
```bash
repo-intel init
repo-intel index --project <project-name>
```

### Query Commands
```bash
repo-intel tool list-symbols --json                    # All symbols
repo-intel tool list-symbols --kind <kind> --json      # Filter by kind
repo-intel tool find-symbol --name <name> --json        # Find specific symbol
repo-intel tool get-callers --name <name> --json        # What calls this?
repo-intel tool get-callees --name <name> --json        # What does this call?
```

## When to Use

✅ **Use repo-intel for**:
- Finding where functions/classes are defined
- Understanding code relationships (call graphs)
- Getting overview of codebase structure
- Finding API endpoints
- Impact analysis (what depends on X)

❌ **Don't use repo-intel for**:
- Reading implementation details (use file reading)
- Text search in code (use grep/search)
- Understanding code semantics (read the code)

## Workflow Pattern

1. **Index** → Run `repo-intel index` first
2. **Query** → Use `repo-intel tool` to find locations
3. **Read** → Use file reading to see implementation
4. **Edit** → Modify code as needed
5. **Re-index** → Update after significant changes

## Symbol Types

- `function` - Standalone functions
- `class` - Classes, structs
- `method` - Class methods
- `interface` - Interfaces, traits
- `endpoint` - HTTP endpoints

## Example Usage

```bash
# Find where UserService is defined
repo-intel tool find-symbol --name UserService --json

# Find all API endpoints
repo-intel tool list-symbols --kind endpoint --json

# Understand dependencies
repo-intel tool get-callers --name processPayment --json
repo-intel tool get-callees --name processPayment --json
```

## Output Format

Always returns JSON. Use `jq` or JSON parsing.

## Supported Languages

Python, JavaScript, TypeScript, Java, Rust, Go, PHP
```

## Tool Definition

Add repo-intel as a tool in your AI assistant:

```json
{
  "name": "repo-intel",
  "description": "Structural code intelligence tool for finding symbols, call graphs, and dependencies",
  "commands": [
    {
      "name": "init",
      "description": "Initialize repo-intel in a project",
      "usage": "repo-intel init [path]"
    },
    {
      "name": "index",
      "description": "Index the codebase",
      "usage": "repo-intel index --project <name> [--verbose]"
    },
    {
      "name": "list-symbols",
      "description": "List all symbols or filter by kind",
      "usage": "repo-intel tool list-symbols [--kind <type>] --json"
    },
    {
      "name": "find-symbol",
      "description": "Find a specific symbol by name",
      "usage": "repo-intel tool find-symbol --name <name> --json"
    },
    {
      "name": "get-callers",
      "description": "Find all callers of a function",
      "usage": "repo-intel tool get-callers --name <name> --json"
    },
    {
      "name": "get-callees",
      "description": "Find all functions called by a symbol",
      "usage": "repo-intel tool get-callees --name <name> --json"
    }
  ]
}
```

## Decision Tree for Tool Selection

```
User question about code?
│
├─ Location question ("Where is X?")
│  └─ Use: repo-intel find-symbol
│
├─ Relationship question ("What calls/uses X?")
│  └─ Use: repo-intel get-callers/get-callees
│
├─ Overview question ("What classes/functions exist?")
│  └─ Use: repo-intel list-symbols
│
├─ Implementation question ("How does X work?")
│  └─ Use: File Read tool (NOT repo-intel)
│
└─ Search question ("Find comments/strings")
   └─ Use: Grep/Search tool (NOT repo-intel)
```

## Integration Examples

### Claude Code (Anthropic)

```xml
<tool_use_hint>
When exploring a new codebase:
1. Check if .repo-intel exists
2. If not, run: repo-intel init && repo-intel index --project <name>
3. Use repo-intel tool commands to explore structure
4. Use Read tool for implementation details
5. Combine both for comprehensive analysis
</tool_use_hint>
```

### Cursor IDE

Add to `.cursorrules`:

```
repo-intel integration:
- Use `repo-intel tool` to find code locations quickly
- Use for structural queries (symbols, call graphs)
- Don't use for reading code (use built-in code viewing)
- Commands: init, index, list-symbols, find-symbol, get-callers, get-callees
```

### Continue

Add to `~/.continue/config.json`:

```json
{
  "tools": [
    {
      "name": "repo-intel",
      "description": "Structural code intelligence",
      "type": "subprocess",
      "command": "repo-intel"
    }
  ]
}
```

### Aider

Add context command:

```python
# In .aider.conf.yml
read: AI_AGENT_GUIDE.md
```

## Testing Integration

Test prompt to verify integration:

```
Test: "Use repo-intel to find all classes in this project"

Expected behavior:
1. Agent checks if indexed
2. Runs: repo-intel tool list-symbols --kind class --json
3. Presents results appropriately
```

## Monitoring Usage

Track repo-intel usage:

```bash
# Check index status
ls -lh .repo-intel/index.db

# Verify symbol count
repo-intel tool list-symbols --json | jq 'length'

# Check by language
repo-intel tool list-symbols --json | jq 'group_by(.language)'
```

## Performance Metrics

Expected performance:
- Indexing: ~1000-5000 LOC/second
- Query: <100ms
- Memory: Minimal (SQLite)

## Error Handling

Common issues:
1. Not indexed → Run `repo-intel index`
2. Empty results → Check language support
3. Outdated → Re-run index

## Best Practices

1. **Index first**: Always ensure codebase is indexed
2. **Use JSON**: Always use --json flag
3. **Combine tools**: repo-intel + Read + Edit
4. **Re-index**: After significant changes
5. **Filter early**: Use --kind to reduce scope
