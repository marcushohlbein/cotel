import pytest
from repo_intel.core.storage import Storage, SymbolEntry, FileEntry, Relation


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


@pytest.fixture
def storage(db_path):
    return Storage(str(db_path))


def test_storage_initialization(storage):
    assert storage.conn is not None


def test_insert_file(storage):
    file_entry = FileEntry(
        id="f1", path="/test.py", language="python", project="test", hash="abc123"
    )
    storage.insert_file(file_entry)
    files = storage.get_files()
    assert len(files) == 1
    assert files[0].path == "/test.py"


def test_insert_symbol(storage):
    symbol = SymbolEntry(
        id="s1",
        name="test_func",
        kind="function",
        language="python",
        file_id="f1",
        project="test",
        start_line=1,
        end_line=5,
        exported=True,
    )
    storage.insert_symbol(symbol)
    symbols = storage.get_symbols()
    assert len(symbols) == 1
    assert symbols[0].name == "test_func"


def test_insert_relation(storage):
    relation = Relation(id="r1", from_symbol_id="s1", to_symbol_id="s2", relation_type="calls")
    storage.insert_relation(relation)
    relations = storage.get_relations()
    assert len(relations) == 1
    assert relations[0].relation_type == "calls"
