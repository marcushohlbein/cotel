from typing import List, Tuple, Callable


class TokenOptimizer:
    """Optimize repomap to fit within token budget using binary search"""

    def optimize(
        self,
        ranked_symbols: List[Tuple[str, str, float]],
        formatter: Callable,
        max_tokens: int = 1024,
        token_counter: Callable[[str], int] = None,
    ) -> Tuple[str, int]:
        """
        Binary search to find optimal number of symbols.

        Args:
            ranked_symbols: List of (file, symbol, score) sorted by score
            formatter: Function to format symbols into string
            max_tokens: Maximum token budget
            token_counter: Function to count tokens (default: simple word count)

        Returns:
            Tuple of (formatted_map, actual_token_count)
        """
        if token_counter is None:
            token_counter = self._simple_token_count

        if not ranked_symbols:
            return "", 0

        lower = 0
        upper = len(ranked_symbols)
        best_map = ""
        best_tokens = 0

        while lower <= upper:
            middle = (lower + upper) // 2

            # Format subset of symbols
            candidate_symbols = ranked_symbols[:middle]
            candidate_map = formatter(candidate_symbols)

            # Count tokens
            tokens = token_counter(candidate_map)

            # Check if within budget
            if tokens <= max_tokens:
                # This is valid, try to include more
                if tokens > best_tokens:
                    best_map = candidate_map
                    best_tokens = tokens
                lower = middle + 1
            else:
                # Over budget, reduce
                upper = middle - 1

        return best_map, best_tokens

    def _simple_token_count(self, text: str) -> int:
        """Simple token count (words)"""
        return len(text.split())
