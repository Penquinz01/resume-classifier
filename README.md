# Resume Classifier & Career Insights

AI-powered resume classification, skill extraction, career roadmap suggestions, and ATS match scoring.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?logo=scikit-learn&logoColor=white)

---

## Features

- **Resume Classification** — Predicts job role (13 categories) with confidence score
- **Skill Extraction** — Identifies 200+ technical skills across 5 categories
- **Missing Skills** — Highlights skills gaps based on the predicted role
- **Career Roadmap** — Provides step-by-step career progression guidance
- **Learning Resources** — Curated resources for each missing skill
- **ATS Match Score** — Compares resume against any job description
- **Analysis History** — Browse and revisit past analyses

---

## Architecture

```
resume-classifier/
├── frontend/          # Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui
│   ├── src/app/       # Pages (Home, Analysis, History)
│   ├── src/components/# UI components
│   ├── src/hooks/     # Custom React hooks
│   ├── src/lib/       # API client
│   └── src/types/     # TypeScript types
│
├── backend/           # FastAPI + Python 3.12
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── core/      # Config, database
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # Business logic
│   └── ml/
│       ├── training/  # Model training pipeline
│       ├── inference/  # Prediction module
│       └── models/    # Saved model artifacts
│
└── database/          # Schema & migrations
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm

### 1. Clone & Setup Backend

```bash
cd resume-classifier/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Copy environment config
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
```

### 2. Train the ML Model

1. Download the dataset from [Kaggle — Resume Dataset](https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset)
2. Place `UpdatedResumeDataSet.csv` in `backend/ml/training/data/`
3. Run the training script:

```bash
cd backend
python -m ml.training.train_model
```

This will:
- Clean and preprocess the text data
- Train Logistic Regression, Random Forest, and Linear SVM
- Evaluate all models and select the best one
- Save the model, vectorizer, and label encoder to `ml/models/`

### 3. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### 4. Setup & Start Frontend

```bash
cd resume-classifier/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend available at `http://localhost:3000`.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/resume/upload` | Upload a resume file (PDF/DOCX) |
| `POST` | `/api/resume/classify` | Classify and analyze a resume |
| `POST` | `/api/resume/ats` | Calculate ATS match score |
| `GET`  | `/api/history` | List past analyses |
| `GET`  | `/api/analysis/{id}` | Get detailed analysis |
| `GET`  | `/health` | Health check |

---

## ML Pipeline

| Step | Details |
|------|---------|
| Data Cleaning | Lowercase, remove URLs/emails/special chars, stopword removal, lemmatization (spaCy) |
| Feature Engineering | TF-IDF Vectorization (5000 features, unigrams + bigrams) |
| Models Compared | Logistic Regression, Random Forest, Linear SVM |
| Evaluation | Accuracy, Precision, Recall, F1 Score, Confusion Matrix |
| Output | Best model saved as `.joblib` |

---

## Design System

Dark-mode only, monochrome palette inspired by Linear, Raycast, and Vercel.

| Element | Color |
|---------|-------|
| Background | `#0D0D0D` |
| Cards | `#171717` |
| Borders | `#262626` |
| Primary Text | `#FAFAFA` |
| Muted Text | `#A1A1AA` |
| Accent | `#D4D4D4` |

No gradients, glassmorphism, neon colors, or excessive animations.

---

## Deployment

### Frontend → Vercel

```bash
cd frontend
npx vercel
```

### Backend → Render

1. Push to GitHub
2. Connect to Render
3. Set environment variables
4. Deploy with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Database → Neon PostgreSQL

1. Create a Neon project
2. Get the connection string
3. Update `DATABASE_URL` in backend `.env`

---

## License

MIT
