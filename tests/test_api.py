"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_resume_parse_text(client):
    payload = {
        "text": "OM PRAKASH SAHU\nEmail: omprakash@example.com\nSkills: Python, SQL, Machine Learning, Power BI.",
        "filename": "test_resume.txt"
    }
    response = client.post("/api/resume/parse-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "python" in data["profile"]["skill_ids"]
    assert len(data["recommended_roles"]) > 0


def test_api_gap_analysis(client):
    payload = {
        "skills": ["python", "sql", "pandas"],
        "target_role_id": "data_scientist"
    }
    response = client.post("/api/skills/gap-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "readiness_score" in data
    assert "strong_skills" in data


def test_api_salary_predict(client):
    payload = {
        "role_id": "data_analyst",
        "experience_years": 2.0,
        "skill_count": 6,
        "education": "Bachelor's Degree",
        "location_tier": "Tier-1",
        "company_tier": "Tier-1"
    }
    response = client.post("/api/salary/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_lpa" in data
    assert "formatted_range" in data


def test_api_market_trends(client):
    response = client.get("/api/market/trends?role_id=data_scientist")
    assert response.status_code == 200
    data = response.json()
    assert "top_demanded_skills" in data
    assert "salary_by_role" in data


def test_api_ats_score(client):
    payload = {
        "profile": {
            "name": "Alex Mercer",
            "email": "alex.mercer@email.com",
            "phone": "+91 9876543210",
            "location": "Bangalore",
            "linkedin": "linkedin.com/in/alexmercer",
            "github": "github.com/alexmercer",
            "skills": ["Python", "SQL", "Pandas", "Scikit-Learn"],
            "skill_ids": ["python", "sql", "pandas", "scikit_learn"],
            "experience_years": 2.5,
            "seniority_level": "Junior Associate",
            "education": {"degree": "Bachelor's Degree", "major": "Computer Science"}
        },
        "target_role_id": "data_scientist",
        "raw_text": "Alex Mercer\nEmail: alex.mercer@email.com\nPhone: +91 9876543210\nSkills: Python, SQL, Pandas, Scikit-Learn\nExperience: 2.5 years of experience improving models by 15%."
    }
    response = client.post("/api/ats/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "keyword" in data
    assert "format" in data
    assert "experience" in data
    assert "verdict" in data
    assert "issues" in data
    assert "wins" in data
    assert 0 <= data["total"] <= 100


def test_api_resume_parse_file_success(client):
    file_content = b"John Doe\nEmail: john.doe@email.com\nSkills: Python, SQL, Machine Learning\nExperience: 3 years building ML models."
    files = {"file": ("resume.txt", file_content, "text/plain")}
    response = client.post("/api/resume/parse-file", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "python" in data["profile"]["skill_ids"]


def test_api_resume_parse_file_size_exceeded(client):
    # Simulate a file larger than 10MB (10.5 MB)
    large_content = b"x" * (11 * 1024 * 1024)
    files = {"file": ("large_resume.pdf", large_content, "application/pdf")}
    response = client.post("/api/resume/parse-file", files=files)
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()


