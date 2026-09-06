import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.engine.market_analyzer import MarketAnalyzer

@pytest.fixture
def mock_ontology_path():
    return "data/skills_ontology.json"

@pytest.fixture
def mock_jobs_data():
    return pd.DataFrame({
        "job_id": [1, 2, 3, 4],
        "role_id": ["data_scientist", "data_scientist", "swe", "ml_engineer"],
        "role_title": ["Data Scientist", "Data Scientist", "Software Engineer", "ML Engineer"],
        "category": ["Data", "Data", "Engineering", "Data"],
        "all_skills": ["python, sql, machine learning", "python, r", "java, python, sql", "python, pytorch, docker, sql"],
        "salary_min_lpa": [10.0, 12.0, 8.0, 15.0],
        "salary_max_lpa": [20.0, 24.0, 16.0, 30.0],
        "salary_mid_lpa": [15.0, 18.0, 12.0, 22.5],
        "location": ["Bangalore", "Mumbai", "Bangalore", "Pune"],
        "company": ["Tech Corp", "Data Co", "Tech Corp", "AI Startup"]
    })

@pytest.fixture
def mock_salary_data():
    return pd.DataFrame({
        "role_id": ["data_scientist", "swe", "ml_engineer"],
        "base_salary": [15.0, 12.0, 22.5]
    })

@patch("src.engine.market_analyzer.pd.read_csv")
def test_market_analyzer_initialization(mock_read_csv, mock_jobs_data, mock_salary_data, mock_ontology_path):
    mock_read_csv.side_effect = [mock_jobs_data, mock_salary_data]
    analyzer = MarketAnalyzer(ontology_path=mock_ontology_path)

    assert not analyzer.df_jobs.empty
    assert not analyzer.df_salary.empty
    assert mock_read_csv.call_count == 2

@patch("src.engine.market_analyzer.pd.read_csv")
def test_get_top_skills_by_role_all(mock_read_csv, mock_jobs_data, mock_salary_data, mock_ontology_path):
    mock_read_csv.side_effect = [mock_jobs_data, mock_salary_data]
    analyzer = MarketAnalyzer(ontology_path=mock_ontology_path)

    # 4 jobs total, skills: python (4), sql (3), machine learning (1), r (1), java (1), pytorch (1), docker (1)
    results = analyzer.get_top_skills_by_role(role_id="all", top_n=3)

    assert len(results) == 3
    # Note: SkillExtractor translates names. Assuming 'python' -> 'Python'
    assert results[0]["skill_name"].lower() == "python"
    assert results[0]["count"] == 4
    assert results[0]["demand_percentage"] == 100.0  # 4/4 * 100

    assert results[1]["skill_name"].lower() == "sql"
    assert results[1]["count"] == 3
    assert results[1]["demand_percentage"] == 75.0  # 3/4 * 100

@patch("src.engine.market_analyzer.pd.read_csv")
def test_get_top_skills_by_role_specific(mock_read_csv, mock_jobs_data, mock_salary_data, mock_ontology_path):
    mock_read_csv.side_effect = [mock_jobs_data, mock_salary_data]
    analyzer = MarketAnalyzer(ontology_path=mock_ontology_path)

    # data_scientist: 2 jobs, python (2), sql (1), machine learning (1), r (1)
    results = analyzer.get_top_skills_by_role(role_id="data_scientist", top_n=2)

    assert len(results) == 2
    assert results[0]["skill_name"].lower() == "python"
    assert results[0]["count"] == 2
    assert results[0]["demand_percentage"] == 100.0

    # Second skill can be sql, machine learning or r depending on sorting, but count should be 1
    assert results[1]["count"] == 1
    assert results[1]["demand_percentage"] == 50.0

@patch("src.engine.market_analyzer.pd.read_csv")
def test_get_salary_by_role_distribution(mock_read_csv, mock_jobs_data, mock_salary_data, mock_ontology_path):
    mock_read_csv.side_effect = [mock_jobs_data, mock_salary_data]
    analyzer = MarketAnalyzer(ontology_path=mock_ontology_path)

    results = analyzer.get_salary_by_role_distribution()

    assert len(results) == 3
    # Should be sorted by avg_salary descending
    # ml_engineer (22.5), data_scientist ((15+18)/2=16.5), swe (12.0)
    assert results[0]["role_id"] == "ml_engineer"
    assert results[0]["avg_lpa"] == 22.5
    assert results[0]["job_count"] == 1

    assert results[1]["role_id"] == "data_scientist"
    assert results[1]["avg_lpa"] == 16.5
    assert results[1]["min_lpa"] == 11.0 # (10+12)/2
    assert results[1]["max_lpa"] == 22.0 # (20+24)/2
    assert results[1]["job_count"] == 2

    assert results[2]["role_id"] == "swe"
    assert results[2]["avg_lpa"] == 12.0

@patch("src.engine.market_analyzer.pd.read_csv")
def test_get_market_overview(mock_read_csv, mock_jobs_data, mock_salary_data, mock_ontology_path):
    mock_read_csv.side_effect = [mock_jobs_data, mock_salary_data]
    analyzer = MarketAnalyzer(ontology_path=mock_ontology_path)

    overview = analyzer.get_market_overview()

    assert overview["total_openings_analyzed"] == 4
    # (15+18+12+22.5)/4 = 16.875 -> 16.9
    assert overview["overall_avg_salary_lpa"] == 16.9
    assert overview["roles_available_count"] == 3

    # Tech Corp appears twice
    assert "Tech Corp" in overview["top_hiring_companies"]
    assert overview["top_hiring_companies"]["Tech Corp"] == 2

    # Bangalore appears twice
    assert "Bangalore" in overview["top_hiring_locations"]
    assert overview["top_hiring_locations"]["Bangalore"] == 2

@patch("src.engine.market_analyzer.pd.read_csv")
def test_empty_dataframe_handling(mock_read_csv, mock_ontology_path):
    mock_read_csv.side_effect = Exception("File not found")
    analyzer = MarketAnalyzer(ontology_path=mock_ontology_path)

    assert analyzer.df_jobs.empty
    assert analyzer.get_top_skills_by_role() == []
    assert analyzer.get_salary_by_role_distribution() == []
    assert analyzer.get_market_overview() == {}
