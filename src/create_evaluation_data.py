# create_evaluation_data.py
import os
import django
from datetime import date
from decimal import Decimal

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from evaluations.models import (
    EvaluationPeriod, Task, ContributionEvaluation,
    ExpertiseEvaluation, ImpactEvaluation, ComprehensiveEvaluation
)

def create_evaluation_data():
    """평가 데이터 생성"""
    print("\n=== OK금융그룹 평가 데이터 생성 시작 ===\n")
    
    # 1. 평가기간 생성
    print("1. 평가기간 생성")
    try:
        period_q4, created = EvaluationPeriod.objects.get_or_create(
            year=2024,
            period_type='Q4',
            defaults={
                'start_date': date(2024, 10, 1),
                'end_date': date(2024, 12, 31),
                'is_active': True,
                'status': 'ONGOING'
            }
        )
        print(f"  {'✓ 생성' if created else '○ 이미 존재'}: 2024년 Q4")
        
        period_annual, created = EvaluationPeriod.objects.get_or_create(
            year=2024,
            period_type='ANNUAL',
            defaults={
                'start_date': date(2024, 1, 1),
                'end_date': date(2024, 12, 31),
                'status': 'ONGOING'
            }
        )
        print(f"  {'✓ 생성' if created else '○ 이미 존재'}: 2024년 연간")
        
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return
    
    # 2. 직원 조회
    print("\n2. 직원 데이터 확인")
    try:
        kim_cs = Employee.objects.get(email='kim.cs@okfinance.co.kr')
        park_yh = Employee.objects.get(email='park.yh@okfinance.co.kr')
        team_leader = Employee.objects.get(email='lee.team@okfinance.co.kr')
        print(f"  ✓ 김철수 (지점장)")
        print(f"  ✓ 박영희 (과장)")
        print(f"  ✓ 이팀장 (팀장)")
    except Employee.DoesNotExist as e:
        print(f"  ❌ 직원을 찾을 수 없습니다: {e}")
        print("  먼저 직원 데이터를 생성해주세요.")
        return
    
    # 3. 김철수 Task 생성
    print("\n3. 김철수 Task 생성")
    tasks_data = [
        {
            'title': '○○동 오피스텔 PF',
            'weight': Decimal('10'),
            'target': Decimal('300'),
            'actual': Decimal('80')
        },
        {
            'title': '○○동 클루센터 B/L',
            'weight': Decimal('30'),
            'target': Decimal('300'),
            'actual': Decimal('50')
        },
        {
            'title': '○○동 오피스텔 종도금대출',
            'weight': Decimal('30'),
            'target': Decimal('300'),
            'actual': Decimal('200')
        },
        {
            'title': '○○동 상가담보대출',
            'weight': Decimal('30'),
            'target': Decimal('300'),
            'actual': Decimal('20')
        }
    ]
    
    for task_data in tasks_data:
        task, created = Task.objects.get_or_create(
            employee=kim_cs,
            evaluation_period=period_q4,
            title=task_data['title'],
            defaults={
                'weight': task_data['weight'],
                'contribution_method': '리딩',
                'target_value': task_data['target'],
                'target_unit': '억원',
                'actual_value': task_data['actual'],
                'status': 'COMPLETED'
            }
        )
        if created:
            task.calculate_achievement_rate()
            task.save()
            print(f"  ✓ {task.title} (달성률: {task.achievement_rate}%)")
        else:
            print(f"  ○ {task.title} (이미 존재)")
    
    # 4. 김철수 평가 생성
    print("\n4. 김철수 평가 데이터 생성")
    
    # 기여도 평가
    contrib_kim, created = ContributionEvaluation.objects.get_or_create(
        employee=kim_cs,
        evaluation_period=period_q4,
        defaults={
            'total_achievement_rate': Decimal('117'),
            'contribution_score': Decimal('4.0'),
            'is_achieved': True,
            'evaluator': team_leader,
            'comments': '목표 초과 달성으로 우수한 기여도'
        }
    )
    print(f"  {'✓' if created else '○'} 기여도 평가: 달성 (4점)")
    
    # 전문성 평가
    expertise_kim, created = ExpertiseEvaluation.objects.get_or_create(
        employee=kim_cs,
        evaluation_period=period_annual,
        defaults={
            'required_level': kim_cs.growth_level,
            'strategic_contribution': 3,
            'interactive_contribution': 3,
            'technical_expertise': 3,
            'business_understanding': 3,
            'total_score': Decimal('3.0'),
            'is_achieved': True,
            'evaluator': team_leader
        }
    )
    print(f"  {'✓' if created else '○'} 전문성 평가: 달성 (3점)")
    
    # 영향력 평가 (미달성)
    impact_kim, created = ImpactEvaluation.objects.get_or_create(
        employee=kim_cs,
        evaluation_period=period_annual,
        defaults={
            'customer_focus': 3,
            'collaboration': 3,
            'innovation': 2,
            'team_leadership': 3,
            'organizational_impact': 2,
            'external_networking': 2,
            'total_score': Decimal('2.5'),
            'is_achieved': False,
            'evaluator': team_leader
        }
    )
    print(f"  {'✓' if created else '○'} 영향력 평가: 미달성 (2.5점)")
    
    # 종합 평가
    comp_kim, created = ComprehensiveEvaluation.objects.get_or_create(
        employee=kim_cs,
        evaluation_period=period_annual,
        defaults={
            'contribution_evaluation': contrib_kim,
            'expertise_evaluation': expertise_kim,
            'impact_evaluation': impact_kim,
            'contribution_achieved': True,
            'expertise_achieved': True,
            'impact_achieved': False,
            'manager': team_leader,
            'manager_comments': '기여도와 전문성은 우수하나 영향력 부분 개선 필요',
            'status': 'COMPLETED'
        }
    )
    if created:
        comp_kim.auto_calculate_manager_grade()
        comp_kim.save()
    print(f"  {'✓' if created else '○'} 종합평가: {comp_kim.manager_grade}등급 (2/3 달성)")
    
    # 5. 박영희 평가 생성
    print("\n5. 박영희 평가 데이터 생성")
    
    # 박영희 Task 생성
    park_tasks = [
        {
            'title': '중소기업 대출 상담',
            'weight': Decimal('40'),
            'target': Decimal('50'),
            'actual': Decimal('55')
        },
        {
            'title': '신규 고객 유치',
            'weight': Decimal('30'),
            'target': Decimal('20'),
            'actual': Decimal('22')
        },
        {
            'title': '기존 고객 관리',
            'weight': Decimal('30'),
            'target': Decimal('100'),
            'actual': Decimal('98')
        }
    ]
    
    for task_data in park_tasks:
        task, created = Task.objects.get_or_create(
            employee=park_yh,
            evaluation_period=period_q4,
            title=task_data['title'],
            defaults={
                'weight': task_data['weight'],
                'contribution_method': '리딩',
                'target_value': task_data['target'],
                'target_unit': '건',
                'actual_value': task_data['actual'],
                'status': 'COMPLETED'
            }
        )
        if created:
            task.calculate_achievement_rate()
            task.save()
    
    # 기여도 평가
    contrib_park, created = ContributionEvaluation.objects.get_or_create(
        employee=park_yh,
        evaluation_period=period_q4,
        defaults={
            'total_achievement_rate': Decimal('105'),
            'contribution_score': Decimal('3.0'),
            'is_achieved': True,
            'evaluator': team_leader
        }
    )
    print(f"  {'✓' if created else '○'} 기여도 평가: 달성 (3점)")
    
    # 전문성 평가
    expertise_park, created = ExpertiseEvaluation.objects.get_or_create(
        employee=park_yh,
        evaluation_period=period_annual,
        defaults={
            'required_level': park_yh.growth_level,
            'strategic_contribution': 3,
            'interactive_contribution': 3,
            'technical_expertise': 3,
            'business_understanding': 3,
            'total_score': Decimal('3.0'),
            'is_achieved': True,
            'evaluator': team_leader
        }
    )
    print(f"  {'✓' if created else '○'} 전문성 평가: 달성 (3점)")
    
    # 영향력 평가
    impact_park, created = ImpactEvaluation.objects.get_or_create(
        employee=park_yh,
        evaluation_period=period_annual,
        defaults={
            'customer_focus': 3,
            'collaboration': 3,
            'innovation': 3,
            'team_leadership': 3,
            'organizational_impact': 3,
            'external_networking': 3,
            'total_score': Decimal('3.0'),
            'is_achieved': True,
            'evaluator': team_leader
        }
    )
    print(f"  {'✓' if created else '○'} 영향력 평가: 달성 (3점)")
    
    # 종합 평가
    comp_park, created = ComprehensiveEvaluation.objects.get_or_create(
        employee=park_yh,
        evaluation_period=period_annual,
        defaults={
            'contribution_evaluation': contrib_park,
            'expertise_evaluation': expertise_park,
            'impact_evaluation': impact_park,
            'contribution_achieved': True,
            'expertise_achieved': True,
            'impact_achieved': True,
            'manager': team_leader,
            'manager_comments': '모든 영역에서 우수한 성과',
            'status': 'COMPLETED'
        }
    )
    if created:
        comp_park.auto_calculate_manager_grade()
        comp_park.save()
    print(f"  {'✓' if created else '○'} 종합평가: {comp_park.manager_grade}등급 (3/3 달성)")
    
    # 6. 결과 요약
    print("\n=== 평가 데이터 생성 완료 ===")
    print(f"평가기간: {EvaluationPeriod.objects.count()}개")
    print(f"Task: {Task.objects.count()}개")
    print(f"기여도 평가: {ContributionEvaluation.objects.count()}개")
    print(f"전문성 평가: {ExpertiseEvaluation.objects.count()}개")
    print(f"영향력 평가: {ImpactEvaluation.objects.count()}개")
    print(f"종합 평가: {ComprehensiveEvaluation.objects.count()}개")
    
    print("\n평가 결과 요약:")
    for comp in ComprehensiveEvaluation.objects.all():
        achieved = []
        if comp.contribution_achieved:
            achieved.append('기여도')
        if comp.expertise_achieved:
            achieved.append('전문성')
        if comp.impact_achieved:
            achieved.append('영향력')
        
        print(f"  {comp.employee.name}: {comp.manager_grade}등급 - {', '.join(achieved)} 달성")

if __name__ == '__main__':
    create_evaluation_data() 