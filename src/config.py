"""
Configuration and constants for the Career Intelligence Engine.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
SAMPLE_RESUMES_DIR = DATA_DIR / "sample_resumes"
ONTOLOGY_PATH = DATA_DIR / "skills_ontology.json"

JOBS_DATASET_PATH = PROCESSED_DATA_DIR / "jobs_dataset.csv"
SALARY_DATASET_PATH = PROCESSED_DATA_DIR / "salary_benchmarks.csv"

ROLE_CLASSIFIER_PATH = MODELS_DIR / "role_classifier.pkl"
SALARY_REGRESSOR_PATH = MODELS_DIR / "salary_regressor.pkl"
TFIDF_MATCHER_PATH = MODELS_DIR / "tfidf_matcher.pkl"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Matching Weights
WEIGHT_SKILLS = 0.50
WEIGHT_NLP_SIMILARITY = 0.25
WEIGHT_EXPERIENCE = 0.15
WEIGHT_EDUCATION = 0.10

# ATS Scorer Weights
WEIGHT_ATS_KEYWORDS = 0.40
WEIGHT_ATS_FORMAT = 0.30
WEIGHT_ATS_EXPERIENCE = 0.30

# v2 Visual Design Tokens (Warm off-white base & indigo accent)
THEME_TOKENS = {
    "base_bg": "#F8F7F5",
    "surface": "#FFFFFF",
    "border": "#E8E6E0",
    "text_primary": "#1A1A18",
    "text_secondary": "#6B7280",
    "accent_indigo": "#4F46E5",
    "accent_bg": "#EEF2FF",
    "success": "#16A34A",
    "success_bg": "#DCFCE7",
    "warning": "#D97706",
    "warning_bg": "#FEF3C7",
    "danger": "#DC2626",
    "danger_bg": "#FEE2E2",
}

# Color Mapping for UI Badges and Categories
CATEGORY_COLORS = {
    "Analytics": "#2563EB",            # Blue
    "Data Science": "#7C3AED",         # Purple
    "Data Science & Engineering": "#9333EA", # Deep Purple
    "Engineering": "#059669",          # Green
    "Engineering & DevOps": "#0D9488",  # Teal
    "Software Engineering": "#D97706", # Amber
    "Cloud & Infrastructure": "#EA580C",# Orange
    "Product & Strategy": "#DC2626"     # Red
}

SKILL_LEVEL_COLORS = {
    "Strong": "#16A34A",              # Green
    "Needs Improvement": "#D97706",    # Amber
    "Missing": "#DC2626"               # Red
}

