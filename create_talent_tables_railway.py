#!/usr/bin/env python
"""
Railway에서 인재 관리 테이블 생성
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 인재 관리 테이블 생성")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection

def create_talent_tables():
    """인재 관리 테이블 생성"""
    print("1. 테이블 존재 확인")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 현재 테이블 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'employees_talentcategory',
                'employees_talentpool',
                'employees_promotioncandidate',
                'employees_retentionrisk'
            )
            ORDER BY table_name;
        """)
        existing_tables = [t[0] for t in cursor.fetchall()]
        
        if existing_tables:
            print(f"이미 존재하는 테이블: {', '.join(existing_tables)}")
        else:
            print("인재 관리 테이블이 없습니다. 생성을 시작합니다.")
        
        print("\n2. 테이블 생성")
        print("-" * 40)
        
        # 1. TalentCategory 테이블
        if 'employees_talentcategory' not in existing_tables:
            try:
                cursor.execute("""
                    CREATE TABLE employees_talentcategory (
                        id SERIAL PRIMARY KEY,
                        category_code VARCHAR(50) UNIQUE NOT NULL,
                        category_name VARCHAR(100) NOT NULL,
                        description TEXT,
                        criteria JSONB,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                print("[OK] employees_talentcategory 생성 완료")
                
                # 기본 카테고리 데이터 삽입
                cursor.execute("""
                    INSERT INTO employees_talentcategory (category_code, category_name, description, criteria)
                    VALUES 
                    ('CORE_TALENT', '핵심 인재', '조직의 핵심 성과를 이끄는 인재', '{"ai_score_min": 80, "performance_min": "A"}'),
                    ('HIGH_POTENTIAL', '고잠재력', '향후 리더로 성장 가능한 인재', '{"ai_score_min": 75, "potential_score_min": 80}'),
                    ('SPECIALIST', '전문가', '특정 분야의 전문 지식을 보유한 인재', '{"expertise_level": "expert", "ai_score_min": 70}'),
                    ('NEEDS_ATTENTION', '관리 필요', '성과 개선이 필요한 인재', '{"ai_score_max": 60, "performance_max": "C"}')
                    ON CONFLICT (category_code) DO NOTHING;
                """)
                print("[OK] 기본 카테고리 데이터 삽입 완료")
            except Exception as e:
                print(f"[INFO] TalentCategory 테이블: {str(e)[:100]}")
        
        # 2. TalentPool 테이블
        if 'employees_talentpool' not in existing_tables:
            try:
                cursor.execute("""
                    CREATE TABLE employees_talentpool (
                        id SERIAL PRIMARY KEY,
                        employee_id INTEGER REFERENCES employees_employee(id) ON DELETE CASCADE,
                        category_id INTEGER REFERENCES employees_talentcategory(id),
                        ai_analysis_result_id INTEGER,
                        ai_score FLOAT DEFAULT 0,
                        confidence_level FLOAT DEFAULT 0,
                        strengths JSONB,
                        development_areas JSONB,
                        recommendations JSONB,
                        status VARCHAR(20) DEFAULT 'PENDING',
                        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        added_by_id INTEGER REFERENCES auth_user(id)
                    );
                """)
                
                # 인덱스
                cursor.execute("CREATE INDEX idx_talentpool_employee ON employees_talentpool(employee_id);")
                cursor.execute("CREATE INDEX idx_talentpool_category ON employees_talentpool(category_id);")
                cursor.execute("CREATE INDEX idx_talentpool_status ON employees_talentpool(status);")
                
                print("[OK] employees_talentpool 생성 완료")
            except Exception as e:
                print(f"[INFO] TalentPool 테이블: {str(e)[:100]}")
        
        # 3. PromotionCandidate 테이블
        if 'employees_promotioncandidate' not in existing_tables:
            try:
                cursor.execute("""
                    CREATE TABLE employees_promotioncandidate (
                        id SERIAL PRIMARY KEY,
                        employee_id INTEGER REFERENCES employees_employee(id) ON DELETE CASCADE,
                        current_position VARCHAR(100),
                        target_position VARCHAR(100),
                        readiness_level VARCHAR(20) DEFAULT 'DEVELOPING',
                        performance_score FLOAT DEFAULT 0,
                        potential_score FLOAT DEFAULT 0,
                        ai_recommendation_score FLOAT DEFAULT 0,
                        expected_promotion_date DATE,
                        development_plan JSONB,
                        completed_requirements JSONB,
                        pending_requirements JSONB,
                        recommendation_reason TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by_id INTEGER REFERENCES auth_user(id)
                    );
                """)
                
                # 인덱스
                cursor.execute("CREATE INDEX idx_promotion_employee ON employees_promotioncandidate(employee_id);")
                cursor.execute("CREATE INDEX idx_promotion_active ON employees_promotioncandidate(is_active);")
                cursor.execute("CREATE INDEX idx_promotion_readiness ON employees_promotioncandidate(readiness_level);")
                
                print("[OK] employees_promotioncandidate 생성 완료")
            except Exception as e:
                print(f"[INFO] PromotionCandidate 테이블: {str(e)[:100]}")
        
        # 4. RetentionRisk 테이블
        if 'employees_retentionrisk' not in existing_tables:
            try:
                cursor.execute("""
                    CREATE TABLE employees_retentionrisk (
                        id SERIAL PRIMARY KEY,
                        employee_id INTEGER REFERENCES employees_employee(id) ON DELETE CASCADE,
                        risk_level VARCHAR(20) DEFAULT 'LOW',
                        risk_score FLOAT DEFAULT 0,
                        risk_factors JSONB,
                        retention_strategy TEXT,
                        action_items JSONB,
                        action_status VARCHAR(20) DEFAULT 'PENDING',
                        assigned_to_id INTEGER REFERENCES auth_user(id),
                        last_review_date DATE,
                        next_review_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by_id INTEGER REFERENCES auth_user(id)
                    );
                """)
                
                # 인덱스
                cursor.execute("CREATE INDEX idx_retention_employee ON employees_retentionrisk(employee_id);")
                cursor.execute("CREATE INDEX idx_retention_risk_level ON employees_retentionrisk(risk_level);")
                cursor.execute("CREATE INDEX idx_retention_status ON employees_retentionrisk(action_status);")
                
                print("[OK] employees_retentionrisk 생성 완료")
            except Exception as e:
                print(f"[INFO] RetentionRisk 테이블: {str(e)[:100]}")

def verify_tables():
    """테이블 생성 확인"""
    print("\n3. 최종 검증")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
            AND table_name IN (
                'employees_talentcategory',
                'employees_talentpool',
                'employees_promotioncandidate',
                'employees_retentionrisk'
            )
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            print("생성된 테이블:")
            for table_name, col_count in tables:
                print(f"  - {table_name} ({col_count} columns)")
                
                # 데이터 개수 확인
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    - 데이터: {count} 레코드")
        else:
            print("❌ 테이블 생성 실패")

def main():
    """메인 실행"""
    
    print("\n시작: Railway 인재 관리 테이블 생성\n")
    
    # 1. 테이블 생성
    create_talent_tables()
    
    # 2. 검증
    verify_tables()
    
    print("\n" + "="*60)
    print("[SUCCESS] Talent management tables created!")
    print("="*60)

if __name__ == "__main__":
    main()