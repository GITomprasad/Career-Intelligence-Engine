"""
Explainable AI (XAI) Engine.
Provides human-interpretable factor breakdowns and feature attribution for career match scores.
"""

from typing import Dict, Any


class ExplainabilityEngine:
    def explain_match_score(
        self,
        candidate_profile: Dict[str, Any],
        target_role: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        match_breakdown: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deconstructs the candidate's match score into positive drivers and score deductions.
        """
        readiness = gap_analysis.get("readiness_score", 50.0)
        strong_skills = gap_analysis.get("strong_skills", [])
        missing_skills = gap_analysis.get("missing_skills", [])
        exp_years = candidate_profile.get("experience_years", 0.0)
        
        # 1. Positive Drivers (Skills adding points)
        positive_drivers = []
        for s in strong_skills[:5]:
            weight = 12.0 if s.get("type") == "Core Requirement" else 6.0
            positive_drivers.append({
                "factor": f"Mastered {s['name']}",
                "impact": f"+{weight:.1f}%",
                "category": s.get("category", "Technical"),
                "detail": f"Directly satisfies a {s.get('type', 'core')} requirement for {target_role.get('title', 'role')}."
            })
            
        if exp_years >= 1.0:
            exp_contrib = min(15.0, exp_years * 3.5)
            positive_drivers.append({
                "factor": f"{exp_years} Years Experience Alignment",
                "impact": f"+{exp_contrib:.1f}%",
                "category": "Experience",
                "detail": f"Candidate demonstrates {candidate_profile.get('seniority_level', 'relevant')} career tenure."
            })

        # 2. Negative Deductions (Gaps lowering score)
        deductions = []
        for s in missing_skills[:4]:
            penalty = 10.0 if s.get("priority") == "Critical Priority" else 5.0
            deductions.append({
                "factor": f"Missing {s['name']}",
                "impact": f"-{penalty:.1f}%",
                "category": s.get("category", "Technical Gap"),
                "detail": f"{s['name']} is heavily prioritized by hiring managers for this profile."
            })
            
        if exp_years < 1.0:
            deductions.append({
                "factor": "Entry-Level / Fresher Experience Profile",
                "impact": "-5.0%",
                "category": "Experience Tenure",
                "detail": "Most mid-level postings require 2+ years of production experience."
            })

        # 3. Key Takeaway & Highest ROI Next Step
        top_roi_skill = missing_skills[0]["name"] if missing_skills else "Cloud Architecture / MLOps"
        takeaway = (
            f"Your score of {readiness}% is primarily propelled by strong foundations in "
            f"{', '.join([s['name'] for s in strong_skills[:3]]) if strong_skills else 'core competencies'}. "
            f"Adding '{top_roi_skill}' to your skillset is the fastest route to push your readiness past 85%."
        )

        return {
            "overall_score": readiness,
            "summary_verdict": "Highly Competitive" if readiness >= 80 else ("Job-Ready with Minor Gaps" if readiness >= 60 else "Foundational Stage"),
            "positive_drivers": positive_drivers,
            "deductions": deductions,
            "key_takeaway": takeaway,
            "highest_roi_skill": top_roi_skill
        }
