-- JobRole 테이블에 직접 데이터 삽입
INSERT INTO job_profiles_jobrole (id, name, code, description, is_active, created_at, updated_at)
VALUES 
    (gen_random_uuid(), '시스템기획', 'SYS_PLAN', 'IT 시스템 기획 업무', true, NOW(), NOW()),
    (gen_random_uuid(), '시스템개발', 'SYS_DEV', 'IT 시스템 개발 업무', true, NOW(), NOW()),
    (gen_random_uuid(), 'HRM', 'HRM', '인사 관리 업무', true, NOW(), NOW()),
    (gen_random_uuid(), '여신영업', 'LOAN_SALES', '기업 여신 영업 업무', true, NOW(), NOW())
ON CONFLICT DO NOTHING;