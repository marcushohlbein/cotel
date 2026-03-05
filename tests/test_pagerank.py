def test_pagerank_scorer_exists():
    """Test that PageRankScorer class exists"""
    from repo_intel.core.pagerank import PageRankScorer

    scorer = PageRankScorer()
    assert hasattr(scorer, "rank_symbols")


def test_pagerank_ranks_symbols():
    """Test that PageRank correctly ranks symbols"""
    from repo_intel.core.pagerank import PageRankScorer

    scorer = PageRankScorer()

    # Sample data
    definitions = {"foo": {"a.py"}, "bar": {"b.py"}, "baz": {"c.py"}}

    references = {
        "foo": ["b.py", "c.py"],  # foo is referenced by b and c
        "bar": ["c.py"],  # bar is referenced by c
        "baz": [],  # baz is not referenced
    }

    chat_files = {"a.py"}  # Working on a.py
    mentioned_idents = set()

    ranked = scorer.rank_symbols(definitions, references, chat_files, mentioned_idents)

    # Should return list of (file, symbol, score)
    assert len(ranked) == 3
    assert all(isinstance(item, tuple) for item in ranked)
    assert all(len(item) == 3 for item in ranked)

    # foo should be ranked higher than baz (more references)
    foo_score = next(s for f, s, sc in ranked if s == "foo")
    baz_score = next(s for f, s, sc in ranked if s == "baz")

    # Actually we want the score, not the symbol
    foo_entry = next((f, s, sc) for f, s, sc in ranked if s == "foo")
    baz_entry = next((f, s, sc) for f, s, sc in ranked if s == "baz")

    assert foo_entry[2] > baz_entry[2], "foo should rank higher than baz"
