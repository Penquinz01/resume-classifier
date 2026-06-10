"""
Career advisor service — generates career improvement suggestions
based on predicted role and detected skills.
"""


# --- Learning Resources by Technology ---

LEARNING_RESOURCES: dict[str, str] = {
    "python": "Python documentation, Automate the Boring Stuff, Real Python",
    "javascript": "MDN Web Docs, JavaScript.info, freeCodeCamp",
    "typescript": "TypeScript Handbook, Total TypeScript by Matt Pocock",
    "react": "React.dev official docs, Epic React by Kent C. Dodds",
    "next.js": "Next.js official docs, Vercel tutorials",
    "vue": "Vue.js official guide, Vue Mastery",
    "angular": "Angular.io official docs, Angular University",
    "django": "Django official tutorial, Django for Beginners",
    "flask": "Flask Mega-Tutorial by Miguel Grinberg",
    "fastapi": "FastAPI official docs, TestDriven.io FastAPI course",
    "node.js": "Node.js official docs, The Odin Project",
    "sql": "SQLBolt, Mode SQL tutorial, LeetCode SQL",
    "postgresql": "PostgreSQL official docs, pgexercises.com",
    "mongodb": "MongoDB University free courses",
    "docker": "Docker official getting started, Docker Mastery on Udemy",
    "kubernetes": "Kubernetes.io official tutorials, KodeKloud",
    "aws": "AWS Skill Builder, A Cloud Guru, Adrian Cantrill courses",
    "gcp": "Google Cloud Skills Boost (Qwiklabs)",
    "azure": "Microsoft Learn, AZ-900 certification path",
    "terraform": "HashiCorp Learn, Terraform Up and Running",
    "git": "Pro Git book (free), Atlassian Git tutorials",
    "tensorflow": "TensorFlow official tutorials, DeepLearning.AI",
    "pytorch": "PyTorch official tutorials, fast.ai",
    "scikit-learn": "scikit-learn official docs, Hands-On ML by Aurélien Géron",
    "pandas": "Pandas documentation, Kaggle Learn",
    "figma": "Figma official tutorials, YouTube design channels",
    "selenium": "Selenium official docs, Test Automation University",
    "ci/cd": "GitHub Actions docs, GitLab CI/CD tutorials",
    "linux": "Linux Journey, The Linux Command Line book",
    "rest api": "RESTful API Design Best Practices, Postman Learning Center",
}


# --- Career Roadmaps by Role ---

CAREER_ROADMAPS: dict[str, list[str]] = {
    "Data Scientist": [
        "Master Python, SQL, and statistics fundamentals",
        "Learn data manipulation with Pandas, NumPy, and data visualization",
        "Study machine learning algorithms and scikit-learn",
        "Practice with Kaggle competitions and real-world datasets",
        "Learn deep learning (TensorFlow/PyTorch) for advanced projects",
        "Study MLOps: model deployment, monitoring, and CI/CD for ML",
        "Build a portfolio with 3-5 end-to-end data science projects",
        "Senior path: specialize in NLP, Computer Vision, or Recommender Systems",
    ],
    "Machine Learning Engineer": [
        "Solidify Python and software engineering fundamentals",
        "Master ML frameworks: scikit-learn, TensorFlow, or PyTorch",
        "Learn model deployment: Docker, Kubernetes, cloud platforms",
        "Study MLOps tools: MLflow, Kubeflow, or SageMaker",
        "Practice building end-to-end ML pipelines",
        "Learn distributed computing for large-scale ML",
        "Build production ML systems with monitoring and A/B testing",
        "Senior path: ML platform architecture, research engineering",
    ],
    "Software Engineer": [
        "Master 1-2 programming languages deeply (Python, Java, Go, etc.)",
        "Learn data structures, algorithms, and system design",
        "Understand databases (SQL + NoSQL) and API design",
        "Learn version control (Git), testing, and CI/CD",
        "Study cloud computing basics (AWS/GCP/Azure)",
        "Practice building full-stack applications",
        "Learn containerization (Docker) and orchestration (Kubernetes)",
        "Senior path: system design, architecture, technical leadership",
    ],
    "Frontend Developer": [
        "Master HTML, CSS, and JavaScript fundamentals",
        "Learn TypeScript for type-safe development",
        "Master a framework: React, Vue, or Angular",
        "Study responsive design, accessibility (a11y), and web performance",
        "Learn state management, routing, and API integration",
        "Study testing (Jest, Cypress, Playwright)",
        "Learn build tools: Vite, Webpack, and CI/CD",
        "Senior path: design systems, web performance, micro-frontends",
    ],
    "Backend Developer": [
        "Master a backend language: Python, Java, Go, or Node.js",
        "Learn SQL databases (PostgreSQL/MySQL) and ORM tools",
        "Study API design: REST, GraphQL, gRPC",
        "Learn authentication/authorization (OAuth, JWT)",
        "Study caching (Redis), message queues (Kafka/RabbitMQ)",
        "Learn containerization (Docker) and cloud deployment",
        "Study microservices architecture and distributed systems",
        "Senior path: system design, scalability, platform engineering",
    ],
    "DevOps Engineer": [
        "Learn Linux system administration and shell scripting",
        "Master containerization with Docker",
        "Learn orchestration with Kubernetes",
        "Study CI/CD pipelines (Jenkins, GitHub Actions, GitLab CI)",
        "Learn Infrastructure as Code: Terraform, CloudFormation",
        "Master a cloud platform: AWS, GCP, or Azure",
        "Study monitoring and observability (Prometheus, Grafana, ELK)",
        "Senior path: SRE, platform engineering, cloud architecture",
    ],
    "Data Analyst": [
        "Master SQL for data querying and manipulation",
        "Learn Excel/Google Sheets for business analysis",
        "Study Python or R for data analysis",
        "Learn data visualization tools: Tableau, Power BI, or Looker",
        "Study statistics and probability fundamentals",
        "Practice with real-world business datasets",
        "Learn data storytelling and presentation skills",
        "Senior path: analytics engineering, data strategy, BI architecture",
    ],
    "UI/UX Designer": [
        "Learn design fundamentals: typography, color theory, layout",
        "Master design tools: Figma (primary), Sketch, Adobe XD",
        "Study user research methodologies and usability testing",
        "Learn wireframing and prototyping techniques",
        "Study interaction design and micro-animations",
        "Build a portfolio with 5+ case studies showing full design process",
        "Learn design systems and component libraries",
        "Senior path: design leadership, product design, design systems",
    ],
    "QA Engineer": [
        "Learn manual testing fundamentals and test case design",
        "Master automation testing with Selenium, Cypress, or Playwright",
        "Study API testing with Postman, REST Assured",
        "Learn a programming language for test scripts (Python, JavaScript)",
        "Study CI/CD integration for automated testing",
        "Learn performance testing (JMeter, k6) and security testing basics",
        "Study test management tools: Jira, TestRail",
        "Senior path: QA architecture, test strategy, SDET leadership",
    ],
    "Product Manager": [
        "Learn product management frameworks (Lean, Agile, Jobs-to-be-Done)",
        "Study user research and customer discovery techniques",
        "Master roadmap planning and prioritization (RICE, MoSCoW)",
        "Learn analytics and data-driven decision making",
        "Study stakeholder management and communication",
        "Learn basic SQL for data analysis",
        "Practice building product specs, user stories, and PRDs",
        "Senior path: product strategy, portfolio management, VP Product",
    ],
    "Game Developer": [
        "Master C++ or C# programming",
        "Learn a game engine: Unity (C#) or Unreal Engine (C++)",
        "Study game design principles and game mechanics",
        "Learn 3D math: linear algebra, physics simulations",
        "Study graphics programming and shaders",
        "Practice building small, complete games (game jams)",
        "Learn multiplayer networking and game architecture",
        "Senior path: engine development, technical director, lead designer",
    ],
    "HR": [
        "Learn HR fundamentals: labor law, compliance, policies",
        "Study recruitment and talent acquisition best practices",
        "Master HRIS systems (Workday, BambooHR, SAP SuccessFactors)",
        "Learn performance management and employee development",
        "Study compensation and benefits administration",
        "Learn HR analytics and data-driven HR",
        "Practice conflict resolution and employee relations",
        "Senior path: HR leadership, people operations, CHRO",
    ],
}


def generate_career_suggestions(
    predicted_role: str,
    detected_skills: dict[str, list[str]],
    missing_skills: list[dict[str, str]],
) -> dict:
    """Generate career improvement suggestions.

    Args:
        predicted_role: The ML-predicted job role.
        detected_skills: Skills found in the resume.
        missing_skills: Skills missing for the target role.

    Returns:
        Dictionary with missing_skills, recommended_technologies,
        learning_suggestions, and career_roadmap.
    """
    # Missing skill names
    missing_names = [s["name"] for s in missing_skills]

    # Recommended technologies (top missing skills prioritized)
    recommended = missing_names[:8]

    # Generate learning suggestions for missing skills
    learning = []
    for skill in missing_names[:6]:
        resource = LEARNING_RESOURCES.get(skill.lower())
        if resource:
            learning.append(f"{skill}: {resource}")
        else:
            learning.append(f"{skill}: Search for tutorials on YouTube, Udemy, or Coursera")

    # Career roadmap
    roadmap = CAREER_ROADMAPS.get(predicted_role, [
        "Build a strong foundation in your domain",
        "Practice with real-world projects",
        "Contribute to open-source or build a portfolio",
        "Network and seek mentorship in your field",
        "Stay updated with industry trends",
    ])

    return {
        "missing_skills": missing_names,
        "recommended_technologies": recommended,
        "learning_suggestions": learning,
        "career_roadmap": roadmap,
    }
