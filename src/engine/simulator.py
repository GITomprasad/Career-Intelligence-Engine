"""
Interactive Career & Trajectory Simulator.
Evaluates 'What-If' scenarios (adding skills, experience, degrees) on readiness and salary.
"""

from typing import List, Dict, Any, Optional
from src.engine.gap_analyzer import SkillGapAnalyzer
from src.models.salary_predictor import SalaryPredictor
from src.models.matcher import JobMatcher


class CareerSimulator:
    def __init__(self, ontology_path: str = None):
        self.gap_analyzer = SkillGapAnalyzer(ontology_path)
        self.salary_predictor = SalaryPredictor(ontology_path=ontology_path)
        self.matcher = JobMatcher()

    def simulate(
        self,
        current_profile: Dict[str, Any],
        target_role_id: str,
        additional_skills: List[str],
        additional_experience_years: float = 0.0,
        simulated_education: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs a What-If simulation comparing the candidate's current state with simulated additions.
        """
        current_skills = list(current_profile.get("skill_ids", []))
        current_exp = float(current_profile.get("experience_years", 0.0))
        current_edu = current_profile.get("education", {}).get("degree", "Bachelor's Degree")
        
        # 1. Baseline Calculations
        base_gap = self.gap_analyzer.analyze_gap(current_skills, target_role_id)
        base_readiness = base_gap.get("readiness_score", 50.0)
        
        base_salary_info = self.salary_predictor.predict_salary(
            role_id=target_role_id,
            experience_years=current_exp,
            skill_count=len(current_skills),
            education=current_edu
        )
        base_salary_lpa = base_salary_info["predicted_lpa"]

        # 2. Simulated State Calculations
        sim_skills = list(set(current_skills + additional_skills))
        sim_exp = current_exp + additional_experience_years
        sim_edu = simulated_education or current_edu

        sim_gap = self.gap_analyzer.analyze_gap(sim_skills, target_role_id)
        sim_readiness = sim_gap.get("readiness_score", base_readiness)

        sim_salary_info = self.salary_predictor.predict_salary(
            role_id=target_role_id,
            experience_years=sim_exp,
            skill_count=len(sim_skills),
            education=sim_edu
        )
        sim_salary_lpa = sim_salary_info["predicted_lpa"]

        # 3. Compute Deltas & Insights
        readiness_delta = round(sim_readiness - base_readiness, 1)
        salary_delta_lpa = round(sim_salary_lpa - base_salary_lpa, 2)
        salary_delta_pct = round((salary_delta_lpa / max(1.0, base_salary_lpa)) * 100, 1)

        # Build simulated profile for job match estimation
        sim_profile = dict(current_profile)
        sim_profile["skill_ids"] = sim_skills
        sim_profile["experience_years"] = sim_exp
        
        sim_matches = self.matcher.match_jobs(sim_profile, target_role_id=target_role_id, top_n=20)
        high_match_jobs_count = sum(1 for j in sim_matches if j["match_score"] >= 75.0)

        return {
            "target_role_id": target_role_id,
            "target_role_title": base_gap.get("role_title", target_role_id),
            "baseline": {
                "skills_count": len(current_skills),
                "experience_years": current_exp,
                "readiness_score": base_readiness,
                "predicted_salary_lpa": base_salary_lpa,
                "formatted_salary": f"₹{base_salary_lpa}L / yr"
            },
            "simulated": {
                "skills_count": len(sim_skills),
                "added_skills": additional_skills,
                "experience_years": sim_exp,
                "readiness_score": sim_readiness,
                "predicted_salary_lpa": sim_salary_lpa,
                "formatted_salary": f"₹{sim_salary_lpa}L / yr",
                "high_match_jobs_unlocked": high_match_jobs_count
            },
            "impact": {
                "readiness_delta_pct": readiness_delta,
                "salary_increase_lpa": salary_delta_lpa,
                "salary_growth_pct": salary_delta_pct,
                "summary": (
                    f"Adding {len(additional_skills)} skills boosts your {base_gap.get('role_title', 'Role')} "
                    f"readiness by +{readiness_delta}% (from {base_readiness}% to {sim_readiness}%) "
                    f"and increases projected market value by +₹{salary_delta_lpa}L/yr (+{salary_delta_pct}%)."
                )
            }
        }
