"""Base parser interface and data classes."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import uuid


@dataclass
class Symbol:
    id: str
    name: str
    kind: str
    start_line: int
    end_line: int
    exported: bool
    http_method: str | None = None
    path: str | None = None


@dataclass
class Relation:
    from_id: str
    to_id: str
    relation_type: str


@dataclass
class ParseResult:
    symbols: List[Symbol]
    relations: List[Relation]


class Parser(ABC):
    """Base parser interface for all language parsers."""

    @abstractmethod
    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse file content and extract symbols and relations."""
        pass

    @staticmethod
    def generate_id() -> str:
        """Generate a unique symbol ID."""
        return str(uuid.uuid4())
