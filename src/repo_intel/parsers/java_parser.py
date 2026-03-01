from tree_sitter import Parser as TSParser, Language
import tree_sitter_java
from repo_intel.parsers.base import Parser, ParseResult, Symbol, Import, Relation
import uuid


class JavaParser(Parser):
    """Java language parser using Tree-sitter."""

    def __init__(self):
        self.language = Language(tree_sitter_java.language())
        self.parser = TSParser(self.language)

    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse Java code and extract symbols."""
        tree = self.parser.parse(bytes(content, "utf-8"))
        root_node = tree.root_node

        symbols = []
        imports = []
        relations = []

        self._in_class = False
        self._traverse(root_node, content, file_id, symbols, imports, relations)

        return ParseResult(symbols=symbols, relations=relations)

    def _traverse(self, node, content, file_id, symbols, imports, relations):
        # Handle method declarations
        if node.type == "method_declaration":
            method_name = self._get_child_name(node, "identifier")
            if method_name:
                symbol_id = str(uuid.uuid4())
                # Check if it's an HTTP endpoint
                http_method = self._extract_http_method(node)
                http_path = self._extract_http_path(node)

                kind = "endpoint" if http_method else ("method" if self._in_class else "function")

                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=method_name,
                        kind=kind,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=True,
                        http_method=http_method,
                        path=http_path,
                    )
                )

                # Extract method calls
                self._extract_calls(node, symbol_id, relations)

        # Handle class declarations
        elif node.type == "class_declaration":
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
                        exported=True,
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
                return

        # Handle interface declarations
        elif node.type == "interface_declaration":
            interface_name = self._get_child_name(node, "identifier")
            if interface_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=interface_name,
                        kind="interface",
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=True,
                    )
                )

        # Handle imports
        elif node.type == "import_declaration":
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
        """Extract method calls from method body."""
        for child in node.children:
            if child.type == "object_creation_expression":
                # Handle constructor calls
                type_name = self._get_identifier_from_expression(child)
                if type_name:
                    relations.append(
                        Relation(from_id=caller_id, to_id=type_name, relation_type="calls")
                    )
            elif child.type == "method_invocation":
                # Handle method calls like obj.method()
                method_name = self._get_method_name(child)
                if method_name:
                    relations.append(
                        Relation(from_id=caller_id, to_id=method_name, relation_type="calls")
                    )
            self._extract_calls(child, caller_id, relations)

    def _get_method_name(self, node):
        """Extract method name from method invocation."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None

    def _get_identifier_from_expression(self, node):
        """Extract type name from object creation expression."""
        for child in node.children:
            if child.type == "type_identifier":
                return child.text.decode("utf-8")
        return None

    def _extract_inheritance(self, node, class_id, relations):
        """Extract inheritance relationships."""
        for child in node.children:
            if child.type == "superclass":
                for subchild in child.children:
                    if subchild.type == "type_identifier":
                        relations.append(
                            Relation(
                                from_id=class_id,
                                to_id=subchild.text.decode("utf-8"),
                                relation_type="extends",
                            )
                        )
            elif child.type == "interfaces":
                for subchild in child.children:
                    if subchild.type == "type_list":
                        for type_elem in subchild.children:
                            if type_elem.type == "type_identifier":
                                relations.append(
                                    Relation(
                                        from_id=class_id,
                                        to_id=type_elem.text.decode("utf-8"),
                                        relation_type="implements",
                                    )
                                )

    def _extract_import(self, node, imports):
        """Extract import statements."""
        for child in node.children:
            if child.type == "scoped_identifier":
                imports.append(
                    Import(module=child.text.decode("utf-8"), line=node.start_point[0] + 1)
                )
                break

    def _extract_http_method(self, node):
        """Extract HTTP method from annotations (Spring MVC)."""
        # Check for annotations in modifiers
        for child in node.children:
            if child.type == "modifiers":
                for modifier in child.children:
                    if modifier.type == "annotation":
                        annotation_text = modifier.text.decode("utf-8")
                        if (
                            "@GetMapping" in annotation_text
                            or "@RequestMapping(method=GET" in annotation_text
                        ):
                            return "GET"
                        elif (
                            "@PostMapping" in annotation_text
                            or "@RequestMapping(method=POST" in annotation_text
                        ):
                            return "POST"
                        elif "@PutMapping" in annotation_text:
                            return "PUT"
                        elif "@DeleteMapping" in annotation_text:
                            return "DELETE"
        return None

    def _extract_http_path(self, node):
        """Extract HTTP path from Spring annotations."""
        for child in node.children:
            if child.type == "modifiers":
                for modifier in child.children:
                    if modifier.type == "annotation":
                        annotation_text = modifier.text.decode("utf-8")
                        start = annotation_text.find('"')
                        if start == -1:
                            start = annotation_text.find("'")
                        if start != -1:
                            end = annotation_text.find(annotation_text[start], start + 1)
                            if end != -1:
                                path = annotation_text[start + 1 : end]
                                if "=" not in path:
                                    return path
        return None
