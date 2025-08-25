#!/usr/bin/env python
"""
인재 관리 테이블 직접 생성
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection

def create_tables():
    """테이블 직접 생성"""
    print("인재 관리 테이블 생성 시작...")
    
    with connection.cursor() as cursor:
        # TalentCategory 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_talentcategory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                category_code VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                criteria TEXT DEFAULT '{}',
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] employees_talentcategory 테이블 생성")
        
        # TalentPool 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_talentpool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL REFERENCES employees_employee(id),
                category_id INTEGER NOT NULL REFERENCES employees_talentcategory(id),
                ai_analysis_result_id INTEGER REFERENCES airiss_aianalysisresult(id),
                ai_score REAL NOT NULL,
                confidence_level REAL NOT NULL,
                status VARCHAR(20) DEFAULT 'PENDING',
                review_date DATE,
                valid_until DATE,
                strengths TEXT DEFAULT '[]',
                development_areas TEXT DEFAULT '[]',
                recommendations TEXT DEFAULT '[]',
                notes TEXT,
                added_by_id INTEGER REFERENCES auth_user(id),
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_by_id INTEGER REFERENCES auth_user(id),
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_id, category_id)
            )
        """)
        print("[OK] employees_talentpool 테이블 생성")
        
        # PromotionCandidate 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_promotioncandidate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL REFERENCES employees_employee(id),
                talent_pool_id INTEGER REFERENCES employees_talentpool(id),
                current_position VARCHAR(50) NOT NULL,
                target_position VARCHAR(50) NOT NULL,
                readiness_level VARCHAR(20) NOT NULL,
                expected_promotion_date DATE,
                performance_score REAL NOT NULL,
                potential_score REAL NOT NULL,
                ai_recommendation_score REAL NOT NULL,
                development_plan TEXT DEFAULT '{}',
                completed_requirements TEXT DEFAULT '[]',
                pending_requirements TEXT DEFAULT '[]',
                is_active BOOLEAN DEFAULT 1,
                review_notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reviewed_by_id INTEGER REFERENCES auth_user(id),
                reviewed_at DATETIME,
                UNIQUE(employee_id, target_position)
            )
        """)
        print("[OK] employees_promotioncandidate 테이블 생성")
        
        # RetentionRisk 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_retentionrisk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL REFERENCES employees_employee(id),
                talent_pool_id INTEGER REFERENCES employees_talentpool(id),
                risk_level VARCHAR(20) NOT NULL,
                risk_score REAL NOT NULL,
                risk_factors TEXT DEFAULT '[]',
                retention_strategy TEXT NOT NULL,
                action_items TEXT DEFAULT '[]',
                action_status VARCHAR(20) DEFAULT 'PENDING',
                intervention_date DATE,
                outcome TEXT,
                is_retained BOOLEAN,
                identified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                assigned_to_id INTEGER REFERENCES auth_user(id)
            )
        """)
        print("[OK] employees_retentionrisk 테이블 생성")
        
        # TalentDevelopment 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_talentdevelopment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL REFERENCES employees_employee(id),
                talent_pool_id INTEGER REFERENCES employees_talentpool(id),
                development_goal VARCHAR(200) NOT NULL,
                current_state TEXT NOT NULL,
                target_state TEXT NOT NULL,
                activities TEXT DEFAULT '[]',
                timeline TEXT DEFAULT '{}',
                resources_needed TEXT DEFAULT '[]',
                progress_percentage INTEGER DEFAULT 0,
                milestones TEXT DEFAULT '[]',
                completed_activities TEXT DEFAULT '[]',
                priority VARCHAR(20) DEFAULT 'MEDIUM',
                is_active BOOLEAN DEFAULT 1,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                created_by_id INTEGER REFERENCES auth_user(id),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] employees_talentdevelopment 테이블 생성")
        
        # 인덱스 생성
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS employees_talentpool_category_status_idx 
            ON employees_talentpool(category_id, status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS employees_talentpool_ai_score_idx 
            ON employees_talentpool(ai_score)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS employees_talentpool_valid_until_idx 
            ON employees_talentpool(valid_until)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS employees_retentionrisk_risk_level_action_status_idx 
            ON employees_retentionrisk(risk_level, action_status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS employees_retentionrisk_risk_score_idx 
            ON employees_retentionrisk(risk_score)
        """)
        print("[OK] 인덱스 생성 완료")
        
        connection.commit()
        print("\n모든 테이블이 성공적으로 생성되었습니다!")

if __name__ == "__main__":
    create_tables()