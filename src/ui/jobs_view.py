"""
Stage 3 View: Jobs You're Eligible For Right Now.
Renders curated job match cards with have/missing skill pills, compensation, and multi-factor breakdown.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)


def render_jobs_view(components: dict):
    """
    Renders the curated Job Matches tab with robust error handling.
    """
    try:
        matcher = components["matcher"]
        profile = st.session_state.get("candidate_profile", {})
        target_role_id = st.session_state.get("target_role_id", "data_scientist")
        roles_dict = components["ontology"].get("roles", {})
        role_meta = roles_dict.get(target_role_id, {})
        role_title = role_meta.get("title", "Target Role")

        st.markdown(f"""
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0 0 4px 0; font-weight: 700; color: var(--text-primary);">💼 Active Job Opportunities for {role_title}</h3>
            <div style="font-size: 0.88rem; color: var(--text-secondary);">
                Ranked by multi-factor algorithmic compatibility (skills, semantic NLP description match, experience tenure, and education).
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Compute matches
        with st.spinner("Fetching matching live job openings..."):
            matched_jobs = matcher.match_jobs(profile, target_role_id=target_role_id, top_n=25)

        # Filter Bar in a clean container
        f1, f2, f3 = st.columns([1.5, 1.5, 1.2])
        with f1:
            loc_options = ["All Locations", "Bangalore, Karnataka", "Hyderabad, Telangana", "Pune, Maharashtra", "Mumbai, Maharashtra", "Remote (India)"]
            selected_loc = st.selectbox("Location Filter:", options=loc_options)
        with f2:
            min_score = st.slider("Minimum Match Score:", min_value=30, max_value=90, value=50, step=5, format="%d%%")
        with f3:
            sort_choice = st.selectbox("Sort Openings By:", ["Match Score (High → Low)", "Salary (High → Low)"])

        # Filter & Sort Logic
        filtered = matched_jobs
        if selected_loc != "All Locations":
            filtered = [j for j in filtered if j.get("location") == selected_loc]
        filtered = [j for j in filtered if j.get("match_score", 0) >= min_score]

        if sort_choice == "Salary (High → Low)":
            filtered.sort(key=lambda x: x.get("salary_max_lpa", 0), reverse=True)
        else:
            filtered.sort(key=lambda x: x.get("match_score", 0), reverse=True)

        st.markdown(f"<div style='font-size: 0.88rem; font-weight: 700; color: var(--text-primary); margin: 16px 0 12px 0;'>Showing top matching openings ({len(filtered)} found):</div>", unsafe_allow_html=True)

        if not filtered:
            st.info("No job openings match the selected filters. Try lowering the minimum match percentage or selecting 'All Locations'.")
            return

        # Top 5 jobs shown by default
        top_5_jobs = filtered[:5]
        remaining_jobs = filtered[5:]

        for job in top_5_jobs:
            _render_job_card(job)

        # Show more expander
        if remaining_jobs:
            with st.expander(f"➕ View {len(remaining_jobs)} More Matching Openings"):
                for job in remaining_jobs:
                    _render_job_card(job)

    except Exception as e:
        logger.error(f"Unexpected error in Jobs View: {e}", exc_info=True)
        st.error("Job Matches view encountered a temporary issue while fetching openings. Please adjust filters or retry.")


def _render_job_card(job: dict):
    """
    Renders an individual job match card with green (have) and red (missing) skill pills.
    """
    match_score = job.get("match_score", 0)
    matched_skills = job.get("matched_skills", [])[:4]
    missing_skills = job.get("missing_skills", [])[:3]

    # Pill HTMLs
    have_pills = "".join([f'<span class="pill-badge pill-green">✓ {s}</span>' for s in matched_skills]) if matched_skills else '<span style="font-size:0.8rem; color:var(--text-muted);">None</span>'
    missing_pills = "".join([f'<span class="pill-badge pill-red">✗ {s}</span>' for s in missing_skills]) if missing_skills else '<span style="font-size:0.8rem; color:var(--color-success);">None — full match!</span>'

    st.markdown(f"""
    <div class="job-item-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
            <div>
                <div style="font-size: 1.15rem; font-weight: 750; color: var(--accent-indigo); margin-bottom: 2px;">
                    {job.get('title', 'Role')}
                </div>
                <div style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 8px;">
                    🏢 <b>{job.get('company', 'Company')}</b> • 📍 {job.get('location', 'Location')} • ⏳ {job.get('min_experience_years', 1)}+ yrs exp
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.4rem; font-weight: 800; color: var(--color-success);">
                    {match_score}%
                </div>
                <div style="font-size: 0.9rem; font-weight: 750; color: var(--text-primary);">
                    {job.get('salary_formatted', 'Competitive')}
                </div>
            </div>
        </div>
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-color);">
            <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-bottom: 6px;">
                <span style="font-size: 0.8rem; font-weight: 750; color: var(--color-success-text); margin-right: 4px;">Skills You Have:</span>
                {have_pills}
            </div>
            <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px;">
                <span style="font-size: 0.8rem; font-weight: 750; color: var(--color-danger-text); margin-right: 4px;">Skills Missing:</span>
                {missing_pills}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"🔍 Description & Multi-Factor Compatibility Breakdown — {job.get('title')} at {job.get('company')}"):
        sb = job.get("score_breakdown", {})
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Skill Match", f"{sb.get('skill_score', 0)}%")
        col2.metric("NLP Fit", f"{sb.get('nlp_score', 0)}%")
        col3.metric("Exp Alignment", f"{sb.get('exp_score', 0)}%")
        col4.metric("Edu Fit", f"{sb.get('edu_score', 0)}%")
        st.markdown(f"**Job Description:**\n\n{job.get('description', 'No description available.')}")
