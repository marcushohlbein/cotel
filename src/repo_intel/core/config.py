from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json


@dataclass
class Config:
    db_path: str = ".repo-intel/index.db"
    project_root: Optional[str] = None
    incremental_enabled: bool = True
    watch_enabled: bool = False

    def __post_init__(self):
        if self.project_root is None:
            self.project_root = str(Path.cwd())

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        return cls(**data)

    def to_dict(self) -> dict:
        return {
            "db_path": self.db_path,
            "project_root": self.project_root,
            "incremental_enabled": self.incremental_enabled,
            "watch_enabled": self.watch_enabled,
        }


def get_config() -> Config:
    config_path = Path.cwd() / ".repo-intel" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)
            return Config.from_dict(data)
    return Config()
