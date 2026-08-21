"""
Career Intelligence Engine - Streamlit Interactive Web Application.
AI-Powered Career Recommendation, Skill Gap Analysis, Salary Prediction & Job Matching Dashboard.
"""

import json
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.config import (
    ONTOLOGY_PATH,
    SAMPLE_RESUMES_DIR,
    CATEGORY_COLORS,
    SKILL_LEVEL_COLORS
)
from src.nlp.parser import ResumeParser
from src.nlp.skill_extractor import SkillExtractor
from src.models.matcher import JobMatcher
from src.models.role_classifier import RoleClassifier
from src.models.salary_predictor import SalaryPredictor
from src.engine.gap_analyzer import SkillGapAnalyzer
from src.engine.roadmap_generator import RoadmapGenerator
from src.engine.explainability import ExplainabilityEngine
from src.engine.simulator import CareerSimulator
from src.engine.market_analyzer import MarketAnalyzer
from src.report.pdf_generator import CareerReportGenerator

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Career Intelligence Engine | AI Career Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Styling (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38BDF8;
        margin: 5px 0;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
    }
    .badge-strong {
        background-color: #065F46;
        color: #6EE7B7;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
    }
    .badge-imp {
        background-color: #78350F;
        color: #FCD34D;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
    }
    .badge-missing {
        background-color: #881337;
        color: #FDA4AF;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
    }
    .job-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 18px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 15px;
        border: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #0F172A;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        border-bottom: 2px solid #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Singleton Resource Initialization (Cached)
# ---------------------------------------------------------
@st.cache_resource
def load_engine_components():
    parser = ResumeParser()
    extractor = SkillExtractor()
    matcher = JobMatcher()
    role_classifier = RoleClassifier()
    salary_predictor = SalaryPredictor()
    gap_analyzer = SkillGapAnalyzer()
    roadmap_generator = RoadmapGenerator()
    explainability = ExplainabilityEngine()
    simulator = CareerSimulator()
    market_analyzer = MarketAnalyzer()
    pdf_gen = CareerReportGenerator()
    
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        ontology = json.load(f)
        
    return {
        "parser": parser,
        "extractor": extractor,
        "matcher": matcher,
        "role_classifier": role_classifier,
        "salary_predictor": salary_predictor,
        "gap_analyzer": gap_analyzer,
        "roadmap_generator": roadmap_generator,
        "explainability": explainability,
        "simulator": simulator,
        "market_analyzer": market_analyzer,
        "pdf_gen": pdf_gen,
        "ontology": ontology
    }

components = load_engine_components()
parser = components["parser"]
extractor = components["extractor"]
matcher = components["matcher"]
role_classifier = components["role_classifier"]
salary_predictor = components["salary_predictor"]
gap_analyzer = components["gap_analyzer"]
roadmap_generator = components["roadmap_generator"]
explainability = components["explainability"]
simulator = components["simulator"]
market_analyzer = components["market_analyzer"]
pdf_gen = components["pdf_gen"]
ontology = components["ontology"]
roles_dict = ontology["roles"]


# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "candidate_profile" not in st.session_state:
    # Load default sample resume (Data Analyst Candidate)
    default_sample_path = os.path.join(SAMPLE_RESUMES_DIR, "data_analyst_candidate.txt")
    if os.path.exists(default_sample_path):
        parsed = parser.parse(default_sample_path)
        st.session_state.candidate_profile = parsed["profile"]
        st.session_state.raw_text = parsed["raw_text"]
    else:
        st.session_state.candidate_profile = {
            "name": "Alex Mercer",
            "email": "alex.mercer@email.com",
            "skills": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Power BI"],
            "skill_ids": ["python", "sql", "pandas", "numpy", "scikit_learn", "power_bi"],
            "experience_years": 1.5,
            "seniority_level": "Junior Associate",
            "education": {"degree": "Bachelor's Degree", "major": "Computer Science"}
        }
        st.session_state.raw_text = "Python, SQL, Pandas, NumPy, Scikit-learn, Power BI"

if "target_role_id" not in st.session_state:
    st.session_state.target_role_id = "data_scientist"


# ---------------------------------------------------------
# Sidebar Navigation & Controls
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
    st.title("Career Intelligence Engine")
    st.caption("AI-Powered Recommendation & Market Intelligence")
    st.markdown("---")

    st.subheader("🎯 Active Target Career")
    role_options = {k: v["title"] for k, v in roles_dict.items()}
    selected_role_id = st.selectbox(
        "Choose Target Role for Analysis:",
        options=list(role_options.keys()),
        format_func=lambda x: role_options[x],
        index=list(role_options.keys()).index(st.session_state.target_role_id) if st.session_state.target_role_id in role_options else 0
    )
    st.session_state.target_role_id = selected_role_id
    
    st.markdown("---")
    st.subheader("📁 Candidate Profile Preset")
    sample_choice = st.selectbox(
        "Load Pre-built Test Candidate:",
        [
            "Custom (Upload / Current)",
            "Om Prakash (Data Analyst)",
            "Aarav Mehta (Data Scientist)",
            "Priya Sharma (ML Engineer)",
            "Rohan Gupta (Fresher)"
        ]
    )

    if sample_choice == "Om Prakash (Data Analyst)":
        p = parser.parse(os.path.join(SAMPLE_RESUMES_DIR, "data_analyst_candidate.txt"))
        st.session_state.candidate_profile = p["profile"]
        st.session_state.raw_text = p["raw_text"]
    elif sample_choice == "Aarav Mehta (Data Scientist)":
        p = parser.parse(os.path.join(SAMPLE_RESUMES_DIR, "data_scientist_candidate.txt"))
        st.session_state.candidate_profile = p["profile"]
        st.session_state.raw_text = p["raw_text"]
    elif sample_choice == "Priya Sharma (ML Engineer)":
        p = parser.parse(os.path.join(SAMPLE_RESUMES_DIR, "ml_engineer_candidate.txt"))
        st.session_state.candidate_profile = p["profile"]
        st.session_state.raw_text = p["raw_text"]
    elif sample_choice == "Rohan Gupta (Fresher)":
        p = parser.parse(os.path.join(SAMPLE_RESUMES_DIR, "fresh_graduate_candidate.txt"))
        st.session_state.candidate_profile = p["profile"]
        st.session_state.raw_text = p["raw_text"]

    st.markdown("---")
    profile = st.session_state.candidate_profile
    st.markdown(f"**Candidate:** {profile.get('name', 'Candidate')}")
    st.markdown(f"**Experience:** {profile.get('experience_years', 0.0)} yrs ({profile.get('seniority_level', 'Fresher')})")
    st.markdown(f"**Skills Detected:** {len(profile.get('skills', []))} skills")


# ---------------------------------------------------------
# Dynamic Calculations for Current Profile & Target Role
# ---------------------------------------------------------
profile = st.session_state.candidate_profile
target_role_id = st.session_state.target_role_id
target_role_meta = roles_dict.get(target_role_id, {})

# Compute Role Predictions (Role Classifier)
recommended_roles = role_classifier.predict_roles(profile.get("skill_ids", []), top_n=4)
top_matched_role = recommended_roles[0] if recommended_roles else {"title": "Data Analyst", "confidence_score": 85.0}

# Compute Skill Gap Analysis
gap_results = gap_analyzer.analyze_gap(profile.get("skill_ids", []), target_role_id)
readiness_score = gap_results.get("readiness_score", 50.0)

# Compute Salary Prediction
salary_results = salary_predictor.predict_salary(
    role_id=target_role_id,
    experience_years=profile.get("experience_years", 0.0),
    skill_count=len(profile.get("skills", [])),
    education=profile.get("education", {}).get("degree", "Bachelor's Degree")
)

# Compute Job Matches
matched_jobs = matcher.match_jobs(profile, target_role_id=target_role_id, top_n=15)
overall_matched_jobs = matcher.match_jobs(profile, target_role_id="all", top_n=15)

# Compute Roadmap
roadmap_data = roadmap_generator.generate_roadmap(gap_results)

# Compute Explainability
xai_explanation = explainability.explain_match_score(
    candidate_profile=profile,
    target_role=target_role_meta,
    gap_analysis=gap_results,
    match_breakdown={}
)


# ---------------------------------------------------------
# Main Tabs Navigation
# ---------------------------------------------------------
tab_dashboard, tab_resume, tab_matches, tab_gaps, tab_simulator, tab_market, tab_report = st.tabs([
    "🏠 Dashboard",
    "📄 Resume Analyzer",
    "💼 Job Matching",
    "🎯 Skill Gap & Roadmap",
    "🧪 What-If Simulator & XAI",
    "📈 Market Intelligence",
    "📑 Export PDF Report"
])


# =========================================================
# TAB 1: EXECUTIVE DASHBOARD
# =========================================================
with tab_dashboard:
    st.markdown(f"## 🚀 Career Intelligence Dashboard: **{profile.get('name', 'Candidate')}**")
    st.caption(f"Evaluating candidate profile against target role: **{target_role_meta.get('title', 'Role')}**")

    # 4 Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Target Role Readiness</div>
            <div class="metric-value">{readiness_score}%</div>
            <div style="color: #10B981; font-size: 0.8rem;">● {xai_explanation.get('summary_verdict', 'Ready')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Best Role Match</div>
            <div class="metric-value" style="font-size: 1.4rem; padding-top: 10px; color: #A78BFA;">{top_matched_role.get('title', 'Role')}</div>
            <div style="color: #94A3B8; font-size: 0.8rem;">{top_matched_role.get('confidence_score', 0)}% ML Confidence</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Predicted Market Salary</div>
            <div class="metric-value" style="font-size: 1.4rem; padding-top: 10px; color: #34D399;">{salary_results.get('formatted_median', 'N/A')}</div>
            <div style="color: #94A3B8; font-size: 0.8rem;">Range: {salary_results.get('formatted_range', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Critical Skill Gaps</div>
            <div class="metric-value" style="color: #F87171;">{len(gap_results.get('missing_skills', []))}</div>
            <div style="color: #94A3B8; font-size: 0.8rem;">Top Gap: {gap_results.get('top_priority_to_learn', ['None'])[0] if gap_results.get('top_priority_to_learn') else 'None'}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gauge Chart & Top Recommended Roles
    c_left, c_right = st.columns([1.2, 1.8])
    with c_left:
        st.subheader("🎯 Role Readiness Gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=readiness_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"<b>{target_role_meta.get('title', 'Target Role')}</b>", 'font': {'size': 18, 'color': '#F8FAFC'}},
            delta={'reference': 70.0, 'increasing': {'color': "#10B981"}, 'decreasing': {'color': "#EF4444"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                'bar': {'color': "#38BDF8"},
                'bgcolor': "#1E293B",
                'borderwidth': 2,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.25)'},
                    {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.25)'},
                    {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.25)'}
                ],
                'threshold': {
                    'line': {'color': "#10B981", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_gauge, use_container_width=True)

    with c_right:
        st.subheader("🤖 AI Career Recommendations")
        st.caption("Supervised ML model role predictions ranked by candidate skill profile:")
        
        for r in recommended_roles:
            c1, c2, c3 = st.columns([2.5, 1.5, 1])
            with c1:
                st.markdown(f"**{r['title']}** <span style='font-size:0.75rem; color:#94A3B8;'>({r['category']})</span>", unsafe_allow_html=True)
                st.progress(r["confidence_score"] / 100.0)
            with c2:
                st.markdown(f"<span style='color:#34D399; font-weight:600;'>₹{r['base_salary_min_lpa']}L - ₹{r['base_salary_max_lpa']}L</span>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"**{r['confidence_score']}%**")
            st.markdown("<hr style='margin:4px 0; border-color:#334155;'>", unsafe_allow_html=True)

    # Quick Snapshot of Gaps & Next Actions
    st.markdown("---")
    st.subheader("💡 Strategic Takeaway & Fast-Track Advice")
    st.info(f"**Key Recommendation:** {xai_explanation.get('key_takeaway', '')}")


# =========================================================
# TAB 2: RESUME ANALYZER & PROFILE
# =========================================================
with tab_resume:
    st.subheader("📄 Resume NLP Extraction & Profile Inspector")
    st.caption("Upload any PDF/TXT resume or inspect the extracted skills, experience, and projects.")

    up_col, text_col = st.columns([1.5, 2.5])
    with up_col:
        uploaded_file = st.file_uploader("Upload Resume (PDF or TXT):", type=["pdf", "txt"])
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            with st.spinner("Extracting NLP metadata and parsing skills..."):
                parse_result = parser.parse(bytes_data, filename=uploaded_file.name)
                if parse_result["success"]:
                    st.session_state.candidate_profile = parse_result["profile"]
                    st.session_state.raw_text = parse_result["raw_text"]
                    st.success(f"Successfully parsed resume: {uploaded_file.name}")
                    st.rerun()
                else:
                    st.error(parse_result.get("error", "Failed to parse document."))

    with text_col:
        with st.expander("📝 View or Edit Raw Resume Text", expanded=False):
            edited_text = st.text_area("Resume Text Content:", value=st.session_state.raw_text, height=180)
            if st.button("Re-parse Edited Text"):
                parse_result = parser.parse(edited_text, filename="custom.txt")
                if parse_result["success"]:
                    st.session_state.candidate_profile = parse_result["profile"]
                    st.session_state.raw_text = edited_text
                    st.success("Profile updated successfully!")
                    st.rerun()

    st.markdown("---")
    p_col1, p_col2 = st.columns([1.5, 2.5])
    
    with p_col1:
        st.markdown("### 👤 Candidate Information")
        st.markdown(f"**Name:** {profile.get('name', 'N/A')}")
        st.markdown(f"**Email:** {profile.get('email', 'N/A')}")
        st.markdown(f"**Phone:** {profile.get('phone', 'N/A')}")
        st.markdown(f"**Location:** {profile.get('location', 'N/A')}")
        if profile.get("linkedin"):
            st.markdown(f"**LinkedIn:** [{profile.get('linkedin')}](https://{profile.get('linkedin')})")
        if profile.get("github"):
            st.markdown(f"**GitHub:** [{profile.get('github')}](https://{profile.get('github')})")

        st.markdown("#### 🎓 Academic Profile")
        edu = profile.get("education", {})
        st.markdown(f"- **Degree:** {edu.get('degree', 'Bachelor')}")
        st.markdown(f"- **Major:** {edu.get('major', 'Computer Science')}")
        st.markdown(f"- **GPA/Score:** {edu.get('gpa', 'N/A')}")
        st.markdown(f"- **Graduation Year:** {edu.get('graduation_year', 'Recent')}")

    with p_col2:
        st.markdown(f"### 🛠️ Detected Skills ({len(profile.get('skills', []))} Total)")
        
        # Categorized Skills Cloud
        by_cat = profile.get("skills_by_category", {})
        if by_cat:
            for cat_name, skills in by_cat.items():
                st.markdown(f"**{cat_name}:**")
                badges_html = " ".join([f"<span class='badge-strong'>{s}</span>" for s in skills])
                st.markdown(badges_html, unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
        else:
            badges_html = " ".join([f"<span class='badge-strong'>{s}</span>" for s in profile.get("skills", [])])
            st.markdown(badges_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 💼 Projects & Key Highlights")
        projects = profile.get("projects", [])
        if projects:
            for p in projects:
                st.markdown(f"- **{p.get('title', 'Project')}**: {p.get('description', '')[:160]}...")
        else:
            st.caption("No explicit projects section segmented.")


# =========================================================
# TAB 3: JOB MATCHING & EXPLORER
# =========================================================
with tab_matches:
    st.subheader(f"💼 Job Market Recommendations for **{target_role_meta.get('title', 'Role')}**")
    st.caption("Matching candidate skill vector, experience, and semantic NLP embeddings against live job postings:")

    f1, f2, f3 = st.columns([1.5, 1.5, 1])
    with f1:
        loc_filter = st.selectbox("Filter Location:", ["All Locations", "Bangalore, Karnataka", "Hyderabad, Telangana", "Pune, Maharashtra", "Mumbai, Maharashtra", "Remote (India)"])
    with f2:
        min_match_slider = st.slider("Minimum Match %:", min_value=30, max_value=90, value=50, step=5)
    with f3:
        sort_by = st.selectbox("Sort By:", ["Match Score (High to Low)", "Salary (High to Low)"])

    # Filter matched jobs
    filtered_jobs = matched_jobs
    if loc_filter != "All Locations":
        filtered_jobs = [j for j in filtered_jobs if j["location"] == loc_filter]
    filtered_jobs = [j for j in filtered_jobs if j["match_score"] >= min_match_slider]
    
    if sort_by == "Salary (High to Low)":
        filtered_jobs.sort(key=lambda x: x["salary_max_lpa"], reverse=True)
    else:
        filtered_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    st.markdown(f"**Found {len(filtered_jobs)} matching openings:**")
    
    for job in filtered_jobs[:10]:
        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h4 style="margin:0; color:#38BDF8;">{job['title']}</h4>
                        <span style="color:#94A3B8; font-size:0.9rem;">🏢 {job['company']} • 📍 {job['location']} • ⏳ {job['min_experience_years']}+ yrs exp</span>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:1.4rem; font-weight:bold; color:#10B981;">{job['match_score']}%</span>
                        <div style="color:#34D399; font-size:0.85rem; font-weight:600;">{job['salary_formatted']}</div>
                    </div>
                </div>
                <div style="margin-top:10px;">
                    <span style="font-size:0.8rem; color:#A78BFA; font-weight:600;">Matched Skills:</span> {' '.join([f"<span class='badge-strong'>{s}</span>" for s in job['matched_skills'][:6]])}
                    {('<br><span style=\"font-size:0.8rem; color:#FDA4AF; font-weight:600;\">Missing Skills:</span> ' + ' '.join([f"<span class='badge-missing'>{s}</span>" for s in job['missing_skills'][:4]])) if job['missing_skills'] else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"View Job Description & Multi-Factor Score Breakdown for {job['title']}"):
                sb = job["score_breakdown"]
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                col_s1.metric("Skill Match", f"{sb['skill_score']}%")
                col_s2.metric("NLP Similarity", f"{sb['nlp_score']}%")
                col_s3.metric("Experience Alignment", f"{sb['exp_score']}%")
                col_s4.metric("Education Fit", f"{sb['edu_score']}%")
                st.write(job["description"])


# =========================================================
# TAB 4: SKILL GAP ANALYZER & ROADMAP
# =========================================================
with tab_gaps:
    st.subheader(f"🎯 Granular Skill Gap Analysis: **{target_role_meta.get('title', 'Role')}**")
    st.caption("Detailed decomposition into Mastered competencies, Near-Match improvements, and Critical missing skills:")

    # 3 Badged Columns
    col_str, col_imp, col_mis = st.columns(3)
    
    with col_str:
        st.markdown(f"### ✅ Mastered Skills ({len(gap_results.get('strong_skills', []))})")
        for s in gap_results.get("strong_skills", []):
            st.markdown(f"<span class='badge-strong'>✓ {s['name']}</span>", unsafe_allow_html=True)
            st.caption(f"{s['type']} • Mastered")
            
    with col_imp:
        st.markdown(f"### ⚠️ Needs Improvement ({len(gap_results.get('improvement_skills', []))})")
        for s in gap_results.get("improvement_skills", []):
            st.markdown(f"<span class='badge-imp'>⚠ {s['name']}</span>", unsafe_allow_html=True)
            st.caption(s.get("reason", "Secondary requirement"))

    with col_mis:
        st.markdown(f"### ❌ Missing Critical Gaps ({len(gap_results.get('missing_skills', []))})")
        for s in gap_results.get("missing_skills", []):
            st.markdown(f"<span class='badge-missing'>✗ {s['name']}</span>", unsafe_allow_html=True)
            st.caption(f"{s['priority']} • {s.get('market_demand', 'High Demand')}")

    st.markdown("---")
    st.subheader(f"🗺️ Personalized {roadmap_data.get('total_estimated_weeks', 8)}-Week Actionable Learning Roadmap")
    st.caption(f"Projected Readiness after closing gaps: **{roadmap_data.get('projected_readiness_after_completion', 95)}%**")

    for phase in roadmap_data.get("phases", []):
        with st.expander(f"📌 {phase['title']} ({phase['duration_weeks']} Weeks)", expanded=True):
            st.markdown(f"**Core Goal:** {phase['goal']}")
            st.markdown("---")
            
            for item in phase["skills"]:
                c_a, c_b = st.columns([1.5, 2.5])
                with c_a:
                    st.markdown(f"#### 🔹 {item['name']}")
                    st.markdown(f"**Estimated Effort:** ~{item['estimated_hours']} Hours")
                    st.markdown(f"**Priority:** `{item['priority']}`")
                with c_b:
                    st.markdown(f"**🏆 Milestone Project:** {item['milestone_project']}")
                    st.markdown(f"**🎯 Interview Prep:** *{item['interview_focus']}*")
                    
                    st.markdown("**Curated Resources:**")
                    for res in item["resources"]:
                        st.markdown(f"- [{res['name']}]({res['url']}) `({res['type']})`")
                st.markdown("<hr style='margin:8px 0; border-color:#334155;'>", unsafe_allow_html=True)


# =========================================================
# TAB 5: WHAT-IF SIMULATOR & EXPLAINABLE AI
# =========================================================
with tab_simulator:
    st.subheader("🧪 Interactive 'What-If' Trajectory & Impact Simulator")
    st.caption("Simulate how adding new skills, certifications, or experience impacts your role readiness and market salary:")

    sim_col_controls, sim_col_results = st.columns([1.5, 2.5])
    
    with sim_col_controls:
        st.markdown("### 🎛️ Simulation Parameters")
        
        # Missing skills suggestions
        missing_ids = [s["skill_id"] for s in gap_results.get("missing_skills", [])]
        all_skills_list = extractor.get_all_skill_ids()
        
        add_skills = st.multiselect(
            "Add Skills to Learn:",
            options=all_skills_list,
            default=missing_ids[:2] if len(missing_ids) >= 2 else missing_ids,
            format_func=lambda x: extractor.get_skill_name(x)
        )
        
        add_exp = st.slider("Add Experience Tenure:", min_value=0.0, max_value=5.0, value=1.0, step=0.5, format="+%.1f yrs")
        
        sim_edu = st.selectbox(
            "Upgrade Highest Degree (Optional):",
            [
                "Keep Current Degree",
                "M.Tech / M.E. Data Science / AI",
                "M.S. in Computer Science",
                "Ph.D. in AI / Machine Learning"
            ]
        )
        degree_param = None if sim_edu == "Keep Current Degree" else sim_edu

    # Run Simulation
    sim_result = simulator.simulate(
        current_profile=profile,
        target_role_id=target_role_id,
        additional_skills=add_skills,
        additional_experience_years=add_exp,
        simulated_education=degree_param
    )

    with sim_col_results:
        st.markdown("### 📊 Simulated Career Trajectory")
        
        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric(
                label="Role Readiness",
                value=f"{sim_result['simulated']['readiness_score']}%",
                delta=f"+{sim_result['impact']['readiness_delta_pct']}%"
            )
        with s2:
            st.metric(
                label="Projected Salary",
                value=sim_result['simulated']['formatted_salary'],
                delta=f"+₹{sim_result['impact']['salary_increase_lpa']}L ({sim_result['impact']['salary_growth_pct']}%)"
            )
        with s3:
            st.metric(
                label="High-Match Jobs",
                value=f"{sim_result['simulated']['high_match_jobs_unlocked']} Openings",
                delta="Unlocked"
            )

        st.success(f"**Impact Summary:** {sim_result['impact']['summary']}")

        # Comparison Bar Chart
        fig_sim = go.Figure(data=[
            go.Bar(name="Baseline", x=["Readiness Score (%)", "Estimated Salary (LPA)"], y=[sim_result["baseline"]["readiness_score"], sim_result["baseline"]["predicted_salary_lpa"]], marker_color="#3B82F6"),
            go.Bar(name="Simulated", x=["Readiness Score (%)", "Estimated Salary (LPA)"], y=[sim_result["simulated"]["readiness_score"], sim_result["simulated"]["predicted_salary_lpa"]], marker_color="#10B981")
        ])
        fig_sim.update_layout(barmode='group', height=260, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Explainable AI (XAI): Why did you receive this match score?")
    st.caption("Granular factor contributions and skill penalties explaining the ML score:")

    xai_left, xai_right = st.columns(2)
    with xai_left:
        st.markdown("#### 🟢 Positive Factors Boosting Score")
        for pos in xai_explanation.get("positive_drivers", []):
            st.markdown(f"**{pos['factor']}** `{pos['impact']}` — <span style='color:#94A3B8;'>{pos['detail']}</span>", unsafe_allow_html=True)

    with xai_right:
        st.markdown("#### 🔴 Score Deductions & Missing Factor Penalties")
        for neg in xai_explanation.get("deductions", []):
            st.markdown(f"**{neg['factor']}** `{neg['impact']}` — <span style='color:#94A3B8;'>{neg['detail']}</span>", unsafe_allow_html=True)


# =========================================================
# TAB 6: MARKET INTELLIGENCE
# =========================================================
with tab_market:
    st.subheader("📈 Real-Time Job Market Intelligence")
    st.caption("Aggregated analytics from 3,500+ tech job openings and 5,000+ salary benchmarks:")

    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown(f"### 🏆 Top In-Demand Skills for **{target_role_meta.get('title', 'Role')}**")
        top_skills_data = market_analyzer.get_top_skills_by_role(role_id=target_role_id, top_n=10)
        df_top_skills = pd.DataFrame(top_skills_data)
        
        if not df_top_skills.empty:
            fig_skills = px.bar(
                df_top_skills,
                x="demand_percentage",
                y="skill_name",
                orientation="h",
                color="demand_percentage",
                color_continuous_scale="Viridis",
                labels={"demand_percentage": "Job Postings Demand (%)", "skill_name": "Skill"}
            )
            fig_skills.update_layout(yaxis=dict(autorange="reversed"), height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_skills, use_container_width=True)

    with m_col2:
        st.markdown("### 💰 Compensation Benchmarks Across Tech Roles")
        salary_dist_data = market_analyzer.get_salary_by_role_distribution()
        df_salary_dist = pd.DataFrame(salary_dist_data)
        
        if not df_salary_dist.empty:
            fig_sal = px.bar(
                df_salary_dist.head(8),
                x="role_title",
                y=["min_lpa", "avg_lpa", "max_lpa"],
                barmode="group",
                labels={"value": "Salary (LPA - ₹ Lakhs/yr)", "role_title": "Role"},
                color_discrete_sequence=["#60A5FA", "#34D399", "#F87171"]
            )
            fig_sal.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_sal, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🌍 Hiring Hubs & Geographic Compensation Distribution")
    overview = market_analyzer.get_market_overview()
    
    col_loc1, col_loc2 = st.columns(2)
    with col_loc1:
        loc_df = pd.DataFrame(list(overview.get("top_hiring_locations", {}).items()), columns=["Location", "Job Count"])
        fig_loc = px.pie(loc_df, values="Job Count", names="Location", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
        fig_loc.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_loc, use_container_width=True)

    with col_loc2:
        comp_df = pd.DataFrame(list(overview.get("top_hiring_companies", {}).items()), columns=["Company", "Openings Count"])
        fig_comp = px.bar(comp_df, x="Openings Count", y="Company", orientation="h", color="Openings Count", color_continuous_scale="Purples")
        fig_comp.update_layout(yaxis=dict(autorange="reversed"), height=280, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_comp, use_container_width=True)


# =========================================================
# TAB 7: PDF REPORT GENERATOR
# =========================================================
with tab_report:
    st.subheader("📑 Export Career Intelligence Evaluation PDF Report")
    st.caption("Generate a downloadable PDF report summarizing your profile, skill gap breakdown, learning roadmap, and job matches.")

    st.markdown(f"""
    **Report Summary Preview:**
    - **Candidate Name:** {profile.get('name', 'Candidate')}
    - **Target Role Evaluated:** {target_role_meta.get('title', 'Role')}
    - **Calculated Readiness:** {readiness_score}%
    - **Estimated Compensation:** {salary_results.get('formatted_range', 'N/A')}
    - **Learning Roadmap Duration:** {roadmap_data.get('total_estimated_weeks', 8)} Weeks ({roadmap_data.get('phases_count', 4)} Phases)
    """)

    if st.button("🚀 Generate & Download PDF Report", type="primary"):
        with st.spinner("Generating PDF evaluation document..."):
            pdf_bytes = pdf_gen.generate_report(
                candidate_profile=profile,
                target_role=target_role_id,
                gap_analysis=gap_results,
                salary_info=salary_results,
                roadmap=roadmap_data,
                top_jobs=matched_jobs[:5]
            )
            
            st.success("PDF Report generated successfully!")
            st.download_button(
                label="📥 Click Here to Download PDF Report",
                data=pdf_bytes,
                file_name=f"Career_Intelligence_Report_{profile.get('name', 'Candidate').replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
