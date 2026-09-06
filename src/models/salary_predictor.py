"""
Salary Prediction Regressor.
Predicts market compensation ranges in LPA (Lakhs Per Annum) based on multi-factor features.
"""

import json
import skops.io as sio
import joblib
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from src.config import SALARY_REGRESSOR_PATH, ONTOLOGY_PATH


class SalaryPredictor:
    def __init__(self, model_path: str = None, ontology_path: str = None):
        self.model_path = model_path or str(SALARY_REGRESSOR_PATH)
        self.ontology_path = ontology_path or str(ONTOLOGY_PATH)
        self.artifact: Optional[Dict[str, Any]] = None
        self.model = None
        self.ohe = None
        self.scaler = None
        self.roles_metadata = {}
        self._load()

    def _load(self):
        with open(self.ontology_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.roles_metadata = data.get("roles", {})

        try:
            self.artifact = sio.load(self.model_path)
            self.model = self.artifact["model"]
            self.ohe = self.artifact["one_hot_encoder"]
            self.scaler = self.artifact["scaler"]
        except (FileNotFoundError, OSError, KeyError, pickle.UnpicklingError, EOFError):
            pass

    def predict_salary(
        self,
        role_id: str,
        experience_years: float,
        skill_count: int,
        education: str = "B.Tech / B.E. Computer Science",
        location_tier: str = "Tier-1",
        company_tier: str = "Tier-1"
    ) -> Dict[str, Any]:
        """
        Predicts expected salary range in LPA.
        """
        if self.model and self.ohe and self.scaler:
            try:
                # Prepare single-row DataFrame
                df_input = pd.DataFrame([{
                    "role_id": role_id,
                    "education": education,
                    "location_tier": location_tier,
                    "company_tier": company_tier
                }])
                X_cat = self.ohe.transform(df_input)
                X_num = np.array([[experience_years, skill_count]])
                X_num_scaled = self.scaler.transform(X_num)
                
                X = np.hstack([X_cat, X_num_scaled])
                pred_median = float(self.model.predict(X)[0])
                
                # Ensure within sane bounds
                pred_median = max(3.5, round(pred_median, 2))
                lower_bound = round(max(3.0, pred_median * 0.85), 2)
                upper_bound = round(pred_median * 1.18, 2)
                
                return {
                    "predicted_lpa": pred_median,
                    "min_lpa": lower_bound,
                    "max_lpa": upper_bound,
                    "currency": "INR (Lakhs / Year)",
                    "formatted_range": f"₹{lower_bound}L - ₹{upper_bound}L / yr",
                    "formatted_median": f"₹{pred_median}L / yr",
                    "model_used": self.artifact.get("model_name", "Gradient Boosting Regressor")
                }
            except (ValueError, TypeError, KeyError, IndexError, AttributeError):
                pass

        # Heuristic fallback if model not loaded
        role_meta = self.roles_metadata.get(role_id, {})
        base_min = role_meta.get("base_salary_min_lpa", 5.0)
        base_max = role_meta.get("base_salary_max_lpa", 14.0)
        mult = role_meta.get("experience_multiplier", 1.5)
        
        growth = (experience_years ** 0.85) * (mult - 1.0) * 2.0
        est_median = round(base_min + (base_max - base_min) * 0.35 + growth + (skill_count * 0.2), 2)
        lower_bound = round(est_median * 0.85, 2)
        upper_bound = round(est_median * 1.20, 2)
        
        return {
            "predicted_lpa": est_median,
            "min_lpa": lower_bound,
            "max_lpa": upper_bound,
            "currency": "INR (Lakhs / Year)",
            "formatted_range": f"₹{lower_bound}L - ₹{upper_bound}L / yr",
            "formatted_median": f"₹{est_median}L / yr",
            "model_used": "Heuristic Benchmark Model"
        }
