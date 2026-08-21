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
    "Strong": "#10B981",              # Emerald Green
    "Needs Improvement": "#F59E0B",    # Amber
    "Missing": "#EF4444"               # Rose Red
}
