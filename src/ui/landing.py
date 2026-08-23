"""
Stage 1 Landing View: Clean, distraction-free resume drop zone.
Provides drag-and-drop uploader, sample resume chips, and trust badges.
"""

import os
import streamlit as st
from src.config import SAMPLE_RESUMES_DIR


def render_landing_page(components: dict):
    """
    Renders Stage 1: Resume drop zone only.
    """
    parser = components["parser"]

    st.markdown("""
    <div class="landing-hero-container">
        <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-bottom: 12px;">
            <span style="font-size: 2.2rem;">🎯</span>
            <span style="font-size: 1.8rem; font-weight: 800; color: var(--accent-indigo); letter-spacing: -0.02em;">Career Intelligence Engine</span>
            <span style="background: var(--accent-bg); color: var(--accent-indigo); padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 700;">v2.0</span>
        </div>
        <div class="landing-title">Instant ATS & Career Intelligence</div>
        <div class="landing-subtitle">
            Upload your resume to calculate your instant ATS screening score, unlock top eligible job openings, and map a personalized roadmap to your dream tech role.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Drop zone container
    col_l, col_center, col_r = st.columns([1, 8, 1])
    with col_center:
        st.markdown('<div class="cie-card" style="padding: 36px 32px; text-align: center; border: 2px dashed var(--accent-indigo);">', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Drop your resume here (PDF or TXT)",
            type=["pdf", "txt"],
            label_visibility="visible",
            help="Upload your latest resume in PDF or plain text format for immediate ATS compatibility scoring."
        )

        if uploaded_file is not None:
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
                    st.error(parse_result.get("error", "Failed to extract text from document."))

        st.markdown("<div style='margin: 18px 0 10px 0; color: var(--text-secondary); font-size: 0.88rem; font-weight: 500;'>— Or explore instantly with a pre-built candidate profile —</div>", unsafe_allow_html=True)

        # Quick sample resume chips
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("📊 Data Analyst", use_container_width=True, help="Alex Mercer (1.5 yrs exp, SQL, Python, Power BI)"):
                _load_sample(parser, "data_analyst_candidate.txt", "Data Analyst Candidate")
        with c2:
            if st.button("🧪 Data Scientist", use_container_width=True, help="Aarav Mehta (3.5 yrs exp, Python, Scikit-Learn, ML)"):
                _load_sample(parser, "data_scientist_candidate.txt", "Data Scientist Candidate")
        with c3:
            if st.button("⚙️ ML Engineer", use_container_width=True, help="Priya Sharma (4.0 yrs exp, PyTorch, Docker, MLOps)"):
                _load_sample(parser, "ml_engineer_candidate.txt", "ML Engineer Candidate")
        with c4:
            if st.button("🎓 Fresher / Graduate", use_container_width=True, help="Rohan Gupta (0.5 yrs exp, Python, SQL, C++)"):
                _load_sample(parser, "fresh_graduate_candidate.txt", "Fresh Graduate Candidate")

        st.markdown('</div>', unsafe_allow_html=True)

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
    file_path = os.path.join(SAMPLE_RESUMES_DIR, filename)
    if os.path.exists(file_path):
        parsed = parser.parse(file_path)
        if parsed.get("success"):
            st.session_state.candidate_profile = parsed["profile"]
            st.session_state.raw_text = parsed["raw_text"]
            st.session_state.onboarding_complete = True
            st.session_state.uploaded_file_name = label
            st.rerun()
