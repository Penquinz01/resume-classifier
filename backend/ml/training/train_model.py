"""
Resume Classification Model Training Pipeline.

This script:
    1. Loads the Kaggle UpdatedResumeDataSet.csv
    2. Maps categories to 13 target classes
    3. Cleans text using spaCy-based pipeline
    4. Vectorizes with TF-IDF
    5. Trains and compares: Logistic Regression, Random Forest, Linear SVM
    6. Evaluates with accuracy, precision, recall, F1, confusion matrix
    7. Saves the best model, vectorizer, and label encoder via Joblib

Usage:
    python -m ml.training.train_model
    # or
    python ml/training/train_model.py

Requires:
    - UpdatedResumeDataSet.csv in ml/training/data/
    - python -m spacy download en_core_web_sm
"""

import os
import sys
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

# Add parent directories to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ml.training.category_mapping import map_category
from ml.training.text_cleaner import clean_text

# --- Configuration ---
DATA_DIR = SCRIPT_DIR / "data"
MODELS_DIR = SCRIPT_DIR.parent / "models"
CSV_FILENAME = "UpdatedResumeDataSet.csv"
TEST_SIZE = 0.2
RANDOM_STATE = 42
TFIDF_MAX_FEATURES = 5000


def load_and_prepare_data(csv_path: Path) -> pd.DataFrame:
    """Load the Kaggle CSV and map categories to target labels."""
    print(f"[1/6] Loading dataset from {csv_path}...")

    df = pd.read_csv(csv_path)
    
    # Map Resume_str column to Resume if loading the custom dataset
    if "Resume_str" in df.columns and "Resume" not in df.columns:
        df["Resume"] = df["Resume_str"]

    print(f"       Loaded {len(df)} resumes with {df['Category'].nunique()} categories")

    # Show original category distribution
    print("\n       Original category distribution:")
    for cat, count in df["Category"].value_counts().items():
        print(f"         {cat}: {count}")

    # Map categories
    df["target_category"] = df["Category"].apply(map_category)
    print(f"\n       After mapping: {df['target_category'].nunique()} target categories")

    # Show mapped distribution
    print("\n       Target category distribution:")
    for cat, count in df["target_category"].value_counts().items():
        print(f"         {cat}: {count}")

    # Drop categories with too few samples (< 3) for stratified split
    category_counts = df["target_category"].value_counts()
    small_cats = category_counts[category_counts < 3].index.tolist()
    if small_cats:
        print(f"\n       Warning: Merging small categories into 'Other': {small_cats}")
        df.loc[df["target_category"].isin(small_cats), "target_category"] = "Other"

    return df


def clean_all_resumes(df: pd.DataFrame) -> pd.DataFrame:
    """Apply text cleaning to all resume texts."""
    print("\n[2/6] Cleaning resume text (this may take a minute)...")

    total = len(df)
    cleaned_texts = []
    for i, text in enumerate(df["Resume"]):
        if (i + 1) % 100 == 0 or i == 0:
            print(f"       Processing {i + 1}/{total}...", end="\r")
        cleaned_texts.append(clean_text(str(text)))

    df["cleaned_text"] = cleaned_texts
    print(f"\n       Cleaned {total} resumes.")

    # Remove any rows where cleaning resulted in empty text
    empty_count = (df["cleaned_text"].str.strip() == "").sum()
    if empty_count > 0:
        print(f"       Removing {empty_count} empty resumes after cleaning.")
        df = df[df["cleaned_text"].str.strip() != ""].copy()

    return df


def vectorize_text(
    X_train: pd.Series, X_test: pd.Series
) -> tuple[np.ndarray, np.ndarray, TfidfVectorizer]:
    """Fit TF-IDF vectorizer on training data and transform both sets."""
    print("\n[3/6] Vectorizing with TF-IDF...")

    vectorizer = TfidfVectorizer(
        max_features=TFIDF_MAX_FEATURES,
        ngram_range=(1, 2),  # unigrams + bigrams
        sublinear_tf=True,
        min_df=2,
        max_df=0.95,
    )

    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    print(f"       Vocabulary size: {len(vectorizer.vocabulary_)}")
    print(f"       Train matrix shape: {X_train_tfidf.shape}")
    print(f"       Test matrix shape: {X_test_tfidf.shape}")

    return X_train_tfidf, X_test_tfidf, vectorizer


def train_and_evaluate_models(
    X_train, X_test, y_train, y_test, label_encoder: LabelEncoder
) -> dict:
    """Train multiple models, evaluate, and return results."""
    print("\n[4/6] Training and evaluating models...\n")

    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            C=1.0,
            solver="lbfgs",
            random_state=RANDOM_STATE,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(
                max_iter=2000,
                C=1.0,
                random_state=RANDOM_STATE,
            ),
            cv=3,
        ),
    }

    results = {}

    for name, model in models.items():
        print(f"  --- {name} ---")
        start = time.time()

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        elapsed = time.time() - start

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            "model": model,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "confusion_matrix": cm,
            "train_time": elapsed,
        }

        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1 Score:  {f1:.4f}")
        print(f"  Time:      {elapsed:.2f}s")

        # Full classification report
        target_names = label_encoder.classes_
        print(f"\n  Classification Report:\n")
        print(
            classification_report(
                y_test, y_pred, target_names=target_names, zero_division=0
            )
        )
        print()

    return results


def select_best_model(results: dict) -> tuple[str, dict]:
    """Select the model with the highest F1 score."""
    print("\n[5/6] Selecting best model...")

    best_name = max(results, key=lambda k: results[k]["f1_score"])
    best = results[best_name]

    print(f"       Best model: {best_name}")
    print(f"       F1 Score:   {best['f1_score']:.4f}")
    print(f"       Accuracy:   {best['accuracy']:.4f}")

    return best_name, best


def save_artifacts(
    model,
    vectorizer: TfidfVectorizer,
    label_encoder: LabelEncoder,
    model_name: str,
    metrics: dict,
) -> None:
    """Save model, vectorizer, label encoder, and metadata to disk."""
    print("\n[6/6] Saving artifacts...")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Save model
    model_path = MODELS_DIR / "resume_classifier.joblib"
    joblib.dump(model, model_path)
    print(f"       Model saved to: {model_path}")

    # Save vectorizer
    vec_path = MODELS_DIR / "tfidf_vectorizer.joblib"
    joblib.dump(vectorizer, vec_path)
    print(f"       Vectorizer saved to: {vec_path}")

    # Save label encoder
    le_path = MODELS_DIR / "label_encoder.joblib"
    joblib.dump(label_encoder, le_path)
    print(f"       Label encoder saved to: {le_path}")

    # Save metadata
    metadata = {
        "model_name": model_name,
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "tfidf_max_features": TFIDF_MAX_FEATURES,
        "test_size": TEST_SIZE,
        "categories": label_encoder.classes_.tolist(),
        "train_time_seconds": metrics["train_time"],
    }
    meta_path = MODELS_DIR / "model_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"       Metadata saved to: {meta_path}")


def main() -> None:
    """Run the full training pipeline."""
    print("=" * 60)
    print("  Resume Classifier — Model Training Pipeline")
    print("=" * 60)

    csv_path = DATA_DIR / CSV_FILENAME
    
    # Check for custom local dataset in Resumes/Resume/Resume.csv
    custom_csv_path = BACKEND_DIR.parent / "Resumes" / "Resume" / "Resume.csv"
    if custom_csv_path.exists():
        csv_path = custom_csv_path
        print(f"\n[✓] Detected custom dataset at {csv_path}")
    elif not csv_path.exists():
        print(f"\nError: Dataset not found at {csv_path}")
        print(f"Please download 'UpdatedResumeDataSet.csv' from Kaggle and place it in:")
        print(f"  {DATA_DIR}/")
        print(f"\nKaggle URL: https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset")
        sys.exit(1)

    # Step 1: Load and prepare data
    df = load_and_prepare_data(csv_path)

    # Step 2: Clean text
    df = clean_all_resumes(df)

    # Step 3: Encode labels and split
    label_encoder = LabelEncoder()
    df["label"] = label_encoder.fit_transform(df["target_category"])

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        df["cleaned_text"],
        df["label"],
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["label"],
    )

    print(f"\n       Train size: {len(X_train_text)}")
    print(f"       Test size:  {len(X_test_text)}")

    # Step 4: Vectorize
    X_train_tfidf, X_test_tfidf, vectorizer = vectorize_text(X_train_text, X_test_text)

    # Step 5: Train and evaluate
    results = train_and_evaluate_models(
        X_train_tfidf, X_test_tfidf, y_train, y_test, label_encoder
    )

    # Step 6: Select best and save
    best_name, best_result = select_best_model(results)
    save_artifacts(
        model=best_result["model"],
        vectorizer=vectorizer,
        label_encoder=label_encoder,
        model_name=best_name,
        metrics=best_result,
    )

    print("\n" + "=" * 60)
    print("  Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
