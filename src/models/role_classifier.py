"""
Role Recommendation Classifier.
Predicts suitable career roles and probability distributions based on candidate skill vectors.
"""

import json
import joblib
import numpy as np
from typing import List, Dict, Any, Optional
from src.config import ROLE_CLASSIFIER_PATH, ONTOLOGY_PATH


class RoleClassifier:
    def __init__(self, model_path: str = None, ontology_path: str = None):
        self.model_path = model_path or str(ROLE_CLASSIFIER_PATH)
        self.ontology_path = ontology_path or str(ONTOLOGY_PATH)
        self.artifact: Optional[Dict[str, Any]] = None
        self.model = None
        self.skill_feature_names: List[str] = []
        self.roles_metadata: Dict[str, Any] = {}
        self._load()

    def _load(self):
        with open(self.ontology_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.roles_metadata = data.get("roles", {})
            
        try:
            self.artifact = joblib.load(self.model_path)
            self.model = self.artifact["model"]
            self.skill_feature_names = self.artifact["skill_feature_names"]
        except Exception:
            # Model not trained yet or fallback
            pass

    def predict_roles(self, skill_ids: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Predicts top recommended career roles with probabilities.
        """
        if not self.model or not self.skill_feature_names:
            # Rule-based fallback if model is missing
            return self._heuristic_role_ranking(skill_ids, top_n)
            
        # Encode skills vector
        present_set = set(skill_ids)
        feature_vector = np.array([1.0 if s in present_set else 0.0 for s in self.skill_feature_names]).reshape(1, -1)
        
        # Check if model has predict_proba
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(feature_vector)[0]
            classes = self.model.classes_
            
            # Sort descending
            sorted_indices = np.argsort(probs)[::-1]
            recommendations = []
            
            for idx in sorted_indices[:top_n]:
                role_id = classes[idx]
                prob = float(probs[idx])
                role_meta = self.roles_metadata.get(role_id, {})
                
                recommendations.append({
                    "role_id": role_id,
                    "title": role_meta.get("title", role_id.replace("_", " ").title()),
                    "category": role_meta.get("category", "Technology"),
                    "confidence_score": round(prob * 100, 1),
                    "base_salary_min_lpa": role_meta.get("base_salary_min_lpa", 5.0),
                    "base_salary_max_lpa": role_meta.get("base_salary_max_lpa", 15.0),
                    "description": role_meta.get("description", "")
                })
            return recommendations
        else:
            return self._heuristic_role_ranking(skill_ids, top_n)

    def _heuristic_role_ranking(self, skill_ids: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        scores = []
        user_skills_set = set(skill_ids)
        
        for role_id, meta in self.roles_metadata.items():
            core = set(meta.get("core_skills", []))
            rec = set(meta.get("recommended_skills", []))
            
            core_overlap = len(core.intersection(user_skills_set))
            rec_overlap = len(rec.intersection(user_skills_set))
            
            score = (core_overlap * 2.0 + rec_overlap * 1.0) / max(1, (len(core) * 2.0 + len(rec) * 1.0))
            scores.append((role_id, meta, score))
            
        scores.sort(key=lambda x: x[2], reverse=True)
        
        results = []
        for role_id, meta, score in scores[:top_n]:
            results.append({
                "role_id": role_id,
                "title": meta.get("title", role_id.replace("_", " ").title()),
                "category": meta.get("category", "Technology"),
                "confidence_score": round(min(100.0, score * 100), 1),
                "base_salary_min_lpa": meta.get("base_salary_min_lpa", 5.0),
                "base_salary_max_lpa": meta.get("base_salary_max_lpa", 15.0),
                "description": meta.get("description", "")
            })
        return results
