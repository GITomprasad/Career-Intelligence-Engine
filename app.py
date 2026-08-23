"""
Career Intelligence Engine v2.0
Thin Orchestrator Application.
Resume-First · ATS-First · Goal-Aware · UX-First
"""

import json
import logging
import streamlit as st

logger = logging.getLogger(__name__)

from src.config import ONTOLOGY_PATH
from src.nlp.parser import ResumeParser
from src.nlp.skill_extractor import SkillExtractor
from src.models.matcher import JobMatcher
from src.models.role_classifier import RoleClassifier
from src.models.salary_predictor import SalaryPredictor
from src.engine.ats_scorer import ATSScorer
from src.engine.gap_analyzer import SkillGapAnalyzer
from src.engine.roadmap_generator import RoadmapGenerator
from src.engine.explainability import ExplainabilityEngine
from src.engine.simulator import CareerSimulator
from src.engine.market_analyzer import MarketAnalyzer
from src.report.pdf_generator import CareerReportGenerator

from src.ui.styles import get_css
from src.ui.landing import render_landing_page
from src.ui.header import render_header
from src.ui.ats_view import render_ats_view
from src.ui.jobs_view import render_jobs_view
from src.ui.goal_view import render_goal_view
from src.ui.market_view import render_market_view
from src.ui.report_view import render_report_view


# Page Configuration
st.set_page_config(
    page_title="Career Intelligence Engine v2",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Centralized v2 Theme & CSS
st.markdown(get_css(), unsafe_allow_html=True)


@st.cache_resource
def load_engine_components():
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        ontology = json.load(f)

    return {
        "parser": ResumeParser(),
        "extractor": SkillExtractor(),
        "matcher": JobMatcher(),
        "role_classifier": RoleClassifier(),
        "salary_predictor": SalaryPredictor(),
        "ats_scorer": ATSScorer(),
        "gap_analyzer": SkillGapAnalyzer(),
        "roadmap_generator": RoadmapGenerator(),
        "explainability": ExplainabilityEngine(),
        "simulator": CareerSimulator(),
        "market_analyzer": MarketAnalyzer(),
        "pdf_gen": CareerReportGenerator(),
        "ontology": ontology
    }


components = load_engine_components()

# Session State Initialization
if "onboarding_complete" not in st.session_state:
    st.session_state.onboarding_complete = False

if "target_role_id" not in st.session_state:
    st.session_state.target_role_id = "data_scientist"

if "candidate_profile" not in st.session_state:
    st.session_state.candidate_profile = {}
    st.session_state.raw_text = ""


# Main Flow Orchestration
try:
    if not st.session_state.onboarding_complete or not st.session_state.candidate_profile:
        # STAGE 1: Drop zone landing only (no tabs, clean first impression)
        render_landing_page(components)
    else:
        # STAGES 2 - 4: Resume-First Intelligence Experience
        profile = st.session_state.candidate_profile
        target_role_id = st.session_state.target_role_id
        raw_text = st.session_state.get("raw_text", "")

        # Calculate ATS Scoring & Diagnostics
        ats_scorer = components["ats_scorer"]
        ats_results = ats_scorer.score(profile, target_role_id, raw_text=raw_text)

        # 1. Persistent Summary Header & Inline Goal Selector
        render_header(components, ats_results)

        # 2. Five Focused Tabs
        tab_ats, tab_jobs, tab_goal, tab_market, tab_report = st.tabs([
            "🎯 ATS Score",
            "💼 Job Matches",
            "🎯 My Goal",
            "📈 Market",
            "📑 Report"
        ])

        with tab_ats:
            render_ats_view(components, ats_results)

        with tab_jobs:
            render_jobs_view(components)

        with tab_goal:
            render_goal_view(components)

        with tab_market:
            render_market_view(components)

        with tab_report:
            render_report_view(components, ats_results)

except Exception as e:
    logger.error(f"Application error in main orchestrator: {e}", exc_info=True)
    st.error("The application encountered an unexpected issue while processing your request. Please click 'Reset' below to reload.")
    if st.button("🔄 Reset Application", key="btn_global_reset"):
        st.session_state.onboarding_complete = False
        st.rerun()
