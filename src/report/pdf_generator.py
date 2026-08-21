"""
PDF Report Generator for Career Intelligence Engine.
Builds professional candidate evaluation and career roadmap PDF reports using ReportLab.
"""

import io
from datetime import datetime
from typing import Dict, Any, List
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
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=6
        )
        self.subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=self.styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=12
        )
        self.section_heading = ParagraphStyle(
            "SecHead",
            parent=self.styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1E40AF"),
            spaceBefore=10,
            spaceAfter=6
        )
        self.body_style = ParagraphStyle(
            "Body",
            parent=self.styles["Normal"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1F2937")
        )
        self.bold_body = ParagraphStyle(
            "BoldBody",
            parent=self.styles["Normal"],
            fontSize=9.5,
            leading=13,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#111827")
        )
        self.kpi_title = ParagraphStyle(
            "KPITitle",
            parent=self.styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#6B7280"),
            alignment=1
        )
        self.kpi_value = ParagraphStyle(
            "KPIValue",
            parent=self.styles["Normal"],
            fontSize=14,
            leading=16,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1E3A8A"),
            alignment=1
        )

    def generate_report(
        self,
        candidate_profile: Dict[str, Any],
        target_role: str,
        gap_analysis: Dict[str, Any],
        salary_info: Dict[str, Any],
        roadmap: Dict[str, Any],
        top_jobs: List[Dict[str, Any]]
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
            topMargin=36,
            bottomMargin=36
        )

        story = []
        now_str = datetime.now().strftime("%B %d, %Y")

        # 1. Header Banner
        story.append(Paragraph("CAREER INTELLIGENCE ENGINE", self.title_style))
        story.append(Paragraph(f"Comprehensive AI Career Readiness & Roadmap Report • Generated on {now_str}", self.subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=12))

        # 2. Candidate Overview & Executive KPI Grid
        name = candidate_profile.get("name", "Candidate")
        email = candidate_profile.get("email", "N/A")
        exp_years = candidate_profile.get("experience_years", 0.0)
        degree = candidate_profile.get("education", {}).get("degree", "Bachelor's Degree")
        readiness = gap_analysis.get("readiness_score", 0.0)
        salary_est = salary_info.get("formatted_range", "N/A")
        
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
                Paragraph(degree, self.body_style)
            ],
            [
                Paragraph("<b>Target Role:</b>", self.body_style),
                Paragraph(f"<b>{gap_analysis.get('role_title', target_role)}</b>", self.bold_body),
                Paragraph("<b>Skills Detected:</b>", self.body_style),
                Paragraph(str(len(candidate_profile.get("skills", []))), self.body_style)
            ]
        ]
        t_profile = Table(profile_data, colWidths=[90, 180, 80, 190])
        t_profile.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_profile)
        story.append(Spacer(1, 10))

        # KPI Summary Cards
        kpi_data = [
            [
                Paragraph("CAREER READINESS", self.kpi_title),
                Paragraph("ESTIMATED MARKET SALARY", self.kpi_title),
                Paragraph("CRITICAL GAPS TO CLOSE", self.kpi_title),
                Paragraph("ESTIMATED ROADMAP TIME", self.kpi_title)
            ],
            [
                Paragraph(f"{readiness}%", self.kpi_value),
                Paragraph(salary_est, self.kpi_value),
                Paragraph(str(len(gap_analysis.get("missing_skills", []))), self.kpi_value),
                Paragraph(f"{roadmap.get('total_estimated_weeks', 8)} Weeks", self.kpi_value)
            ]
        ]
        t_kpi = Table(kpi_data, colWidths=[135, 135, 135, 135])
        t_kpi.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3B82F6")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t_kpi)
        story.append(Spacer(1, 14))

        # 3. Skill Gap Breakdown Section
        story.append(Paragraph("1. Granular Skill Gap Analysis", self.section_heading))
        
        strong_skills = [s["name"] for s in gap_analysis.get("strong_skills", [])]
        missing_skills = [s["name"] for s in gap_analysis.get("missing_skills", [])]
        imp_skills = [s["name"] for s in gap_analysis.get("improvement_skills", [])]

        gap_table_data = [
            [
                Paragraph("<b>Mastered & Strong Skills</b>", self.bold_body),
                Paragraph("<b>High-Priority Skill Gaps</b>", self.bold_body),
                Paragraph("<b>Secondary Improvements</b>", self.bold_body)
            ],
            [
                Paragraph(", ".join(strong_skills[:8]) if strong_skills else "None detected", self.body_style),
                Paragraph(", ".join(missing_skills[:8]) if missing_skills else "No critical gaps!", self.body_style),
                Paragraph(", ".join(imp_skills[:8]) if imp_skills else "None", self.body_style)
            ]
        ]
        t_gap = Table(gap_table_data, colWidths=[180, 180, 180])
        t_gap.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#D1FAE5")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FEE2E2")),
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#FEF3C7")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t_gap)
        story.append(Spacer(1, 14))

        # 4. Actionable Learning Roadmap
        story.append(Paragraph("2. Personalized Phased Learning Pathway", self.section_heading))
        
        roadmap_rows = [[
            Paragraph("<b>Phase & Goal</b>", self.bold_body),
            Paragraph("<b>Duration</b>", self.bold_body),
            Paragraph("<b>Key Skills to Cover</b>", self.bold_body),
            Paragraph("<b>Milestone Capstone</b>", self.bold_body)
        ]]
        
        for p in roadmap.get("phases", [])[:4]:
            skills_list = ", ".join([s["name"] for s in p.get("skills", [])[:4]])
            milestone = p.get("skills", [{}])[0].get("milestone_project", "Build hands-on milestone project")[:80] + "..."
            roadmap_rows.append([
                Paragraph(f"<b>{p.get('title', 'Phase')}</b><br/><font color='#4B5563'>{p.get('goal', '')[:65]}</font>", self.body_style),
                Paragraph(f"{p.get('duration_weeks', 2)} Wks", self.body_style),
                Paragraph(skills_list, self.body_style),
                Paragraph(milestone, self.body_style)
            ])

        t_roadmap = Table(roadmap_rows, colWidths=[160, 45, 160, 175])
        t_roadmap.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_roadmap)
        story.append(Spacer(1, 14))

        # 5. Top Recommended Jobs
        story.append(Paragraph("3. Top Matching Job Opportunities", self.section_heading))
        job_rows = [[
            Paragraph("<b>Job Title & Company</b>", self.bold_body),
            Paragraph("<b>Location</b>", self.bold_body),
            Paragraph("<b>Comp. Range</b>", self.bold_body),
            Paragraph("<b>Match %</b>", self.bold_body)
        ]]
        
        for job in top_jobs[:5]:
            job_rows.append([
                Paragraph(f"<b>{job.get('title', 'Role')}</b><br/><font color='#2563EB'>{job.get('company', 'Company')}</font>", self.body_style),
                Paragraph(job.get("location", "India"), self.body_style),
                Paragraph(job.get("salary_formatted", "N/A"), self.body_style),
                Paragraph(f"<b>{job.get('match_score', 0)}%</b>", self.bold_body)
            ])

        t_jobs = Table(job_rows, colWidths=[200, 120, 140, 80])
        t_jobs.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_jobs)
        story.append(Spacer(1, 14))

        # Footer Notice
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=10, spaceAfter=6))
        story.append(Paragraph(
            "<font color='#9CA3AF' size='7.5'>Note: Salary estimations and match percentages are generated via predictive machine learning models based on current job market data benchmarks and are provided as evaluative guidance.</font>",
            self.body_style
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
