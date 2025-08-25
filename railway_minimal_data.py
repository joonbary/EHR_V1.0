#!/usr/bin/env python
"""
Railway 최소 데이터 생성 - 실제 DB 스키마에 맞춤
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User

print("="*60)
print("Railway 최소 데이터 생성")
print("="*60)

def create_employees_minimal():
    """최소 필드만으로 Employee 생성"""
    print("\n1. Employee 데이터 생성 (Railway 스키마)")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # Railway DB의 실제 필드만 사용
        # id, name, email, department, position, hire_date, phone, address, 
        # emergency_contact, emergency_phone, no
        
        for i in range(1, 11):
            try:
                # Railway DB의 필수 필드 포함
                cursor.execute("""
                    INSERT INTO employees_employee 
                    (no, name, email, department, position, hire_date, phone, 
                     address, emergency_contact, emergency_phone, 
                     job_group, job_type, job_role, growth_level, new_position, grade_level,
                     employment_type, employment_status,
                     created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    20250000 + i,  # no (integer)
                    f'테스트직원{i}',  # name
                    f'test{i}@okfn.co.kr',  # email
                    'IT',  # department
                    'STAFF',  # position
                    date.today() - timedelta(days=365),  # hire_date
                    f'010-{random.randint(1000,9999)}-{random.randint(1000,9999)}',  # phone
                    '서울시 강남구',  # address
                    f'비상연락{i}',  # emergency_contact
                    '010-0000-0000',  # emergency_phone
                    '일반직',  # job_group
                    '정규직',  # job_type
                    'IT개발',  # job_role
                    1,  # growth_level (integer)
                    'STAFF',  # new_position
                    1,  # grade_level (integer)
                    '정규직',  # employment_type
                    '재직',  # employment_status
                    datetime.now(),  # created_at
                    datetime.now()  # updated_at
                ])
                print(f"  [OK] 테스트직원{i} 생성")
            except Exception as e:
                print(f"  [ERROR] Employee {i} 생성 실패: {e}")

def create_airiss_minimal():
    """AIRISS 데이터 생성"""
    print("\n2. AIRISS 분석 결과 생성")
    print("-" * 40)
    
    from airiss.models import AIAnalysisResult, AIAnalysisType
    
    # 분석 타입 생성 또는 가져오기
    try:
        analysis_type = AIAnalysisType.objects.filter(name='Railway AI 분석').first()
        if not analysis_type:
            analysis_type = AIAnalysisType.objects.create(
                name='Railway AI 분석',
                type_code='RAILWAY_TEST',
                description='Railway 테스트 AI 분석',
                is_active=True
            )
    except Exception as e:
        print(f"  [ERROR] AIAnalysisType 생성 실패: {e}")
        # 기존 타입 사용
        analysis_type = AIAnalysisType.objects.first()
        if not analysis_type:
            return 0
    
    # Employee 데이터 직접 조회
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, no, name FROM employees_employee LIMIT 10")
        employees = cursor.fetchall()
        
        if not employees:
            print("  [WARNING] Employee가 없습니다.")
            return 0
        
        created_count = 0
        for emp_id, emp_no, emp_name in employees:
            try:
                # Employee 객체 없이 직접 ID로 삽입
                score = random.uniform(70, 95)
                cursor.execute("""
                    INSERT INTO airiss_aianalysisresult 
                    (employee_id, analysis_type_id, score, confidence, 
                     result_data, recommendations, analyzed_at, valid_until)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, [
                    emp_id,  # employee_id
                    analysis_type.id,  # analysis_type_id
                    score,  # score
                    0.85,  # confidence
                    '{"performance_score": ' + str(score) + ', "potential_score": ' + str(score * 0.9) + '}',  # result_data
                    f'{emp_name} AI 분석 결과',  # recommendations
                    datetime.now(),  # analyzed_at
                    datetime.now() + timedelta(days=180)  # valid_until
                ])
                created_count += 1
                print(f"  [OK] {emp_name} AIRISS 결과 생성")
            except Exception as e:
                print(f"  [ERROR] AIRISS 생성 실패: {e}")
        
        return created_count

def create_talent_minimal():
    """인재풀 데이터 생성"""
    print("\n3. 인재풀 데이터 생성")
    print("-" * 40)
    
    from employees.models_talent import TalentCategory
    
    # 카테고리 확인
    category = TalentCategory.objects.filter(category_code='CORE_TALENT').first()
    if not category:
        print("  [ERROR] 카테고리가 없습니다.")
        return 0
    
    with connection.cursor() as cursor:
        # AIAnalysisResult 조회
        cursor.execute("""
            SELECT ar.id, ar.employee_id, ar.score, ar.confidence, e.name
            FROM airiss_aianalysisresult ar
            JOIN employees_employee e ON ar.employee_id = e.id
            LIMIT 10
        """)
        results = cursor.fetchall()
        
        if not results:
            print("  [WARNING] AIAnalysisResult가 없습니다.")
            return 0
        
        created_count = 0
        for result_id, emp_id, score, confidence, emp_name in results:
            try:
                cursor.execute("""
                    INSERT INTO employees_talentpool 
                    (employee_id, category_id, ai_analysis_result_id, ai_score, 
                     confidence_level, strengths, development_areas, status, 
                     added_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (employee_id) DO UPDATE SET
                    ai_score = EXCLUDED.ai_score,
                    updated_at = EXCLUDED.updated_at
                """, [
                    emp_id,  # employee_id
                    category.id,  # category_id
                    result_id,  # ai_analysis_result_id
                    float(score),  # ai_score
                    float(confidence),  # confidence_level
                    '["리더십", "전문성"]',  # strengths (JSON)
                    '["전략적 사고"]',  # development_areas (JSON)
                    'ACTIVE',  # status
                    datetime.now(),  # added_at
                    datetime.now()  # updated_at
                ])
                created_count += 1
                print(f"  [OK] {emp_name} 인재풀 등록")
            except Exception as e:
                print(f"  [ERROR] 인재풀 생성 실패: {e}")
        
        return created_count

def verify_data():
    """데이터 검증"""
    print("\n4. 데이터 검증")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # Employee 수
        cursor.execute("SELECT COUNT(*) FROM employees_employee")
        emp_count = cursor.fetchone()[0]
        print(f"Employee: {emp_count}명")
        
        # AIAnalysisResult 수
        cursor.execute("SELECT COUNT(*) FROM airiss_aianalysisresult")
        airiss_count = cursor.fetchone()[0]
        print(f"AIAnalysisResult: {airiss_count}개")
        
        # TalentPool 수
        cursor.execute("SELECT COUNT(*) FROM employees_talentpool")
        talent_count = cursor.fetchone()[0]
        print(f"TalentPool: {talent_count}명")
        
        # 샘플 데이터
        if emp_count > 0:
            cursor.execute("""
                SELECT e.name, e.department, e.position
                FROM employees_employee e
                LIMIT 3
            """)
            samples = cursor.fetchall()
            print("\n샘플 Employee:")
            for sample in samples:
                print(f"  - {sample[0]} ({sample[1]}, {sample[2]})")
        
        if talent_count > 0:
            cursor.execute("""
                SELECT e.name, tp.ai_score, tc.name
                FROM employees_talentpool tp
                JOIN employees_employee e ON tp.employee_id = e.id
                JOIN employees_talentcategory tc ON tp.category_id = tc.id
                LIMIT 3
            """)
            talents = cursor.fetchall()
            print("\n샘플 인재풀:")
            for talent in talents:
                print(f"  - {talent[0]}: {talent[1]:.1f}점 ({talent[2]})")

def main():
    """메인 실행"""
    print("\n시작: Railway 최소 데이터 생성\n")
    
    # 1. Employee 생성
    create_employees_minimal()
    
    # 2. AIRISS 데이터 생성
    airiss_count = create_airiss_minimal()
    
    # 3. 인재풀 생성
    if airiss_count > 0:
        create_talent_minimal()
    
    # 4. 검증
    verify_data()
    
    print("\n" + "="*60)
    print("[SUCCESS] Railway 데이터 생성 완료!")
    print("="*60)
    print("\n확인 URL:")
    print("- 인재 관리: https://ehrv10-production.up.railway.app/ai-insights/")
    print("- 관리자: https://ehrv10-production.up.railway.app/admin/")

if __name__ == "__main__":
    main()