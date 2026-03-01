from repo_intel.core.storage import Storage


def find_symbol(storage: Storage, name: str) -> dict | None:
    """Find a symbol by name."""
    symbols = storage.get_symbols()

    for symbol in symbols:
        if symbol.name == name:
            return {
                "id": symbol.id,
                "name": symbol.name,
                "kind": symbol.kind,
                "language": symbol.language,
                "file_id": symbol.file_id,
                "project": symbol.project,
                "start_line": symbol.start_line,
                "end_line": symbol.end_line,
                "exported": symbol.exported,
                "http_method": symbol.http_method,
                "path": symbol.path,
            }

    return None
