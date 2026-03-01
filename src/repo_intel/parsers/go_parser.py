from tree_sitter import Parser as TSParser, Language
import tree_sitter_go
from repo_intel.parsers.base import Parser, ParseResult, Symbol, Import, Relation
import uuid


class GoParser(Parser):
    """Go language parser using Tree-sitter."""

    def __init__(self):
        self.language = Language(tree_sitter_go.language())
        self.parser = TSParser(self.language)

    def parse(self, content: str, file_id: str) -> ParseResult:
        """Parse Go code and extract symbols."""
        tree = self.parser.parse(bytes(content, "utf-8"))
        root_node = tree.root_node

        symbols = []
        imports = []
        relations = []

        self._traverse(root_node, content, file_id, symbols, imports, relations)

        return ParseResult(symbols=symbols, imports=imports, relations=relations)

    def _traverse(self, node, content, file_id, symbols, imports, relations):
        # Handle function declarations
        if node.type == "function_declaration":
            func_name = self._get_identifier(node)
            if func_name:
                symbol_id = str(uuid.uuid4())

                # Check if it's an HTTP endpoint (receiver function with specific signatures)
                is_endpoint, http_method, http_path = self._extract_http_info(node)

                kind = "endpoint" if is_endpoint else "function"

                symbols.append(
                    Symbol(
                        id=symbol_id,
                        name=func_name,
                        kind=kind,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        exported=self._is_exported(func_name),
                        http_method=http_method,
                        path=http_path,
                    )
                )

                # Extract function calls
                self._extract_calls(node, symbol_id, relations)

        # Handle type declarations (structs, interfaces)
        elif node.type == "type_declaration":
            for child in node.children:
                if child.type == "type_spec":
                    type_name = self._get_identifier(child)
                    if type_name:
                        symbol_id = str(uuid.uuid4())
                        # Determine kind
                        kind = "interface"
                        for subchild in child.children:
                            if subchild.type == "struct_type":
                                kind = "class"

                        symbols.append(
                            Symbol(
                                id=symbol_id,
                                name=type_name,
                                kind=kind,
                                start_line=node.start_point[0] + 1,
                                end_line=node.end_point[0] + 1,
                                exported=self._is_exported(type_name),
                            )
                        )

        # Handle imports
        elif node.type == "import_declaration":
            self._extract_import(node, imports)

        # Recurse into children
        for child in node.children:
            self._traverse(child, content, file_id, symbols, imports, relations)

    def _get_identifier(self, node):
        """Extract identifier from node."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None

    def _is_exported(self, name):
        """Check if function is exported (capitalized)."""
        return name and name[0].isupper()

    def _extract_calls(self, node, caller_id, relations):
        """Extract function calls from function body."""
        for child in node.children:
            if child.type == "call_expression":
                func_name = self._get_call_name(child)
                if func_name:
                    relations.append(
                        Relation(from_id=caller_id, to_id=func_name, relation_type="calls")
                    )
            self._extract_calls(child, caller_id, relations)

    def _get_call_name(self, node):
        """Extract function name from call expression."""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
            # Handle method calls like pkg.Function()
            elif child.type == "selector_expression":
                for subchild in child.children:
                    if subchild.type == "field_identifier":
                        return subchild.text.decode("utf-8")
                    elif subchild.type == "identifier":
                        return subchild.text.decode("utf-8")
        return None

    def _extract_import(self, node, imports):
        """Extract import statements."""
        for child in node.children:
            if child.type == "import_spec":
                for subchild in child.children:
                    if subchild.type == "interpreted_string_literal":
                        import_path = subchild.text.decode("utf-8").strip('"')
                        imports.append(Import(module=import_path, line=node.start_point[0] + 1))
                        return

    def _extract_http_info(self, node):
        """Extract HTTP info from function signature (common Go web frameworks)."""
        func_name = self._get_identifier(node)
        if not func_name:
            return False, None, None

        # Common Go HTTP patterns
        http_methods = ["Get", "Post", "Put", "Delete", "Patch"]
        for method in http_methods:
            if func_name.startswith(method):
                # Extract path from function parameters
                path = self._extract_path_from_params(node)
                return True, method.upper(), path

        return False, None, None

    def _extract_path_from_params(self, node):
        """Extract URL path from function parameters."""
        # Look for string parameters that might be URL paths
        for child in node.children:
            if child.type == "parameter_list":
                for param in child.children:
                    if param.type == "parameter_declaration":
                        for subchild in param.children:
                            if subchild.type == "interpreted_string_literal":
                                path = subchild.text.decode("utf-8").strip('"')
                                if path.startswith("/"):
                                    return path
        return None
