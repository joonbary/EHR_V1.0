#!/usr/bin/env python
"""
Railway 데이터베이스 리셋 및 재구성 스크립트
"""
import os
import sys
import django
from django.db import connection
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def reset_database():
    """데이터베이스를 완전히 리셋"""
    print("=" * 60)
    print("데이터베이스 리셋 시작")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # django_migrations 테이블의 HR 관련 레코드만 삭제
        try:
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'hr'
            """)
            print("HR 마이그레이션 레코드 삭제 완료")
        except Exception as e:
            print(f"HR 마이그레이션 레코드 삭제 중 오류 (무시 가능): {e}")
        
        # HR 테이블들 삭제 (있다면)
        hr_tables = [
            'hr_jobfamily', 'hr_jobcategory', 'hr_jobposition', 'hr_jobgrade',
            'hr_salarygrade', 'hr_basesalary', 'hr_performancebonus', 'hr_allowance',
            'hr_careerhistory', 'hr_promotionhistory', 'hr_education', 'hr_certification',
            'hr_training', 'hr_performanceevaluation', 'hr_competencyevaluation',
            'hr_benefit', 'hr_employeebenefit', 'hr_monthlysalary'
        ]
        
        for table in hr_tables:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                print(f"  - {table} 삭제")
            except Exception as e:
                print(f"  - {table} 삭제 중 오류 (무시 가능): {e}")

def create_hr_tables():
    """HR 테이블 생성"""
    print("\nHR 테이블 생성 중...")
    
    try:
        # HR 마이그레이션 생성
        call_command('makemigrations', 'hr', '--skip-checks', '--noinput')
        print("HR 마이그레이션 파일 생성 완료")
    except Exception as e:
        print(f"HR 마이그레이션 생성 중 오류 (무시 가능): {e}")
    
    try:
        # HR 마이그레이션만 실행
        call_command('migrate', 'hr', '--skip-checks')
        print("HR 마이그레이션 실행 완료")
    except Exception as e:
        print(f"HR 마이그레이션 실행 중 오류: {e}")
        
        # 강제 테이블 생성 시도
        print("\n강제 테이블 생성 시도...")
        with connection.cursor() as cursor:
            # JobFamily 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_jobfamily (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(10) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    description TEXT,
                    sort_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # JobCategory 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_jobcategory (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(10) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    description TEXT,
                    job_family_id INTEGER REFERENCES hr_jobfamily(id) ON DELETE CASCADE,
                    sort_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # JobPosition 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_jobposition (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(10) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    description TEXT,
                    required_skills TEXT,
                    job_category_id INTEGER REFERENCES hr_jobcategory(id) ON DELETE CASCADE,
                    sort_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # JobGrade 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_jobgrade (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(10) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    level INTEGER NOT NULL,
                    min_experience_years INTEGER DEFAULT 0,
                    sort_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # SalaryGrade 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_salarygrade (
                    id SERIAL PRIMARY KEY,
                    grade_code VARCHAR(10) UNIQUE NOT NULL,
                    grade_name VARCHAR(50) NOT NULL,
                    min_amount DECIMAL(12,0) NOT NULL,
                    max_amount DECIMAL(12,0) NOT NULL,
                    mid_point DECIMAL(12,0),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 추가 테이블들 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_performancebonus (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    bonus_amount DECIMAL(12,0) NOT NULL,
                    bonus_type VARCHAR(50),
                    payment_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_promotionhistory (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    from_grade_id INTEGER,
                    to_grade_id INTEGER,
                    promotion_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_training (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    training_name VARCHAR(200),
                    start_date DATE NOT NULL,
                    end_date DATE,
                    hours INTEGER,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_performanceevaluation (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    evaluator_id INTEGER,
                    evaluation_period VARCHAR(50),
                    rating VARCHAR(10),
                    is_finalized BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_benefit (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(10) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_employeebenefit (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    benefit_id INTEGER REFERENCES hr_benefit(id) ON DELETE CASCADE,
                    enrollment_date DATE NOT NULL,
                    usage_amount DECIMAL(12,0),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_monthlysalary (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    gross_amount DECIMAL(12,0),
                    net_amount DECIMAL(12,0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_allowance (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    allowance_type VARCHAR(50),
                    amount DECIMAL(12,0),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_education (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    degree VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_certification (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    certification_name VARCHAR(200),
                    issue_date DATE,
                    is_valid BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # BaseSalary 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_basesalary (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    base_amount DECIMAL(12,0) NOT NULL,
                    effective_date DATE NOT NULL,
                    end_date DATE,
                    salary_grade_id INTEGER REFERENCES hr_salarygrade(id) ON DELETE SET NULL,
                    job_grade_id INTEGER REFERENCES hr_jobgrade(id) ON DELETE SET NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            print("기본 HR 테이블 생성 완료")

def main():
    try:
        reset_database()
        create_hr_tables()
        
        print("\n" + "=" * 60)
        print("HR 테이블 구성 완료!")
        print("=" * 60)
        
        # 테이블 확인
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename LIKE 'hr_%'
            """)
            count = cursor.fetchone()[0]
            print(f"\n생성된 HR 테이블 수: {count}개")
            
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()