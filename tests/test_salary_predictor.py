"""
Unit tests for Salary Predictor.
"""

import pytest
from src.models.salary_predictor import SalaryPredictor


@pytest.fixture
def predictor():
    return SalaryPredictor()


def test_salary_prediction_bounds(predictor):
    pred = predictor.predict_salary(
        role_id="data_scientist",
        experience_years=2.0,
        skill_count=8,
        education="Bachelor's Degree",
        location_tier="Tier-1",
        company_tier="Tier-1"
    )
    
    assert "predicted_lpa" in pred
    assert pred["predicted_lpa"] > 4.0
    assert pred["max_lpa"] > pred["min_lpa"]
    assert "formatted_range" in pred


def test_salary_experience_monotonicity(predictor):
    sal_junior = predictor.predict_salary(role_id="ml_engineer", experience_years=1.0, skill_count=5)
    sal_senior = predictor.predict_salary(role_id="ml_engineer", experience_years=7.0, skill_count=12)
    
    assert sal_senior["predicted_lpa"] > sal_junior["predicted_lpa"]
