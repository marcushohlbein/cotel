from typing import List, Dict
from repo_intel.core.storage import Storage


def list_symbols(storage: Storage, kind_filter: str | None = None) -> List[Dict]:
    """List all symbols, optionally filtered by kind."""
    symbols = storage.get_symbols()

    if kind_filter:
        symbols = [s for s in symbols if s.kind == kind_filter]

    return [
        {
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
        for s in symbols
    ]
