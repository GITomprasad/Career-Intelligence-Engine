"""
Unit tests for Skill Gap Analyzer, Roadmap Generator, and Simulator.
"""

import pytest
from src.engine.gap_analyzer import SkillGapAnalyzer
from src.engine.roadmap_generator import RoadmapGenerator


@pytest.fixture
def gap_analyzer():
    return SkillGapAnalyzer()


@pytest.fixture
def roadmap_gen():
    return RoadmapGenerator()


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
