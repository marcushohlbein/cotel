import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import time


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
        # Ensure parent directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
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

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        self.conn.commit()

    def insert_file(self, file_entry: FileEntry):
        self.conn.execute(
            "INSERT OR REPLACE INTO files VALUES (?, ?, ?, ?, ?)",
            (
                file_entry.id,
                file_entry.path,
                file_entry.language,
                file_entry.project,
                file_entry.hash,
            ),
        )
        self.conn.commit()

    def insert_symbol(self, symbol: SymbolEntry):
        self.conn.execute(
            """INSERT OR REPLACE INTO symbols
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                symbol.id,
                symbol.name,
                symbol.kind,
                symbol.language,
                symbol.file_id,
                symbol.project,
                symbol.start_line,
                symbol.end_line,
                int(symbol.exported),
                symbol.http_method,
                symbol.path,
            ),
        )
        self.conn.commit()

    def insert_relation(self, relation: Relation):
        self.conn.execute(
            "INSERT OR REPLACE INTO relations VALUES (?, ?, ?, ?)",
            (relation.id, relation.from_symbol_id, relation.to_symbol_id, relation.relation_type),
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
        cursor = self.conn.execute("SELECT * FROM symbols WHERE file_id = ?", (file_id,))
        return [SymbolEntry(*row) for row in cursor.fetchall()]

    def delete_symbols_by_file(self, file_id: str):
        self.conn.execute("DELETE FROM symbols WHERE file_id = ?", (file_id,))
        self.conn.execute(
            "DELETE FROM relations WHERE from_symbol_id IN "
            "(SELECT id FROM symbols WHERE file_id = ?)",
            (file_id,),
        )
        self.conn.commit()

    def delete_file(self, file_id: str):
        self.conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        self.conn.commit()

    def count_files(self) -> int:
        cursor = self.conn.execute("SELECT COUNT(*) FROM files")
        return cursor.fetchone()[0]

    def get_last_index_time(self) -> float:
        cursor = self.conn.execute("SELECT value FROM metadata WHERE key = 'last_index_time'")
        row = cursor.fetchone()
        return float(row[0]) if row else 0.0

    def set_last_index_time(self, timestamp: float):
        self.conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            ("last_index_time", str(timestamp)),
        )
        self.conn.commit()

    def is_index_stale(self, project_root: str, max_age_seconds: int = 3600) -> bool:
        """Check if index is stale and needs reindexing."""
        from repo_intel.utils.file_walker import walk_project

        # Check 1: No index exists
        if self.count_files() == 0:
            return True

        # Check 2: Last index too old
        last_index = self.get_last_index_time()
        if time.time() - last_index > max_age_seconds:
            return True

        # Check 3: File count mismatch
        actual_files = len(walk_project(project_root))
        db_files = self.count_files()
        if abs(actual_files - db_files) > 5:  # Allow small variance
            return True

        return False
