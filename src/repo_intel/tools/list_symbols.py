from typing import List, Dict
from repo_intel.core.storage import Storage


def _symbol_to_dict(s) -> Dict:
    """Convert SymbolEntry to dictionary."""
    return {
        "id": s.id,
        "name": s.name,
        "kind": s.kind,
        "language": s.language,
        "file_id": s.file_id,
        "project": s.project,
        "start_line": s.start_line,
        "end_line": s.end_line,
        "exported": s.exported,
        "http_method": s.http_method,
        "path": s.path,
    }


def list_symbols(storage: Storage, kind_filter: str | None = None) -> List[Dict]:
    """List all symbols, optionally filtered by kind."""
    symbols = storage.get_symbols_by_kind(kind_filter) if kind_filter else storage.get_symbols()
    return [_symbol_to_dict(s) for s in symbols]
