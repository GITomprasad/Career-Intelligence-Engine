"""
Resume Parser Engine.
Extracts contact info, education, skills, projects, and work experience from PDF and TXT resumes.
"""

import io
import re
from typing import Dict, Any, List, Optional
import pypdf

from .skill_extractor import SkillExtractor
from .experience_analyzer import ExperienceAnalyzer


class ResumeParser:
    def __init__(self, ontology_path: str = None):
        self.skill_extractor = SkillExtractor(ontology_path)
        self.exp_analyzer = ExperienceAnalyzer()

    def parse(self, input_source: Any, filename: str = "") -> Dict[str, Any]:
        """
        Parses resume from either file path, bytes, file-like object, or raw text.
        """
        text = self._extract_raw_text(input_source, filename)
        if not text or not text.strip():
            return {
                "success": False,
                "error": "No readable text could be extracted from the document.",
                "raw_text": "",
                "profile": {}
            }

        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Extract components
        contact_info = self._extract_contact_info(cleaned_text)
        sections = self._segment_sections(cleaned_text)
        education_info = self._extract_education(cleaned_text, sections.get("education", ""))
        skills_info = self.skill_extractor.extract_skills(cleaned_text)
        exp_info = self.exp_analyzer.analyze_experience(cleaned_text, sections.get("education", ""))
        projects = self._extract_projects(cleaned_text, sections.get("projects", ""))
        certifications = self._extract_certifications(cleaned_text, sections.get("certifications", ""))

        profile = {
            "name": contact_info["name"],
            "email": contact_info["email"],
            "phone": contact_info["phone"],
            "location": contact_info["location"],
            "linkedin": contact_info["linkedin"],
            "github": contact_info["github"],
            "education": education_info,
            "skills": skills_info["skill_names"],
            "skill_ids": skills_info["skill_ids"],
            "skills_by_category": skills_info["by_category"],
            "skills_count": skills_info["total_count"],
            "experience_years": exp_info["estimated_years"],
            "seniority_level": exp_info["seniority_level"],
            "experience_bracket": exp_info["experience_bracket"],
            "action_verb_score": exp_info["action_verb_score"],
            "projects": projects,
            "certifications": certifications,
            "summary": sections.get("summary", "")[:400]
        }

        return {
            "success": True,
            "raw_text": cleaned_text,
            "sections": sections,
            "profile": profile
        }

    def _extract_raw_text(self, input_source: Any, filename: str = "") -> str:
        """Extracts plain text from various input types."""
        # 1. Plain text string
        if isinstance(input_source, str):
            # Check if it's a file path
            if (input_source.endswith(".pdf") or input_source.endswith(".txt")) and len(input_source) < 500:
                try:
                    if input_source.endswith(".pdf"):
                        reader = pypdf.PdfReader(input_source)
                        return "\n".join([page.extract_text() or "" for page in reader.pages])
                    else:
                        with open(input_source, "r", encoding="utf-8", errors="ignore") as f:
                            return f.read()
                except Exception:
                    return input_source
            return input_source

        # 2. Bytes / ByteIO
        if isinstance(input_source, bytes) or hasattr(input_source, "read"):
            stream = io.BytesIO(input_source) if isinstance(input_source, bytes) else input_source
            if filename.lower().endswith(".pdf") or not filename:
                try:
                    reader = pypdf.PdfReader(stream)
                    pages_text = [page.extract_text() or "" for page in reader.pages]
                    return "\n".join(pages_text)
                except Exception:
                    # Fallback to UTF-8 decoding if not valid PDF
                    if isinstance(input_source, bytes):
                        return input_source.decode("utf-8", errors="ignore")
                    stream.seek(0)
                    return stream.read().decode("utf-8", errors="ignore")
            else:
                if isinstance(input_source, bytes):
                    return input_source.decode("utf-8", errors="ignore")
                return stream.read().decode("utf-8", errors="ignore")

        return ""

    def _clean_text(self, text: str) -> str:
        # Standardize line breaks and spaces
        text = re.sub(r"\r\n|\r", "\n", text)
        text = re.sub(r"\t", " ", text)
        text = re.sub(r" +", " ", text)
        return text.strip()

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # Name: Usually first 1-3 lines
        candidate_name = "Candidate"
        for line in lines[:4]:
            clean_line = re.sub(r"[^a-zA-Z\s]", "", line).strip()
            # Ignore headers like 'RESUME', 'CURRICULUM VITAE'
            if clean_line.upper() in ["RESUME", "CURRICULUM VITAE", "CV", "BIO"]:
                continue
            words = clean_line.split()
            if 2 <= len(words) <= 4 and all(len(w) >= 2 for w in words):
                candidate_name = clean_line.title()
                break
                
        # Email
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        email = email_match.group(0) if email_match else "Not Provided"
        
        # Phone
        phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+91[-.\s]?\d{10}|\b\d{10}\b", text)
        phone = phone_match.group(0) if phone_match else "Not Provided"
        
        # Location
        location = "Not Specified"
        loc_patterns = [
            r"(?:Location|Address|City)\s*:\s*([A-Za-z\s,]+)",
            r"\b(Bangalore|Bengaluru|Hyderabad|Pune|Mumbai|Delhi|Noida|Gurgaon|Chennai|Kolkata|Ahmedabad|San Francisco|New York|London|Remote)\b"
        ]
        for pat in loc_patterns:
            loc_match = re.search(pat, text, re.IGNORECASE)
            if loc_match:
                location = loc_match.group(1).strip()
                break

        # LinkedIn & GitHub
        linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
        linkedin = f"linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else ""
        
        github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
        github = f"github.com/{github_match.group(1)}" if github_match else ""
        
        return {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin": linkedin,
            "github": github
        }

    def _segment_sections(self, text: str) -> Dict[str, str]:
        section_headers = {
            "summary": ["summary", "professional summary", "about me", "objective", "profile"],
            "education": ["education", "academic background", "academics", "qualifications"],
            "experience": ["experience", "work experience", "employment", "professional experience", "internships"],
            "projects": ["projects", "key projects", "academic projects", "personal projects", "capstone"],
            "skills": ["skills", "technical skills", "core competencies", "technologies", "tech stack"],
            "certifications": ["certifications", "licenses", "courses", "achievements", "publications"]
        }
        
        # Identify section positions
        header_positions = []
        lines = text.split("\n")
        
        for idx, line in enumerate(lines):
            clean = line.strip().lower()
            clean = re.sub(r"[^a-z\s]", "", clean)
            for sec_name, keywords in section_headers.items():
                if clean in keywords or any(clean.startswith(kw + " ") for kw in keywords):
                    header_positions.append((idx, sec_name))
                    break

        sections = {}
        for i in range(len(header_positions)):
            start_idx, sec_name = header_positions[i]
            end_idx = header_positions[i + 1][0] if i + 1 < len(header_positions) else len(lines)
            sec_text = "\n".join(lines[start_idx + 1:end_idx]).strip()
            sections[sec_name] = sec_text
            
        return sections

    def _extract_education(self, full_text: str, edu_section: str) -> Dict[str, Any]:
        text_to_scan = edu_section if edu_section else full_text
        
        # Degree detection
        degrees = [
            (r"\b(?:Ph\.?D|Doctor of Philosophy)\b", "Ph.D. / Doctorate"),
            (r"\b(?:M\.?Tech|Master of Technology|M\.?S|M\.?Sc|Master of Science|M\.?C\.?A|MBA)\b", "Master's Degree"),
            (r"\b(?:B\.?Tech|Bachelor of Technology|B\.?E|Bachelor of Engineering|B\.?S|B\.?Sc|B\.?C\.?A)\b", "Bachelor's Degree")
        ]
        
        detected_degree = "Bachelor's Degree" # Default assumption
        for pat, deg_name in degrees:
            if re.search(pat, text_to_scan, re.IGNORECASE):
                detected_degree = deg_name
                break
                
        # Major / Field
        majors = [
            "Computer Science", "Artificial Intelligence", "Data Science",
            "Information Technology", "Electrical Engineering", "Electronics",
            "Mechanical Engineering", "Mathematics", "Statistics", "Data Analytics"
        ]
        detected_major = "Computer Science / Related"
        for m in majors:
            if re.search(r"\b" + re.escape(m) + r"\b", text_to_scan, re.IGNORECASE):
                detected_major = m
                break
                
        # CGPA / Percentage
        gpa_match = re.search(r"(?:CGPA|GPA|Score|Percentage)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:/|out of)?\s*(?:10|100|4\.0)?", text_to_scan, re.IGNORECASE)
        gpa_str = gpa_match.group(0) if gpa_match else "N/A"
        
        # Year
        year_match = re.search(r"\b(201\d|202\d)\b", text_to_scan)
        grad_year = year_match.group(0) if year_match else "Recent"

        return {
            "degree": detected_degree,
            "major": detected_major,
            "gpa": gpa_str,
            "graduation_year": grad_year
        }

    def _extract_projects(self, full_text: str, project_section: str) -> List[Dict[str, str]]:
        text_to_scan = project_section if project_section else full_text
        projects = []
        
        # Look for numbered or bulleted project titles
        lines = text_to_scan.split("\n")
        current_project = None
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            # Check if line looks like a project header (e.g. "1. Project Name", "• Project Name", "Project:")
            if re.match(r"^(?:\d+\.|\*|\-|\•)\s+([A-Za-z0-9\s\-\:]+)", line_str) or (line_str.isupper() and len(line_str) < 50):
                if current_project:
                    projects.append(current_project)
                title = re.sub(r"^(?:\d+\.|\*|\-|\•)\s*", "", line_str)
                current_project = {"title": title, "description": ""}
            elif current_project:
                current_project["description"] += " " + line_str
                
        if current_project:
            projects.append(current_project)
            
        return projects[:5]

    def _extract_certifications(self, full_text: str, cert_section: str) -> List[str]:
        text_to_scan = cert_section if cert_section else full_text
        certs = []
        for line in text_to_scan.split("\n"):
            clean = line.strip().strip("-*•").strip()
            if len(clean) > 5 and any(kw in clean.lower() for kw in ["certified", "certificate", "specialization", "course", "badge", "associate", "professional", "coursera", "udemy"]):
                certs.append(clean)
        return certs[:6]
