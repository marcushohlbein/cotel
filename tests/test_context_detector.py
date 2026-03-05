def test_context_detector_exists():
    """Test that ContextDetector class exists"""
    from repo_intel.core.context_detector import ContextDetector

    detector = ContextDetector()
    assert hasattr(detector, "detect_context")
