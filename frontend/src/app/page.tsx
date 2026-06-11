"use client";

/**
 * Home Page — Resume upload with recent analyses.
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Navbar } from "@/components/Navbar";
import { ResumeUploader } from "@/components/ResumeUploader";
import { AnalysisDashboard } from "@/components/AnalysisDashboard";
import { useResumeUpload } from "@/hooks/useResumeUpload";
import { getHistory } from "@/lib/api";
import type { AnalysisHistoryItem } from "@/types";

export default function HomePage() {
  const router = useRouter();
  const {
    step,
    file,
    result,
    error,
    progress,
    handleFileSelect,
    handleUploadAndClassify,
    reset,
  } = useResumeUpload();

  const [recentAnalyses, setRecentAnalyses] = useState<AnalysisHistoryItem[]>([]);

  useEffect(() => {
    getHistory(5, 0)
      .then((data) => setRecentAnalyses(data.analyses))
      .catch(() => {});
  }, [step]);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <>
      <Navbar />
      <main className="page-container">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          <h1 className="page-title">Resume Classifier</h1>
          <p className="page-description">
            Upload your resume to get AI-powered classification, skill analysis, and career insights.
          </p>
        </motion.div>

        {/* Upload Section */}
        <div style={{ maxWidth: "600px", margin: "0 auto 2rem" }}>
          <ResumeUploader
            onFileSelect={handleFileSelect}
            selectedFile={file}
            isDisabled={step === "uploading" || step === "classifying"}
          />

          {/* Action Button */}
          {file && step !== "complete" && (
            <motion.div
              style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.15 }}
            >
              <button
                className="btn btn-primary"
                onClick={handleUploadAndClassify}
                disabled={step === "uploading" || step === "classifying"}
                id="analyze-button"
                style={{ flex: 1 }}
              >
                {step === "uploading" || step === "classifying" ? (
                  <span className="btn-loading">
                    <svg className="spinner" width="16" height="16" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" fill="none" strokeDasharray="60" strokeLinecap="round">
                        <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/>
                      </circle>
                    </svg>
                    {step === "uploading" ? "Uploading..." : "Analyzing..."}
                  </span>
                ) : (
                  "Analyze Resume"
                )}
              </button>
            </motion.div>
          )}

          {/* Progress */}
          {(step === "uploading" || step === "classifying") && (
            <div className="progress-bar">
              <motion.div
                className="progress-bar-fill"
                initial={{ width: "0%" }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          )}

          {/* Status */}
          <AnimatePresence>
            {step === "uploading" && (
              <motion.p
                className="status-message"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                Uploading and parsing resume...
              </motion.p>
            )}
            {step === "classifying" && (
              <motion.p
                className="status-message"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                Running classification and extracting skills...
              </motion.p>
            )}
          </AnimatePresence>

          {/* Error */}
          {error && (
            <p className="status-message status-error">{error}</p>
          )}
        </div>

        {/* Results */}
        <AnimatePresence>
          {step === "complete" && result && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <h2 className="section-title">Analysis Results</h2>
                <button className="btn btn-secondary" onClick={reset} id="new-analysis-button">
                  New Analysis
                </button>
              </div>
              <AnalysisDashboard result={result} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Recent Analyses */}
        {step !== "complete" && recentAnalyses.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2, delay: 0.1 }}
            style={{ marginTop: "2rem" }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
              <h2 className="section-title">Recent Analyses</h2>
              <button
                className="btn btn-secondary"
                onClick={() => router.push("/history")}
                style={{ fontSize: "0.75rem", padding: "0.25rem 0.625rem" }}
              >
                View All
              </button>
            </div>
            <div className="card-section" style={{ padding: 0, overflow: "hidden" }}>
              <table className="history-table">
                <thead>
                  <tr>
                    <th>File</th>
                    <th>Role</th>
                    <th>Confidence</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAnalyses.map((a) => (
                    <tr
                      key={a.id}
                      onClick={() => router.push(`/analysis/${a.id}`)}
                    >
                      <td>{a.filename}</td>
                      <td>
                        {a.predicted_role ? (
                          <span className="history-role-badge">{a.predicted_role}</span>
                        ) : (
                          <span className="history-confidence">—</span>
                        )}
                      </td>
                      <td className="history-confidence">
                        {a.confidence != null
                          ? `${Math.round(a.confidence * 100)}%`
                          : "—"}
                      </td>
                      <td className="history-date">{formatDate(a.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </main>
    </>
  );
}
