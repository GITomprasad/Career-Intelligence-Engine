"""
Skill Extractor & Normalization Engine.
Extracts, categorizes, and standardizes technical and soft skills from freeform text.
"""

import json
import re
from typing import Dict, List, Set, Tuple, Any
from src.config import ONTOLOGY_PATH


class SkillExtractor:
    def __init__(self, ontology_path: str = None):
        self.ontology_path = ontology_path or str(ONTOLOGY_PATH)
        self.categories: Dict[str, Any] = {}
        self.roles: Dict[str, Any] = {}
        self.skill_map: Dict[str, Dict[str, Any]] = {} # id -> meta
        self.alias_to_id: Dict[str, str] = {} # lower alias -> skill id
        self.regex_patterns: List[Tuple[re.Pattern, str]] = [] # (compiled_regex, skill_id)
        self._load_ontology()

    def _load_ontology(self):
        with open(self.ontology_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.categories = data.get("categories", {})
        self.roles = data.get("roles", {})
        
        # Build lookup tables
        temp_alias_list = []
        for cat_id, cat_info in self.categories.items():
            for skill in cat_info.get("skills", []):
                s_id = skill["id"]
                s_name = skill["name"]
                aliases = skill.get("aliases", [s_id, s_name.lower()])
                
                self.skill_map[s_id] = {
                    "id": s_id,
                    "name": s_name,
                    "category_id": cat_id,
                    "category_name": cat_info["name"],
                    "aliases": aliases
                }
                
                for alias in aliases:
                    alias_clean = alias.strip().lower()
                    self.alias_to_id[alias_clean] = s_id
                    temp_alias_list.append((alias_clean, s_id))
                    
        # Sort aliases by length descending so multi-word tokens match first (e.g. 'machine learning' before 'learning')
        temp_alias_list.sort(key=lambda x: len(x[0]), reverse=True)
        
        # Build optimized regex patterns
        for alias, s_id in temp_alias_list:
            # Handle special symbols like c++, c#, .net, r, c
            if alias == "c++":
                pat = re.compile(r"(?:\b|(?<=\s))c\+\+(?:\b|(?=\s)|[,;.\)])", re.IGNORECASE)
            elif alias == "c#":
                pat = re.compile(r"(?:\b|(?<=\s))c\#(?:\b|(?=\s)|[,;.\)])", re.IGNORECASE)
            elif alias == ".net":
                pat = re.compile(r"(?:\b|(?<=\s))\.(?:net)(?:\b|(?=\s)|[,;.\)])", re.IGNORECASE)
            elif alias in ["r", "c"]:
                # Strict isolation for single-letter languages
                pat = re.compile(r"(?:\b|(?<=\s))" + re.escape(alias) + r"(?=\b|[,;.\)])", re.IGNORECASE)
            else:
                pat = re.compile(r"\b" + re.escape(alias) + r"\b", re.IGNORECASE)
            self.regex_patterns.append((pat, s_id))

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extracts all canonical skills present in the given text.
        Returns:
            {
                "skill_ids": ["python", "sql", ...],
                "skill_names": ["Python", "SQL", ...],
                "by_category": { "Programming Languages": [...], ... },
                "total_count": 12
            }
        """
        if not text:
            return {"skill_ids": [], "skill_names": [], "by_category": {}, "total_count": 0}
            
        found_ids: Set[str] = set()
        clean_text = " " + text.replace("/", " / ").replace("-", " ") + " "
        
        # Pass 1: Regex matching
        for pattern, s_id in self.regex_patterns:
            if pattern.search(clean_text):
                found_ids.add(s_id)
                # mask the matched skill to avoid substring matches
                clean_text = pattern.sub(" ", clean_text)
                
        # Group by category
        by_cat: Dict[str, List[str]] = {}
        skill_names = []
        
        for s_id in sorted(list(found_ids)):
            s_info = self.skill_map.get(s_id)
            if s_info:
                cat_name = s_info["category_name"]
                if cat_name not in by_cat:
                    by_cat[cat_name] = []
                by_cat[cat_name].append(s_info["name"])
                skill_names.append(s_info["name"])
                
        return {
            "skill_ids": sorted(list(found_ids)),
            "skill_names": skill_names,
            "by_category": by_cat,
            "total_count": len(found_ids)
        }

    def normalize_skill(self, skill_token: str) -> str:
        """Translates any alias/token into canonical skill_id, or None if unknown."""
        token_clean = skill_token.strip().lower()
        if token_clean in self.alias_to_id:
            return self.alias_to_id[token_clean]
        # Try direct regex scan on token
        for pattern, s_id in self.regex_patterns:
            if pattern.search(token_clean):
                return s_id
        return None

    def get_skill_name(self, skill_id: str) -> str:
        """Returns pretty display name for a skill ID."""
        info = self.skill_map.get(skill_id)
        return info["name"] if info else skill_id.replace("_", " ").title()

    def get_all_skill_ids(self) -> List[str]:
        return sorted(list(self.skill_map.keys()))
