# 🌟 Career Intelligence Engine — Feature Documentation

A comprehensive guide to the capabilities, analytical engines, and user-facing modules of the **Career Intelligence Engine**.

---

## 1. 📂 Universal Multi-Format & AI OCR Resume Ingestion
- **Document Support**: Ingests `.pdf`, `.docx`, `.doc`, `.rtf`, `.txt`, `.md`, `.html`, and structured `.json` resumes.
- **Neural OCR for Image Resumes**: Ingests `.jpg`, `.jpeg`, `.png`, `.webp`, `.tiff`, and `.bmp` files (e.g. photos or scans of resumes) and extracts text using **RapidOCR ONNX Runtime** with zero external binaries required.
- **Entity Extraction**: Automatically identifies Candidate Name, Email, Phone Number (Indian & international formats), Location, LinkedIn URL, GitHub handle, Portfolio URL, Degrees, Major, Institution, CGPA/Percentage, and Graduation Year.

---

## 2. 🎯 Instant ATS Screening Score & Diagnostics
- **Weighted Scoring**: Evaluates candidate compatibility against target role standards across three dimensions:
  - **Keyword Match (50%)**: Presence of mandatory core skills and recommended secondary skills.
  - **Format Quality & Readability (30%)**: Section completeness, contact info validity, bullet points, and strong action verb density.
  - **Experience Depth (20%)**: Tenure fit relative to role requirements.
- **Visual SVG Progress Ring**: Dynamic color ring displaying score out of 100 with actionable screening verdicts:
  - 🟢 **Strong Match (71 - 100)**: Clean alignment with ATS screening criteria.
  - 🟡 **Needs Work (41 - 70)**: Gaps in critical keywords or formatting structure.
  - 🔴 **Critical Action Required (0 - 40)**: Severe keyword mismatches or missing sections.
- **Strengths & Actionable Fixes Breakdown**: Categorized 2-column cards listing exact positive signals vs high-priority improvements.

---

## 3. 🧠 500+ Skills Ontology & Canonical Alias Normalizer
- Structured taxonomy spanning 7 major tech categories:
  1. *Programming Languages* (Python, TypeScript, Go, Rust, Java, C++, Swift, Kotlin, etc.)
  2. *Data Science & Machine Learning* (PyTorch, TensorFlow, Scikit-Learn, Pandas, NumPy, etc.)
  3. *Generative AI & LLMs* (LangChain, LlamaIndex, RAG, Transformers, Vector DBs, Prompt Engineering)
  4. *Data Engineering & Big Data* (Spark, Kafka, dbt, Snowflake, Airflow, Hadoop, Databricks)
  5. *Cloud, DevOps & SRE* (AWS, GCP, Azure, Docker, Kubernetes, Terraform, Prometheus, CI/CD)
  6. *Cybersecurity & Networking* (SIEM, Penetration Testing, SOC Analysis, OWASP, Wireshark)
  7. *Web & Mobile Engineering* (React, Next.js, Node.js, FastAPI, Django, Flutter, React Native)
- **Fuzzy & Multi-Word Alias Normalization**: Resolves variations into canonical IDs (e.g., `k8s` $\to$ `kubernetes`, `sklearn` $\to$ `scikit_learn`, `postgres` $\to$ `postgresql`, `dax` $\to$ `power_bi`).

---

## 4. 🧭 26 Modern Tech Career Target Roles
Supports comprehensive career path evaluations across 26 high-demand tech roles:
- **Data & AI Track**: Data Analyst, Data Scientist, Machine Learning Engineer, AI Research Scientist, GenAI / LLM Engineer, Data Engineer, BI Developer.
- **Software Engineering Track**: Frontend Developer, Backend Software Engineer, Full Stack Engineer, Cloud Architect, DevOps Engineer, Site Reliability Engineer (SRE).
- **Mobile & Specialized Track**: Mobile App Developer (iOS/Android), Cybersecurity Analyst, Penetration Tester, QA Automation Engineer, Product Manager, Technical Scrum Master, and more.

---

## 5. 💼 Multi-Factor Job Compatibility Matcher
- Matches candidate profiles across a dataset of **3,500+ tech job openings**.
- **Hybrid Matching Metric**:
  - `50% Skill Match` (Core & secondary skill overlap)
  - `25% NLP Semantic Similarity` (TF-IDF Cosine similarity)
  - `15% Experience Proximity` (Tenure fit)
  - `10% Education Fit` (Degree alignment)
- Displays transparent match percentage badges, company name, location, salary bracket, required vs matched skills, and direct application links.

---

## 6. 🔍 Granular Skill Gap Decomposition
Deconstructs a candidate's skills against any selected target role into three actionable tiers:
1. **Mastered Competencies (Green)**: Verified matching skills.
2. **In-Progress / Adjacent Skills (Amber)**: Related skills that can be quickly leveled up.
3. **Critical Missing Gaps (Red)**: High-priority missing skills that hiring managers filter for.

---

## 7. 🗺️ Dynamic 4-Phase Prerequisite-Aware Roadmap
Generates a customized, step-by-step learning pathway:
- **Phase 1: Foundations & Core Tooling** (~2 weeks)
- **Phase 2: Core Engineering & Frameworks** (~2-3 weeks)
- **Phase 3: Advanced Architectures & Productionization** (~2-3 weeks)
- **Phase 4: Capstone Portfolio Projects & Interview Prep** (~2 weeks)
- **Curated Deliverables**: Estimated study hours, direct links to official documentation and tutorials, portfolio milestone projects, and interview questions.

---

## 8. 💰 Predictive Compensation Modeling (LPA)
- Evaluates candidate tenure, target role, skill volume, and education to forecast competitive market compensation in **₹ Lakhs Per Annum (LPA)**.
- Provides median estimates, realistic min/max ranges, and experience percentile comparisons based on 5,000+ benchmark records.

---

## 9. 🚀 Live "What-If" Career Trajectory Simulator
- Allows candidates to interactively simulate adding new skills (e.g. Docker, PyTorch, AWS), adding +1 to +5 years of experience, or upgrading their degree.
- **Real-Time Delta Outputs**:
  - Role Readiness jump (e.g. `+18%`)
  - Projected Market Salary growth (e.g. `+₹3.2L/yr`)
  - Number of newly unlocked high-match job postings.

---

## 10. 📑 Executive PDF Career Report & Market Intelligence
- **ReportLab PDF Exporter**: Compiles an executive evaluation PDF including ATS scores, skill gap breakdown, learning roadmap curriculum, and matched opportunities.
- **Market Intelligence View**: Visualizes macro hiring trends, top 10 in-demand skills by role, geographic hiring hubs (Bengaluru, Hyderabad, Pune, etc.), and top hiring employers using Plotly charts.
