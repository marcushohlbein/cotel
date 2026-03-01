# Project Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Set up the foundational Python project structure for repo-intel with configuration, documentation, and package directories

**Architecture:** Standard Python package with pyproject.toml for build/deps, modular source structure (core/parsers/analysis/tools/server/utils), using Hatchling build backend

**Tech Stack:** Python 3.11+, Hatchling, Click CLI, tree-sitter parsing

---

### Task 1: Create pyproject.toml

**Files:**
- Create: `pyproject.toml`

**Step 1: Create pyproject.toml with project metadata**

Write the complete pyproject.toml file with:
- Project metadata (name, version, description)
- Python version requirement (>=3.11)
- Core dependencies (click, tree-sitter libraries for 6 languages)
- Dev dependencies (pytest, black, ruff, mypy)
- CLI entry point
- Tool configurations (black, ruff, mypy)

File content (from spec):
```toml
[project]
name = "repo-intel"
version = "0.1.0"
description = "Local-first structural intelligence for code repositories"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.0",
    "tree-sitter>=0.20.0",
    "tree-sitter-python>=0.20.0",
    "tree-sitter-javascript>=0.20.0",
    "tree-sitter-java>=0.20.0",
    "tree-sitter-rust>=0.20.0",
    "tree-sitter-go>=0.20.0",
    "tree-sitter-php>=0.20.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[project.scripts]
repo-intel = "repo_intel.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

**Step 2: Verify pyproject.toml is valid TOML**

Run: `python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"`
Expected: No output (no error)

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add pyproject.toml with project metadata and dependencies"
```

---

### Task 2: Create README.md

**Files:**
- Create: `README.md`

**Step 1: Create README.md with project documentation**

Write the complete README.md file with:
- Project description
- Features list
- Installation instructions
- Usage examples

File content (from spec):
```markdown
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
```

**Step 2: Verify README.md is valid Markdown**

Run: `head -20 README.md`
Expected: Shows project header and content

**Step 3: Commit**

```bash
git add README.md
git commit -m "feat: add README.md with project documentation"
```

---

### Task 3: Create .gitignore

**Files:**
- Create: `.gitignore`

**Step 1: Create .gitignore with Python patterns**

Write the complete .gitignore file with:
- Python build artifacts
- Virtual environments
- IDE files
- repo-intel specific patterns

File content (from spec):
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/

# repo-intel
.repo-intel/
*.db
```

**Step 2: Verify .gitignore patterns work**

Run: `git status --short`
Expected: Only shows new files, no ignored artifacts

**Step 3: Commit**

```bash
git add .gitignore
git commit -m "feat: add .gitignore with Python and project patterns"
```

---

### Task 4: Create package directory structure

**Files:**
- Create: `src/repo_intel/__init__.py`
- Create: `src/repo_intel/core/__init__.py`
- Create: `src/repo_intel/parsers/__init__.py`
- Create: `src/repo_intel/analysis/__init__.py`
- Create: `src/repo_intel/tools/__init__.py`
- Create: `src/repo_intel/server/__init__.py`
- Create: `src/repo_intel/utils/__init__.py`

**Step 1: Create directory structure**

Run: `mkdir -p src/repo_intel/{core,parsers,analysis,tools,server,utils}`
Expected: No output (directories created)

**Step 2: Create all __init__.py files**

Run: `touch src/repo_intel/__init__.py src/repo_intel/core/__init__.py src/repo_intel/parsers/__init__.py src/repo_intel/analysis/__init__.py src/repo_intel/tools/__init__.py src/repo_intel/server/__init__.py src/repo_intel/utils/__init__.py`
Expected: No output (files created)

**Step 3: Verify package structure**

Run: `tree src/ -L 3` (or `find src/ -type f -name "__init__.py"`)
Expected output:
```
src/
└── repo_intel/
    ├── __init__.py
    ├── analysis/
    │   └── __init__.py
    ├── core/
    │   └── __init__.py
    ├── parsers/
    │   └── __init__.py
    ├── server/
    │   └── __init__.py
    ├── tools/
    │   └── __init__.py
    └── utils/
        └── __init__.py
```

**Step 4: Verify package can be discovered (dry-run)**

Run: `python -c "import sys; sys.path.insert(0, 'src'); import repo_intel; print(repo_intel.__file__)"` (optional, may fail until built)
Expected: Shows path to repo_intel package OR error about missing cli module (OK)

**Step 5: Commit**

```bash
git add src/
git commit -m "feat: add package directory structure with module __init__ files"
```

---

### Task 5: Final verification

**Files:**
- Verify: All files from previous tasks

**Step 1: Verify all files exist**

Run: `ls -la pyproject.toml README.md .gitignore src/repo_intel/__init__.py`
Expected: All files listed

**Step 2: Verify directory structure**

Run: `ls -la src/repo_intel/`
Expected: Shows `core/`, `parsers/`, `analysis/`, `tools/`, `server/`, `utils/` directories

**Step 3: Verify git history**

Run: `git log --oneline -5`
Expected: Shows 4 commits for the project foundation tasks

**Step 4: Self-review checklist**

- [x] pyproject.toml created with all required fields
- [x] README.md created with project documentation
- [x] .gitignore created with Python and project patterns
- [x] All module directories created in src/repo_intel/
- [x] All __init__.py files created
- [x] All changes committed with proper messages

---

## Summary

This plan creates the foundational project structure for repo-intel:
1. Project configuration (pyproject.toml)
2. Documentation (README.md)
3. Git ignore patterns (.gitignore)
4. Package structure with 6 modules (core, parsers, analysis, tools, server, utils)

Total commits: 4 (one per major component)

**Next steps after this plan:**
- Implement core module (config, storage, indexing)
- Implement parsers for target languages
- Implement analysis modules (call graph, dependency graph, etc.)
- Implement CLI tools
- Implement stdio server
