/**
 * API client for communicating with the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// --- Types ---

export interface UploadResponse {
  analysis_id: string;
  filename: string;
  status: string;
  message: string;
}

export interface ClassificationScore {
  category: string;
  probability: number;
}

export interface SkillItem {
  name: string;
  category: string;
}

export interface CareerSuggestions {
  missing_skills: string[];
  recommended_technologies: string[];
  learning_suggestions: string[];
  career_roadmap: string[];
}

export interface ClassificationResult {
  analysis_id: string;
  predicted_role: string;
  confidence: number;
  all_scores: ClassificationScore[];
  detected_skills: SkillItem[];
  missing_skills: SkillItem[];
  career_suggestions: CareerSuggestions;
}

export interface ATSScoreResponse {
  analysis_id: string;
  match_percentage: number;
  matching_keywords: string[];
  missing_keywords: string[];
  suggestions: string[];
}

export interface AnalysisHistoryItem {
  id: string;
  filename: string;
  predicted_role: string | null;
  confidence: number | null;
  score: number | null;
  created_at: string;
}

export interface AnalysisDetail {
  id: string;
  filename: string;
  predicted_role: string | null;
  confidence: number | null;
  score: number | null;
  all_scores: ClassificationScore[];
  detected_skills: SkillItem[];
  missing_skills: SkillItem[];
  career_suggestions: CareerSuggestions;
  created_at: string;
}

// --- API Functions ---

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }
  return response.json();
}

/**
 * Upload a resume file.
 */
export async function uploadResume(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/resume/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<UploadResponse>(response);
}

/**
 * Classify a previously uploaded resume.
 */
export async function classifyResume(analysisId: string): Promise<ClassificationResult> {
  const response = await fetch(`${API_BASE}/resume/classify?analysis_id=${analysisId}`, {
    method: "POST",
  });

  return handleResponse<ClassificationResult>(response);
}

/**
 * Get ATS score for a resume against a job description.
 */
export async function getATSScore(
  analysisId: string,
  jobDescription: string
): Promise<ATSScoreResponse> {
  const response = await fetch(`${API_BASE}/resume/ats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      analysis_id: analysisId,
      job_description: jobDescription,
    }),
  });

  return handleResponse<ATSScoreResponse>(response);
}

/**
 * Get analysis history.
 */
export async function getHistory(
  limit: number = 50,
  offset: number = 0
): Promise<{ analyses: AnalysisHistoryItem[]; total: number }> {
  const response = await fetch(
    `${API_BASE}/history?limit=${limit}&offset=${offset}`
  );

  return handleResponse(response);
}

/**
 * Get detailed analysis results.
 */
export async function getAnalysisDetail(analysisId: string): Promise<AnalysisDetail> {
  const response = await fetch(`${API_BASE}/analysis/${analysisId}`);
  return handleResponse<AnalysisDetail>(response);
}
