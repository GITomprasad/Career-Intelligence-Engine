"""
Unit tests for the SkillExtractor class.
"""

import json
import pytest
import re
from pathlib import Path

from src.nlp.skill_extractor import SkillExtractor


@pytest.fixture
def mock_ontology_path(tmp_path):
    """Creates a temporary mock ontology file for testing."""
    mock_data = {
        "categories": {
            "prog_lang": {
                "name": "Programming Languages",
                "skills": [
                    {"id": "python", "name": "Python", "aliases": ["python", "python3", "py"]},
                    {"id": "cpp", "name": "C++", "aliases": ["c++", "cpp"]},
                    {"id": "csharp", "name": "C#", "aliases": ["c#", "csharp"]},
                    {"id": "dotnet", "name": ".NET", "aliases": [".net"]},
                    {"id": "c", "name": "C", "aliases": ["c"]},
                    {"id": "r", "name": "R", "aliases": ["r"]},
                    {"id": "ml", "name": "Machine Learning", "aliases": ["machine learning", "ml"]},
                    {"id": "learning", "name": "Learning", "aliases": ["learning"]}
                ]
            }
        },
        "roles": {}
    }

    file_path = tmp_path / "mock_ontology.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    return str(file_path)


@pytest.fixture
def extractor(mock_ontology_path):
    """Returns a SkillExtractor initialized with the mock ontology."""
    return SkillExtractor(ontology_path=mock_ontology_path)


def test_extract_skills_empty(extractor):
    """Test extracting skills from empty text."""
    res_none = extractor.extract_skills(None)
    assert res_none["skill_ids"] == []
    assert res_none["total_count"] == 0

    res_empty = extractor.extract_skills("")
    assert res_empty["skill_ids"] == []
    assert res_empty["total_count"] == 0


def test_extract_skills_none_present(extractor):
    """Test text with no matching skills."""
    res = extractor.extract_skills("I like to eat apples and bananas")
    assert res["skill_ids"] == []
    assert res["total_count"] == 0


def test_extract_skills_basic(extractor):
    """Test basic skill extraction and case insensitivity."""
    res = extractor.extract_skills("I have experience with Python and Py.")
    assert "python" in res["skill_ids"]
    assert res["total_count"] == 1
    assert "Programming Languages" in res["by_category"]
    assert "Python" in res["by_category"]["Programming Languages"]


def test_extract_skills_special_characters(extractor):
    """Test extracting skills with special characters like C++, C#, .NET."""
    res = extractor.extract_skills("Developed in C++ and C# with .NET framework")
    assert "cpp" in res["skill_ids"]
    assert "csharp" in res["skill_ids"]
    assert "dotnet" in res["skill_ids"]
    assert res["total_count"] == 3


def test_extract_skills_single_letters(extractor):
    """Test single letter skill extraction ensuring boundaries are respected."""
    res = extractor.extract_skills("I drive a car, but I code in C and analyze in R.")
    assert "c" in res["skill_ids"]
    assert "r" in res["skill_ids"]
    assert "cpp" not in res["skill_ids"]

    res2 = extractor.extract_skills("crater cart")
    assert "c" not in res2["skill_ids"]
    assert "r" not in res2["skill_ids"]


def test_extract_skills_multi_word(extractor):
    """Test multi-word matching takes precedence over single word."""
    # The aliases are sorted by length, so 'machine learning' should match
    res = extractor.extract_skills("I do Machine Learning")
    assert "ml" in res["skill_ids"]
    assert "learning" not in res["skill_ids"] # 'learning' shouldn't be double-matched if 'machine learning' matches


def test_extract_skills_punctuation(extractor):
    """Test extraction with punctuation nearby."""
    res = extractor.extract_skills("Languages: Python, C++, and C#; also .NET.")
    assert "python" in res["skill_ids"]
    assert "cpp" in res["skill_ids"]
    assert "csharp" in res["skill_ids"]
    assert "dotnet" in res["skill_ids"]


def test_normalize_skill_exact_alias(extractor):
    """Test normalizing a skill from an exact alias."""
    assert extractor.normalize_skill("python3") == "python"
    assert extractor.normalize_skill("c++") == "cpp"
    assert extractor.normalize_skill("Machine Learning") == "ml"

def test_normalize_skill_unknown(extractor):
    """Test normalizing an unknown skill."""
    assert extractor.normalize_skill("unknown_skill") is None


def test_get_skill_name(extractor):
    """Test getting the display name for a skill."""
    assert extractor.get_skill_name("python") == "Python"
    assert extractor.get_skill_name("cpp") == "C++"

    # Test fallback for unknown ID
    assert extractor.get_skill_name("unknown_skill_id") == "Unknown Skill Id"


def test_get_all_skill_ids(extractor):
    """Test getting all loaded skill IDs."""
    ids = extractor.get_all_skill_ids()
    expected_ids = ["c", "cpp", "csharp", "dotnet", "learning", "ml", "python", "r"]
    assert ids == expected_ids
