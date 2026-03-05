import math
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
import networkx as nx


class PageRankScorer:
    """Rank symbols by importance using PageRank algorithm"""

    def rank_symbols(
        self,
        definitions: Dict[str, Set[str]],
        references: Dict[str, List[str]],
        chat_files: Set[str],
        mentioned_idents: Set[str],
    ) -> List[Tuple[str, str, float]]:
        """
        Rank symbols using PageRank.

        Args:
            definitions: symbol_name -> set of files where defined
            references: symbol_name -> list of files where referenced
            chat_files: files currently being worked on
            mentioned_idents: identifiers mentioned in conversation

        Returns:
            List of (file, symbol, score) tuples, sorted by score descending
        """
        # Build graph
        G = nx.MultiDiGraph()

        # Add edges based on references
        for symbol, ref_files in references.items():
            definers = definitions.get(symbol, set())

            if not definers:
                continue

            # Calculate weight multiplier
            weight = self._calculate_weight(symbol, mentioned_idents, definers)

            for ref_file in ref_files:
                for def_file in definers:
                    # Edge from referencing file to defining file
                    G.add_edge(ref_file, def_file, weight=weight, symbol=symbol)

        # Personalization: boost chat files
        personalization = {}
        if chat_files:
            for f in chat_files:
                personalization[f] = 1.0 / len(chat_files)

        # Run PageRank
        try:
            if personalization:
                ranked = nx.pagerank(
                    G, weight="weight", personalization=personalization, dangling=personalization
                )
            else:
                ranked = nx.pagerank(G, weight="weight")
        except:
            # Fallback if graph is empty
            return []

        # Convert to symbol rankings
        symbol_scores = []
        for symbol, definers in definitions.items():
            for def_file in definers:
                score = ranked.get(def_file, 0)
                symbol_scores.append((def_file, symbol, score))

        # Sort by score descending
        symbol_scores.sort(key=lambda x: x[2], reverse=True)

        return symbol_scores

    def _calculate_weight(
        self, symbol: str, mentioned_idents: Set[str], definers: Set[str]
    ) -> float:
        """Calculate edge weight multiplier"""
        weight = 1.0

        # Boost mentioned identifiers
        if symbol in mentioned_idents:
            weight *= 10.0

        # Boost meaningful names
        is_snake = "_" in symbol and any(c.isalpha() for c in symbol)
        is_kebab = "-" in symbol and any(c.isalpha() for c in symbol)
        is_camel = any(c.isupper() for c in symbol) and any(c.islower() for c in symbol)

        if (is_snake or is_kebab or is_camel) and len(symbol) >= 8:
            weight *= 10.0

        # Penalize private symbols
        if symbol.startswith("_"):
            weight *= 0.1

        # Penalize common names
        if len(definers) > 5:
            weight *= 0.1

        return weight
