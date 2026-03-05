def test_pagerank_scorer_exists():
    """Test that PageRankScorer class exists"""
    from repo_intel.core.pagerank import PageRankScorer

    scorer = PageRankScorer()
    assert hasattr(scorer, "rank_symbols")
