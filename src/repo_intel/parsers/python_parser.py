from tree_sitter import Parser as TSParser, Language
import tree_sitter_python
from repo_intel.parsers.base import Parser, ParseResult, Symbol, Import, Relation
import uuid


class PythonParser(Parser):
    """Python language parser using Tree-sitter."""

    def __init__(self):
        self.language = Language(tree_sitter_python.language())
        self.parser = TSParser(self.language)

    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse Python code and extract symbols."""
        tree = self.parser.parse(bytes(content, "utf-8"))
        root_node = tree.root_node

        symbols = []
        imports = []
        relations = []

        # Track if we're inside a class
        self._in_class = False

        self._traverse(root_node, content, file_id, symbols, imports, relations)

        return ParseResult(symbols=symbols, imports=imports, relations=relations)

    def _traverse(self, node, content, file_id, symbols, imports, relations):
        """Recursively traverse tree nodes."""

        # Handle function definitions
        if node.type == "function_definition":
            func_name = self._get_child_name(node, "identifier")
            if func_name:
                symbol_id = str(uuid.uuid4())
                # Check if this is an HTTP endpoint
                http_method = self._extract_http_method(node)
                http_path = self._extract_http_path(node)

                # Determine kind
                if http_method and http_path:
                    kind = "endpoint"
                elif self._in_class:
                    kind = "method"
                else:
                    kind = "function"

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
        elif node.type == "class_definition":
            class_name = self._get_child_name(node, "identifier")
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

                # Mark that we're inside a class for methods
                old_in_class = self._in_class
                self._in_class = True

                # Recurse into class body
                for child in node.children:
                    self._traverse(child, content, file_id, symbols, imports, relations)

                self._in_class = old_in_class
                return  # Don't recurse again at the end

        # Handle imports
        elif node.type in ("import_statement", "import_from_statement"):
            self._extract_import(node, imports)

        # Recurse into children
        for child in node.children:
            self._traverse(child, content, file_id, symbols, imports, relations)

    def _get_child_name(self, node, child_type):
        """Extract name from child node by type."""
        for child in node.children:
            if child.type == child_type:
                return child.text.decode("utf-8")
        return None

    def _extract_calls(self, node, caller_id, relations):
        """Extract function calls from function body."""
        for child in node.children:
            if child.type == "call":
                func_name = child.children[0].text.decode("utf-8") if child.children else None
                if func_name:
                    relations.append(
                        Relation(
                            from_id=caller_id,
                            to_id=func_name,  # Will resolve to actual symbol ID later
                            relation_type="calls",
                        )
                    )
            self._extract_calls(child, caller_id, relations)

    def _extract_inheritance(self, node, class_id, relations):
        """Extract inheritance relationships."""
        for child in node.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type == "identifier":
                        relations.append(
                            Relation(
                                from_id=class_id,
                                to_id=arg.text.decode("utf-8"),
                                relation_type="extends",
                            )
                        )

    def _extract_import(self, node, imports):
        """Extract import statements."""
        if node.type == "import_statement":
            for child in node.children:
                if child.type == "dotted_name":
                    imports.append(
                        Import(module=child.text.decode("utf-8"), line=node.start_point[0] + 1)
                    )
                    break  # Only extract the module name once
        elif node.type == "import_from_statement":
            for child in node.children:
                if child.type == "dotted_name":
                    imports.append(
                        Import(module=child.text.decode("utf-8"), line=node.start_point[0] + 1)
                    )
                    break  # Only extract the module name, not the imported items

    def _extract_http_method(self, node):
        """Extract HTTP method from Flask/FastAPI decorators."""
        # Check decorators (they come before the function)
        parent = node.parent
        if parent:
            for sibling in parent.children:
                if sibling.type == "decorator":
                    decorator_text = sibling.text.decode("utf-8")
                    if "methods=" in decorator_text:
                        if "'GET'" in decorator_text or '"GET"' in decorator_text:
                            return "GET"
                        elif "'POST'" in decorator_text or '"POST"' in decorator_text:
                            return "POST"
                    elif (
                        "@app.route" in decorator_text
                        or "@router." in decorator_text
                        or ".get(" in decorator_text
                    ):
                        return "GET"  # Default
                    elif ".post(" in decorator_text:
                        return "POST"
        return None

    def _extract_http_path(self, node):
        """Extract HTTP path from Flask/FastAPI decorators."""
        # Check decorators (they come before the function)
        parent = node.parent
        if parent:
            for sibling in parent.children:
                if sibling.type == "decorator":
                    decorator_text = sibling.text.decode("utf-8")
                    if (
                        "route(" in decorator_text
                        or ".get(" in decorator_text
                        or ".post(" in decorator_text
                    ):
                        # Extract path string
                        start = decorator_text.find('"')
                        if start == -1:
                            start = decorator_text.find("'")
                        if start != -1:
                            end = decorator_text.find(decorator_text[start], start + 1)
                            if end != -1:
                                return decorator_text[start + 1 : end]
        return None
