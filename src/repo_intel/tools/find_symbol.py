from repo_intel.core.storage import Storage
from repo_intel.tools.list_symbols import _symbol_to_dict


def find_symbol(storage: Storage, name: str) -> dict | None:
    """Find a symbol by name."""
    symbol = storage.get_symbol_by_name(name)
    return _symbol_to_dict(symbol) if symbol else None
