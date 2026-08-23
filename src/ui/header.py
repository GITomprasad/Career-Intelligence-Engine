"""
Persistent Top Bar & Navigation Header for Career Intelligence Engine v2.
Displays back button, candidate snapshot, mini ATS score indicator, and inline Goal selector.
Wrapped inside a clean native bordered container for flawless visibility on desktop and mobile.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)


def render_header(components: dict, ats_results: dict):
    """
    Renders the persistent top navigation bar with Back button, candidate snapshot, and target goal selector.
    """
    try:
        profile = st.session_state.get("candidate_profile", {})
        roles_dict = components["ontology"].get("roles", {})
        role_options = {k: v["title"] for k, v in roles_dict.items()}

        current_role_id = st.session_state.get("target_role_id", "data_scientist")
        if current_role_id not in role_options:
            current_role_id = list(role_options.keys())[0]

        ats_score = ats_results.get("total", 0)
        score_color = ats_results.get("status_color", "#16A34A")

        with st.container(border=True):
            col_back, col_info, col_role = st.columns([1.5, 3.5, 3.0])

            with col_back:
                if st.button("⬅️ Back to Upload", key="btn_header_back", use_container_width=True, help="Return to resume upload screen"):
                    st.session_state.onboarding_complete = False
                    st.rerun()

            with col_info:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px; padding: 2px 0;">
                    <div style="background: {score_color}25; border: 2px solid {score_color}; color: {score_color}; border-radius: 50%; width: 44px; height: 44px; min-width: 44px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 850; line-height: 1;">
                        <span style="font-size: 1.05rem;">{ats_score}</span>
                        <span style="font-size: 0.55rem; font-weight: 800; opacity: 0.9;">ATS</span>
                    </div>
                    <div>
                        <div style="font-size: 1.05rem; font-weight: 800; color: var(--text-primary); line-height: 1.2;">
                            {profile.get('name', 'Candidate Profile')}
                        </div>
                        <div style="font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); margin-top: 2px;">
                            {profile.get('experience_years', 0.0)} yrs exp ({profile.get('seniority_level', 'Junior')}) • {len(profile.get('skills', []))} skills
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_role:
                selected_role = st.selectbox(
                    "Target Career Goal:",
                    options=list(role_options.keys()),
                    index=list(role_options.keys()).index(current_role_id),
                    format_func=lambda x: f"🎯 Aiming for: {role_options[x]}",
                    key="header_role_selector",
                    label_visibility="collapsed"
                )
                if selected_role != st.session_state.get("target_role_id"):
                    st.session_state.target_role_id = selected_role
                    st.session_state.goal_role_id = selected_role
                    st.rerun()

        st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error rendering header: {e}", exc_info=True)
