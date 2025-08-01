"""
수동으로 변경사항 계산
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.api_views_workforce import calculate_workforce_changes
from datetime import date

# 오늘 날짜로 변경사항 계산
result = calculate_workforce_changes(date.today())
print(f"Calculation result: {result}")

# 결과 확인
from employees.models_workforce import WeeklyWorkforceChange
count = WeeklyWorkforceChange.objects.count()
print(f"Total change records: {count}")

# 샘플 데이터 출력
if count > 0:
    changes = WeeklyWorkforceChange.objects.all()[:5]
    for change in changes:
        print(f"\n{change.company} - {change.job_group} - {change.grade}")
        print(f"  Current: {change.current_headcount}, Base: {change.base_headcount}")
        print(f"  Base type: {change.base_type}")