import os
from pathlib import Path
from typing import List, Set

IGNORED_DIRS = {
    ".git",
    ".svn",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".repo-intel",
}

PROJECT_MARKERS = [
    "package.json",
    "pom.xml",
    "build.gradle",
    "Cargo.toml",
    "go.mod",
    "composer.json",
    "requirements.txt",
    "pyproject.toml",
]


def walk_project(root: str) -> List[str]:
    """Walk project directory and return source files."""
    files = []
    root_path = Path(root)

    for file_path in root_path.rglob("*"):
        if file_path.is_file():
            relative = file_path.relative_to(root_path)
            parts = relative.parts

            # Skip ignored directories
            if any(part in IGNORED_DIRS for part in parts):
                continue

            files.append(str(file_path))

    return files


def find_project_roots(root: str) -> List[str]:
    """Find monorepo subprojects by marker files."""
    projects = []
    root_path = Path(root)

    for item in root_path.iterdir():
        if item.is_dir():
            for marker in PROJECT_MARKERS:
                if (item / marker).exists():
                    projects.append(str(item))
                    break

    return projects
