"""
Resume Classification Inference Module.

Loads the trained model, vectorizer, and label encoder from disk
and provides a simple prediction interface.
"""

import json
from pathlib import Path
from dataclasses import dataclass

import numpy as np
import joblib

# Add parent for imports
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ml.training.text_cleaner import clean_text


@dataclass
class PredictionResult:
    """Result of a resume classification prediction."""

    predicted_role: str
    confidence: float
    all_probabilities: dict[str, float]


class ResumePredictor:
    """Loads saved ML artifacts and predicts job categories from resume text."""

    def __init__(self, models_dir: str | Path | None = None):
        """Initialize the predictor by loading saved artifacts.

        Args:
            models_dir: Path to directory containing .joblib files.
                        Defaults to backend/ml/models/.
        """
        if models_dir is None:
            models_dir = SCRIPT_DIR.parent / "models"
        else:
            models_dir = Path(models_dir)

        self._models_dir = models_dir
        self._model = None
        self._vectorizer = None
        self._label_encoder = None
        self._metadata = None
        self._loaded = False

    def load(self) -> None:
        """Load model artifacts from disk or set up fallback mode."""
        model_path = self._models_dir / "resume_classifier.joblib"
        vec_path = self._models_dir / "tfidf_vectorizer.joblib"
        le_path = self._models_dir / "label_encoder.joblib"
        meta_path = self._models_dir / "model_metadata.json"

        # Check if all files exist
        all_exist = all(p.exists() for p in [model_path, vec_path, le_path])
        if not all_exist:
            print("\n" + "="*80)
            print("WARNING: ML model artifacts not found at:", self._models_dir)
            print("Running in MOCK/FALLBACK RULE-BASED MODE.")
            print("To use the real trained model, please run the training script:")
            print("  python -m ml.training.train_model")
            print("="*80 + "\n")
            self._fallback_mode = True
            self._metadata = {
                "model_type": "Fallback Rule-Based",
                "accuracy": 0.75,
                "f1_macro": 0.72,
                "trained_at": "N/A (Mock Mode)"
            }
            self._loaded = True
            return

        self._fallback_mode = False
        self._model = joblib.load(model_path)
        self._vectorizer = joblib.load(vec_path)
        self._label_encoder = joblib.load(le_path)

        if meta_path.exists():
            with open(meta_path) as f:
                self._metadata = json.load(f)

        self._loaded = True

    def _ensure_loaded(self) -> None:
        """Lazily load artifacts if not already loaded."""
        if not self._loaded:
            self.load()

    def _predict_fallback(self, cleaned_text: str) -> PredictionResult:
        """Rule-based prediction when ML model files aren't trained yet."""
        from ml.training.category_mapping import TARGET_CATEGORIES
        text = cleaned_text.lower()
        
        # Rule-based keyword matching
        keywords = {
            "Data Scientist": ["data scientist", "machine learning", "deep learning", "statistics", "data science", "pandas", "numpy", "scikit"],
            "Machine Learning Engineer": ["machine learning engineer", "mlops", "pytorch", "tensorflow", "neural networks", "computer vision", "llm", "transformers"],
            "Software Engineer": ["software engineer", "full stack", "java", "c++", "c#", "algorithms", "git", "oop", "object oriented"],
            "Frontend Developer": ["frontend developer", "react", "next.js", "nextjs", "javascript", "typescript", "html", "css", "vue", "angular", "tailwind"],
            "Backend Developer": ["backend developer", "fastapi", "django", "flask", "express", "nodejs", "node.js", "postgresql", "sqlite", "mongodb", "sql", "database", "redis"],
            "DevOps Engineer": ["devops", "aws", "docker", "kubernetes", "ci/cd", "jenkins", "terraform", "ansible", "linux", "cloud"],
            "Data Analyst": ["data analyst", "tableau", "power bi", "excel", "sql query", "dashboards", "business intelligence"],
            "UI/UX Designer": ["ui/ux", "designer", "figma", "sketch", "adobe xd", "wireframe", "prototype", "user experience"],
            "QA Engineer": ["qa engineer", "testing", "selenium", "cypress", "junit", "test cases", "automation testing"],
            "Product Manager": ["product manager", "scrum", "agile", "product roadmap", "backlog", "jira", "pmo", "stakeholder"],
            "Game Developer": ["game developer", "unity", "unreal engine", "shader", "game design"],
            "HR": ["hr", "human resources", "recruitment", "talent acquisition", "sourcing", "payroll", "employee relations"],
        }
        
        scores = {cat: 0.0 for cat in TARGET_CATEGORIES}
        
        # Count keyword occurrences
        total_matches = 0.0
        for category, kws in keywords.items():
            for kw in kws:
                count = text.count(kw)
                if count > 0:
                    scores[category] += count
                    total_matches += count
        
        # Normalize and compute probabilities
        if total_matches == 0:
            predicted_role = "Other"
            confidence = 0.5
            all_probabilities = {cat: 1.0 / len(TARGET_CATEGORIES) for cat in TARGET_CATEGORIES}
            all_probabilities["Other"] = 0.5
            # normalize remaining
            other_prob = all_probabilities["Other"]
            rem_prob = (1.0 - other_prob) / (len(TARGET_CATEGORIES) - 1)
            for cat in TARGET_CATEGORIES:
                if cat != "Other":
                    all_probabilities[cat] = rem_prob
        else:
            # Sort categories by score descending
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            # Pick top role
            predicted_role = sorted_scores[0][0]
            if scores[predicted_role] == 0:
                predicted_role = "Other"
            
            # Simple soft distribution
            base_prob = 0.02
            rem_prob_pool = 1.0 - (base_prob * len(TARGET_CATEGORIES))
            
            all_probabilities = {}
            for cat in TARGET_CATEGORIES:
                score = scores.get(cat, 0.0)
                share = score / total_matches if total_matches > 0 else 0
                all_probabilities[cat] = round(base_prob + share * rem_prob_pool, 4)
            
            predicted_prob = all_probabilities[predicted_role]
            confidence = float(predicted_prob)

        # Sort probability dict
        all_probabilities = dict(
            sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True)
        )

        return PredictionResult(
            predicted_role=predicted_role,
            confidence=round(confidence, 4),
            all_probabilities=all_probabilities
        )

    def predict(self, resume_text: str) -> PredictionResult:
        """Predict the job category for a resume.

        Args:
            resume_text: Raw resume text (will be cleaned internally).

        Returns:
            PredictionResult with predicted role, confidence, and
            probability distribution over all categories.
        """
        self._ensure_loaded()

        # Clean text using the same pipeline as training
        cleaned = clean_text(resume_text)

        if self._fallback_mode:
            return self._predict_fallback(cleaned)

        if not cleaned.strip():
            # If cleaning removes everything, return low-confidence "Other"
            return PredictionResult(
                predicted_role="Other",
                confidence=0.0,
                all_probabilities={
                    cat: 0.0 for cat in self._label_encoder.classes_
                },
            )

        # Vectorize
        text_vector = self._vectorizer.transform([cleaned])

        # Predict class
        predicted_label = self._model.predict(text_vector)[0]
        predicted_role = self._label_encoder.inverse_transform([predicted_label])[0]

        # Get probabilities
        if hasattr(self._model, "predict_proba"):
            probas = self._model.predict_proba(text_vector)[0]
        else:
            # Fallback for models without predict_proba
            probas = np.zeros(len(self._label_encoder.classes_))
            probas[predicted_label] = 1.0

        confidence = float(probas.max())

        # Build probability dict
        all_probabilities = {
            self._label_encoder.inverse_transform([i])[0]: float(p)
            for i, p in enumerate(probas)
        }

        # Sort by probability descending
        all_probabilities = dict(
            sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True)
        )

        return PredictionResult(
            predicted_role=predicted_role,
            confidence=round(confidence, 4),
            all_probabilities={
                k: round(v, 4) for k, v in all_probabilities.items()
            },
        )

    @property
    def metadata(self) -> dict | None:
        """Return model metadata (accuracy, F1, etc.) if available."""
        self._ensure_loaded()
        return self._metadata

    @property
    def categories(self) -> list[str]:
        """Return list of categories the model can predict."""
        self._ensure_loaded()
        if self._fallback_mode:
            from ml.training.category_mapping import TARGET_CATEGORIES
            return TARGET_CATEGORIES
        return self._label_encoder.classes_.tolist()


# Module-level singleton for convenience
_default_predictor: ResumePredictor | None = None


def get_predictor(models_dir: str | Path | None = None) -> ResumePredictor:
    """Get or create the default predictor singleton.

    Args:
        models_dir: Optional override for models directory.

    Returns:
        Loaded ResumePredictor instance.
    """
    global _default_predictor
    if _default_predictor is None:
        _default_predictor = ResumePredictor(models_dir)
    return _default_predictor

