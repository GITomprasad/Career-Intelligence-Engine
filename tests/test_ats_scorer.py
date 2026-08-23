"""
Unit Tests for ATS Compatibility Scorer Engine.
"""

import pytest
import os
from src.engine.ats_scorer import ATSScorer
from src.nlp.parser import ResumeParser
from src.config import SAMPLE_RESUMES_DIR


@pytest.fixture
def ats_scorer():
    return ATSScorer()


@pytest.fixture
def resume_parser():
    return ResumeParser()


def test_ats_scorer_init(ats_scorer):
    assert ats_scorer is not None
    assert len(ats_scorer.roles) > 0


def test_ats_scorer_sample_data_analyst(ats_scorer, resume_parser):
    file_path = os.path.join(SAMPLE_RESUMES_DIR, "data_analyst_candidate.txt")
    parsed = resume_parser.parse(file_path)
    assert parsed["success"] is True

    result = ats_scorer.score(
        profile=parsed["profile"],
        target_role_id="data_analyst",
        raw_text=parsed["raw_text"]
    )

    assert "total" in result
    assert "keyword" in result
    assert "format" in result
    assert "experience" in result
    assert "issues" in result
    assert "wins" in result
    assert "verdict" in result
    assert "ats_pass_rate_estimate" in result

    assert 0 <= result["total"] <= 100
    assert 0 <= result["keyword"] <= 100
    assert 0 <= result["format"] <= 100
    assert 0 <= result["experience"] <= 100

    # Data Analyst candidate targeting Data Analyst role should score relatively high
    assert result["total"] >= 65
    assert len(result["wins"]) > 0


def test_ats_scorer_mismatched_role(ats_scorer, resume_parser):
    # Fresher candidate targeting Senior ML Engineer
    file_path = os.path.join(SAMPLE_RESUMES_DIR, "fresh_graduate_candidate.txt")
    parsed = resume_parser.parse(file_path)
    assert parsed["success"] is True

    result = ats_scorer.score(
        profile=parsed["profile"],
        target_role_id="ml_engineer",
        raw_text=parsed["raw_text"]
    )

    assert len(result["issues"]) > 0
    # Missing key ML skills should be mentioned in issues
    assert any("Add" in issue or "competencies" in issue or "experience" in issue.lower() for issue in result["issues"])


def test_ats_scorer_empty_profile(ats_scorer):
    empty_profile = {
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "skill_ids": [],
        "experience_years": 0.0,
        "education": {}
    }
    result = ats_scorer.score(empty_profile, "data_scientist", "")
    assert result["total"] <= 40
    assert len(result["issues"]) >= 3
