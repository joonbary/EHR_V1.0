"""
Production 환경의 직원 데이터 확인
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from employees.models import Employee
from django.db.models import Count

print("Production 직원 데이터 확인")
print("=" * 50)

# 전체 직원 수
total = Employee.objects.count()
print(f"전체 직원 수: {total}명")

# 회사별 통계
print("\n회사별 직원 수:")
company_stats = Employee.objects.values('company').annotate(count=Count('id')).order_by('-count')
for stat in company_stats[:10]:
    company = stat['company'] or '미지정'
    print(f"  {company}: {stat['count']}명")

# 최근 등록된 직원 확인
print("\n최근 등록된 직원 (이메일):")
recent = Employee.objects.order_by('-id')[:10]
for emp in recent:
    print(f"  {emp.name} - {emp.email}")

# 이메일 패턴 확인
print("\n이메일 패턴별 통계:")
email_patterns = {
    'emp0805': Employee.objects.filter(email__contains='emp0805').count(),
    'emp0001-emp1790': Employee.objects.filter(email__regex=r'emp\d{4}@').count(),
    '기타': Employee.objects.exclude(email__contains='emp').count()
}

for pattern, count in email_patterns.items():
    print(f"  {pattern}: {count}명")