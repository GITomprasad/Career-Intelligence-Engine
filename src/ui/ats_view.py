"""
Stage 2 View: Instant ATS Score — The Hero Screen.
Renders the circular SVG score ring, sub-scores progress bars, metric cards, and 2-column Issues & Wins.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)


def render_ats_view(components: dict, ats_results: dict):
    """
    Renders the hero ATS score evaluation screen with high-contrast visuals and error handling.
    """
    try:
        total_score = ats_results.get("total", 0)
        keyword_score = ats_results.get("keyword", 0.0)
        format_score = ats_results.get("format", 0.0)
        exp_score = ats_results.get("experience", 0.0)
        verdict = ats_results.get("verdict", "")
        target_role_title = ats_results.get("target_role_title", "Target Role")
        pass_rate = ats_results.get("ats_pass_rate_estimate", 0)
        skills_count = ats_results.get("skills_detected_count", 0)
        missing_count = ats_results.get("missing_keywords_count", 0)
        issues = ats_results.get("issues", [])
        wins = ats_results.get("wins", [])

        # Color band selection
        if total_score >= 71:
            ring_color = "#16A34A"  # Green
            bg_ring_color = "#DCFCE7"
            badge_text_color = "#14532D"
        elif total_score >= 41:
            ring_color = "#D97706"  # Amber
            bg_ring_color = "#FEF3C7"
            badge_text_color = "#78350F"
        else:
            ring_color = "#DC2626"  # Red
            bg_ring_color = "#FEE2E2"
            badge_text_color = "#7F1D1D"

        # SVG Ring Calculations (radius 70, circumference ~439.82)
        radius = 70
        circumference = 2 * 3.14159265 * radius
        stroke_dashoffset = circumference - (circumference * (total_score / 100.0))

        # --- ABOVE THE FOLD: 2 COLUMNS ---
        col_hero_ring, col_subscores = st.columns([1.2, 2.0])

        with col_hero_ring:
            st.markdown(f"""
            <div class="hero-score-card">
                <div style="font-size: 0.88rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-secondary); margin-bottom: 8px;">
                    ATS Screening Score
                </div>
                <div style="position: relative; width: 170px; height: 170px; display: flex; align-items: center; justify-content: center; margin: 4px 0 12px 0;">
                    <svg width="170" height="170" viewBox="0 0 170 170" style="transform: rotate(-90deg);">
                        <!-- Background Track -->
                        <circle
                            cx="85"
                            cy="85"
                            r="{radius}"
                            fill="none"
                            stroke="{bg_ring_color}"
                            stroke-width="13"
                        />
                        <!-- Progress Arc -->
                        <circle
                            cx="85"
                            cy="85"
                            r="{radius}"
                            fill="none"
                            stroke="{ring_color}"
                            stroke-width="13"
                            stroke-linecap="round"
                            stroke-dasharray="{circumference}"
                            stroke-dashoffset="{stroke_dashoffset}"
                            style="transition: stroke-dashoffset 0.8s ease;"
                        />
                    </svg>
                    <div style="position: absolute; text-align: center;">
                        <div style="font-size: 2.6rem; font-weight: 850; color: {ring_color}; line-height: 1;">
                            {total_score}
                        </div>
                        <div style="font-size: 0.82rem; font-weight: 750; color: var(--text-secondary); margin-top: 2px;">
                            / 100 ATS
                        </div>
                    </div>
                </div>
                <div style="font-size: 0.88rem; font-weight: 700; color: {badge_text_color}; background: {bg_ring_color}; padding: 6px 14px; border-radius: 999px; max-width: 92%; line-height: 1.3;">
                    ● {verdict}
                </div>
                <div style="font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); margin-top: 8px;">
                    Evaluated against {target_role_title} criteria
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_subscores:
            st.markdown('<div class="cie-card" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown('<h4 style="margin-top: 0; margin-bottom: 16px; font-weight: 750; color: var(--text-primary);">Score Breakdown & Metrics</h4>', unsafe_allow_html=True)

            # Sub-score progress bars
            # 1. Keyword Match
            st.markdown(f"""
            <div class="subscore-row">
                <div class="subscore-header">
                    <span>🔑 Keyword Match (Core & Recommended Skills)</span>
                    <span style="color: var(--accent-indigo);">{int(keyword_score)}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(1.0, keyword_score / 100.0))

            # 2. Format & Readability
            st.markdown(f"""
            <div class="subscore-row" style="margin-top: 10px;">
                <div class="subscore-header">
                    <span>📐 Format Quality & Readability</span>
                    <span style="color: var(--accent-indigo);">{int(format_score)}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(1.0, format_score / 100.0))

            # 3. Experience Depth
            st.markdown(f"""
            <div class="subscore-row" style="margin-top: 10px;">
                <div class="subscore-header">
                    <span>⏳ Experience Depth & Seniority Fit</span>
                    <span style="color: var(--accent-indigo);">{int(exp_score)}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(1.0, exp_score / 100.0))

            st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid var(--border-color);'>", unsafe_allow_html=True)

            # 3 Native Metric Cards in a row
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(label="Skills Detected", value=f"{skills_count}")
            with m2:
                st.metric(label="Missing Keywords", value=f"{missing_count}")
            with m3:
                st.metric(label="Estimated Pass Rate", value=f"{pass_rate}%")

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

        # --- BELOW THE FOLD: ISSUES & WINS ---
        col_wins, col_issues = st.columns(2)

        with col_wins:
            st.markdown("""
            <div class="cie-card">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px;">
                    <span style="background: var(--color-success-bg); color: var(--color-success-text); padding: 4px 10px; border-radius: 6px; font-weight: 800;">✓</span>
                    <span style="font-size: 1.05rem; font-weight: 750; color: var(--color-success-text);">What's Working (Strengths)</span>
                </div>
            """, unsafe_allow_html=True)

            if wins:
                for win in wins:
                    st.markdown(f"""
                    <div class="win-card">
                        <span style="font-weight: 800;">✓</span>
                        <span>{win}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Upload your resume to evaluate strong factors.")

            st.markdown('</div>', unsafe_allow_html=True)

        with col_issues:
            st.markdown("""
            <div class="cie-card">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px;">
                    <span style="background: var(--color-danger-bg); color: var(--color-danger-text); padding: 4px 10px; border-radius: 6px; font-weight: 800;">!</span>
                    <span style="font-size: 1.05rem; font-weight: 750; color: var(--color-danger-text);">What to Fix (Actionable Fixes)</span>
                </div>
            """, unsafe_allow_html=True)

            if issues:
                for issue in issues:
                    st.markdown(f"""
                    <div class="issue-card">
                        <span style="font-weight: 800;">•</span>
                        <span>{issue}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No critical issues detected! Your resume aligns cleanly with ATS guidelines.")

            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Unexpected error in ATS View: {e}", exc_info=True)
        st.error("ATS Score view encountered a temporary error. Please try uploading or selecting a resume again.")
