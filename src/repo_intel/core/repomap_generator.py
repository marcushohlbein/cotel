from typing import Dict, List, Set, Tuple
from pathlib import Path

from .pagerank import PageRankScorer
from .token_optimizer import TokenOptimizer
from .context_detector import ContextDetector
from .storage import Storage
from ..formatters.toon_formatter import TOONFormatter


class RepoMapGenerator:
    """Orchestrate repomap generation"""

    def __init__(self, storage: Storage, repo_root: str):
        self.storage = storage
        self.repo_root = repo_root
        self.pagerank = PageRankScorer()
        self.optimizer = TokenOptimizer()
        self.context_detector = ContextDetector()
        self.toon_formatter = TOONFormatter()

    def generate(self, max_tokens: int = 1024, output_format: str = "toon") -> str:
        """
        Generate repomap.

        Args:
            max_tokens: Maximum token budget
            output_format: 'toon' or 'json'

        Returns:
            Formatted repomap string
        """
        # 1. Detect context
        modified_files, mentioned_idents = self.context_detector.detect_context(self.repo_root)

        # 2. Load definitions and references from storage
        definitions = self._load_definitions()
        references = self._load_references()

        # 3. Rank symbols using PageRank
        ranked_symbols = self.pagerank.rank_symbols(
            definitions, references, modified_files, mentioned_idents
        )

        # 4. Optimize for token budget
        formatter = (
            self._format_symbols_toon if output_format == "toon" else self._format_symbols_json
        )

        optimized_map, tokens_used = self.optimizer.optimize(
            ranked_symbols, formatter, max_tokens=max_tokens
        )

        # 5. Format final output
        if output_format == "toon":
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
            FROM "references" r
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
            cursor = self.storage.conn.execute(
                """
                SELECT s.name, s.kind, f.path, s.start_line, s.end_line, s.signature
                FROM symbols s
                JOIN files f ON s.file_id = f.id
                WHERE s.name = ? AND f.path = ?
            """,
                (symbol_name, file_path),
            )

            row = cursor.fetchone()
            if row:
                symbol_data.append(
                    {
                        "name": row[0],
                        "kind": row[1],
                        "file": row[2],
                        "start_line": row[3],
                        "end_line": row[4],
                        "signature": row[5] or "",
                    }
                )

        # Get file data
        file_data = self._get_file_summary()

        # Format as TOON
        metadata = {
            "project": Path(self.repo_root).name,
            "tokens_used": 0,  # Will be updated by optimizer
        }

        return self.toon_formatter.format(symbol_data, file_data, metadata)

    def _format_symbols_json(self, symbols: List[Tuple[str, str, float]]) -> str:
        """Format symbols for JSON output"""
        import json

        symbol_list = []
        for file_path, symbol_name, score in symbols:
            cursor = self.storage.conn.execute(
                """
                SELECT s.name, s.kind, f.path, s.start_line, s.end_line, s.signature
                FROM symbols s
                JOIN files f ON s.file_id = f.id
                WHERE s.name = ? AND f.path = ?
            """,
                (symbol_name, file_path),
            )

            row = cursor.fetchone()
            if row:
                symbol_list.append(
                    {
                        "name": row[0],
                        "kind": row[1],
                        "file": row[2],
                        "start_line": row[3],
                        "end_line": row[4],
                        "signature": row[5] or "",
                        "score": score,
                    }
                )

        return json.dumps({"project": Path(self.repo_root).name, "symbols": symbol_list}, indent=2)

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
            files.append({"path": row[0], "symbol_count": row[1], "language": row[2] or "unknown"})

        return files
