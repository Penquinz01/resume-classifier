"""
ATS (Applicant Tracking System) scoring service.

Compares a resume against a job description to calculate
a match percentage and identify missing keywords.
"""

import re
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ml.training.text_cleaner import clean_text_light


def _extract_keywords(text: str, top_n: int = 50) -> list[str]:
    """Extract the most important keywords from text using TF-IDF.

    Args:
        text: Input text.
        top_n: Number of top keywords to return.

    Returns:
        List of keyword strings, ordered by importance.
    """
    # Simple word extraction for single-document TF-IDF
    words = re.findall(r"\b[a-zA-Z][a-zA-Z+#./-]{1,30}\b", text.lower())
    word_counts = Counter(words)

    # Filter out very common words
    stop_extras = {
        "the", "and", "for", "with", "that", "this", "from", "are",
        "was", "were", "been", "have", "has", "had", "will", "would",
        "could", "should", "may", "might", "can", "shall", "not",
        "but", "nor", "yet", "both", "each", "all", "any",
        "our", "your", "their", "its", "his", "her", "who",
        "which", "what", "when", "where", "how", "why",
        "also", "such", "than", "then", "into", "about",
        "over", "after", "before", "between", "under", "above",
        "able", "use", "using", "used", "work", "working",
        "experience", "year", "years", "role", "team",
    }

    filtered = {
        word: count
        for word, count in word_counts.items()
        if word not in stop_extras and len(word) > 1
    }

    # Sort by frequency
    sorted_words = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]


def calculate_ats_score(
    resume_text: str,
    job_description: str,
) -> dict:
    """Calculate ATS match score between a resume and job description.

    Args:
        resume_text: Raw resume text.
        job_description: Job description text.

    Returns:
        Dictionary with match_percentage, matching_keywords,
        missing_keywords, and suggestions.
    """
    # Clean texts lightly (preserve structure for keyword matching)
    resume_clean = clean_text_light(resume_text).lower()
    jd_clean = clean_text_light(job_description).lower()

    # --- TF-IDF Cosine Similarity ---
    vectorizer = TfidfVectorizer(
        max_features=3000,
        ngram_range=(1, 2),
        stop_words="english",
    )

    try:
        tfidf_matrix = vectorizer.fit_transform([resume_clean, jd_clean])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:
        # If vectorization fails (e.g., empty text)
        similarity = 0.0

    # Convert to percentage (scale up — raw cosine is usually low for docs)
    match_percentage = min(round(similarity * 100 * 1.5, 1), 100.0)

    # --- Keyword Analysis ---
    jd_keywords = _extract_keywords(jd_clean, top_n=40)
    resume_lower = resume_clean

    matching = []
    missing = []

    for keyword in jd_keywords:
        if keyword in resume_lower:
            matching.append(keyword)
        else:
            missing.append(keyword)

    # --- Generate Suggestions ---
    suggestions = _generate_suggestions(missing, match_percentage)

    return {
        "match_percentage": match_percentage,
        "matching_keywords": matching[:20],  # Top 20
        "missing_keywords": missing[:15],    # Top 15 missing
        "suggestions": suggestions,
    }


def _generate_suggestions(missing_keywords: list[str], match_pct: float) -> list[str]:
    """Generate actionable resume improvement suggestions.

    Args:
        missing_keywords: Keywords found in JD but not in resume.
        match_pct: Current match percentage.

    Returns:
        List of suggestion strings.
    """
    suggestions = []

    if match_pct < 30:
        suggestions.append(
            "Your resume has low alignment with this job description. "
            "Consider tailoring your resume specifically for this role."
        )
    elif match_pct < 60:
        suggestions.append(
            "Your resume has moderate alignment. Adding missing keywords "
            "could significantly improve your ATS score."
        )
    else:
        suggestions.append(
            "Your resume has good alignment with this job description. "
            "Fine-tune with the missing keywords below for an even stronger match."
        )

    if missing_keywords:
        top_missing = ", ".join(missing_keywords[:5])
        suggestions.append(
            f"Add these high-priority keywords to your resume: {top_missing}"
        )

    if len(missing_keywords) > 5:
        suggestions.append(
            f"Consider incorporating {len(missing_keywords) - 5} additional "
            "keywords from the job description where relevant to your experience."
        )

    suggestions.append(
        "Use the exact terminology from the job description — "
        "ATS systems often match on exact phrases."
    )

    suggestions.append(
        "Quantify your achievements where possible "
        "(e.g., 'Improved performance by 40%' instead of 'Improved performance')."
    )

    return suggestions
