"""
Unit tests for Role Classifier.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.models.role_classifier import RoleClassifier

@pytest.fixture
def classifier():
    return RoleClassifier()

def test_predict_roles_with_model(classifier):
    # Test with actual model if available
    if not classifier.model:
        pytest.skip("Trained model not found")

    skill_ids = ["python", "sql", "pandas", "scikit_learn"]
    results = classifier.predict_roles(skill_ids, top_n=3)

    assert isinstance(results, list)
    assert len(results) <= 3
    if len(results) > 0:
        for res in results:
            assert "role_id" in res
            assert "title" in res
            assert "confidence_score" in res
            assert "base_salary_min_lpa" in res

def test_predict_roles_fallback_no_model():
    # Initialize with an invalid model path to force fallback
    fallback_classifier = RoleClassifier(model_path="invalid_path.pkl")
    assert fallback_classifier.model is None

    skill_ids = ["python", "sql", "pandas", "scikit_learn"]
    results = fallback_classifier.predict_roles(skill_ids, top_n=2)

    assert isinstance(results, list)
    assert len(results) <= 2
    if len(results) > 0:
        for res in results:
            assert "role_id" in res
            assert "title" in res
            assert "confidence_score" in res
            assert "base_salary_min_lpa" in res
            assert "category" in res

@patch("src.models.role_classifier.joblib.load")
def test_predict_roles_model_no_predict_proba(mock_load):
    # Mock joblib to return a model without predict_proba
    mock_model = MagicMock()
    del mock_model.predict_proba

    mock_load.return_value = {
        "model": mock_model,
        "skill_feature_names": ["python", "sql"]
    }

    classifier = RoleClassifier(model_path="dummy.pkl")
    assert classifier.model is mock_model
    assert not hasattr(classifier.model, "predict_proba")

    skill_ids = ["python", "sql"]
    results = classifier.predict_roles(skill_ids, top_n=3)

    assert isinstance(results, list)
    assert len(results) <= 3
    if len(results) > 0:
        for res in results:
            assert "role_id" in res
            assert "title" in res
            assert "confidence_score" in res
