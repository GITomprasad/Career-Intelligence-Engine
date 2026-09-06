"""
Unit tests for Skill Gap Analyzer, Roadmap Generator, and Simulator.
"""

import pytest
from src.engine.gap_analyzer import SkillGapAnalyzer
from src.engine.roadmap_generator import RoadmapGenerator
from src.engine.simulator import CareerSimulator


@pytest.fixture
def gap_analyzer():
    return SkillGapAnalyzer()


@pytest.fixture
def roadmap_gen():
    return RoadmapGenerator()


@pytest.fixture
def simulator():
    return CareerSimulator()


def test_gap_analyzer_classification(gap_analyzer):
    candidate_skills = ["python", "sql", "pandas", "numpy"]
    result = gap_analyzer.analyze_gap(candidate_skills, "data_scientist")
    
    assert "readiness_score" in result
    assert result["readiness_score"] > 20.0
    assert len(result["strong_skills"]) >= 2
    assert len(result["missing_skills"]) > 0


def test_roadmap_generation(gap_analyzer, roadmap_gen):
    candidate_skills = ["python", "sql"]
    gap = gap_analyzer.analyze_gap(candidate_skills, "data_scientist")
    roadmap = roadmap_gen.generate_roadmap(gap)
    
    assert "phases" in roadmap
    assert len(roadmap["phases"]) >= 2
    assert roadmap["total_estimated_weeks"] > 0


def test_career_simulator_deltas(simulator):
    profile = {
        "name": "Test User",
        "skill_ids": ["python", "sql"],
        "experience_years": 1.0,
        "education": {"degree": "Bachelor's Degree"}
    }
    
    sim = simulator.simulate(
        current_profile=profile,
        target_role_id="data_scientist",
        additional_skills=["docker", "aws", "machine_learning"],
        additional_experience_years=1.0
    )
    
    assert sim["impact"]["readiness_delta_pct"] > 0
    assert sim["impact"]["salary_increase_lpa"] > 0
