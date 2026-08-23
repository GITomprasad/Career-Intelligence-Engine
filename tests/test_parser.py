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


def test_resume_parser_json(parser):
    json_resume = """
    {
        "basics": {
            "name": "Vikram Malhotra",
            "email": "vikram.m@gmail.com",
            "phone": "+91 9876543210",
            "location": "Bangalore"
        },
        "skills": [
            {"name": "Python", "keywords": ["Django", "FastAPI"]},
            {"name": "Databases", "keywords": ["PostgreSQL", "Redis"]}
        ]
    }
    """
    result = parser.parse(json_resume, filename="resume.json")
    assert result["success"] is True
    profile = result["profile"]
    assert profile["name"] == "Vikram Malhotra"
    assert profile["email"] == "vikram.m@gmail.com"
    assert "python" in profile["skill_ids"]
    assert "fastapi" in profile["skill_ids"]


def test_resume_parser_rtf(parser):
    rtf_content = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Courier;}}\f0\fs24 Ananya Sharma\par Python Developer with 2+ years of experience in AWS, Docker, and Flask.\par Email: ananya.s@example.com\par}"
    result = parser.parse(rtf_content.encode("utf-8"), filename="resume.rtf")
    assert result["success"] is True
    profile = result["profile"]
    assert "Ananya Sharma" in profile["name"]
    assert "python" in profile["skill_ids"]
    assert "aws" in profile["skill_ids"]
    assert profile["experience_years"] == 2.0


def test_resume_parser_markdown(parser):
    md_content = """
    # Rohan Gupta
    **Email**: rohan.g@gmail.com | **Phone**: +91 9876543210 | **Location**: Pune

    ## Professional Summary
    Software Engineer with 1.5 years of experience in React, TypeScript, and Node.js.

    ## Education
    - **B.Tech Computer Science**, Pune University (2020 - 2024)

    ## Technical Skills
    - Python, React, TypeScript, Docker, Git
    """
    result = parser.parse(md_content, filename="resume.md")
    assert result["success"] is True
    profile = result["profile"]
    assert profile["name"] == "Rohan Gupta"
    assert "python" in profile["skill_ids"]
    assert "react" in profile["skill_ids"]
    assert "typescript" in profile["skill_ids"]
    assert profile["experience_years"] == 1.5
    assert profile["seniority_level"] == "Junior Associate"


def test_resume_parser_image_ocr(parser):
    from PIL import Image, ImageDraw
    import io

    # Create a synthetic resume image
    img = Image.new("RGB", (600, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "Neha Patel\nSenior Python Developer with 5 years experience\nSkills: Python, SQL, Docker, AWS", fill=(0, 0, 0))

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    result = parser.parse(img_bytes, filename="resume.png")
    assert result["success"] is True
    profile = result["profile"]
    assert "Patel" in profile["name"]
    assert "python" in profile["skill_ids"]
    assert "docker" in profile["skill_ids"]
    assert profile["experience_years"] == 5.0


