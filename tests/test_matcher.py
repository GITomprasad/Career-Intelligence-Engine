"""
Unit tests for Job Matching Engine and Role Classifier.
"""

import pytest
from src.models.matcher import JobMatcher
from src.models.role_classifier import RoleClassifier


@pytest.fixture
def matcher():
    return JobMatcher()


@pytest.fixture
def classifier():
    return RoleClassifier()


def test_job_matcher_scoring(matcher):
    candidate_profile = {
        "name": "Test Candidate",
        "skill_ids": ["python", "sql", "pandas", "scikit_learn", "machine_learning"],
        "skills": ["Python", "SQL", "Pandas", "Scikit-Learn", "Machine Learning"],
        "experience_years": 2.0,
        "education": {"degree": "Bachelor's Degree"},
        "raw_text": "Experienced Python and SQL Machine Learning engineer with Pandas and Scikit-learn."
    }
    
    matches = matcher.match_jobs(candidate_profile, target_role_id="data_scientist", top_n=5)
    assert len(matches) > 0
    top_match = matches[0]
    assert top_match["match_score"] >= 40.0
    assert "matched_skills" in top_match
    assert "score_breakdown" in top_match


def test_role_classifier_prediction(classifier):
    skills = ["python", "sql", "power_bi", "tableau", "excel"]
    roles = classifier.predict_roles(skills, top_n=3)
    
    assert len(roles) >= 1
    role_titles = [r["title"].lower() for r in roles]
    assert any("analyst" in t or "data" in t for t in role_titles)
