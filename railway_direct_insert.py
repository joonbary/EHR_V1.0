#!/usr/bin/env python
"""
Railway 직접 SQL 삽입으로 데이터 생성
"""

import os
import sys
import django
from datetime import datetime, date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
import random

print("="*60)
print("Railway 직접 데이터 삽입")
print("="*60)

def check_employee_columns():
    """Employee 테이블 컬럼 확인"""
    print("\n1. Employee 테이블 컬럼 확인")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # PostgreSQL 컬럼 정보 조회
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee' 
            ORDER BY ordinal_position
            LIMIT 20
        """)
        columns = cursor.fetchall()
        
        print("Employee 테이블 컬럼:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (null={col[2]})")
        
        return [col[0] for col in columns]

def create_users_directly():
    """User 직접 생성"""
    print("\n2. User 생성")
    print("-" * 40)
    
    created_users = []
    for i in range(1, 6):
        username = f"railway_emp_{i}"
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"railway{i}@okfn.co.kr",
                    'first_name': f"Railway{i}",
                    'last_name': "직원",
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                print(f"  [OK] User {username} 생성")
            created_users.append(user.id)
        except Exception as e:
            print(f"  [ERROR] User 생성 실패: {e}")
    
    return created_users

def insert_employees_directly(user_ids):
    """Employee 데이터 직접 SQL 삽입"""
    print("\n3. Employee 직접 삽입")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 먼저 컬럼 확인
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee' 
            AND column_name IN ('id', 'no', 'name', 'email', 'phone', 'department', 
                               'position', 'hire_date', 'user_id', 'job_group', 
                               'job_type', 'growth_level', 'new_position', 
                               'grade_level', 'employment_type', 'employment_status')
        """)
        available_columns = [row[0] for row in cursor.fetchall()]
        print(f"사용 가능한 컬럼: {', '.join(available_columns)}")
        
        # 기본 컬럼만으로 삽입 시도
        for i, user_id in enumerate(user_ids, 1):
            try:
                # 최소한의 필드만 사용
                cursor.execute("""
                    INSERT INTO employees_employee 
                    (no, name, email, phone, department, position, hire_date, user_id,
                     job_group, job_type, growth_level, new_position, grade_level,
                     employment_type, employment_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (no) DO NOTHING
                """, [
                    20250000 + i,  # no
                    f'Railway직원{i}',  # name
                    f'railway{i}@okfn.co.kr',  # email
                    f'010-{random.randint(1000,9999)}-{random.randint(1000,9999)}',  # phone
                    'IT',  # department
                    'STAFF',  # position
                    date.today() - timedelta(days=365),  # hire_date
                    user_id,  # user_id
                    '일반직',  # job_group
                    '정규직',  # job_type
                    'LEVEL1',  # growth_level
                    'STAFF',  # new_position
                    'G1',  # grade_level
                    '정규직',  # employment_type
                    '재직'  # employment_status
                ])
                print(f"  [OK] Employee Railway직원{i} 삽입")
            except Exception as e:
                print(f"  [ERROR] Employee {i} 삽입 실패: {e}")
                # 더 간단한 삽입 시도
                try:
                    cursor.execute("""
                        INSERT INTO employees_employee 
                        (no, name, email, department, position, hire_date, phone,
                         job_group, job_type, growth_level, new_position, grade_level,
                         employment_type, employment_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (no) DO NOTHING
                    """, [
                        20250000 + i, f'Railway직원{i}', f'railway{i}@okfn.co.kr',
                        'IT', 'STAFF', date.today() - timedelta(days=365),
                        '010-1234-5678', '일반직', '정규직', 'LEVEL1', 'STAFF', 'G1',
                        '정규직', '재직'
                    ])
                    print(f"  [OK] Employee Railway직원{i} 삽입 (user 없이)")
                except Exception as e2:
                    print(f"  [ERROR2] 최종 실패: {e2}")

def create_airiss_data():
    """AIRISS 데이터 생성"""
    print("\n4. AIRISS 분석 결과 생성")
    print("-" * 40)
    
    from airiss.models import AIAnalysisResult, AIAnalysisType
    from employees.models import Employee
    
    # 분석 타입 생성
    analysis_type, _ = AIAnalysisType.objects.get_or_create(
        name='Railway 테스트 분석',
        defaults={
            'description': 'Railway 테스트용 AI 분석',
            'is_active': True
        }
    )
    
    # Employee 조회
    employees = Employee.objects.all()[:5]
    if not employees:
        print("  [WARNING] Employee가 없습니다.")
        return 0
    
    created_count = 0
    for emp in employees:
        try:
            score = random.uniform(70, 95)
            result, created = AIAnalysisResult.objects.update_or_create(
                employee=emp,
                analysis_type=analysis_type,
                defaults={
                    'score': score,
                    'confidence': 0.85,
                    'result_data': {
                        'performance_score': score,
                        'potential_score': score * 0.9
                    },
                    'recommendations': f'{emp.name} 성과 분석',
                    'analyzed_at': datetime.now(),
                    'valid_until': datetime.now() + timedelta(days=180)
                }
            )
            if created:
                created_count += 1
                print(f"  [OK] {emp.name} AIRISS 결과 생성")
        except Exception as e:
            print(f"  [ERROR] AIRISS 생성 실패: {e}")
    
    return created_count

def sync_talent_data():
    """인재풀 동기화"""
    print("\n5. 인재풀 동기화")
    print("-" * 40)
    
    from airiss.models import AIAnalysisResult
    from employees.models_talent import TalentCategory, TalentPool
    
    # 카테고리 확인
    category = TalentCategory.objects.filter(category_code='CORE_TALENT').first()
    if not category:
        print("  [ERROR] 카테고리가 없습니다.")
        return 0
    
    # AIAnalysisResult 동기화
    results = AIAnalysisResult.objects.all()[:5]
    created_count = 0
    
    for result in results:
        try:
            talent, created = TalentPool.objects.get_or_create(
                employee=result.employee,
                defaults={
                    'category': category,
                    'ai_analysis_result_id': result.id,
                    'ai_score': float(result.score),
                    'confidence_level': float(result.confidence),
                    'strengths': ['리더십'],
                    'development_areas': ['전략'],
                    'status': 'ACTIVE',
                    'added_at': result.analyzed_at
                }
            )
            if created:
                created_count += 1
                print(f"  [OK] {result.employee.name} 인재풀 등록")
        except Exception as e:
            print(f"  [ERROR] 인재풀 동기화 실패: {e}")
    
    return created_count

def verify_data():
    """데이터 검증"""
    print("\n6. 최종 데이터 검증")
    print("-" * 40)
    
    from employees.models import Employee
    from airiss.models import AIAnalysisResult
    from employees.models_talent import TalentPool
    
    with connection.cursor() as cursor:
        # Employee 수 확인
        cursor.execute("SELECT COUNT(*) FROM employees_employee")
        emp_count = cursor.fetchone()[0]
        print(f"Employee: {emp_count}명")
        
        # 샘플 데이터 확인
        if emp_count > 0:
            cursor.execute("SELECT no, name, department FROM employees_employee LIMIT 3")
            samples = cursor.fetchall()
            for sample in samples:
                print(f"  - {sample[0]}: {sample[1]} ({sample[2]})")
    
    print(f"AIAnalysisResult: {AIAnalysisResult.objects.count()}개")
    print(f"TalentPool: {TalentPool.objects.count()}명")

def main():
    """메인 실행"""
    print("\n시작: Railway 직접 데이터 삽입\n")
    
    # 1. 컬럼 확인
    columns = check_employee_columns()
    
    # 2. User 생성
    user_ids = create_users_directly()
    
    # 3. Employee 삽입
    insert_employees_directly(user_ids)
    
    # 4. AIRISS 데이터
    airiss_count = create_airiss_data()
    
    # 5. 인재풀 동기화
    if airiss_count > 0:
        sync_talent_data()
    
    # 6. 검증
    verify_data()
    
    print("\n" + "="*60)
    print("[완료] Railway 데이터 삽입 프로세스 완료")
    print("="*60)
    print("\n확인:")
    print("- https://ehrv10-production.up.railway.app/ai-insights/")
    print("- https://ehrv10-production.up.railway.app/admin/")

if __name__ == "__main__":
    main()