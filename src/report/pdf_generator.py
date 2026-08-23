"""
PDF Report Generator for Career Intelligence Engine v2.
Builds professional candidate evaluation, ATS score diagnostics, and career roadmap PDF reports using ReportLab.
"""

import io
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class CareerReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()

    def _init_custom_styles(self):
        self.title_style = ParagraphStyle(
            "DocTitle",
            parent=self.styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#4F46E5"),
            spaceAfter=4
        )
        self.subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=self.styles["Normal"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#6B7280"),
            spaceAfter=10
        )
        self.section_heading = ParagraphStyle(
            "SecHead",
            parent=self.styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#312E81"),
            spaceBefore=8,
            spaceAfter=5
        )
        self.body_style = ParagraphStyle(
            "Body",
            parent=self.styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1A1A18")
        )
        self.bold_body = ParagraphStyle(
            "BoldBody",
            parent=self.styles["Normal"],
            fontSize=9,
            leading=12,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#111827")
        )
        self.kpi_title = ParagraphStyle(
            "KPITitle",
            parent=self.styles["Normal"],
            fontSize=7.5,
            leading=9,
            textColor=colors.HexColor("#6B7280"),
            alignment=1
        )
        self.kpi_value = ParagraphStyle(
            "KPIValue",
            parent=self.styles["Normal"],
            fontSize=13,
            leading=15,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#4F46E5"),
            alignment=1
        )

    def generate_report(
        self,
        candidate_profile: Dict[str, Any],
        target_role: str,
        gap_analysis: Dict[str, Any],
        salary_info: Dict[str, Any],
        roadmap: Dict[str, Any],
        top_jobs: List[Dict[str, Any]],
        ats_results: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Builds and returns the binary PDF content.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=32,
            bottomMargin=32
        )

        story = []
        now_str = datetime.now().strftime("%B %d, %Y")

        # 1. Header Banner
        story.append(Paragraph("CAREER INTELLIGENCE ENGINE v2", self.title_style))
        story.append(Paragraph(f"AI Career Readiness, ATS Diagnostics & Phased Learning Roadmap • {now_str}", self.subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceAfter=10))

        # 2. Candidate Overview & Executive KPI Grid
        name = candidate_profile.get("name", "Candidate")
        email = candidate_profile.get("email", "N/A")
        exp_years = candidate_profile.get("experience_years", 0.0)
        degree = candidate_profile.get("education", {}).get("degree", "Bachelor's Degree") if isinstance(candidate_profile.get("education"), dict) else "Bachelor's Degree"
        readiness = gap_analysis.get("readiness_score", 0.0)
        salary_est = salary_info.get("formatted_range", "N/A")
        ats_score = ats_results.get("total", 75) if ats_results else 75
        
        # Profile Data Table
        profile_data = [
            [
                Paragraph("<b>Candidate Name:</b>", self.body_style),
                Paragraph(name, self.bold_body),
                Paragraph("<b>Email:</b>", self.body_style),
                Paragraph(email, self.body_style)
            ],
            [
                Paragraph("<b>Experience:</b>", self.body_style),
                Paragraph(f"{exp_years} yrs ({candidate_profile.get('seniority_level', 'Fresher')})", self.body_style),
                Paragraph("<b>Education:</b>", self.body_style),
                Paragraph(str(degree), self.body_style)
            ],
            [
                Paragraph("<b>Target Goal Role:</b>", self.body_style),
                Paragraph(f"<b>{gap_analysis.get('role_title', target_role)}</b>", self.bold_body),
                Paragraph("<b>Skills Detected:</b>", self.body_style),
                Paragraph(str(len(candidate_profile.get("skills", []))), self.body_style)
            ]
        ]
        t_profile = Table(profile_data, colWidths=[90, 180, 80, 190])
        t_profile.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F7F5")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E8E6E0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E8E6E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_profile)
        story.append(Spacer(1, 8))

        # KPI Summary Cards (Now including ATS Compatibility)
        kpi_data = [
            [
                Paragraph("ATS SCORE", self.kpi_title),
                Paragraph("ROLE READINESS", self.kpi_title),
                Paragraph("TARGET SALARY", self.kpi_title),
                Paragraph("ROADMAP TIME", self.kpi_title)
            ],
            [
                Paragraph(f"{ats_score}/100", self.kpi_value),
                Paragraph(f"{int(readiness)}%", self.kpi_value),
                Paragraph(salary_est, self.kpi_value),
                Paragraph(f"{roadmap.get('total_estimated_weeks', 8)} Weeks", self.kpi_value)
            ]
        ]
        t_kpi = Table(kpi_data, colWidths=[135, 135, 135, 135])
        t_kpi.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF2FF")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#4F46E5")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D2FE")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_kpi)
        story.append(Spacer(1, 10))

        # 3. ATS Screening Diagnostics (If available)
        if ats_results:
            story.append(Paragraph("1. ATS Screening Diagnostics & Actionable Fixes", self.section_heading))
            ats_rows = [
                [
                    Paragraph("<b>Keywords Sub-Score:</b>", self.body_style),
                    Paragraph(f"{int(ats_results.get('keyword', 0))}%", self.bold_body),
                    Paragraph("<b>Format Sub-Score:</b>", self.body_style),
                    Paragraph(f"{int(ats_results.get('format', 0))}%", self.bold_body),
                    Paragraph("<b>Experience Depth:</b>", self.body_style),
                    Paragraph(f"{int(ats_results.get('experience', 0))}%", self.bold_body),
                ]
            ]
            t_ats_sub = Table(ats_rows, colWidths=[110, 60, 110, 60, 120, 80])
            t_ats_sub.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F7F5")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E8E6E0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E8E6E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t_ats_sub)
            story.append(Spacer(1, 6))

            issues_text = "<br/>".join([f"• {iss}" for iss in ats_results.get("issues", [])[:4]])
            wins_text = "<br/>".join([f"• {w}" for w in ats_results.get("wins", [])[:4]])

            iw_data = [
                [
                    Paragraph("<b>Key Strengths (What's Working)</b>", self.bold_body),
                    Paragraph("<b>High-Priority Actionable Fixes</b>", self.bold_body)
                ],
                [
                    Paragraph(wins_text if wins_text else "None", self.body_style),
                    Paragraph(issues_text if issues_text else "No critical issues detected", self.body_style)
                ]
            ]
            t_iw = Table(iw_data, colWidths=[270, 270])
            t_iw.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#DCFCE7")),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FEE2E2")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(t_iw)
            story.append(Spacer(1, 10))

        # 4. Skill Gap Breakdown Section
        story.append(Paragraph("2. Skill Gap Decomposition", self.section_heading))
        strong_skills = [s["name"] for s in gap_analysis.get("strong_skills", [])]
        missing_skills = [s["name"] for s in gap_analysis.get("missing_skills", [])]
        imp_skills = [s["name"] for s in gap_analysis.get("improvement_skills", [])]

        gap_table_data = [
            [
                Paragraph("<b>Mastered Skills (Have)</b>", self.bold_body),
                Paragraph("<b>Critical Missing Gaps</b>", self.bold_body),
                Paragraph("<b>In-Progress / Related</b>", self.bold_body)
            ],
            [
                Paragraph(", ".join(strong_skills[:8]) if strong_skills else "None detected", self.body_style),
                Paragraph(", ".join(missing_skills[:8]) if missing_skills else "No critical gaps!", self.body_style),
                Paragraph(", ".join(imp_skills[:8]) if imp_skills else "None", self.body_style)
            ]
        ]
        t_gap = Table(gap_table_data, colWidths=[180, 180, 180])
        t_gap.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#DCFCE7")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FEE2E2")),
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#FEF3C7")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_gap)
        story.append(Spacer(1, 10))

        # 5. Phased Learning Pathway
        story.append(Paragraph("3. Phased Learning Pathway to Goal", self.section_heading))
        roadmap_rows = [[
            Paragraph("<b>Phase & Goal</b>", self.bold_body),
            Paragraph("<b>Duration</b>", self.bold_body),
            Paragraph("<b>Key Deliverables</b>", self.bold_body),
            Paragraph("<b>Milestone Capstone</b>", self.bold_body)
        ]]
        
        for p in roadmap.get("phases", [])[:4]:
            skills_list = ", ".join([s["name"] for s in p.get("skills", [])[:4]])
            milestone = p.get("skills", [{}])[0].get("milestone_project", "Build hands-on milestone project")[:75] + "..."
            roadmap_rows.append([
                Paragraph(f"<b>{p.get('title', 'Phase')}</b><br/><font color='#4B5563'>{p.get('goal', '')[:60]}</font>", self.body_style),
                Paragraph(f"{p.get('duration_weeks', 2)} Wks", self.body_style),
                Paragraph(skills_list, self.body_style),
                Paragraph(milestone, self.body_style)
            ])

        t_roadmap = Table(roadmap_rows, colWidths=[150, 45, 165, 180])
        t_roadmap.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_roadmap)
        story.append(Spacer(1, 10))

        # 6. Top Recommended Jobs
        story.append(Paragraph("4. Top Matching Job Opportunities", self.section_heading))
        job_rows = [[
            Paragraph("<b>Job Title & Company</b>", self.bold_body),
            Paragraph("<b>Location</b>", self.bold_body),
            Paragraph("<b>Comp. Range</b>", self.bold_body),
            Paragraph("<b>Match %</b>", self.bold_body)
        ]]
        
        for job in top_jobs[:5]:
            job_rows.append([
                Paragraph(f"<b>{job.get('title', 'Role')}</b><br/><font color='#4F46E5'>{job.get('company', 'Company')}</font>", self.body_style),
                Paragraph(job.get("location", "India"), self.body_style),
                Paragraph(job.get("salary_formatted", "N/A"), self.body_style),
                Paragraph(f"<b>{job.get('match_score', 0)}%</b>", self.bold_body)
            ])

        t_jobs = Table(job_rows, colWidths=[200, 120, 140, 80])
        t_jobs.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_jobs)
        story.append(Spacer(1, 10))

        # Footer Notice
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=8, spaceAfter=4))
        story.append(Paragraph(
            "<font color='#9CA3AF' size='7'>Career Intelligence Engine v2 • Evaluative guidance based on automated ATS screening rules, NLP vector extraction, and market benchmarks.</font>",
            self.body_style
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
