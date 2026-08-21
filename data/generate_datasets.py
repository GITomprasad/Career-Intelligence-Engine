"""
Dataset Generator for Career Intelligence Engine.
Generates realistic job market postings, salary benchmarks, and test candidate resumes.
"""

import json
import os
import random
import numpy as np
import pandas as pd

# Set seed for reproducible synthetic dataset generation
random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
SAMPLE_RESUMES_DIR = os.path.join(DATA_DIR, "sample_resumes")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(SAMPLE_RESUMES_DIR, exist_ok=True)

# Load skills ontology
ontology_path = os.path.join(DATA_DIR, "skills_ontology.json")
with open(ontology_path, "r", encoding="utf-8") as f:
    ontology = json.load(f)

ROLES = ontology["roles"]
CATEGORIES = ontology["categories"]

# Market meta definitions
COMPANIES = [
    ("Google India", "Tech Giant", "Tier-1", 1.35),
    ("Microsoft IDC", "Tech Giant", "Tier-1", 1.30),
    ("Amazon Development Centre", "Tech Giant", "Tier-1", 1.28),
    ("Flipkart", "High-Growth Unicorn", "Tier-1", 1.22),
    ("Swiggy", "High-Growth Unicorn", "Tier-1", 1.20),
    ("Zomato", "High-Growth Unicorn", "Tier-1", 1.18),
    ("JPMorgan Chase & Co.", "Fintech & Investment Banking", "Tier-1", 1.25),
    ("Goldman Sachs", "Fintech & Investment Banking", "Tier-1", 1.27),
    ("Tiger Analytics", "Analytics Consultancy", "Tier-2", 1.05),
    ("Fractal Analytics", "Analytics Consultancy", "Tier-2", 1.05),
    ("Mu Sigma", "Analytics Consultancy", "Tier-2", 0.95),
    ("TCS Innovation Labs", "IT Services & Enterprise", "Tier-2", 0.85),
    ("Infosys Center of AI", "IT Services & Enterprise", "Tier-2", 0.85),
    ("Wipro Technologies", "IT Services & Enterprise", "Tier-2", 0.82),
    ("Cognizant Digital", "IT Services & Enterprise", "Tier-2", 0.85),
    ("Razorpay", "Fintech Unicorn", "Tier-1", 1.22),
    ("CRED", "Fintech Unicorn", "Tier-1", 1.25),
    ("InMobi", "AdTech Unicorn", "Tier-1", 1.18),
    ("PhonePe", "Fintech Unicorn", "Tier-1", 1.20),
    ("Ola Electric", "EV Tech Unicorn", "Tier-1", 1.15),
    ("Ola Cabs", "High-Growth Unicorn", "Tier-1", 1.12),
    ("Target India", "Retail Enterprise", "Tier-2", 1.05),
    ("Walmart Global Tech", "Retail Tech", "Tier-1", 1.22),
    ("Deloitte USI", "Consulting Tier-1", "Tier-2", 1.08),
    ("PwC Accelerate", "Consulting Tier-1", "Tier-2", 1.02),
    ("EY GDS", "Consulting Tier-1", "Tier-2", 1.00),
    ("KPMG Tech Consulting", "Consulting Tier-1", "Tier-2", 1.00),
    ("Accenture Applied Intelligence", "Global IT Consulting", "Tier-2", 1.02),
    ("IBM India Research", "Enterprise Tech", "Tier-2", 1.10),
    ("Cisco Systems", "Enterprise Tech", "Tier-1", 1.20),
    ("Qualcomm India", "Hardware & AI", "Tier-1", 1.25),
    ("NVIDIA Bangalore", "AI Tech Giant", "Tier-1", 1.40),
    ("Uber Engineering", "Tech Giant", "Tier-1", 1.35),
    ("Atlassian India", "Product Tech", "Tier-1", 1.32),
    ("Postman", "Product Unicorn", "Tier-1", 1.25),
]

LOCATIONS = [
    ("Bangalore, Karnataka", 1.15, "Tier-1"),
    ("Hyderabad, Telangana", 1.08, "Tier-1"),
    ("Pune, Maharashtra", 1.02, "Tier-1"),
    ("Mumbai, Maharashtra", 1.12, "Tier-1"),
    ("Gurgaon / Delhi NCR", 1.10, "Tier-1"),
    ("Chennai, Tamil Nadu", 0.98, "Tier-2"),
    ("Noida, Uttar Pradesh", 0.96, "Tier-2"),
    ("Ahmedabad, Gujarat", 0.88, "Tier-3"),
    ("Kolkata, West Bengal", 0.88, "Tier-3"),
    ("Remote (India)", 1.05, "Remote"),
]

EXPERIENCE_LEVELS = [
    ("Entry Level / Fresher", 0, 1, 0.25),
    ("Junior Associate", 1, 3, 0.35),
    ("Mid-Level Specialist", 3, 6, 0.25),
    ("Senior Engineer / Lead", 6, 10, 0.12),
    ("Principal / Staff", 10, 15, 0.03),
]

EDUCATION_LEVELS = [
    ("B.Tech / B.E. Computer Science", 1.0),
    ("B.Tech / B.E. Non-CS / IT", 0.95),
    ("M.Tech / M.E. Data Science / AI", 1.15),
    ("M.S. in Computer Science", 1.20),
    ("B.Sc. / B.C.A. Statistics / CS", 0.90),
    ("M.Sc. / M.C.A. Data Analytics", 1.05),
    ("Ph.D. in AI / Machine Learning", 1.40),
]


def generate_job_postings(num_jobs=3500):
    jobs = []
    
    for i in range(num_jobs):
        role_key = random.choice(list(ROLES.keys()))
        role_info = ROLES[role_key]
        company, company_type, comp_tier, comp_multiplier = random.choice(COMPANIES)
        loc_name, loc_multiplier, loc_tier = random.choice(LOCATIONS)
        
        # Pick experience level according to distribution
        exp_weights = [e[3] for e in EXPERIENCE_LEVELS]
        exp_tier = random.choices(EXPERIENCE_LEVELS, weights=exp_weights)[0]
        min_exp = exp_tier[1]
        max_exp = exp_tier[2]
        exp_years = random.randint(min_exp, max_exp)
        
        # Skills selection
        core_skills = role_info["core_skills"]
        rec_skills = role_info["recommended_skills"]
        opt_skills = role_info["optional_skills"]
        
        # Select required skills: almost all core skills + subset of recommended
        num_req_core = max(1, len(core_skills) - random.choice([0, 0, 1]))
        selected_core = random.sample(core_skills, min(num_req_core, len(core_skills)))
        selected_rec = random.sample(rec_skills, min(random.randint(1, 3), len(rec_skills)))
        required_skills = list(set(selected_core + selected_rec))
        
        # Select optional skills
        selected_opt = random.sample(opt_skills + rec_skills, min(random.randint(1, 3), len(opt_skills + rec_skills)))
        preferred_skills = [s for s in selected_opt if s not in required_skills]
        
        # Salary calculation (in LPA - Lakhs Per Annum)
        base_min = role_info["base_salary_min_lpa"]
        base_max = role_info["base_salary_max_lpa"]
        exp_mult = 1.0 + (exp_years * (role_info["experience_multiplier"] - 1.0) / 4.0)
        
        calculated_min = base_min * exp_mult * comp_multiplier * loc_multiplier
        calculated_max = base_max * exp_mult * comp_multiplier * loc_multiplier
        
        # Add slight natural variance (+/- 8%)
        salary_min_lpa = round(calculated_min * random.uniform(0.92, 1.08), 1)
        salary_max_lpa = round(calculated_max * random.uniform(0.95, 1.10), 1)
        if salary_max_lpa <= salary_min_lpa:
            salary_max_lpa = round(salary_min_lpa * 1.3, 1)
        
        # Job Description Generator
        skills_str = ", ".join([s.replace("_", " ").title() for s in required_skills])
        pref_str = ", ".join([s.replace("_", " ").title() for s in preferred_skills])
        
        description = (
            f"We are hiring a talented {role_info['title']} to join {company} in {loc_name}. "
            f"{role_info['description']} "
            f"You will work with high-performing cross-functional teams to build scalable solutions. "
            f"Key Requirements: {exp_years}+ years of experience with {skills_str}. "
            f"Preferred / Good to have: {pref_str}. "
            f"Strong analytical mindset, problem-solving, and communication skills required."
        )
        
        job_id = f"JOB-{1000 + i}"
        jobs.append({
            "job_id": job_id,
            "title": f"{exp_tier[0].split('/')[0].strip()} {role_info['title']}" if exp_years > 0 else f"Junior {role_info['title']}",
            "role_id": role_key,
            "role_title": role_info["title"],
            "category": role_info["category"],
            "company": company,
            "company_type": company_type,
            "company_tier": comp_tier,
            "location": loc_name,
            "location_tier": loc_tier,
            "min_experience_years": min_exp,
            "max_experience_years": max_exp,
            "avg_experience_years": exp_years,
            "required_skills": ",".join(required_skills),
            "preferred_skills": ",".join(preferred_skills),
            "all_skills": ",".join(list(set(required_skills + preferred_skills))),
            "salary_min_lpa": salary_min_lpa,
            "salary_max_lpa": salary_max_lpa,
            "salary_mid_lpa": round((salary_min_lpa + salary_max_lpa) / 2.0, 1),
            "description": description,
            "posted_days_ago": random.randint(1, 30),
            "applicants_count": random.randint(15, 380)
        })
        
    df = pd.DataFrame(jobs)
    output_file = os.path.join(PROCESSED_DIR, "jobs_dataset.csv")
    df.to_csv(output_file, index=False)
    print(f"Successfully generated {len(df)} job postings at: {output_file}")
    return df


def generate_salary_benchmarks(num_records=5000):
    benchmarks = []
    
    for i in range(num_records):
        role_key = random.choice(list(ROLES.keys()))
        role_info = ROLES[role_key]
        company, company_type, comp_tier, comp_multiplier = random.choice(COMPANIES)
        loc_name, loc_multiplier, loc_tier = random.choice(LOCATIONS)
        edu_name, edu_multiplier = random.choice(EDUCATION_LEVELS)
        
        exp_years = round(random.choices(
            [random.uniform(0, 2), random.uniform(2, 5), random.uniform(5, 9), random.uniform(9, 15)],
            weights=[0.35, 0.35, 0.20, 0.10]
        )[0], 1)
        
        # Skill pool count
        total_skills_count = random.randint(4, 18)
        
        # Salary formula with realistic micro-factors
        base_min = role_info["base_salary_min_lpa"]
        base_max = role_info["base_salary_max_lpa"]
        exp_growth = (exp_years ** 0.85) * (role_info["experience_multiplier"] - 1.0) * 2.2
        skill_bonus = (total_skills_count - 4) * 0.22
        
        raw_salary = (base_min + (base_max - base_min) * 0.35 + exp_growth + skill_bonus) * comp_multiplier * loc_multiplier * edu_multiplier
        # Add random noise
        salary_lpa = round(max(3.0, raw_salary * random.uniform(0.92, 1.08)), 2)
        
        benchmarks.append({
            "record_id": f"SAL-{2000 + i}",
            "role_id": role_key,
            "role_title": role_info["title"],
            "category": role_info["category"],
            "experience_years": exp_years,
            "education": edu_name,
            "education_multiplier": edu_multiplier,
            "location": loc_name,
            "location_tier": loc_tier,
            "company_type": company_type,
            "company_tier": comp_tier,
            "skill_count": total_skills_count,
            "salary_lpa": salary_lpa
        })
        
    df_salary = pd.DataFrame(benchmarks)
    output_file = os.path.join(PROCESSED_DIR, "salary_benchmarks.csv")
    df_salary.to_csv(output_file, index=False)
    print(f"Successfully generated {len(df_salary)} salary records at: {output_file}")
    return df_salary


def generate_sample_resumes():
    """Generates sample test resumes for immediate testing."""
    samples = {
        "data_analyst_candidate": {
            "text": """
OM PRAKASH SAHU
Email: omprakash.sahu@email.com | Phone: +91 9876543210
LinkedIn: linkedin.com/in/omprakash-sahu | GitHub: github.com/omprakash-sahu
Location: Bangalore, India

PROFESSIONAL SUMMARY
Aspiring Data Analyst with strong hands-on experience in SQL, Python, Excel, Power BI, and statistical analysis. Proven track record of turning business data into executive dashboards and actionable business metrics.

EDUCATION
Bachelor of Technology in Computer Science & Engineering (2020 - 2024)
National Institute of Technology, Rourkela | CGPA: 8.6 / 10.0

TECHNICAL SKILLS
- Programming Languages: Python, SQL (PostgreSQL, MySQL), R
- Data Analysis & BI: Power BI, Tableau, Advanced Excel (VBA, Macros, Pivot Tables), DAX
- Libraries: Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn
- Databases & Tools: PostgreSQL, MySQL, Git, GitHub, Jupyter Notebooks, JIRA
- Core Competencies: Statistical Analysis, A/B Testing, KPI Dashboards, ETL Pipelines, Data Cleansing

WORK EXPERIENCE & INTERNSHIPS
Data Analytics Intern | FinTech Solutions Pvt. Ltd. (Jan 2024 - June 2024)
- Built interactive Power BI dashboards tracking monthly active users (MAU) and churn rates across 250,000+ customers.
- Wrote complex SQL queries, window functions, and CTEs to extract data from PostgreSQL tables, reducing reporting query execution time by 35%.
- Performed exploratory data analysis (EDA) and cohort analysis using Python (Pandas, Seaborn) to uncover key retention drivers.

PROJECTS
1. E-Commerce Sales & Customer Segmentation Analytics
- Ingested 100k+ transaction records, cleaned raw data with Pandas, and modeled customer lifetime value (CLV).
- Designed interactive 4-page Power BI dashboard with dynamic KPI drill-downs, increasing insights discovery speed by 40%.
- Tech Stack: Python, SQL, Power BI, Pandas, Matplotlib.

2. Healthcare Patient Readmission Predictive Dashboard
- Conducted statistical hypothesis testing and built exploratory charts on 50k patient medical records.
- Deployed a Tableau dashboard highlighting critical risk factors for early hospital readmissions.
- Tech Stack: Python, Tableau, Statistics, Excel.

CERTIFICATIONS
- Microsoft Certified: Power BI Data Analyst Associate (PL-300)
- Google Data Analytics Professional Certificate (Coursera)
- Advanced SQL for Data Scientists (LinkedIn Learning)
"""
        },
        "data_scientist_candidate": {
            "text": """
AARAV MEHTA
Email: aarav.mehta@datascience.io | Phone: +91 9123456780
LinkedIn: linkedin.com/in/aarav-mehta | GitHub: github.com/aarav-mehta
Location: Hyderabad, India

PROFESSIONAL SUMMARY
Data Scientist with 2+ years of experience in developing machine learning models, statistical inference, NLP pipelines, and data-driven solutions. Passionate about end-to-end ML lifecycles from EDA to model deployment.

EDUCATION
Master of Technology in Artificial Intelligence & Data Science (2021 - 2023)
Indian Institute of Technology, Hyderabad | CGPA: 9.1 / 10.0
Bachelor of Technology in Computer Science (2017 - 2021) | CGPA: 8.8 / 10.0

TECHNICAL SKILLS
- Programming & Scripting: Python, SQL, C++, Bash
- Machine Learning & Deep Learning: Scikit-learn, XGBoost, LightGBM, PyTorch, TensorFlow, Keras
- NLP & LLMs: SpaCy, NLTK, HuggingFace Transformers, BERT, Prompt Engineering, LangChain
- Data Science Stack: Pandas, NumPy, SciPy, Matplotlib, Seaborn, Feature Engineering
- Cloud, MLOps & Tools: Docker, Git, MLflow, FastAPI, AWS (S3, EC2), PostgreSQL, Linux

PROFESSIONAL EXPERIENCE
Associate Data Scientist | CogniTech AI Labs (July 2023 - Present)
- Engineered XGBoost and Random Forest predictive models for customer churn forecasting with an ROC-AUC of 0.89.
- Built automated feature engineering and preprocessing pipelines using Scikit-Learn pipelines and Pandas, reducing model retraining time by 50%.
- Created RESTful microservice with FastAPI and Docker to serve real-time inferences with <60ms p99 latency.
- Collaborated with product and engineering teams using Agile Scrum methodologies to deliver AI features.

KEY PROJECTS
1. Intelligent Customer Support NLP Intent Classifier & RAG Agent
- Built an NLP text classification system with HuggingFace BERT and fine-tuned embeddings on 40,000+ support tickets (94% F1-score).
- Developed a LangChain-powered RAG pipeline with vector search for automated resolution of common queries.
- Tech Stack: Python, PyTorch, Transformers, LangChain, FastAPI, Docker.

2. Financial Fraud Detection with Anomaly Detection & Imbalanced Learning
- Implemented SMOTE, Isolation Forests, and ensemble tree models on 1.2M credit card transactions, detecting fraudulent patterns with 91% recall.
- Tech Stack: Python, Scikit-learn, XGBoost, Pandas, SQL.

PUBLICATIONS & CERTIFICATIONS
- AWS Certified Machine Learning - Specialty
- DeepLearning.AI Deep Learning Specialization (Andrew Ng)
"""
        },
        "ml_engineer_candidate": {
            "text": """
PRIYA SHARMA
Email: priya.sharma@mleng.dev | Phone: +91 9988776655
LinkedIn: linkedin.com/in/priyasharma-ml | GitHub: github.com/priyasharma
Location: Bangalore, India

PROFESSIONAL SUMMARY
Machine Learning Engineer with 3+ years of experience specializing in scalable ML systems, MLOps, deep learning architectures, and production model serving on Kubernetes and AWS.

EDUCATION
B.Tech in Computer Science & Engineering (2019 - 2023)
VIT Vellore | CGPA: 8.9 / 10.0

TECHNICAL SKILLS
- Languages: Python, C++, SQL, Bash
- Frameworks & DL: PyTorch, TensorFlow, Scikit-learn, ONNX, TensorRT
- MLOps & Infrastructure: Docker, Kubernetes, CI/CD, MLflow, Kubeflow, AWS (EC2, S3, SageMaker, Lambda), Linux
- Backend & Serving: FastAPI, gRPC, Triton Inference Server, Redis, PostgreSQL
- Engineering Practices: System Design, Git, Agile, Unit Testing, Distributed Training

EXPERIENCE
Machine Learning Engineer | Apex AI Systems (June 2023 - Present)
- Designed and maintained automated CI/CD MLOps pipelines using Docker, GitHub Actions, and Kubernetes, deploying 12+ computer vision and NLP models.
- Optimized PyTorch model inference using ONNX Runtime and TensorRT, achieving 3.8x throughput speedup and cutting cloud GPU compute costs by 45%.
- Implemented real-time data drift and concept drift monitoring with Prometheus and MLflow.

PROJECTS
1. Real-time Distributed Model Inference Engine
- Architected a high-concurrency model serving platform using FastAPI, Triton, and Redis caching handling 1,500 req/sec at <30ms latency.
- Tech Stack: Python, PyTorch, Docker, Kubernetes, Triton, Redis, AWS.

2. MLOps Automated Training & Deployment Pipeline
- Built end-to-end reproducible pipeline from S3 data ingestion to automated model evaluation and containerized deployment.
- Tech Stack: MLflow, Docker, AWS SageMaker, GitHub Actions, PyTorch.
"""
        },
        "fresh_graduate_candidate": {
            "text": """
ROHAN GUPTA
Email: rohan.gupta.tech@gmail.com | Phone: +91 9012345678
LinkedIn: linkedin.com/in/rohan-gupta-dev | GitHub: github.com/rohangupta-code
Location: Pune, India

OBJECTIVE
Motivated Computer Science graduate seeking an entry-level Data Analyst / Junior Data Scientist role. Solid foundation in Python, SQL, Statistics, and foundational Machine Learning.

EDUCATION
B.E. in Information Technology (2020 - 2024)
Pune Institute of Computer Technology (PICT) | CGPA: 8.2 / 10.0

TECHNICAL SKILLS
- Programming: Python, SQL, C++, HTML, CSS, JavaScript
- Data Analysis: Pandas, NumPy, Matplotlib, Seaborn, Excel
- Basic Machine Learning: Scikit-learn, Linear Regression, Logistic Regression, Decision Trees
- Tools: Git, GitHub, VS Code, Jupyter Notebook, MySQL

ACADEMIC PROJECTS
1. House Price Prediction System
- Cleaned and prepared tabular housing datasets, conducted exploratory data analysis and feature scaling.
- Trained multiple Scikit-learn regression models (Linear Regression, Random Forest), achieving 84% R2 score.
- Tech Stack: Python, Pandas, Scikit-learn, Matplotlib.

2. Student Academic Performance Analysis
- Analyzed student demographic and test score data using Python and MySQL to find factors correlating with exam performance.
- Visualized findings through interactive charts and statistical summaries.
- Tech Stack: Python, MySQL, Seaborn, Excel.

CERTIFICATIONS
- Python for Data Science and Machine Learning Bootcamp (Udemy)
- SQL Fundamentals (HackerRank 5-star Gold Badge)
"""
        }
    }
    
    for name, data in samples.items():
        txt_path = os.path.join(SAMPLE_RESUMES_DIR, f"{name}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(data["text"].strip())
        print(f"Generated sample resume text: {txt_path}")
        
        # Also generate PDF version using reportlab
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            pdf_path = os.path.join(SAMPLE_RESUMES_DIR, f"{name}.pdf")
            doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            
            story = []
            lines = data["text"].strip().split("\n")
            for line in lines:
                line_str = line.strip()
                if not line_str:
                    story.append(Spacer(1, 6))
                elif line_str.isupper() and len(line_str) < 40:
                    story.append(Paragraph(f"<b><font color='#1E3A8A'>{line_str}</font></b>", styles["Heading3"]))
                    story.append(Spacer(1, 3))
                else:
                    safe_line = line_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(safe_line, styles["Normal"]))
            
            doc.build(story)
            print(f"Generated sample resume PDF: {pdf_path}")
        except Exception as e:
            print(f"Notice: Could not generate PDF for {name}: {e}")

if __name__ == "__main__":
    print("Starting dataset and sample resume generation...")
    generate_job_postings(3500)
    generate_salary_benchmarks(5000)
    generate_sample_resumes()
    print("All datasets and sample resumes generated successfully!")
