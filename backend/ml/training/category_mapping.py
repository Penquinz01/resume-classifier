"""
Category mapping from Kaggle Updated Resume Dataset (25 categories)
to the project's 13 target categories.
"""

# Mapping: Kaggle category -> Target category
CATEGORY_MAP: dict[str, str] = {
    # Data Science & Analytics
    "Data Science": "Data Scientist",
    "Business Analyst": "Data Analyst",

    # Machine Learning (mapped from broader data science roles)
    # Note: The Kaggle dataset doesn't have a dedicated ML Engineer category.
    # If needed, a subset of "Data Science" resumes could be reclassified
    # based on keyword presence (e.g., "model deployment", "MLOps").

    # Software Engineering
    "Python Developer": "Software Engineer",
    "Java Developer": "Software Engineer",
    "DotNet Developer": "Software Engineer",
    "SAP Developer": "Software Engineer",
    "Blockchain": "Software Engineer",

    # Frontend
    "Web Designing": "Frontend Developer",

    # Backend
    "Database": "Backend Developer",
    "ETL Developer": "Backend Developer",
    "Hadoop": "Backend Developer",

    # DevOps
    "DevOps Engineer": "DevOps Engineer",
    "Network Security Engineer": "DevOps Engineer",

    # QA
    "Automation Testing": "QA Engineer",
    "Testing": "QA Engineer",

    # Product / Management
    "PMO": "Product Manager",
    "Operations Manager": "Product Manager",

    # HR
    "HR": "HR",

    # Other (non-tech or niche)
    "Arts": "Other",
    "Advocate": "Other",
    "Sales": "Other",
    "Health and fitness": "Other",
    "Civil Engineer": "Other",
    "Mechanical Engineer": "Other",
    "Electrical Engineering": "Other",
}

# The full list of target categories our model will predict
TARGET_CATEGORIES: list[str] = [
    "Data Scientist",
    "Machine Learning Engineer",
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "DevOps Engineer",
    "Data Analyst",
    "UI/UX Designer",
    "QA Engineer",
    "Product Manager",
    "Game Developer",
    "HR",
    "Other",
]


def map_category(kaggle_category: str) -> str:
    """Map a Kaggle dataset category to a target category.

    Args:
        kaggle_category: Original category from the Kaggle dataset.

    Returns:
        Mapped target category string. Defaults to "Other" if unknown.
    """
    return CATEGORY_MAP.get(kaggle_category.strip(), "Other")
