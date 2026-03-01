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
