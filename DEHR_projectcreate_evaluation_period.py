#\!/usr/bin/env python
"""
평가 기간 생성 스크립트
"""

import os
import sys
import django
from datetime import date, timedelta

# Django 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehr_evaluation.settings")
django.setup()

from evaluations.models import EvaluationPeriod

def create_evaluation_period():
    """활성 평가 기간 생성"""
    
    # 기존 활성 평가 기간이 있는지 확인
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if active_period:
        print(f"이미 활성 평가 기간이 있습니다: {active_period.name}")
        return active_period
    
    # 새 평가 기간 생성
    today = date.today()
    start_date = today - timedelta(days=30)  # 30일 전부터
    end_date = today + timedelta(days=60)    # 60일 후까지
    
    period = EvaluationPeriod.objects.create(
        name="2024년 하반기 평가",
        start_date=start_date,
        end_date=end_date,
        is_active=True,
        description="2024년 하반기 성과평가 기간입니다."
    )
    
    print(f"새 평가 기간이 생성되었습니다: {period.name}")
    print(f"기간: {period.start_date} ~ {period.end_date}")
    print(f"활성 상태: {period.is_active}")
    
    # 기존의 다른 평가 기간들은 비활성화
    EvaluationPeriod.objects.exclude(id=period.id).update(is_active=False)
    print("다른 평가 기간들은 비활성화되었습니다.")
    
    return period

if __name__ == "__main__":
    try:
        period = create_evaluation_period()
        print("\n평가 기간 생성이 완료되었습니다\!")
        
        # 모든 평가 기간 출력
        print("\n현재 평가 기간 목록:")
        for p in EvaluationPeriod.objects.all():
            status = "✓ 활성" if p.is_active else "  비활성"
            print(f"{status} | {p.name} | {p.start_date} ~ {p.end_date}")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        sys.exit(1)

