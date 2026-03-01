# Testing Agent Integration

## Quick Test

### 1. Verify Installation

```bash
# Check repo-intel is installed
which repo-intel
# Should output: /Users/.../bin/repo-intel

# Check skill exists
ls .agents/skills/repo-intel/SKILL.md
# Should exist with 686 lines
```

### 2. Test Skill Activation

In OpenCode or Claude Code, try these queries:

**Query 1: Find all classes**
```
"Find all classes in this codebase"
```

**Expected agent behavior:**
1. Activates repo-intel skill (matches trigger)
2. Checks if indexed
3. Runs: `repo-intel index --project test` (if needed)
4. Runs: `repo-intel tool list-symbols --kind class --json`
5. Returns list of classes

**Query 2: Call graph**
```
"What calls the main function?"
```

**Expected agent behavior:**
1. Activates skill
2. Runs: `repo-intel tool get-callers --name main --json`
3. Reports callers

**Query 3: API structure**
```
"Show me all HTTP endpoints in this API"
```

**Expected agent behavior:**
1. Activates skill
2. Runs: `repo-intel tool list-symbols --kind endpoint --json`
3. Groups by method/path
4. Reports endpoints

### 3. Test Hook (Optional)

```bash
# Test hook manually
.agents/hooks/auto-index.sh

# Check if it ran
ls -la .repo-intel/index.db
```

## Manual Testing Examples

### Example 1: Explore a Python Project

```bash
# In a Python project
cd /path/to/python-project

# Index
repo-intel index --project python-app -v

# Find all functions
repo-intel tool list-symbols --kind function --json | jq '.[].name'

# Find Flask/FastAPI endpoints
repo-intel tool list-symbols --kind endpoint --json | \
  jq '.[] | {method: .http_method, path: .path}'

# Find what calls a function
repo-intel tool get-callers --name main --json
```

### Example 2: Analyze a Java Spring Boot Project

```bash
# Index
repo-intel index --project spring-app -v

# Find all Spring controllers
repo-intel tool list-symbols --kind class --json | \
  jq '.[] | select(.name | endswith("Controller"))'

# Find all GET endpoints
repo-intel tool list-symbols --kind endpoint --json | \
  jq '.[] | select(.http_method == "GET")'

# Trace call chain
repo-intel tool get-callees --name getData --json
```

### Example 3: Explore a JavaScript Express App

```bash
# Index
repo-intel index --project express-app -v

# Find Express routes
repo-intel tool list-symbols --kind endpoint --json

# Find Express middleware
repo-intel tool list-symbols --kind function --json | \
  jq '.[] | select(.name | contains("middleware"))'
```

## Expected Skill Activation Scenarios

### Scenario 1: Understanding Code Structure
**User:** "What are the main components of this codebase?"

**Agent will:**
1. Activate repo-intel skill
2. Index if needed
3. List symbols by kind
4. Group and summarize
5. Report architecture overview

### Scenario 2: Impact Analysis
**User:** "What will break if I change the UserService class?"

**Agent will:**
1. Activate skill
2. Find UserService
3. Get all callers
4. Get all callees
5. Analyze dependencies
6. Report impact assessment

### Scenario 3: Debugging
**User:** "Where is the validateToken function called from?"

**Agent will:**
1. Activate skill
2. Run get-callers for validateToken
3. Show all call sites
4. Optionally trace upward

### Scenario 4: API Documentation
**User:** "Document all the API endpoints"

**Agent will:**
1. Activate skill
2. List all endpoints
3. Group by resource
4. Format as documentation
5. Optionally read code for each endpoint

## Verification Checklist

**✅ Skill file exists:**
```bash
ls -la .agents/skills/repo-intel/SKILL.md
```

**✅ Hook is executable (if using):**
```bash
ls -la .agents/hooks/auto-index.sh
```

**✅ repo-intel works:**
```bash
repo-intel --help
```

**✅ Can index a test project:**
```bash
mkdir -p test-agent
echo "def test(): pass" > test-agent/test.py
cd test-agent
repo-intel index --project test
repo-intel tool list-symbols --json
```

**✅ Agent recognizes triggers:**
- Try various natural language queries
- Check if agent activates skill
- Verify structured JSON usage

## Troubleshooting Agent Integration

**Problem:** Agent doesn't use repo-intel

**Check:**
1. Skill file location correct? `.agents/skills/repo-intel/SKILL.md`
2. Trigger phrases match skill activation triggers?
3. repo-intel in PATH? `which repo-intel`
4. Agent supports skills? (OpenCode, Claude Code do)

**Problem:** Agent uses wrong commands

**Solution:**
1. Check skill documentation is clear
2. Add more examples to skill
3. Provide specific trigger phrases

**Problem:** JSON output not parsed correctly

**Solution:**
1. Always use `--json` flag
2. Show `jq` examples in skill
3. Provide parsing examples

## Success Metrics

**You know it's working when:**
- ✅ Agent activates skill on structural queries
- ✅ Agent uses correct CLI commands
- ✅ Agent parses JSON output correctly
- ✅ Agent provides useful insights from data
- ✅ No need to explain repo-intel to agent

**Test queries to try:**
1. "Find all classes"
2. "What calls this function"
3. "Show API endpoints"
4. "Trace the call chain"
5. "Analyze dependencies"

---

**Need help?** Check `.agents/AGENT_INTEGRATION.md` for full integration guide.
