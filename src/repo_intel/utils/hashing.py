import hashlib
from pathlib import Path


def hash_file(file_path: str) -> str:
    """Generate SHA-256 hash of file contents."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def file_changed(file_path: str, stored_hash: str) -> bool:
    """Check if file has changed based on hash."""
    current_hash = hash_file(file_path)
    return current_hash != stored_hash
