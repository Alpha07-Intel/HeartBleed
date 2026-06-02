import pytest
from heartbleed.core.models import Profile, InputType, ConfidenceLevel
from heartbleed.analyzers.correlation import CorrelationEngine

def test_profile_model():
    p = Profile(
        platform="Test",
        username="user123",
        url="https://test.com/user123"
    )
    assert p.username == "user123"
    assert p.platform == "Test"

def test_correlation_scoring():
    engine = CorrelationEngine(input_value="johndoe")
    
    # Exact match
    p1 = Profile(platform="P1", username="johndoe", url="https://p1.com/johndoe")
    res1 = engine.correlate(p1)
    assert res1.score >= 30
    assert res1.confidence != ConfidenceLevel.LOW
    
    # Mismatch
    p2 = Profile(platform="P2", username="different", url="https://p2.com/different")
    res2 = engine.correlate(p2)
    assert res2.score == 0
    assert res2.confidence == ConfidenceLevel.LOW

def test_cross_correlation():
    engine = CorrelationEngine(input_value="testuser")
    p1 = Profile(platform="P1", username="testuser", url="u1", location="London")
    p2 = Profile(platform="P2", username="testuser", url="u2", location="London")
    
    results = engine.correlate_batch([p1, p2])
    # Both should have exact username (30) + shared location (10) = 40
    assert results[0].score == 40
    assert results[1].score == 40
    assert any("Shared location" in r for r in results[0].match_reasons)
