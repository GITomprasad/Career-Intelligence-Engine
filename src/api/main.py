"""
FastAPI REST Application for Career Intelligence Engine.
Provides HTTP API endpoints for resume parsing, job matching, gap analysis, salary prediction, and career simulation.
"""

from typing import Dict, Any, List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.nlp.parser import ResumeParser
from src.models.matcher import JobMatcher
from src.models.role_classifier import RoleClassifier
from src.models.salary_predictor import SalaryPredictor
from src.engine.gap_analyzer import SkillGapAnalyzer
from src.engine.roadmap_generator import RoadmapGenerator
from src.engine.explainability import ExplainabilityEngine
from src.engine.simulator import CareerSimulator
from src.engine.market_analyzer import MarketAnalyzer
from src.report.pdf_generator import CareerReportGenerator
from src.api.schemas import (
    TextParseRequest,
    CandidateProfileSchema,
    JobMatchRequest,
    GapAnalysisRequest,
    SalaryPredictRequest,
    SimulationRequest,
    RoadmapRequest
)

app = FastAPI(
    title="Career Intelligence Engine API",
    description="AI-Powered Career Recommendation, Skill Gap Analysis, Salary Prediction & Job Matching API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
parser = ResumeParser()
matcher = JobMatcher()
role_classifier = RoleClassifier()
salary_predictor = SalaryPredictor()
gap_analyzer = SkillGapAnalyzer()
roadmap_generator = RoadmapGenerator()
explainability_engine = ExplainabilityEngine()
simulator = CareerSimulator()
market_analyzer = MarketAnalyzer()
pdf_generator = CareerReportGenerator()


@app.get("/api/health", tags=["System"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Career Intelligence Engine API",
        "version": "1.0.0"
    }


@app.post("/api/resume/parse-file", tags=["Resume NLP"])
async def parse_resume_file(file: UploadFile = File(...)):
    """
    Upload and parse a PDF or TXT resume file.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
    result = parser.parse(contents, filename=file.filename)
    if not result.get("success"):
        raise HTTPException(status_code=422, detail=result.get("error", "Failed to parse resume."))
        
    # Also attach initial role recommendations
    profile = result["profile"]
    recommended_roles = role_classifier.predict_roles(profile.get("skill_ids", []), top_n=5)
    result["recommended_roles"] = recommended_roles
    return result


@app.post("/api/resume/parse-text", tags=["Resume NLP"])
def parse_resume_text(req: TextParseRequest):
    """
    Parse resume from raw plain text.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be empty.")
        
    result = parser.parse(req.text, filename=req.filename or "resume.txt")
    if not result.get("success"):
        raise HTTPException(status_code=422, detail=result.get("error", "Failed to parse text."))
        
    profile = result["profile"]
    recommended_roles = role_classifier.predict_roles(profile.get("skill_ids", []), top_n=5)
    result["recommended_roles"] = recommended_roles
    return result


@app.post("/api/match/jobs", tags=["Matching Engine"])
def match_jobs(req: JobMatchRequest):
    """
    Match candidate profile against jobs database using hybrid multi-factor scoring.
    """
    profile_dict = req.profile.model_dump()
    matches = matcher.match_jobs(
        candidate_profile=profile_dict,
        target_role_id=req.target_role_id,
        top_n=req.top_n,
        min_score=req.min_score
    )
    return {
        "total_matches": len(matches),
        "target_role_filter": req.target_role_id or "All Roles",
        "matches": matches
    }


@app.post("/api/skills/gap-analysis", tags=["Skill Gap"])
def analyze_skill_gap(req: GapAnalysisRequest):
    """
    Evaluate candidate skills against target role benchmarks to identify strong, improvement, and missing skills.
    """
    gap_result = gap_analyzer.analyze_gap(req.skills, req.target_role_id)
    if "error" in gap_result:
        raise HTTPException(status_code=404, detail=gap_result["error"])
    return gap_result


@app.post("/api/salary/predict", tags=["Salary Prediction"])
def predict_salary(req: SalaryPredictRequest):
    """
    Predict market salary range based on role, experience, skill count, and education.
    """
    pred = salary_predictor.predict_salary(
        role_id=req.role_id,
        experience_years=req.experience_years,
        skill_count=req.skill_count,
        education=req.education,
        location_tier=req.location_tier,
        company_tier=req.company_tier
    )
    return pred


@app.post("/api/roadmap/generate", tags=["Learning Roadmap"])
def generate_roadmap(req: RoadmapRequest):
    """
    Generate dynamic phased learning roadmap from gap analysis results.
    """
    roadmap = roadmap_generator.generate_roadmap(req.gap_analysis)
    return roadmap


@app.post("/api/simulator/what-if", tags=["Simulator & What-If"])
def simulate_career_trajectory(req: SimulationRequest):
    """
    Simulate career readiness and salary bump when adding skills or experience.
    """
    profile_dict = req.current_profile.model_dump()
    sim_result = simulator.simulate(
        current_profile=profile_dict,
        target_role_id=req.target_role_id,
        additional_skills=req.additional_skills,
        additional_experience_years=req.additional_experience_years,
        simulated_education=req.simulated_education
    )
    return sim_result


@app.get("/api/market/trends", tags=["Market Intelligence"])
def get_market_trends(role_id: Optional[str] = Query(None, description="Optional role filter")):
    """
    Retrieve macro job market trends, top in-demand skills, and salary distributions.
    """
    top_skills = market_analyzer.get_top_skills_by_role(role_id=role_id, top_n=15)
    salary_dist = market_analyzer.get_salary_by_role_distribution()
    overview = market_analyzer.get_market_overview()
    
    return {
        "overview": overview,
        "top_demanded_skills": top_skills,
        "salary_by_role": salary_dist
    }


@app.post("/api/report/download", tags=["PDF Reporting"])
def download_pdf_report(
    profile: CandidateProfileSchema,
    target_role_id: str = "data_scientist"
):
    """
    Generates and returns downloadable evaluation report PDF.
    """
    profile_dict = profile.model_dump()
    gap_result = gap_analyzer.analyze_gap(profile_dict.get("skill_ids", []), target_role_id)
    salary_info = salary_predictor.predict_salary(
        role_id=target_role_id,
        experience_years=profile_dict.get("experience_years", 0.0),
        skill_count=len(profile_dict.get("skill_ids", []))
    )
    roadmap = roadmap_generator.generate_roadmap(gap_result)
    top_jobs = matcher.match_jobs(profile_dict, target_role_id=target_role_id, top_n=5)
    
    pdf_bytes = pdf_generator.generate_report(
        candidate_profile=profile_dict,
        target_role=target_role_id,
        gap_analysis=gap_result,
        salary_info=salary_info,
        roadmap=roadmap,
        top_jobs=top_jobs
    )
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Career_Report_{profile.name.replace(' ', '_')}.pdf"}
    )
