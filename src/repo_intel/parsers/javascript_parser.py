from tree_sitter import Parser as TSParser, Language
import tree_sitter_javascript
from repo_intel.parsers.base import Parser, ParseResult, Symbol, Relation
import uuid


class JavaScriptParser(Parser):
    """JavaScript/TypeScript parser using Tree-sitter."""

    def __init__(self, language="javascript"):
        # For now, both JS and TS use the same parser
        # TypeScript support can be added later with a separate grammar
        self.language = Language(tree_sitter_javascript.language())
        self.parser = TSParser(self.language)

    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse JavaScript/TypeScript code."""
        tree = self.parser.parse(bytes(content, "utf-8"))
        root_node = tree.root_node

        symbols = []
        relations = []

        self._traverse(root_node, content, file_id, symbols, relations)

        return ParseResult(symbols=symbols, relations=relations)

    def _traverse(self, node, content, file_id, symbols, relations):
        # Function declarations
        if node.type == "function_declaration":
            func_name = self._get_identifier(node)
            if func_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=func_name,
                        kind="function",
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=False,
                    )
                )

        # Class declarations
        elif node.type == "class_declaration":
            class_name = self._get_identifier(node)
            if class_name:
                symbol_id = str(uuid.uuid4())
                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=class_name,
                        kind="class",
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=self._is_exported(node),
                    )
                )

        # Variable declarations with arrow functions
        elif node.type in ("variable_declaration", "lexical_declaration"):
            self._handle_variable_declaration(node, symbols)

        # Expressions (for Express-style endpoints)
        elif node.type == "expression_statement":
            self._handle_expression(node, symbols, relations)


        # Recurse
        for child in node.children:
            self._traverse(child, content, file_id, symbols, relations)

    def _get_identifier(self, node):
        """Extract identifier from node."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None

    def _is_exported(self, node):
        """Check if node is exported."""
        parent = node.parent
        if parent and parent.type == "export_statement":
            return True
        return False

    def _handle_variable_declaration(self, node, symbols):
        """Handle variable declarations (including arrow functions)."""
        for child in node.children:
            if child.type == "variable_declarator":
                name = self._get_identifier(child)
                if name and self._has_arrow_function(child):
                    symbols.append(
                        Symbol(
                            id=str(uuid.uuid4()),
                            name=name,
                            kind="function",
                            start_line=node.start_point[0] + 1,
                            end_line=node.end_point[0] + 1,
                            exported=False,
                        )
                    )

    def _has_arrow_function(self, node):
        """Recursively check if node contains an arrow function."""
        if node.type == "arrow_function":
            return True
        for child in node.children:
            if self._has_arrow_function(child):
                return True
        return False

    def _handle_expression(self, node, symbols, relations):
        """Handle expressions for HTTP endpoint detection."""
        text = node.text.decode("utf-8")

        # Express-style: app.get('/path', handler)
        if "app." in text or "router." in text:
            for child in node.children:
                if child.type == "call_expression":
                    method = self._extract_http_method(child)
                    path = self._extract_path(child)

                    if method and path:
                        symbols.append(
                            Symbol(
                                id=str(uuid.uuid4()),
                                name=f"{method} {path}",
                                kind="endpoint",
                                start_line=node.start_point[0] + 1,
                                end_line=node.end_point[0] + 1,
                                exported=True,
                                http_method=method,
                                path=path,
                            )
                        )

    def _extract_http_method(self, node):
        """Extract HTTP method from call expression."""
        for child in node.children:
            if child.type == "member_expression":
                for subchild in child.children:
                    if subchild.type in ("property_identifier", "identifier"):
                        method = subchild.text.decode("utf-8").upper()
                        if method in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                            return method
        return None

    def _extract_path(self, node):
        """Extract path string from call expression."""
        for child in node.children:
            if child.type == "arguments":
                for arg in child.children:
                    if arg.type == "string":
                        return arg.text.decode("utf-8").strip('"').strip("'")
        return None
