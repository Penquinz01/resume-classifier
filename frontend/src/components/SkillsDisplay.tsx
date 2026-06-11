"use client";

/**
 * SkillsDisplay — categorized skill pills showing detected and missing skills.
 */

import { motion } from "framer-motion";
import type { SkillItem } from "@/types";
import { SKILL_CATEGORY_LABELS, SKILL_CATEGORY_ORDER, type SkillCategory } from "@/types";

interface SkillsDisplayProps {
  detected: SkillItem[];
  missing: SkillItem[];
}

function groupByCategory(skills: SkillItem[]): Record<string, SkillItem[]> {
  const grouped: Record<string, SkillItem[]> = {};
  for (const skill of skills) {
    if (!grouped[skill.category]) {
      grouped[skill.category] = [];
    }
    grouped[skill.category].push(skill);
  }
  return grouped;
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.03 },
  },
};

const item = {
  hidden: { opacity: 0, y: 4 },
  show: { opacity: 1, y: 0, transition: { duration: 0.15 } },
};

export function SkillsDisplay({ detected, missing }: SkillsDisplayProps) {
  const detectedGrouped = groupByCategory(detected);
  const missingGrouped = groupByCategory(missing);

  return (
    <div className="skills-display">
      {/* Detected Skills */}
      <div className="skills-section">
        <h3 className="skills-section-title">
          Detected Skills
          <span className="skills-count">{detected.length}</span>
        </h3>

        {SKILL_CATEGORY_ORDER.map((cat) => {
          const skills = detectedGrouped[cat];
          if (!skills || skills.length === 0) return null;

          return (
            <div key={cat} className="skills-category">
              <p className="skills-category-label">
                {SKILL_CATEGORY_LABELS[cat as SkillCategory]}
              </p>
              <motion.div
                className="skills-pills"
                variants={container}
                initial="hidden"
                animate="show"
              >
                {skills.map((skill) => (
                  <motion.span
                    key={skill.name}
                    className="skill-pill skill-pill-detected"
                    variants={item}
                  >
                    {skill.name}
                  </motion.span>
                ))}
              </motion.div>
            </div>
          );
        })}

        {detected.length === 0 && (
          <p className="skills-empty">No skills detected.</p>
        )}
      </div>

      {/* Missing Skills */}
      {missing.length > 0 && (
        <div className="skills-section">
          <h3 className="skills-section-title">
            Missing Skills
            <span className="skills-count skills-count-missing">
              {missing.length}
            </span>
          </h3>

          {SKILL_CATEGORY_ORDER.map((cat) => {
            const skills = missingGrouped[cat];
            if (!skills || skills.length === 0) return null;

            return (
              <div key={cat} className="skills-category">
                <p className="skills-category-label">
                  {SKILL_CATEGORY_LABELS[cat as SkillCategory]}
                </p>
                <motion.div
                  className="skills-pills"
                  variants={container}
                  initial="hidden"
                  animate="show"
                >
                  {skills.map((skill) => (
                    <motion.span
                      key={skill.name}
                      className="skill-pill skill-pill-missing"
                      variants={item}
                    >
                      {skill.name}
                    </motion.span>
                  ))}
                </motion.div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
