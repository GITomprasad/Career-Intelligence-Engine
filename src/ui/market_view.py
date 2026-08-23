"""
Market Intelligence View: Macro Trends, In-Demand Skills, and Compensation Benchmarks.
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def render_market_view(components: dict):
    """
    Renders the Market Intelligence tab.
    """
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
        st.markdown(f'<h4 style="margin-top:0; font-weight:700;">🏆 Top In-Demand Skills for {role_title}</h4>', unsafe_allow_html=True)
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
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_skills, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="cie-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-top:0; font-weight:700;">💰 Compensation Benchmarks Across Tech Roles</h4>', unsafe_allow_html=True)
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
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_sal, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Hiring Hubs & Employers
    overview = market_analyzer.get_market_overview()
    c_loc1, c_loc2 = st.columns(2)

    with c_loc1:
        st.markdown(f'<div class="cie-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-top:0; font-weight:700;">🌍 Geographic Hiring Hub Distribution</h4>', unsafe_allow_html=True)
        loc_df = pd.DataFrame(list(overview.get("top_hiring_locations", {}).items()), columns=["Location", "Job Openings"])
        fig_loc = px.pie(loc_df, values="Job Openings", names="Location", hole=0.45, color_discrete_sequence=px.colors.sequential.Indigo)
        fig_loc.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_loc, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_loc2:
        st.markdown(f'<div class="cie-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-top:0; font-weight:700;">🏢 Top Tech Employers Hiring</h4>', unsafe_allow_html=True)
        comp_df = pd.DataFrame(list(overview.get("top_hiring_companies", {}).items()), columns=["Company", "Openings"])
        fig_comp = px.bar(comp_df, x="Openings", y="Company", orientation="h", color="Openings", color_continuous_scale="Purples")
        fig_comp.update_layout(
            yaxis=dict(autorange="reversed"),
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
