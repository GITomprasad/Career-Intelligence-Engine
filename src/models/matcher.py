"""
Hybrid Multi-Factor Job Matching Engine.
Calculates compatibility using Skill Overlap, TF-IDF Cosine Similarity, and Experience Alignment.
"""

import joblib
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

from src.config import (
    JOBS_DATASET_PATH,
    TFIDF_MATCHER_PATH,
    WEIGHT_SKILLS,
    WEIGHT_NLP_SIMILARITY,
    WEIGHT_EXPERIENCE,
    WEIGHT_EDUCATION
)


class JobMatcher:
    def __init__(self, jobs_path: str = None, tfidf_path: str = None):
        self.jobs_path = jobs_path or str(JOBS_DATASET_PATH)
        self.tfidf_path = tfidf_path or str(TFIDF_MATCHER_PATH)
        self.df_jobs = pd.DataFrame()
        self.tfidf_artifact = None
        self._load()

    def _load(self):
        try:
            self.df_jobs = pd.read_csv(self.jobs_path)
        except Exception as e:
            logger.error(f"Failed to load jobs data from {self.jobs_path}: {e}")

        try:
            self.tfidf_artifact = joblib.load(self.tfidf_path)
        except Exception as e:
            logger.error(f"Failed to load TF-IDF model from {self.tfidf_path}: {e}")

    def match_jobs(
        self,
        candidate_profile: Dict[str, Any],
        target_role_id: Optional[str] = None,
        top_n: int = 15,
        min_score: float = 30.0
    ) -> List[Dict[str, Any]]:
        """
        Matches a candidate profile against the job market database.
        """
        if self.df_jobs.empty:
            return []

        user_skills = set(candidate_profile.get("skill_ids", []))
        user_exp = float(candidate_profile.get("experience_years", 0.0))
        user_edu = candidate_profile.get("education", {}).get("degree", "")
        raw_text = candidate_profile.get("raw_text", "") or " ".join(candidate_profile.get("skills", []))

        # Filter by target role if specified
        if target_role_id and target_role_id != "all":
            df_filtered = self.df_jobs[self.df_jobs["role_id"] == target_role_id].copy()
        else:
            df_filtered = self.df_jobs.copy()

        if df_filtered.empty:
            df_filtered = self.df_jobs.copy()

        # Compute TF-IDF NLP Similarity if vectorizer is available
        nlp_scores = np.zeros(len(df_filtered))
        if self.tfidf_artifact and raw_text:
            try:
                vectorizer = self.tfidf_artifact["vectorizer"]
                user_vec = vectorizer.transform([raw_text])
                
                # Transform filtered jobs text
                job_corpus = (
                    df_filtered["role_title"] + " " +
                    df_filtered["description"] + " " +
                    df_filtered["all_skills"].apply(lambda s: " ".join(str(s).split(",")))
                ).tolist()
                jobs_mat = vectorizer.transform(job_corpus)
                
                sims = cosine_similarity(user_vec, jobs_mat)[0]
                nlp_scores = sims * 100.0
            except Exception as e:
                logger.error(f"Failed to compute NLP scores: {e}")
                nlp_scores = np.zeros(len(df_filtered))

        matches = []
        n_rows = len(df_filtered)
        if n_rows == 0:
            return []

        # 4. Education & Certification Score (10%) (Constant for user)
        edu_score = 80.0
        if "Master" in user_edu or "Ph.D" in user_edu:
            edu_score = 100.0
        elif "Bachelor" in user_edu:
            edu_score = 90.0

        # 3. Experience Alignment Score (15%)
        min_exp_arr = df_filtered["min_experience_years"].to_numpy().astype(float)
        max_exp_arr = df_filtered["max_experience_years"].to_numpy().astype(float)

        deficit = min_exp_arr - user_exp
        exp_score_arr = np.full(n_rows, 100.0)

        mask_under = user_exp < min_exp_arr
        mask_over = user_exp > (max_exp_arr + 2)

        exp_score_arr[mask_under] = np.maximum(20.0, 100.0 - (deficit[mask_under] * 30.0))
        exp_score_arr[mask_over] = 85.0

        # 1. Skill Match Score (50%)
        req_skills_series = df_filtered["required_skills"].to_numpy()
        pref_skills_series = df_filtered["preferred_skills"].to_numpy()

        def process_skills(req_val, pref_val):
            req_set = set(str(req_val).split(",")) if pd.notna(req_val) else set()
            pref_set = set(str(pref_val).split(",")) if pd.notna(pref_val) else set()
            
            matched_req = user_skills.intersection(req_set)
            matched_pref = user_skills.intersection(pref_set)
            missing_req = req_set - user_skills
            
            req_ratio = len(matched_req) / max(1, len(req_set))
            pref_ratio = len(matched_pref) / max(1, len(pref_set)) if pref_set else 1.0
            
            skill_score = (req_ratio * 0.85 + pref_ratio * 0.15) * 100.0
            return skill_score, matched_req, matched_pref, missing_req
            
        skill_results = [process_skills(req, pref) for req, pref in zip(req_skills_series, pref_skills_series)]
        skill_score_arr = np.array([r[0] for r in skill_results])

        # 2. NLP Semantic Score (25%) is already in nlp_scores
        # Make sure nlp_scores length matches
        if len(nlp_scores) < n_rows:
            padded_nlp = np.full(n_rows, 50.0)
            padded_nlp[:len(nlp_scores)] = nlp_scores
            nlp_scores = padded_nlp
        elif len(nlp_scores) > n_rows:
            nlp_scores = nlp_scores[:n_rows]
            
        # Composite weighted match
        total_scores = (
            (skill_score_arr * WEIGHT_SKILLS) +
            (nlp_scores * WEIGHT_NLP_SIMILARITY) +
            (exp_score_arr * WEIGHT_EXPERIENCE) +
            (edu_score * WEIGHT_EDUCATION)
        )
        total_scores = np.clip(np.round(total_scores, 1), 15.0, 98.5)

        valid_indices = np.where(total_scores >= min_score)[0]

        if len(valid_indices) > 0:
            valid_scores = total_scores[valid_indices]
            # Sort indices by score descending, take top_n
            sort_order = np.argsort(-valid_scores)[:top_n]
            top_indices = valid_indices[sort_order]

            df_top = df_filtered.iloc[top_indices]
            top_total_scores = total_scores[top_indices]
            top_skill_scores = skill_score_arr[top_indices]
            top_nlp_scores = nlp_scores[top_indices]
            top_exp_scores = exp_score_arr[top_indices]

            for i, row in enumerate(df_top.itertuples()):
                orig_idx = top_indices[i]
                matched_req = skill_results[orig_idx][1]
                matched_pref = skill_results[orig_idx][2]
                missing_req = skill_results[orig_idx][3]

                matches.append({
                    "job_id": row.job_id,
                    "title": row.title,
                    "role_id": row.role_id,
                    "role_title": row.role_title,
                    "category": row.category,
                    "company": row.company,
                    "company_type": row.company_type,
                    "company_tier": row.company_tier,
                    "location": row.location,
                    "salary_min_lpa": row.salary_min_lpa,
                    "salary_max_lpa": row.salary_max_lpa,
                    "salary_formatted": f"₹{row.salary_min_lpa}L - ₹{row.salary_max_lpa}L / yr",
                    "min_experience_years": row.min_experience_years,
                    "match_score": float(top_total_scores[i]),
                    "score_breakdown": {
                        "skill_score": round(float(top_skill_scores[i]), 1),
                        "nlp_score": round(float(top_nlp_scores[i]), 1),
                        "exp_score": round(float(top_exp_scores[i]), 1),
                        "edu_score": round(edu_score, 1)
                    },
                    "matched_skills": [s.replace("_", " ").title() for s in sorted(list(matched_req))],
                    "missing_skills": [s.replace("_", " ").title() for s in sorted(list(missing_req))],
                    "preferred_matched": [s.replace("_", " ").title() for s in sorted(list(matched_pref))],
                    "description": row.description
                })

        return matches
