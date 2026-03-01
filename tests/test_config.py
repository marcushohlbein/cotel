from repo_intel.core.config import Config, get_config


def test_config_defaults():
    config = Config()
    assert config.db_path == ".repo-intel/index.db"
    assert config.project_root is not None


def test_config_from_dict():
    config = Config.from_dict({"db_path": "custom.db"})
    assert config.db_path == "custom.db"


def test_get_config_creates_default():
    config = get_config()
    assert isinstance(config, Config)
