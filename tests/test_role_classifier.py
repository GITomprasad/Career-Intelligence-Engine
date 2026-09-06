import pytest
from src.models.role_classifier import RoleClassifier
from src.config import ONTOLOGY_PATH

def test_role_classifier_invalid_model_path_fallback():
    """Test that a non-existent model triggers the fallback exception handling block."""
    classifier = RoleClassifier(model_path="non_existent_model.pkl", ontology_path=str(ONTOLOGY_PATH))

    # Check that model attributes are None/empty due to fallback
    assert classifier.artifact is None
    assert classifier.model is None
    assert classifier.skill_feature_names == []

    # Check that predict_roles still works and uses the fallback heuristic ranking
    roles = classifier.predict_roles(["python", "sql"], top_n=2)
    assert len(roles) == 2
    assert "role_id" in roles[0]
    assert "confidence_score" in roles[0]

def test_role_classifier_invalid_file_content_fallback(tmp_path):
    """Test that an invalid (corrupted) model file triggers the fallback exception handling block."""
    invalid_model = tmp_path / "invalid_model.pkl"
    invalid_model.write_text("invalid content")

    classifier = RoleClassifier(model_path=str(invalid_model), ontology_path=str(ONTOLOGY_PATH))

    # Check that model attributes are None/empty due to fallback
    assert classifier.artifact is None
    assert classifier.model is None
    assert classifier.skill_feature_names == []

    # Check that predict_roles still works using fallback logic
    roles = classifier.predict_roles(["python", "sql"])
    assert len(roles) > 0

def test_role_classifier_default_loading():
    """Test that the role classifier can handle standard loading defaults gracefully."""
    classifier = RoleClassifier(ontology_path=str(ONTOLOGY_PATH))
    assert classifier.roles_metadata is not None
    assert len(classifier.roles_metadata) > 0
