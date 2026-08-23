"""
Persistent Top Bar & Navigation Header for Career Intelligence Engine v2.
Displays candidate snapshot, mini ATS score indicator, and inline Goal selector.
"""

import streamlit as st


def render_header(components: dict, ats_results: dict):
    """
    Renders the persistent top bar visible above all 5 tabs.
    """
    profile = st.session_state.get("candidate_profile", {})
    roles_dict = components["ontology"].get("roles", {})
    role_options = {k: v["title"] for k, v in roles_dict.items()}

    current_role_id = st.session_state.get("target_role_id", "data_scientist")
    if current_role_id not in role_options:
        current_role_id = list(role_options.keys())[0]

    ats_score = ats_results.get("total", 0)
    score_color = ats_results.get("status_color", "#16A34A")

    col_info, col_role, col_action = st.columns([3.5, 3.5, 1.2])

    with col_info:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="background: {score_color}15; border: 1.5px solid {score_color}; color: {score_color}; border-radius: 50%; width: 46px; height: 46px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 800; line-height: 1;">
                <span style="font-size: 1.05rem;">{ats_score}</span>
                <span style="font-size: 0.55rem; font-weight: 700; opacity: 0.85;">ATS</span>
            </div>
            <div>
                <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">
                    {profile.get('name', 'Candidate Profile')}
                </div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">
                    {profile.get('experience_years', 0.0)} yrs exp ({profile.get('seniority_level', 'Junior')}) • {len(profile.get('skills', []))} skills detected
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

    with col_action:
        if st.button("🔄 New Resume", use_container_width=True, help="Upload a different resume"):
            st.session_state.onboarding_complete = False
            st.rerun()

    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
