from tree_sitter import Parser as TSParser, Language
import tree_sitter_php
from repo_intel.parsers.base import Parser, ParseResult, Symbol, Import, Relation
import uuid


class PHPParser(Parser):
    """PHP language parser using Tree-sitter."""

    def __init__(self):
        self.language = Language(tree_sitter_php.language_php())
        self.parser = TSParser(self.language)

    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse PHP code and extract symbols."""
        tree = self.parser.parse(bytes(content, "utf-8"))
        root_node = tree.root_node

        symbols = []
        imports = []
        relations = []

        self._in_class = False
        self._traverse(root_node, content, file_id, symbols, imports, relations)

        return ParseResult(symbols=symbols, imports=imports, relations=relations)

    def _traverse(self, node, content, file_id, symbols, imports, relations):
        # Handle function definitions
        if node.type == "function_definition":
            func_name = self._get_name_from_node(node)
            if func_name:
                symbol_id = str(uuid.uuid4())
                kind = "method" if self._in_class else "function"

                # Check for HTTP endpoints (common patterns in Laravel, Symfony)
                http_method, http_path = self._extract_http_info(node)

                if http_method:
                    kind = "endpoint"

                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=func_name,
                        kind=kind,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=False,
                        http_method=http_method,
                        path=http_path,
                    )
                )

                # Extract function calls
                self._extract_calls(node, symbol_id, relations)

        # Handle class definitions
        elif node.type == "class_declaration":
            class_name = self._get_child_name(node, "name")
            if class_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=class_name,
                        kind="class",
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=False,
                    )
                )

                # Check for inheritance
                self._extract_inheritance(node, symbol_id, relations)

                # Mark that we're inside a class
                old_in_class = self._in_class
                self._in_class = True

                # Recurse into class body
                for child in node.children:
                    self._traverse(child, content, file_id, symbols, imports, relations)

                self._in_class = old_in_class
                return

        # Handle interface declarations
        elif node.type == "interface_declaration":
            interface_name = self._get_child_name(node, "name")
            if interface_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=interface_name,
                        kind="interface",
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=False,
                    )
                )

        # Handle use statements
        elif node.type == "use_statement":
            self._extract_import(node, imports)

        # Recurse into children
        for child in node.children:
            self._traverse(child, content, file_id, symbols, imports, relations)

    def _get_name_from_node(self, node):
        """Extract name from node by checking for name child."""
        for child in node.children:
            if child.type == "name":
                if child.is_named:
                    return child.text.decode("utf-8")
        return None

    def _get_child_name(self, node, child_type):
        """Extract name from child node by type."""
        for child in node.children:
            if child.type == child_type:
                return child.text.decode("utf-8")
        return None

    def _extract_calls(self, node, caller_id, relations):
        """Extract function calls from function body."""
        for child in node.children:
            if child.type == "function_call_expression":
                func_name = self._get_function_call_name(child)
                if func_name:
                    relations.append(
                        Relation(from_id=caller_id, to_id=func_name, relation_type="calls")
                    )
            self._extract_calls(child, caller_id, relations)

    def _get_function_call_name(self, node):
        """Extract function name from call expression."""
        for child in node.children:
            if child.type == "name":
                for subchild in child.children:
                    if subchild.type == "identifier":
                        return subchild.text.decode("utf-8")
        return None

    def _extract_inheritance(self, node, class_id, relations):
        """Extract inheritance relationships."""
        for child in node.children:
            if child.type == "extends_clause":
                for subchild in child.children:
                    if subchild.type == "name":
                        for name_elem in subchild.children:
                            if name_elem.type == "identifier":
                                relations.append(
                                    Relation(
                                        from_id=class_id,
                                        to_id=name_elem.text.decode("utf-8"),
                                        relation_type="extends",
                                    )
                                )
            elif child.type == "implements_clause":
                for subchild in child.children:
                    if subchild.type == "name":
                        for name_elem in subchild.children:
                            if name_elem.type == "identifier":
                                relations.append(
                                    Relation(
                                        from_id=class_id,
                                        to_id=name_elem.text.decode("utf-8"),
                                        relation_type="implements",
                                    )
                                )

    def _extract_import(self, node, imports):
        """Extract use statements."""
        for child in node.children:
            if child.type == "namespace_name":
                imports.append(
                    Import(module=child.text.decode("utf-8"), line=node.start_point[0] + 1)
                )
                break

    def _extract_http_info(self, node):
        """Extract HTTP method and path from PHP function patterns."""
        func_name = self._get_child_name(node, "name")
        if not func_name:
            return None, None

        # Laravel patterns: getUser, postUser, etc.
        # Common HTTP methods
        if func_name.startswith("get") or func_name.startswith("index"):
            return "GET", self._extract_path_from_name(func_name, "get")
        elif func_name.startswith("post") or func_name.startswith("store"):
            return "POST", self._extract_path_from_name(func_name, "post")
        elif func_name.startswith("put") or func_name.startswith("update"):
            return "PUT", self._extract_path_from_name(func_name, "put")
        elif func_name.startswith("delete") or func_name.startswith("destroy"):
            return "DELETE", self._extract_path_from_name(func_name, "delete")

        return None, None

    def _extract_path_from_name(self, func_name, prefix):
        """Extract path from function name (Laravel conventions)."""
        # Remove the HTTP method prefix
        if func_name.startswith(prefix):
            remaining = func_name[len(prefix) :]
            if remaining:
                # Capitalize first letter
                return (
                    f"/{remaining[0].lower()}{remaining[1:]}"
                    if len(remaining) > 1
                    else f"/{remaining.lower()}"
                )
        return None
