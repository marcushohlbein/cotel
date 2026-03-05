def test_repomap_generator_exists():
    """Test that RepoMapGenerator class exists"""
    from repo_intel.core.repomap_generator import RepoMapGenerator
    from repo_intel.core.storage import Storage

    storage = Storage(":memory:")
    generator = RepoMapGenerator(storage, "/tmp")
    assert hasattr(generator, "generate")
