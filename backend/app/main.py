"""
FastAPI application entry point.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend root is in sys.path for ml imports
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup: create tables (development only)
    await init_db()

    # Pre-load ML model (fail fast if missing)
    try:
        from ml.inference.predictor import get_predictor
        predictor = get_predictor(settings.MODEL_PATH)
        predictor.load()
        print(f"[✓] ML model loaded from {settings.MODEL_PATH}")
        if predictor.metadata:
            print(f"    Model: {predictor.metadata.get('model_name', 'unknown')}")
            print(f"    F1 Score: {predictor.metadata.get('f1_score', 'N/A')}")
    except FileNotFoundError as e:
        print(f"[!] ML model not found: {e}")
        print("    The API will start but classification endpoints will fail.")
        print("    Run the training script first: python -m ml.training.train_model")
    except Exception as e:
        print(f"[!] Error loading ML model: {e}")

    yield

    # Shutdown: cleanup if needed
    print("[✓] Application shutdown complete.")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered resume classification, skill extraction, and career insights.",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}
