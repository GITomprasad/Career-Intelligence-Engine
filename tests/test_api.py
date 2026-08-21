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
