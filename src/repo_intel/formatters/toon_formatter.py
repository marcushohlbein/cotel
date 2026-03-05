from typing import List, Tuple, Dict


class TOONFormatter:
    """Format repomap as TOON (Token-Oriented Object Notation)"""

    def format(self, symbols: List[Dict], files: List[Dict], metadata: Dict) -> str:
        """
        Format repomap data as TOON.

        Args:
            symbols: List of symbol dicts
            files: List of file dicts
            metadata: Repo metadata (project, tokens_used, etc.)

        Returns:
            TOON formatted string
        """
        lines = []

        # Metadata section
        lines.append("repo_map{")
        for key, value in metadata.items():
            lines.append(f"  {key}: {self._format_value(value)}")
        lines.append("}")

        # Symbols section (tabular array)
        if symbols:
            lines.append("")
            lines.append(
                f"symbols[{len(symbols)}]{{name,kind,file,start_line,end_line,signature}}:"
            )
            for sym in symbols:
                row = ",".join(
                    [
                        sym.get("name", ""),
                        sym.get("kind", ""),
                        sym.get("file", ""),
                        str(sym.get("start_line", 0)),
                        str(sym.get("end_line", 0)),
                        self._escape_csv(sym.get("signature", "")),
                    ]
                )
                lines.append(f"  {row}")

        # Files section (tabular array)
        if files:
            lines.append("")
            lines.append(f"files[{len(files)}]{{path,symbol_count,language}}:")
            for f in files:
                row = ",".join(
                    [f.get("path", ""), str(f.get("symbol_count", 0)), f.get("language", "")]
                )
                lines.append(f"  {row}")

        return "\n".join(lines) + "\n"

    def _format_value(self, value) -> str:
        """Format a value for TOON"""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return "true" if value else "false"
        else:
            return str(value)

    def _escape_csv(self, value: str) -> str:
        """Escape value for CSV-style field"""
        if "," in value or '"' in value or "\n" in value:
            escaped = value.replace('"', '""')
            return f'"{escaped}"'
        return value
