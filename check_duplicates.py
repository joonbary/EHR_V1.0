#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
중복 데이터 확인
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db.models import Count

print("=" * 80)
print("직원 데이터 중복 확인")
print("=" * 80)

# 전체 직원 수
total = Employee.objects.count()
print(f"\n전체 직원 수: {total}명")

# 이메일 중복 확인
email_duplicates = Employee.objects.values('email').annotate(count=Count('id')).filter(count__gt=1)
print(f"\n중복된 이메일: {email_duplicates.count()}개")

if email_duplicates:
    print("\n중복된 이메일 샘플 (상위 5개):")
    for dup in email_duplicates[:5]:
        print(f"  {dup['email']}: {dup['count']}번")
        # 해당 이메일의 직원들 확인
        employees = Employee.objects.filter(email=dup['email'])[:3]
        for emp in employees:
            print(f"    - ID: {emp.id}, 이름: {emp.name}, 회사: {emp.company}")

# 이름 중복 확인
name_duplicates = Employee.objects.values('name').annotate(count=Count('id')).filter(count__gt=1).order_by('-count')
print(f"\n동명이인: {name_duplicates.count()}명")

if name_duplicates:
    print("\n동명이인 상위 5명:")
    for dup in name_duplicates[:5]:
        print(f"  {dup['name']}: {dup['count']}명")

# 유니크한 이메일 수
unique_emails = Employee.objects.values('email').distinct().count()
print(f"\n고유한 이메일 수: {unique_emails}개")

# 중복 제거시 실제 직원 수
print(f"\n실제 직원 수 (중복 제거): {unique_emails}명")

print("\n" + "=" * 80)