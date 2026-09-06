"""
ATS (Applicant Tracking System) Compatibility Scorer.
Evaluates resume keyword match, format/readability quality, and experience depth.
Generates numeric sub-scores, overall ATS score (0-100), pass rate forecast, and actionable wins/fixes.
"""

import json
import re
from typing import Dict, Any, List, Optional
from src.config import (
    ONTOLOGY_PATH,
    WEIGHT_ATS_KEYWORDS,
    WEIGHT_ATS_FORMAT,
    WEIGHT_ATS_EXPERIENCE
)
from src.nlp.skill_extractor import SkillExtractor
from src.engine.gap_analyzer import SkillGapAnalyzer


class ATSScorer:
    def __init__(self, ontology_path: Optional[str] = None):
        self.ontology_path = ontology_path or str(ONTOLOGY_PATH)
        self.extractor = SkillExtractor(self.ontology_path)
        self.gap_analyzer = SkillGapAnalyzer(self.ontology_path)
        self._load_ontology()

    def _load_ontology(self):
        with open(self.ontology_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.roles = data.get("roles", {})

    def score(self, profile: Dict[str, Any], target_role_id: str, raw_text: str = "") -> Dict[str, Any]:
        """
        Calculates ATS compatibility score and returns actionable insights.
        """
        role_meta = self.roles.get(target_role_id, {})
        role_title = role_meta.get("title", target_role_id.replace("_", " ").title())
        
        text_content = raw_text or profile.get("raw_text", "")
        if not text_content and profile.get("skills"):
            # Fallback text representation from profile if raw text isn't passed
            text_content = " ".join(profile.get("skills", [])) + " " + profile.get("summary", "")

        candidate_skills = profile.get("skill_ids", [])
        if not candidate_skills and profile.get("skills"):
            candidate_skills = [
                self.extractor.normalize_skill(s) or s.lower().replace(" ", "_")
                for s in profile.get("skills", [])
            ]

        # 1. Compute Keyword Match Sub-Score (40%)
        kw_score, kw_issues, kw_wins, kw_details = self._score_keywords(candidate_skills, target_role_id, role_title)

        # 2. Compute Format & Readability Sub-Score (30%)
        fmt_score, fmt_issues, fmt_wins, fmt_details = self._score_format(profile, text_content, role_meta)

        # 3. Compute Experience Depth Sub-Score (30%)
        exp_score, exp_issues, exp_wins, exp_details = self._score_experience(profile, target_role_id, role_meta)

        # Total ATS Score (0 - 100)
        total_score = round(
            (kw_score * WEIGHT_ATS_KEYWORDS) +
            (fmt_score * WEIGHT_ATS_FORMAT) +
            (exp_score * WEIGHT_ATS_EXPERIENCE)
        )
        total_score = max(0, min(100, int(total_score)))

        # Estimated ATS Pass Rate
        if total_score >= 80:
            pass_rate = min(96, int(total_score * 0.96 + 2))
            verdict = "Good — passes most ATS filters"
            status_badge = "Excellent"
            status_color = "#16A34A"
        elif total_score >= 65:
            pass_rate = min(85, int(total_score * 0.90 + 3))
            verdict = "Good — passes most ATS filters"
            status_badge = "Good"
            status_color = "#16A34A"
        elif total_score >= 45:
            pass_rate = int(total_score * 0.75)
            verdict = "Needs work — address critical keyword & format fixes"
            status_badge = "Needs Work"
            status_color = "#D97706"
        else:
            pass_rate = max(10, int(total_score * 0.60))
            verdict = "Critical gaps — high risk of automated ATS rejection"
            status_badge = "At Risk"
            status_color = "#DC2626"

        all_issues = kw_issues + fmt_issues + exp_issues
        all_wins = kw_wins + fmt_wins + exp_wins

        return {
            "total": total_score,
            "keyword": round(kw_score, 1),
            "format": round(fmt_score, 1),
            "experience": round(exp_score, 1),
            "verdict": verdict,
            "status_badge": status_badge,
            "status_color": status_color,
            "ats_pass_rate_estimate": pass_rate,
            "skills_detected_count": len(profile.get("skills", [])),
            "missing_keywords_count": len(kw_details.get("missing_core", [])) + len(kw_details.get("missing_rec", [])),
            "issues": all_issues,
            "wins": all_wins,
            "keyword_details": kw_details,
            "format_details": fmt_details,
            "experience_details": exp_details,
            "target_role_title": role_title,
            "target_role_id": target_role_id
        }

    def _score_keywords(self, candidate_skill_ids: List[str], target_role_id: str, role_title: str):
        role_meta = self.roles.get(target_role_id, {})
        core_skills = role_meta.get("core_skills", [])
        rec_skills = role_meta.get("recommended_skills", [])

        if not core_skills:
            return 75.0, [], ["Role keywords evaluated."], {"matched_core": [], "missing_core": [], "matched_rec": [], "missing_rec": []}

        cand_set = set(candidate_skill_ids)
        matched_core = [s for s in core_skills if s in cand_set]
        missing_core = [s for s in core_skills if s not in cand_set]
        matched_rec = [s for s in rec_skills if s in cand_set]
        missing_rec = [s for s in rec_skills if s not in cand_set]

        core_ratio = len(matched_core) / max(1, len(core_skills))
        rec_ratio = len(matched_rec) / max(1, len(rec_skills)) if rec_skills else 1.0

        # Core skills count 75%, recommended skills count 25%
        kw_score = min(100.0, (core_ratio * 75.0) + (rec_ratio * 25.0))

        issues = []
        wins = []

        for s_id in missing_core[:3]:
            s_name = self.extractor.get_skill_name(s_id)
            issues.append(f"Add '{s_name}' to your skills section — appears in 80%+ of {role_title} postings")

        if len(missing_core) > 3:
            more_names = [self.extractor.get_skill_name(s) for s in missing_core[3:5]]
            issues.append(f"Incorporate key {role_title} competencies: {', '.join(more_names)}")

        if missing_rec and len(missing_core) < 2:
            rec_name = self.extractor.get_skill_name(missing_rec[0])
            issues.append(f"Consider adding secondary skill '{rec_name}' to stand out against peer applicants")

        # Wins
        if matched_core:
            core_names = [self.extractor.get_skill_name(s) for s in matched_core[:5]]
            wins.append(f"Matched key core keywords: {', '.join(core_names)}")
        if len(matched_core) >= 4:
            wins.append(f"Strong alignment on primary {role_title} technical competencies")
        if matched_rec:
            wins.append(f"Contains {len(matched_rec)} recommended supporting skills")

        details = {
            "matched_core": [self.extractor.get_skill_name(s) for s in matched_core],
            "missing_core": [self.extractor.get_skill_name(s) for s in missing_core],
            "matched_rec": [self.extractor.get_skill_name(s) for s in matched_rec],
            "missing_rec": [self.extractor.get_skill_name(s) for s in missing_rec]
        }

        return kw_score, issues, wins, details

    def _score_format(self, profile: Dict[str, Any], text: str, role_meta: Dict[str, Any]):
        score = 0.0
        issues = []
        wins = []

        # 1. Contact information (25 pts)
        email = profile.get("email", "")
        phone = profile.get("phone", "")
        has_email = bool(email and "@" in email and "not" not in email.lower())
        has_phone = bool(phone and len(re.sub(r"\D", "", phone)) >= 7 and "not" not in phone.lower())
        
        if has_email and has_phone:
            score += 25.0
            wins.append("Contact info complete: Valid email address and phone number found")
        elif has_email:
            score += 15.0
            issues.append("Add a direct phone number to candidate header for recruiter reachability")
        elif has_phone:
            score += 15.0
            issues.append("Add a professional email address to your resume header")
        else:
            issues.append("Missing primary contact details (email and phone) in header")

        # 2. Portfolio links (LinkedIn/GitHub) (15 pts)
        linkedin = profile.get("linkedin", "")
        github = profile.get("github", "")
        has_portfolio = bool(linkedin or github or re.search(r"linkedin\.com|github\.com|portfolio|gitlab\.com", text, re.IGNORECASE))
        
        if has_portfolio:
            score += 15.0
            wins.append("Online portfolio / profile link (LinkedIn or GitHub) detected")
        else:
            score += 5.0
            issues.append("Add a GitHub profile link — 91% of tech postings screen for portfolio links")

        # 3. Resume word count & density (25 pts)
        word_count = len(text.split()) if text else 0
        if 400 <= word_count <= 850:
            score += 25.0
            wins.append(f"Optimal resume length ({word_count} words) for automated ATS parsing depth")
        elif 250 <= word_count < 400:
            score += 15.0
            issues.append(f"Resume word count is {word_count} — aim for 450–700 for better ATS parse depth")
        elif word_count > 850:
            score += 18.0
            issues.append(f"Resume is lengthy ({word_count} words) — consider tightening bullet points to under 800 words")
        else:
            score += 8.0
            issues.append("Resume content is sparse (<250 words) — expand on projects, responsibilities, and achievements")

        # 4. Standard section headers (15 pts)
        sections = profile.get("sections", {})
        has_sections = bool(sections) or any(kw in text.lower() for kw in ["experience", "education", "skills", "projects"])
        if has_sections:
            score += 15.0
            wins.append("Standard ATS-friendly section headers detected (Experience, Skills, Education)")
        else:
            score += 8.0
            issues.append("Ensure standard section headers ('Work Experience', 'Technical Skills', 'Education') are clearly labeled")

        # 5. Quantified impact & Action verbs (20 pts)
        quantified_matches = re.findall(
            r"\b(?:\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?|\b\d+\s*(?:k|m|crore|lakh|users|clients|projects|queries|ms|x|hours|days|percent)\b)",
            text,
            re.IGNORECASE
        )
        bullet_points = [line for line in text.split("\n") if line.strip().startswith(("-", "•", "*", "1.", "2.", "3."))]
        
        if len(quantified_matches) >= 3:
            score += 20.0
            wins.append(f"Quantified achievements detected ({len(quantified_matches)} metrics with numbers/percentages)")
        elif len(quantified_matches) >= 1:
            score += 12.0
            issues.append("Quantify achievements: add numbers to at least 3 bullet points (e.g. 'improved accuracy by 12%')")
        else:
            score += 5.0
            issues.append("No quantified impact metrics detected — add measurable business outcomes (e.g. 'improved accuracy by 12%')")

        details = {
            "word_count": word_count,
            "has_contact_info": bool(has_email and has_phone),
            "has_portfolio": has_portfolio,
            "quantified_metrics_count": len(quantified_matches),
            "bullet_points_count": len(bullet_points)
        }

        return min(100.0, score), issues, wins, details

    def _score_experience(self, profile: Dict[str, Any], target_role_id: str, role_meta: Dict[str, Any]):
        score = 0.0
        issues = []
        wins = []

        cand_exp = float(profile.get("experience_years", 0.0))
        seniority = profile.get("seniority_level", "Fresher / Entry Level")
        edu = profile.get("education", {})
        degree = edu.get("degree", "Bachelor's Degree") if isinstance(edu, dict) else "Bachelor's Degree"

        # 1. Experience Years Alignment (40 pts)
        if "lead" in target_role_id or "senior" in target_role_id or "architect" in target_role_id:
            expected_exp = 4.0
        elif "junior" in target_role_id or "entry" in target_role_id:
            expected_exp = 0.5
        else:
            expected_exp = 1.5

        if cand_exp >= expected_exp:
            score += 40.0
            wins.append(f"{cand_exp}+ years of relevant experience meets role requirements ({expected_exp}+ yrs)")
        elif cand_exp >= (expected_exp * 0.5):
            score += 26.0
            issues.append(f"Target role typically expects {expected_exp}+ years of experience (current estimated: {cand_exp} yrs) — emphasize project depth & internships")
        else:
            score += 15.0
            issues.append(f"Experience gap for {role_meta.get('title', 'Target Role')} — build hands-on portfolio capstones to demonstrate capability")

        # 2. Seniority & Domain Context (30 pts)
        if cand_exp >= 1.0 or "Specialist" in seniority or "Associate" in seniority or "Senior" in seniority:
            score += 30.0
            wins.append(f"Seniority bracket ({seniority}) aligns with technical hiring standards")
        else:
            score += 20.0
            wins.append("Entry-level candidate profile evaluated against junior benchmark standards")

        # 3. Academic & Educational Profile (30 pts)
        has_degree = bool(degree and "none" not in str(degree).lower())
        if has_degree:
            score += 30.0
            wins.append(f"Education credentials ({degree}) match role requirements")
        else:
            score += 15.0
            issues.append("Explicitly state highest degree / academic background in the Education section")

        details = {
            "candidate_experience_years": cand_exp,
            "expected_experience_years": expected_exp,
            "seniority_level": seniority,
            "education_degree": degree
        }

        return min(100.0, score), issues, wins, details
