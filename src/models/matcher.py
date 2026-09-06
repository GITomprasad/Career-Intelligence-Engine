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
        indices = list(range(len(df_filtered)))

        for idx, (_, row) in enumerate(df_filtered.iterrows()):
            req_skills = set(str(row["required_skills"]).split(",")) if pd.notna(row["required_skills"]) else set()
            pref_skills = set(str(row["preferred_skills"]).split(",")) if pd.notna(row["preferred_skills"]) else set()
            
            # 1. Skill Match Score (50%)
            matched_req = user_skills.intersection(req_skills)
            matched_pref = user_skills.intersection(pref_skills)
            missing_req = req_skills - user_skills
            
            req_ratio = len(matched_req) / max(1, len(req_skills))
            pref_ratio = len(matched_pref) / max(1, len(pref_skills)) if pref_skills else 1.0
            skill_score = (req_ratio * 0.85 + pref_ratio * 0.15) * 100.0
            
            # 2. NLP Semantic Score (25%)
            nlp_score = float(nlp_scores[idx]) if idx < len(nlp_scores) else 50.0
            
            # 3. Experience Alignment Score (15%)
            min_exp = float(row["min_experience_years"])
            max_exp = float(row["max_experience_years"])
            if min_exp <= user_exp <= max_exp + 2:
                exp_score = 100.0
            elif user_exp < min_exp:
                deficit = min_exp - user_exp
                exp_score = max(20.0, 100.0 - (deficit * 30.0))
            else:
                # Overqualified
                exp_score = 85.0
                
            # 4. Education & Certification Score (10%)
            edu_score = 80.0
            if "Master" in user_edu or "Ph.D" in user_edu:
                edu_score = 100.0
            elif "Bachelor" in user_edu:
                edu_score = 90.0

            # Composite weighted match
            total_score = (
                (skill_score * WEIGHT_SKILLS) +
                (nlp_score * WEIGHT_NLP_SIMILARITY) +
                (exp_score * WEIGHT_EXPERIENCE) +
                (edu_score * WEIGHT_EDUCATION)
            )
            
            total_score = min(98.5, max(15.0, round(total_score, 1)))

            if total_score >= min_score:
                matches.append({
                    "job_id": row["job_id"],
                    "title": row["title"],
                    "role_id": row["role_id"],
                    "role_title": row["role_title"],
                    "category": row["category"],
                    "company": row["company"],
                    "company_type": row["company_type"],
                    "company_tier": row["company_tier"],
                    "location": row["location"],
                    "salary_min_lpa": row["salary_min_lpa"],
                    "salary_max_lpa": row["salary_max_lpa"],
                    "salary_formatted": f"₹{row['salary_min_lpa']}L - ₹{row['salary_max_lpa']}L / yr",
                    "min_experience_years": row["min_experience_years"],
                    "match_score": total_score,
                    "score_breakdown": {
                        "skill_score": round(skill_score, 1),
                        "nlp_score": round(nlp_score, 1),
                        "exp_score": round(exp_score, 1),
                        "edu_score": round(edu_score, 1)
                    },
                    "matched_skills": [s.replace("_", " ").title() for s in sorted(list(matched_req))],
                    "missing_skills": [s.replace("_", " ").title() for s in sorted(list(missing_req))],
                    "preferred_matched": [s.replace("_", " ").title() for s in sorted(list(matched_pref))],
                    "description": row["description"]
                })

        # Sort matches by match_score descending
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:top_n]
