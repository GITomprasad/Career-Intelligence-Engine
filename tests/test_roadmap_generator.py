import pytest
from src.engine.roadmap_generator import RoadmapGenerator


@pytest.fixture
def roadmap_generator():
    return RoadmapGenerator()


def test_generate_roadmap_empty_gap(roadmap_generator):
    """
    Test roadmap generation when there are no missing or improvement skills.
    """
    gap_analysis = {
        "missing_skills": [],
        "improvement_skills": [],
        "role_title": "Data Scientist",
        "readiness_score": 90.0
    }

    result = roadmap_generator.generate_roadmap(gap_analysis)

    assert result["status"] == "All Core Skills Mastered"
    assert "Congratulations" in result["message"]
    assert result["total_estimated_weeks"] == 2
    assert result["phases"] == []


def test_generate_roadmap_with_gaps(roadmap_generator):
    """
    Test roadmap generation with a mix of missing and improvement skills,
    ensuring correct phase categorization and output structure.
    """
    gap_analysis = {
        "missing_skills": [
            {"skill_id": "python", "name": "Python", "priority": "High Priority", "status": "Missing"},
            {"skill_id": "machine_learning", "name": "Machine Learning", "priority": "Medium Priority", "status": "Missing"}
        ],
        "improvement_skills": [
            {"skill_id": "docker", "name": "Docker", "priority": "Low Priority", "status": "Needs Improvement"},
            {"skill_id": "unknown_skill", "name": "Unknown Skill", "priority": "Low Priority", "status": "Needs Improvement"}
        ],
        "role_title": "Machine Learning Engineer",
        "readiness_score": 50.0
    }

    result = roadmap_generator.generate_roadmap(gap_analysis)

    assert result["target_role"] == "Machine Learning Engineer"
    assert result["current_readiness"] == 50.0
    assert result["projected_readiness_after_completion"] == 96.0
    assert result["phases_count"] == 4  # Foundations, ML/Core, DevOps/Cloud, and Capstone
    assert len(result["phases"]) == 4

    # Phase 1: Foundations
    phase1 = result["phases"][0]
    assert phase1["phase_number"] == 1
    assert "Foundations" in phase1["title"]
    assert len(phase1["skills"]) == 1
    assert phase1["skills"][0]["skill_id"] == "python"

    # Phase 2: Domain Competencies (Core)
    phase2 = result["phases"][1]
    assert phase2["phase_number"] == 2
    assert "Domain Competencies" in phase2["title"]
    assert len(phase2["skills"]) == 2
    skill_ids_phase2 = [s["skill_id"] for s in phase2["skills"]]
    assert "machine_learning" in skill_ids_phase2
    assert "unknown_skill" in skill_ids_phase2 # Fallback to Phase 2 for unknown skills

    # Phase 3: Production Engineering & Cloud/DevOps
    phase3 = result["phases"][2]
    assert phase3["phase_number"] == 3
    assert "Production Engineering" in phase3["title"]
    assert len(phase3["skills"]) == 1
    assert phase3["skills"][0]["skill_id"] == "docker"

    # Phase 4: Capstone
    phase4 = result["phases"][3]
    assert phase4["phase_number"] == 4
    assert "Capstone" in phase4["title"]
    assert len(phase4["skills"]) == 1
    assert phase4["skills"][0]["skill_id"] == "portfolio_capstone"
    assert phase4["duration_weeks"] == 2

    # Check total estimated weeks
    total_weeks = sum(p["duration_weeks"] for p in result["phases"])
    assert result["total_estimated_weeks"] == total_weeks


def test_generate_roadmap_skill_data_enrichment(roadmap_generator):
    """
    Test that skills are correctly enriched with data from the knowledge base (skill_curriculum).
    """
    gap_analysis = {
        "missing_skills": [
            {"skill_id": "sql", "name": "SQL", "priority": "High Priority", "status": "Missing"}
        ],
        "improvement_skills": [],
        "role_title": "Data Analyst",
        "readiness_score": 75.0
    }

    result = roadmap_generator.generate_roadmap(gap_analysis)

    # SQL should be in Phase 1
    sql_skill = result["phases"][0]["skills"][0]

    assert sql_skill["skill_id"] == "sql"
    assert sql_skill["name"] == "SQL"
    assert sql_skill["status"] == "Missing"
    assert sql_skill["priority"] == "High Priority"
    assert sql_skill["category"] == "General" # item doesn't have a category, so it falls back to General, though skill_curriculum has "category": "Foundations"
    assert sql_skill["estimated_hours"] == 15
    assert len(sql_skill["resources"]) == 3
    assert "Design a relational schema" in sql_skill["milestone_project"]
    assert "Window functions" in sql_skill["interview_focus"]
