"""
Market Intelligence & Labor Market Analytics.
Analyzes job market demand distributions, skill frequencies, and salary heatmaps.
"""

from collections import Counter
from typing import Dict, List, Any, Optional
import pandas as pd
from src.config import JOBS_DATASET_PATH, SALARY_DATASET_PATH, ONTOLOGY_PATH
from src.nlp.skill_extractor import SkillExtractor


class MarketAnalyzer:
    def __init__(
        self,
        jobs_path: str = None,
        salary_path: str = None,
        ontology_path: str = None
    ):
        self.jobs_path = jobs_path or str(JOBS_DATASET_PATH)
        self.salary_path = salary_path or str(SALARY_DATASET_PATH)
        self.extractor = SkillExtractor(ontology_path)
        self.df_jobs = pd.DataFrame()
        self.df_salary = pd.DataFrame()
        self._load()

    def _load(self):
        try:
            self.df_jobs = pd.read_csv(self.jobs_path)
            self.df_salary = pd.read_csv(self.salary_path)
        except Exception:
            pass

    def get_top_skills_by_role(self, role_id: Optional[str] = None, top_n: int = 12) -> List[Dict[str, Any]]:
        """Returns the most demanded skills for a specific role or overall market."""
        if self.df_jobs.empty:
            return []

        df_target = self.df_jobs if not role_id or role_id == "all" else self.df_jobs[self.df_jobs["role_id"] == role_id]
        if df_target.empty:
            df_target = self.df_jobs

        all_skills = [
            clean
            for skills_str in df_target["all_skills"].dropna()
            for s in str(skills_str).split(",")
            if (clean := s.strip())
        ]

        total_postings = len(df_target)
        counter = Counter(all_skills)
        
        results = []
        for s_id, count in counter.most_common(top_n):
            name = self.extractor.get_skill_name(s_id)
            pct = round((count / max(1, total_postings)) * 100, 1)
            results.append({
                "skill_id": s_id,
                "skill_name": name,
                "count": count,
                "demand_percentage": pct
            })
        return results

    def get_salary_by_role_distribution(self) -> List[Dict[str, Any]]:
        """Returns average, min, and max salary LPA by role."""
        if self.df_jobs.empty:
            return []

        grouped = self.df_jobs.groupby(["role_id", "role_title", "category"]).agg(
            min_salary=("salary_min_lpa", "mean"),
            max_salary=("salary_max_lpa", "mean"),
            avg_salary=("salary_mid_lpa", "mean"),
            job_count=("job_id", "count")
        ).reset_index()

        grouped = grouped.sort_values(by="avg_salary", ascending=False)
        
        records = []
        for _, row in grouped.iterrows():
            records.append({
                "role_id": row["role_id"],
                "role_title": row["role_title"],
                "category": row["category"],
                "min_lpa": round(row["min_salary"], 1),
                "max_lpa": round(row["max_salary"], 1),
                "avg_lpa": round(row["avg_salary"], 1),
                "job_count": int(row["job_count"])
            })
        return records

    def get_market_overview(self) -> Dict[str, Any]:
        """Returns high-level macro market indicators."""
        if self.df_jobs.empty:
            return {}

        total_jobs = len(self.df_jobs)
        avg_market_salary = round(self.df_jobs["salary_mid_lpa"].mean(), 1)
        top_hiring_locations = self.df_jobs["location"].value_counts().head(5).to_dict()
        top_hiring_companies = self.df_jobs["company"].value_counts().head(5).to_dict()
        
        return {
            "total_openings_analyzed": total_jobs,
            "overall_avg_salary_lpa": avg_market_salary,
            "top_hiring_locations": top_hiring_locations,
            "top_hiring_companies": top_hiring_companies,
            "roles_available_count": self.df_jobs["role_id"].nunique()
        }
