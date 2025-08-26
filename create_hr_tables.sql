-- HR 관리 시스템 테이블 생성 스크립트

-- 1. 직군 테이블
CREATE TABLE IF NOT EXISTS hr_jobfamily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 직종 테이블
CREATE TABLE IF NOT EXISTS hr_jobcategory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    job_family_id INTEGER REFERENCES hr_jobfamily(id)
);
