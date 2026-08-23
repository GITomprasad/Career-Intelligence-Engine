"""
Market Intelligence View: Macro Trends, In-Demand Skills, and Compensation Benchmarks.
"""

import logging
import streamlit as st
import pandas as pd
import plotly.express as px

logger = logging.getLogger(__name__)


def render_market_view(components: dict):
    """
    Renders the Market Intelligence tab with robust error handling and accessible charts.
    """
    try:
        market_analyzer = components["market_analyzer"]
        target_role_id = st.session_state.get("target_role_id", "data_scientist")
        roles_dict = components["ontology"].get("roles", {})
        role_title = roles_dict.get(target_role_id, {}).get("title", "Target Role")

        st.markdown(f"""
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0 0 4px 0; font-weight: 700; color: var(--text-primary);">📈 Real-Time Job Market Intelligence</h3>
            <div style="font-size: 0.88rem; color: var(--text-secondary);">
                Aggregated analytics across 3,500+ tech job postings and 5,000+ salary benchmarks in India.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f'<div class="cie-card">', unsafe_allow_html=True)
            st.markdown(f'<h4 style="margin-top:0; font-weight:700; color: var(--text-primary);">🏆 Top In-Demand Skills for {role_title}</h4>', unsafe_allow_html=True)
            try:
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
                    fig_skills.update_layout(
                        yaxis=dict(autorange="reversed"),
                        height=320,
                        margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter, sans-serif")
                    )
                    st.plotly_chart(fig_skills, use_container_width=True)
                else:
                    st.info(f"No skill demand data currently indexed for {role_title}.")
            except Exception as e:
                logger.error(f"Error rendering top skills chart: {e}")
                st.info("Top in-demand skills data is temporarily unavailable.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown(f'<div class="cie-card">', unsafe_allow_html=True)
            st.markdown('<h4 style="margin-top:0; font-weight:700; color: var(--text-primary);">💰 Compensation Benchmarks Across Tech Roles</h4>', unsafe_allow_html=True)
            try:
                salary_dist_data = market_analyzer.get_salary_by_role_distribution()
                df_salary_dist = pd.DataFrame(salary_dist_data)

                if not df_salary_dist.empty:
                    fig_sal = px.bar(
                        df_salary_dist.head(8),
                        x="role_title",
                        y=["min_lpa", "avg_lpa", "max_lpa"],
                        barmode="group",
                        labels={"value": "Salary (LPA - ₹ Lakhs/yr)", "role_title": "Role"},
                        color_discrete_sequence=["#818CF8", "#4F46E5", "#312E81"]
                    )
                    fig_sal.update_layout(
                        height=320,
                        margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter, sans-serif"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_sal, use_container_width=True)
                else:
                    st.info("Salary distribution benchmarks are currently unavailable.")
            except Exception as e:
                logger.error(f"Error rendering salary distribution chart: {e}")
                st.info("Compensation benchmark chart is temporarily unavailable.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Hiring Hubs & Employers
        c_loc1, c_loc2 = st.columns(2)

        with c_loc1:
            st.markdown(f'<div class="cie-card">', unsafe_allow_html=True)
            st.markdown('<h4 style="margin-top:0; font-weight:700; color: var(--text-primary);">🌍 Geographic Hiring Hub Distribution</h4>', unsafe_allow_html=True)
            try:
                overview = market_analyzer.get_market_overview()
                loc_data = overview.get("top_hiring_locations", {})
                if loc_data:
                    loc_df = pd.DataFrame(list(loc_data.items()), columns=["Location", "Job Openings"])
                    fig_loc = px.pie(
                        loc_df,
                        values="Job Openings",
                        names="Location",
                        hole=0.45,
                        color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    fig_loc.update_layout(
                        height=260,
                        margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter, sans-serif")
                    )
                    st.plotly_chart(fig_loc, use_container_width=True)
                else:
                    st.info("Geographic hiring hub data is currently unavailable.")
            except Exception as e:
                logger.error(f"Error rendering geographic distribution pie chart: {e}")
                st.info("Geographic distribution data is currently unavailable.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c_loc2:
            st.markdown(f'<div class="cie-card">', unsafe_allow_html=True)
            st.markdown('<h4 style="margin-top:0; font-weight:700; color: var(--text-primary);">🏢 Top Tech Employers Hiring</h4>', unsafe_allow_html=True)
            try:
                overview = market_analyzer.get_market_overview()
                comp_data = overview.get("top_hiring_companies", {})
                if comp_data:
                    comp_df = pd.DataFrame(list(comp_data.items()), columns=["Company", "Openings"])
                    fig_comp = px.bar(
                        comp_df,
                        x="Openings",
                        y="Company",
                        orientation="h",
                        color="Openings",
                        color_continuous_scale="Purples"
                    )
                    fig_comp.update_layout(
                        yaxis=dict(autorange="reversed"),
                        height=260,
                        margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter, sans-serif")
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.info("Top employer hiring data is currently unavailable.")
            except Exception as e:
                logger.error(f"Error rendering company hiring bar chart: {e}")
                st.info("Top employer data is currently unavailable.")
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Unexpected error in market view: {e}", exc_info=True)
        st.error("Market Intelligence view encountered a temporary error while rendering. Please try selecting a different target role.")
