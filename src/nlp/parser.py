"""
Universal Multi-Format Resume Parser Engine.
Extracts contact info, education, skills, projects, and work experience from:
- Documents: PDF (.pdf), Word (.docx, .doc), Rich Text (.rtf), Plain Text (.txt, .md), HTML (.html), JSON (.json)
- Images: JPG (.jpg, .jpeg), PNG (.png), WEBP (.webp), TIFF (.tiff, .tif), BMP (.bmp) via Neural OCR.
"""

import io
import json
import logging
import os
import re
import zipfile
import defusedxml.ElementTree as ET
from typing import Dict, Any, List, Optional, Union
import numpy as np
from PIL import Image
import pypdf

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from rapidocr_onnxruntime import RapidOCR
    OCR_ENGINE = RapidOCR()
    HAS_OCR = True
except Exception as e:
    OCR_ENGINE = None
    HAS_OCR = False

from .skill_extractor import SkillExtractor
from .experience_analyzer import ExperienceAnalyzer

logger = logging.getLogger(__name__)


class ResumeParser:
    def __init__(self, ontology_path: str = None):
        self.skill_extractor = SkillExtractor(ontology_path)
        self.exp_analyzer = ExperienceAnalyzer()

    def parse(self, input_source: Any, filename: str = "") -> Dict[str, Any]:
        """
        Parses resume from either file path, bytes, file-like object, or raw text.
        Supports PDF, DOCX, DOC, JPG, PNG, WEBP, RTF, TXT, MD, HTML, and JSON.
        """
        text = self._extract_raw_text(input_source, filename)
        if not text or not text.strip():
            return {
                "success": False,
                "error": "No readable text could be extracted from the document. Please ensure the file is clear and not empty or password-protected.",
                "raw_text": "",
                "profile": {}
            }

        # Clean text
        cleaned_text = self._clean_text(text)

        # Check if structured JSON resume
        if filename.lower().endswith(".json") or (cleaned_text.startswith("{") and cleaned_text.endswith("}")):
            json_profile = self._try_parse_json_resume(cleaned_text)
            if json_profile:
                return {
                    "success": True,
                    "raw_text": cleaned_text,
                    "sections": {},
                    "profile": json_profile
                }

        # Extract components from freeform text
        contact_info = self._extract_contact_info(cleaned_text)
        sections = self._segment_sections(cleaned_text)
        education_info = self._extract_education(cleaned_text, sections.get("education", ""))
        skills_info = self.skill_extractor.extract_skills(cleaned_text)
        exp_info = self.exp_analyzer.analyze_experience(
            cleaned_text,
            education_text=sections.get("education", ""),
            experience_text=sections.get("experience", "")
        )
        projects = self._extract_projects(cleaned_text, sections.get("projects", ""))
        certifications = self._extract_certifications(cleaned_text, sections.get("certifications", ""))

        profile = {
            "name": contact_info["name"],
            "email": contact_info["email"],
            "phone": contact_info["phone"],
            "location": contact_info["location"],
            "linkedin": contact_info["linkedin"],
            "github": contact_info["github"],
            "portfolio": contact_info.get("portfolio", ""),
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
        """Extracts plain text across all supported file formats."""
        # 1. Plain text string passed directly
        if isinstance(input_source, str):
            if (any(input_source.lower().endswith(ext) for ext in [
                ".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png", ".webp",
                ".txt", ".md", ".rtf", ".html", ".htm", ".json"
            ])) and len(input_source) < 500:
                if os.path.exists(input_source):
                    try:
                        with open(input_source, "rb") as f:
                            return self._extract_from_bytes(f.read(), os.path.basename(input_source))
                    except Exception as e:
                        logger.error(f"Error reading file path {input_source}: {e}")
            return input_source

        # 2. Bytes or Stream
        if isinstance(input_source, bytes):
            return self._extract_from_bytes(input_source, filename)

        if hasattr(input_source, "read"):
            try:
                data = input_source.read()
                fname = getattr(input_source, "name", filename)
                return self._extract_from_bytes(data, fname)
            except Exception as e:
                logger.error(f"Error reading stream: {e}")

        return ""

    def _extract_from_bytes(self, raw_bytes: bytes, filename: str = "") -> str:
        """Dispatches binary data to the corresponding format parser."""
        if not raw_bytes:
            return ""

        fn = filename.lower()

        # 1. Image Formats (JPG, JPEG, PNG, WEBP, TIFF, BMP) via Neural OCR
        image_extensions = (".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp", ".jfif")
        is_image_bytes = (
            raw_bytes.startswith(b"\xff\xd8\xff") or  # JPEG
            raw_bytes.startswith(b"\x89PNG\r\n\x1a\n") or  # PNG
            raw_bytes.startswith(b"RIFF") and b"WEBP" in raw_bytes[:16] or  # WEBP
            raw_bytes.startswith(b"BM")  # BMP
        )

        if fn.endswith(image_extensions) or is_image_bytes:
            img_text = self._extract_from_image(raw_bytes)
            if img_text:
                return img_text

        # 2. PDF Parser
        if fn.endswith(".pdf") or raw_bytes.startswith(b"%PDF-"):
            try:
                stream = io.BytesIO(raw_bytes)
                reader = pypdf.PdfReader(stream)
                text_pages = [page.extract_text() or "" for page in reader.pages]
                full_pdf_text = "\n".join(text_pages).strip()
                if full_pdf_text and len(full_pdf_text) > 30:
                    return full_pdf_text
            except Exception as e:
                logger.warning(f"PDF extraction warning: {e}")

        # 3. DOCX Parser (Word OpenXML)
        if fn.endswith(".docx") or raw_bytes.startswith(b"PK\x03\x04"):
            # Try python-docx first
            if HAS_DOCX:
                try:
                    doc = docx.Document(io.BytesIO(raw_bytes))
                    doc_paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                    # Also include tables
                    for table in doc.tables:
                        for row in table.rows:
                            row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                            if row_text:
                                doc_paragraphs.append(row_text)
                    extracted = "\n".join(doc_paragraphs).strip()
                    if extracted:
                        return extracted
                except Exception as e:
                    logger.warning(f"python-docx extraction warning: {e}")

            # Built-in XML ZIP Fallback for DOCX
            try:
                with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
                    if "word/document.xml" in z.namelist():
                        xml_content = z.read("word/document.xml")
                        tree = ET.fromstring(xml_content)
                        texts = [node.text for node in tree.iter() if node.text]
                        extracted_xml = " ".join(texts).strip()
                        if extracted_xml:
                            return extracted_xml
            except Exception as e:
                logger.warning(f"DOCX XML zip extraction warning: {e}")

        # 4. RTF Parser (.rtf)
        if fn.endswith(".rtf") or raw_bytes.startswith(b"{\\rtf"):
            try:
                rtf_str = raw_bytes.decode("utf-8", errors="ignore")
                rtf_str = re.sub(r"\\par\b|\\line\b", "\n", rtf_str)
                rtf_clean = re.sub(r"\\[a-z0-9]+-?", " ", rtf_str)
                rtf_clean = re.sub(r"[{}]", " ", rtf_clean)
                return rtf_clean.strip()
            except Exception as e:
                logger.warning(f"RTF decode warning: {e}")

        # 5. HTML Parser (.html, .htm)
        if fn.endswith(".html") or fn.endswith(".htm") or b"<html" in raw_bytes.lower():
            try:
                html_str = raw_bytes.decode("utf-8", errors="ignore")
                html_str = re.sub(r"<style[\s\S]*?</style>", "", html_str, flags=re.IGNORECASE)
                html_str = re.sub(r"<script[\s\S]*?</script>", "", html_str, flags=re.IGNORECASE)
                text_clean = re.sub(r"<[^>]+>", "\n", html_str)
                return text_clean.strip()
            except Exception as e:
                logger.warning(f"HTML decode warning: {e}")

        # 6. Generic Text Decoder (UTF-8, UTF-16, Latin-1, CP1252)
        for enc in ["utf-8", "utf-8-sig", "utf-16", "latin-1", "cp1252"]:
            try:
                decoded = raw_bytes.decode(enc)
                if decoded and len(decoded.strip()) > 10:
                    return decoded
            except UnicodeDecodeError:
                continue

        # Last resort: ASCII decode ignoring non-printable bytes
        return "".join([chr(b) for b in raw_bytes if 32 <= b <= 126 or b in (10, 13, 9)])

    def _extract_from_image(self, img_bytes: bytes) -> str:
        """Extracts text from image bytes using RapidOCR."""
        if not HAS_OCR or OCR_ENGINE is None:
            logger.warning("OCR engine not available for image parsing.")
            return ""

        try:
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img_np = np.array(image)
            ocr_result, _ = OCR_ENGINE(img_np)

            if not ocr_result:
                return ""

            lines = []
            for item in ocr_result:
                # RapidOCR item format: [box, text, score]
                if len(item) >= 2 and isinstance(item[1], str):
                    text_line = item[1].strip()
                    if text_line:
                        lines.append(text_line)

            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error running OCR on resume image: {e}", exc_info=True)
            return ""

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\r\n|\r", "\n", text)
        text = re.sub(r"\t", " ", text)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        # Strip raw PDF object headers / stream artifacts
        text = re.sub(r"/(?:Type|Subtype|Filter|Length|Width|Height|BitsPerComponent|ColorSpace|XObject|Font|Image)\b[^\n]*", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\b\d+\s+\d+\s+obj\b[\s\S]*?\bendobj\b", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\bstream\b[\s\S]*?\bendstream\b", " ", text, flags=re.IGNORECASE)
        text = re.sub(r" +", " ", text)
        return text.strip()

    def _try_parse_json_resume(self, text: str) -> Optional[Dict[str, Any]]:
        """Parses structured JSON resume schema (e.g. JSONResume standard)."""
        try:
            data = json.loads(text)
            basics = data.get("basics", data)
            name = basics.get("name", "Candidate")
            email = basics.get("email", "Not Provided")
            phone = basics.get("phone", "Not Provided")
            location = basics.get("location", {}).get("city", "Not Specified") if isinstance(basics.get("location"), dict) else str(basics.get("location", "Not Specified"))

            raw_skills = []
            if "skills" in data and isinstance(data["skills"], list):
                for s in data["skills"]:
                    if isinstance(s, dict):
                        raw_skills.append(s.get("name", ""))
                        raw_skills.extend(s.get("keywords", []))
                    elif isinstance(s, str):
                        raw_skills.append(s)

            skills_text = " ".join(raw_skills) + " " + text
            skills_info = self.skill_extractor.extract_skills(skills_text)
            exp_info = self.exp_analyzer.analyze_experience(text)

            return {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "linkedin": basics.get("linkedin", ""),
                "github": basics.get("github", ""),
                "portfolio": basics.get("website", basics.get("url", "")),
                "education": self._extract_education(text, ""),
                "skills": skills_info["skill_names"],
                "skill_ids": skills_info["skill_ids"],
                "skills_by_category": skills_info["by_category"],
                "skills_count": skills_info["total_count"],
                "experience_years": exp_info["estimated_years"],
                "seniority_level": exp_info["seniority_level"],
                "experience_bracket": exp_info["experience_bracket"],
                "action_verb_score": exp_info["action_verb_score"],
                "projects": data.get("projects", []),
                "certifications": [c.get("name", "") if isinstance(c, dict) else str(c) for c in data.get("certificates", data.get("certifications", []))],
                "summary": basics.get("summary", "")[:400]
            }
        except Exception:
            return None

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Explicit Name Matching
        candidate_name = None
        for line in lines[:8]:
            name_m = re.search(r"^(?:Name|Full\s*Name|Candidate\s*Name)\s*[:=]\s*([A-Za-z\s\.\-]{2,40})", line, re.IGNORECASE)
            if name_m:
                candidate_name = name_m.group(1).strip().title()
                break

        # 2. Heuristic Top-Line Name Search
        if not candidate_name:
            noise_words = {
                "RESUME", "CURRICULUM VITAE", "CV", "BIO", "PROFILE", "SUMMARY", "CONTACT",
                "EDUCATION", "EXPERIENCE", "SKILLS", "PROJECTS", "CERTIFICATIONS", "PAGE",
                "ABOUT ME", "OBJECTIVE", "EMAIL", "PHONE", "LINKEDIN", "GITHUB", "PORTFOLIO",
                "TYPE", "XOBJECT", "OBJECT", "STREAM", "ENDSTREAM", "IMAGE", "DOCUMENT",
                "MARKSHEET", "TRANSCRIPT", "STATEMENT", "EXAMINATION", "BOARD", "GOVERNMENT"
            }
            for line in lines[:6]:
                if "@" in line or "http" in line or ".com" in line or re.search(r"\d{3}", line) or "|" in line:
                    continue
                clean_line = re.sub(r"[^a-zA-Z\s\.]", "", line).strip()
                words = clean_line.split()
                if 2 <= len(words) <= 4 and all(len(w) >= 2 for w in words):
                    if not any(w.upper() in noise_words for w in words):
                        candidate_name = clean_line.title()
                        break

        # 3. Email Extraction
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        email = email_match.group(0) if email_match else "Not Provided"

        if not candidate_name and email != "Not Provided":
            prefix = email.split("@")[0]
            parts = re.split(r"[._\-0-9]+", prefix)
            clean_parts = [p.capitalize() for p in parts if len(p) >= 2]
            if 1 <= len(clean_parts) <= 3:
                candidate_name = " ".join(clean_parts)
            else:
                candidate_name = "Candidate"
        elif not candidate_name:
            candidate_name = "Candidate"

        # 4. Phone Extraction
        phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+91[-.\s]?[6-9]\d{9}|\b[6-9]\d{9}\b|\b\d{10}\b", text)
        phone = phone_match.group(0) if phone_match else "Not Provided"

        # 5. Location Extraction
        location = "Not Specified"
        loc_patterns = [
            r"(?:Location|Address|City|Based in)\s*[:=]?\s*([A-Za-z\s,]+)",
            r"\b(Bangalore|Bengaluru|Hyderabad|Pune|Mumbai|Delhi|Noida|Gurgaon|Gurugram|Chennai|Kolkata|Ahmedabad|Jaipur|Kochi|Chandigarh|San Francisco|New York|London|Seattle|Austin|Berlin|Singapore|Remote)\b"
        ]
        for pat in loc_patterns:
            loc_match = re.search(pat, text, re.IGNORECASE)
            if loc_match:
                location = loc_match.group(1).strip().title()
                break

        # 6. LinkedIn & GitHub & Portfolio
        linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_\-\.]+)", text, re.IGNORECASE)
        linkedin = f"linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else ""

        github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_\-\.]+)", text, re.IGNORECASE)
        github = f"github.com/{github_match.group(1)}" if github_match else ""

        portfolio_match = re.search(r"(?:https?://)?(?:www\.)?([a-zA-Z0-9_\-\.]+\.(?:dev|io|me|app|ai|tech|net|org))\b", text, re.IGNORECASE)
        portfolio = f"https://{portfolio_match.group(1)}" if portfolio_match and "github" not in portfolio_match.group(0).lower() and "linkedin" not in portfolio_match.group(0).lower() else ""

        return {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio
        }

    def _segment_sections(self, text: str) -> Dict[str, str]:
        section_headers = {
            "summary": ["summary", "professional summary", "about me", "objective", "profile", "career objective"],
            "education": ["education", "academic background", "academics", "qualifications", "educational details"],
            "experience": ["experience", "work experience", "employment", "professional experience", "internships", "work history"],
            "projects": ["projects", "key projects", "academic projects", "personal projects", "capstone", "technical projects"],
            "skills": ["skills", "technical skills", "core competencies", "technologies", "tech stack", "programming skills"],
            "certifications": ["certifications", "licenses", "courses", "achievements", "publications", "certificates", "awards"]
        }

        header_positions = []
        lines = text.split("\n")

        for idx, line in enumerate(lines):
            clean = line.strip().lower()
            clean = re.sub(r"[^a-z\s]", "", clean)
            for sec_name, keywords in section_headers.items():
                if clean in keywords or any(clean == kw or clean.startswith(kw + " ") for kw in keywords):
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

        degrees = [
            (r"\b(?:Ph\.?D|Doctor of Philosophy|Doctorate)\b", "Ph.D. / Doctorate"),
            (r"\b(?:M\.?Tech|Master of Technology|M\.?E|Master of Engineering|M\.?S|M\.?Sc|Master of Science|M\.?C\.?A|MBA)\b", "Master's Degree"),
            (r"\b(?:B\.?Tech|Bachelor of Technology|B\.?E|Bachelor of Engineering|B\.?S|B\.?Sc|Bachelor of Science|B\.?C\.?A|B\.?Com)\b", "Bachelor's Degree"),
            (r"\b(?:Diploma|Associate Degree|Polytechnic)\b", "Diploma / Associate")
        ]

        detected_degree = "Bachelor's Degree"
        for pat, deg_name in degrees:
            if re.search(pat, text_to_scan, re.IGNORECASE):
                detected_degree = deg_name
                break

        majors = [
            "Artificial Intelligence", "Data Science", "Computer Science", "Information Technology",
            "Software Engineering", "Cybersecurity", "Electrical Engineering", "Electronics and Communication",
            "Mechanical Engineering", "Civil Engineering", "Mathematics", "Statistics", "Data Analytics",
            "Business Administration", "Physics"
        ]
        detected_major = "Computer Science / Related"
        for m in majors:
            if re.search(r"\b" + re.escape(m) + r"\b", text_to_scan, re.IGNORECASE):
                detected_major = m
                break

        inst_match = re.search(r"\b([A-Za-z\s]+(?:University|Institute|College|Academy|IIT|NIT|BITS|VIT|IIIT))\b", text_to_scan, re.IGNORECASE)
        institution = inst_match.group(1).strip() if inst_match else "Accredited University"

        gpa_match = re.search(r"(?:CGPA|GPA|Score|Percentage|Marks)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:/|out of)?\s*(?:10|100|4\.0|4)?%?", text_to_scan, re.IGNORECASE)
        gpa_str = gpa_match.group(0) if gpa_match else "N/A"

        year_match = re.search(r"\b(201\d|202\d)\b", text_to_scan)
        grad_year = year_match.group(0) if year_match else "Recent"

        return {
            "degree": detected_degree,
            "major": detected_major,
            "institution": institution,
            "gpa": gpa_str,
            "graduation_year": grad_year
        }

    def _extract_projects(self, full_text: str, project_section: str) -> List[Dict[str, str]]:
        text_to_scan = project_section if project_section else full_text
        projects = []
        lines = text_to_scan.split("\n")
        current_project = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if re.match(r"^(?:\d+\.|\*|\-|\•)\s+([A-Za-z0-9\s\-\:\/]+)", line_str) or (line_str.isupper() and 5 < len(line_str) < 60):
                if current_project:
                    projects.append(current_project)
                title = re.sub(r"^(?:\d+\.|\*|\-|\•)\s*", "", line_str)
                current_project = {"title": title, "description": ""}
            elif current_project:
                current_project["description"] += " " + line_str

        if current_project:
            projects.append(current_project)

        return projects[:6]

    def _extract_certifications(self, full_text: str, cert_section: str) -> List[str]:
        text_to_scan = cert_section if cert_section else full_text
        certs = []
        for line in text_to_scan.split("\n"):
            clean = line.strip().strip("-*•").strip()
            if len(clean) > 4 and any(kw in clean.lower() for kw in [
                "certified", "certificate", "specialization", "course", "badge",
                "associate", "professional", "coursera", "udemy", "aws certified",
                "gcp", "azure", "kubernetes", "cisco", "oracle", "deep learning.ai"
            ]):
                certs.append(clean)
        return certs[:8]

    def validate_is_resume(self, text: str) -> dict:
        """
        Checks whether extracted text looks like a genuine resume/CV.
        Rejects standalone marksheets, transcripts, certificates, invoices, official docs, and non-resume files,
        while ensuring resumes with education milestones (CBSE, ICSE, SGPA, grades) are accurately accepted.
        Returns {"is_resume": bool, "reason": str, "confidence": float}
        """
        import re

        if not text or len(text.strip()) < 80:
            return {
                "is_resume": False,
                "reason": "The document is too short or contains no readable text. Please upload your resume in PDF, Word DOCX, Image, or TXT format.",
                "confidence": 0.0
            }

        text_lower = text.lower()

        # 1. Definitive Standalone Marksheet / Academic Transcript phrases
        # Note: Non-discriminative terms (e.g. CBSE, ICSE, Class 10/12, SGPA, DOB) are excluded
        # because legitimate resumes commonly list these education milestones.
        definitive_marksheet_phrases = [
            "statement of marks", "marks statement", "marks memo", "memo of marks",
            "mark sheet", "marksheet", "grade sheet", "grade card", "tabulation sheet",
            "transcript of records", "academic transcript", "consolidated marks memo",
            "controller of examinations", "board of examination", "board of examinations",
            "total marks obtained", "maximum marks", "minimum marks", "marks obtained",
            "internal assessment marks", "theory marks", "practical marks",
            "hall ticket no", "admit card no", "sub code", "subject code"
        ]

        certificate_keywords = [
            "this is to certify that", "hereby certify that", "certificate of completion",
            "certificate of participation", "certificate of achievement", "certificate of excellence",
            "this certificate is awarded to", "has successfully completed the course",
            "in recognition of active participation", "provisional certificate"
        ]

        financial_keywords = [
            "tax invoice", "invoice no", "bill to:", "ship to:", "total amount due",
            "payment due date", "bank account statement", "remittance advice"
        ]

        official_doc_keywords = [
            "unique identification authority of india", "income tax department",
            "election commission of india", "driving licence", "driving license",
            "passport no", "aadhaar number"
        ]

        # 2. Positive Resume Section Headers
        resume_section_headers = [
            "work experience", "professional experience", "employment history", "work history",
            "technical skills", "core competencies", "skills & competencies", "key skills", "skills",
            "projects", "personal projects", "key projects", "academic projects", "technical projects",
            "certifications", "licenses & certifications", "career summary", "professional summary", "summary",
            "education", "educational qualification", "academic background", "academics",
            "achievements", "publications", "volunteer experience", "internship experience", "internships"
        ]

        # Valid contact patterns (Email, LinkedIn, GitHub, formatted phone number, portfolio)
        contact_patterns = [
            r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}",
            r"linkedin\.com/in/",
            r"github\.com/",
            r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+91[-.\s]?[6-9]\d{9}|\b[6-9]\d{9}\b",
            r"(?:https?://)?(?:www\.)?[a-zA-Z0-9_\-\.]+\.(?:dev|io|me|app|ai|tech)"
        ]

        career_keywords = [
            "bachelor", "master", "b.tech", "b.e.", "m.tech", "m.s.", "m.sc", "b.sc", "bca", "mca", "mba", "ph.d",
            "software engineer", "developer", "data scientist", "data analyst", "ml engineer", "intern", "consultant",
            "responsible for", "developed", "designed", "managed", "implemented", "built", "created", "collaborated",
            "spearheaded", "engineered", "optimized", "python", "java", "sql", "machine learning", "pytorch",
            "tensorflow", "react", "node.js", "aws", "docker", "kubernetes", "git"
        ]

        # Extract skills count as strong domain signal
        skills_info = self.skill_extractor.extract_skills(text)
        extracted_skills_count = skills_info.get("total_count", 0)

        # Check negative signals
        marksheet_hits = [k for k in definitive_marksheet_phrases if k in text_lower]
        cert_hits = [k for k in certificate_keywords if k in text_lower]
        fin_hits = [k for k in financial_keywords if k in text_lower]
        off_hits = [k for k in official_doc_keywords if k in text_lower]

        # Check positive signals
        matched_headers = sum(1 for h in resume_section_headers if h in text_lower)
        matched_contacts = sum(1 for p in contact_patterns if re.search(p, text_lower))
        matched_career = sum(1 for k in career_keywords if k in text_lower)

        # Compute positive resume score
        header_score = min(matched_headers * 15, 45)
        contact_score = min(matched_contacts * 15, 30)
        career_score = min(max(extracted_skills_count * 4, matched_career * 3), 35)
        resume_score = header_score + contact_score + career_score

        has_strong_resume_structure = (
            (matched_headers >= 2 and (matched_contacts >= 1 or extracted_skills_count >= 1 or matched_career >= 2)) or
            (matched_headers >= 1 and matched_contacts >= 1 and (extracted_skills_count >= 2 or matched_career >= 3)) or
            (resume_score >= 45 and matched_contacts >= 1)
        )

        non_resume_score = 0
        rejection_reason = ""

        # Only evaluate non-resume documents if the text lacks strong resume structure
        if not has_strong_resume_structure:
            if len(marksheet_hits) >= 2 or (len(marksheet_hits) == 1 and matched_headers == 0 and matched_contacts == 0):
                non_resume_score += len(marksheet_hits) * 35
                rejection_reason = (
                    "This document appears to be a standalone marksheet or academic transcript, not a complete resume. "
                    "Please upload your resume/CV containing your experience, skills, and summary."
                )
            elif len(cert_hits) >= 1 and matched_headers < 2 and extracted_skills_count < 2:
                non_resume_score += len(cert_hits) * 35
                rejection_reason = (
                    "This document looks like an individual course certificate or completion letter. "
                    "Please upload your full resume/CV instead."
                )
            elif (len(fin_hits) + len(off_hits)) >= 1 and resume_score < 30:
                non_resume_score += 40
                rejection_reason = (
                    "This looks like an invoice, bill, or government ID document, not a resume. "
                    "Please upload your resume/CV."
                )
            elif resume_score < 25 or (matched_headers < 1 and matched_contacts == 0):
                rejection_reason = (
                    "This document doesn't appear to be a resume. "
                    "No resume sections (Experience, Skills, Education) or contact information were detected. "
                    "Please upload your CV or resume in PDF, Word DOCX, Image, or TXT format."
                )

        total = resume_score + non_resume_score
        confidence = resume_score / total if total > 0 else (0.90 if has_strong_resume_structure else 0.0)

        is_resume = not bool(rejection_reason) and (has_strong_resume_structure or (resume_score >= 25 and non_resume_score == 0))

        return {
            "is_resume": is_resume,
            "reason": rejection_reason if not is_resume else "Resume detected successfully.",
            "confidence": round(min(confidence, 1.0), 2),
            "debug": {
                "resume_score": resume_score,
                "non_resume_score": non_resume_score,
                "matched_headers": matched_headers,
                "matched_contacts": matched_contacts,
                "extracted_skills_count": extracted_skills_count,
                "has_strong_resume_structure": has_strong_resume_structure,
                "marksheet_hits": marksheet_hits,
            }
        }


