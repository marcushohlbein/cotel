# How to Test repo-intel on a Real Repository

## Quick Start

```bash
# 1. Install repo-intel
cd /path/to/repo-intel
pip install -e .

# 2. Navigate to your target repository
cd /path/to/your-project

# 3. Initialize repo-intel
repo-intel init

# 4. Index your code
repo-intel index --project myproject
```

## Example: Testing on a Python Project

### Step 1: Create a Sample Project

```bash
mkdir demo-project
cd demo-project
```

Create `demo-project/app.py`:
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users."""
    return jsonify({"users": []})

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    """Get user by ID."""
    return jsonify({"id": id, "name": "Test"})

def helper_function():
    """A helper function."""
    return "help"

class UserService:
    """User service class."""

    def get_all(self):
        """Get all users."""
        return helper_function()
```

Create `demo-project/utils.py`:
```python
def format_response(data):
    """Format API response."""
    return {"data": data}

def validate_request(req):
    """Validate incoming request."""
    return True
```

### Step 2: Initialize and Index

```bash
# Initialize
repo-intel init

# Index the project
repo-intel index --project demo
```

Output:
```
Initialized repo-intel in .
Indexed 2 files
```

### Step 3: Query Your Code

#### List All Symbols

```bash
repo-intel tool list-symbols --json
```

Output:
```json
[
  {
    "id": "...",
    "name": "get_users",
    "kind": "endpoint",
    "language": "python",
    "http_method": "GET",
    "path": "/api/users"
  },
  {
    "name": "UserService",
    "kind": "class"
  },
  {
    "name": "helper_function",
    "kind": "function"
  }
]
```

#### Find a Specific Symbol

```bash
repo-intel tool find-symbol --name get_users --json
```

#### Filter by Symbol Kind

```bash
# List only functions
repo-intel tool list-symbols --kind function --json

# List only endpoints
repo-intel tool list-symbols --kind endpoint --json

# List only classes
repo-intel tool list-symbols --kind class --json
```

#### Explore Call Graphs

```bash
# Find callers of a function
repo-intel tool get-callers --name helper_function --json

# Find callees (what a function calls)
repo-intel tool get-callees --name UserService --json
```

## Testing on a Real Repository

### Example 1: FastAPI Application

```bash
cd your-fastapi-app
repo-intel init
repo-intel index --project fastapi-app

# Find all HTTP endpoints
repo-intel tool list-symbols --kind endpoint --json

# Find specific endpoint
repo-intel tool find-symbol --name get_users --json
```

### Example 2: Flask Application

```bash
cd your-flask-app
repo-intel init
repo-intel index --project flask-app

# List all routes/endpoints
repo-intel tool list-symbols --kind endpoint --json | jq '.[] | {name, path, http_method}'
```

### Example 3: Python Package

```bash
cd your-python-package
repo-intel init
repo-intel index --project mypackage

# Find all functions
repo-intel tool list-symbols --kind function --json

# Find all classes
repo-intel tool list-symbols --kind class --json
```

## Advanced Queries

### Combine with jq for Filtering

```bash
# Get all endpoints with GET method
repo-intel tool list-symbols --json | \
  jq '.[] | select(.http_method == "GET")'

# Get symbols from a specific file
repo-intel tool list-symbols --json | \
  jq '.[] | select(.file_id == "file-id-here")'

# Count symbols by kind
repo-intel tool list-symbols --json | \
  jq 'group_by(.kind) | map({kind: .[0].kind, count: length})'
```

### Export to File

```bash
# Export all symbols to JSON file
repo-intel tool list-symbols --json > symbols.json

# Export specific query
repo-intel tool find-symbol --name my_function --json > function_info.json
```

## Incremental Indexing

repo-intel only reindexes changed files:

```bash
# Make changes to a file
echo "def new_function(): pass" >> app.py

# Reindex (only changed files are processed)
repo-intel index --project demo
```

## Inspect the Database Directly

```bash
cd your-project
sqlite3 .repo-intel/index.db

# SQL queries
SELECT name, kind, language FROM symbols;
SELECT * FROM symbols WHERE kind = 'endpoint';
SELECT * FROM relations WHERE relation_type = 'calls';
```

## Troubleshooting

### Issue: No symbols found

```bash
# Check if database exists
ls -lh .repo-intel/index.db

# Re-index from scratch
rm .repo-intel/index.db
repo-intel index --project myproject
```

### Issue: Wrong project detected

```bash
# Check config
cat .repo-intel/config.json

# Manually set project root
{
  "db_path": ".repo-intel/index.db",
  "project_root": "/absolute/path/to/project",
  "incremental_enabled": true
}
```

### Issue: Parser not working

```bash
# Check if language is supported
repo-intel tool list-symbols --json

# Currently supported: Python, JavaScript, TypeScript
# More languages planned (Java, Rust, Go, PHP)
```

## Performance Tips

1. **Large repositories**: Indexing scales linearly with LOC
2. **Incremental updates**: Only changed files are reindexed
3. **Database size**: ~1KB per symbol (typical project: 1-10MB)
4. **Query speed**: Symbol lookups < 100ms

## Clean Up

```bash
# Remove index database
rm .repo-intel/index.db

# Remove entire repo-intel config
rm -rf .repo-intel
```
