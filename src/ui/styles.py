"""
Centralized CSS Design System for Career Intelligence Engine v2.
Implements the warm off-white + indigo palette, typography hierarchy, 8px spacing grid, and dark mode support.
"""

def get_css() -> str:
    return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-base: #F8F7F5;
        --bg-surface: #FFFFFF;
        --border-color: #E8E6E0;
        --text-primary: #1A1A18;
        --text-secondary: #6B7280;
        --text-muted: #9CA3AF;
        --accent-indigo: #4F46E5;
        --accent-indigo-hover: #4338CA;
        --accent-bg: #EEF2FF;
        --color-success: #16A34A;
        --color-success-bg: #DCFCE7;
        --color-success-text: #15803D;
        --color-warning: #D97706;
        --color-warning-bg: #FEF3C7;
        --color-warning-text: #B45309;
        --color-danger: #DC2626;
        --color-danger-bg: #FEE2E2;
        --color-danger-text: #B91C1C;
        --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
        --card-shadow-hover: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
    }

    [data-theme="dark"], .stApp[data-theme="dark"] {
        --bg-base: #111827;
        --bg-surface: #1F2937;
        --border-color: #374151;
        --text-primary: #F9FAFB;
        --text-secondary: #9CA3AF;
        --text-muted: #6B7280;
        --accent-indigo: #6366F1;
        --accent-indigo-hover: #818CF8;
        --accent-bg: #1E1B4B;
        --color-success: #22C55E;
        --color-success-bg: #064E3B;
        --color-success-text: #6EE7B7;
        --color-warning: #F59E0B;
        --color-warning-bg: #78350F;
        --color-warning-text: #FDE68A;
        --color-danger: #EF4444;
        --color-danger-bg: #7F1D1D;
        --color-danger-text: #FCA5A5;
        --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        --card-shadow-hover: 0 4px 8px rgba(0, 0, 0, 0.4);
    }

    /* Base Font & Canvas */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--text-primary);
        background-color: var(--bg-base);
    }

    /* Container Spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* Modern Card Container */
    .cie-card {
        background-color: var(--bg-surface);
        border: 0.5px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
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
        border: 0.5px solid var(--border-color);
        border-radius: 16px;
        padding: 28px;
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
        border: 0.5px solid var(--border-color);
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: var(--card-shadow);
    }

    /* Skill Badge Pills (999px border radius) */
    .pill-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 3px 4px 3px 0;
        line-height: 1.2;
    }
    .pill-green {
        background-color: var(--color-success-bg);
        color: var(--color-success-text);
        border: 0.5px solid rgba(22, 163, 74, 0.2);
    }
    .pill-amber {
        background-color: var(--color-warning-bg);
        color: var(--color-warning-text);
        border: 0.5px solid rgba(217, 119, 6, 0.2);
    }
    .pill-red {
        background-color: var(--color-danger-bg);
        color: var(--color-danger-text);
        border: 0.5px solid rgba(220, 38, 38, 0.2);
    }
    .pill-indigo {
        background-color: var(--accent-bg);
        color: var(--accent-indigo);
        border: 0.5px solid rgba(79, 70, 229, 0.2);
    }

    /* Issue & Win Cards */
    .issue-card {
        background-color: var(--color-danger-bg);
        border-left: 4px solid var(--color-danger);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: var(--color-danger-text);
        font-size: 0.88rem;
        font-weight: 500;
        display: flex;
        align-items: flex-start;
        gap: 8px;
    }
    .win-card {
        background-color: var(--color-success-bg);
        border-left: 4px solid var(--color-success);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: var(--color-success-text);
        font-size: 0.88rem;
        font-weight: 500;
        display: flex;
        align-items: flex-start;
        gap: 8px;
    }

    /* Job Match Card */
    .job-item-card {
        background-color: var(--bg-surface);
        border: 0.5px solid var(--border-color);
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
        max-width: 780px;
        margin: 40px auto 20px auto;
    }
    .landing-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.03em;
        margin-bottom: 8px;
    }
    .landing-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-bottom: 28px;
    }
    .trust-badge-row {
        display: flex;
        justify-content: center;
        gap: 24px;
        margin-top: 32px;
        flex-wrap: wrap;
    }
    .trust-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-secondary);
        background: var(--bg-surface);
        padding: 8px 16px;
        border-radius: 999px;
        border: 0.5px solid var(--border-color);
        box-shadow: var(--card-shadow);
    }

    /* Sub-score Progress Row */
    .subscore-row {
        margin-bottom: 14px;
    }
    .subscore-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* 4-Phase Horizontal Roadmap Timeline */
    .timeline-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 20px 0;
    }
    @media (max-width: 768px) {
        .timeline-container {
            grid-template-columns: 1fr;
        }
    }
    .timeline-phase-card {
        background-color: var(--bg-surface);
        border: 0.5px solid var(--border-color);
        border-top: 4px solid var(--accent-indigo);
        border-radius: 10px;
        padding: 16px;
        box-shadow: var(--card-shadow);
    }
    .timeline-phase-num {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--accent-indigo);
        margin-bottom: 4px;
        letter-spacing: 0.05em;
    }
    .timeline-phase-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    .timeline-phase-desc {
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.35;
    }

    /* Streamlit Tab Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 4px;
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.92rem;
        padding: 8px 18px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-bg) !important;
        color: var(--accent-indigo) !important;
        font-weight: 700 !important;
    }

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: 0.5px solid var(--border-color);
        transition: all 0.15s ease;
    }
    .stButton>button[kind="primary"] {
        background-color: var(--accent-indigo);
        color: white;
        border: none;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: var(--accent-indigo-hover);
    }
</style>
"""
