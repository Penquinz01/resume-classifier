"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from pydantic import BaseModel, Field


# --- Resume Upload ---

class ResumeUploadResponse(BaseModel):
    """Response after uploading a resume file."""
    analysis_id: str
    filename: str
    status: str = "uploaded"
    message: str = "Resume uploaded successfully"


# --- Classification ---

class ClassificationScore(BaseModel):
    """Probability score for a single category."""
    category: str
    probability: float


class ClassificationResult(BaseModel):
    """Full classification result for a resume."""
    analysis_id: str
    predicted_role: str
    confidence: float = Field(ge=0, le=1)
    all_scores: list[ClassificationScore]
    detected_skills: list["SkillItem"]
    missing_skills: list["SkillItem"]
    career_suggestions: "CareerSuggestions"


# --- Skills ---

class SkillItem(BaseModel):
    """A single skill with its category."""
    name: str
    category: str  # language, framework, database, cloud, tool


class SkillsResult(BaseModel):
    """Categorized skills from a resume."""
    detected: list[SkillItem]
    missing: list[SkillItem]
    languages: list[str]
    frameworks: list[str]
    databases: list[str]
    cloud: list[str]
    tools: list[str]


# --- Career Suggestions ---

class CareerSuggestions(BaseModel):
    """Career improvement recommendations."""
    missing_skills: list[str]
    recommended_technologies: list[str]
    learning_suggestions: list[str]
    career_roadmap: list[str]


# --- ATS ---

class ATSScoreRequest(BaseModel):
    """Request body for ATS scoring."""
    analysis_id: str
    job_description: str = Field(min_length=10)


class ATSScoreResponse(BaseModel):
    """ATS match analysis result."""
    analysis_id: str
    match_percentage: float = Field(ge=0, le=100)
    matching_keywords: list[str]
    missing_keywords: list[str]
    suggestions: list[str]


# --- History ---

class AnalysisHistoryItem(BaseModel):
    """Summary of a past analysis for the history list."""
    id: str
    filename: str
    predicted_role: str | None
    confidence: float | None
    score: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisHistoryResponse(BaseModel):
    """List of past analyses."""
    analyses: list[AnalysisHistoryItem]
    total: int


# --- Full Analysis Detail ---

class AnalysisDetail(BaseModel):
    """Complete analysis detail for a single resume."""
    id: str
    filename: str
    predicted_role: str | None
    confidence: float | None
    score: float | None
    all_scores: list[ClassificationScore]
    detected_skills: list[SkillItem]
    missing_skills: list[SkillItem]
    career_suggestions: CareerSuggestions
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Error ---

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    status_code: int = 400
