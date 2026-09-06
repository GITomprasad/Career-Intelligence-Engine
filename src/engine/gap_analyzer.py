"""
Skill Gap Analyzer.
Performs granular skill gap analysis, calculates role readiness, and assigns market demand priority.
"""

import json
from typing import Dict, List, Any
from src.config import ONTOLOGY_PATH
from src.nlp.skill_extractor import SkillExtractor


class SkillGapAnalyzer:
    def __init__(self, ontology_path: str = None):
        self.ontology_path = ontology_path or str(ONTOLOGY_PATH)
        self.extractor = SkillExtractor(self.ontology_path)
        self.roles: Dict[str, Any] = {}
        self.categories: Dict[str, Any] = {}
        self._load_ontology()

    def _load_ontology(self):
        with open(self.ontology_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.roles = data.get("roles", {})
            self.categories = data.get("categories", {})

    def analyze_gap(self, candidate_skills: List[str], target_role_id: str) -> Dict[str, Any]:
        """
        Analyzes candidate skills against target role requirements.
        """
        role_meta = self.roles.get(target_role_id)
        if not role_meta:
            return {
                "error": f"Role '{target_role_id}' not found in ontology.",
                "readiness_score": 0.0,
                "strong_skills": [],
                "improvement_skills": [],
                "missing_skills": []
            }

        # Normalize candidate skills to canonical IDs
        candidate_ids = set()
        for s in candidate_skills:
            normalized = self.extractor.normalize_skill(s)
            if normalized:
                candidate_ids.add(normalized)
            else:
                candidate_ids.add(s.strip().lower().replace(" ", "_"))

        core_skills = role_meta.get("core_skills", [])
        rec_skills = role_meta.get("recommended_skills", [])
        opt_skills = role_meta.get("optional_skills", [])

        # Categorize
        strong = []
        needs_improvement = []
        missing = []

        # Find categories candidate is active in
        candidate_active_categories = set()
        for s_id in candidate_ids:
            s_info = self.extractor.skill_map.get(s_id)
            if s_info:
                candidate_active_categories.add(s_info["category_id"])

        # Evaluate Core Skills
        for s_id in core_skills:
            s_name = self.extractor.get_skill_name(s_id)
            s_info = self.extractor.skill_map.get(s_id, {})
            cat_id = s_info.get("category_id", "")
            
            if s_id in candidate_ids:
                strong.append({
                    "skill_id": s_id,
                    "name": s_name,
                    "type": "Core Requirement",
                    "status": "Strong",
                    "category": s_info.get("category_name", "General"),
                    "priority": "Mastered"
                })
            elif cat_id and cat_id in candidate_active_categories:
                # Candidate has experience in this domain but missing this specific tool
                needs_improvement.append({
                    "skill_id": s_id,
                    "name": s_name,
                    "type": "Core Requirement",
                    "status": "Needs Improvement",
                    "category": s_info.get("category_name", "General"),
                    "priority": "High Priority",
                    "reason": f"You have background in {s_info.get('category_name', 'this domain')}, but need proficiency in {s_name}."
                })
            else:
                missing.append({
                    "skill_id": s_id,
                    "name": s_name,
                    "type": "Core Requirement",
                    "status": "Missing",
                    "category": s_info.get("category_name", "General"),
                    "priority": "Critical Priority",
                    "market_demand": "High (Demanded in 85%+ Job Postings)"
                })

        # Evaluate Recommended Skills
        for s_id in rec_skills:
            s_name = self.extractor.get_skill_name(s_id)
            s_info = self.extractor.skill_map.get(s_id, {})
            cat_id = s_info.get("category_id", "")
            
            if s_id in candidate_ids:
                strong.append({
                    "skill_id": s_id,
                    "name": s_name,
                    "type": "Recommended",
                    "status": "Strong",
                    "category": s_info.get("category_name", "General"),
                    "priority": "Mastered"
                })
            elif cat_id and cat_id in candidate_active_categories:
                needs_improvement.append({
                    "skill_id": s_id,
                    "name": s_name,
                    "type": "Recommended",
                    "status": "Needs Improvement",
                    "category": s_info.get("category_name", "General"),
                    "priority": "Medium Priority",
                    "reason": f"Secondary requirement in {s_info.get('category_name', 'domain')} to boost competitiveness."
                })
            else:
                missing.append({
                    "skill_id": s_id,
                    "name": s_name,
                    "type": "Recommended",
                    "status": "Missing",
                    "category": s_info.get("category_name", "General"),
                    "priority": "Medium Priority",
                    "market_demand": "Moderate (Demanded in 60%+ Job Postings)"
                })

        # Calculate Readiness Score
        total_core = len(core_skills)
        total_rec = len(rec_skills)
        matched_core_count = sum(1 for s in strong if s["type"] == "Core Requirement")
        matched_rec_count = sum(1 for s in strong if s["type"] == "Recommended")
        improvement_count = len(needs_improvement)

        # Weighted calculation
        raw_score = (
            (matched_core_count * 2.0) +
            (matched_rec_count * 1.0) +
            (improvement_count * 0.45)
        )
        max_possible = max(1.0, (total_core * 2.0) + (total_rec * 1.0))
        readiness_pct = min(100.0, max(15.0, round((raw_score / max_possible) * 100, 1)))

        return {
            "role_id": target_role_id,
            "role_title": role_meta.get("title", target_role_id),
            "category": role_meta.get("category", "Technology"),
            "readiness_score": readiness_pct,
            "summary": {
                "total_required_skills": total_core + total_rec,
                "matched_count": len(strong),
                "improvement_count": len(needs_improvement),
                "missing_count": len(missing)
            },
            "strong_skills": strong,
            "improvement_skills": needs_improvement,
            "missing_skills": missing,
            "top_priority_to_learn": [s["name"] for s in missing if s.get("priority") == "Critical Priority"][:3]
        }
