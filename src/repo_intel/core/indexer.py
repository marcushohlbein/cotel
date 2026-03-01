from pathlib import Path
from repo_intel.core.storage import Storage, FileEntry, SymbolEntry, Relation
from repo_intel.parsers.factory import get_parser
from repo_intel.parsers.base import Parser
from repo_intel.utils.hashing import hash_file
from repo_intel.utils.language_detector import detect_language
from repo_intel.utils.file_walker import walk_project
import click
import time
from dataclasses import dataclass
from typing import List, Tuple, Literal, Optional


IndexStatus = Literal["indexed", "skipped", "failed"]


@dataclass
class IndexResult:
    """Result of indexing operation."""

    total_files: int
    indexed: int
    skipped: int
    failed: int
    failed_files: List[str]
    total_symbols: int
    languages: dict
    duration: float

    @property
    def success_rate(self) -> float:
        if self.total_files == 0:
            return 100.0
        return (self.indexed / self.total_files) * 100


class Indexer:
    """Main indexing orchestration."""

    def __init__(self, db_path: str, verbose: bool = False):
        self.storage = Storage(db_path)
        self.verbose = verbose

    def index_file(
        self, file_path: str, project: str, commit: bool = True
    ) -> Tuple[IndexStatus, int, Optional[str]]:
        """Index a single file. Returns (status, symbol_count, error_msg)."""
        language = detect_language(file_path)
        if not language:
            return ("failed", 0, None)

        parser = get_parser(language)
        if not parser:
            return ("failed", 0, f"No parser for {language}")

        if self.verbose:
            click.echo(f"  → {file_path} ({language})")

        try:
            # Check if file changed
            file_entry = self.storage.get_file_by_path(file_path)
            current_hash = hash_file(file_path)

            if file_entry and file_entry.hash == current_hash:
                return ("skipped", 0, None)

            # Delete old symbols for this file
            if file_entry:
                self.storage.delete_symbols_by_file(file_entry.id)

            # Parse file
            with open(file_path) as f:
                content = f.read()

            parse_result = parser.parse(content, file_path)

            # Store file entry
            file_id = Parser.generate_id()
            file_entry = FileEntry(
                id=file_id,
                path=file_path,
                language=language,
                project=project,
                hash=current_hash,
            )
            self.storage.insert_file(file_entry, commit=commit)

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
                    path=symbol.path,
                )
                self.storage.insert_symbol(entry, commit=commit)

            # Store relations
            for relation in parse_result.relations:
                rel = Relation(
                    id=Parser.generate_id(),
                    from_symbol_id=relation.from_id,
                    to_symbol_id=relation.to_id,
                    relation_type=relation.relation_type,
                )
                self.storage.insert_relation(rel, commit=commit)

            return ("indexed", len(parse_result.symbols), None)

        except Exception as e:
            return ("failed", 0, str(e))

    def index_project(self, project_root: str, project: str, chunk_size: int = 50):
        """Index entire project with chunking and detailed results."""
        start_time = time.time()
        files = walk_project(project_root)
        total = len(files)

        click.echo(f"📊 Indexing {total} files...")

        indexed = 0
        skipped = 0
        failed = 0
        failed_files = []
        total_symbols = 0
        languages = {}

        for i, file_path in enumerate(files, 1):
            # Show chunk progress
            if i % chunk_size == 0 or i == total:
                chunk_num = (i - 1) // chunk_size + 1
                total_chunks = (total + chunk_size - 1) // chunk_size
                click.echo(f"  Processing chunk {chunk_num}/{total_chunks} [{i}/{total}]")

            # Determine if we should commit (at end of chunk or last file)
            is_chunk_end = (i % chunk_size == 0) or (i == total)

            # Index file (don't commit yet)
            status, symbol_count, error = self.index_file(file_path, project, commit=False)

            if status == "indexed":
                indexed += 1
                total_symbols += symbol_count
            elif status == "skipped":
                skipped += 1
            else:  # failed
                failed += 1
                failed_files.append(file_path)

            # Track languages
            if status in ("indexed", "skipped"):
                lang = detect_language(file_path)
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1

            # Commit at end of chunk
            if is_chunk_end:
                try:
                    self.storage.conn.commit()
                except Exception as e:
                    self.storage.conn.rollback()
                    # Mark remaining as failed
                    failed += total - i
                    break

        self.storage.set_last_index_time(time.time())

        duration = time.time() - start_time

        return IndexResult(
            total_files=total,
            indexed=indexed,
            skipped=skipped,
            failed=failed,
            failed_files=failed_files,
            total_symbols=total_symbols,
            languages=languages,
            duration=duration,
        )
