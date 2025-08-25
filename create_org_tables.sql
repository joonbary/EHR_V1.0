-- OrganizationStructure 테이블 생성 SQL
-- Railway PostgreSQL에서 직접 실행

-- 1. OrganizationStructure 테이블
CREATE TABLE IF NOT EXISTS employees_organizationstructure (
    id SERIAL PRIMARY KEY,
    org_code VARCHAR(50) UNIQUE NOT NULL,
    org_name VARCHAR(100) NOT NULL,
    org_level INTEGER NOT NULL DEFAULT 1,
    parent_id INTEGER,
    full_path VARCHAR(500) DEFAULT '',
    group_name VARCHAR(100) DEFAULT '',
    company_name VARCHAR(100) DEFAULT '',
    headquarters_name VARCHAR(100) DEFAULT '',
    department_name VARCHAR(100) DEFAULT '',
    team_name VARCHAR(100) DEFAULT '',
    description TEXT DEFAULT '',
    establishment_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    leader_id INTEGER,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER
);

-- 외래키 제약 조건
ALTER TABLE employees_organizationstructure 
ADD CONSTRAINT fk_org_parent 
FOREIGN KEY (parent_id) 
REFERENCES employees_organizationstructure(id) 
ON DELETE CASCADE;

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_org_code ON employees_organizationstructure(org_code);
CREATE INDEX IF NOT EXISTS idx_org_level_status ON employees_organizationstructure(org_level, status);
CREATE INDEX IF NOT EXISTS idx_org_parent ON employees_organizationstructure(parent_id);

-- 2. OrganizationUploadHistory 테이블
CREATE TABLE IF NOT EXISTS employees_organizationuploadhistory (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    total_rows INTEGER DEFAULT 0,
    processed_rows INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    error_details JSONB DEFAULT '[]'::jsonb,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    uploaded_by_id INTEGER,
    options JSONB DEFAULT '{}'::jsonb
);

-- 3. EmployeeOrganizationMapping 테이블
CREATE TABLE IF NOT EXISTS employees_employeeorganizationmapping (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    organization_id INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT TRUE,
    role VARCHAR(50),
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Employee 테이블에 organization_id 컬럼 추가
ALTER TABLE employees_employee 
ADD COLUMN IF NOT EXISTS organization_id INTEGER;

-- 5. 마이그레이션 레코드 추가 (이미 적용된 것으로 표시)
INSERT INTO django_migrations (app, name, applied) 
VALUES ('employees', '0002_add_missing_extended_fields', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

INSERT INTO django_migrations (app, name, applied) 
VALUES ('employees', '0003_organizationstructure_employeeorganizationmapping_and_more', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- 6. 초기 샘플 데이터
INSERT INTO employees_organizationstructure 
(org_code, org_name, org_level, parent_id, status, sort_order, group_name, full_path) 
VALUES 
('GRP001', 'OK금융그룹', 1, NULL, 'active', 1, 'OK금융그룹', 'OK금융그룹')
ON CONFLICT (org_code) DO NOTHING;

INSERT INTO employees_organizationstructure 
(org_code, org_name, org_level, parent_id, status, sort_order, group_name, company_name, full_path) 
VALUES 
('COM001', 'OK저축은행', 2, 
 (SELECT id FROM employees_organizationstructure WHERE org_code='GRP001'),
 'active', 1, 'OK금융그룹', 'OK저축은행', 'OK금융그룹 > OK저축은행')
ON CONFLICT (org_code) DO NOTHING;

INSERT INTO employees_organizationstructure 
(org_code, org_name, org_level, parent_id, status, sort_order, 
 group_name, company_name, headquarters_name, full_path) 
VALUES 
('HQ001', '리테일본부', 3,
 (SELECT id FROM employees_organizationstructure WHERE org_code='COM001'),
 'active', 1, 'OK금융그룹', 'OK저축은행', '리테일본부',
 'OK금융그룹 > OK저축은행 > 리테일본부')
ON CONFLICT (org_code) DO NOTHING;