-- Resume Classifier Database Schema
-- PostgreSQL DDL

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id          VARCHAR(36)     PRIMARY KEY,
    email       VARCHAR(255)    UNIQUE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Resume analyses table
CREATE TABLE IF NOT EXISTS resume_analyses (
    id              VARCHAR(36)     PRIMARY KEY,
    user_id         VARCHAR(36)     REFERENCES users(id) ON DELETE SET NULL,
    filename        VARCHAR(255)    NOT NULL,
    predicted_role  VARCHAR(100),
    confidence      FLOAT,
    score           FLOAT,
    raw_text        TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON resume_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON resume_analyses(created_at DESC);

-- Skill results table
CREATE TABLE IF NOT EXISTS skill_results (
    id              VARCHAR(36)     PRIMARY KEY,
    analysis_id     VARCHAR(36)     NOT NULL REFERENCES resume_analyses(id) ON DELETE CASCADE,
    skill_name      VARCHAR(100)    NOT NULL,
    skill_type      VARCHAR(50)     NOT NULL,  -- 'detected' or 'missing'
    category        VARCHAR(50)                 -- 'language', 'framework', 'database', 'cloud', 'tool'
);

CREATE INDEX IF NOT EXISTS idx_skills_analysis_id ON skill_results(analysis_id);
