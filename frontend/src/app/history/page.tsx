"use client";

/**
 * History Page — lists all past resume analyses.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Navbar } from "@/components/Navbar";
import { getHistory } from "@/lib/api";
import type { AnalysisHistoryItem } from "@/types";

export default function HistoryPage() {
  const router = useRouter();
  const [analyses, setAnalyses] = useState<AnalysisHistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    getHistory(50, 0)
      .then((data) => {
        setAnalyses(data.analyses);
        setTotal(data.total);
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
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
          <h1 className="page-title">History</h1>
          <p className="page-description">
            {total > 0
              ? `${total} resume${total !== 1 ? "s" : ""} analyzed`
              : "No analyses yet"}
          </p>
        </motion.div>

        {isLoading && (
          <div className="empty-state">
            <div
              className="spinner"
              style={{
                width: 24,
                height: 24,
                border: "2px solid #262626",
                borderTopColor: "#FAFAFA",
                borderRadius: "50%",
                margin: "0 auto",
              }}
            />
          </div>
        )}

        {error && (
          <div className="empty-state">
            <p className="empty-state-title">Error</p>
            <p className="empty-state-text">{error}</p>
          </div>
        )}

        {!isLoading && !error && analyses.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
            </div>
            <p className="empty-state-title">No analyses yet</p>
            <p className="empty-state-text">
              Upload a resume to get started.
            </p>
            <button
              className="btn btn-primary"
              onClick={() => router.push("/")}
              style={{ marginTop: "1rem" }}
            >
              Upload Resume
            </button>
          </div>
        )}

        {analyses.length > 0 && (
          <motion.div
            className="card-section"
            style={{ padding: 0, overflow: "hidden" }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2, delay: 0.05 }}
          >
            <table className="history-table" id="history-table">
              <thead>
                <tr>
                  <th>Resume</th>
                  <th>Predicted Role</th>
                  <th>Confidence</th>
                  <th>Score</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {analyses.map((a, i) => (
                  <motion.tr
                    key={a.id}
                    onClick={() => router.push(`/analysis/${a.id}`)}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.15, delay: i * 0.02 }}
                  >
                    <td>{a.filename}</td>
                    <td>
                      {a.predicted_role ? (
                        <span className="history-role-badge">
                          {a.predicted_role}
                        </span>
                      ) : (
                        <span className="history-confidence">Pending</span>
                      )}
                    </td>
                    <td className="history-confidence">
                      {a.confidence != null
                        ? `${Math.round(a.confidence * 100)}%`
                        : "—"}
                    </td>
                    <td className="history-confidence">
                      {a.score != null ? `${Math.round(a.score)}` : "—"}
                    </td>
                    <td className="history-date">{formatDate(a.created_at)}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        )}
      </main>
    </>
  );
}
