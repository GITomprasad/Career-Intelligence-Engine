"""
Unit tests for MarketAnalyzer.
"""

import pytest
import pandas as pd
from src.engine.market_analyzer import MarketAnalyzer

def test_market_analyzer_load_invalid_paths():
    """Test that MarketAnalyzer handles invalid paths gracefully during initialization."""
    # Initialize with paths that do not exist
    analyzer = MarketAnalyzer(
        jobs_path="invalid_jobs_path.csv",
        salary_path="invalid_salary_path.csv",
        ontology_path=None # Can just use default for ontology if we don't care, but this might hit an issue if we don't have default.
    )

    # Verify that dataframes remain empty due to the exception being caught
    assert analyzer.df_jobs.empty is True
    assert analyzer.df_salary.empty is True

def test_market_analyzer_get_top_skills_by_role_empty():
    """Test get_top_skills_by_role with empty dataframe."""
    analyzer = MarketAnalyzer(
        jobs_path="invalid.csv",
        salary_path="invalid.csv"
    )
    assert analyzer.get_top_skills_by_role() == []

def test_market_analyzer_get_salary_by_role_distribution_empty():
    """Test get_salary_by_role_distribution with empty dataframe."""
    analyzer = MarketAnalyzer(
        jobs_path="invalid.csv",
        salary_path="invalid.csv"
    )
    assert analyzer.get_salary_by_role_distribution() == []

def test_market_analyzer_get_market_overview_empty():
    """Test get_market_overview with empty dataframe."""
    analyzer = MarketAnalyzer(
        jobs_path="invalid.csv",
        salary_path="invalid.csv"
    )
    assert analyzer.get_market_overview() == {}
