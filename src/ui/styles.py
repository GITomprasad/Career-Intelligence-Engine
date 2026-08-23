"""
Centralized CSS Design System for Career Intelligence Engine v2.
Implements the high-contrast warm off-white + indigo palette, accessible typography, 8px spacing grid, and comprehensive dark mode support.
"""

def get_css() -> str:
    return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-base: #F8F7F5;
        --bg-surface: #FFFFFF;
        --border-color: #D1D5DB;
        --border-subtle: #E5E7EB;
        --text-primary: #111827;
        --text-secondary: #4B5563;
        --text-muted: #6B7280;
        --accent-indigo: #4F46E5;
        --accent-indigo-hover: #4338CA;
        --accent-bg: #EEF2FF;
        --color-success: #16A34A;
        --color-success-bg: #DCFCE7;
        --color-success-text: #14532D;
        --color-warning: #D97706;
        --color-warning-bg: #FEF3C7;
        --color-warning-text: #78350F;
        --color-danger: #DC2626;
        --color-danger-bg: #FEE2E2;
        --color-danger-text: #7F1D1D;
        --btn-bg: #FFFFFF;
        --btn-text: #111827;
        --btn-border: #D1D5DB;
        --uploader-bg: #FFFFFF;
        --uploader-border: #4F46E5;
        --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
        --card-shadow-hover: 0 4px 8px -1px rgba(0, 0, 0, 0.12), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    [data-theme="dark"], .stApp[data-theme="dark"], body[data-theme="dark"] {
        --bg-base: #0F172A;
        --bg-surface: #1E293B;
        --border-color: #334155;
        --border-subtle: #475569;
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
        --accent-indigo: #6366F1;
        --accent-indigo-hover: #818CF8;
        --accent-bg: #1E1B4B;
        --color-success: #22C55E;
        --color-success-bg: #064E3B;
        --color-success-text: #BBF7D0;
        --color-warning: #F59E0B;
        --color-warning-bg: #78350F;
        --color-warning-text: #FDE68A;
        --color-danger: #EF4444;
        --color-danger-bg: #7F1D1D;
        --color-danger-text: #FECACA;
        --btn-bg: #1E293B;
        --btn-text: #F8FAFC;
        --btn-border: #475569;
        --uploader-bg: #1E293B;
        --uploader-border: #6366F1;
        --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
        --card-shadow-hover: 0 4px 8px rgba(0, 0, 0, 0.5);
    }

    /* Base Typography & Canvas */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--text-primary);
        background-color: var(--bg-base);
    }

    /* Streamlit Container Width & Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* Responsive Grid Helper */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* Card Container */
    .cie-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 22px;
        box-shadow: var(--card-shadow);
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
    }
    .cie-card:hover {
        box-shadow: var(--card-shadow-hover);
    }

    /* Hero Score Card */
    .hero-score-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 26px;
        box-shadow: var(--card-shadow);
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    /* Sticky Persistent Header */
    .cie-header-bar {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: var(--card-shadow);
    }

    /* High-Contrast Skill Badge Pills (999px border radius) */
    .pill-badge {
        display: inline-flex;
        align-items: center;
        padding: 5px 13px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin: 3px 4px 3px 0;
        line-height: 1.25;
    }
    .pill-green {
        background-color: var(--color-success-bg);
        color: var(--color-success-text);
        border: 1px solid rgba(22, 163, 74, 0.35);
    }
    .pill-amber {
        background-color: var(--color-warning-bg);
        color: var(--color-warning-text);
        border: 1px solid rgba(217, 119, 6, 0.35);
    }
    .pill-red {
        background-color: var(--color-danger-bg);
        color: var(--color-danger-text);
        border: 1px solid rgba(220, 38, 38, 0.35);
    }
    .pill-indigo {
        background-color: var(--accent-bg);
        color: var(--accent-indigo);
        border: 1px solid rgba(79, 70, 229, 0.35);
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
        font-weight: 600;
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
        font-weight: 600;
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
    }
    .job-item-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--card-shadow-hover);
    }

    /* Landing Drop Zone */
    .landing-hero-container {
        text-align: center;
        max-width: 820px;
        margin: 32px auto 24px auto;
        padding: 0 16px;
    }
    .landing-title {
        font-size: 2.3rem;
        font-weight: 800;
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
        margin-bottom: 24px;
        line-height: 1.5;
    }
    .trust-badge-row {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-top: 28px;
        flex-wrap: wrap;
    }
    .trust-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.88rem;
        font-weight: 700;
        color: var(--text-primary);
        background: var(--bg-surface);
        padding: 10px 18px;
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
        font-weight: 700;
        color: var(--text-primary);
    }

    /* 4-Phase Horizontal Roadmap Timeline */
    .timeline-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 16px 0;
    }
    @media (max-width: 900px) {
        .timeline-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    @media (max-width: 550px) {
        .timeline-container {
            grid-template-columns: 1fr;
        }
    }
    .timeline-phase-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-top: 4px solid var(--accent-indigo);
        border-radius: 10px;
        padding: 16px;
        box-shadow: var(--card-shadow);
    }
    .timeline-phase-num {
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        color: var(--accent-indigo);
        margin-bottom: 4px;
        letter-spacing: 0.05em;
    }
    .timeline-phase-title {
        font-size: 0.95rem;
        font-weight: 750;
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
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: var(--text-secondary) !important;
        font-weight: 700 !important;
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
        font-weight: 800 !important;
    }

    /* High-Contrast Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricDelta"] {
        font-weight: 700 !important;
    }

    /* -------------------------------------------------------------
       ACCESSIBLE BUTTONS & SAMPLE CHIPS (High Contrast)
       ------------------------------------------------------------- */
    .stButton > button {
        background-color: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        border: 1.5px solid var(--btn-border) !important;
        border-radius: 10px !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
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
        box-shadow: 0 2px 6px rgba(79, 70, 229, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background-color: var(--accent-indigo-hover) !important;
        color: #FFFFFF !important;
        border-color: var(--accent-indigo-hover) !important;
        transform: translateY(-2px) !important;
    }

    /* -------------------------------------------------------------
       ACCESSIBLE RESUME UPLOAD COMPONENT (High Contrast)
       ------------------------------------------------------------- */
    [data-testid="stFileUploader"] {
        width: 100%;
        margin-bottom: 12px;
    }
    [data-testid="stFileUploader"] section {
        background-color: var(--uploader-bg) !important;
        border: 2px dashed var(--uploader-border) !important;
        border-radius: 14px !important;
        padding: 28px 20px !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"] section:hover {
        background-color: var(--accent-bg) !important;
        border-color: var(--accent-indigo) !important;
    }
    [data-testid="stFileUploader"] label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
        color: var(--text-primary) !important;
        font-size: 1.05rem !important;
        font-weight: 750 !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
        color: var(--text-primary) !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] span {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: var(--text-secondary) !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        display: block !important;
        margin-top: 6px !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: var(--accent-indigo) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        padding: 8px 22px !important;
        margin-top: 8px !important;
        box-shadow: 0 2px 4px rgba(79, 70, 229, 0.25) !important;
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
        font-weight: 600 !important;
    }

    /* Form Controls & Inputs */
    .stSelectbox label, .stMultiSelect label, .stSlider label, .stTextArea label {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }
    div[data-baseweb="select"] {
        border-radius: 8px !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        background-color: var(--bg-surface) !important;
        border-radius: 8px !important;
    }
</style>
"""
