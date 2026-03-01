# Teaching Coding Agents to Use repo-intel

## Summary

Two complementary approaches for integrating repo-intel with AI coding agents:

### 1. SKILL (Primary Method) ✅

**File:** `.agents/skills/repo-intel/SKILL.md`

**What it does:**
- Teaches agents WHEN to use repo-intel
- Teaches agents HOW to use repo-intel
- Provides context, examples, and best practices
- Auto-activates based on user queries

**Activation Triggers:**
- "Find all classes in this codebase"
- "What calls this function"
- "Show HTTP endpoints"
- "Trace call hierarchy"
- "Analyze code structure"
- 15+ more triggers

**Content Covered:**
- Quick start guide
- 5 core tools (list-symbols, find-symbol, get-callers, get-callees, get-dependencies)
- 5 practical examples (exploring, impact analysis, debugging, API docs, class hierarchies)
- Best practices
- Language-specific features (Python, JS, Java, Rust, Go, PHP)
- Troubleshooting

**When it activates:**
- On-demand when agent recognizes structural analysis needs
- When user asks about code relationships
- When exploring unfamiliar codebases

### 2. HOOK (Optional Enhancement)

**File:** `.agents/hooks/auto-index.sh`

**What it does:**
- Automatically indexes repository
- Keeps index fresh
- Runs in background (non-blocking)
- Smart caching (skips if recent)

**Integration options:**
1. Shell integration (recommended)
2. Manual execution
3. Cron job

**When to use:**
- Large, frequently changing codebases
- Team projects
- When you always need fresh data

## Comparison

| Feature | Skill | Hook |
|---------|-------|------|
| **Purpose** | Teach usage | Automate indexing |
| **Activation** | On-demand | Proactive |
| **What it does** | Explains HOW & WHEN | Keeps data fresh |
| **Required?** | Yes (recommended) | No (optional) |
| **Setup** | Already done | Optional setup |

## Recommended Setup

### Minimal (Just the Skill)

```bash
# Skill is already in place
.agents/skills/repo-intel/SKILL.md

# Agent will learn to use repo-intel when needed
```

### Enhanced (Skill + Hook)

```bash
# Add shell integration for auto-indexing
echo '
# Auto-index with repo-intel on cd
function cd() {
    builtin cd "$@" || return
    [ -f .git/config ] && [ -x .agents/hooks/auto-index.sh ] && .agents/hooks/auto-index.sh
}
' >> ~/.zshrc

source ~/.zshrc
```

## How Agents Will Use It

### Scenario 1: "What calls this function?"

**Agent process:**
1. Recognizes trigger → Activates repo-intel skill
2. Reads skill documentation
3. Executes: `repo-intel tool get-callers --name <function> --json`
4. Analyzes JSON output
5. Reports findings to user

### Scenario 2: "Explore this codebase"

**Agent process:**
1. Recognizes trigger → Activates repo-intel skill
2. Checks if indexed: `ls .repo-intel/index.db`
3. If not: `repo-intel index --project <name> -v`
4. Discovers structure: `repo-intel tool list-symbols --json`
5. Groups by kind/language
6. Reports overview

### Scenario 3: "Find all API endpoints"

**Agent process:**
1. Activates skill
2. Queries endpoints: `repo-intel tool list-symbols --kind endpoint --json`
3. Formats with jq: `| jq '.[] | {method, path, name}'`
4. Reports to user

## Why a Skill (Not Plugin/Hook)?

### Skills are ideal because:

1. **Contextual Teaching**
   - Explain WHEN to use (triggers)
   - Explain WHY to use (benefits)
   - Show HOW to use (examples)

2. **Flexible Activation**
   - On-demand (only when needed)
   - No overhead when not analyzing code
   - Works with any agent type

3. **Comprehensive Documentation**
   - Not just tool reference
   - Real-world examples
   - Best practices built-in

4. **Multi-Agent Compatible**
   - Works with opencode
   - Works with Claude Code
   - Works with any agent that supports skills

### Hooks complement skills:

- **Hooks** = Proactive automation (keep data fresh)
- **Skills** = Reactive teaching (use when needed)
- **Together** = Best experience

## Integration Status

✅ Skill created: `.agents/skills/repo-intel/SKILL.md` (686 lines)
✅ Hook created: `.agents/hooks/auto-index.sh` (optional)
✅ Documentation: `.agents/hooks/README.md`
✅ Activation triggers: 20+
✅ Examples: 5 practical scenarios
✅ Language support: 7 languages

## Next Steps

1. **Test the skill:**
   ```bash
   # In any project
   repo-intel index --project test -v

   # Try a trigger with your agent
   # "Show me all classes in this codebase"
   ```

2. **Optional: Enable auto-indexing hook**
   ```bash
   # Add to shell
   echo 'function cd() { builtin cd "$@"; [ -f .agents/hooks/auto-index.sh ] && .agents/hooks/auto-index.sh; }' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Let agents discover it**
   - Agents will auto-activate skill when triggers match
   - No manual configuration needed

---

**Result:** Agents now understand repo-intel and will use it automatically when analyzing code structure, tracing relationships, or exploring codebases!
