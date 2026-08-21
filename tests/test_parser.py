"""
Unit tests for Resume Parser and Skill Extractor.
"""

import os
import pytest
from src.nlp.parser import ResumeParser
from src.nlp.skill_extractor import SkillExtractor
from src.config import SAMPLE_RESUMES_DIR


@pytest.fixture
def parser():
    return ResumeParser()


@pytest.fixture
def extractor():
    return SkillExtractor()


def test_skill_extractor_normalization(extractor):
    # Test canonical normalization
    assert extractor.normalize_skill("sklearn") == "scikit_learn"
    assert extractor.normalize_skill("k8s") == "kubernetes"
    assert extractor.normalize_skill("postgres") == "postgresql"
    assert extractor.normalize_skill("power bi") == "power_bi"


def test_skill_extractor_from_text(extractor):
    text = "Experienced in Python, SQL, Docker, AWS EC2, and Scikit-Learn."
    result = extractor.extract_skills(text)
    
    assert "python" in result["skill_ids"]
    assert "sql" in result["skill_ids"]
    assert "docker" in result["skill_ids"]
    assert "aws" in result["skill_ids"]
    assert "scikit_learn" in result["skill_ids"]
    assert result["total_count"] >= 5


def test_resume_parser_txt(parser):
    sample_path = os.path.join(SAMPLE_RESUMES_DIR, "data_analyst_candidate.txt")
    result = parser.parse(sample_path)
    
    assert result["success"] is True
    profile = result["profile"]
    assert "OM PRAKASH SAHU" in profile["name"].upper() or "SAHU" in profile["name"].upper()
    assert "omprakash.sahu@email.com" in profile["email"]
    assert "python" in profile["skill_ids"]
    assert "power_bi" in profile["skill_ids"]
    assert profile["skills_count"] >= 5


def test_resume_parser_pdf(parser):
    sample_pdf_path = os.path.join(SAMPLE_RESUMES_DIR, "data_scientist_candidate.pdf")
    if os.path.exists(sample_pdf_path):
        result = parser.parse(sample_pdf_path)
        assert result["success"] is True
        profile = result["profile"]
        assert len(profile["skills"]) > 0
        assert "python" in profile["skill_ids"]
