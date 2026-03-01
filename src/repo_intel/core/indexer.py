from pathlib import Path
from repo_intel.core.storage import Storage, FileEntry, SymbolEntry, Relation
from repo_intel.parsers.factory import get_parser
from repo_intel.utils.hashing import hash_file
from repo_intel.utils.language_detector import detect_language
from repo_intel.utils.file_walker import walk_project
import uuid
import click


class Indexer:
    """Main indexing orchestration."""

    def __init__(self, db_path: str, verbose: bool = False):
        self.storage = Storage(db_path)
        self.verbose = verbose

    def index_file(self, file_path: str, project: str) -> bool:
        """Index a single file."""
        language = detect_language(file_path)
        if not language:
            return False

        parser = get_parser(language)
        if not parser:
            return False

        if self.verbose:
            print(f"  → {file_path} ({language})")

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
            id=file_id, path=file_path, language=language, project=project, hash=current_hash
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
                path=symbol.path,
            )
            self.storage.insert_symbol(entry)

        # Store relations
        for relation in parse_result.relations:
            rel = Relation(
                id=str(uuid.uuid4()),
                from_symbol_id=relation.from_id,
                to_symbol_id=relation.to_id,
                relation_type=relation.relation_type,
            )
            self.storage.insert_relation(rel)

        return True

    def index_project(self, project_root: str, project: str, verbose: bool = False):
        """Index entire project."""
        files = walk_project(project_root)
        total = len(files)

        if verbose:
            print(f"Indexing {total} files...")

        indexed = 0
        for i, file_path in enumerate(files, 1):
            if verbose or (i % 10 == 0):
                # Show progress every 10 files or in verbose mode
                progress = f"[{i}/{total}] " if not verbose else ""
                click.echo(f"{progress}{file_path}")

            if self.index_file(file_path, project):
                indexed += 1

        return indexed
