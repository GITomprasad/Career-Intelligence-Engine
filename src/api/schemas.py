"""
Pydantic Data Schemas for REST API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TextParseRequest(BaseModel):
    text: str = Field(..., description="Raw resume text")
    filename: Optional[str] = Field("resume.txt", description="Optional filename")


class CandidateProfileSchema(BaseModel):
    name: str = "Candidate"
    email: str = "Not Provided"
    phone: str = "Not Provided"
    location: str = "Not Specified"
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    education: Dict[str, Any] = Field(default_factory=dict)
    skills: List[str] = Field(default_factory=list)
    skill_ids: List[str] = Field(default_factory=list)
    skills_by_category: Dict[str, List[str]] = Field(default_factory=dict)
    skills_count: int = 0
    experience_years: float = 0.0
    seniority_level: str = "Fresher / Entry Level"
    experience_bracket: str = "0-1 yrs"
    action_verb_score: float = 0.0
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    summary: str = ""
    raw_text: Optional[str] = ""


class JobMatchRequest(BaseModel):
    profile: CandidateProfileSchema
    target_role_id: Optional[str] = Field(None, description="Optional role filter (e.g. 'data_scientist')")
    top_n: int = Field(15, ge=1, le=50)
    min_score: float = Field(30.0, ge=0.0, le=100.0)


class GapAnalysisRequest(BaseModel):
    skills: List[str] = Field(..., description="List of candidate skills or skill_ids")
    target_role_id: str = Field(..., description="Target role ID (e.g. 'data_scientist')")


class SalaryPredictRequest(BaseModel):
    role_id: str
    experience_years: float = Field(0.0, ge=0.0, le=40.0)
    skill_count: int = Field(5, ge=1, le=50)
    education: str = "B.Tech / B.E. Computer Science"
    location_tier: str = "Tier-1"
    company_tier: str = "Tier-1"


class SimulationRequest(BaseModel):
    current_profile: CandidateProfileSchema
    target_role_id: str
    additional_skills: List[str] = Field(default_factory=list)
    additional_experience_years: float = Field(0.0, ge=0.0, le=10.0)
    simulated_education: Optional[str] = None


class RoadmapRequest(BaseModel):
    gap_analysis: Dict[str, Any]
