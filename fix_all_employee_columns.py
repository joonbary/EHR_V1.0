#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Employee 테이블에 모든 누락된 컬럼 추가
"""

import os
import django
import sys

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection

def add_all_missing_columns():
    """Employee 테이블에 모든 누락된 컬럼 추가"""
    
    with connection.cursor() as cursor:
        try:
            # 현재 컬럼 확인 (PostgreSQL)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'employees_employee'
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print(f"Current columns count: {len(columns)}")
            
            # 필요한 모든 컬럼들 정의 (Employee 모델 기준)
            required_columns = {
                # 익명화 필드들
                'dummy_chinese_name': 'VARCHAR(100)',
                'dummy_name': 'VARCHAR(100)',
                'dummy_mobile': 'VARCHAR(20)',
                'dummy_registered_address': 'TEXT',
                'dummy_residence_address': 'TEXT',
                'dummy_email': 'VARCHAR(254)',
                
                # 일련번호 및 회사 정보
                'no': 'INTEGER',
                'company': 'VARCHAR(10)',
                
                # 직급 정보
                'previous_position': 'VARCHAR(50)',
                'current_position': 'VARCHAR(50)',
                
                # 조직 구조
                'headquarters1': 'VARCHAR(100)',
                'headquarters2': 'VARCHAR(100)',
                'department1': 'VARCHAR(100)',
                'department2': 'VARCHAR(100)',
                'department3': 'VARCHAR(100)',
                'department4': 'VARCHAR(100)',
                'final_department': 'VARCHAR(100)',
                
                # 직군/계열 및 인사 정보
                'job_series': 'VARCHAR(50)',
                'title': 'VARCHAR(50)',
                'responsibility': 'VARCHAR(50)',
                'promotion_level': 'VARCHAR(20)',
                'salary_grade': 'VARCHAR(20)',
                
                # 개인 정보
                'gender': 'VARCHAR(1)',
                'age': 'INTEGER',
                'birth_date': 'DATE',
                
                # 입사 관련 날짜들
                'group_join_date': 'DATE',
                'career_join_date': 'DATE',
                'new_join_date': 'DATE',
                
                # 근무 년수 및 평가
                'promotion_accumulated_years': 'DECIMAL(5,2)',
                'final_evaluation': 'VARCHAR(10)',
                
                # 태그 정보
                'job_tag_name': 'VARCHAR(100)',
                'rank_tag_name': 'VARCHAR(100)',
                
                # 추가 정보
                'education': 'VARCHAR(50)',
                'marital_status': 'VARCHAR(1)',
                'job_family': 'VARCHAR(50)',
                'job_field': 'VARCHAR(50)',
                'classification': 'VARCHAR(50)',
                'current_headcount': 'VARCHAR(10)',
                'detailed_classification': 'VARCHAR(100)',
                'category': 'VARCHAR(50)',
                'diversity_years': 'DECIMAL(5,2)',
                
                # 신인사제도 필드들
                'job_group': 'VARCHAR(20)',
                'job_type': 'VARCHAR(50)',
                'job_role': 'VARCHAR(100)',
                'growth_level': 'INTEGER',
                'new_position': 'VARCHAR(50)',
                'grade_level': 'INTEGER',
                'employment_type': 'VARCHAR(20)',
                'employment_status': 'VARCHAR(20)',
                
                # AI 예측 관련 추가 필드들
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
            
            added_count = 0
            for col_name, col_type in required_columns.items():
                if col_name not in columns:
                    try:
                        # 컬럼 추가
                        cursor.execute(f"ALTER TABLE employees_employee ADD COLUMN {col_name} {col_type} NULL")
                        print(f"+ Added {col_name} ({col_type})")
                        
                        # 기본값 설정
                        if col_type == 'INTEGER':
                            default_value = 0
                        elif col_type.startswith('DECIMAL'):
                            default_value = 0.0
                        elif col_type == 'BOOLEAN':
                            default_value = False
                        elif col_type == 'DATE':
                            default_value = None  # DATE는 NULL로 둠
                        elif 'email' in col_name.lower():
                            default_value = 'dummy@example.com'
                        else:
                            default_value = '익명화'
                        
                        if default_value is not None:
                            cursor.execute(f"UPDATE employees_employee SET {col_name} = %s WHERE {col_name} IS NULL", [default_value])
                        
                        added_count += 1
                    except Exception as e:
                        print(f"x Error adding {col_name}: {e}")
                else:
                    print(f"- {col_name} already exists")
            
            print(f"\nAdded {added_count} columns")
            print(f"Total columns now: {len(columns) + added_count}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_all_missing_columns()