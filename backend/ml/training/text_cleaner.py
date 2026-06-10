"""
Text cleaning pipeline for resume text.
Used during both model training and inference to ensure consistency.
"""

import re
import spacy

# Load spaCy model (small English model)
# Download with: python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
except OSError:
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' not found. "
        "Install it with: python -m spacy download en_core_web_sm"
    )

# Common English stopwords (subset — spaCy also handles this)
EXTRA_STOPWORDS = {
    "resume", "curriculum", "vitae", "objective", "summary",
    "reference", "references", "available", "upon", "request",
    "page", "name", "address", "phone", "email", "date",
}


def clean_text(text: str) -> str:
    """Clean resume text for ML processing.

    Pipeline:
        1. Convert to lowercase
        2. Remove URLs
        3. Remove email addresses
        4. Remove phone numbers
        5. Remove special characters and punctuation
        6. Remove extra whitespace
        7. Remove stopwords
        8. Lemmatize tokens

    Args:
        text: Raw resume text string.

    Returns:
        Cleaned text string ready for TF-IDF vectorization.
    """
    if not text or not isinstance(text, str):
        return ""

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+\.\S+", " ", text)

    # Remove phone numbers (various formats)
    text = re.sub(r"[\+]?[\d\-\(\)\s]{7,15}", " ", text)

    # Remove special characters and punctuation (keep letters and spaces)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Process with spaCy for lemmatization and stopword removal
    doc = nlp(text)
    tokens = []
    for token in doc:
        # Skip stopwords, punctuation, whitespace, and very short tokens
        if (
            token.is_stop
            or token.is_punct
            or token.is_space
            or len(token.text) < 2
            or token.text in EXTRA_STOPWORDS
        ):
            continue
        tokens.append(token.lemma_)

    return " ".join(tokens)


def clean_text_light(text: str) -> str:
    """Light cleaning for skill extraction (preserves more structure).

    Only removes URLs, emails, and normalizes whitespace.
    Does NOT lemmatize or remove stopwords.

    Args:
        text: Raw resume text string.

    Returns:
        Lightly cleaned text.
    """
    if not text or not isinstance(text, str):
        return ""

    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text
