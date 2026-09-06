import pytest
from src.nlp.experience_analyzer import ExperienceAnalyzer

@pytest.fixture
def analyzer():
    return ExperienceAnalyzer()

def test_empty_input(analyzer):
    result = analyzer.analyze_experience("")
    assert result["estimated_years"] == 0.0
    assert result["seniority_level"] == "Fresher / Entry Level"
    assert result["experience_bracket"] == "0-1 yrs"
    assert result["action_verb_score"] == 0.0
    assert result["projects_detected"] == 0

def test_explicit_experience(analyzer):
    # Test "X+ years of experience" pattern
    text1 = "I have 5.5+ years of relevant experience in software engineering."
    res1 = analyzer.analyze_experience(text1)
    assert res1["estimated_years"] == 5.5

    # Test "exp: X yrs" pattern
    text2 = "Exp: 3 yrs working with Python and React."
    res2 = analyzer.analyze_experience(text2)
    assert res2["estimated_years"] == 3.0

    # Test "X + years in" pattern
    text3 = "Senior developer with 10 + years in the tech industry."
    res3 = analyzer.analyze_experience(text3)
    assert res3["estimated_years"] == 10.0

def test_fresher_student_cues(analyzer):
    # Student with no internship
    text1 = "I am a fresh graduate seeking entry-level opportunities."
    res1 = analyzer.analyze_experience(text1)
    assert res1["estimated_years"] == 0.0
    assert res1["seniority_level"] == "Fresher / Entry Level"

    # Student with internship
    text2 = "Student aspiring to be a developer. Did a summer intern role."
    res2 = analyzer.analyze_experience(text2)
    assert res2["estimated_years"] == 0.5
    assert res2["seniority_level"] == "Fresher / Entry Level"

def test_fallback_cues(analyzer):
    # No explicit years or fresher cues, but has "intern"
    res1 = analyzer.analyze_experience("Worked as an intern at Tech Corp.")
    assert res1["estimated_years"] == 0.5

    # No explicit years, but has "senior"
    res2 = analyzer.analyze_experience("Senior Developer at Acme Corp.")
    assert res2["estimated_years"] == 5.0

def test_date_intervals(analyzer):
    # Test "Month Year - Month Year"
    text1 = "Software Engineer\nAcme Corp\nJan 2020 - Dec 2022"
    res1 = analyzer.analyze_experience(text1)
    # (2022 - 2020)*12 + (12 - 1) = 24 + 11 = 35 months = 2.9 years
    assert res1["estimated_years"] == 2.9

    # Test "MM/YYYY - Present"
    text2 = f"Backend Developer\n07/2021 - Present"
    res2 = analyzer.analyze_experience(text2)
    # Assuming current year is dynamic in analyzer
    # The analyzer uses datetime.now(), so we can't hardcode the exact result easily
    # We can at least check it's > 0
    assert res2["estimated_years"] > 0.0

def test_year_intervals(analyzer):
    # Test "Year - Year"
    text1 = "Software Developer 2018 - 2022"
    res1 = analyzer.analyze_experience(text1)
    assert res1["estimated_years"] == 4.0

    # Test "Year - Present"
    text2 = "Lead Engineer 2020 - Current"
    res2 = analyzer.analyze_experience(text2)
    assert res2["estimated_years"] >= (analyzer.current_year - 2020)

def test_education_filtering(analyzer):
    # If a date range is clearly education, it shouldn't count towards work experience
    # unless it's in the experience section
    text = """
    EDUCATION
    B.Tech Computer Science
    University of Engineering (2018 - 2022)
    CGPA: 8.5

    WORK EXPERIENCE
    Software Engineer (2022 - 2023)
    """
    res = analyzer.analyze_experience(text)
    # Only 2022 - 2023 should count (1 year)
    assert res["estimated_years"] == 1.0

def test_seniority_levels(analyzer):
    def check_seniority(text, expected_level, expected_bracket):
        res = analyzer.analyze_experience(text)
        assert res["seniority_level"] == expected_level
        assert res["experience_bracket"] == expected_bracket

    check_seniority("Fresher", "Fresher / Entry Level", "0-1 yrs")
    check_seniority("2 years of experience", "Junior Associate", "1-3 yrs")
    check_seniority("5 years of experience", "Mid-Level Specialist", "3-6 yrs")
    check_seniority("8 years of experience", "Senior Engineer / Lead", "6-10 yrs")
    check_seniority("12 years of experience", "Principal / Staff", "10+ yrs")

def test_action_verbs_and_projects(analyzer):
    text = """
    I engineered and deployed a new microservice architecture.
    Optimized the database queries which reduced latency.
        Spearheaded the capstone project:
    Key Project 1: Built a recommendation engine.
    Academic Project: Developed a chat application.
    """
    res = analyzer.analyze_experience(text)

    # engineered, deployed, optimized, reduced, spearheaded, built, developed -> 7 verbs
    assert res["action_verb_score"] > 0.0

    # capstone project, Key Project 1, Academic Project
    assert res["projects_detected"] >= 3
