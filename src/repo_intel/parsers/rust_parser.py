from tree_sitter import Parser as TSParser, Language
import tree_sitter_rust
from repo_intel.parsers.base import Parser, ParseResult, Symbol, Relation
import uuid


class RustParser(Parser):
    """Rust language parser using Tree-sitter."""

    def __init__(self):
        self.language = Language(tree_sitter_rust.language())
        self.parser = TSParser(self.language)

    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse Rust code and extract symbols."""
        tree = self.parser.parse(bytes(content, "utf-8"))
        root_node = tree.root_node

        symbols = []
        relations = []

        self._in_impl = False
        self._traverse(root_node, content, file_id, symbols, relations)

        return ParseResult(symbols=symbols, relations=relations)

    def _traverse(self, node, content, file_id, symbols, relations):
        # Handle function definitions
        if node.type == "function_item":
            func_name = self._get_identifier(node)
            if func_name:
                symbol_id = str(uuid.uuid4())
                kind = "method" if self._in_impl else "function"

                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=func_name,
                        kind=kind,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=self._is_public(node),
                        http_method=None,
                        path=None,
                    )
                )

                self._extract_calls(node, symbol_id, relations)

        # Handle struct definitions
        elif node.type == "struct_item":
            struct_name = self._get_type_identifier(node)
            if struct_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=struct_name,
                        kind="class",
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=self._is_public(node),
                    )
                )

        # Handle impl blocks
        elif node.type == "impl_item":
            old_in_impl = self._in_impl
            self._in_impl = True

            for child in node.children:
                self._traverse(child, content, file_id, symbols, relations)

            self._in_impl = old_in_impl
            return

        # Handle trait definitions
        elif node.type == "trait_item":
            trait_name = self._get_type_identifier(node)
            if trait_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=trait_name,
                        kind="interface",
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=self._is_public(node),
                    )
                )


        for child in node.children:
            self._traverse(child, content, file_id, symbols, relations)

    def _get_identifier(self, node):
        """Extract identifier from node."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None

    def _get_type_identifier(self, node):
        """Extract type_identifier from node."""
        for child in node.children:
            if child.type == "type_identifier":
                return child.text.decode("utf-8")
        return None

    def _is_public(self, node):
        """Check if item is public (has 'pub' keyword)."""
        for child in node.children:
            if child.type == "visibility_modifier":
                return True
        return False

    def _extract_calls(self, node, caller_id, relations):
        """Extract function calls from function body."""
        for child in node.children:
            if child.type == "call_expression":
                func_name = self._get_function_call_name(child)
                if func_name:
                    relations.append(
                        Relation(from_id=caller_id, to_id=func_name, relation_type="calls")
                    )
            self._extract_calls(child, caller_id, relations)

    def _get_function_call_name(self, node):
        """Extract function name from call expression."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
            # Handle method calls like object.method()
            elif child.type == "field_expression":
                for subchild in child.children:
                    if subchild.type == "field_identifier":
                        return subchild.text.decode("utf-8")
        return None

