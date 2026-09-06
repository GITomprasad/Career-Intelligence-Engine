import pytest
from src.engine.explainability import ExplainabilityEngine

@pytest.fixture
def explainability_engine():
    return ExplainabilityEngine()

def test_explain_match_score_high_readiness(explainability_engine):
    candidate_profile = {
        "experience_years": 3.0,
        "seniority_level": "mid-level"
    }
    target_role = {
        "title": "Software Engineer"
    }
    gap_analysis = {
        "readiness_score": 85.0,
        "strong_skills": [
            {"name": "Python", "type": "Core Requirement", "category": "Programming"},
            {"name": "Django", "type": "Core Requirement", "category": "Framework"},
            {"name": "SQL", "type": "Secondary", "category": "Database"},
            {"name": "AWS", "type": "Secondary", "category": "Cloud"},
            {"name": "Docker", "type": "Secondary", "category": "DevOps"},
            {"name": "Git", "type": "Secondary", "category": "Tools"} # 6th skill to test slicing
        ],
        "missing_skills": []
    }
    match_breakdown = {}

    result = explainability_engine.explain_match_score(
        candidate_profile, target_role, gap_analysis, match_breakdown
    )

    assert result["overall_score"] == 85.0
    assert result["summary_verdict"] == "Highly Competitive"

    # 5 strong skills + 1 experience driver = 6 positive drivers
    assert len(result["positive_drivers"]) == 6
    assert result["positive_drivers"][0]["impact"] == "+12.0%" # Core Requirement
    assert result["positive_drivers"][2]["impact"] == "+6.0%"  # Secondary

    # Experience driver
    exp_driver = next(d for d in result["positive_drivers"] if d["category"] == "Experience")
    assert exp_driver["impact"] == "+10.5%" # min(15.0, 3.0 * 3.5)

    assert len(result["deductions"]) == 0
    assert result["highest_roi_skill"] == "Cloud Architecture / MLOps"
    assert "primarily propelled by strong foundations in Python, Django, SQL" in result["key_takeaway"]

def test_explain_match_score_job_ready(explainability_engine):
    candidate_profile = {
        "experience_years": 0.5,
        "seniority_level": "junior"
    }
    target_role = {
        "title": "Data Scientist"
    }
    gap_analysis = {
        "readiness_score": 70.0,
        "strong_skills": [
            {"name": "Python", "type": "Core Requirement", "category": "Programming"}
        ],
        "missing_skills": [
            {"name": "Machine Learning", "priority": "Critical Priority", "category": "AI"},
            {"name": "Deep Learning", "priority": "Critical Priority", "category": "AI"},
            {"name": "NLP", "priority": "Medium", "category": "AI"},
            {"name": "Computer Vision", "priority": "Medium", "category": "AI"},
            {"name": "MLOps", "priority": "Low", "category": "DevOps"} # 5th missing skill to test slicing
        ]
    }
    match_breakdown = {}

    result = explainability_engine.explain_match_score(
        candidate_profile, target_role, gap_analysis, match_breakdown
    )

    assert result["overall_score"] == 70.0
    assert result["summary_verdict"] == "Job-Ready with Minor Gaps"

    # 1 strong skill, experience < 1.0 so no experience driver
    assert len(result["positive_drivers"]) == 1

    # 4 missing skills + 1 experience deduction = 5 deductions
    assert len(result["deductions"]) == 5
    assert result["deductions"][0]["impact"] == "-10.0%" # Critical Priority
    assert result["deductions"][2]["impact"] == "-5.0%"  # Medium

    # Experience deduction
    exp_deduction = next(d for d in result["deductions"] if d["category"] == "Experience Tenure")
    assert exp_deduction["impact"] == "-5.0%"

    assert result["highest_roi_skill"] == "Machine Learning"
    assert "primarily propelled by strong foundations in Python" in result["key_takeaway"]
    assert "Adding 'Machine Learning' to your skillset" in result["key_takeaway"]

def test_explain_match_score_default_foundational(explainability_engine):
    # Testing with mostly empty inputs
    result = explainability_engine.explain_match_score(
        candidate_profile={},
        target_role={},
        gap_analysis={},
        match_breakdown={}
    )

    assert result["overall_score"] == 50.0
    assert result["summary_verdict"] == "Foundational Stage"

    assert len(result["positive_drivers"]) == 0

    # Experience years default to 0.0, so < 1.0 deduction applies
    assert len(result["deductions"]) == 1
    assert result["deductions"][0]["category"] == "Experience Tenure"

    assert result["highest_roi_skill"] == "Cloud Architecture / MLOps"
    assert "propelled by strong foundations in core competencies" in result["key_takeaway"]
    assert "Adding 'Cloud Architecture / MLOps' to your skillset" in result["key_takeaway"]
