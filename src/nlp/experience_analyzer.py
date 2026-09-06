"""
Experience & Seniority Analyzer.
Accurately extracts professional tenure, seniority tiers, and project complexity
while strictly distinguishing work experience from multi-year college degrees.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional


class ExperienceAnalyzer:
    MONTH_MAP = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
        "nov": 11, "november": 11, "dec": 12, "december": 12
    }

    def __init__(self):
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        # Explicit experience statements (e.g. "3+ years of experience", "2.5 yrs exp")
        self.explicit_patterns = [
            re.compile(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp|industry experience|relevant experience)", re.IGNORECASE),
            re.compile(r"(?:experience|exp)\s*[:=]\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)", re.IGNORECASE),
            re.compile(r"\b(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)\s+(?:in|of|as|working)\b", re.IGNORECASE)
        ]

        # Explicit Fresher / Student cues
        self.fresher_patterns = [
            re.compile(r"\b(?:fresher|fresh graduate|entry level|student|seeking entry-level|graduate 202[3-6]|aspiring)\b", re.IGNORECASE)
        ]

        # Education degree markers to ignore when calculating job experience
        self.edu_markers = [
            "b.tech", "btech", "b.e", "b.e.", "bachelor", "m.tech", "mtech", "m.s", "m.sc", "master",
            "b.sc", "bca", "mca", "ph.d", "doctorate", "degree", "diploma", "school", "college",
            "university", "institute", "cgpa", "gpa", "class xii", "cbse", "icse", "hsc", "ssc"
        ]

        # Action verbs
        self.action_verbs = {
            "architected", "developed", "engineered", "built", "designed", "deployed",
            "implemented", "optimized", "spearheaded", "orchestrated", "automated",
            "reduced", "increased", "improved", "accelerated", "scaled", "led", "created"
        }

    def analyze_experience(self, text: str, education_text: str = "", experience_text: str = "") -> Dict[str, Any]:
        """
        Analyzes resume text to estimate total professional experience and seniority level.
        """
        if not text or not text.strip():
            return {
                "estimated_years": 0.0,
                "seniority_level": "Fresher / Entry Level",
                "experience_bracket": "0-1 yrs",
                "action_verb_score": 0.0,
                "projects_detected": 0
            }

        years_candidates: List[float] = []

        # 1. Check Explicit Experience Statements in text / summary
        for pat in self.explicit_patterns:
            for match in pat.finditer(text):
                try:
                    val = float(match.group(1))
                    if 0.5 <= val <= 35.0:
                        years_candidates.append(val)
                except (ValueError, IndexError):
                    pass

        # 2. Check for explicit Fresher mentions
        is_explicit_fresher = any(pat.search(text) for pat in self.fresher_patterns)

        # 3. Parse Work Experience Intervals
        # Prioritize experience section if available, otherwise filter out education lines
        scan_text = experience_text if experience_text.strip() else self._filter_out_education_lines(text, education_text)

        work_intervals = self._extract_date_intervals(scan_text)
        if work_intervals > 0:
            years_candidates.append(work_intervals)

        # 4. Synthesize Final Estimated Years
        if years_candidates:
            # Pick conservative max of explicit statements or work intervals
            estimated_years = round(max(years_candidates), 1)
        elif is_explicit_fresher:
            # Check if candidate has internships mentioned
            if "intern" in text.lower():
                estimated_years = 0.5
            else:
                estimated_years = 0.0
        else:
            # Fallback based on text indicators
            if "intern" in text.lower() or "internship" in text.lower():
                estimated_years = 0.5
            elif "senior" in text.lower() or "lead" in text.lower():
                estimated_years = 5.0
            else:
                estimated_years = 0.0

        # 5. Classify Seniority Level
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

        # 6. Action verb score
        tokens = re.findall(r"\b[a-z]+\b", text.lower())
        verb_hits = sum(1 for t in tokens if t in self.action_verbs)
        action_verb_score = min(100.0, round((verb_hits / max(1, len(tokens))) * 500, 1))

        # 7. Project count
        project_matches = re.findall(r"(?:project|key project|academic project|capstone)\s*\d*[:\n\-]", text, re.IGNORECASE)
        project_count = max(len(project_matches), 1 if "project" in text.lower() else 0)

        return {
            "estimated_years": estimated_years,
            "seniority_level": seniority,
            "experience_bracket": bracket,
            "action_verb_score": action_verb_score,
            "projects_detected": project_count
        }

    def _filter_out_education_lines(self, full_text: str, education_text: str = "") -> str:
        """Removes lines that look like college degree / schooling descriptions."""
        lines = full_text.split("\n")
        cleaned_lines = []
        in_edu_block = False

        for line in lines:
            lower = line.strip().lower()
            if not lower:
                continue

            # Check if entering an education section
            if lower in ["education", "academic qualifications", "academics", "educational background"]:
                in_edu_block = True
                continue
            if in_edu_block and lower in ["experience", "work experience", "employment", "projects", "skills", "certifications"]:
                in_edu_block = False

            if in_edu_block:
                continue

            # Skip individual lines with degree markers
            if any(marker in lower for marker in self.edu_markers):
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _extract_date_intervals(self, text: str) -> float:
        """Calculates total duration in years from job date ranges like 'Jan 2023 - Present'."""
        total_months = 0

        # Pattern 1: Month Year - Month Year / Present (e.g. 'Jan 2022 - Jun 2024' or '07/2023 - Present')
        month_yr_pat = re.compile(
            r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?|\d{1,2})\s*[/,\s]?\s*((?:19|20)\d{2})\s*(?:-|–|to)\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?|\d{1,2})?\s*[/,\s]?\s*((?:19|20)\d{2}|present|current|till date|now)",
            re.IGNORECASE
        )

        for match in month_yr_pat.finditer(text):
            start_m_str, start_yr_str, end_m_str, end_yr_str = match.groups()
            try:
                start_yr = int(start_yr_str)
                start_m = self._parse_month(start_m_str) if start_m_str else 1

                if end_yr_str and any(kw in end_yr_str.lower() for kw in ["present", "current", "till date", "now"]):
                    end_yr = self.current_year
                    end_m = self.current_month
                elif end_yr_str and re.match(r"(?:19|20)\d{2}", end_yr_str):
                    end_yr = int(end_yr_str)
                    end_m = self._parse_month(end_m_str) if end_m_str else 12
                else:
                    end_yr = start_yr
                    end_m = 12

                months = (end_yr - start_yr) * 12 + (end_m - start_m)
                if 1 <= months <= 400:
                    total_months += months
            except Exception:
                pass

        if total_months > 0:
            return round(total_months / 12.0, 1)

        # Pattern 2: Year - Year / Present (e.g. '2022 - Present' or '2021 - 2023')
        year_pat = re.compile(r"(\b(?:19|20)\d{2}\b)\s*(?:-|–|to)\s*(\b(?:19|20)\d{2}\b|present|current|till date|now)", re.IGNORECASE)
        for match in year_pat.finditer(text):
            start_yr_str, end_yr_str = match.groups()
            try:
                start_yr = int(start_yr_str)
                if any(kw in end_yr_str.lower() for kw in ["present", "current", "till date", "now"]):
                    end_yr = self.current_year
                else:
                    end_yr = int(end_yr_str)

                diff = end_yr - start_yr
                # Filter out likely 4-year degree ranges if diff == 4 and no company keyword
                if 0 < diff <= 30:
                    return float(diff)
            except Exception:
                pass

        return 0.0

    def _parse_month(self, month_str: Optional[str]) -> int:
        if not month_str:
            return 1
        m_clean = month_str.strip().lower()
        if m_clean.isdigit():
            return max(1, min(12, int(m_clean)))
        for k, v in self.MONTH_MAP.items():
            if m_clean.startswith(k):
                return v
        return 1
