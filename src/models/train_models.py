"""
Model Training & Benchmarking Pipeline.
Trains role classification, salary regression, and TF-IDF semantic matching artifacts.
"""

import json
import os
import skops.io as sio
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    JOBS_DATASET_PATH,
    SALARY_DATASET_PATH,
    ONTOLOGY_PATH,
    ROLE_CLASSIFIER_PATH,
    SALARY_REGRESSOR_PATH,
    TFIDF_MATCHER_PATH,
    MODELS_DIR
)


def train_role_classifier():
    print("=" * 60)
    print("Training Role Classification Models...")
    print("=" * 60)

    # 1. Load Data
    df_jobs = pd.read_csv(JOBS_DATASET_PATH)
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        ontology = json.load(f)

    # Extract all distinct skills across ontology
    all_skill_ids = []
    for cat in ontology["categories"].values():
        for s in cat["skills"]:
            all_skill_ids.append(s["id"])
    all_skill_ids = sorted(list(set(all_skill_ids)))
    
    # Build multi-hot feature matrix X
    def encode_skills(skills_str):
        if pd.isna(skills_str):
            return [0.0] * len(all_skill_ids)
        present = set(str(skills_str).split(","))
        return [1.0 if s in present else 0.0 for s in all_skill_ids]

    X_list = [encode_skills(s) for s in df_jobs["all_skills"]]
    X = np.array(X_list, dtype=np.float64)
    y = np.array(df_jobs["role_id"].tolist())
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Benchmark candidates
    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=12, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=80, max_depth=5, random_state=42)
    }
    
    results = {}
    best_name = None
    best_f1 = -1.0
    best_model = None
    
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        results[name] = {"accuracy": float(acc), "f1": float(f1)}
        print(f"[{name}] Accuracy: {acc * 100:.2f}% | F1-Score: {f1 * 100:.2f}%")
        
        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_model = model
            
    print(f"\n--> Selected Best Role Classifier: {best_name} (F1: {best_f1*100:.2f}%)")
    
    # Save model artifact
    artifact = {
        "model": best_model,
        "model_name": best_name,
        "skill_feature_names": all_skill_ids,
        "classes": list(best_model.classes_),
        "benchmark_metrics": results
    }
    sio.dump(artifact, ROLE_CLASSIFIER_PATH)
    print(f"Saved Role Classifier to {ROLE_CLASSIFIER_PATH}")
    return results


def train_salary_regressor():
    print("\n" + "=" * 60)
    print("Training Salary Prediction Regressors...")
    print("=" * 60)

    df_salary = pd.read_csv(SALARY_DATASET_PATH)
    
    # Categorical and numerical features
    cat_cols = ["role_id", "education", "location_tier", "company_tier"]
    num_cols = ["experience_years", "skill_count"]
    
    # Preprocessing
    ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    X_cat = ohe.fit_transform(df_salary[cat_cols])
    X_num = np.array(df_salary[num_cols].values, dtype=np.float64)
    
    scaler = StandardScaler()
    X_num_scaled = scaler.fit_transform(X_num)
    
    X = np.hstack([X_cat, X_num_scaled])
    y = np.array(df_salary["salary_lpa"].tolist(), dtype=np.float64)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    regressors = {
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=120, max_depth=12, random_state=42),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    }
    
    results = {}
    best_name = None
    best_r2 = -1.0
    best_model = None
    
    for name, model in regressors.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {"MAE": float(mae), "RMSE": float(rmse), "R2": float(r2)}
        print(f"[{name}] MAE: {mae:.2f} LPA | RMSE: {rmse:.2f} LPA | R2 Score: {r2*100:.2f}%")
        
        if r2 > best_r2:
            best_r2 = r2
            best_name = name
            best_model = model
            
    print(f"\n--> Selected Best Salary Regressor: {best_name} (R2: {best_r2*100:.2f}%)")
    
    artifact = {
        "model": best_model,
        "model_name": best_name,
        "one_hot_encoder": ohe,
        "scaler": scaler,
        "cat_cols": cat_cols,
        "num_cols": num_cols,
        "benchmark_metrics": results
    }
    sio.dump(artifact, SALARY_REGRESSOR_PATH)
    print(f"Saved Salary Regressor to {SALARY_REGRESSOR_PATH}")
    return results


def train_tfidf_matcher():
    print("\n" + "=" * 60)
    print("Fitting TF-IDF Job Matching Engine...")
    print("=" * 60)

    df_jobs = pd.read_csv(JOBS_DATASET_PATH)
    
    # Combine title, description, and skills into unified searchable text corpus
    corpus = (
        df_jobs["role_title"].astype(str) + " " +
        df_jobs["description"].astype(str) + " " +
        df_jobs["all_skills"].astype(str).apply(lambda s: " ".join(s.split(",")))
    ).tolist()
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        max_features=5000,
        sublinear_tf=True
    )
    
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    artifact = {
        "vectorizer": vectorizer,
        "tfidf_matrix": tfidf_matrix,
        "job_ids": df_jobs["job_id"].tolist(),
        "job_titles": df_jobs["title"].tolist(),
        "role_ids": df_jobs["role_id"].tolist()
    }
    
    sio.dump(artifact, TFIDF_MATCHER_PATH)
    print(f"Fitted TF-IDF vocabulary on {len(corpus)} jobs (Matrix shape: {tfidf_matrix.shape}).")
    print(f"Saved TF-IDF Matcher to {TFIDF_MATCHER_PATH}")


if __name__ == "__main__":
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    train_role_classifier()
    train_salary_regressor()
    train_tfidf_matcher()
    print("\nAll ML training and artifact generation completed successfully!")
