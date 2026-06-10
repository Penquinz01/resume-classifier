"""
Skill extraction from resume text.

Uses dictionary matching, regex patterns, and spaCy NER
to identify technical skills organized by category.
"""

import re
from ml.training.text_cleaner import clean_text_light


# --- Comprehensive Skill Dictionaries ---

SKILL_CATEGORIES: dict[str, list[str]] = {
    "language": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "go", "golang", "rust", "ruby", "php", "swift", "kotlin",
        "scala", "r", "matlab", "perl", "lua", "dart", "elixir",
        "haskell", "clojure", "assembly", "fortran", "cobol",
        "objective-c", "groovy", "julia", "shell", "bash",
        "powershell", "sql", "html", "css", "sass", "less",
    ],
    "framework": [
        "react", "reactjs", "react.js", "next.js", "nextjs",
        "angular", "vue", "vue.js", "vuejs", "svelte", "nuxt",
        "django", "flask", "fastapi", "express", "express.js",
        "spring", "spring boot", "springboot", ".net", "asp.net",
        "rails", "ruby on rails", "laravel", "symfony",
        "node.js", "nodejs", "deno", "bun",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn",
        "opencv", "spacy", "nltk", "transformers", "huggingface",
        "flutter", "react native", "electron",
        "tailwind", "tailwindcss", "bootstrap", "material ui",
        "jquery", "three.js", "d3.js", "d3",
        "fastify", "nestjs", "koa", "hapi",
        "gin", "echo", "fiber", "actix",
        "unity", "unreal engine", "godot",
    ],
    "database": [
        "postgresql", "postgres", "mysql", "mariadb", "sqlite",
        "mongodb", "cassandra", "couchdb", "dynamodb",
        "redis", "memcached", "elasticsearch",
        "oracle", "sql server", "mssql",
        "firebase", "firestore", "supabase",
        "neo4j", "graphql", "prisma",
        "sequelize", "typeorm", "sqlalchemy",
        "mongoose", "drizzle",
    ],
    "cloud": [
        "aws", "amazon web services", "ec2", "s3", "lambda",
        "azure", "microsoft azure",
        "gcp", "google cloud", "google cloud platform",
        "heroku", "vercel", "netlify", "render",
        "digitalocean", "linode", "cloudflare",
        "docker", "kubernetes", "k8s",
        "terraform", "ansible", "puppet", "chef",
        "ci/cd", "jenkins", "github actions", "gitlab ci",
        "circleci", "travis ci", "argo cd",
        "serverless", "cloudformation", "cdk",
    ],
    "tool": [
        "git", "github", "gitlab", "bitbucket",
        "jira", "confluence", "trello", "asana", "notion",
        "figma", "sketch", "adobe xd", "photoshop", "illustrator",
        "vs code", "vscode", "intellij", "pycharm", "vim", "neovim",
        "postman", "swagger", "insomnia",
        "linux", "ubuntu", "centos", "debian",
        "nginx", "apache", "caddy",
        "grafana", "prometheus", "datadog", "new relic",
        "splunk", "elk", "kibana", "logstash",
        "webpack", "vite", "rollup", "esbuild", "turbopack",
        "npm", "yarn", "pnpm", "pip", "poetry", "conda",
        "pytest", "jest", "mocha", "cypress", "selenium",
        "playwright", "puppeteer",
        "kafka", "rabbitmq", "celery", "airflow",
        "tableau", "power bi", "looker",
        "jupyter", "colab", "databricks",
        "mlflow", "wandb", "dvc",
        "agile", "scrum", "kanban",
        "rest", "rest api", "grpc", "websocket",
        "oauth", "jwt", "saml",
    ],
}

# Flatten for quick lookup: skill_name -> category
_SKILL_LOOKUP: dict[str, str] = {}
for category, skills in SKILL_CATEGORIES.items():
    for skill in skills:
        _SKILL_LOOKUP[skill.lower()] = category


# --- Role-Specific Required Skills ---

ROLE_REQUIRED_SKILLS: dict[str, list[str]] = {
    "Data Scientist": [
        "python", "sql", "pandas", "numpy", "scikit-learn",
        "tensorflow", "pytorch", "matplotlib", "statistics",
        "jupyter", "r", "machine learning", "deep learning",
    ],
    "Machine Learning Engineer": [
        "python", "tensorflow", "pytorch", "scikit-learn",
        "docker", "kubernetes", "mlflow", "aws", "sql",
        "pandas", "numpy", "ci/cd", "git", "rest api",
    ],
    "Software Engineer": [
        "python", "java", "javascript", "git", "sql",
        "docker", "rest api", "ci/cd", "linux",
        "data structures", "algorithms", "testing",
    ],
    "Frontend Developer": [
        "javascript", "typescript", "react", "html", "css",
        "git", "tailwind", "next.js", "vue", "webpack",
        "responsive design", "figma", "jest",
    ],
    "Backend Developer": [
        "python", "java", "sql", "postgresql", "mongodb",
        "docker", "rest api", "git", "linux", "redis",
        "ci/cd", "microservices", "node.js",
    ],
    "DevOps Engineer": [
        "docker", "kubernetes", "aws", "terraform", "linux",
        "ci/cd", "jenkins", "github actions", "ansible",
        "prometheus", "grafana", "python", "bash",
    ],
    "Data Analyst": [
        "sql", "python", "excel", "tableau", "power bi",
        "pandas", "statistics", "r", "visualization",
        "jupyter", "data cleaning", "reporting",
    ],
    "UI/UX Designer": [
        "figma", "sketch", "adobe xd", "photoshop",
        "html", "css", "prototyping", "wireframing",
        "user research", "usability testing", "typography",
    ],
    "QA Engineer": [
        "selenium", "cypress", "pytest", "jest",
        "automation testing", "manual testing", "jira",
        "postman", "sql", "git", "ci/cd", "python",
    ],
    "Product Manager": [
        "jira", "agile", "scrum", "sql", "analytics",
        "roadmap", "stakeholder management", "figma",
        "data analysis", "communication", "strategy",
    ],
    "Game Developer": [
        "unity", "unreal engine", "c++", "c#",
        "3d modeling", "game design", "shaders",
        "physics", "ai", "multiplayer", "godot",
    ],
    "HR": [
        "recruitment", "talent acquisition", "hris",
        "performance management", "employee relations",
        "compliance", "onboarding", "training",
    ],
}


def extract_skills(text: str) -> dict[str, list[str]]:
    """Extract skills from resume text using dictionary matching.

    Args:
        text: Raw or lightly cleaned resume text.

    Returns:
        Dictionary with skill categories as keys and lists of
        matched skill names as values.
    """
    cleaned = clean_text_light(text).lower()

    found: dict[str, list[str]] = {
        "language": [],
        "framework": [],
        "database": [],
        "cloud": [],
        "tool": [],
    }

    for skill, category in _SKILL_LOOKUP.items():
        # Use word boundary matching for short skills to avoid false positives
        if len(skill) <= 2:
            pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern, cleaned):
                if skill not in found[category]:
                    found[category].append(skill)
        else:
            if skill in cleaned:
                if skill not in found[category]:
                    found[category].append(skill)

    return found


def get_missing_skills(
    detected_skills: dict[str, list[str]],
    predicted_role: str,
) -> list[dict[str, str]]:
    """Determine which skills are missing for the predicted role.

    Args:
        detected_skills: Skills found in the resume (by category).
        predicted_role: The ML-predicted job category.

    Returns:
        List of dicts with 'name' and 'category' for each missing skill.
    """
    required = ROLE_REQUIRED_SKILLS.get(predicted_role, [])
    all_detected = set()
    for skills in detected_skills.values():
        all_detected.update(s.lower() for s in skills)

    missing = []
    for skill in required:
        if skill.lower() not in all_detected:
            # Determine category
            category = _SKILL_LOOKUP.get(skill.lower(), "tool")
            missing.append({"name": skill, "category": category})

    return missing
