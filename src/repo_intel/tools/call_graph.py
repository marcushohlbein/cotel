from typing import List
from repo_intel.core.storage import Storage


def get_callers(storage: Storage, symbol_name: str) -> List[dict]:
    """Get all symbols that call the given symbol."""
    relations = storage.get_relations()
    symbols = storage.get_symbols()

    # Find symbol ID
    symbol_id = None
    for symbol in symbols:
        if symbol.name == symbol_name:
            symbol_id = symbol.id
            break

    if not symbol_id:
        return []

    # Find callers
    caller_ids = [
        r.from_symbol_id
        for r in relations
        if r.to_symbol_id == symbol_id and r.relation_type == "calls"
    ]

    # Return caller symbols
    return [
        {"id": s.id, "name": s.name, "kind": s.kind, "file_id": s.file_id}
        for s in symbols
        if s.id in caller_ids
    ]


def get_callees(storage: Storage, symbol_name: str) -> List[dict]:
    """Get all symbols called by the given symbol."""
    relations = storage.get_relations()
    symbols = storage.get_symbols()

    # Find symbol ID
    symbol_id = None
    for symbol in symbols:
        if symbol.name == symbol_name:
            symbol_id = symbol.id
            break

    if not symbol_id:
        return []

    # Find callees
    callee_ids = [
        r.to_symbol_id
        for r in relations
        if r.from_symbol_id == symbol_id and r.relation_type == "calls"
    ]

    # Return callee symbols
    return [
        {"id": s.id, "name": s.name, "kind": s.kind, "file_id": s.file_id}
        for s in symbols
        if s.id in callee_ids
    ]
