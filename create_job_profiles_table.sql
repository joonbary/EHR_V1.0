-- JobProfile 테이블 생성 SQL
CREATE TABLE IF NOT EXISTS job_profiles_jobprofile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_responsibility TEXT NOT NULL,
    qualification TEXT NOT NULL,
    basic_skills JSONB DEFAULT '[]'::jsonb,
    applied_skills JSONB DEFAULT '[]'::jsonb,
    growth_path TEXT DEFAULT '',
    related_certifications JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    updated_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    job_role_id UUID UNIQUE REFERENCES job_profiles_jobrole(id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS job_profiles_jobprofile_created_by_id_idx ON job_profiles_jobprofile(created_by_id);
CREATE INDEX IF NOT EXISTS job_profiles_jobprofile_updated_by_id_idx ON job_profiles_jobprofile(updated_by_id);
CREATE INDEX IF NOT EXISTS job_profiles_jobprofile_job_role_id_idx ON job_profiles_jobprofile(job_role_id);