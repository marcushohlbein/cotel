# Repomap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform repo-intel into standalone repomap tool with TOON output, PageRank scoring, and auto-context detection.

**Architecture:** Extend existing repo-intel infrastructure by adding reference tracking, PageRank scorer, token optimizer, and TOON formatter. Rename package from repo-intel to repomap.

**Tech Stack:** Python 3.14, tree-sitter, NetworkX, SQLite, Click, TOON format

---

## Phase 1: Database Schema Extension

### Task 1: Add references table to schema

**Files:**
- Modify: `src/repo_intel/core/storage.py:45-80`
- Test: `tests/test_storage.py`

**Step 1: Write the failing test**

```python
# tests/test_storage.py

def test_references_table_exists():
    """Test that references table is created"""
    storage = Storage(":memory:")
    
    # Check references table exists
    cursor = storage.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='references'"
    )
    result = cursor.fetchone()
    assert result is not None, "references table should exist"
    
    # Check columns
    cursor = storage.conn.execute("PRAGMA table_info(references)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    assert "id" in columns
    assert "symbol_id" in columns
    assert "file_id" in columns
    assert "line_number" in columns
    assert "context_snippet" in columns
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_storage.py::test_references_table_exists -v`
Expected: FAIL with "references table should exist"

**Step 3: Add references table to schema**

```python
# src/repo_intel/core/storage.py

# In __init__ method, after creating symbols table:
self.conn.execute("""
    CREATE TABLE IF NOT EXISTS references (
        id TEXT PRIMARY KEY,
        symbol_id TEXT NOT NULL,
        file_id TEXT NOT NULL,
        line_number INTEGER NOT NULL,
        context_snippet TEXT,
        FOREIGN KEY (symbol_id) REFERENCES symbols(id),
        FOREIGN KEY (file_id) REFERENCES files(id)
    )
""")

# Create index for faster lookups
self.conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_references_symbol 
    ON references(symbol_id)
""")

self.conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_references_file 
    ON references(file_id)
""")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_storage.py::test_references_table_exists -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/storage.py tests/test_storage.py
git commit -m "feat(storage): add references table for symbol usage tracking"
```

---

### Task 2: Add signature column to symbols table

**Files:**
- Modify: `src/repo_intel/core/storage.py:30-45`
- Test: `tests/test_storage.py`

**Step 1: Write the failing test**

```python
# tests/test_storage.py

def test_symbols_table_has_signature():
    """Test that symbols table has signature column"""
    storage = Storage(":memory:")
    
    cursor = storage.conn.execute("PRAGMA table_info(symbols)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    assert "signature" in columns, "symbols table should have signature column"
    assert columns["signature"] == "TEXT"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_storage.py::test_symbols_table_has_signature -v`
Expected: FAIL with "symbols table should have signature column"

**Step 3: Add signature column to schema**

```python
# src/repo_intel/core/storage.py

# In CREATE TABLE symbols:
CREATE TABLE IF NOT EXISTS symbols (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    language TEXT NOT NULL,
    file_id TEXT NOT NULL,
    project TEXT,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    exported INTEGER DEFAULT 0,
    http_method TEXT,
    path TEXT,
    signature TEXT,  -- NEW: function/class signature
    FOREIGN KEY (file_id) REFERENCES files(id)
)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_storage.py::test_symbols_table_has_signature -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/storage.py tests/test_storage.py
git commit -m "feat(storage): add signature column to symbols table"
```

---

## Phase 2: Reference Extraction

### Task 3: Add reference extraction to base parser

**Files:**
- Modify: `src/repo_intel/parsers/base.py:80-120`
- Test: `tests/test_parser_base.py`

**Step 1: Write the failing test**

```python
# tests/test_parser_base.py

def test_base_parser_extract_references():
    """Test that base parser has extract_references method"""
    from repo_intel.parsers.base import BaseParser
    
    parser = BaseParser()
    
    # Should have method
    assert hasattr(parser, 'extract_references')
    
    # Should return list
    code = "def foo(): pass\nbar()"
    refs = parser.extract_references(code)
    assert isinstance(refs, list)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_parser_base.py::test_base_parser_extract_references -v`
Expected: FAIL with "has no attribute 'extract_references'"

**Step 3: Add extract_references to base parser**

```python
# src/repo_intel/parsers/base.py

class BaseParser(ABC):
    # ... existing methods ...
    
    def extract_references(self, source_code: str) -> List[Dict]:
        """
        Extract symbol references from source code.
        
        Returns list of dicts with:
        - name: symbol name being referenced
        - line: line number
        - context: surrounding code snippet (optional)
        
        Default implementation returns empty list.
        Override in language-specific parsers.
        """
        return []
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_parser_base.py::test_base_parser_extract_references -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/parsers/base.py tests/test_parser_base.py
git commit -m "feat(parsers): add extract_references method to base parser"
```

---

### Task 4: Implement reference extraction for Python parser

**Files:**
- Modify: `src/repo_intel/parsers/python_parser.py:150-200`
- Test: `tests/test_python_parser.py`

**Step 1: Write the failing test**

```python
# tests/test_python_parser.py

def test_python_parser_extract_references():
    """Test Python parser extracts function calls"""
    from repo_intel.parsers.python_parser import PythonParser
    
    parser = PythonParser()
    code = """
def foo():
    bar()
    baz(1, 2)
    obj.method()
"""
    
    refs = parser.extract_references(code)
    
    # Should find bar, baz, obj.method
    ref_names = [r['name'] for r in refs]
    
    assert 'bar' in ref_names
    assert 'baz' in ref_names
    # Method calls might be 'obj.method' or just 'method'
    assert any('method' in name for name in ref_names)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_python_parser.py::test_python_parser_extract_references -v`
Expected: FAIL with "assert 'bar' in ref_names"

**Step 3: Implement reference extraction using tree-sitter**

```python
# src/repo_intel/parsers/python_parser.py

def extract_references(self, source_code: str) -> List[Dict]:
    """Extract function/method calls from Python code"""
    tree = self.parser.parse(bytes(source_code, "utf8"))
    
    references = []
    
    # Query for call expressions
    query = self.language.query("""
        (call
          function: (identifier) @func_name)
        (call
          function: (attribute
            attribute: (identifier) @method_name))
    """)
    
    captures = query.captures(tree.root_node)
    
    for node, tag in captures:
        if tag in ('func_name', 'method_name'):
            name = node.text.decode('utf8')
            line = node.start_point[0]
            
            references.append({
                'name': name,
                'line': line,
                'context': None  # Could extract surrounding lines
            })
    
    return references
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_python_parser.py::test_python_parser_extract_references -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/parsers/python_parser.py tests/test_python_parser.py
git commit -m "feat(python): implement reference extraction for Python"
```

---

### Task 5: Update indexer to store references

**Files:**
- Modify: `src/repo_intel/core/indexer.py:200-250`
- Test: `tests/test_indexer.py`

**Step 1: Write the failing test**

```python
# tests/test_indexer.py

def test_indexer_stores_references():
    """Test that indexer stores symbol references"""
    import tempfile
    from repo_intel.core.indexer import Indexer
    from repo_intel.core.storage import Storage
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
def foo():
    bar()
    baz()
""")
        
        # Index
        storage = Storage(Path(tmpdir) / ".repo-intel" / "index.db")
        indexer = Indexer(storage, tmpdir)
        indexer.index_file(str(test_file))
        
        # Check references were stored
        cursor = storage.conn.execute("SELECT COUNT(*) FROM references")
        count = cursor.fetchone()[0]
        
        assert count > 0, "Should have stored references"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_indexer.py::test_indexer_stores_references -v`
Expected: FAIL with "Should have stored references"

**Step 3: Update indexer to extract and store references**

```python
# src/repo_intel/core/indexer.py

def index_file(self, file_path: str) -> None:
    """Index a single file"""
    # ... existing symbol extraction code ...
    
    # NEW: Extract references
    references = parser.extract_references(content)
    
    # Store references
    for ref in references:
        ref_id = self._generate_id(f"{file_path}:{ref['name']}:{ref['line']}")
        
        # Find symbol_id for this reference
        # (symbol that's being referenced, not the file it's in)
        symbol = self._find_symbol_by_name(ref['name'])
        
        if symbol:
            self.storage.conn.execute("""
                INSERT OR REPLACE INTO references 
                (id, symbol_id, file_id, line_number, context_snippet)
                VALUES (?, ?, ?, ?, ?)
            """, (
                ref_id,
                symbol['id'],
                file_id,
                ref['line'],
                ref.get('context')
            ))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_indexer.py::test_indexer_stores_references -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/indexer.py tests/test_indexer.py
git commit -m "feat(indexer): store symbol references during indexing"
```

---

## Phase 3: PageRank Scoring

### Task 6: Create PageRank scorer module

**Files:**
- Create: `src/repo_intel/core/pagerank.py`
- Test: `tests/test_pagerank.py`

**Step 1: Write the failing test**

```python
# tests/test_pagerank.py

def test_pagerank_scorer_exists():
    """Test that PageRankScorer class exists"""
    from repo_intel.core.pagerank import PageRankScorer
    
    scorer = PageRankScorer()
    assert hasattr(scorer, 'rank_symbols')
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_pagerank.py::test_pagerank_scorer_exists -v`
Expected: FAIL with "cannot import name 'PageRankScorer'"

**Step 3: Create PageRankScorer class**

```python
# src/repo_intel/core/pagerank.py

import math
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
import networkx as nx


class PageRankScorer:
    """Rank symbols by importance using PageRank algorithm"""
    
    def rank_symbols(
        self,
        definitions: Dict[str, Set[str]],
        references: Dict[str, List[str]],
        chat_files: Set[str],
        mentioned_idents: Set[str]
    ) -> List[Tuple[str, str, float]]:
        """
        Rank symbols using PageRank.
        
        Args:
            definitions: symbol_name -> set of files where defined
            references: symbol_name -> list of files where referenced
            chat_files: files currently being worked on
            mentioned_idents: identifiers mentioned in conversation
        
        Returns:
            List of (file, symbol, score) tuples, sorted by score descending
        """
        # Build graph
        G = nx.MultiDiGraph()
        
        # Add edges based on references
        for symbol, ref_files in references.items():
            definers = definitions.get(symbol, set())
            
            if not definers:
                continue
            
            # Calculate weight multiplier
            weight = self._calculate_weight(symbol, mentioned_idents, definers)
            
            for ref_file in ref_files:
                for def_file in definers:
                    # Edge from referencing file to defining file
                    G.add_edge(
                        ref_file, 
                        def_file, 
                        weight=weight,
                        symbol=symbol
                    )
        
        # Personalization: boost chat files
        personalization = {}
        if chat_files:
            for f in chat_files:
                personalization[f] = 1.0 / len(chat_files)
        
        # Run PageRank
        try:
            if personalization:
                ranked = nx.pagerank(
                    G, 
                    weight='weight',
                    personalization=personalization,
                    dangling=personalization
                )
            else:
                ranked = nx.pagerank(G, weight='weight')
        except:
            # Fallback if graph is empty
            return []
        
        # Convert to symbol rankings
        symbol_scores = []
        for symbol, definers in definitions.items():
            for def_file in definers:
                score = ranked.get(def_file, 0)
                symbol_scores.append((def_file, symbol, score))
        
        # Sort by score descending
        symbol_scores.sort(key=lambda x: x[2], reverse=True)
        
        return symbol_scores
    
    def _calculate_weight(
        self,
        symbol: str,
        mentioned_idents: Set[str],
        definers: Set[str]
    ) -> float:
        """Calculate edge weight multiplier"""
        weight = 1.0
        
        # Boost mentioned identifiers
        if symbol in mentioned_idents:
            weight *= 10.0
        
        # Boost meaningful names
        is_snake = '_' in symbol and any(c.isalpha() for c in symbol)
        is_kebab = '-' in symbol and any(c.isalpha() for c in symbol)
        is_camel = any(c.isupper() for c in symbol) and any(c.islower() for c in symbol)
        
        if (is_snake or is_kebab or is_camel) and len(symbol) >= 8:
            weight *= 10.0
        
        # Penalize private symbols
        if symbol.startswith('_'):
            weight *= 0.1
        
        # Penalize common names
        if len(definers) > 5:
            weight *= 0.1
        
        return weight
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_pagerank.py::test_pagerank_scorer_exists -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/pagerank.py tests/test_pagerank.py
git commit -m "feat(pagerank): implement PageRank symbol scoring"
```

---

### Task 7: Test PageRank with sample data

**Files:**
- Test: `tests/test_pagerank.py`

**Step 1: Write integration test**

```python
# tests/test_pagerank.py

def test_pagerank_ranks_symbols():
    """Test that PageRank correctly ranks symbols"""
    from repo_intel.core.pagerank import PageRankScorer
    
    scorer = PageRankScorer()
    
    # Sample data
    definitions = {
        'foo': {'a.py'},
        'bar': {'b.py'},
        'baz': {'c.py'}
    }
    
    references = {
        'foo': ['b.py', 'c.py'],  # foo is referenced by b and c
        'bar': ['c.py'],           # bar is referenced by c
        'baz': []                  # baz is not referenced
    }
    
    chat_files = {'a.py'}  # Working on a.py
    mentioned_idents = set()
    
    ranked = scorer.rank_symbols(
        definitions, references, chat_files, mentioned_idents
    )
    
    # Should return list of (file, symbol, score)
    assert len(ranked) == 3
    assert all(isinstance(item, tuple) for item in ranked)
    assert all(len(item) == 3 for item in ranked)
    
    # foo should be ranked higher than baz (more references)
    foo_score = next(s for f, s, sc in ranked if s == 'foo')
    baz_score = next(s for f, s, sc in ranked if s == 'baz')
    
    # Actually we want the score, not the symbol
    foo_entry = next((f, s, sc) for f, s, sc in ranked if s == 'foo')
    baz_entry = next((f, s, sc) for f, s, sc in ranked if s == 'baz')
    
    assert foo_entry[2] > baz_entry[2], "foo should rank higher than baz"
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_pagerank.py::test_pagerank_ranks_symbols -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_pagerank.py
git commit -m "test(pagerank): add integration test for symbol ranking"
```

---

## Phase 4: Token Optimization

### Task 8: Create token optimizer module

**Files:**
- Create: `src/repo_intel/core/token_optimizer.py`
- Test: `tests/test_token_optimizer.py`

**Step 1: Write the failing test**

```python
# tests/test_token_optimizer.py

def test_token_optimizer_exists():
    """Test that TokenOptimizer class exists"""
    from repo_intel.core.token_optimizer import TokenOptimizer
    
    optimizer = TokenOptimizer()
    assert hasattr(optimizer, 'optimize')
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_token_optimizer.py::test_token_optimizer_exists -v`
Expected: FAIL with "cannot import name 'TokenOptimizer'"

**Step 3: Create TokenOptimizer class**

```python
# src/repo_intel/core/token_optimizer.py

from typing import List, Tuple, Callable


class TokenOptimizer:
    """Optimize repomap to fit within token budget using binary search"""
    
    def optimize(
        self,
        ranked_symbols: List[Tuple[str, str, float]],
        formatter: Callable,
        max_tokens: int = 1024,
        token_counter: Callable[[str], int] = None
    ) -> Tuple[str, int]:
        """
        Binary search to find optimal number of symbols.
        
        Args:
            ranked_symbols: List of (file, symbol, score) sorted by score
            formatter: Function to format symbols into string
            max_tokens: Maximum token budget
            token_counter: Function to count tokens (default: simple word count)
        
        Returns:
            Tuple of (formatted_map, actual_token_count)
        """
        if token_counter is None:
            token_counter = self._simple_token_count
        
        if not ranked_symbols:
            return "", 0
        
        lower = 0
        upper = len(ranked_symbols)
        best_map = ""
        best_tokens = 0
        
        while lower <= upper:
            middle = (lower + upper) // 2
            
            # Format subset of symbols
            candidate_symbols = ranked_symbols[:middle]
            candidate_map = formatter(candidate_symbols)
            
            # Count tokens
            tokens = token_counter(candidate_map)
            
            # Check if within budget
            if tokens <= max_tokens:
                # This is valid, try to include more
                if tokens > best_tokens:
                    best_map = candidate_map
                    best_tokens = tokens
                lower = middle + 1
            else:
                # Over budget, reduce
                upper = middle - 1
        
        return best_map, best_tokens
    
    def _simple_token_count(self, text: str) -> int:
        """Simple token count (words)"""
        return len(text.split())
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_token_optimizer.py::test_token_optimizer_exists -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/token_optimizer.py tests/test_token_optimizer.py
git commit -m "feat(optimizer): implement token budget optimization"
```

---

### Task 9: Test token optimizer with sample data

**Files:**
- Test: `tests/test_token_optimizer.py`

**Step 1: Write integration test**

```python
# tests/test_token_optimizer.py

def test_token_optimizer_fits_budget():
    """Test that optimizer fits within token budget"""
    from repo_intel.core.token_optimizer import TokenOptimizer
    
    optimizer = TokenOptimizer()
    
    # Sample ranked symbols
    symbols = [
        ('a.py', 'foo', 0.9),
        ('b.py', 'bar', 0.8),
        ('c.py', 'baz', 0.7),
        ('d.py', 'qux', 0.6),
        ('e.py', 'quux', 0.5)
    ]
    
    # Simple formatter
    def formatter(syms):
        return '\n'.join(f"{f}:{s}" for f, s, _ in syms)
    
    # Optimize with small budget
    result, tokens = optimizer.optimize(
        symbols, 
        formatter, 
        max_tokens=3  # Only 3 words allowed
    )
    
    # Should fit within budget
    assert tokens <= 3
    
    # Should include highest-ranked symbols
    assert 'foo' in result
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_token_optimizer.py::test_token_optimizer_fits_budget -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_token_optimizer.py
git commit -m "test(optimizer): add integration test for token budget"
```

---

## Phase 5: Context Detection

### Task 10: Create context detector module

**Files:**
- Create: `src/repo_intel/core/context_detector.py`
- Test: `tests/test_context_detector.py`

**Step 1: Write the failing test**

```python
# tests/test_context_detector.py

def test_context_detector_exists():
    """Test that ContextDetector class exists"""
    from repo_intel.core.context_detector import ContextDetector
    
    detector = ContextDetector()
    assert hasattr(detector, 'detect_context')
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_context_detector.py::test_context_detector_exists -v`
Expected: FAIL with "cannot import name 'ContextDetector'"

**Step 3: Create ContextDetector class**

```python
# src/repo_intel/core/context_detector.py

import subprocess
from pathlib import Path
from typing import Set, Tuple
import re


class ContextDetector:
    """Auto-detect relevant context from git"""
    
    def detect_context(self, repo_root: str) -> Tuple[Set[str], Set[str]]:
        """
        Detect relevant files and identifiers from git status.
        
        Returns:
            Tuple of (modified_files, mentioned_identifiers)
        """
        modified_files = set()
        mentioned_idents = set()
        
        try:
            # Get modified files
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                modified_files = {f for f in files if f}
            
            # Get staged files
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                modified_files.update(f for f in files if f)
            
            # Extract identifiers from diff
            result = subprocess.run(
                ['git', 'diff', '--unified=0'],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                mentioned_idents = self._extract_identifiers(result.stdout)
        
        except (subprocess.SubprocessError, FileNotFoundError):
            # Git not available or not a git repo
            pass
        
        return modified_files, mentioned_idents
    
    def _extract_identifiers(self, diff: str) -> Set[str]:
        """Extract potential identifiers from diff"""
        identifiers = set()
        
        # Look for function/class definitions being added/modified
        patterns = [
            r'^\+.*def\s+(\w+)',      # Python def
            r'^\+.*function\s+(\w+)',  # JS function
            r'^\+.*class\s+(\w+)',     # class definition
            r'^\+.*interface\s+(\w+)', # interface
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.MULTILINE)
            identifiers.update(matches)
        
        return identifiers
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_context_detector.py::test_context_detector_exists -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/context_detector.py tests/test_context_detector.py
git commit -m "feat(context): implement git-based context detection"
```

---

## Phase 6: TOON Formatter

### Task 11: Create TOON formatter module

**Files:**
- Create: `src/repo_intel/formatters/toon_formatter.py`
- Test: `tests/test_toon_formatter.py`

**Step 1: Write the failing test**

```python
# tests/test_toon_formatter.py

def test_toon_formatter_exists():
    """Test that TOONFormatter class exists"""
    from repo_intel.formatters.toon_formatter import TOONFormatter
    
    formatter = TOONFormatter()
    assert hasattr(formatter, 'format')
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_toon_formatter.py::test_toon_formatter_exists -v`
Expected: FAIL with "cannot import name 'TOONFormatter'"

**Step 3: Create TOONFormatter class**

```python
# src/repo_intel/formatters/toon_formatter.py

from typing import List, Tuple, Dict


class TOONFormatter:
    """Format repomap as TOON (Token-Oriented Object Notation)"""
    
    def format(
        self,
        symbols: List[Dict],
        files: List[Dict],
        metadata: Dict
    ) -> str:
        """
        Format repomap data as TOON.
        
        Args:
            symbols: List of symbol dicts
            files: List of file dicts
            metadata: Repo metadata (project, tokens_used, etc.)
        
        Returns:
            TOON formatted string
        """
        lines = []
        
        # Metadata section
        lines.append("repo_map{")
        for key, value in metadata.items():
            lines.append(f"  {key}: {self._format_value(value)}")
        lines.append("}")
        
        # Symbols section (tabular array)
        if symbols:
            lines.append("")
            lines.append(f"symbols[{len(symbols)}]{{name,kind,file,start_line,end_line,signature}}:")
            for sym in symbols:
                row = ','.join([
                    sym.get('name', ''),
                    sym.get('kind', ''),
                    sym.get('file', ''),
                    str(sym.get('start_line', 0)),
                    str(sym.get('end_line', 0)),
                    self._escape_csv(sym.get('signature', ''))
                ])
                lines.append(f"  {row}")
        
        # Files section (tabular array)
        if files:
            lines.append("")
            lines.append(f"files[{len(files)}]{{path,symbol_count,language}}:")
            for f in files:
                row = ','.join([
                    f.get('path', ''),
                    str(f.get('symbol_count', 0)),
                    f.get('language', '')
                ])
                lines.append(f"  {row}")
        
        return '\n'.join(lines) + '\n'
    
    def _format_value(self, value) -> str:
        """Format a value for TOON"""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        else:
            return str(value)
    
    def _escape_csv(self, value: str) -> str:
        """Escape value for CSV-style field"""
        if ',' in value or '"' in value or '\n' in value:
            escaped = value.replace('"', '""')
            return f'"{escaped}"'
        return value
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_toon_formatter.py::test_toon_formatter_exists -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/formatters/toon_formatter.py tests/test_toon_formatter.py
git commit -m "feat(formatter): implement TOON output format"
```

---

### Task 12: Test TOON formatter output

**Files:**
- Test: `tests/test_toon_formatter.py`

**Step 1: Write integration test**

```python
# tests/test_toon_formatter.py

def test_toon_formatter_output():
    """Test that TOON formatter produces valid output"""
    from repo_intel.formatters.toon_formatter import TOONFormatter
    
    formatter = TOONFormatter()
    
    symbols = [
        {
            'name': 'foo',
            'kind': 'function',
            'file': 'a.py',
            'start_line': 10,
            'end_line': 20,
            'signature': 'def foo(x, y)'
        },
        {
            'name': 'Bar',
            'kind': 'class',
            'file': 'b.py',
            'start_line': 5,
            'end_line': 30,
            'signature': 'class Bar:'
        }
    ]
    
    files = [
        {'path': 'a.py', 'symbol_count': 5, 'language': 'python'},
        {'path': 'b.py', 'symbol_count': 3, 'language': 'python'}
    ]
    
    metadata = {
        'project': 'test',
        'tokens_used': 50
    }
    
    output = formatter.format(symbols, files, metadata)
    
    # Check structure
    assert 'repo_map{' in output
    assert 'symbols[2]' in output
    assert 'files[2]' in output
    
    # Check content
    assert 'foo' in output
    assert 'Bar' in output
    assert 'a.py' in output
    assert 'b.py' in output
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_toon_formatter.py::test_toon_formatter_output -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_toon_formatter.py
git commit -m "test(formatter): add integration test for TOON output"
```

---

## Phase 7: Repomap Generator

### Task 13: Create repomap generator orchestrator

**Files:**
- Create: `src/repo_intel/core/repomap_generator.py`
- Test: `tests/test_repomap_generator.py`

**Step 1: Write the failing test**

```python
# tests/test_repomap_generator.py

def test_repomap_generator_exists():
    """Test that RepoMapGenerator class exists"""
    from repo_intel.core.repomap_generator import RepoMapGenerator
    
    generator = RepoMapGenerator()
    assert hasattr(generator, 'generate')
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_repomap_generator.py::test_repomap_generator_exists -v`
Expected: FAIL with "cannot import name 'RepoMapGenerator'"

**Step 3: Create RepoMapGenerator class**

```python
# src/repo_intel/core/repomap_generator.py

from typing import Dict, List, Set, Tuple
from pathlib import Path

from .pagerank import PageRankScorer
from .token_optimizer import TokenOptimizer
from .context_detector import ContextDetector
from .storage import Storage
from ..formatters.toon_formatter import TOONFormatter
from ..formatters.json_formatter import JSONFormatter


class RepoMapGenerator:
    """Orchestrate repomap generation"""
    
    def __init__(self, storage: Storage, repo_root: str):
        self.storage = storage
        self.repo_root = repo_root
        self.pagerank = PageRankScorer()
        self.optimizer = TokenOptimizer()
        self.context_detector = ContextDetector()
        self.toon_formatter = TOONFormatter()
        self.json_formatter = JSONFormatter()
    
    def generate(
        self,
        max_tokens: int = 1024,
        output_format: str = 'toon'
    ) -> str:
        """
        Generate repomap.
        
        Args:
            max_tokens: Maximum token budget
            output_format: 'toon' or 'json'
        
        Returns:
            Formatted repomap string
        """
        # 1. Detect context
        modified_files, mentioned_idents = self.context_detector.detect_context(
            self.repo_root
        )
        
        # 2. Load definitions and references from storage
        definitions = self._load_definitions()
        references = self._load_references()
        
        # 3. Rank symbols using PageRank
        ranked_symbols = self.pagerank.rank_symbols(
            definitions,
            references,
            modified_files,
            mentioned_idents
        )
        
        # 4. Optimize for token budget
        formatter = (
            self._format_symbols_toon if output_format == 'toon'
            else self._format_symbols_json
        )
        
        optimized_map, tokens_used = self.optimizer.optimize(
            ranked_symbols,
            formatter,
            max_tokens=max_tokens
        )
        
        # 5. Format final output
        if output_format == 'toon':
            return optimized_map
        else:
            return optimized_map
    
    def _load_definitions(self) -> Dict[str, Set[str]]:
        """Load symbol definitions from storage"""
        definitions = {}
        
        cursor = self.storage.conn.execute("""
            SELECT s.name, f.path
            FROM symbols s
            JOIN files f ON s.file_id = f.id
        """)
        
        for row in cursor:
            symbol_name, file_path = row
            if symbol_name not in definitions:
                definitions[symbol_name] = set()
            definitions[symbol_name].add(file_path)
        
        return definitions
    
    def _load_references(self) -> Dict[str, List[str]]:
        """Load symbol references from storage"""
        references = {}
        
        cursor = self.storage.conn.execute("""
            SELECT s.name, f.path
            FROM references r
            JOIN symbols s ON r.symbol_id = s.id
            JOIN files f ON r.file_id = f.id
        """)
        
        for row in cursor:
            symbol_name, file_path = row
            if symbol_name not in references:
                references[symbol_name] = []
            references[symbol_name].append(file_path)
        
        return references
    
    def _format_symbols_toon(self, symbols: List[Tuple[str, str, float]]) -> str:
        """Format symbols for TOON output"""
        # Load full symbol data
        symbol_data = []
        for file_path, symbol_name, score in symbols:
            cursor = self.storage.conn.execute("""
                SELECT s.name, s.kind, f.path, s.start_line, s.end_line, s.signature
                FROM symbols s
                JOIN files f ON s.file_id = f.id
                WHERE s.name = ? AND f.path = ?
            """, (symbol_name, file_path))
            
            row = cursor.fetchone()
            if row:
                symbol_data.append({
                    'name': row[0],
                    'kind': row[1],
                    'file': row[2],
                    'start_line': row[3],
                    'end_line': row[4],
                    'signature': row[5] or ''
                })
        
        # Get file data
        file_data = self._get_file_summary()
        
        # Format as TOON
        metadata = {
            'project': Path(self.repo_root).name,
            'tokens_used': 0  # Will be updated by optimizer
        }
        
        return self.toon_formatter.format(symbol_data, file_data, metadata)
    
    def _format_symbols_json(self, symbols: List[Tuple[str, str, float]]) -> str:
        """Format symbols for JSON output"""
        # Similar to TOON but returns JSON
        # Implementation similar to above
        pass
    
    def _get_file_summary(self) -> List[Dict]:
        """Get file summary data"""
        cursor = self.storage.conn.execute("""
            SELECT f.path, COUNT(s.id) as symbol_count, f.language
            FROM files f
            LEFT JOIN symbols s ON s.file_id = f.id
            GROUP BY f.id
        """)
        
        files = []
        for row in cursor:
            files.append({
                'path': row[0],
                'symbol_count': row[1],
                'language': row[2] or 'unknown'
            })
        
        return files
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_repomap_generator.py::test_repomap_generator_exists -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/core/repomap_generator.py tests/test_repomap_generator.py
git commit -m "feat(generator): implement repomap generation orchestrator"
```

---

## Phase 8: CLI Refactoring

### Task 14: Refactor CLI for hybrid structure

**Files:**
- Modify: `src/repo_intel/cli.py`
- Test: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
# tests/test_cli.py

def test_cli_default_command():
    """Test that CLI has default repomap command"""
    from click.testing import CliRunner
    from repo_intel.cli import cli
    
    runner = CliRunner()
    
    # Should have default command
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'repomap' in result.output.lower() or 'generate' in result.output.lower()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_cli_default_command -v`
Expected: FAIL (current CLI doesn't have default command)

**Step 3: Refactor CLI to hybrid structure**

```python
# src/repo_intel/cli.py

import click
from pathlib import Path

from .core.storage import Storage
from .core.repomap_generator import RepoMapGenerator
from .core.indexer import Indexer


@click.group(invoke_without_command=True)
@click.option('--max-tokens', default=1024, help='Maximum token budget')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON instead of TOON')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, max_tokens, output_json, verbose):
    """
    Generate repository map for AI coding assistants.
    
    Default action: Generate repomap (auto-indexes if needed)
    
    Subcommands: list, find, callers, callees, index
    """
    ctx.ensure_object(dict)
    ctx.obj['max_tokens'] = max_tokens
    ctx.obj['output_json'] = output_json
    ctx.obj['verbose'] = verbose
    
    if ctx.invoked_subcommand is None:
        # Default: generate repomap
        return _generate_repomap(ctx)


def _generate_repomap(ctx):
    """Generate repomap"""
    repo_root = Path.cwd()
    db_path = repo_root / '.repo-intel' / 'index.db'
    
    # Auto-index if needed
    if not db_path.exists():
        if ctx.obj['verbose']:
            click.echo("Indexing repository...")
        storage = Storage(str(db_path))
        indexer = Indexer(storage, str(repo_root))
        indexer.index_all()
    else:
        storage = Storage(str(db_path))
    
    # Generate repomap
    generator = RepoMapGenerator(storage, str(repo_root))
    
    output_format = 'json' if ctx.obj['output_json'] else 'toon'
    repomap = generator.generate(
        max_tokens=ctx.obj['max_tokens'],
        output_format=output_format
    )
    
    click.echo(repomap)


@cli.command('list')
@click.option('--type', 'symbol_type', help='Filter by symbol type (function, class, method, etc.)')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def list_symbols(ctx, symbol_type, output_json):
    """List all symbols"""
    # Implementation from existing repo-intel
    pass


@cli.command('find')
@click.option('--name', required=True, help='Symbol name to find')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def find_symbol(ctx, name, output_json):
    """Find a specific symbol"""
    # Implementation from existing repo-intel
    pass


@cli.command('callers')
@click.option('--name', required=True, help='Symbol name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def get_callers(ctx, name, output_json):
    """Get callers of a symbol"""
    # Implementation from existing repo-intel
    pass


@cli.command('callees')
@click.option('--name', required=True, help='Symbol name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def get_callees(ctx, name, output_json):
    """Get callees of a symbol"""
    # Implementation from existing repo-intel
    pass


@cli.command('index')
@click.option('--verbose', '-v', is_flag=True, help='Show progress')
@click.pass_context
def index_repo(ctx, verbose):
    """Index repository (usually auto-handled)"""
    # Implementation from existing repo-intel
    pass


if __name__ == '__main__':
    cli()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_cli_default_command -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/repo_intel/cli.py tests/test_cli.py
git commit -m "feat(cli): refactor to hybrid structure with default repomap command"
```

---

## Phase 9: Package Rename

### Task 15: Update package name from repo-intel to repomap

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `src/repo_intel/__init__.py`

**Step 1: Update pyproject.toml**

```toml
# pyproject.toml

[project]
name = "repomap"
version = "0.2.0"
description = "Token-efficient repository maps for AI coding assistants"
# ... rest of metadata

[project.scripts]
repomap = "repo_intel.cli:cli"  # Keep module name, change binary name
```

**Step 2: Update README.md**

```markdown
# repomap

Token-efficient repository maps for AI coding assistants.

## Installation

pip install repomap

## Usage

repomap                    # Generate TOON repomap
repomap --max-tokens 2048  # Adjust token budget
repomap --json            # JSON output
```

**Step 3: Update imports if needed**

Keep module as `repo_intel` internally (avoid breaking changes), just rename package/binary.

**Step 4: Test installation**

```bash
pip install -e .
repomap --help
```

**Step 5: Commit**

```bash
git add pyproject.toml README.md
git commit -m "refactor: rename package from repo-intel to repomap"
```

---

## Phase 10: Integration Testing

### Task 16: End-to-end test

**Files:**
- Test: `tests/test_e2e_repomap.py`

**Step 1: Write comprehensive E2E test**

```python
# tests/test_e2e_repomap.py

def test_e2e_repomap_generation():
    """Test complete repomap generation workflow"""
    import tempfile
    from pathlib import Path
    from click.testing import CliRunner
    from repo_intel.cli import cli
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample Python project
        repo = Path(tmpdir)
        
        (repo / 'main.py').write_text("""
from utils import helper

def main():
    helper()
    print("done")

if __name__ == '__main__':
    main()
""")
        
        (repo / 'utils.py').write_text("""
def helper():
    return "helping"
""")
        
        # Initialize git repo
        import subprocess
        subprocess.run(['git', 'init'], cwd=tmpdir, check=True)
        subprocess.run(['git', 'add', '.'], cwd=tmpdir, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmpdir, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmpdir, check=True)
        subprocess.run(['git', 'commit', '-m', 'init'], cwd=tmpdir, check=True)
        
        # Run repomap
        runner = CliRunner()
        result = runner.invoke(cli, ['--max-tokens', '500'], cwd=tmpdir)
        
        # Should succeed
        assert result.exit_code == 0
        
        # Should contain TOON format
        assert 'repo_map{' in result.output
        assert 'symbols[' in result.output
        
        # Should contain our functions
        assert 'main' in result.output or 'helper' in result.output
```

**Step 2: Run test**

Run: `pytest tests/test_e2e_repomap.py::test_e2e_repomap_generation -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_e2e_repomap.py
git commit -m "test(e2e): add comprehensive end-to-end test"
```

---

## Phase 11: Documentation

### Task 17: Update documentation

**Files:**
- Update: `README.md`
- Update: `QUICKSTART.md`
- Create: `docs/repomap-guide.md`

**Step 1: Update README with repomap examples**

**Step 2: Create repomap usage guide**

**Step 3: Update skill documentation**

**Step 4: Commit**

```bash
git add README.md QUICKSTART.md docs/
git commit -m "docs: update documentation for repomap"
```

---

## Success Criteria

After all tasks complete:

- [ ] `repomap` command generates TOON output
- [ ] PageRank ranks modified files higher
- [ ] Token optimization fits within budget
- [ ] Auto-context detection works from git
- [ ] All existing repo-intel commands still work
- [ ] Performance < 1s for typical repos
- [ ] Tests pass: `pytest tests/ -v`

---

**Plan complete! Ready for execution.**
