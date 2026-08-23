"""
Stage 4 View: Goal Mode — I Want to Become [Role].
Unifies Skill Gap Analysis, 4-Phase Visual Roadmap, and Inline What-If Simulator into one cohesive tab.
Uses native Streamlit containers to guarantee clean layout and zero broken DOM elements.
"""

import logging
import streamlit as st
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def render_goal_view(components: dict):
    """
    Renders the unified Goal Mode tab with robust error handling and high contrast elements.
    """
    try:
        gap_analyzer = components["gap_analyzer"]
        roadmap_generator = components["roadmap_generator"]
        simulator = components["simulator"]
        extractor = components["extractor"]
        profile = st.session_state.get("candidate_profile", {})
        target_role_id = st.session_state.get("target_role_id", "data_scientist")
        roles_dict = components["ontology"].get("roles", {})
        role_meta = roles_dict.get(target_role_id, {})
        role_title = role_meta.get("title", "Target Role")

        # 1. Compute Gap Analysis
        gap_results = gap_analyzer.analyze_gap(profile.get("skill_ids", []), target_role_id)
        readiness_score = gap_results.get("readiness_score", 50.0)
        strong_skills = gap_results.get("strong_skills", [])
        imp_skills = gap_results.get("improvement_skills", [])
        missing_skills = gap_results.get("missing_skills", [])

        # 2. Compute Phased Roadmap
        roadmap_data = roadmap_generator.generate_roadmap(gap_results)
        total_weeks = roadmap_data.get("total_estimated_weeks", 8)

        # --- SECTION A: GOAL HEADER & READINESS HERO ---
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <span style="background: var(--accent-bg); color: var(--accent-indigo); padding: 4px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 800; text-transform: uppercase;">
                        Goal-Oriented Trajectory
                    </span>
                    <h2 style="margin: 6px 0 2px 0; font-weight: 800; color: var(--text-primary);">🎯 Goal Roadmap: {role_title}</h2>
                    <div style="font-size: 0.88rem; color: var(--text-secondary);">
                        Category: <b>{role_meta.get('category', 'Technology')}</b> • Base Comp Range: <b>₹{role_meta.get('base_salary_min_lpa', 8)}L - ₹{role_meta.get('base_salary_max_lpa', 25)}L / yr</b>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary);">Role Readiness</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: var(--accent-indigo); line-height: 1;">
                        {int(readiness_score)}%
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- SECTION B: 3-COLUMN GAP BREAKDOWN CARD ---
        with st.container(border=True):
            st.markdown('<h4 style="margin-top: 0; margin-bottom: 14px; font-weight: 700; color: var(--text-primary);">1. Skill Gap Decomposition</h4>', unsafe_allow_html=True)

            c_str, c_imp, c_mis = st.columns(3)

            with c_str:
                st.markdown(f"""
                <div style="font-size: 0.9rem; font-weight: 750; color: var(--color-success-text); margin-bottom: 8px;">
                    ✅ Mastered Competencies ({len(strong_skills)})
                </div>
                """, unsafe_allow_html=True)
                if strong_skills:
                    for s in strong_skills:
                        st.markdown(f'<span class="pill-badge pill-green">✓ {s["name"]}</span>', unsafe_allow_html=True)
                else:
                    st.caption("No matching core skills detected.")

            with c_imp:
                st.markdown(f"""
                <div style="font-size: 0.9rem; font-weight: 750; color: var(--color-warning-text); margin-bottom: 8px;">
                    ⚠️ In-Progress / Related ({len(imp_skills)})
                </div>
                """, unsafe_allow_html=True)
                if imp_skills:
                    for s in imp_skills:
                        st.markdown(f'<span class="pill-badge pill-amber">⚠ {s["name"]}</span>', unsafe_allow_html=True)
                else:
                    st.caption("None in intermediate tier.")

            with c_mis:
                st.markdown(f"""
                <div style="font-size: 0.9rem; font-weight: 750; color: var(--color-danger-text); margin-bottom: 8px;">
                    ❌ Missing Critical Gaps ({len(missing_skills)})
                </div>
                """, unsafe_allow_html=True)
                if missing_skills:
                    for s in missing_skills:
                        st.markdown(f'<span class="pill-badge pill-red">✗ {s["name"]}</span>', unsafe_allow_html=True)
                else:
                    st.caption("No critical gaps remaining!")

        # --- SECTION C: 4-PHASE VISUAL HORIZONTAL TIMELINE ROADMAP ---
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <h4 style="margin: 0; font-weight: 700; color: var(--text-primary);">2. Phased Actionable Learning Pathway</h4>
                <span style="font-size: 0.85rem; font-weight: 700; color: var(--accent-indigo); background: var(--accent-bg); padding: 4px 12px; border-radius: 999px;">
                    ⏱️ Total Estimated Time: ~{total_weeks} Weeks
                </span>
            </div>
            """, unsafe_allow_html=True)

            phases = roadmap_data.get("phases", [])

            # Horizontal 4-Phase Grid
            if phases:
                cols = st.columns(len(phases))
                for idx, phase in enumerate(phases):
                    with cols[idx]:
                        phase_num = phase.get("phase_number", idx + 1)
                        phase_title = phase.get("title", f"Phase {phase_num}")
                        phase_dur = phase.get("duration_weeks", 2)
                        phase_goal = phase.get("goal", "")
                        phase_skills_cnt = len(phase.get("skills", []))

                        st.markdown(f"""
                        <div class="timeline-phase-card">
                            <div class="timeline-phase-num">PHASE {phase_num} • {phase_dur} WEEKS</div>
                            <div class="timeline-phase-title">{phase_title.split(':')[-1].strip()}</div>
                            <div class="timeline-phase-desc">{phase_goal[:85]}...</div>
                            <div style="margin-top: 10px; font-size: 0.78rem; font-weight: 700; color: var(--accent-indigo);">
                                📚 {phase_skills_cnt} Skills & Deliverables
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

                # Expandable Phase Drilldown
                for phase in phases:
                    with st.expander(f"📖 Drilldown: {phase.get('title')} ({phase.get('duration_weeks')} Weeks)"):
                        st.markdown(f"**Phase Objective:** {phase.get('goal')}")
                        st.markdown("---")
                        for s in phase.get("skills", []):
                            c1, c2 = st.columns([1.2, 2.0])
                            with c1:
                                st.markdown(f"##### 🔹 {s.get('name')}")
                                st.markdown(f"**Estimated Hours:** ~{s.get('estimated_hours', 15)} hrs")
                                st.markdown(f"**Priority Tier:** `{s.get('priority', 'Medium')}`")
                            with c2:
                                st.markdown(f"**🏆 Milestone Project:** {s.get('milestone_project', 'Build hands-on implementation')}")
                                st.markdown(f"**🎯 Interview Qs Focus:** *{s.get('interview_focus', 'Core technical principles')}*")
                                st.markdown("**Recommended Curated Resources:**")
                                for r in s.get("resources", []):
                                    st.markdown(f"- [{r.get('name')}]({r.get('url')}) `({r.get('type')})`")
                            st.markdown("<hr style='margin: 8px 0; border: none; border-top: 0.5px solid var(--border-color);'>", unsafe_allow_html=True)
            else:
                st.success(f"🎉 You already satisfy all primary competency requirements for {role_title}!")

        # --- SECTION D: INLINE WHAT-IF SIMULATOR ---
        with st.container(border=True):
            st.markdown("""
            <div style="margin-bottom: 14px;">
                <span style="background: var(--accent-bg); color: var(--accent-indigo); padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">
                    Live Career Simulator
                </span>
                <h4 style="margin: 6px 0 2px 0; font-weight: 700; color: var(--text-primary);">3. Simulate Adding Skills & Experience</h4>
                <div style="font-size: 0.85rem; color: var(--text-secondary);">
                    See real-time projected impact on your goal readiness score, predicted market salary, and unlocked high-match jobs.
                </div>
            </div>
            """, unsafe_allow_html=True)

            sim_controls_col, sim_results_col = st.columns([1.4, 2.0])

            with sim_controls_col:
                missing_ids = [s["skill_id"] for s in missing_skills]
                all_skills = extractor.get_all_skill_ids()

                sim_skills = st.multiselect(
                    "Select Skills to Acquire:",
                    options=all_skills,
                    default=missing_ids[:2] if len(missing_ids) >= 2 else missing_ids,
                    format_func=lambda x: extractor.get_skill_name(x),
                    key="goal_sim_skills"
                )

                sim_exp_add = st.slider(
                    "Add Years of Experience:",
                    min_value=0.0,
                    max_value=5.0,
                    value=1.0,
                    step=0.5,
                    format="+%.1f yrs",
                    key="goal_sim_exp"
                )

                sim_edu_choice = st.selectbox(
                    "Upgrade Highest Degree (Optional):",
                    [
                        "Keep Current Degree",
                        "M.Tech / M.E. Data Science / AI",
                        "M.S. in Computer Science",
                        "Ph.D. in AI / Machine Learning"
                    ],
                    key="goal_sim_edu"
                )
                sim_degree = None if sim_edu_choice == "Keep Current Degree" else sim_edu_choice

            # Run Simulation
            sim_result = simulator.simulate(
                current_profile=profile,
                target_role_id=target_role_id,
                additional_skills=sim_skills,
                additional_experience_years=sim_exp_add,
                simulated_education=sim_degree
            )

            with sim_results_col:
                # Delta Metrics in a clean row
                d1, d2, d3 = st.columns(3)
                with d1:
                    st.metric(
                        label="Role Readiness",
                        value=f"{sim_result['simulated']['readiness_score']}%",
                        delta=f"+{sim_result['impact']['readiness_delta_pct']}%"
                    )
                with d2:
                    st.metric(
                        label="Market Salary",
                        value=sim_result['simulated']['formatted_salary'],
                        delta=f"+₹{sim_result['impact']['salary_increase_lpa']}L ({sim_result['impact']['salary_growth_pct']}%)"
                    )
                with d3:
                    st.metric(
                        label="High-Match Jobs",
                        value=f"{sim_result['simulated']['high_match_jobs_unlocked']} Openings",
                        delta="Unlocked"
                    )

                st.markdown(f"""
                <div style="background: var(--accent-bg); border-left: 4px solid var(--accent-indigo); padding: 10px 14px; border-radius: 8px; font-size: 0.85rem; color: var(--accent-indigo); font-weight: 600; margin: 12px 0;">
                    🚀 <b>Simulation Impact:</b> {sim_result['impact']['summary']}
                </div>
                """, unsafe_allow_html=True)

                # Visual Comparison Bar Chart
                try:
                    fig = go.Figure(data=[
                        go.Bar(
                            name="Current Baseline",
                            x=["Readiness (%)", "Salary (LPA)"],
                            y=[sim_result["baseline"]["readiness_score"], sim_result["baseline"]["predicted_salary_lpa"]],
                            marker_color="#94A3B8"
                        ),
                        go.Bar(
                            name="Simulated Future",
                            x=["Readiness (%)", "Salary (LPA)"],
                            y=[sim_result["simulated"]["readiness_score"], sim_result["simulated"]["predicted_salary_lpa"]],
                            marker_color="#4F46E5"
                        )
                    ])
                    fig.update_layout(
                        barmode="group",
                        height=220,
                        margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter, sans-serif", color="#94A3B8"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    logger.error(f"Error rendering simulation chart: {e}")
                    st.caption("Simulation comparison chart is unavailable.")

    except Exception as e:
        logger.error(f"Unexpected error in Goal View: {e}", exc_info=True)
        st.error("Career Goal & Roadmap view encountered a temporary error. Please reselect your target role from the header.")
