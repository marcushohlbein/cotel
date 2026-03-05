import subprocess
from pathlib import Path
from typing import Set, Tuple
import re


class ContextDetector:
    """Auto-detect relevant context from git"""

    def detect_context(self, repo_root: str) -> Tuple[Set[str], Set[str]]:
        """
        Detect relevant files and identifiers from git status.

        Returns:
            Tuple of (modified_files, mentioned_identifiers)
        """
        modified_files = set()
        mentioned_idents = set()

        try:
            # Get modified files
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                modified_files = {f for f in files if f}

            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                modified_files.update(f for f in files if f)

            # Extract identifiers from diff
            result = subprocess.run(
                ["git", "diff", "--unified=0"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                mentioned_idents = self._extract_identifiers(result.stdout)

        except (subprocess.SubprocessError, FileNotFoundError):
            # Git not available or not a git repo
            pass

        return modified_files, mentioned_idents

    def _extract_identifiers(self, diff: str) -> Set[str]:
        """Extract potential identifiers from diff"""
        identifiers = set()

        # Look for function/class definitions being added/modified
        patterns = [
            r"^\+.*def\s+(\w+)",  # Python def
            r"^\+.*function\s+(\w+)",  # JS function
            r"^\+.*class\s+(\w+)",  # class definition
            r"^\+.*interface\s+(\w+)",  # interface
        ]

        for pattern in patterns:
            matches = re.findall(pattern, diff, re.MULTILINE)
            identifiers.update(matches)

        return identifiers
