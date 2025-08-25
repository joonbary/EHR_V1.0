#!/usr/bin/env python
"""
인재 관리 시스템 테스트 및 초기 데이터 생성
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from employees.models_talent import TalentCategory, TalentPool, PromotionCandidate, RetentionRisk
from airiss.models import AIAnalysisType, AIAnalysisResult
from django.contrib.auth.models import User
from django.utils import timezone
import random

def create_talent_categories():
    """인재 카테고리 생성"""
    print("\n1. 인재 카테고리 생성")
    print("-" * 40)
    
    categories = [
        {
            'name': '핵심인재',
            'category_code': 'CORE_TALENT',
            'description': 'AI 평가 상위 10% 이내의 핵심 인력',
            'criteria': {'min_score': 90, 'min_confidence': 0.8}
        },
        {
            'name': '승진후보자',
            'category_code': 'PROMOTION_CANDIDATE',
            'description': 'AI 승진 가능성 평가 75점 이상',
            'criteria': {'min_score': 75, 'min_confidence': 0.7}
        },
        {
            'name': '관리필요인력',
            'category_code': 'NEEDS_ATTENTION',
            'description': 'AI 평가 하위 20% 또는 이직 위험도 높음',
            'criteria': {'max_score': 50, 'risk_level': 'HIGH'}
        },
        {
            'name': '이직위험군',
            'category_code': 'RETENTION_RISK',
            'description': 'AI 이직 위험도 70% 이상',
            'criteria': {'min_risk_score': 70}
        },
    ]
    
    for cat_data in categories:
        category, created = TalentCategory.objects.get_or_create(
            category_code=cat_data['category_code'],
            defaults={
                'name': cat_data['name'],
                'description': cat_data['description'],
                'criteria': cat_data['criteria']
            }
        )
        if created:
            print(f"  [생성] {category.name}")
        else:
            print(f"  [존재] {category.name}")
    
    return TalentCategory.objects.all()

def create_test_airiss_results():
    """테스트용 AIRISS 분석 결과 생성"""
    print("\n2. AIRISS 분석 결과 생성")
    print("-" * 40)
    
    # 분석 유형 생성
    analysis_types = [
        ('PROMOTION_POTENTIAL', '승진 가능성 분석'),
        ('TURNOVER_RISK', '퇴사 위험도 예측'),
        ('TALENT_RECOMMENDATION', '인재 추천'),
    ]
    
    for type_code, name in analysis_types:
        analysis_type, created = AIAnalysisType.objects.get_or_create(
            type_code=type_code,
            defaults={'name': name, 'description': f'{name} AI 분석'}
        )
        if created:
            print(f"  [생성] {name}")
    
    # 직원 샘플 가져오기
    employees = Employee.objects.all()[:10]
    if not employees:
        print("  [경고] 직원 데이터가 없습니다. 먼저 직원 데이터를 생성하세요.")
        return
    
    # Admin 사용자
    admin_user = User.objects.filter(is_superuser=True).first()
    
    results_created = 0
    for emp in employees:
        # 승진 가능성 분석
        if random.random() > 0.3:  # 70% 확률로 생성
            score = random.uniform(60, 95)
            analysis_result = AIAnalysisResult.objects.create(
                analysis_type=AIAnalysisType.objects.get(type_code='PROMOTION_POTENTIAL'),
                employee=emp,
                score=score,
                confidence=random.uniform(0.7, 0.95),
                result_data={
                    'strengths': ['리더십', '문제해결능력', '팀워크'],
                    'weaknesses': ['시간관리'],
                    'readiness': 'NEAR_READY' if score > 80 else 'DEVELOPING'
                },
                recommendations=['리더십 교육 프로그램 참여', '프로젝트 관리 경험 확대'],
                insights=f'{emp.name}님은 승진 가능성 {score:.1f}점으로 평가되었습니다.',
                created_by=admin_user
            )
            results_created += 1
        
        # 이직 위험도 분석
        if random.random() > 0.5:  # 50% 확률로 생성
            risk_score = random.uniform(20, 90)
            analysis_result = AIAnalysisResult.objects.create(
                analysis_type=AIAnalysisType.objects.get(type_code='TURNOVER_RISK'),
                employee=emp,
                score=risk_score,
                confidence=random.uniform(0.6, 0.9),
                result_data={
                    'risk_factors': ['보상 불만족', '경력 정체', '업무 과부하'],
                    'retention_probability': 100 - risk_score
                },
                recommendations=['보상 재검토', '경력 개발 계획 수립', '업무 재배분'],
                insights=f'{emp.name}님의 이직 위험도는 {risk_score:.1f}%입니다.',
                created_by=admin_user
            )
            results_created += 1
    
    print(f"  [완료] {results_created}개 분석 결과 생성")
    return AIAnalysisResult.objects.all()

def sync_to_talent_pool():
    """AIRISS 결과를 인재풀로 동기화"""
    print("\n3. 인재풀 동기화")
    print("-" * 40)
    
    analysis_results = AIAnalysisResult.objects.all()
    synced_count = 0
    
    for result in analysis_results:
        talent_pool = TalentPool.update_from_airiss(result)
        if talent_pool:
            print(f"  [동기화] {result.employee.name} → {talent_pool.category.name}")
            synced_count += 1
    
    print(f"  [완료] {synced_count}개 인재풀 항목 생성/업데이트")
    return TalentPool.objects.all()

def create_promotion_candidates():
    """승진 후보자 생성"""
    print("\n4. 승진 후보자 관리")
    print("-" * 40)
    
    # 승진 가능성 높은 인재풀 가져오기
    promotion_pools = TalentPool.objects.filter(
        category__category_code='PROMOTION_CANDIDATE',
        ai_score__gte=75
    )
    
    created_count = 0
    for pool in promotion_pools:
        candidate, created = PromotionCandidate.objects.get_or_create(
            employee=pool.employee,
            target_position='차장' if pool.employee.position == '과장' else '부장',
            defaults={
                'talent_pool': pool,
                'current_position': pool.employee.position or '과장',
                'readiness_level': 'READY' if pool.ai_score >= 85 else 'NEAR_READY',
                'expected_promotion_date': timezone.now().date() + timezone.timedelta(days=180),
                'performance_score': pool.ai_score,
                'potential_score': pool.ai_score * 0.9,
                'ai_recommendation_score': pool.ai_score,
                'development_plan': {
                    'required_training': ['리더십 과정', 'MBA 과정'],
                    'required_experience': ['프로젝트 리더 경험', '팀 관리 경험']
                }
            }
        )
        if created:
            print(f"  [생성] {candidate.employee.name} - {candidate.target_position} 후보")
            created_count += 1
    
    print(f"  [완료] {created_count}명 승진 후보자 등록")

def create_retention_risks():
    """이직 위험 관리 생성"""
    print("\n5. 이직 위험 관리")
    print("-" * 40)
    
    # 이직 위험 높은 인재풀 가져오기
    risk_pools = TalentPool.objects.filter(
        category__category_code='RETENTION_RISK',
        ai_score__gte=70
    )
    
    created_count = 0
    for pool in risk_pools:
        risk, created = RetentionRisk.objects.get_or_create(
            employee=pool.employee,
            defaults={
                'talent_pool': pool,
                'risk_level': 'CRITICAL' if pool.ai_score >= 85 else 'HIGH',
                'risk_score': pool.ai_score,
                'risk_factors': pool.ai_analysis_result.result_data.get('risk_factors', []),
                'retention_strategy': '긴급 면담 실시, 보상 패키지 재검토, 경력 개발 기회 제공',
                'action_items': [
                    '1:1 면담 스케줄링',
                    '보상 벤치마킹 실시',
                    '경력 개발 계획 수립'
                ],
                'action_status': 'PENDING'
            }
        )
        if created:
            print(f"  [생성] {risk.employee.name} - 위험도 {risk.risk_score:.1f}%")
            created_count += 1
    
    print(f"  [완료] {created_count}명 이직 위험 관리 등록")

def display_summary():
    """전체 요약 표시"""
    from django.db.models import Avg
    
    print("\n" + "="*60)
    print("인재 관리 시스템 요약")
    print("="*60)
    
    print(f"인재 카테고리: {TalentCategory.objects.count()}개")
    print(f"AI 분석 결과: {AIAnalysisResult.objects.count()}개")
    print(f"인재풀 등록: {TalentPool.objects.count()}명")
    print(f"승진 후보자: {PromotionCandidate.objects.count()}명")
    print(f"이직 위험군: {RetentionRisk.objects.count()}명")
    
    print("\n카테고리별 인재 현황:")
    for category in TalentCategory.objects.all():
        count = TalentPool.objects.filter(category=category).count()
        if count > 0:
            avg_score = TalentPool.objects.filter(category=category).aggregate(
                avg_score=Avg('ai_score')
            )['avg_score'] or 0
            print(f"  - {category.name}: {count}명 (평균 점수: {avg_score:.1f})")
    
    print("\n" + "="*60)
    print("Django Admin에서 확인:")
    print("http://localhost:8000/admin/employees/talentpool/")
    print("http://localhost:8000/admin/employees/promotioncandidate/")
    print("http://localhost:8000/admin/employees/retentionrisk/")
    print("="*60)

def main():
    """메인 실행"""
    
    print("\n" + "="*60)
    print("AIRISS-EHR 인재 관리 통합 테스트")
    print("="*60)
    
    # 1. 인재 카테고리 생성
    create_talent_categories()
    
    # 2. AIRISS 분석 결과 생성
    create_test_airiss_results()
    
    # 3. 인재풀 동기화
    sync_to_talent_pool()
    
    # 4. 승진 후보자 생성
    create_promotion_candidates()
    
    # 5. 이직 위험 관리 생성
    create_retention_risks()
    
    # 6. 요약 표시
    display_summary()

if __name__ == "__main__":
    main()