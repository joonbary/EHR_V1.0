#!/usr/bin/env python
"""
이직 위험도 분석 기능 테스트 스크립트
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from ai_predictions.models import TurnoverRisk, RiskFactor, RetentionPlan, TurnoverAlert
from ai_predictions.services import TurnoverRiskAnalyzer, TurnoverAlertSystem
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from compensation.models import EmployeeCompensation

def create_risk_factors():
    """기본 위험 요소 생성"""
    print("기본 위험 요소 생성 중...")
    
    risk_factors_data = [
        {
            'name': '낮은 성과 평가',
            'factor_type': 'PERFORMANCE',
            'description': '최근 성과 평가가 기준 이하인 경우',
            'base_weight': 0.8,
        },
        {
            'name': '시장 대비 낮은 급여',
            'factor_type': 'COMPENSATION',
            'description': '동일 직급/직책 대비 급여가 시장 평균보다 낮은 경우',
            'base_weight': 0.9,
        },
        {
            'name': '승진 기회 부족',
            'factor_type': 'CAREER',
            'description': '장기간 승진이 없거나 경력 발전 기회가 제한적인 경우',
            'base_weight': 0.7,
        },
        {
            'name': '과도한 업무량',
            'factor_type': 'WORKLOAD',
            'description': '지속적인 야근 및 과도한 업무 부담',
            'base_weight': 0.6,
        },
        {
            'name': '상사와의 관계 문제',
            'factor_type': 'RELATIONSHIP',
            'description': '직속 상관과의 업무적/개인적 갈등',
            'base_weight': 0.8,
        },
        {
            'name': '낮은 참여도',
            'factor_type': 'ENGAGEMENT',
            'description': '회사 활동 및 팀 업무 참여도 저조',
            'base_weight': 0.5,
        }
    ]
    
    created_count = 0
    for factor_data in risk_factors_data:
        factor, created = RiskFactor.objects.get_or_create(
            name=factor_data['name'],
            defaults=factor_data
        )
        if created:
            created_count += 1
    
    print(f"위험 요소 {created_count}개 생성됨")

def get_sample_employees():
    """기존 직원 데이터에서 테스트용 샘플 선택"""
    print("테스트용 직원 선택 중...")
    
    # 기존 재직 직원 중에서 처음 3명 선택
    existing_employees = Employee.objects.filter(employment_status='재직')[:3]
    
    if not existing_employees.exists():
        print("기존 직원 데이터가 없습니다. 기본 직원 데이터를 생성합니다...")
        # 간단한 기본 데이터만 생성
        from django.contrib.auth.models import User
        
        sample_data = [
            {'name': '김테스트', 'department': '개발팀'},
            {'name': '박테스트', 'department': '마케팅팀'},
            {'name': '이테스트', 'department': '기획팀'}
        ]
        
        created_employees = []
        for i, data in enumerate(sample_data, start=9001):
            try:
                employee = Employee.objects.create(
                    no=i,
                    name=data['name'],
                    department=data['department'],
                    position='대리',
                    hire_date=date.today() - timedelta(days=365),
                    employment_status='재직'
                )
                created_employees.append(employee)
            except Exception as e:
                print(f"직원 생성 오류: {e}")
                continue
        
        existing_employees = created_employees
    
    print(f"테스트 대상 직원: {len(existing_employees)}명")
    return list(existing_employees)

def test_risk_analysis():
    """위험도 분석 테스트"""
    print("\n위험도 분석 기능 테스트 중...")
    
    analyzer = TurnoverRiskAnalyzer()
    
    # 기존 직원 중에서 테스트 대상 선택
    test_employees = Employee.objects.filter(employment_status='재직')[:3]
    
    results = []
    for employee in test_employees:
        try:
            print(f"\n=== {employee.name} 분석 중 ===")
            analysis = analyzer.analyze_employee_risk(employee)
            
            print(f"위험도 점수: {analysis['risk_score']:.3f}")
            print(f"위험도 레벨: {analysis['risk_level']}")
            print(f"AI 신뢰도: {analysis['confidence_level']:.3f}")
            print(f"주요 위험 요소: {len(analysis['primary_risk_factors'])}개")
            print(f"보호 요소: {len(analysis['protective_factors'])}개")
            
            if analysis['predicted_departure_date']:
                print(f"예상 퇴사일: {analysis['predicted_departure_date']}")
            
            # DB에 저장
            risk_record, created = TurnoverRisk.objects.update_or_create(
                employee=employee,
                prediction_date__date=date.today(),
                defaults={
                    'risk_level': analysis['risk_level'],
                    'risk_score': analysis['risk_score'],
                    'confidence_level': analysis['confidence_level'],
                    'primary_risk_factors': analysis['primary_risk_factors'],
                    'secondary_risk_factors': analysis['secondary_risk_factors'],
                    'protective_factors': analysis['protective_factors'],
                    'predicted_departure_date': analysis['predicted_departure_date'],
                    'ai_analysis': analysis['ai_analysis'],
                    'ai_recommendations': analysis['recommendations'],
                    'ai_model_version': analysis['model_version'],
                    'status': 'ACTIVE'
                }
            )
            
            results.append(analysis)
            
        except Exception as e:
            print(f"분석 오류 ({employee.name}): {e}")
    
    print(f"\n총 {len(results)}명 분석 완료")
    return results

def test_alert_system():
    """알림 시스템 테스트"""
    print("\n알림 시스템 테스트 중...")
    
    alert_system = TurnoverAlertSystem()
    
    # 고위험 직원에 대한 알림 생성 테스트
    high_risk_employee = Employee.objects.filter(employment_status='재직').first()
    if high_risk_employee:
        # 가상의 고위험 분석 결과
        fake_analysis = {
            'employee_id': high_risk_employee.id,
            'risk_score': 0.85,
            'risk_level': 'CRITICAL',
            'primary_risk_factors': [
                {'type': 'PERFORMANCE', 'factor': '낮은 성과 평가', 'score': 0.8}
            ]
        }
        
        try:
            alerts = alert_system.check_and_create_alerts(high_risk_employee, fake_analysis)
            print(f"생성된 알림 수: {len(alerts)}")
            
            for alert in alerts:
                print(f"- {alert.title} (심각도: {alert.get_severity_display()})")
                
        except Exception as e:
            print(f"알림 시스템 테스트 오류: {e}")

def test_retention_plan():
    """유지 계획 테스트"""
    print("\n유지 계획 생성 테스트 중...")
    
    # 고위험 직원의 위험도 레코드 조회 (또는 생성)
    high_risk_record = TurnoverRisk.objects.filter(
        risk_level__in=['CRITICAL', 'HIGH']
    ).first()
    
    # 위험도 레코드가 없으면 테스트용으로 생성
    if not high_risk_record:
        test_employee = Employee.objects.filter(employment_status='재직').first()
        if test_employee:
            high_risk_record = TurnoverRisk.objects.create(
                employee=test_employee,
                risk_level='CRITICAL',
                risk_score=0.85,
                confidence_level=0.8,
                primary_risk_factors=[{'type': 'TEST', 'factor': '테스트 위험 요소'}],
                ai_analysis={'test': True},
                ai_recommendations=['테스트 추천사항'],
                status='ACTIVE'
            )
    
    if high_risk_record:
        try:
            retention_plan = RetentionPlan.objects.create(
                turnover_risk=high_risk_record,
                title=f"{high_risk_record.employee.name} 유지 계획",
                description="고위험 직원에 대한 긴급 유지 계획",
                priority='URGENT',
                status='ACTIVE',
                start_date=date.today(),
                target_completion_date=date.today() + timedelta(days=30),
                action_items=[
                    {
                        'title': '1:1 면담 실시',
                        'description': '직속 상관과의 개별 면담을 통한 고민 파악',
                        'due_date': (date.today() + timedelta(days=3)).isoformat(),
                        'completed': False
                    },
                    {
                        'title': '성과 개선 지원',
                        'description': '성과 향상을 위한 멘토링 프로그램 배정',
                        'due_date': (date.today() + timedelta(days=7)).isoformat(),
                        'completed': False
                    },
                    {
                        'title': '보상 검토',
                        'description': '현재 급여 수준 및 승진 가능성 검토',
                        'due_date': (date.today() + timedelta(days=14)).isoformat(),
                        'completed': False
                    }
                ],
                success_metrics=[
                    '위험도 점수 0.5 이하로 감소',
                    '직무 만족도 조사 점수 3.5 이상',
                    '성과 평가 점수 3.0 이상'
                ],
                estimated_budget=Decimal('2000000')  # 200만원
            )
            
            print(f"유지 계획 생성됨: {retention_plan.title}")
            print(f"실행 항목: {len(retention_plan.action_items)}개")
            print(f"성공 지표: {len(retention_plan.success_metrics)}개")
            
        except Exception as e:
            print(f"유지 계획 생성 오류: {e}")
    else:
        print("고위험 직원의 위험도 레코드를 찾을 수 없습니다.")

def print_summary():
    """결과 요약 출력"""
    print("\n" + "="*60)
    print("AIRISS AI Quick Win Phase 3 테스트 결과 요약")
    print("="*60)
    
    # 위험도 분석 결과
    risk_records = TurnoverRisk.objects.filter(prediction_date__date=date.today())
    print(f"오늘 분석된 직원 수: {risk_records.count()}명")
    
    for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = risk_records.filter(risk_level=level).count()
        if count > 0:
            print(f"  - {dict(TurnoverRisk.RISK_LEVEL_CHOICES)[level]}: {count}명")
    
    # 알림 현황
    alerts = TurnoverAlert.objects.filter(created_at__date=date.today())
    print(f"\n오늘 생성된 알림: {alerts.count()}건")
    
    # 유지 계획 현황
    plans = RetentionPlan.objects.filter(status='ACTIVE')
    print(f"활성 유지 계획: {plans.count()}건")
    
    print("\n테스트 완료! 대시보드에서 확인하세요:")
    print("http://localhost:8000/ai-predictions/")

def main():
    """메인 실행 함수"""
    print("AIRISS AI Quick Win Phase 3 - 이직 위험도 분석 테스트")
    print("="*60)
    
    # 기존 테스트 데이터 정리
    print("기존 테스트 데이터 정리 중...")
    TurnoverRisk.objects.filter(prediction_date__date=date.today()).delete()
    TurnoverAlert.objects.filter(created_at__date=date.today()).delete()
    RetentionPlan.objects.filter(title__contains='테스트').delete()
    
    # 테스트 실행
    create_risk_factors()
    test_employees = get_sample_employees()
    analysis_results = test_risk_analysis()
    test_alert_system()
    test_retention_plan()
    
    # 결과 요약
    print_summary()

if __name__ == "__main__":
    main()