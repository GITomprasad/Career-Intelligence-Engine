import pytest
from unittest.mock import patch
from src.nlp.experience_analyzer import ExperienceAnalyzer

@pytest.fixture
def analyzer():
    return ExperienceAnalyzer()

def test_extract_date_intervals_pattern1_exception(analyzer):
    """
    Test that the try/except block for month parsing (Pattern 1)
    gracefully handles exceptions like ValueError.
    """
    text = "Jan 2020 - Dec 2022"
    # The rationale suggested causing an invalid string to int conversion.
    # We can trigger the except block by making _parse_month raise a ValueError,
    # which simulates a failure during the try block execution.
    with patch.object(ExperienceAnalyzer, '_parse_month', side_effect=ValueError("Simulated ValueError")):
        # The ValueError should be caught and ignored, resulting in 0.0 total years
        assert analyzer._extract_date_intervals(text) == 0.0

def test_extract_date_intervals_pattern2_exception(analyzer):
    """
    Test that the try/except block for year parsing (Pattern 2)
    gracefully handles exceptions.
    """
    text = "2020 - Present"
    # By mutating analyzer.current_year to an invalid string type,
    # we cause a TypeError when it attempts the subtraction: end_yr - start_yr.
    # The except block is a blanket except Exception:, so it will catch TypeError.
    # We test that it gracefully returns 0.0.
    analyzer.current_year = "InvalidYear"

    assert analyzer._extract_date_intervals(text) == 0.0
