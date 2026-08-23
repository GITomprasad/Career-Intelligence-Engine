"""
Dynamic Learning Roadmap Generator.
Builds a phased, prerequisite-aware learning curriculum for closing skill gaps.
"""

from typing import Dict, List, Any
from src.nlp.skill_extractor import SkillExtractor


class RoadmapGenerator:
    def __init__(self, ontology_path: str = None):
        self.extractor = SkillExtractor(ontology_path)
        
        # Knowledge Base of Learning Resources and Milestones
        self.skill_curriculum = {
            "python": {
                "category": "Foundations",
                "hours": 20,
                "resources": [
                    {"name": "Python for Everybody (University of Michigan)", "type": "Course", "url": "https://www.py4e.com/"},
                    {"name": "Official Python 3 Documentation & Tutorial", "type": "Docs", "url": "https://docs.python.org/3/tutorial/"},
                    {"name": "Real Python Tutorials", "type": "Interactive", "url": "https://realpython.com/"}
                ],
                "milestone_project": "Build an object-oriented CLI application with error handling and unit tests.",
                "interview_focus": "Data types, list comprehensions, decorators, generators, and memory management."
            },
            "sql": {
                "category": "Foundations",
                "hours": 15,
                "resources": [
                    {"name": "Mode Analytics Interactive SQL Tutorial", "type": "Interactive", "url": "https://mode.com/sql-tutorial/"},
                    {"name": "SQLZoo Interactive Practice", "type": "Exercises", "url": "https://sqlzoo.net/"},
                    {"name": "PostgreSQL Official Documentation", "type": "Docs", "url": "https://www.postgresql.org/docs/"}
                ],
                "milestone_project": "Design a relational schema with window functions, CTEs, and indexed query optimizations.",
                "interview_focus": "Window functions (ROW_NUMBER, RANK), self-joins, indexing, and query optimization."
            },
            "machine_learning": {
                "category": "Core Engineering",
                "hours": 35,
                "resources": [
                    {"name": "Machine Learning Specialization (Andrew Ng)", "type": "Course", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
                    {"name": "Scikit-Learn User Guide", "type": "Docs", "url": "https://scikit-learn.org/stable/user_guide.html"},
                    {"name": "Kaggle Machine Learning Competitions", "type": "Practice", "url": "https://www.kaggle.com/learn"}
                ],
                "milestone_project": "Build a cross-validated multi-model benchmark pipeline with hyperparameter tuning.",
                "interview_focus": "Bias-variance tradeoff, regularization (L1/L2), evaluation metrics (ROC-AUC, F1), and tree ensembles."
            },
            "deep_learning": {
                "category": "Core Engineering",
                "hours": 40,
                "resources": [
                    {"name": "Deep Learning Specialization (DeepLearning.AI)", "type": "Course", "url": "https://www.deeplearning.ai/"},
                    {"name": "PyTorch 60-Minute Blitz", "type": "Tutorial", "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html"}
                ],
                "milestone_project": "Train and fine-tune a convolutional neural network with data augmentation and early stopping.",
                "interview_focus": "Backpropagation, gradient descent optimizers (Adam, SGD), vanishing gradients, and dropout."
            },
            "nlp": {
                "category": "Specialized",
                "hours": 30,
                "resources": [
                    {"name": "Hugging Face NLP Course", "type": "Interactive", "url": "https://huggingface.co/learn/nlp-course"},
                    {"name": "SpaCy 101 Guide", "type": "Docs", "url": "https://spacy.io/usage/spacy-101"}
                ],
                "milestone_project": "Develop a semantic search engine or text classifier with BERT embeddings.",
                "interview_focus": "Tokenization, self-attention mechanism, transformer architectures, and embedding similarity."
            },
            "llms": {
                "category": "Specialized",
                "hours": 25,
                "resources": [
                    {"name": "LangChain & LlamaIndex Official Guides", "type": "Docs", "url": "https://python.langchain.com/"},
                    {"name": "DeepLearning.AI Generative AI with LLMs", "type": "Course", "url": "https://www.deeplearning.ai/courses/generative-ai-with-llms/"}
                ],
                "milestone_project": "Build an end-to-end RAG application with vector database indexing and chunking strategies.",
                "interview_focus": "RAG architecture, vector embeddings, context window limits, prompt engineering, and evaluation."
            },
            "docker": {
                "category": "Production & DevOps",
                "hours": 15,
                "resources": [
                    {"name": "Docker Official Getting Started Guide", "type": "Docs", "url": "https://docs.docker.com/get-started/"},
                    {"name": "Docker for Data Science (FreeCodeCamp)", "type": "Tutorial", "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo"}
                ],
                "milestone_project": "Containerize a full ML inference service with multi-stage builds and Docker Compose.",
                "interview_focus": "Images vs containers, volume mounting, layer caching, and multi-stage builds."
            },
            "kubernetes": {
                "category": "Production & DevOps",
                "hours": 25,
                "resources": [
                    {"name": "Kubernetes Official Basics Tutorial", "type": "Interactive", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/"},
                    {"name": "TechWorld with Nana Kubernetes Course", "type": "Video", "url": "https://www.youtube.com/watch?v=X48VuDVv0do"}
                ],
                "milestone_project": "Deploy a containerized API to local Minikube cluster with ReplicaSets and Ingress routing.",
                "interview_focus": "Pods, Deployments, Services, ConfigMaps, and horizontal pod autoscaling (HPA)."
            },
            "aws": {
                "category": "Production & DevOps",
                "hours": 30,
                "resources": [
                    {"name": "AWS Skill Builder Free Cloud Practitioner / Architect Modules", "type": "Course", "url": "https://explore.skillbuilder.aws/"},
                    {"name": "AWS Documentation: S3, EC2, Lambda & SageMaker", "type": "Docs", "url": "https://docs.aws.amazon.com/"}
                ],
                "milestone_project": "Deploy an automated serverless ML inference pipeline on AWS Lambda and S3.",
                "interview_focus": "IAM permissions, S3 lifecycle, EC2 sizing, Lambda cold starts, and CloudWatch monitoring."
            },
            "mlops": {
                "category": "Production & DevOps",
                "hours": 25,
                "resources": [
                    {"name": "MLOps Specialization by Andrew Ng", "type": "Course", "url": "https://www.deeplearning.ai/courses/machine-learning-engineering-for-production-mlops/"},
                    {"name": "MLflow Official Documentation", "type": "Docs", "url": "https://mlflow.org/docs/latest/index.html"}
                ],
                "milestone_project": "Set up experiment tracking, model versioning, registry, and drift detection with MLflow.",
                "interview_focus": "Data drift vs concept drift, CI/CD for ML, artifact stores, and model rollback strategies."
            },
            "power_bi": {
                "category": "Analytics",
                "hours": 20,
                "resources": [
                    {"name": "Microsoft Learn Power BI Data Analyst Path", "type": "Interactive", "url": "https://learn.microsoft.com/en-us/training/paths/data-analytics-microsoft/"},
                    {"name": "Guy in a Cube YouTube Channel", "type": "Video", "url": "https://guyinacube.com/"}
                ],
                "milestone_project": "Build an executive sales & customer churn dashboard with complex DAX measures.",
                "interview_focus": "DAX CALCULATE, STAR schema data modeling, relationship directions, and row-level security."
            },
            "tableau": {
                "category": "Analytics",
                "hours": 20,
                "resources": [
                    {"name": "Tableau Free Training Videos", "type": "Video", "url": "https://www.tableau.com/learn/training"},
                    {"name": "Tableau Public Community Projects", "type": "Portfolio", "url": "https://public.tableau.com/"}
                ],
                "milestone_project": "Publish a multi-story dashboard on Tableau Public with parameters and LOD expressions.",
                "interview_focus": "Level of Detail (LOD) calculations, table calculations, blending vs joins."
            },
            "apache_spark": {
                "category": "Engineering",
                "hours": 25,
                "resources": [
                    {"name": "Databricks PySpark Free Learning Path", "type": "Course", "url": "https://www.databricks.com/learn/training/home"},
                    {"name": "Apache Spark Official Quick Start", "type": "Docs", "url": "https://spark.apache.org/docs/latest/quick-start.html"}
                ],
                "milestone_project": "Process 10GB+ semi-structured clickstream logs using PySpark DataFrames and partition pruning.",
                "interview_focus": "Lazy evaluation, RDD vs DataFrame, DAG execution, wide vs narrow transformations, and shuffling."
            },
            "apache_airflow": {
                "category": "Engineering",
                "hours": 20,
                "resources": [
                    {"name": "Astronomer Airflow Academy", "type": "Interactive", "url": "https://academy.astronomer.io/"},
                    {"name": "Apache Airflow Official Tutorial", "type": "Docs", "url": "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html"}
                ],
                "milestone_project": "Author a resilient DAG scheduled daily with custom operators, XComs, and Slack alerting.",
                "interview_focus": "DAG scheduling, idempotency, backfilling, operators vs sensors, and task execution lifecycle."
            },
            "react": {
                "category": "Frontend & Web",
                "hours": 25,
                "resources": [
                    {"name": "React.dev Official Interactive Tutorial", "type": "Interactive", "url": "https://react.dev/"},
                    {"name": "Next.js Full App Router Course", "type": "Docs", "url": "https://nextjs.org/learn"}
                ],
                "milestone_project": "Build an interactive, server-side rendered dashboard with state management and custom hooks.",
                "interview_focus": "Virtual DOM, React reconciliation, useEffect dependency array, custom hooks, and server components."
            },
            "typescript": {
                "category": "Frontend & Web",
                "hours": 15,
                "resources": [
                    {"name": "TypeScript Handbook (Microsoft)", "type": "Docs", "url": "https://www.typescriptlang.org/docs/handbook/intro.html"},
                    {"name": "Total TypeScript by Matt Pocock", "type": "Interactive", "url": "https://www.totaltypescript.com/"}
                ],
                "milestone_project": "Refactor a vanilla JS codebase into strict, type-safe generic interfaces and union types.",
                "interview_focus": "Generics, utility types (Partial, Record), type narrowing, discrimination unions, and interface vs type."
            },
            "fastapi": {
                "category": "Backend Engineering",
                "hours": 15,
                "resources": [
                    {"name": "FastAPI Official Documentation", "type": "Docs", "url": "https://fastapi.tiangolo.com/"},
                    {"name": "TestDriven.io FastAPI Guide", "type": "Tutorial", "url": "https://testdriven.io/"}
                ],
                "milestone_project": "Create an async REST API with Pydantic validation, dependency injection, and JWT auth.",
                "interview_focus": "Async/await concurrency, Pydantic serialization, dependency injection, and background tasks."
            },
            "dbt": {
                "category": "Data Engineering & Analytics",
                "hours": 15,
                "resources": [
                    {"name": "dbt Learn Official Fundamentals", "type": "Course", "url": "https://learn.getdbt.com/"},
                    {"name": "dbt Best Practices Guide", "type": "Docs", "url": "https://docs.getdbt.com/guides/best-practices"}
                ],
                "milestone_project": "Build a multi-layer staging and marts dimensional data model with automated testing.",
                "interview_focus": "Modular SQL modeling, Jinja templating, schema testing, and incremental materializations."
            },
            "snowflake": {
                "category": "Data Engineering & Analytics",
                "hours": 15,
                "resources": [
                    {"name": "Snowflake Hands-on Essentials", "type": "Docs", "url": "https://quickstarts.snowflake.com/"},
                    {"name": "Snowflake Architecture Deep Dive", "type": "Docs", "url": "https://docs.snowflake.com/"}
                ],
                "milestone_project": "Configure role-based access, virtual warehouse sizing, and zero-copy clones for analytics.",
                "interview_focus": "Multi-cluster architecture, micro-partitions, time travel, and external stages."
            },
            "cybersecurity": {
                "category": "Security & Infrastructure",
                "hours": 30,
                "resources": [
                    {"name": "OWASP Top 10 Security Guide", "type": "Docs", "url": "https://owasp.org/www-project-top-ten/"},
                    {"name": "TryHackMe Security Fundamentals", "type": "Interactive", "url": "https://tryhackme.com/"}
                ],
                "milestone_project": "Conduct an end-to-end vulnerability assessment and harden cloud infrastructure with IAM policies.",
                "interview_focus": "Threat modeling, cryptography (symmetric vs asymmetric), PKI, zero trust architecture, and OWASP vulnerabilities."
            },
            "flutter": {
                "category": "Mobile Development",
                "hours": 25,
                "resources": [
                    {"name": "Flutter Official Getting Started", "type": "Docs", "url": "https://docs.flutter.dev/"},
                    {"name": "Flutter & Dart Apprentice", "type": "Tutorial", "url": "https://flutter.dev/learn"}
                ],
                "milestone_project": "Develop a cross-platform mobile app with state management (Bloc/Provider) and offline local caching.",
                "interview_focus": "Widget tree rendering, stateful vs stateless widgets, streams, and async isolates."
            },
            "qa_automation": {
                "category": "Quality Assurance & SDET",
                "hours": 20,
                "resources": [
                    {"name": "Playwright Official Automation Guide", "type": "Docs", "url": "https://playwright.dev/"},
                    {"name": "Pytest Full Testing Framework Tutorial", "type": "Docs", "url": "https://docs.pytest.org/"}
                ],
                "milestone_project": "Implement an automated CI test suite covering unit, API integration, and headless browser E2E tests.",
                "interview_focus": "Page Object Model (POM), fixture scopes, headless test parallelization, and mock fixtures."
            },
            "monitoring_observability": {
                "category": "DevOps & SRE",
                "hours": 20,
                "resources": [
                    {"name": "Prometheus & Grafana Official Labs", "type": "Docs", "url": "https://prometheus.io/docs/introduction/overview/"},
                    {"name": "Google SRE Workbook: Monitoring Distributed Systems", "type": "Book", "url": "https://sre.google/sre-book/monitoring-distributed-systems/"}
                ],
                "milestone_project": "Set up a Prometheus metrics exporter with Grafana alerting dashboards for service SLO tracking.",
                "interview_focus": "SLIs vs SLOs vs SLAs, Golden Signals (Latency, Traffic, Errors, Saturation), and alert routing."
            },
            "system_design": {
                "category": "Architecture & Engineering",
                "hours": 30,
                "resources": [
                    {"name": "System Design Primer by Donne Martin", "type": "Interactive", "url": "https://github.com/donnemartin/system-design-primer"},
                    {"name": "Designing Data-Intensive Applications (Martin Kleppmann)", "type": "Book", "url": "https://dataintensive.net/"}
                ],
                "milestone_project": "Design a high-throughput, distributed rate-limiting and URL shortener architecture blueprint.",
                "interview_focus": "CAP theorem, horizontal vs vertical scaling, load balancing, caching strategies (Write-Through/Write-Back), and database sharding."
            }
        }

    def generate_roadmap(self, gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a 4-phase structured learning roadmap for closing identified skill gaps.
        """
        missing_skills = gap_analysis.get("missing_skills", [])
        improvement_skills = gap_analysis.get("improvement_skills", [])
        target_role = gap_analysis.get("role_title", "Target Role")
        
        all_gap_items = missing_skills + improvement_skills
        if not all_gap_items:
            return {
                "status": "All Core Skills Mastered",
                "message": f"Congratulations! You already meet the core skill requirements for {target_role}.",
                "total_estimated_weeks": 2,
                "phases": []
            }

        # Distribute into 4 logical progressive phases
        phase1_items = [] # Foundations (Python, SQL, Statistics, Excel, Basics)
        phase2_items = [] # Core ML / Analytics / Deep Domain
        phase3_items = [] # Engineering / Cloud / DevOps / Scaling
        phase4_items = [] # Capstone, Integration & Production

        for item in all_gap_items:
            s_id = item["skill_id"]
            s_name = item["name"]
            curriculum = self.skill_curriculum.get(s_id, {
                "category": "Domain Specialization",
                "hours": 15,
                "resources": [
                    {"name": f"Official {s_name} Documentation", "type": "Docs", "url": f"https://www.google.com/search?q={s_name}+documentation"}
                ],
                "milestone_project": f"Build a practical hands-on project applying {s_name}.",
                "interview_focus": f"Core concepts, performance trade-offs, and best practices in {s_name}."
            })

            enriched_item = {
                "skill_id": s_id,
                "name": s_name,
                "status": item.get("status", "Missing"),
                "priority": item.get("priority", "Medium Priority"),
                "category": item.get("category", "General"),
                "estimated_hours": curriculum["hours"],
                "resources": curriculum["resources"],
                "milestone_project": curriculum["milestone_project"],
                "interview_focus": curriculum["interview_focus"]
            }

            cat_lower = curriculum["category"].lower()
            if "foundation" in cat_lower or s_id in ["python", "sql", "statistics", "excel"]:
                phase1_items.append(enriched_item)
            elif "core" in cat_lower or "analytics" in cat_lower or s_id in ["machine_learning", "pandas", "power_bi", "tableau"]:
                phase2_items.append(enriched_item)
            elif "devops" in cat_lower or "production" in cat_lower or "engineering" in cat_lower or s_id in ["docker", "aws", "kubernetes", "mlops", "apache_spark", "apache_airflow"]:
                phase3_items.append(enriched_item)
            else:
                phase2_items.append(enriched_item)

        # Build Phase structure
        phases = []
        
        if phase1_items:
            phases.append({
                "phase_number": 1,
                "title": "Phase 1: Foundations & Core Tooling",
                "duration_weeks": max(2, len(phase1_items) * 1),
                "goal": "Solidify programming, data manipulation, and database query fundamentals.",
                "skills": phase1_items
            })
            
        if phase2_items:
            phases.append({
                "phase_number": 2,
                "title": "Phase 2: Domain Competencies & Modeling",
                "duration_weeks": max(3, len(phase2_items) * 1),
                "goal": f"Master the core algorithms, analytics techniques, and tools needed for {target_role}.",
                "skills": phase2_items
            })
            
        if phase3_items:
            phases.append({
                "phase_number": 3,
                "title": "Phase 3: Production Engineering & Cloud/DevOps",
                "duration_weeks": max(3, len(phase3_items) * 1),
                "goal": "Containerize, deploy, and scale data pipelines and machine learning workloads.",
                "skills": phase3_items
            })

        # Always add Phase 4 Capstone & Interview Preparation
        phases.append({
            "phase_number": len(phases) + 1,
            "title": f"Phase {len(phases) + 1}: End-to-End Capstone Project & Portfolio",
            "duration_weeks": 2,
            "goal": f"Build a standout full-stack {target_role} portfolio project with interactive UI and GitHub repository.",
            "skills": [
                {
                    "skill_id": "portfolio_capstone",
                    "name": f"{target_role} Production Capstone Project",
                    "status": "Target Milestone",
                    "priority": "Critical Priority",
                    "estimated_hours": 30,
                    "resources": [
                        {"name": "GitHub Portfolio Showcase Guide", "type": "Guide", "url": "https://github.com"}
                    ],
                    "milestone_project": f"Create an end-to-end {target_role} pipeline with automated tests, Docker, and live deployment.",
                    "interview_focus": "System architecture walkthrough, trade-off decisions, and live technical demonstration."
                }
            ]
        })

        total_weeks = sum(p["duration_weeks"] for p in phases)

        return {
            "target_role": target_role,
            "current_readiness": gap_analysis.get("readiness_score", 0.0),
            "projected_readiness_after_completion": 96.0,
            "total_estimated_weeks": total_weeks,
            "phases_count": len(phases),
            "phases": phases
        }
