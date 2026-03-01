from typing import List
from repo_intel.core.storage import Storage


def _symbol_summary(s) -> dict:
    """Convert SymbolEntry to summary dictionary."""
    return {"id": s.id, "name": s.name, "kind": s.kind, "file_id": s.file_id}


def _get_related_symbols(storage: Storage, symbol_name: str, direction: "from" | "to") -> List[dict]:
    """Get symbols related by calls relation in the specified direction."""
    symbol = storage.get_symbol_by_name(symbol_name)
    if not symbol:
        return []

    symbol_id = symbol.id
    relations = storage.get_relations_by_from(symbol_id, "calls") if direction == "from" else storage.get_relations_by_to(symbol_id, "calls")

    related_ids = [r.to_symbol_id if direction == "from" else r.from_symbol_id for r in relations]

    if not related_ids:
        return []

    # Get related symbols in one query using IN clause
    placeholders = ",".join("?" * len(related_ids))
    cursor = storage.conn.execute(f"SELECT * FROM symbols WHERE id IN ({placeholders})", related_ids)
    from repo_intel.core.storage import SymbolEntry
    return [_symbol_summary(SymbolEntry(*row)) for row in cursor.fetchall()]


def get_callers(storage: Storage, symbol_name: str) -> List[dict]:
    """Get all symbols that call the given symbol."""
    return _get_related_symbols(storage, symbol_name, "to")


def get_callees(storage: Storage, symbol_name: str) -> List[dict]:
    """Get all symbols called by the given symbol."""
    return _get_related_symbols(storage, symbol_name, "from")
