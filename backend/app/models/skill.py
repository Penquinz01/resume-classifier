"""
Skill Result SQLAlchemy model.
"""

import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SkillResult(Base):
    """Stores individual skill results for a resume analysis."""

    __tablename__ = "skill_results"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("resume_analyses.id", ondelete="CASCADE"),
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(100))
    skill_type: Mapped[str] = mapped_column(
        String(50),
        comment="'detected' or 'missing'",
    )
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="e.g. 'language', 'framework', 'database', 'cloud', 'tool'",
    )

    # Relationships
    analysis = relationship("ResumeAnalysis", back_populates="skills")

    def __repr__(self) -> str:
        return (
            f"<SkillResult {self.skill_name} "
            f"type={self.skill_type} "
            f"category={self.category}>"
        )
