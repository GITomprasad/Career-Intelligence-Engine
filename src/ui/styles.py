"""
Centralized CSS Design System for Career Intelligence Engine v2.
Strict, Permanent Dark-Mode-Only Architecture.
Deep Slate Canvas (#0B0F19) · Elevated Surface Cards (#1E293B) · Vivid Indigo (#818CF8) · Accessible High-Contrast Typography
"""

def get_css() -> str:
    return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* =========================================================================
       PERMANENT DARK MODE THEME TOKENS
       ========================================================================= */
    :root {
        --bg-base: #0B0F19;
        --bg-surface: #1E293B;
        --bg-surface-alt: #0F172A;
        --bg-surface-hover: #293548;
        --border-color: #334155;
        --border-subtle: #1E293B;
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
        --accent-indigo: #818CF8;
        --accent-indigo-hover: #A5B4FC;
        --accent-bg: #1E1B4B;
        --color-success: #4ADE80;
        --color-success-bg: #064E3B;
        --color-success-text: #DCFCE7;
        --color-warning: #FBBF24;
        --color-warning-bg: #78350F;
        --color-warning-text: #FEF3C7;
        --color-danger: #F87171;
        --color-danger-bg: #7F1D1D;
        --color-danger-text: #FEE2E2;
        --btn-bg: #1E293B;
        --btn-text: #F8FAFC;
        --btn-border: #475569;
        --uploader-bg: #1E293B;
        --uploader-border: #818CF8;
        --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
        --card-shadow-hover: 0 6px 20px rgba(0, 0, 0, 0.65);
    }

    /* =========================================================================
       GLOBAL DARK CANVAS & TYPOGRAPHY ENFORCEMENT
       ========================================================================= */
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: var(--text-primary) !important;
        background-color: var(--bg-base) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }

    p, span, label, div, small, li {
        color: inherit;
    }

    /* Top Header & Toolbar */
    [data-testid="stHeader"] {
        background: transparent !important;
        height: 2.5rem !important;
        z-index: 10 !important;
    }

    /* Hide Streamlit Deploy Button */
    .stDeployButton, [data-testid="stDeployButton"], [data-testid="stToolbar"] .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }

    /* Page Container */
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1200px !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 3.8rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* =========================================================================
       NATIVE STREAMLIT BORDERED CONTAINERS AS DARK CARDS
       ========================================================================= */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 14px !important;
        box-shadow: var(--card-shadow) !important;
        padding: 20px !important;
        margin-bottom: 14px !important;
        transition: all 0.2s ease-in-out;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: var(--card-shadow-hover) !important;
        border-color: #475569 !important;
    }

    /* Standalone HTML Card */
    .cie-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 22px;
        box-shadow: var(--card-shadow);
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
        color: var(--text-primary);
    }
    .cie-card:hover {
        box-shadow: var(--card-shadow-hover);
        border-color: #475569;
    }

    /* Hero Score Card */
    .hero-score-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 22px;
        box-shadow: var(--card-shadow);
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: var(--text-primary);
    }

    /* High-Contrast Skill Badge Pills (999px border radius) */
    .pill-badge {
        display: inline-flex;
        align-items: center;
        padding: 5px 13px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 750;
        margin: 3px 4px 3px 0;
        line-height: 1.25;
    }
    .pill-green {
        background-color: var(--color-success-bg);
        color: var(--color-success-text);
        border: 1px solid var(--color-success);
    }
    .pill-amber {
        background-color: var(--color-warning-bg);
        color: var(--color-warning-text);
        border: 1px solid var(--color-warning);
    }
    .pill-red {
        background-color: var(--color-danger-bg);
        color: var(--color-danger-text);
        border: 1px solid var(--color-danger);
    }
    .pill-indigo {
        background-color: var(--accent-bg);
        color: var(--accent-indigo);
        border: 1px solid var(--accent-indigo);
    }

    /* Actionable Issue & Win Cards */
    .issue-card {
        background-color: var(--color-danger-bg);
        border-left: 4px solid var(--color-danger);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: var(--color-danger-text);
        font-size: 0.9rem;
        font-weight: 650;
        display: flex;
        align-items: flex-start;
        gap: 10px;
        line-height: 1.4;
    }
    .win-card {
        background-color: var(--color-success-bg);
        border-left: 4px solid var(--color-success);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: var(--color-success-text);
        font-size: 0.9rem;
        font-weight: 650;
        display: flex;
        align-items: flex-start;
        gap: 10px;
        line-height: 1.4;
    }

    /* Job Match Card */
    .job-item-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow: var(--card-shadow);
        border-left: 4px solid var(--accent-indigo);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        color: var(--text-primary);
    }
    .job-item-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--card-shadow-hover);
    }

    /* Landing Drop Zone */
    .landing-hero-container {
        text-align: center;
        max-width: 820px;
        margin: 16px auto 20px auto;
        padding: 0 16px;
    }
    .landing-title {
        font-size: 2.3rem;
        font-weight: 850;
        color: var(--text-primary);
        letter-spacing: -0.03em;
        margin-bottom: 8px;
        line-height: 1.2;
    }
    @media (max-width: 640px) {
        .landing-title {
            font-size: 1.8rem;
        }
    }
    .landing-subtitle {
        font-size: 1.05rem;
        color: var(--text-secondary);
        margin-bottom: 22px;
        line-height: 1.5;
    }
    .trust-badge-row {
        display: flex;
        justify-content: center;
        gap: 14px;
        margin-top: 24px;
        flex-wrap: wrap;
    }
    .trust-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--text-primary);
        background: var(--bg-surface);
        padding: 8px 16px;
        border-radius: 999px;
        border: 1px solid var(--border-color);
        box-shadow: var(--card-shadow);
    }

    /* Sub-score Progress Row */
    .subscore-row {
        margin-bottom: 12px;
    }
    .subscore-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
        font-size: 0.88rem;
        font-weight: 750;
        color: var(--text-primary);
    }

    /* 4-Phase Horizontal Roadmap Timeline */
    .timeline-phase-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-top: 4px solid var(--accent-indigo);
        border-radius: 10px;
        padding: 16px;
        box-shadow: var(--card-shadow);
        color: var(--text-primary);
    }
    .timeline-phase-num {
        font-size: 0.75rem;
        font-weight: 850;
        text-transform: uppercase;
        color: var(--accent-indigo);
        margin-bottom: 4px;
        letter-spacing: 0.05em;
    }
    .timeline-phase-title {
        font-size: 0.95rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    .timeline-phase-desc {
        font-size: 0.82rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }

    /* Streamlit Tab Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1.5px solid var(--border-color);
        padding-bottom: 4px;
        margin-bottom: 20px;
        flex-wrap: wrap;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: transparent !important;
        border-radius: 8px;
        color: var(--text-secondary) !important;
        font-weight: 750 !important;
        font-size: 0.95rem !important;
        padding: 8px 18px !important;
        border: none !important;
        transition: all 0.15s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--accent-bg) !important;
        color: var(--accent-indigo) !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-bg) !important;
        color: var(--accent-indigo) !important;
        font-weight: 850 !important;
        border-bottom: 2.5px solid var(--accent-indigo) !important;
    }

    /* High-Contrast Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 850 !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 750 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricDelta"] {
        font-weight: 750 !important;
    }

    /* -------------------------------------------------------------
       ACCESSIBLE BUTTONS & SAMPLE CHIPS (Dark Theme)
       ------------------------------------------------------------- */
    .stButton > button {
        background-color: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        border: 1.5px solid var(--btn-border) !important;
        border-radius: 10px !important;
        font-size: 0.92rem !important;
        font-weight: 750 !important;
        padding: 10px 16px !important;
        box-shadow: var(--card-shadow) !important;
        transition: all 0.18s ease-in-out !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: var(--accent-bg) !important;
        color: var(--accent-indigo) !important;
        border-color: var(--accent-indigo) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--card-shadow-hover) !important;
    }
    .stButton > button:active, .stButton > button:focus {
        border-color: var(--accent-indigo) !important;
        outline: 2px solid var(--accent-indigo) !important;
    }

    /* Primary Action Buttons */
    .stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
        background-color: var(--accent-indigo) !important;
        color: #FFFFFF !important;
        border: 1.5px solid var(--accent-indigo) !important;
        box-shadow: 0 2px 6px rgba(129, 140, 248, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background-color: var(--accent-indigo-hover) !important;
        color: #FFFFFF !important;
        border-color: var(--accent-indigo-hover) !important;
        transform: translateY(-2px) !important;
    }

    /* -------------------------------------------------------------
       DARK RESUME UPLOAD COMPONENT
       ------------------------------------------------------------- */
    [data-testid="stFileUploader"] {
        width: 100%;
        margin-bottom: 8px;
    }
    [data-testid="stFileUploader"] label, 
    [data-testid="stWidgetLabel"] p, 
    [data-testid="stWidgetLabel"] label {
        color: var(--text-primary) !important;
        font-size: 1.05rem !important;
        font-weight: 750 !important;
        margin-bottom: 6px !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: var(--uploader-bg) !important;
        border: 2px dashed var(--uploader-border) !important;
        border-radius: 12px !important;
        padding: 20px 16px !important;
        text-align: center !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        background-color: var(--accent-bg) !important;
        border-color: var(--accent-indigo) !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
        color: var(--text-primary) !important;
        font-size: 1rem !important;
        font-weight: 750 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] span {
        color: var(--text-primary) !important;
        font-weight: 750 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        display: block !important;
        margin-top: 4px !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: var(--accent-indigo) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-weight: 750 !important;
        padding: 8px 20px !important;
        margin-top: 4px !important;
        box-shadow: 0 2px 4px rgba(129, 140, 248, 0.25) !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: var(--accent-indigo-hover) !important;
        color: #FFFFFF !important;
    }
    [data-testid="stFileUploaderFileData"] {
        background-color: var(--accent-bg) !important;
        color: var(--accent-indigo) !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        font-weight: 700 !important;
    }

    /* Form Controls & Inputs (Dark Theme) */
    .stSelectbox label, .stMultiSelect label, .stSlider label, .stTextArea label {
        color: var(--text-primary) !important;
        font-weight: 750 !important;
        font-size: 0.92rem !important;
    }
    div[data-baseweb="select"] {
        border-radius: 8px !important;
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-color) !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        color: var(--text-primary) !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    li[role="option"] {
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: var(--bg-surface-hover) !important;
        color: var(--accent-indigo) !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 750 !important;
        color: var(--text-primary) !important;
        background-color: var(--bg-surface) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
    }
    .streamlit-expanderContent {
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border-bottom-left-radius: 8px !important;
        border-bottom-right-radius: 8px !important;
    }
</style>
"""
