#!/usr/bin/env python
"""
이직 위험도 예측 모듈을 위한 Employee 테이블 컬럼 수정 스크립트
"""

import os
import django
import sys

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection

def fix_employee_table():
    """Employee 테이블 스키마 수정"""
    
    with connection.cursor() as cursor:
        # 필요한 컬럼들이 존재하는지 확인하고 없으면 추가
        missing_columns = []
        
        # 테이블의 현재 컬럼 조회 (SQLite)
        cursor.execute("PRAGMA table_info(employees_employee)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"기존 컬럼들: {existing_columns}")
        
        # 필요한 컬럼들 정의 (모델에서 사용되는 컬럼들)
        required_columns = {
            'dummy_chinese_name': 'VARCHAR(100)',
            'age': 'INTEGER',
            'tenure_years': 'DECIMAL(5,2)',
            'last_promotion_date': 'DATE',
            'performance_score': 'DECIMAL(3,2)',
            'attendance_rate': 'DECIMAL(5,2)',
            'training_hours': 'INTEGER',
            'overtime_hours': 'DECIMAL(8,2)',
            'commute_distance': 'DECIMAL(8,2)',
            'work_life_balance_score': 'DECIMAL(3,2)',
            'job_satisfaction_score': 'DECIMAL(3,2)',
            'career_development_score': 'DECIMAL(3,2)',
            'manager_rating': 'DECIMAL(3,2)',
            'peer_feedback_score': 'DECIMAL(3,2)',
            'innovation_projects': 'INTEGER',
            'certifications_count': 'INTEGER',
            'mentoring_involvement': 'BOOLEAN',
            'cross_functional_experience': 'BOOLEAN',
            'leadership_roles': 'INTEGER',
            'voluntary_turnover_risk': 'DECIMAL(3,2)',
            'market_demand_level': 'DECIMAL(3,2)',
            'internal_mobility_interest': 'DECIMAL(3,2)',
            'compensation_satisfaction': 'DECIMAL(3,2)',
            'benefits_utilization': 'DECIMAL(3,2)',
            'flexible_work_usage': 'DECIMAL(3,2)',
            'team_collaboration_score': 'DECIMAL(3,2)',
            'stress_level_indicator': 'DECIMAL(3,2)',
            'personal_development_budget': 'DECIMAL(10,2)',
            'recognition_count': 'INTEGER'
        }
        
        # 누락된 컬럼 찾기
        for column, column_type in required_columns.items():
            if column not in existing_columns:
                missing_columns.append((column, column_type))
        
        print(f"누락된 컬럼들: {missing_columns}")
        
        # 누락된 컬럼들 추가
        for column, column_type in missing_columns:
            try:
                sql = f"ALTER TABLE employees_employee ADD COLUMN {column} {column_type} NULL"
                print(f"실행: {sql}")
                cursor.execute(sql)
                print(f"✓ {column} 컬럼 추가 성공")
            except Exception as e:
                print(f"✗ {column} 컬럼 추가 실패: {e}")
                # 컬럼이 이미 존재할 수 있으므로 계속 진행
                continue
        
        # 더미 데이터로 NULL 값들 채우기
        try:
            cursor.execute("""
                UPDATE employees_employee 
                SET 
                    dummy_chinese_name = COALESCE(dummy_chinese_name, '익명화'),
                    age = COALESCE(age, 30),
                    tenure_years = COALESCE(tenure_years, 2.5),
                    performance_score = COALESCE(performance_score, 3.5),
                    attendance_rate = COALESCE(attendance_rate, 95.0),
                    training_hours = COALESCE(training_hours, 40),
                    overtime_hours = COALESCE(overtime_hours, 10.0),
                    commute_distance = COALESCE(commute_distance, 20.0),
                    work_life_balance_score = COALESCE(work_life_balance_score, 3.5),
                    job_satisfaction_score = COALESCE(job_satisfaction_score, 3.5),
                    career_development_score = COALESCE(career_development_score, 3.0),
                    manager_rating = COALESCE(manager_rating, 3.5),
                    peer_feedback_score = COALESCE(peer_feedback_score, 3.5),
                    innovation_projects = COALESCE(innovation_projects, 2),
                    certifications_count = COALESCE(certifications_count, 1),
                    mentoring_involvement = COALESCE(mentoring_involvement, false),
                    cross_functional_experience = COALESCE(cross_functional_experience, false),
                    leadership_roles = COALESCE(leadership_roles, 0),
                    voluntary_turnover_risk = COALESCE(voluntary_turnover_risk, 0.3),
                    market_demand_level = COALESCE(market_demand_level, 0.5),
                    internal_mobility_interest = COALESCE(internal_mobility_interest, 0.4),
                    compensation_satisfaction = COALESCE(compensation_satisfaction, 3.5),
                    benefits_utilization = COALESCE(benefits_utilization, 0.7),
                    flexible_work_usage = COALESCE(flexible_work_usage, 0.5),
                    team_collaboration_score = COALESCE(team_collaboration_score, 3.5),
                    stress_level_indicator = COALESCE(stress_level_indicator, 0.4),
                    personal_development_budget = COALESCE(personal_development_budget, 500000.00),
                    recognition_count = COALESCE(recognition_count, 3)
                WHERE 
                    dummy_chinese_name IS NULL OR age IS NULL OR tenure_years IS NULL OR 
                    performance_score IS NULL OR attendance_rate IS NULL OR training_hours IS NULL OR
                    overtime_hours IS NULL OR commute_distance IS NULL OR work_life_balance_score IS NULL OR
                    job_satisfaction_score IS NULL OR career_development_score IS NULL OR manager_rating IS NULL OR
                    peer_feedback_score IS NULL OR innovation_projects IS NULL OR certifications_count IS NULL OR
                    mentoring_involvement IS NULL OR cross_functional_experience IS NULL OR leadership_roles IS NULL OR
                    voluntary_turnover_risk IS NULL OR market_demand_level IS NULL OR internal_mobility_interest IS NULL OR
                    compensation_satisfaction IS NULL OR benefits_utilization IS NULL OR flexible_work_usage IS NULL OR
                    team_collaboration_score IS NULL OR stress_level_indicator IS NULL OR personal_development_budget IS NULL OR
                    recognition_count IS NULL;
            """)
            print("✓ 더미 데이터 업데이트 완료")
        except Exception as e:
            print(f"✗ 더미 데이터 업데이트 실패: {e}")
        
        print("Employee 테이블 스키마 수정 완료!")

if __name__ == "__main__":
    try:
        fix_employee_table()
    except Exception as e:
        print(f"스크립트 실행 오류: {e}")
        sys.exit(1)