"use client";

/**
 * ConfidenceGauge — circular arc showing classification confidence.
 */

import { motion } from "framer-motion";

interface ConfidenceGaugeProps {
  value: number; // 0 to 1
  size?: number;
  label?: string;
}

export function ConfidenceGauge({
  value,
  size = 140,
  label = "Confidence",
}: ConfidenceGaugeProps) {
  const percentage = Math.round(value * 100);
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const fillLength = circumference * value;
  const center = size / 2;

  return (
    <div className="gauge-container" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="gauge-svg"
      >
        {/* Background circle */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="#262626"
          strokeWidth={strokeWidth}
        />
        {/* Filled arc */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="#FAFAFA"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          animate={{ strokeDashoffset: circumference - fillLength }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
          transform={`rotate(-90 ${center} ${center})`}
        />
      </svg>
      <div className="gauge-label">
        <motion.span
          className="gauge-value"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.2 }}
        >
          {percentage}%
        </motion.span>
        <span className="gauge-text">{label}</span>
      </div>
    </div>
  );
}
