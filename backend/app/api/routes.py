"""
FastAPI API routes for resume classification, skill extraction,
ATS scoring, and analysis history.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.config import settings
from app.core.database import get_db
from app.models.analysis import ResumeAnalysis
from app.models.skill import SkillResult
from app.schemas.resume import (
    ResumeUploadResponse,
    ClassificationResult,
    ClassificationScore,
    SkillItem,
    CareerSuggestions,
    ATSScoreRequest,
    ATSScoreResponse,
    AnalysisHistoryItem,
    AnalysisHistoryResponse,
    AnalysisDetail,
)
from app.services.resume_parser import parse_resume
from app.services.skill_extractor import extract_skills, get_missing_skills
from app.services.career_advisor import generate_career_suggestions
from app.services.ats_scorer import calculate_ats_score
from ml.inference.predictor import get_predictor

router = APIRouter(prefix="/api", tags=["resume"])


@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a resume file (PDF or DOCX) and extract text."""
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Use PDF or DOCX.",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    # Parse resume text
    try:
        raw_text = parse_resume(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {str(e)}",
        )

    if not raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from the uploaded file.",
        )

    # Create analysis record
    analysis = ResumeAnalysis(
        id=str(uuid.uuid4()),
        filename=file.filename,
        raw_text=raw_text,
    )
    db.add(analysis)
    await db.flush()

    return ResumeUploadResponse(
        analysis_id=analysis.id,
        filename=file.filename,
        status="uploaded",
        message="Resume uploaded and parsed successfully.",
    )


@router.post("/resume/classify", response_model=ClassificationResult)
async def classify_resume(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Classify a previously uploaded resume and extract skills."""
    # Fetch analysis
    result = await db.execute(
        select(ResumeAnalysis).where(ResumeAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if not analysis.raw_text:
        raise HTTPException(
            status_code=400,
            detail="No resume text found. Please upload a resume first.",
        )

    # --- ML Classification ---
    predictor = get_predictor(settings.MODEL_PATH)
    prediction = predictor.predict(analysis.raw_text)

    # --- Skill Extraction ---
    detected_skills_dict = extract_skills(analysis.raw_text)
    missing_skills_list = get_missing_skills(detected_skills_dict, prediction.predicted_role)

    # --- Career Suggestions ---
    career = generate_career_suggestions(
        prediction.predicted_role,
        detected_skills_dict,
        missing_skills_list,
    )

    # --- Calculate overall score (0-100) ---
    # Weighted: confidence (40%) + skills match (30%) + skills breadth (30%)
    total_detected = sum(len(v) for v in detected_skills_dict.values())
    total_missing = len(missing_skills_list)
    skills_ratio = (
        total_detected / (total_detected + total_missing)
        if (total_detected + total_missing) > 0
        else 0
    )
    breadth_score = min(total_detected / 15, 1.0)  # Cap at 15 skills

    overall_score = round(
        (prediction.confidence * 40 + skills_ratio * 30 + breadth_score * 30),
        1,
    )

    # --- Update analysis record ---
    analysis.predicted_role = prediction.predicted_role
    analysis.confidence = prediction.confidence
    analysis.score = overall_score

    # --- Save detected skills ---
    for category, skills in detected_skills_dict.items():
        for skill_name in skills:
            db.add(SkillResult(
                id=str(uuid.uuid4()),
                analysis_id=analysis.id,
                skill_name=skill_name,
                skill_type="detected",
                category=category,
            ))

    # --- Save missing skills ---
    for skill_info in missing_skills_list:
        db.add(SkillResult(
            id=str(uuid.uuid4()),
            analysis_id=analysis.id,
            skill_name=skill_info["name"],
            skill_type="missing",
            category=skill_info["category"],
        ))

    await db.flush()

    # --- Build response ---
    all_scores = [
        ClassificationScore(category=cat, probability=prob)
        for cat, prob in prediction.all_probabilities.items()
    ]

    detected_items = [
        SkillItem(name=skill, category=cat)
        for cat, skills in detected_skills_dict.items()
        for skill in skills
    ]

    missing_items = [
        SkillItem(name=s["name"], category=s["category"])
        for s in missing_skills_list
    ]

    return ClassificationResult(
        analysis_id=analysis.id,
        predicted_role=prediction.predicted_role,
        confidence=prediction.confidence,
        all_scores=all_scores,
        detected_skills=detected_items,
        missing_skills=missing_items,
        career_suggestions=CareerSuggestions(**career),
    )


@router.post("/resume/ats", response_model=ATSScoreResponse)
async def ats_score(
    request: ATSScoreRequest,
    db: AsyncSession = Depends(get_db),
):
    """Calculate ATS match score for a resume against a job description."""
    # Fetch analysis
    result = await db.execute(
        select(ResumeAnalysis).where(ResumeAnalysis.id == request.analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if not analysis.raw_text:
        raise HTTPException(
            status_code=400,
            detail="No resume text found.",
        )

    # Calculate ATS score
    ats_result = calculate_ats_score(analysis.raw_text, request.job_description)

    return ATSScoreResponse(
        analysis_id=analysis.id,
        match_percentage=ats_result["match_percentage"],
        matching_keywords=ats_result["matching_keywords"],
        missing_keywords=ats_result["missing_keywords"],
        suggestions=ats_result["suggestions"],
    )


@router.get("/history", response_model=AnalysisHistoryResponse)
async def get_history(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """Get list of past resume analyses."""
    # Count total
    count_result = await db.execute(
        select(ResumeAnalysis.id)
    )
    total = len(count_result.all())

    # Fetch analyses
    result = await db.execute(
        select(ResumeAnalysis)
        .order_by(desc(ResumeAnalysis.created_at))
        .offset(offset)
        .limit(limit)
    )
    analyses = result.scalars().all()

    items = [
        AnalysisHistoryItem(
            id=a.id,
            filename=a.filename,
            predicted_role=a.predicted_role,
            confidence=a.confidence,
            score=a.score,
            created_at=a.created_at,
        )
        for a in analyses
    ]

    return AnalysisHistoryResponse(analyses=items, total=total)


@router.get("/analysis/{analysis_id}", response_model=AnalysisDetail)
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed results for a single analysis."""
    # Fetch analysis
    result = await db.execute(
        select(ResumeAnalysis).where(ResumeAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Fetch skills
    skills_result = await db.execute(
        select(SkillResult).where(SkillResult.analysis_id == analysis_id)
    )
    skills = skills_result.scalars().all()

    detected = [
        SkillItem(name=s.skill_name, category=s.category or "tool")
        for s in skills if s.skill_type == "detected"
    ]
    missing = [
        SkillItem(name=s.skill_name, category=s.category or "tool")
        for s in skills if s.skill_type == "missing"
    ]

    # Re-generate career suggestions
    detected_dict: dict[str, list[str]] = {}
    for s in detected:
        detected_dict.setdefault(s.category, []).append(s.name)

    missing_list = [{"name": s.name, "category": s.category} for s in missing]

    career = generate_career_suggestions(
        analysis.predicted_role or "Other",
        detected_dict,
        missing_list,
    )

    # Classification scores (re-predict if we have the text)
    all_scores = []
    if analysis.raw_text:
        try:
            predictor = get_predictor(settings.MODEL_PATH)
            prediction = predictor.predict(analysis.raw_text)
            all_scores = [
                ClassificationScore(category=cat, probability=prob)
                for cat, prob in prediction.all_probabilities.items()
            ]
        except Exception:
            pass

    return AnalysisDetail(
        id=analysis.id,
        filename=analysis.filename,
        predicted_role=analysis.predicted_role,
        confidence=analysis.confidence,
        score=analysis.score,
        all_scores=all_scores,
        detected_skills=detected,
        missing_skills=missing,
        career_suggestions=CareerSuggestions(**career),
        created_at=analysis.created_at,
    )
