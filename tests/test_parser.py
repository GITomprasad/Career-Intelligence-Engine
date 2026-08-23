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


def test_validate_is_resume_with_cbse_and_grades(parser):
    """Ensure resumes with CBSE, ICSE, Class 10/12, and SGPA/CGPA are accepted and not rejected as marksheets."""
    resume_text = """
    Om Prakash Sahu
    Email: omprakash.sahu@email.com | Phone: +91 9876543210 | Bangalore
    LinkedIn: linkedin.com/in/omprakash-sahu | GitHub: github.com/opsahu

    PROFESSIONAL SUMMARY
    Data Analyst with 2 years of experience analyzing datasets and building interactive dashboards with Python, SQL, and Power BI.

    EDUCATION
    - B.Tech in Computer Science, VIT Vellore (2019 - 2023) - SGPA: 8.8 / 10
    - Class XII (Senior Secondary), CBSE Board - 92.4%
    - Class X (Secondary School Examination), CBSE Board - 95.0%

    TECHNICAL SKILLS
    - Languages: Python, SQL, C++
    - Tools & Libraries: Pandas, NumPy, Scikit-Learn, Power BI, Tableau, Excel, Git

    WORK EXPERIENCE
    Data Analyst | Analytics Corp (2023 - Present)
    - Developed automated ETL pipelines reducing manual reporting by 40%.
    - Designed executive Power BI dashboards for 15+ KPIs.

    PROJECTS
    - Customer Churn Predictor: Built ML model with 88% accuracy using Scikit-Learn.
    """
    validation = parser.validate_is_resume(resume_text)
    assert validation["is_resume"] is True
    assert validation["confidence"] >= 0.70


def test_validate_is_resume_with_certifications_and_billing(parser):
    """Ensure resumes with certification sections and invoicing/finance project keywords are accepted."""
    resume_text = """
    Priya Sharma
    Email: priya.sharma@example.com | Phone: +91 9123456789 | Hyderabad
    GitHub: github.com/priyasharma

    PROFESSIONAL EXPERIENCE
    Senior Backend Engineer at FinTech Solutions (2021 - Present)
    - Engineered tax invoice generation and automated GST/GSTIN reconciliation system handling 50k transactions daily.
    - Integrated payment gateway and bank statement webhook listener.

    SKILLS
    Python, FastAPI, PostgreSQL, Docker, AWS, Redis, Git

    CERTIFICATIONS
    - AWS Certified Solutions Architect - Associate
    - DeepLearning.AI Machine Learning Specialization Certificate

    EDUCATION
    Master of Technology in Computer Science, IIT Hyderabad (2019 - 2021)
    """
    validation = parser.validate_is_resume(resume_text)
    assert validation["is_resume"] is True


def test_validate_is_resume_rejects_standalone_marksheet(parser):
    """Ensure a standalone marksheet transcript with no resume sections is rejected."""
    marksheet_text = """
    CENTRAL BOARD OF SECONDARY EDUCATION
    STATEMENT OF MARKS / MARKS SHEET
    SECONDARY SCHOOL EXAMINATION
    ROLL NO: 1234567    NAME: CANDIDATE
    SUB CODE   SUBJECT NAME      MAX MARKS   THEORY   PRACTICAL   TOTAL MARKS OBTAINED   POSITIONAL GRADE
    041        MATHEMATICS       100         068      020         088                    A1
    086        SCIENCE           100         065      020         085                    A2
    CONTROLLER OF EXAMINATIONS
    """
    validation = parser.validate_is_resume(marksheet_text)
    assert validation["is_resume"] is False
    assert "marksheet" in validation["reason"].lower() or "transcript" in validation["reason"].lower()


def test_validate_is_resume_rejects_standalone_certificate(parser):
    """Ensure an individual course certificate with no resume structure is rejected."""
    cert_text = """
    CERTIFICATE OF COMPLETION
    This is to certify that John Doe has successfully completed the course
    Full Stack Web Development with 80 hours of instruction.
    Certificate of Achievement awarded on October 12, 2023.
    """
    validation = parser.validate_is_resume(cert_text)
    assert validation["is_resume"] is False


def test_validate_is_resume_rejects_standalone_invoice(parser):
    """Ensure a standalone financial invoice is rejected."""
    invoice_text = """
    TAX INVOICE
    Invoice No: INV-2023-0094
    Bill To: ACME Corporation
    Ship To: ACME Warehouse
    Total Amount Due: $1,450.00
    Payment Due Date: 2023-11-30
    Bank Account Statement Ref: 987654321
    """
    validation = parser.validate_is_resume(invoice_text)
    assert validation["is_resume"] is False


