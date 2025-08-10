"""
평가 기간 생성 스크립트
"""
import os
import sys
import django
from datetime import date, datetime

# UTF-8 인코딩 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from evaluations.models import EvaluationPeriod

def create_evaluation_periods():
    """평가 기간 생성"""
    
    # 현재 연도
    current_year = 2024
    
    # 2024년 4분기 평가 기간 생성 (활성화)
    q4_period, created = EvaluationPeriod.objects.get_or_create(
        year=current_year,
        period_type='Q4',
        defaults={
            'start_date': date(2024, 10, 1),
            'end_date': date(2024, 12, 31),
            'is_active': True,
            'status': 'ONGOING'
        }
    )
    
    if created:
        print(f"✅ 2024년 4분기 평가 기간 생성 완료 (활성화)")
    else:
        # 기존 기간 활성화
        q4_period.is_active = True
        q4_period.status = 'ONGOING'
        q4_period.save()
        print(f"✅ 2024년 4분기 평가 기간 활성화 완료")
    
    # 이전 분기들도 생성 (비활성화)
    quarters = [
        ('Q1', date(2024, 1, 1), date(2024, 3, 31), 'COMPLETED'),
        ('Q2', date(2024, 4, 1), date(2024, 6, 30), 'COMPLETED'),
        ('Q3', date(2024, 7, 1), date(2024, 9, 30), 'COMPLETED'),
    ]
    
    for period_type, start_date, end_date, status in quarters:
        period, created = EvaluationPeriod.objects.get_or_create(
            year=current_year,
            period_type=period_type,
            defaults={
                'start_date': start_date,
                'end_date': end_date,
                'is_active': False,
                'status': status
            }
        )
        if created:
            print(f"✅ 2024년 {period_type} 평가 기간 생성 완료")
    
    # 2024년 연간 평가 기간 생성
    annual_period, created = EvaluationPeriod.objects.get_or_create(
        year=current_year,
        period_type='ANNUAL',
        defaults={
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 12, 31),
            'is_active': False,
            'status': 'ONGOING'
        }
    )
    
    if created:
        print(f"✅ 2024년 연간 평가 기간 생성 완료")
    
    # 전체 평가 기간 확인
    all_periods = EvaluationPeriod.objects.all()
    print(f"\n📊 전체 평가 기간: {all_periods.count()}개")
    for period in all_periods:
        status = "🟢 활성화" if period.is_active else "⚪ 비활성화"
        print(f"  - {period} ({period.status}) {status}")

if __name__ == "__main__":
    print("=" * 60)
    print("평가 기간 생성 시작")
    print("=" * 60)
    
    try:
        create_evaluation_periods()
        print("\n✅ 평가 기간 생성 완료!")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()