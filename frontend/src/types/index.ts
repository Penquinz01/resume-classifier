/**
 * Shared TypeScript types for the application.
 * Re-exports API types and adds UI-specific types.
 */

export type {
  UploadResponse,
  ClassificationScore,
  SkillItem,
  CareerSuggestions,
  ClassificationResult,
  ATSScoreResponse,
  AnalysisHistoryItem,
  AnalysisDetail,
} from "@/lib/api";

// --- UI-specific types ---

export type AnalysisStep = "idle" | "uploading" | "classifying" | "complete" | "error";

export interface UploadState {
  step: AnalysisStep;
  file: File | null;
  analysisId: string | null;
  error: string | null;
}

export type SkillCategory = "language" | "framework" | "database" | "cloud" | "tool";

export const SKILL_CATEGORY_LABELS: Record<SkillCategory, string> = {
  language: "Languages",
  framework: "Frameworks",
  database: "Databases",
  cloud: "Cloud & DevOps",
  tool: "Tools",
};

export const SKILL_CATEGORY_ORDER: SkillCategory[] = [
  "language",
  "framework",
  "database",
  "cloud",
  "tool",
];
