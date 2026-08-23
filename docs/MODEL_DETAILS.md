# 🤖 Machine Learning Models & Evaluation Details

This document details the machine learning methodology, datasets, feature engineering pipelines, model training benchmarks, and evaluation metrics implemented in the **Career Intelligence Engine**.

---

## 1. Datasets Overview

The system utilizes structured synthetic and benchmark datasets generated from industry market distributions in India and global tech hubs:

| Dataset | Records | Features / Dimensions | Purpose |
| :--- | :--- | :--- | :--- |
| **`jobs_dataset.csv`** | 3,500 postings | `job_id`, `role_id`, `role_title`, `company`, `location`, `min_exp`, `max_exp`, `salary_min_lpa`, `salary_max_lpa`, `mandatory_skills`, `preferred_skills`, `description` | Job compatibility matching, market hiring hubs, and company demand trends |
| **`salary_benchmarks.csv`** | 5,000 records | `role_id`, `experience_years`, `skill_count`, `education_level`, `company_tier`, `salary_lpa` | Supervised regression training for market compensation forecasting |
| **`skills_ontology.json`** | 500+ skills, 26 roles | Categorized taxonomy with canonical names, regex aliases, milestone projects, and curated learning URLs | Entity normalization, gap analysis, and ATS scoring |

---

## 2. Machine Learning Models & Architectures

### 2.1 Multi-Class Role Recommendation Classifier
- **Task**: Supervised classification predicting the most suitable career role (out of 26 target tech roles) given a candidate's detected skills vector.
- **Input Features**: Multi-hot binary vector of 500+ skill dimensions.
- **Models Benchmarked**:
  - **Random Forest Classifier** (`n_estimators=100`, `max_depth=20`, `random_state=42`)
  - **Logistic Regression** (`C=1.0`, `max_iter=500`)
  - **Gradient Boosting Classifier**
- **Evaluation Results (80/20 Train-Test Split)**:
  - **Selected Model**: **Random Forest Classifier**
  - **Accuracy**: $99.14\%$
  - **Weighted F1-Score**: $99.01\%$
  - **Precision**: $99.20\%$ | **Recall**: $99.05\%$
- **Artifact**: Saved as `models/role_classifier.pkl`.

---

### 2.2 Multi-Variable Salary Compensation Regressor
- **Task**: Continuous regression predicting competitive base compensation in **₹ Lakhs Per Annum (LPA)**.
- **Input Features**:
  - `role_id` (One-Hot Encoded across 26 categories)
  - `experience_years` (Standardized float, clipped to 0–25 years)
  - `skill_count` (Integer count of verified candidate skills)
  - `education_level` (Ordinal / One-Hot encoded: Bachelor's, Master's, Ph.D., Diploma)
- **Models Benchmarked**:
  - **Ridge Regression** (`alpha=1.0`)
  - **Gradient Boosting Regressor** (`n_estimators=100`, `learning_rate=0.1`, `max_depth=4`)
  - **Random Forest Regressor** (`n_estimators=100`, `max_depth=12`)
- **Evaluation Results (80/20 Train-Test Split)**:
  - **Selected Model**: **Ridge Regressor** (Linear Regularized baseline ensuring smooth, monotonic salary growth without tree overfitting)
  - **Coefficient of Determination ($R^2$)**: $89.71\%$
  - **Mean Absolute Error (MAE)**: $\approx 1.84\text{ LPA}$
  - **Root Mean Squared Error (RMSE)**: $\approx 2.31\text{ LPA}$
- **Artifact**: Saved as `models/salary_regressor.pkl`.

---

### 2.3 Hybrid TF-IDF & Cosine Similarity Matcher
- **Task**: Semantic and keyword relevance ranking between candidate profile tokens and 3,500+ job descriptions.
- **Pipeline**:
  - `TfidfVectorizer(max_features=2500, stop_words='english', ngram_range=(1, 2))` fitted on job descriptions and required skills.
  - Cosine similarity computed between candidate skill representation and pre-computed job TF-IDF sparse matrix.
- **Artifact**: Saved as `models/tfidf_matcher.pkl`.

---

## 3. Retraining & Benchmarking Pipeline

To regenerate datasets and retrain all models from scratch:

```bash
# Step 1: Generate processed datasets
python data/generate_datasets.py

# Step 2: Train and evaluate ML models
python -m src.models.train_models
```

---

## 4. Model Limitations & Transparency Notice

- **Estimates, Not Guarantees**: Predicted salaries and ATS scores are statistical approximations based on training data distributions in Indian and international tech markets. Actual employer compensation and ATS hiring decisions depend on portfolio quality, interview performance, negotiation, and individual company compensation bands.
- **Domain Boundaries**: The skill taxonomy is optimized for modern technology, data, software, cloud, and engineering roles. Resumes outside technology domains (e.g. healthcare, legal) will have lower keyword detection rates.
