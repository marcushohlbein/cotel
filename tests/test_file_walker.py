from repo_intel.utils.file_walker import walk_project, find_project_roots


def test_walk_project(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# test")
    (tmp_path / ".git").mkdir()

    files = list(walk_project(str(tmp_path)))
    # Only Python files are returned (not README.md)
    assert len(files) == 1
    assert any(f.endswith("main.py") for f in files)
    # README.md is now filtered out
    assert not any(f.endswith("README.md") for f in files)
    # .git is still filtered
    assert not any(".git" in f for f in files)


def test_find_project_roots(tmp_path):
    (tmp_path / "frontend").mkdir()
    (tmp_path / "backend").mkdir()
    (tmp_path / "frontend" / "package.json").write_text("{}")
    (tmp_path / "backend" / "pom.xml").write_text("<project></project>")

    roots = find_project_roots(str(tmp_path))
    assert len(roots) == 2
