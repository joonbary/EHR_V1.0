#!/usr/bin/env python
"""
Railway 간단한 초기 데이터 생성
- Employee 모델의 필드 확인 후 생성
"""

import os
import sys
import django
import random
from datetime import datetime, date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import transaction, connection
from employees.models import Employee
from django.contrib.auth.models import User
from airiss.models import AIAnalysisResult, AIAnalysisType
from employees.models_talent import TalentCategory, TalentPool, PromotionCandidate, RetentionRisk

print("="*60)
print("Railway 간단한 데이터 초기화")
print("="*60)

def check_employee_fields():
    """Employee 모델의 필드 확인"""
    print("\n1. Employee 모델 필드 확인")
    print("-" * 40)
    
    # Employee 모델의 필드 목록 가져오기
    fields = [f.name for f in Employee._meta.get_fields()]
    print(f"사용 가능한 필드: {', '.join(fields[:10])}...")
    
    # 필수 필드 확인
    required_fields = []
    for field in Employee._meta.get_fields():
        if hasattr(field, 'null') and not field.null and not field.blank:
            required_fields.append(field.name)
    
    print(f"필수 필드: {', '.join(required_fields)}")
    return fields

def create_simple_employees(num=10):
    """간단한 Employee 데이터 생성"""
    print(f"\n2. {num}명의 간단한 Employee 생성")
    print("-" * 40)
    
    created_count = 0
    
    with transaction.atomic():
        for i in range(1, num + 1):
            try:
                # User 생성
                username = f"emp{datetime.now().year}{i:04d}"
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f"emp{i}@okfn.co.kr",
                        'first_name': f"직원{i}",
                        'last_name': "테스트",
                        'is_active': True
                    }
                )
                
                if user_created:
                    user.set_password('password123')
                    user.save()
                
                # Employee 생성 (최소 필드만, no는 숫자 타입)
                employee, created = Employee.objects.update_or_create(
                    no=20250000 + i,  # 사번을 숫자로
                    defaults={
                        'user': user,
                        'name': f"테스트직원{i}",
                        'email': f"emp{i}@okfn.co.kr",
                        'phone': f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                        'department': random.choice(['IT', 'HR', 'FINANCE', 'MARKETING']),
                        'position': random.choice(['STAFF', 'SENIOR', 'MANAGER']),
                        'hire_date': date.today() - timedelta(days=random.randint(365, 3650)),
                        # 필수 필드 추가
                        'job_group': '일반직',
                        'job_type': '정규직',
                        'growth_level': 'LEVEL1',
                        'new_position': 'STAFF',
                        'grade_level': 'G1',
                        'employment_type': '정규직',
                        'employment_status': '재직',
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"  [OK] {employee.name} 생성")
                    
            except Exception as e:
                print(f"  [ERROR] Employee {i} 생성 실패: {e}")
    
    print(f"\n[완료] {created_count}명 생성 성공")
    return created_count

def create_airiss_results():
    """AIRISS 분석 결과 생성"""
    print("\n3. AIRISS 분석 결과 생성")
    print("-" * 40)
    
    # 분석 타입 생성
    analysis_type, _ = AIAnalysisType.objects.get_or_create(
        name='성과 잠재력 분석',
        defaults={
            'description': 'AI 기반 성과 및 잠재력 분석',
            'is_active': True
        }
    )
    
    created_count = 0
    employees = Employee.objects.all()[:5]  # 상위 5명만
    
    for employee in employees:
        try:
            score = random.uniform(60, 95)
            
            result, created = AIAnalysisResult.objects.update_or_create(
                employee=employee,
                analysis_type=analysis_type,
                defaults={
                    'score': score,
                    'confidence': 0.85,
                    'result_data': {
                        'performance_score': score,
                        'potential_score': score * 0.9,
                        'strengths': ['리더십', '전문성'],
                        'development_areas': ['전략적 사고']
                    },
                    'recommendations': f'{employee.name}님은 우수한 성과를 보이고 있습니다.',
                    'analyzed_at': datetime.now(),
                    'valid_until': datetime.now() + timedelta(days=180)
                }
            )
            
            if created:
                created_count += 1
                print(f"  [OK] {employee.name} 분석 결과 생성")
                
        except Exception as e:
            print(f"  [ERROR] AIRISS 생성 실패: {e}")
    
    print(f"\n[완료] {created_count}개 분석 결과 생성")
    return created_count

def sync_to_talent():
    """인재풀 동기화"""
    print("\n4. 인재풀 동기화")
    print("-" * 40)
    
    # 카테고리 생성
    category, _ = TalentCategory.objects.get_or_create(
        category_code='CORE_TALENT',
        defaults={'name': '핵심인재', 'description': '핵심 성과 인재'}
    )
    
    created_count = 0
    results = AIAnalysisResult.objects.all()
    
    for result in results:
        try:
            talent, created = TalentPool.objects.get_or_create(
                employee=result.employee,
                defaults={
                    'category': category,
                    'ai_analysis_result_id': result.id,
                    'ai_score': float(result.score),
                    'confidence_level': float(result.confidence),
                    'strengths': ['리더십', '전문성'],
                    'development_areas': ['전략적 사고'],
                    'status': 'ACTIVE',
                    'added_at': result.analyzed_at
                }
            )
            
            if created:
                created_count += 1
                print(f"  [OK] {result.employee.name} 인재풀 등록")
                
        except Exception as e:
            print(f"  [ERROR] 인재풀 동기화 실패: {e}")
    
    print(f"\n[완료] {created_count}명 인재풀 등록")
    return created_count

def verify_data():
    """데이터 검증"""
    print("\n5. 데이터 검증")
    print("-" * 40)
    
    print(f"Employee: {Employee.objects.count()}명")
    print(f"AIAnalysisResult: {AIAnalysisResult.objects.count()}개")
    print(f"TalentPool: {TalentPool.objects.count()}명")
    print(f"PromotionCandidate: {PromotionCandidate.objects.count()}명")
    print(f"RetentionRisk: {RetentionRisk.objects.count()}명")

def main():
    """메인 실행"""
    print("\n시작: Railway 간단한 데이터 초기화\n")
    
    # 1. Employee 필드 확인
    fields = check_employee_fields()
    
    # 2. Employee 생성
    emp_count = create_simple_employees(10)
    
    if emp_count > 0:
        # 3. AIRISS 결과 생성
        airiss_count = create_airiss_results()
        
        if airiss_count > 0:
            # 4. 인재풀 동기화
            talent_count = sync_to_talent()
    
    # 5. 검증
    verify_data()
    
    print("\n" + "="*60)
    print("[SUCCESS] Railway 데이터 초기화 완료!")
    print("="*60)
    print("\n확인 URL:")
    print("- https://ehrv10-production.up.railway.app/ai-insights/")
    print("- https://ehrv10-production.up.railway.app/admin/")

if __name__ == "__main__":
    main()