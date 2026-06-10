"""
Application configuration via environment variables.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # --- Application ---
    APP_NAME: str = "Resume Classifier API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # --- Database ---
    # Default to SQLite for local development.
    # For production, use PostgreSQL:
    #   postgresql+asyncpg://user:password@host:5432/resume_classifier
    DATABASE_URL: str = "sqlite+aiosqlite:///./data.db"

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # --- ML Model ---
    MODEL_PATH: str = str(
        Path(__file__).resolve().parent.parent.parent / "ml" / "models"
    )

    # --- File Upload ---
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton instance
settings = Settings()
