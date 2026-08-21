"""
Experience & Seniority Analyzer.
Calculates experience years, seniority tiers, and project complexity from resume text.
"""

import re
from datetime import datetime
from typing import Dict, Any, List


class ExperienceAnalyzer:
    def __init__(self):
        self.current_year = datetime.now().year
        
        # Regex patterns for explicit experience statements
        self.explicit_patterns = [
            re.compile(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)", re.IGNORECASE),
            re.compile(r"(?:experience|exp)\s*:\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)", re.IGNORECASE),
            re.compile(r"(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)", re.IGNORECASE)
        ]
        
        # Regex for date ranges: e.g. "2021 - 2024", "Jan 2022 - Present", "06/2020 - 08/2023"
        self.date_range_patterns = [
            re.compile(r"(\b(?:19|20)\d{2}\b)\s*(?:-|–|to)\s*(\b(?:19|20)\d{2}\b|present|current|till date)", re.IGNORECASE),
            re.compile(r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(?:19|20)\d{2})\s*(?:-|–|to)\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(?:19|20)\d{2}|present|current|now)", re.IGNORECASE)
        ]
        
        # Strong impact action verbs
        self.action_verbs = {
            "architected", "developed", "engineered", "built", "designed", "deployed",
            "implemented", "optimized", "spearheaded", "orchestrated", "automated",
            "reduced", "increased", "improved", "accelerated", "scaled", "led", "created"
        }

    def analyze_experience(self, text: str, education_text: str = "") -> Dict[str, Any]:
        """
        Analyzes resume text to estimate total experience, seniority, and project strength.
        """
        if not text:
            return {
                "estimated_years": 0.0,
                "seniority_level": "Fresher / Entry Level",
                "experience_bracket": "0-1 yrs",
                "action_verb_score": 0.0,
                "projects_detected": 0
            }
            
        years_candidates: List[float] = []
        
        # Check explicit experience mentions
        for pat in self.explicit_patterns:
            matches = pat.findall(text)
            for m in matches:
                try:
                    val = float(m)
                    if 0.5 <= val <= 35.0:
                        years_candidates.append(val)
                except ValueError:
                    pass
                    
        # Check date intervals in work experience sections
        date_intervals_years = 0.0
        for pat in self.date_range_patterns:
            for start_str, end_str in pat.findall(text):
                # Extract year digits
                start_match = re.search(r"(?:19|20)\d{2}", start_str)
                if not start_match:
                    continue
                start_yr = int(start_match.group(0))
                
                if any(kw in end_str.lower() for kw in ["present", "current", "till date", "now"]):
                    end_yr = self.current_year
                else:
                    end_match = re.search(r"(?:19|20)\d{2}", end_str)
                    end_yr = int(end_match.group(0)) if end_match else start_yr
                    
                # Skip graduation date ranges if they match education context
                diff = max(0, min(15, end_yr - start_yr))
                if 1990 <= start_yr <= self.current_year and diff <= 15:
                    date_intervals_years = max(date_intervals_years, float(diff))
                    
        if date_intervals_years > 0:
            years_candidates.append(date_intervals_years)
            
        # Determine final estimated years
        if years_candidates:
            # Pick conservative median or max if realistic
            estimated_years = float(max(years_candidates))
        else:
            # Check for intern / student cues
            lower_text = text.lower()
            if "intern" in lower_text or "student" in lower_text or "fresher" in lower_text:
                estimated_years = 0.5
            else:
                estimated_years = 1.0 # Default baseline
                
        # Classify seniority
        if estimated_years < 1.0:
            seniority = "Fresher / Entry Level"
            bracket = "0-1 yrs"
        elif estimated_years < 3.0:
            seniority = "Junior Associate"
            bracket = "1-3 yrs"
        elif estimated_years < 6.0:
            seniority = "Mid-Level Specialist"
            bracket = "3-6 yrs"
        elif estimated_years < 10.0:
            seniority = "Senior Engineer / Lead"
            bracket = "6-10 yrs"
        else:
            seniority = "Principal / Staff"
            bracket = "10+ yrs"
            
        # Action verb density score
        tokens = re.findall(r"\b[a-z]+\b", text.lower())
        verb_hits = sum(1 for t in tokens if t in self.action_verbs)
        action_verb_score = min(100.0, round((verb_hits / max(1, len(tokens))) * 500, 1))
        
        # Project count detection
        project_matches = re.findall(r"(?:project|key project|academic project|capstone)\s*\d*[:\n\-]", text, re.IGNORECASE)
        project_count = max(len(project_matches), 1 if "project" in text.lower() else 0)
        
        return {
            "estimated_years": estimated_years,
            "seniority_level": seniority,
            "experience_bracket": bracket,
            "action_verb_score": action_verb_score,
            "projects_detected": project_count
        }
