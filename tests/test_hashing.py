from repo_intel.utils.hashing import hash_file, file_changed


def test_hash_file(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')")
    h1 = hash_file(str(test_file))
    h2 = hash_file(str(test_file))
    assert h1 == h2
    assert len(h1) == 64  # SHA-256


def test_file_change_detection(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("v1")
    h1 = hash_file(str(test_file))
    test_file.write_text("v2")
    h2 = hash_file(str(test_file))
    assert h1 != h2
