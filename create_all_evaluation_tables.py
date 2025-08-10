"""
Railway 서버에 모든 평가 관련 테이블 생성
"""
import os
import sys
import django
from datetime import date

# UTF-8 인코딩 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection

def create_all_evaluation_tables():
    """모든 평가 관련 테이블 생성"""
    
    tables = [
        # 이미 생성된 테이블
        ('evaluations_evaluationperiod', 'SKIP - Already exists'),
        
        # Task 테이블
        ('evaluations_task', """
            CREATE TABLE IF NOT EXISTS evaluations_task (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees_employee(id) ON DELETE CASCADE,
                evaluation_period_id INTEGER REFERENCES evaluations_evaluationperiod(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                contribution_type VARCHAR(20) DEFAULT 'operation',
                weight DECIMAL(5,2),
                contribution_method VARCHAR(20) DEFAULT 'leading',
                contribution_scope VARCHAR(20) DEFAULT 'independent',
                target_value DECIMAL(15,2),
                target_unit VARCHAR(20),
                actual_value DECIMAL(15,2),
                achievement_rate DECIMAL(5,2),
                base_score DECIMAL(3,1),
                final_score DECIMAL(3,1),
                last_checkin_date TIMESTAMP WITH TIME ZONE,
                checkin_count INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'PLANNED',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """),
        
        # ContributionEvaluation 테이블
        ('evaluations_contributionevaluation', """
            CREATE TABLE IF NOT EXISTS evaluations_contributionevaluation (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees_employee(id) ON DELETE CASCADE,
                evaluation_period_id INTEGER REFERENCES evaluations_evaluationperiod(id) ON DELETE CASCADE,
                evaluator_id INTEGER REFERENCES employees_employee(id) ON DELETE SET NULL,
                contribution_score DECIMAL(3,1),
                total_score DECIMAL(5,2),
                is_achieved BOOLEAN DEFAULT FALSE,
                evaluation_date DATE,
                status VARCHAR(20) DEFAULT 'DRAFT',
                comments TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """),
        
        # ExpertiseEvaluation 테이블
        ('evaluations_expertiseevaluation', """
            CREATE TABLE IF NOT EXISTS evaluations_expertiseevaluation (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees_employee(id) ON DELETE CASCADE,
                evaluation_period_id INTEGER REFERENCES evaluations_evaluationperiod(id) ON DELETE CASCADE,
                evaluator_id INTEGER REFERENCES employees_employee(id) ON DELETE SET NULL,
                hard_skill_level VARCHAR(20),
                soft_skill_level VARCHAR(20),
                expertise_score DECIMAL(3,1),
                total_score DECIMAL(5,2),
                is_achieved BOOLEAN DEFAULT FALSE,
                evaluation_date DATE,
                status VARCHAR(20) DEFAULT 'DRAFT',
                comments TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """),
        
        # ImpactEvaluation 테이블
        ('evaluations_impactevaluation', """
            CREATE TABLE IF NOT EXISTS evaluations_impactevaluation (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees_employee(id) ON DELETE CASCADE,
                evaluation_period_id INTEGER REFERENCES evaluations_evaluationperiod(id) ON DELETE CASCADE,
                evaluator_id INTEGER REFERENCES employees_employee(id) ON DELETE SET NULL,
                impact_level VARCHAR(20),
                leadership_type VARCHAR(20),
                values_type VARCHAR(20),
                impact_score DECIMAL(3,1),
                total_score DECIMAL(5,2),
                is_achieved BOOLEAN DEFAULT FALSE,
                evaluation_date DATE,
                status VARCHAR(20) DEFAULT 'DRAFT',
                comments TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """),
        
        # ComprehensiveEvaluation 테이블
        ('evaluations_comprehensiveevaluation', """
            CREATE TABLE IF NOT EXISTS evaluations_comprehensiveevaluation (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees_employee(id) ON DELETE CASCADE,
                evaluation_period_id INTEGER REFERENCES evaluations_evaluationperiod(id) ON DELETE CASCADE,
                contribution_evaluation_id INTEGER,
                expertise_evaluation_id INTEGER,
                impact_evaluation_id INTEGER,
                contribution_score DECIMAL(3,1),
                expertise_score DECIMAL(3,1),
                impact_score DECIMAL(3,1),
                total_score DECIMAL(5,2),
                weighted_score DECIMAL(5,2),
                preliminary_grade VARCHAR(3),
                final_grade VARCHAR(3),
                is_calibrated BOOLEAN DEFAULT FALSE,
                calibration_adjustment DECIMAL(5,2) DEFAULT 0,
                manager_feedback TEXT,
                hr_feedback TEXT,
                employee_feedback TEXT,
                status VARCHAR(20) DEFAULT 'DRAFT',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """),
        
        # CalibrationSession 테이블
        ('evaluations_calibrationsession', """
            CREATE TABLE IF NOT EXISTS evaluations_calibrationsession (
                id SERIAL PRIMARY KEY,
                evaluation_period_id INTEGER REFERENCES evaluations_evaluationperiod(id) ON DELETE CASCADE,
                session_name VARCHAR(200),
                session_date DATE,
                department VARCHAR(100),
                participants TEXT,
                status VARCHAR(20) DEFAULT 'SCHEDULED',
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """),
        
        # TaskCheckin 테이블 (체크인 이력)
        ('evaluations_taskcheckin', """
            CREATE TABLE IF NOT EXISTS evaluations_taskcheckin (
                id SERIAL PRIMARY KEY,
                task_id INTEGER REFERENCES evaluations_task(id) ON DELETE CASCADE,
                checkin_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                progress_note TEXT,
                progress_percentage INTEGER DEFAULT 0,
                created_by_id INTEGER REFERENCES employees_employee(id) ON DELETE SET NULL
            );
        """),
        
        # GrowthLevel 테이블
        ('evaluations_growthlevel', """
            CREATE TABLE IF NOT EXISTS evaluations_growthlevel (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees_employee(id) ON DELETE CASCADE,
                evaluation_period_id INTEGER REFERENCES evaluations_evaluationperiod(id) ON DELETE CASCADE,
                current_level VARCHAR(20),
                target_level VARCHAR(20),
                progress_percentage DECIMAL(5,2) DEFAULT 0,
                certification_status VARCHAR(20),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
    ]
    
    with connection.cursor() as cursor:
        for table_name, sql in tables:
            try:
                if sql == 'SKIP - Already exists':
                    print(f"⏭️  {table_name}: Skipping (already created)")
                    continue
                    
                # 테이블 존재 확인
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table_name}'
                    );
                """)
                
                exists = cursor.fetchone()[0]
                
                if not exists:
                    cursor.execute(sql)
                    print(f"✅ {table_name}: Created successfully")
                else:
                    print(f"⚪ {table_name}: Already exists")
                    
            except Exception as e:
                print(f"❌ {table_name}: Error - {e}")
    
    print("\n" + "="*60)
    print("테이블 생성 완료!")
    print("="*60)

def verify_tables():
    """생성된 테이블 확인"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'evaluations_%'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\n📊 평가 관련 테이블 목록:")
        for table in tables:
            print(f"  ✓ {table[0]}")
        print(f"\n총 {len(tables)}개 테이블")

if __name__ == "__main__":
    print("="*60)
    print("Railway 평가 시스템 테이블 생성")
    print("="*60)
    
    try:
        # 1. 테이블 생성
        create_all_evaluation_tables()
        
        # 2. 검증
        verify_tables()
        
        print("\n✅ 모든 작업 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()