"use client";

/**
 * Custom hook for managing resume upload and classification flow.
 */

import { useState, useCallback } from "react";
import { uploadResume, classifyResume } from "@/lib/api";
import type { ClassificationResult, AnalysisStep } from "@/types";

interface UseResumeUploadReturn {
  step: AnalysisStep;
  file: File | null;
  analysisId: string | null;
  result: ClassificationResult | null;
  error: string | null;
  progress: number;
  handleFileSelect: (file: File) => void;
  handleUploadAndClassify: () => Promise<void>;
  reset: () => void;
}

export function useResumeUpload(): UseResumeUploadReturn {
  const [step, setStep] = useState<AnalysisStep>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const handleFileSelect = useCallback((selectedFile: File) => {
    // Validate file type
    const ext = selectedFile.name.split(".").pop()?.toLowerCase();
    if (ext !== "pdf" && ext !== "docx") {
      setError("Please upload a PDF or DOCX file.");
      return;
    }

    // Validate file size (10 MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File size must be under 10 MB.");
      return;
    }

    setFile(selectedFile);
    setError(null);
    setStep("idle");
    setResult(null);
  }, []);

  const handleUploadAndClassify = useCallback(async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    try {
      // Step 1: Upload
      setStep("uploading");
      setError(null);
      setProgress(20);

      const uploadResult = await uploadResume(file);
      setAnalysisId(uploadResult.analysis_id);
      setProgress(50);

      // Step 2: Classify
      setStep("classifying");
      setProgress(70);

      const classifyResult = await classifyResume(uploadResult.analysis_id);
      setResult(classifyResult);
      setProgress(100);

      // Done
      setStep("complete");
    } catch (err) {
      setStep("error");
      setError(err instanceof Error ? err.message : "An unexpected error occurred.");
    }
  }, [file]);

  const reset = useCallback(() => {
    setStep("idle");
    setFile(null);
    setAnalysisId(null);
    setResult(null);
    setError(null);
    setProgress(0);
  }, []);

  return {
    step,
    file,
    analysisId,
    result,
    error,
    progress,
    handleFileSelect,
    handleUploadAndClassify,
    reset,
  };
}
