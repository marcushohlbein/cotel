# repo-intel Implementation Plan (Python)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local-first, language-agnostic structural intelligence layer for repositories that enables LLM agents to reason about symbols, call graphs, dependencies, inheritance, and HTTP boundaries.

**Architecture:** Python-based CLI tool using Tree-sitter for language parsing, SQLite for storage, and stdio protocol for tool integration. Modular design with separate parsers per language, incremental reindexing, and monorepo awareness.

**Tech Stack:** Python 3.11+, Tree-sitter, SQLite (built-in), Click (CLI), pyproject.toml

---

## Task 1: Project Foundation

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `.gitignore`
- Create: `src/__init__.py`

**Step 1: Create pyproject.toml**

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

**Step 2: Create README.md**

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

**Step 3: Create .gitignore**

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

**Step 4: Create base package structure**

```bash
mkdir -p src/repo_intel/{core,parsers,analysis,tools,server,utils}
touch src/repo_intel/__init__.py
touch src/repo_intel/core/__init__.py
touch src/repo_intel/parsers/__init__.py
touch src/repo_intel/analysis/__init__.py
touch src/repo_intel/tools/__init__.py
touch src/repo_intel/server/__init__.py
touch src/repo_intel/utils/__init__.py
```

**Step 5: Commit**

```bash
git add pyproject.toml README.md .gitignore src/
git commit -m "feat: project foundation with Python tooling"
```

---

## Task 2: Core Configuration Module

**Files:**
- Create: `src/repo_intel/core/config.py`
- Create: `tests/test_config.py`

**Step 1: Write configuration model tests**

```python
from repo_intel.core.config import Config, get_config

def test_config_defaults():
    config = Config()
    assert config.db_path == ".repo-intel/index.db"
    assert config.project_root is not None

def test_config_from_dict():
    config = Config.from_dict({"db_path": "custom.db"})
    assert config.db_path == "custom.db"

def test_get_config_creates_default():
    config = get_config()
    assert isinstance(config, Config)
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_config.py -v
```

Expected: FAIL - module not found

**Step 3: Implement configuration module**

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json

@dataclass
class Config:
    db_path: str = ".repo-intel/index.db"
    project_root: Optional[str] = None
    incremental_enabled: bool = True
    watch_enabled: bool = False

    def __post_init__(self):
        if self.project_root is None:
            self.project_root = str(Path.cwd())

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        return cls(**data)

    def to_dict(self) -> dict:
        return {
            "db_path": self.db_path,
            "project_root": self.project_root,
            "incremental_enabled": self.incremental_enabled,
            "watch_enabled": self.watch_enabled,
        }

def get_config() -> Config:
    config_path = Path.cwd() / ".repo-intel" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)
            return Config.from_dict(data)
    return Config()
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_config.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/config.py tests/test_config.py
git commit -m "feat: core configuration module"
```

---

## Task 3: SQLite Storage Layer

**Files:**
- Create: `src/repo_intel/core/storage.py`
- Create: `tests/test_storage.py`

**Step 1: Write storage tests**

```python
import pytest
from repo_intel.core.storage import Storage, SymbolEntry, FileEntry, Relation

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"

@pytest.fixture
def storage(db_path):
    return Storage(str(db_path))

def test_storage_initialization(storage):
    assert storage.conn is not None

def test_insert_file(storage):
    file_entry = FileEntry(
        id="f1",
        path="/test.py",
        language="python",
        project="test",
        hash="abc123"
    )
    storage.insert_file(file_entry)
    files = storage.get_files()
    assert len(files) == 1
    assert files[0].path == "/test.py"

def test_insert_symbol(storage):
    symbol = SymbolEntry(
        id="s1",
        name="test_func",
        kind="function",
        language="python",
        file_id="f1",
        project="test",
        start_line=1,
        end_line=5,
        exported=True
    )
    storage.insert_symbol(symbol)
    symbols = storage.get_symbols()
    assert len(symbols) == 1
    assert symbols[0].name == "test_func"

def test_insert_relation(storage):
    relation = Relation(
        id="r1",
        from_symbol_id="s1",
        to_symbol_id="s2",
        relation_type="calls"
    )
    storage.insert_relation(relation)
    relations = storage.get_relations()
    assert len(relations) == 1
    assert relations[0].relation_type == "calls"
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_storage.py -v
```

Expected: FAIL - module not found

**Step 3: Implement storage module**

```python
import sqlite3
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FileEntry:
    id: str
    path: str
    language: str
    project: str
    hash: str

@dataclass
class SymbolEntry:
    id: str
    name: str
    kind: str
    language: str
    file_id: str
    project: str
    start_line: int
    end_line: int
    exported: bool
    http_method: Optional[str] = None
    path: Optional[str] = None

@dataclass
class Relation:
    id: str
    from_symbol_id: str
    to_symbol_id: str
    relation_type: str

class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                path TEXT,
                language TEXT,
                project TEXT,
                hash TEXT
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                id TEXT PRIMARY KEY,
                name TEXT,
                kind TEXT,
                language TEXT,
                file_id TEXT,
                project TEXT,
                start_line INTEGER,
                end_line INTEGER,
                exported INTEGER,
                http_method TEXT,
                path TEXT
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id TEXT PRIMARY KEY,
                from_symbol_id TEXT,
                to_symbol_id TEXT,
                relation_type TEXT
            )
        """)

        self.conn.commit()

    def insert_file(self, file_entry: FileEntry):
        self.conn.execute(
            "INSERT OR REPLACE INTO files VALUES (?, ?, ?, ?, ?)",
            (file_entry.id, file_entry.path, file_entry.language,
             file_entry.project, file_entry.hash)
        )
        self.conn.commit()

    def insert_symbol(self, symbol: SymbolEntry):
        self.conn.execute(
            """INSERT OR REPLACE INTO symbols
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (symbol.id, symbol.name, symbol.kind, symbol.language,
             symbol.file_id, symbol.project, symbol.start_line,
             symbol.end_line, int(symbol.exported), symbol.http_method,
             symbol.path)
        )
        self.conn.commit()

    def insert_relation(self, relation: Relation):
        self.conn.execute(
            "INSERT OR REPLACE INTO relations VALUES (?, ?, ?, ?)",
            (relation.id, relation.from_symbol_id, relation.to_symbol_id,
             relation.relation_type)
        )
        self.conn.commit()

    def get_files(self) -> List[FileEntry]:
        cursor = self.conn.execute("SELECT * FROM files")
        return [FileEntry(*row) for row in cursor.fetchall()]

    def get_symbols(self) -> List[SymbolEntry]:
        cursor = self.conn.execute("SELECT * FROM symbols")
        return [SymbolEntry(*row) for row in cursor.fetchall()]

    def get_relations(self) -> List[Relation]:
        cursor = self.conn.execute("SELECT * FROM relations")
        return [Relation(*row) for row in cursor.fetchall()]

    def get_file_by_path(self, path: str) -> Optional[FileEntry]:
        cursor = self.conn.execute("SELECT * FROM files WHERE path = ?", (path,))
        row = cursor.fetchone()
        return FileEntry(*row) if row else None

    def get_symbols_by_file(self, file_id: str) -> List[SymbolEntry]:
        cursor = self.conn.execute(
            "SELECT * FROM symbols WHERE file_id = ?", (file_id,)
        )
        return [SymbolEntry(*row) for row in cursor.fetchall()]

    def delete_symbols_by_file(self, file_id: str):
        self.conn.execute("DELETE FROM symbols WHERE file_id = ?", (file_id,))
        self.conn.execute(
            "DELETE FROM relations WHERE from_symbol_id IN "
            "(SELECT id FROM symbols WHERE file_id = ?)",
            (file_id,)
        )
        self.conn.commit()
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_storage.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/storage.py tests/test_storage.py
git commit -m "feat: SQLite storage layer with schema"
```

---

## Task 4: File Hashing Utility

**Files:**
- Create: `src/repo_intel/utils/hashing.py`
- Create: `tests/test_hashing.py`

**Step 1: Write hashing tests**

```python
from repo_intel.utils.hashing import hash_file, file_changed

def test_hash_file(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')")
    h1 = hash_file(str(test_file))
    h2 = hash_file(str(test_file))
    assert h1 == h2
    assert len(h1) == 64  # SHA-256

def test_file_change_detection(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("v1")
    h1 = hash_file(str(test_file))
    test_file.write_text("v2")
    h2 = hash_file(str(test_file))
    assert h1 != h2
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_hashing.py -v
```

Expected: FAIL

**Step 3: Implement hashing module**

```python
import hashlib
from pathlib import Path

def hash_file(file_path: str) -> str:
    """Generate SHA-256 hash of file contents."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def file_changed(file_path: str, stored_hash: str) -> bool:
    """Check if file has changed based on hash."""
    current_hash = hash_file(file_path)
    return current_hash != stored_hash
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_hashing.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/utils/hashing.py tests/test_hashing.py
git commit -m "feat: file hashing utility for incremental indexing"
```

---

## Task 5: File Walker Utility

**Files:**
- Create: `src/repo_intel/utils/file_walker.py`
- Create: `tests/test_file_walker.py`

**Step 1: Write file walker tests**

```python
from repo_intel.utils.file_walker import walk_project, find_project_roots

def test_walk_project(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# test")
    (tmp_path / ".git").mkdir()

    files = list(walk_project(str(tmp_path)))
    assert len(files) == 2
    assert any(f.endswith("main.py") for f in files)
    assert any(f.endswith("README.md") for f in files)
    assert not any(".git" in f for f in files)

def test_find_project_roots(tmp_path):
    (tmp_path / "frontend").mkdir()
    (tmp_path / "backend").mkdir()
    (tmp_path / "frontend" / "package.json").write_text("{}")
    (tmp_path / "backend" / "pom.xml").write_text("<project></project>")

    roots = find_project_roots(str(tmp_path))
    assert len(roots) == 2
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_file_walker.py -v
```

Expected: FAIL

**Step 3: Implement file walker module**

```python
import os
from pathlib import Path
from typing import List, Set

IGNORED_DIRS = {
    ".git", ".svn", "node_modules", "venv", ".venv",
    "__pycache__", ".pytest_cache", "dist", "build",
    ".repo-intel"
}

PROJECT_MARKERS = [
    "package.json", "pom.xml", "build.gradle", "Cargo.toml",
    "go.mod", "composer.json", "requirements.txt", "pyproject.toml"
]

def walk_project(root: str) -> List[str]:
    """Walk project directory and return source files."""
    files = []
    root_path = Path(root)

    for file_path in root_path.rglob("*"):
        if file_path.is_file():
            relative = file_path.relative_to(root_path)
            parts = relative.parts

            # Skip ignored directories
            if any(part in IGNORED_DIRS for part in parts):
                continue

            files.append(str(file_path))

    return files

def find_project_roots(root: str) -> List[str]:
    """Find monorepo subprojects by marker files."""
    projects = []
    root_path = Path(root)

    for item in root_path.iterdir():
        if item.is_dir():
            for marker in PROJECT_MARKERS:
                if (item / marker).exists():
                    projects.append(str(item))
                    break

    return projects
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_file_walker.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/utils/file_walker.py tests/test_file_walker.py
git commit -m "feat: file walking and project detection"
```

---

## Task 6: Language Detector

**Files:**
- Create: `src/repo_intel/utils/language_detector.py`
- Create: `tests/test_language_detector.py`

**Step 1: Write language detection tests**

```python
from repo_intel.utils.language_detector import detect_language

def test_python_detection():
    assert detect_language("test.py") == "python"
    assert detect_language("test.pyi") == "python"

def test_javascript_detection():
    assert detect_language("test.js") == "javascript"
    assert detect_language("test.jsx") == "javascript"

def test_typescript_detection():
    assert detect_language("test.ts") == "typescript"
    assert detect_language("test.tsx") == "typescript"

def test_java_detection():
    assert detect_language("Test.java") == "java"

def test_rust_detection():
    assert detect_language("main.rs") == "rust"

def test_go_detection():
    assert detect_language("main.go") == "go"

def test_php_detection():
    assert detect_language("index.php") == "php"

def test_unknown_detection():
    assert detect_language("README.md") is None
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_language_detector.py -v
```

Expected: FAIL

**Step 3: Implement language detector**

```python
from pathlib import Path

LANGUAGE_MAP = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".rs": "rust",
    ".go": "go",
    ".php": "php",
}

def detect_language(file_path: str) -> str | None:
    """Detect programming language from file extension."""
    ext = Path(file_path).suffix
    return LANGUAGE_MAP.get(ext)
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_language_detector.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/utils/language_detector.py tests/test_language_detector.py
git commit -m "feat: language detection by file extension"
```

---

## Task 7: Base Parser Interface

**Files:**
- Create: `src/repo_intel/parsers/base.py`
- Create: `tests/test_parser_base.py`

**Step 1: Write parser interface tests**

```python
from repo_intel.parsers.base import Parser, ParseResult

def test_parse_result_structure():
    result = ParseResult(
        symbols=[],
        imports=[],
        relations=[]
    )
    assert result.symbols == []
    assert result.imports == []
    assert result.relations == []

def test_parser_interface():
    class TestParser(Parser):
        def parse(self, content: str, file_id: str) -> ParseResult:
            return ParseResult(symbols=[], imports=[], relations=[])

    parser = TestParser()
    result = parser.parse("test content", "file_id")
    assert isinstance(result, ParseResult)
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_parser_base.py -v
```

Expected: FAIL

**Step 3: Implement base parser interface**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class Symbol:
    id: str
    name: str
    kind: str
    start_line: int
    end_line: int
    exported: bool
    http_method: str | None = None
    path: str | None = None

@dataclass
class Import:
    module: str
    line: int

@dataclass
class Relation:
    from_id: str
    to_id: str
    relation_type: str

@dataclass
class ParseResult:
    symbols: List[Symbol]
    imports: List[Import]
    relations: List[Relation]

class Parser(ABC):
    """Base parser interface for all language parsers."""

    @abstractmethod
    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse file content and extract symbols, imports, and relations."""
        pass
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_parser_base.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/parsers/base.py tests/test_parser_base.py
git commit -m "feat: base parser interface"
```

---

## Task 8: Python Parser (Tree-sitter)

**Files:**
- Create: `src/repo_intel/parsers/python_parser.py`
- Create: `tests/test_python_parser.py`

**Step 1: Write Python parser tests**

```python
from repo_intel.parsers.python_parser import PythonParser

def test_parse_function():
    code = """
def hello_world():
    print('hello')
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    assert len(result.symbols) == 1
    assert result.symbols[0].name == "hello_world"
    assert result.symbols[0].kind == "function"

def test_parse_class():
    code = """
class MyClass:
    def method(self):
        pass
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyClass" in symbols
    assert symbols["MyClass"].kind == "class"
    assert "method" in symbols
    assert symbols["method"].kind == "method"

def test_parse_imports():
    code = """
import os
from sys import argv
from collections import defaultdict
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    assert len(result.imports) == 3
    imports = [i.module for i in result.imports]
    assert "os" in imports
    assert "sys" in imports
    assert "collections" in imports

def test_parse_decorator_endpoint():
    code = """
from flask import Flask
app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    pass
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    endpoint_symbols = [s for s in result.symbols if s.kind == "endpoint"]
    assert len(endpoint_symbols) == 1
    assert endpoint_symbols[0].name == "get_users"
    assert endpoint_symbols[0].http_method == "GET"
    assert endpoint_symbols[0].path == "/users"

def test_function_calls():
    code = """
def caller():
    callee()
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    call_relations = [r for r in result.relations if r.relation_type == "calls"]
    assert len(call_relations) == 1
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_python_parser.py -v
```

Expected: FAIL

**Step 3: Implement Python parser**

```python
from tree_sitter import Language, Parser
from repo_intel.parsers.base import Parser, ParseResult, Symbol, Import, Relation
import uuid

class PythonParser(Parser):
    """Python language parser using Tree-sitter."""

    def __init__(self):
        self.parser = Parser()
        self.language = Language("vendor/tree-sitter-python")
        self.parser.set_language(self.language)

    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse Python code and extract symbols."""
        tree = self.parser.parse(bytes(content, "utf-8"))
        root_node = tree.root_node

        symbols = []
        imports = []
        relations = []

        self._traverse(root_node, content, file_id, symbols, imports, relations)

        return ParseResult(
            symbols=symbols,
            imports=imports,
            relations=relations
        )

    def _traverse(self, node, content, file_id, symbols, imports, relations):
        """Recursively traverse tree nodes."""

        # Handle function definitions
        if node.type == "function_definition":
            func_name = self._get_child_name(node, "identifier")
            if func_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(Symbol(
                    id=symbol_id,
                    name=func_name,
                    kind="function",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    exported=False,
                    http_method=self._extract_http_method(node),
                    path=self._extract_http_path(node)
                ))

                # Extract function calls
                self._extract_calls(node, symbol_id, relations)

        # Handle class definitions
        elif node.type == "class_definition":
            class_name = self._get_child_name(node, "identifier")
            if class_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(Symbol(
                    id=symbol_id,
                    name=class_name,
                    kind="class",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    exported=False
                ))

                # Check for inheritance
                self._extract_inheritance(node, symbol_id, relations)

        # Handle imports
        elif node.type in ("import_statement", "import_from_statement"):
            self._extract_import(node, imports)

        # Recurse into children
        for child in node.children:
            self._traverse(child, content, file_id, symbols, imports, relations)

    def _get_child_name(self, node, child_type):
        """Extract name from child node by type."""
        for child in node.children:
            if child.type == child_type:
                return child.text.decode("utf-8")
        return None

    def _extract_calls(self, node, caller_id, relations):
        """Extract function calls from function body."""
        for child in node.children:
            if child.type == "call":
                func_name = child.children[0].text.decode("utf-8") if child.children else None
                if func_name:
                    relations.append(Relation(
                        from_id=caller_id,
                        to_id=func_name,  # Will resolve to actual symbol ID later
                        relation_type="calls"
                    ))
            self._extract_calls(child, caller_id, relations)

    def _extract_inheritance(self, node, class_id, relations):
        """Extract inheritance relationships."""
        for child in node.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type == "identifier":
                        relations.append(Relation(
                            from_id=class_id,
                            to_id=arg.text.decode("utf-8"),
                            relation_type="extends"
                        ))

    def _extract_import(self, node, imports):
        """Extract import statements."""
        if node.type == "import_statement":
            for child in node.children:
                if child.type == "dotted_name":
                    imports.append(Import(
                        module=child.text.decode("utf-8"),
                        line=node.start_point[0] + 1
                    ))
        elif node.type == "import_from_statement":
            for child in node.children:
                if child.type == "dotted_name":
                    imports.append(Import(
                        module=child.text.decode("utf-8"),
                        line=node.start_point[0] + 1
                    ))

    def _extract_http_method(self, node):
        """Extract HTTP method from Flask/FastAPI decorators."""
        for child in node.children:
            if child.type == "decorator":
                decorator_text = child.text.decode("utf-8")
                if "methods=" in decorator_text:
                    if "'GET'" in decorator_text or '"GET"' in decorator_text:
                        return "GET"
                    elif "'POST'" in decorator_text or '"POST"' in decorator_text:
                        return "POST"
                elif "@app.route" in decorator_text or "@router." in decorator_text:
                    return "GET"  # Default
        return None

    def _extract_http_path(self, node):
        """Extract HTTP path from Flask/FastAPI decorators."""
        for child in node.children:
            if child.type == "decorator":
                decorator_text = child.text.decode("utf-8")
                if "route(" in decorator_text or ".get(" in decorator_text or ".post(" in decorator_text:
                    # Extract path string
                    start = decorator_text.find('"')
                    if start == -1:
                        start = decorator_text.find("'")
                    if start != -1:
                        end = decorator_text.find(decorator_text[start], start + 1)
                        if end != -1:
                            return decorator_text[start+1:end]
        return None
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_python_parser.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/parsers/python_parser.py tests/test_python_parser.py
git commit -m "feat: Python parser with Tree-sitter"
```

---

## Task 9: JavaScript/TypeScript Parser

**Files:**
- Create: `src/repo_intel/parsers/javascript_parser.py`
- Create: `tests/test_javascript_parser.py`

**Step 1: Write JavaScript parser tests**

```python
from repo_intel.parsers.javascript_parser import JavaScriptParser

def test_parse_function():
    code = """
function helloWorld() {
    console.log('hello');
}
"""
    parser = JavaScriptParser()
    result = parser.parse(code, "test_file")

    assert len(result.symbols) == 1
    assert result.symbols[0].name == "helloWorld"

def test_parse_class():
    code = """
class MyClass {
    method() {
        // ...
    }
}
"""
    parser = JavaScriptParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyClass" in symbols
    assert symbols["MyClass"].kind == "class"

def test_parse_arrow_function():
    code = """
const arrowFunc = () => {
    return 42;
};
"""
    parser = JavaScriptParser()
    result = parser.parse(code, "test_file")

    arrow_symbols = [s for s in result.symbols if s.name == "arrowFunc"]
    assert len(arrow_symbols) == 1

def test_parse_endpoint():
    code = """
app.get('/users', (req, res) => {
    res.json([]);
});
"""
    parser = JavaScriptParser()
    result = parser.parse(code, "test_file")

    endpoints = [s for s in result.symbols if s.kind == "endpoint"]
    assert len(endpoints) == 1
    assert endpoints[0].http_method == "GET"
    assert endpoints[0].path == "/users"
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_javascript_parser.py -v
```

Expected: FAIL

**Step 3: Implement JavaScript/TypeScript parser**

```python
from tree_sitter import Language, Parser
from repo_intel.parsers.base import Parser, ParseResult, Symbol, Import, Relation
import uuid

class JavaScriptParser(Parser):
    """JavaScript/TypeScript parser using Tree-sitter."""

    def __init__(self, language="javascript"):
        self.parser = Parser()
        if language == "typescript":
            self.language = Language("vendor/tree-sitter-typescript")
        else:
            self.language = Language("vendor/tree-sitter-javascript")
        self.parser.set_language(self.language)

    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse JavaScript/TypeScript code."""
        tree = self.parser.parse(bytes(content, "utf-8"))
        root_node = tree.root_node

        symbols = []
        imports = []
        relations = []

        self._traverse(root_node, content, file_id, symbols, imports, relations)

        return ParseResult(symbols=symbols, imports=imports, relations=relations)

    def _traverse(self, node, content, file_id, symbols, imports, relations):
        # Function declarations
        if node.type == "function_declaration":
            func_name = self._get_identifier(node)
            if func_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(Symbol(
                    id=symbol_id,
                    name=func_name,
                    kind="function",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    exported=False
                ))

        # Class declarations
        elif node.type == "class_declaration":
            class_name = self._get_identifier(node)
            if class_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(Symbol(
                    id=symbol_id,
                    name=class_name,
                    kind="class",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    exported=self._is_exported(node)
                ))

        # Variable declarations with arrow functions
        elif node.type == "variable_declaration":
            self._handle_variable_declaration(node, symbols)

        # Expressions (for Express-style endpoints)
        elif node.type == "expression_statement":
            self._handle_expression(node, symbols, relations)

        # Import statements
        elif node.type == "import_statement":
            self._extract_import(node, imports)

        # Recurse
        for child in node.children:
            self._traverse(child, content, file_id, symbols, imports, relations)

    def _get_identifier(self, node):
        """Extract identifier from node."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None

    def _is_exported(self, node):
        """Check if node is exported."""
        parent = node.parent
        if parent and parent.type == "export_statement":
            return True
        return False

    def _handle_variable_declaration(self, node, symbols):
        """Handle variable declarations (including arrow functions)."""
        for child in node.children:
            if child.type == "variable_declarator":
                name = self._get_identifier(child)
                if name:
                    # Check if it's a function
                    for subchild in child.children:
                        if subchild.type == "arrow_function":
                            symbols.append(Symbol(
                                id=str(uuid.uuid4()),
                                name=name,
                                kind="function",
                                start_line=node.start_point[0] + 1,
                                end_line=node.end_point[0] + 1,
                                exported=False
                            ))

    def _handle_expression(self, node, symbols, relations):
        """Handle expressions for HTTP endpoint detection."""
        text = node.text.decode("utf-8")

        # Express-style: app.get('/path', handler)
        if "app." in text or "router." in text:
            for child in node.children:
                if child.type == "call_expression":
                    method = self._extract_http_method(child)
                    path = self._extract_path(child)

                    if method and path:
                        symbols.append(Symbol(
                            id=str(uuid.uuid4()),
                            name=f"{method} {path}",
                            kind="endpoint",
                            start_line=node.start_point[0] + 1,
                            end_line=node.end_point[0] + 1,
                            exported=True,
                            http_method=method,
                            path=path
                        ))

    def _extract_http_method(self, node):
        """Extract HTTP method from call expression."""
        for child in node.children:
            if child.type == "member_expression":
                for subchild in child.children:
                    if subchild.type in ("property_identifier", "identifier"):
                        method = subchild.text.decode("utf-8").upper()
                        if method in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                            return method
        return None

    def _extract_path(self, node):
        """Extract path string from call expression."""
        for child in node.children:
            if child.type == "arguments":
                for arg in child.children:
                    if arg.type == "string":
                        return arg.text.decode("utf-8").strip('"').strip("'")
        return None

    def _extract_import(self, node, imports):
        """Extract import statements."""
        for child in node.children:
            if child.type == "string":
                imports.append(Import(
                    module=child.text.decode("utf-8").strip('"').strip("'"),
                    line=node.start_point[0] + 1
                ))
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_javascript_parser.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/parsers/javascript_parser.py tests/test_javascript_parser.py
git commit -m "feat: JavaScript/TypeScript parser"
```

---

## Task 10: Parser Factory

**Files:**
- Create: `src/repo_intel/parsers/factory.py`
- Create: `tests/test_parser_factory.py`

**Step 1: Write parser factory tests**

```python
from repo_intel.parsers.factory import get_parser

def test_get_python_parser():
    parser = get_parser("python")
    assert parser is not None
    assert hasattr(parser, 'parse')

def test_get_javascript_parser():
    parser = get_parser("javascript")
    assert parser is not None

def test_get_typescript_parser():
    parser = get_parser("typescript")
    assert parser is not None

def test_unsupported_language():
    parser = get_parser("cobol")
    assert parser is None
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_parser_factory.py -v
```

Expected: FAIL

**Step 3: Implement parser factory**

```python
from repo_intel.parsers.python_parser import PythonParser
from repo_intel.parsers.javascript_parser import JavaScriptParser

def get_parser(language: str):
    """Get parser instance for language."""
    parsers = {
        "python": PythonParser,
        "javascript": lambda: JavaScriptParser("javascript"),
        "typescript": lambda: JavaScriptParser("typescript"),
    }

    parser_class = parsers.get(language)
    if parser_class:
        return parser_class() if callable(parser_class) else parser_class

    return None
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_parser_factory.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/parsers/factory.py tests/test_parser_factory.py
git commit -m "feat: parser factory for language selection"
```

---

## Task 11: Core Indexer

**Files:**
- Create: `src/repo_intel/core/indexer.py`
- Create: `tests/test_indexer.py`

**Step 1: Write indexer tests**

```python
import pytest
from repo_intel.core.indexer import Indexer
from repo_intel.core.storage import Storage

@pytest.fixture
def temp_indexer(tmp_path):
    db_path = tmp_path / "test.db"
    return Indexer(str(db_path))

def test_index_file(temp_indexer, tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def hello():
    pass
""")

    temp_indexer.index_file(str(test_file), project="test")

    symbols = temp_indexer.storage.get_symbols()
    assert len(symbols) == 1
    assert symbols[0].name == "hello"

def test_index_project(temp_indexer, tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def func1(): pass")
    (tmp_path / "src" / "utils.py").write_text("def func2(): pass")

    temp_indexer.index_project(str(tmp_path), project="test")

    symbols = temp_indexer.storage.get_symbols()
    assert len(symbols) >= 2
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_indexer.py -v
```

Expected: FAIL

**Step 3: Implement core indexer**

```python
from pathlib import Path
from repo_intel.core.storage import Storage, FileEntry, SymbolEntry, Relation
from repo_intel.parsers.factory import get_parser
from repo_intel.utils.hashing import hash_file
from repo_intel.utils.language_detector import detect_language
from repo_intel.utils.file_walker import walk_project
import uuid

class Indexer:
    """Main indexing orchestration."""

    def __init__(self, db_path: str):
        self.storage = Storage(db_path)

    def index_file(self, file_path: str, project: str) -> bool:
        """Index a single file."""
        language = detect_language(file_path)
        if not language:
            return False

        parser = get_parser(language)
        if not parser:
            return False

        # Check if file changed
        file_entry = self.storage.get_file_by_path(file_path)
        current_hash = hash_file(file_path)

        if file_entry and file_entry.hash == current_hash:
            return False  # Skip unchanged files

        # Delete old symbols for this file
        if file_entry:
            self.storage.delete_symbols_by_file(file_entry.id)

        # Parse file
        with open(file_path) as f:
            content = f.read()

        parse_result = parser.parse(content, file_path)

        # Store file entry
        file_id = str(uuid.uuid4())
        file_entry = FileEntry(
            id=file_id,
            path=file_path,
            language=language,
            project=project,
            hash=current_hash
        )
        self.storage.insert_file(file_entry)

        # Store symbols
        for symbol in parse_result.symbols:
            entry = SymbolEntry(
                id=symbol.id,
                name=symbol.name,
                kind=symbol.kind,
                language=language,
                file_id=file_id,
                project=project,
                start_line=symbol.start_line,
                end_line=symbol.end_line,
                exported=symbol.exported,
                http_method=symbol.http_method,
                path=symbol.path
            )
            self.storage.insert_symbol(entry)

        # Store relations
        for relation in parse_result.relations:
            rel = Relation(
                id=str(uuid.uuid4()),
                from_symbol_id=relation.from_id,
                to_symbol_id=relation.to_id,
                relation_type=relation.relation_type
            )
            self.storage.insert_relation(rel)

        return True

    def index_project(self, project_root: str, project: str):
        """Index entire project."""
        files = walk_project(project_root)

        indexed = 0
        for file_path in files:
            if self.index_file(file_path, project):
                indexed += 1

        return indexed
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_indexer.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/indexer.py tests/test_indexer.py
git commit -m "feat: core indexing engine"
```

---

## Task 12: CLI - Entry Point

**Files:**
- Create: `src/repo_intel/cli.py`

**Step 1: Create CLI structure**

```python
import click
from pathlib import Path
from repo_intel.core.config import Config, get_config
from repo_intel.core.indexer import Indexer
from repo_intel.core.storage import Storage

@click.group()
def main():
    """repo-intel: Local-first structural intelligence for code repositories."""
    pass

@main.command()
@click.argument('path', type=click.Path(exists=True), default='.')
def init(path):
    """Initialize repo-intel in a repository."""
    config_dir = Path(path) / '.repo-intel'
    config_dir.mkdir(exist_ok=True)

    config_path = config_dir / 'config.json'
    if not config_path.exists():
        config = Config(project_root=str(Path(path).resolve()))
        import json
        with open(config_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)

    click.echo(f"Initialized repo-intel in {path}")

@main.command()
@click.option('--project', default='default', help='Project name')
def index(project):
    """Index the repository."""
    config = get_config()
    db_path = Path(config.project_root) / config.db_path

    indexer = Indexer(str(db_path))
    indexed = indexer.index_project(config.project_root, project)

    click.echo(f"Indexed {indexed} files")

@main.command()
def watch():
    """Watch for changes and reindex."""
    click.echo("Watch mode not yet implemented")

@main.command()
def stdio():
    """Start stdio protocol for tool integration."""
    click.echo("Stdio mode not yet implemented")

@main.command()
@click.argument('tool_name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def tool(tool_name, output_json):
    """Run a specific tool."""
    click.echo(f"Tool '{tool_name}' not yet implemented")

if __name__ == '__main__':
    main()
```

**Step 2: Test CLI**

```bash
python -m repo_intel.cli --help
```

Expected: Help output

**Step 3: Commit**

```bash
git add src/repo_intel/cli.py
git commit -m "feat: CLI entry point with init and index commands"
```

---

## Task 13: CLI Tools - list_symbols

**Files:**
- Create: `src/repo_intel/tools/list_symbols.py`
- Create: `tests/test_list_symbols.py`

**Step 1: Write list_symbols tests**

```python
from repo_intel.tools.list_symbols import list_symbols

def test_list_symbols(temp_indexer_with_data):
    result = list_symbols(temp_indexer_with_data.storage)
    assert len(result) > 0
    assert 'name' in result[0]
    assert 'kind' in result[0]

def test_list_symbols_filter_by_kind(temp_indexer_with_data):
    result = list_symbols(
        temp_indexer_with_data.storage,
        kind_filter='function'
    )
    for symbol in result:
        assert symbol['kind'] == 'function'
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_list_symbols.py -v
```

Expected: FAIL

**Step 3: Implement list_symbols tool**

```python
from typing import List, Dict
from repo_intel.core.storage import Storage

def list_symbols(storage: Storage, kind_filter: str | None = None) -> List[Dict]:
    """List all symbols, optionally filtered by kind."""
    symbols = storage.get_symbols()

    if kind_filter:
        symbols = [s for s in symbols if s.kind == kind_filter]

    return [
        {
            'id': s.id,
            'name': s.name,
            'kind': s.kind,
            'language': s.language,
            'file': s.file_id,
            'project': s.project,
            'start_line': s.start_line,
            'end_line': s.end_line,
            'exported': s.exported,
            'http_method': s.http_method,
            'path': s.path
        }
        for s in symbols
    ]
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_list_symbols.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/tools/list_symbols.py tests/test_list_symbols.py
git commit -m "feat: list_symbols tool"
```

---

## Task 14: CLI Tools - find_symbol

**Files:**
- Create: `src/repo_intel/tools/find_symbol.py`
- Create: `tests/test_find_symbol.py`

**Step 1: Write find_symbol tests**

```python
from repo_intel.tools.find_symbol import find_symbol

def test_find_symbol_by_name(temp_indexer_with_data):
    result = find_symbol(temp_indexer_with_data.storage, "hello")
    assert result is not None
    assert result['name'] == 'hello'

def test_find_symbol_not_found(temp_indexer_with_data):
    result = find_symbol(temp_indexer_with_data.storage, "nonexistent")
    assert result is None
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_find_symbol.py -v
```

Expected: FAIL

**Step 3: Implement find_symbol tool**

```python
from repo_intel.core.storage import Storage

def find_symbol(storage: Storage, name: str) -> dict | None:
    """Find a symbol by name."""
    symbols = storage.get_symbols()

    for symbol in symbols:
        if symbol.name == name:
            return {
                'id': symbol.id,
                'name': symbol.name,
                'kind': symbol.kind,
                'language': symbol.language,
                'file_id': symbol.file_id,
                'project': symbol.project,
                'start_line': symbol.start_line,
                'end_line': symbol.end_line,
                'exported': symbol.exported,
                'http_method': symbol.http_method,
                'path': symbol.path
            }

    return None
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_find_symbol.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/tools/find_symbol.py tests/test_find_symbol.py
git commit -m "feat: find_symbol tool"
```

---

## Task 15: CLI Tools - get_callers and get_callees

**Files:**
- Create: `src/repo_intel/tools/call_graph.py`
- Create: `tests/test_call_graph.py`

**Step 1: Write call graph tests**

```python
from repo_intel.tools.call_graph import get_callers, get_callees

def test_get_callers(temp_indexer_with_data):
    # Assuming 'callee' is called by 'caller'
    result = get_callers(temp_indexer_with_data.storage, "callee")
    assert len(result) >= 0

def test_get_callees(temp_indexer_with_data):
    # Assuming 'caller' calls 'callee'
    result = get_callees(temp_indexer_with_data.storage, "caller")
    assert len(result) >= 0
```

**Step 2: Run tests to verify failure**

```bash
pytest tests/test_call_graph.py -v
```

Expected: FAIL

**Step 3: Implement call graph tools**

```python
from typing import List
from repo_intel.core.storage import Storage

def get_callers(storage: Storage, symbol_name: str) -> List[dict]:
    """Get all symbols that call the given symbol."""
    relations = storage.get_relations()
    symbols = storage.get_symbols()

    # Find symbol ID
    symbol_id = None
    for symbol in symbols:
        if symbol.name == symbol_name:
            symbol_id = symbol.id
            break

    if not symbol_id:
        return []

    # Find callers
    caller_ids = [
        r.from_symbol_id for r in relations
        if r.to_symbol_id == symbol_id and r.relation_type == "calls"
    ]

    # Return caller symbols
    return [
        {
            'id': s.id,
            'name': s.name,
            'kind': s.kind,
            'file_id': s.file_id
        }
        for s in symbols
        if s.id in caller_ids
    ]

def get_callees(storage: Storage, symbol_name: str) -> List[dict]:
    """Get all symbols called by the given symbol."""
    relations = storage.get_relations()
    symbols = storage.get_symbols()

    # Find symbol ID
    symbol_id = None
    for symbol in symbols:
        if symbol.name == symbol_name:
            symbol_id = symbol.id
            break

    if not symbol_id:
        return []

    # Find callees
    callee_ids = [
        r.to_symbol_id for r in relations
        if r.from_symbol_id == symbol_id and r.relation_type == "calls"
    ]

    # Return callee symbols
    return [
        {
            'id': s.id,
            'name': s.name,
            'kind': s.kind,
            'file_id': s.file_id
        }
        for s in symbols
        if s.id in callee_ids
    ]
```

**Step 4: Run tests to verify pass**

```bash
pytest tests/test_call_graph.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/tools/call_graph.py tests/test_call_graph.py
git commit -m "feat: call graph tools (get_callers, get_callees)"
```

---

## Task 16: CLI Tool Integration

**Files:**
- Modify: `src/repo_intel/cli.py`

**Step 1: Update CLI to include tool commands**

```python
import json
from repo_intel.tools.list_symbols import list_symbols
from repo_intel.tools.find_symbol import find_symbol
from repo_intel.tools.call_graph import get_callers, get_callees

@main.command()
@click.argument('tool_name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def tool(tool_name, output_json):
    """Run a specific tool."""
    config = get_config()
    db_path = Path(config.project_root) / config.db_path
    storage = Storage(str(db_path))

    tools = {
        'list-symbols': lambda: list_symbols(storage),
        'find-symbol': lambda name: find_symbol(storage, name),
        'get-callers': lambda name: get_callers(storage, name),
        'get-callees': lambda name: get_callees(storage, name),
    }

    if tool_name not in tools:
        click.echo(f"Unknown tool: {tool_name}")
        return

    result = tools[tool_name]()

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(result)
```

**Step 2: Test CLI integration**

```bash
repo-intel tool list-symbols --json
```

Expected: JSON output

**Step 3: Commit**

```bash
git add src/repo_intel/cli.py
git commit -m "feat: integrate tools into CLI"
```

---

## Task 17: End-to-End Integration Test

**Files:**
- Create: `tests/test_e2e.py`

**Step 1: Write end-to-end test**

```python
import pytest
from pathlib import Path
from repo_intel.core.indexer import Indexer
from repo_intel.core.storage import Storage
from repo_intel.tools.list_symbols import list_symbols
from repo_intel.tools.find_symbol import find_symbol

def test_full_indexing_workflow(tmp_path):
    # Create test project
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("""
def greet(name):
    return f"Hello, {name}"

def main():
    greet("World")
""")

    # Index project
    db_path = tmp_path / "index.db"
    indexer = Indexer(str(db_path))
    indexed = indexer.index_project(str(tmp_path), project="test")

    assert indexed >= 1

    # Query symbols
    storage = Storage(str(db_path))
    symbols = list_symbols(storage)

    assert len(symbols) >= 2
    symbol_names = [s['name'] for s in symbols]
    assert 'greet' in symbol_names
    assert 'main' in symbol_names

    # Find specific symbol
    greet_symbol = find_symbol(storage, "greet")
    assert greet_symbol is not None
    assert greet_symbol['kind'] == 'function'
```

**Step 2: Run e2e test**

```bash
pytest tests/test_e2e.py -v
```

Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_e2e.py
git commit -m "test: end-to-end integration test"
```

---

## Task 18: Documentation and README Updates

**Files:**
- Modify: `README.md`
- Create: `ARCHITECTURE.md`

**Step 1: Update README with full usage**

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

## Quick Start

```bash
# In your project directory
cd /path/to/your/project
repo-intel init

# Index your code
repo-intel index --project myapp

# Query symbols
repo-intel tool list-symbols --json
repo-intel tool find-symbol myFunction --json

# Explore call graphs
repo-intel tool get-callers myFunction --json
repo-intel tool get-callees myFunction --json
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design details.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/
black src/
```
```

**Step 2: Create ARCHITECTURE.md**

```markdown
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
```

**Step 3: Commit**

```bash
git add README.md ARCHITECTURE.md
git commit -m "docs: complete README and architecture documentation"
```

---

## Task 19: Performance Benchmarks

**Files:**
- Create: `tests/benchmarks/test_indexing.py`

**Step 1: Create benchmark suite**

```python
import pytest
import time
from pathlib import Path
from repo_intel.core.indexer import Indexer

def test_indexing_performance_small(tmp_path):
    """Test indexing of small project (~100 LOC)."""
    # Create 10 Python files with ~10 LOC each
    for i in range(10):
        (tmp_path / f"file_{i}.py").write_text(f"""
def function_{i}():
    result = {i} * 2
    return result

def helper_{i}():
    function_{i}()
""")

    db_path = tmp_path / "bench.db"
    indexer = Indexer(str(db_path))

    start = time.time()
    indexed = indexer.index_project(str(tmp_path), project="bench")
    duration = time.time() - start

    assert indexed == 10
    assert duration < 2.0  # Should complete in under 2 seconds
```

**Step 2: Run benchmark**

```bash
pytest tests/benchmarks/test_indexing.py -v
```

Expected: PASS

**Step 3: Commit**

```bash
git add tests/benchmarks/test_indexing.py
git commit -m "test: add indexing performance benchmarks"
```

---

## Task 20: Final Polish and Release Prep

**Files:**
- Modify: `pyproject.toml`
- Create: `CHANGELOG.md`

**Step 1: Update pyproject.toml with version and metadata**

```toml
[project]
name = "repo-intel"
version = "0.1.0"
description = "Local-first structural intelligence for code repositories"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
]
```

**Step 2: Create CHANGELOG.md**

```markdown
# Changelog

## [0.1.0] - 2026-03-01

### Added
- Multi-language symbol indexing (Python, JavaScript, TypeScript)
- Call graph generation and querying
- Dependency tracking via import analysis
- Incremental reindexing with file hashing
- Monorepo project detection
- CLI with init, index, and tool commands
- SQLite-based storage
- Tree-sitter parser integration

### Tools
- list-symbols: List all indexed symbols
- find-symbol: Find symbol by name
- get-callers: Get callers of a function
- get-callees: Get functions called by a function
```

**Step 3: Run full test suite**

```bash
pytest tests/ -v
ruff check src/
black --check src/
```

Expected: All tests pass, no lint errors

**Step 4: Final commit**

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: prepare for v0.1.0 release"
git tag v0.1.0
```

---

## Summary

This plan builds repo-intel incrementally with TDD, covering:

1. **Project Foundation**: Python tooling setup
2. **Core Infrastructure**: Config, storage, hashing, file walking, language detection
3. **Parsers**: Base interface, Python, JavaScript/TypeScript parsers with Tree-sitter
4. **Indexer**: Main orchestration engine
5. **CLI**: Entry point with commands
6. **Tools**: Query interfaces for symbols and call graphs
7. **Testing**: Unit tests, integration tests, benchmarks
8. **Documentation**: README, architecture docs, changelog

Each task includes:
- Exact file paths
- Complete code implementations
- Test verification steps
- Commit instructions

**Estimated Timeline**: 20 tasks × 15-30 minutes = 5-10 hours of focused development.
