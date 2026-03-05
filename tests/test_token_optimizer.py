def test_token_optimizer_exists():
    """Test that TokenOptimizer class exists"""
    from repo_intel.core.token_optimizer import TokenOptimizer

    optimizer = TokenOptimizer()
    assert hasattr(optimizer, "optimize")


def test_token_optimizer_fits_budget():
    """Test that optimizer fits within token budget"""
    from repo_intel.core.token_optimizer import TokenOptimizer

    optimizer = TokenOptimizer()

    # Sample ranked symbols
    symbols = [
        ("a.py", "foo", 0.9),
        ("b.py", "bar", 0.8),
        ("c.py", "baz", 0.7),
        ("d.py", "qux", 0.6),
        ("e.py", "quux", 0.5),
    ]

    # Simple formatter
    def formatter(syms):
        return "\n".join(f"{f}:{s}" for f, s, _ in syms)

    # Optimize with small budget
    result, tokens = optimizer.optimize(
        symbols,
        formatter,
        max_tokens=3,  # Only 3 words allowed
    )

    # Should fit within budget
    assert tokens <= 3

    # Should include highest-ranked symbols
    assert "foo" in result
