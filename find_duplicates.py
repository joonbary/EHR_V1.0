#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db.models import Count

print("중복 데이터 상세 분석")
print("=" * 60)

# 이메일 중복 확인
duplicated_emails = Employee.objects.values('email').annotate(count=Count('id')).filter(count__gt=1)
if duplicated_emails:
    print(f"\n중복된 이메일: {duplicated_emails.count()}개")
    for dup in duplicated_emails[:3]:
        print(f"  {dup['email']}: {dup['count']}번 중복")
        
        # 해당 이메일의 직원들 확인
        emps = Employee.objects.filter(email=dup['email'])[:2]
        for emp in emps:
            print(f"    - ID:{emp.id}, 이름:{emp.name}, 회사:{emp.company}")
else:
    print("\n이메일 중복 없음")

# 전체 통계
total = Employee.objects.count()
unique_emails = Employee.objects.values('email').distinct().count()

print(f"\n전체 직원: {total}명")
print(f"고유 이메일: {unique_emails}개")
print(f"중복으로 인한 초과: {total - unique_emails}명")

# 원본 엑셀 파일 행 수와 비교
print(f"\n원본 엑셀 데이터:")
print(f"  - OK_employee_new_part1: 900명")
print(f"  - OK_employee_new_part2: 890명")
print(f"  - 합계: 1,790명")
print(f"\n현재 DB와 차이: {total - 1790}명 초과")