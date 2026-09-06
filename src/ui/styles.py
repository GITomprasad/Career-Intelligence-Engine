"""
Centralized CSS Design System for Career Intelligence Engine v2.
Dual-Engine Contrast System: Perfect Dark Mode + Flawless Color-Corrected Light Mode.
Ensures 100% text legibility, accessible contrast ratios, and crisp button text in both themes.
"""

from pathlib import Path

def get_css() -> str:
    """
    Returns unified CSS styling for the application.
    """
    css_path = Path(__file__).parent / "styles.css"
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    return f"\n<style>\n{css_content}\n</style>\n"
