"""
Stage 1 Landing View: Clean, high-contrast, distraction-free resume drop zone.
Provides accessible drag-and-drop uploader, visible sample candidate chips, and trust badges.
"""

import os
import logging
import streamlit as st
from src.config import SAMPLE_RESUMES_DIR

logger = logging.getLogger(__name__)


def render_landing_page(components: dict):
    """
    Renders Stage 1: Resume drop zone only with high contrast and accessible controls.
    """
    parser = components["parser"]

    st.markdown("""
    <div class="landing-hero-container">
        <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-bottom: 12px;">
            <span style="font-size: 2.2rem;">🎯</span>
            <span style="font-size: 1.8rem; font-weight: 800; color: var(--accent-indigo); letter-spacing: -0.02em;">Career Intelligence Engine</span>
            <span style="background: var(--accent-bg); color: var(--accent-indigo); padding: 4px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 800;">v2.0</span>
        </div>
        <div class="landing-title">Instant ATS & Career Intelligence</div>
        <div class="landing-subtitle">
            Upload your resume to calculate your instant ATS screening score, unlock top eligible job openings, and map a personalized roadmap to your dream tech role.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Centered container for drop zone & sample chips
    col_l, col_center, col_r = st.columns([1, 8, 1])

    with col_center:
        with st.container():
            # File Uploader
            uploaded_file = st.file_uploader(
                "Drop your resume here (PDF or TXT):",
                type=["pdf", "txt"],
                label_visibility="visible",
                help="Upload your latest resume in PDF or plain text format for immediate ATS compatibility scoring."
            )

            if uploaded_file is not None:
                try:
                    bytes_data = uploaded_file.read()
                    with st.spinner("Parsing resume structure and analyzing ATS compatibility..."):
                        parse_result = parser.parse(bytes_data, filename=uploaded_file.name)
                        if parse_result.get("success"):
                            st.session_state.candidate_profile = parse_result["profile"]
                            st.session_state.raw_text = parse_result["raw_text"]
                            st.session_state.onboarding_complete = True
                            st.session_state.uploaded_file_name = uploaded_file.name
                            st.rerun()
                        else:
                            st.error(parse_result.get("error", "Failed to extract text from document. Please ensure the file is not password-protected."))
                except Exception as e:
                    logger.error(f"Error parsing uploaded resume: {e}", exc_info=True)
                    st.error("An error occurred while parsing the resume. Please try uploading a plain text (.txt) or standard PDF file.")

            # Section Divider for Sample Profiles
            st.markdown("""
            <div style="margin: 28px 0 16px 0; text-align: center;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 14px;">
                    <div style="height: 1px; flex: 1; background: var(--border-color);"></div>
                    <span style="color: var(--text-primary); font-size: 0.88rem; font-weight: 750; letter-spacing: 0.04em;">
                        ⚡ OR EXPLORE INSTANTLY WITH A TEST PROFILE
                    </span>
                    <div style="height: 1px; flex: 1; background: var(--border-color);"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # High-Contrast Sample Candidate Profile Buttons
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("📊 Data Analyst", key="btn_sample_da", use_container_width=True, help="Alex Mercer (1.5 yrs exp, SQL, Python, Power BI)"):
                    _load_sample(parser, "data_analyst_candidate.txt", "Data Analyst Candidate")
            with c2:
                if st.button("🧪 Data Scientist", key="btn_sample_ds", use_container_width=True, help="Aarav Mehta (3.5 yrs exp, Python, Scikit-Learn, ML)"):
                    _load_sample(parser, "data_scientist_candidate.txt", "Data Scientist Candidate")
            with c3:
                if st.button("⚙️ ML Engineer", key="btn_sample_mle", use_container_width=True, help="Priya Sharma (4.0 yrs exp, PyTorch, Docker, MLOps)"):
                    _load_sample(parser, "ml_engineer_candidate.txt", "ML Engineer Candidate")
            with c4:
                if st.button("🎓 Fresher / Grad", key="btn_sample_fresh", use_container_width=True, help="Rohan Gupta (0.5 yrs exp, Python, SQL, C++)"):
                    _load_sample(parser, "fresh_graduate_candidate.txt", "Fresh Graduate Candidate")

        # Trust badges
        st.markdown("""
        <div class="trust-badge-row">
            <div class="trust-badge">
                <span>🛡️</span>
                <span>Rule-Based ATS Screening</span>
            </div>
            <div class="trust-badge">
                <span>⚡</span>
                <span>500+ Skills Evaluated</span>
            </div>
            <div class="trust-badge">
                <span>📈</span>
                <span>Real-Time Salary Forecast</span>
            </div>
            <div class="trust-badge">
                <span>💼</span>
                <span>3,500+ Job Benchmarks</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _load_sample(parser, filename: str, label: str):
    try:
        file_path = os.path.join(SAMPLE_RESUMES_DIR, filename)
        if os.path.exists(file_path):
            parsed = parser.parse(file_path)
            if parsed.get("success"):
                st.session_state.candidate_profile = parsed["profile"]
                st.session_state.raw_text = parsed["raw_text"]
                st.session_state.onboarding_complete = True
                st.session_state.uploaded_file_name = label
                st.rerun()
            else:
                st.error("Failed to load sample resume.")
        else:
            st.error(f"Sample resume file '{filename}' was not found.")
    except Exception as e:
        logger.error(f"Error loading sample profile {filename}: {e}", exc_info=True)
        st.error("Could not load candidate sample profile. Please try another sample or upload a resume.")
