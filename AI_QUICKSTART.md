# Quick Start for AI Agents

## TL;DR

```bash
# 1. Setup (one-time)
repo-intel init && repo-intel index --project myproject

# 2. Query
repo-intel tool list-symbols --json
repo-intel tool find-symbol --name MyFunction --json
repo-intel tool get-callers --name MyFunction --json
```

## The One-Liner Learning

**repo-intel answers STRUCTURAL questions, not SEMANTIC questions.**

- ✅ WHERE is X? → repo-intel
- ✅ WHAT calls X? → repo-intel
- ❌ HOW does X work? → Read tool
- ❌ WHY does X do Y? → Read tool

## Decision Tree

```
Question type?
├─ Location → repo-intel
├─ Relationship → repo-intel
├─ Implementation → Read file
└─ Search → Grep
```

## Remember

1. **Index first**: `repo-intel index --project NAME`
2. **Use JSON**: Always `--json` flag
3. **Combine tools**: repo-intel → Read → Edit
4. **Re-index**: After major changes

## Supported Languages

Python, JavaScript, TypeScript, Java, Rust, Go, PHP

## More Info

- Full guide: `AI_AGENT_GUIDE.md`
- Templates: `PROMPT_TEMPLATES.md`
- Integration: `AI_INTEGRATION.md`
