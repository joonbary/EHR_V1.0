#!/usr/bin/env python
"""
Railway 초기 데이터 설정 스크립트
1. Employee 가상 데이터 생성 (100명)
2. AIRISS 분석 결과 생성
3. 인재풀 데이터 동기화
"""

import os
import sys
import django
import random
from datetime import datetime, date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import transaction
from employees.models import Employee
from django.contrib.auth.models import User
from airiss.models import AIAnalysisResult, AIAnalysisType
from employees.models_talent import TalentCategory, TalentPool, PromotionCandidate, RetentionRisk

print("="*60)
print("Railway 초기 데이터 설정")
print("="*60)

# 간단한 데이터 생성 함수들
def generate_korean_name():
    """한국 이름 생성"""
    last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
    first_names = ['민수', '지훈', '서연', '지우', '하준', '서준', '민지', '수빈', '예진', '유진']
    return random.choice(last_names) + random.choice(first_names)

def generate_employee_data(num_employees=100):
    """Employee 데이터 생성"""
    print(f"\n1. Employee 데이터 {num_employees}명 생성 중...")
    
    positions = ['사원', '대리', '과장', '차장', '부장']
    departments = ['IT개발팀', '영업팀', '인사팀', '재무팀', '마케팅팀', '기획팀']
    companies = ['OK저축은행', 'OK캐피탈', 'OK증권']
    
    created_count = 0
    
    with transaction.atomic():
        for i in range(1, num_employees + 1):
            try:
                emp_no = f"2024{i:04d}"
                name = generate_korean_name()
                
                # User 생성
                user, user_created = User.objects.get_or_create(
                    username=emp_no,
                    defaults={
                        'email': f"emp{i}@okfn.co.kr",
                        'first_name': name[1:],
                        'last_name': name[0],
                        'is_active': True
                    }
                )
                
                if user_created:
                    user.set_password('password123')
                    user.save()
                
                # Employee 생성
                position = random.choice(positions)
                age = random.randint(25, 55)
                
                employee, created = Employee.objects.update_or_create(
                    no=emp_no,
                    defaults={
                        'user': user,
                        'name': name,
                        'email': f"emp{i}@okfn.co.kr",
                        'phone': f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                        'gender': random.choice(['M', 'F']),
                        'birth_date': date.today() - timedelta(days=age*365),
                        'age': age,
                        'hire_date': date.today() - timedelta(days=random.randint(365, 3650)),
                        
                        # 조직 정보
                        'group_name': 'OK금융그룹',
                        'company': random.choice(companies),
                        'department': random.choice(departments),
                        'position': position,
                        
                        # 상태
                        'employment_status': '재직',
                        'employment_type': '정규직',
                    }
                )
                
                if created:
                    created_count += 1
                    
            except Exception as e:
                print(f"[ERROR] Employee {i} 생성 실패: {e}")
    
    print(f"[OK] {created_count}명의 Employee 생성 완료")
    return created_count

def generate_airiss_data():
    """AIRISS 분석 결과 데이터 생성"""
    print("\n2. AIRISS 분석 결과 생성 중...")
    
    # 분석 타입 생성
    analysis_type, _ = AIAnalysisType.objects.get_or_create(
        name='성과 잠재력 분석',
        defaults={
            'description': 'AI 기반 성과 및 잠재력 종합 분석',
            'is_active': True
        }
    )
    
    created_count = 0
    employees = Employee.objects.all()[:50]  # 상위 50명만 분석
    
    with transaction.atomic():
        for employee in employees:
            try:
                # AI 분석 결과 생성
                score = random.uniform(60, 95)
                confidence = random.uniform(0.7, 0.95)
                
                result, created = AIAnalysisResult.objects.update_or_create(
                    employee=employee,
                    analysis_type=analysis_type,
                    defaults={
                        'score': score,
                        'confidence': confidence,
                        'result_data': {
                            'performance_score': score,
                            'potential_score': score * 0.9,
                            'strengths': ['리더십', '전문성', '협업능력'],
                            'development_areas': ['전략적 사고', '의사결정'],
                            'recommendations': ['리더십 교육', '멘토링 프로그램']
                        },
                        'recommendations': f'{employee.name}님은 {score:.1f}점의 우수한 성과를 보이고 있습니다.',
                        'analyzed_at': datetime.now(),
                        'valid_until': datetime.now() + timedelta(days=180)
                    }
                )
                
                if created:
                    created_count += 1
                    
            except Exception as e:
                print(f"[ERROR] AIRISS 분석 생성 실패: {e}")
    
    print(f"[OK] {created_count}개의 AIRISS 분석 결과 생성 완료")
    return created_count

def sync_talent_pool():
    """인재풀 동기화"""
    print("\n3. 인재풀 데이터 동기화 중...")
    
    # 카테고리 확인/생성
    categories = {}
    category_data = [
        ('CORE_TALENT', '핵심인재', '조직의 핵심 성과를 이끄는 인재'),
        ('HIGH_POTENTIAL', '고잠재력', '향후 리더로 성장 가능한 인재'),
        ('SPECIALIST', '전문가', '특정 분야의 전문 지식을 보유한 인재'),
        ('NEEDS_ATTENTION', '관리필요', '성과 개선이 필요한 인재')
    ]
    
    for code, name, desc in category_data:
        category, _ = TalentCategory.objects.get_or_create(
            category_code=code,
            defaults={'name': name, 'description': desc}
        )
        categories[code] = category
    
    # AIAnalysisResult를 TalentPool로 동기화
    created_count = 0
    results = AIAnalysisResult.objects.all()
    
    with transaction.atomic():
        for result in results:
            try:
                # 점수에 따른 카테고리 결정
                if result.score >= 85:
                    category = categories['CORE_TALENT']
                elif result.score >= 75:
                    category = categories['HIGH_POTENTIAL']
                elif result.score >= 65:
                    category = categories['SPECIALIST']
                else:
                    category = categories['NEEDS_ATTENTION']
                
                talent, created = TalentPool.objects.get_or_create(
                    employee=result.employee,
                    defaults={
                        'category': category,
                        'ai_analysis_result_id': result.id,
                        'ai_score': float(result.score),
                        'confidence_level': float(result.confidence),
                        'strengths': result.result_data.get('strengths', []),
                        'development_areas': result.result_data.get('development_areas', []),
                        'status': 'ACTIVE',
                        'added_at': result.analyzed_at
                    }
                )
                
                if created:
                    created_count += 1
                    
                    # 고성과자는 승진 후보자로도 등록
                    if result.score >= 80:
                        PromotionCandidate.objects.get_or_create(
                            employee=result.employee,
                            defaults={
                                'current_position': result.employee.position or '사원',
                                'target_position': '차상위직급',
                                'readiness_level': 'READY' if result.score >= 85 else 'DEVELOPING',
                                'performance_score': float(result.score),
                                'potential_score': float(result.score * 0.9),
                                'ai_recommendation_score': float(result.score),
                                'expected_promotion_date': date.today() + timedelta(days=180),
                                'is_active': True
                            }
                        )
                    
                    # 저성과자는 이직 위험군으로 등록
                    if result.score < 70:
                        RetentionRisk.objects.get_or_create(
                            employee=result.employee,
                            defaults={
                                'risk_level': 'HIGH' if result.score < 65 else 'MEDIUM',
                                'risk_score': 100 - float(result.score),
                                'risk_factors': ['성과 부진', '동기 저하'],
                                'retention_strategy': '1:1 면담 및 개선 계획 수립',
                                'action_status': 'PENDING'
                            }
                        )
                        
            except Exception as e:
                print(f"[ERROR] 인재풀 동기화 실패: {e}")
    
    print(f"[OK] {created_count}명의 인재풀 데이터 동기화 완료")
    return created_count

def verify_data():
    """데이터 검증"""
    print("\n4. 데이터 검증")
    print("-" * 40)
    
    print(f"Employee: {Employee.objects.count()}명")
    print(f"AIAnalysisResult: {AIAnalysisResult.objects.count()}개")
    print(f"TalentPool: {TalentPool.objects.count()}명")
    print(f"PromotionCandidate: {PromotionCandidate.objects.count()}명")
    print(f"RetentionRisk: {RetentionRisk.objects.count()}명")
    
    # 카테고리별 통계
    for category in TalentCategory.objects.all():
        count = TalentPool.objects.filter(category=category).count()
        print(f"  - {category.name}: {count}명")

def main():
    """메인 실행"""
    print("\n시작: Railway 초기 데이터 설정\n")
    
    # 기존 데이터 확인
    existing_employees = Employee.objects.count()
    if existing_employees > 0:
        print(f"[INFO] 이미 {existing_employees}명의 Employee가 존재합니다.")
        proceed = input("계속 진행하시겠습니까? (y/n): ")
        if proceed.lower() != 'y':
            print("중단됨")
            return
    
    # 1. Employee 생성
    emp_count = generate_employee_data(100)
    
    if emp_count > 0:
        # 2. AIRISS 분석 결과 생성
        airiss_count = generate_airiss_data()
        
        if airiss_count > 0:
            # 3. 인재풀 동기화
            talent_count = sync_talent_pool()
    
    # 4. 최종 검증
    verify_data()
    
    print("\n" + "="*60)
    print("[SUCCESS] Railway 초기 데이터 설정 완료!")
    print("="*60)
    print("\n다음 URL에서 확인:")
    print("- https://ehrv10-production.up.railway.app/ai-insights/")
    print("- https://ehrv10-production.up.railway.app/admin/")

if __name__ == "__main__":
    main()