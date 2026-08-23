"""
PDF Report View: Career Evaluation Document Generator & Exporter.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)


def render_report_view(components: dict, ats_results: dict):
    """
    Renders the PDF Report generation tab with robust error handling.
    """
    try:
        pdf_gen = components["pdf_gen"]
        gap_analyzer = components["gap_analyzer"]
        salary_predictor = components["salary_predictor"]
        roadmap_generator = components["roadmap_generator"]
        matcher = components["matcher"]

        profile = st.session_state.get("candidate_profile", {})
        target_role_id = st.session_state.get("target_role_id", "data_scientist")
        roles_dict = components["ontology"].get("roles", {})
        role_meta = roles_dict.get(target_role_id, {})
        role_title = role_meta.get("title", "Target Role")

        gap_results = gap_analyzer.analyze_gap(profile.get("skill_ids", []), target_role_id)
        salary_results = salary_predictor.predict_salary(
            role_id=target_role_id,
            experience_years=profile.get("experience_years", 0.0),
            skill_count=len(profile.get("skills", [])),
            education=profile.get("education", {}).get("degree", "Bachelor's Degree") if isinstance(profile.get("education"), dict) else "Bachelor's Degree"
        )
        roadmap_data = roadmap_generator.generate_roadmap(gap_results)
        matched_jobs = matcher.match_jobs(profile, target_role_id=target_role_id, top_n=5)

        st.markdown("""
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0 0 4px 0; font-weight: 700; color: var(--text-primary);">📑 Export Comprehensive Career Report</h3>
            <div style="font-size: 0.88rem; color: var(--text-secondary);">
                Generate an executive-ready PDF report detailing your ATS score, skill gap breakdown, personalized 4-phase learning pathway, and matching opportunities.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="cie-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-top:0; font-weight:700; color: var(--text-primary);">Evaluation Summary Preview</h4>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("ATS Compatibility", f"{ats_results.get('total', 0)}/100")
        with c2:
            st.metric("Role Readiness", f"{int(gap_results.get('readiness_score', 0))}%")
        with c3:
            st.metric("Target Comp", salary_results.get("formatted_median", "N/A"))
        with c4:
            st.metric("Roadmap Timeline", f"{roadmap_data.get('total_estimated_weeks', 8)} Wks")

        st.markdown(f"""
        <div style="margin: 16px 0; font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6;">
            • <b>Candidate Name:</b> {profile.get('name', 'Candidate')}<br/>
            • <b>Target Evaluated Role:</b> {role_title}<br/>
            • <b>Critical Gaps Identified:</b> {len(gap_results.get('missing_skills', []))} missing competencies<br/>
            • <b>Learning Curriculum:</b> {len(roadmap_data.get('phases', []))} structured phases with hands-on milestone projects<br/>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Compile & Download Evaluation PDF", key="btn_compile_pdf", type="primary", use_container_width=True):
            try:
                with st.spinner("Compiling ATS diagnostics, roadmap curriculum, and market matching data..."):
                    pdf_bytes = pdf_gen.generate_report(
                        candidate_profile=profile,
                        target_role=target_role_id,
                        gap_analysis=gap_results,
                        salary_info=salary_results,
                        roadmap=roadmap_data,
                        top_jobs=matched_jobs,
                        ats_results=ats_results
                    )

                    candidate_clean_name = profile.get("name", "Candidate").replace(" ", "_")
                    st.success("✅ PDF report compiled successfully!")
                    st.download_button(
                        label="📥 Click Here to Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"Career_Intelligence_Report_{candidate_clean_name}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                logger.error(f"Error compiling PDF report: {e}", exc_info=True)
                st.error("Failed to compile PDF report. Please check profile details and try again.")

        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Unexpected error in Report View: {e}", exc_info=True)
        st.error("Report Export view encountered a temporary error. Please retry.")
