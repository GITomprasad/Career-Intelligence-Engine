import pytest
from unittest.mock import patch, MagicMock
from src.engine.simulator import CareerSimulator


@pytest.fixture
def simulator():
    # Mocking dependencies at instantiation time.
    # CareerSimulator __init__ instantiates SkillGapAnalyzer, SalaryPredictor, JobMatcher.
    with patch("src.engine.simulator.SkillGapAnalyzer") as mock_gap_analyzer_cls, \
         patch("src.engine.simulator.SalaryPredictor") as mock_salary_predictor_cls, \
         patch("src.engine.simulator.JobMatcher") as mock_matcher_cls:

        # Create instances that the mocked classes will return
        mock_gap_analyzer = MagicMock()
        mock_salary_predictor = MagicMock()
        mock_matcher = MagicMock()

        mock_gap_analyzer_cls.return_value = mock_gap_analyzer
        mock_salary_predictor_cls.return_value = mock_salary_predictor
        mock_matcher_cls.return_value = mock_matcher

        # Instantiate CareerSimulator which uses the mocked classes
        simulator = CareerSimulator()

        # Give access to the mocked instances for test verification
        simulator.mock_gap_analyzer = mock_gap_analyzer
        simulator.mock_salary_predictor = mock_salary_predictor
        simulator.mock_matcher = mock_matcher

        yield simulator


def test_simulate_happy_path(simulator):
    # Setup mocks for base state
    # First call is base gap, second call is sim gap
    simulator.mock_gap_analyzer.analyze_gap.side_effect = [
        {"readiness_score": 50.0, "role_title": "Data Scientist"},
        {"readiness_score": 80.0, "role_title": "Data Scientist"}
    ]

    # First call is base salary, second call is sim salary
    simulator.mock_salary_predictor.predict_salary.side_effect = [
        {"predicted_lpa": 10.0},
        {"predicted_lpa": 15.0}
    ]

    simulator.mock_matcher.match_jobs.return_value = [
        {"match_score": 80.0}, {"match_score": 75.0}, {"match_score": 60.0}
    ]

    profile = {
        "skill_ids": ["python"],
        "experience_years": 2.0,
        "education": {"degree": "Bachelor's Degree"}
    }

    result = simulator.simulate(
        current_profile=profile,
        target_role_id="data_scientist",
        additional_skills=["sql", "pandas"],
        additional_experience_years=1.0
    )

    # Verify Readiness
    assert result["baseline"]["readiness_score"] == 50.0
    assert result["simulated"]["readiness_score"] == 80.0
    assert result["impact"]["readiness_delta_pct"] == 30.0

    # Verify Salary
    assert result["baseline"]["predicted_salary_lpa"] == 10.0
    assert result["simulated"]["predicted_salary_lpa"] == 15.0
    assert result["impact"]["salary_increase_lpa"] == 5.0
    assert result["impact"]["salary_growth_pct"] == 50.0

    # Verify Jobs Match count >= 75.0 (2 out of 3 matches)
    assert result["simulated"]["high_match_jobs_unlocked"] == 2

    # Verify calls
    assert simulator.mock_gap_analyzer.analyze_gap.call_count == 2
    assert simulator.mock_salary_predictor.predict_salary.call_count == 2
    simulator.mock_matcher.match_jobs.assert_called_once()


def test_simulate_zero_additions(simulator):
    simulator.mock_gap_analyzer.analyze_gap.return_value = {"readiness_score": 60.0, "role_title": "Software Engineer"}
    simulator.mock_salary_predictor.predict_salary.return_value = {"predicted_lpa": 12.0}
    simulator.mock_matcher.match_jobs.return_value = []

    profile = {
        "skill_ids": ["java", "spring"],
        "experience_years": 3.0,
        "education": {"degree": "Bachelor's Degree"}
    }

    result = simulator.simulate(
        current_profile=profile,
        target_role_id="software_engineer",
        additional_skills=[],
        additional_experience_years=0.0
    )

    assert result["impact"]["readiness_delta_pct"] == 0.0
    assert result["impact"]["salary_increase_lpa"] == 0.0
    assert result["impact"]["salary_growth_pct"] == 0.0


def test_simulate_simulated_education(simulator):
    simulator.mock_gap_analyzer.analyze_gap.return_value = {"readiness_score": 50.0, "role_title": "Role"}
    simulator.mock_salary_predictor.predict_salary.side_effect = [
        {"predicted_lpa": 8.0},
        {"predicted_lpa": 12.0}
    ]
    simulator.mock_matcher.match_jobs.return_value = []

    profile = {
        "skill_ids": ["c++"],
        "experience_years": 1.0,
        "education": {"degree": "High School"}
    }

    result = simulator.simulate(
        current_profile=profile,
        target_role_id="role",
        additional_skills=[],
        additional_experience_years=0.0,
        simulated_education="Master's Degree"
    )

    # Make sure we called predict_salary with Master's Degree the second time
    calls = simulator.mock_salary_predictor.predict_salary.call_args_list
    assert calls[0].kwargs["education"] == "High School"
    assert calls[1].kwargs["education"] == "Master's Degree"

    assert result["impact"]["salary_increase_lpa"] == 4.0


def test_simulate_low_base_salary(simulator):
    # Testing division by zero prevention using `max(1.0, base_salary_lpa)`
    simulator.mock_gap_analyzer.analyze_gap.return_value = {"readiness_score": 10.0, "role_title": "Role"}
    simulator.mock_salary_predictor.predict_salary.side_effect = [
        {"predicted_lpa": 0.5}, # Base salary very low
        {"predicted_lpa": 5.5}  # Sim salary
    ]
    simulator.mock_matcher.match_jobs.return_value = []

    profile = {
        "skill_ids": [],
        "experience_years": 0.0,
        "education": {"degree": "None"}
    }

    result = simulator.simulate(
        current_profile=profile,
        target_role_id="role",
        additional_skills=["python"],
        additional_experience_years=0.0
    )

    # Delta is 5.0
    assert result["impact"]["salary_increase_lpa"] == 5.0
    # Expected pct = (5.0 / max(1.0, 0.5)) * 100 = 500.0%
    assert result["impact"]["salary_growth_pct"] == 500.0
