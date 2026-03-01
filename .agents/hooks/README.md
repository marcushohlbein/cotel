# Hook: auto-index.sh

**Purpose:** Automatically index repository with repo-intel when entering a project directory.

**When it runs:** On shell session start or directory change (if integrated with shell)

**What it does:**
1. Checks if repo-intel is installed
2. Checks if current directory is a git repository
3. Checks if repository was indexed recently (within last hour)
4. If not, indexes in background

**Integration:**

### Option 1: Shell Integration (Recommended)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Auto-index with repo-intel on cd
function cd() {
    builtin cd "$@" || return
    [ -f .git/config ] && [ -x .agents/hooks/auto-index.sh ] && .agents/hooks/auto-index.sh
}
```

### Option 2: Manual Execution

```bash
# Run manually
.agents/hooks/auto-index.sh
```

### Option 3: Cron Job (Large Projects)

```bash
# Index every 2 hours
0 */2 * * * cd /path/to/project && repo-intel index --project auto
```

**Benefits:**
- Always have fresh index when you need it
- Runs in background (no blocking)
- Smart caching (only reindexes if changed)
- Zero-friction usage

**Note:** For most projects, manual indexing is sufficient. Use auto-indexing for:
- Very large codebases
- Frequently changing code
- Team projects where staying in sync matters
