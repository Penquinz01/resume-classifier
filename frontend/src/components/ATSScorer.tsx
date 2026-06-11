"use client";

/**
 * ATSScorer — job description input + ATS match score display.
 */

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getATSScore } from "@/lib/api";
import type { ATSScoreResponse } from "@/types";

interface ATSScorerProps {
  analysisId: string;
}

export function ATSScorer({ analysisId }: ATSScorerProps) {
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState<ATSScoreResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScore = useCallback(async () => {
    if (jobDescription.trim().length < 10) {
      setError("Please enter a longer job description.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await getATSScore(analysisId, jobDescription);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to calculate ATS score.");
    } finally {
      setIsLoading(false);
    }
  }, [analysisId, jobDescription]);

  const getScoreColor = (pct: number): string => {
    if (pct >= 70) return "#4ade80";
    if (pct >= 40) return "#fbbf24";
    return "#f87171";
  };

  return (
    <div className="ats-scorer" id="ats-scorer">
      <h3 className="section-title">ATS Match Score</h3>
      <p className="section-description">
        Paste a job description to see how well your resume matches.
      </p>

      <div className="ats-input-group">
        <textarea
          className="ats-textarea"
          placeholder="Paste the job description here..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          rows={6}
          id="ats-job-description"
        />
        <button
          className="btn btn-primary"
          onClick={handleScore}
          disabled={isLoading || jobDescription.trim().length < 10}
          id="ats-score-button"
        >
          {isLoading ? (
            <span className="btn-loading">
              <svg className="spinner" width="16" height="16" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" fill="none" strokeDasharray="60" strokeLinecap="round">
                  <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/>
                </circle>
              </svg>
              Analyzing...
            </span>
          ) : (
            "Calculate Match"
          )}
        </button>
      </div>

      {error && (
        <p className="ats-error">{error}</p>
      )}

      <AnimatePresence>
        {result && (
          <motion.div
            className="ats-result"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Score */}
            <div className="ats-score-display">
              <div className="ats-score-circle">
                <svg width="100" height="100" viewBox="0 0 100 100">
                  <circle
                    cx="50" cy="50" r="42"
                    fill="none"
                    stroke="#262626"
                    strokeWidth="6"
                  />
                  <motion.circle
                    cx="50" cy="50" r="42"
                    fill="none"
                    stroke={getScoreColor(result.match_percentage)}
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeDasharray={2 * Math.PI * 42}
                    strokeDashoffset={2 * Math.PI * 42}
                    animate={{
                      strokeDashoffset:
                        2 * Math.PI * 42 * (1 - result.match_percentage / 100),
                    }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    transform="rotate(-90 50 50)"
                  />
                </svg>
                <span
                  className="ats-score-value"
                  style={{ color: getScoreColor(result.match_percentage) }}
                >
                  {Math.round(result.match_percentage)}%
                </span>
              </div>
              <p className="ats-score-label">ATS Match</p>
            </div>

            {/* Keywords */}
            <div className="ats-keywords">
              {result.matching_keywords.length > 0 && (
                <div className="ats-keyword-group">
                  <h4 className="ats-keyword-title">Matching Keywords</h4>
                  <div className="skills-pills">
                    {result.matching_keywords.map((kw) => (
                      <span key={kw} className="skill-pill skill-pill-detected">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {result.missing_keywords.length > 0 && (
                <div className="ats-keyword-group">
                  <h4 className="ats-keyword-title">Missing Keywords</h4>
                  <div className="skills-pills">
                    {result.missing_keywords.map((kw) => (
                      <span key={kw} className="skill-pill skill-pill-missing">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Suggestions */}
            {result.suggestions.length > 0 && (
              <div className="ats-suggestions">
                <h4 className="ats-keyword-title">Suggestions</h4>
                <ul className="ats-suggestion-list">
                  {result.suggestions.map((suggestion, i) => (
                    <li key={i} className="ats-suggestion-item">
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
