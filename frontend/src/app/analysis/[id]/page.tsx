"use client";

/**
 * Analysis Detail Page — shows full results for a single analysis.
 */

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import { Navbar } from "@/components/Navbar";
import { ConfidenceGauge } from "@/components/ConfidenceGauge";
import { SkillsDisplay } from "@/components/SkillsDisplay";
import { ATSScorer } from "@/components/ATSScorer";
import { getAnalysisDetail } from "@/lib/api";
import type { AnalysisDetail } from "@/types";

const fadeIn = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.2 },
};

export default function AnalysisPage() {
  const params = useParams();
  const analysisId = params.id as string;

  const [data, setData] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!analysisId) return;

    setIsLoading(true);
    getAnalysisDetail(analysisId)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [analysisId]);

  const overallScore = data
    ? Math.round(
        (data.confidence ?? 0) * 40 +
        (data.detected_skills.length /
          Math.max(data.detected_skills.length + data.missing_skills.length, 1)) *
          30 +
        Math.min(data.detected_skills.length / 15, 1) * 30
      )
    : 0;

  return (
    <>
      <Navbar />
      <main className="page-container">
        {isLoading && (
          <div className="empty-state">
            <div className="spinner" style={{ width: 24, height: 24, border: "2px solid #262626", borderTopColor: "#FAFAFA", borderRadius: "50%", margin: "0 auto" }} />
            <p className="empty-state-text" style={{ marginTop: "1rem" }}>Loading analysis...</p>
          </div>
        )}

        {error && (
          <div className="empty-state">
            <p className="empty-state-title">Error</p>
            <p className="empty-state-text">{error}</p>
          </div>
        )}

        {data && (
          <>
            <motion.div {...fadeIn}>
              <p className="page-description" style={{ marginBottom: "0.25rem" }}>
                {data.filename}
              </p>
              <h1 className="page-title" style={{ marginBottom: "1.5rem" }}>
                {data.predicted_role || "Pending Analysis"}
              </h1>
            </motion.div>

            {/* Summary Cards */}
            <div className="dashboard-grid">
              <motion.div className="card-section" {...fadeIn}>
                <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
                  <ConfidenceGauge
                    value={data.confidence ?? 0}
                    size={120}
                  />
                  <div>
                    <div className="stat-row" style={{ padding: 0, marginBottom: "0.375rem" }}>
                      <span className="stat-label">Resume Score</span>
                      <span className="stat-value">{data.score ?? overallScore}/100</span>
                    </div>
                    <div className="stat-row" style={{ padding: 0 }}>
                      <span className="stat-label">Skills Found</span>
                      <span className="stat-value">{data.detected_skills.length}</span>
                    </div>
                    <div className="stat-row" style={{ padding: 0 }}>
                      <span className="stat-label">Skills Missing</span>
                      <span className="stat-value" style={{ color: data.missing_skills.length > 0 ? "#f87171" : "inherit" }}>
                        {data.missing_skills.length}
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>

              {data.all_scores.length > 0 && (
                <motion.div className="card-section" {...fadeIn} transition={{ ...fadeIn.transition, delay: 0.05 }}>
                  <p className="section-title" style={{ marginBottom: "0.75rem" }}>
                    Classification Scores
                  </p>
                  {data.all_scores.slice(0, 5).map((score) => (
                    <div key={score.category} className="stat-row">
                      <span className="stat-label">{score.category}</span>
                      <span className="stat-value" style={{ fontVariantNumeric: "tabular-nums" }}>
                        {Math.round(score.probability * 100)}%
                      </span>
                    </div>
                  ))}
                </motion.div>
              )}
            </div>

            {/* Skills */}
            <motion.div
              className="card-section"
              {...fadeIn}
              transition={{ ...fadeIn.transition, delay: 0.1 }}
            >
              <SkillsDisplay
                detected={data.detected_skills}
                missing={data.missing_skills}
              />
            </motion.div>

            {/* Career Suggestions */}
            <motion.div
              className="card-section career-section"
              {...fadeIn}
              transition={{ ...fadeIn.transition, delay: 0.15 }}
            >
              <h3 className="section-title">Career Roadmap</h3>
              <p className="section-description">
                Recommended path for {data.predicted_role}
              </p>
              <ol className="career-roadmap-list">
                {data.career_suggestions.career_roadmap.map((step, i) => (
                  <li key={i} className="career-roadmap-item">{step}</li>
                ))}
              </ol>

              {data.career_suggestions.learning_suggestions.length > 0 && (
                <div style={{ marginTop: "1.25rem" }}>
                  <h4 className="ats-keyword-title">Learning Resources</h4>
                  <ul className="learning-list">
                    {data.career_suggestions.learning_suggestions.map((item, i) => (
                      <li key={i} className="learning-item">{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </motion.div>

            {/* ATS Scorer */}
            <motion.div
              className="card-section"
              style={{ marginTop: "1rem" }}
              {...fadeIn}
              transition={{ ...fadeIn.transition, delay: 0.2 }}
            >
              <ATSScorer analysisId={data.id} />
            </motion.div>
          </>
        )}
      </main>
    </>
  );
}
