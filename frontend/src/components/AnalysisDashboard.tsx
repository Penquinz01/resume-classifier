"use client";

/**
 * AnalysisDashboard — two-column layout showing all analysis results.
 */

import { motion } from "framer-motion";
import type { ClassificationResult } from "@/types";
import { ConfidenceGauge } from "./ConfidenceGauge";
import { SkillsDisplay } from "./SkillsDisplay";
import { ATSScorer } from "./ATSScorer";

interface AnalysisDashboardProps {
  result: ClassificationResult;
}

const fadeIn = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.2 },
};

export function AnalysisDashboard({ result }: AnalysisDashboardProps) {
  const overallScore = Math.round(
    result.confidence * 40 +
    (result.detected_skills.length /
      Math.max(result.detected_skills.length + result.missing_skills.length, 1)) *
      30 +
    Math.min(result.detected_skills.length / 15, 1) * 30
  );

  return (
    <div className="analysis-dashboard">
      {/* Top: Summary Cards */}
      <div className="dashboard-grid">
        {/* Left: Score & Role */}
        <motion.div className="card-section" {...fadeIn}>
          <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
            <ConfidenceGauge value={result.confidence} size={120} />
            <div>
              <p className="stat-label">Predicted Role</p>
              <p className="stat-value" style={{ fontSize: "1.125rem", marginBottom: "0.5rem" }}>
                {result.predicted_role}
              </p>
              <div className="stat-row" style={{ padding: 0 }}>
                <span className="stat-label">Resume Score</span>
                <span className="stat-value">{overallScore}/100</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Right: Top Scores */}
        <motion.div className="card-section" {...fadeIn} transition={{ ...fadeIn.transition, delay: 0.05 }}>
          <p className="section-title" style={{ marginBottom: "0.75rem" }}>Classification Scores</p>
          {result.all_scores.slice(0, 5).map((score) => (
            <div key={score.category} className="stat-row">
              <span className="stat-label">{score.category}</span>
              <span className="stat-value" style={{ fontVariantNumeric: "tabular-nums" }}>
                {Math.round(score.probability * 100)}%
              </span>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Skills Section */}
      <motion.div
        className="card-section"
        {...fadeIn}
        transition={{ ...fadeIn.transition, delay: 0.1 }}
      >
        <SkillsDisplay
          detected={result.detected_skills}
          missing={result.missing_skills}
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
          Recommended path for {result.predicted_role}
        </p>
        <ol className="career-roadmap-list">
          {result.career_suggestions.career_roadmap.map((step, i) => (
            <li key={i} className="career-roadmap-item">{step}</li>
          ))}
        </ol>

        {result.career_suggestions.learning_suggestions.length > 0 && (
          <div style={{ marginTop: "1.25rem" }}>
            <h4 className="ats-keyword-title">Learning Resources</h4>
            <ul className="learning-list">
              {result.career_suggestions.learning_suggestions.map((item, i) => (
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
        <ATSScorer analysisId={result.analysis_id} />
      </motion.div>
    </div>
  );
}
