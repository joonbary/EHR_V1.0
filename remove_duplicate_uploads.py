#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
중복 업로드된 데이터 제거 - 이메일 기준으로 최신 것만 남기기
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import connection

print("=" * 80)
print("중복 업로드 데이터 정리")
print("=" * 80)

# 현재 상태
total_before = Employee.objects.count()
print(f"\n정리 전 직원 수: {total_before}명")

# 각 이메일별로 가장 최근 ID(최신 데이터)만 남기고 나머지 삭제
with connection.cursor() as cursor:
    # 중복된 이메일별로 최신 ID를 제외한 나머지 삭제
    cursor.execute("""
        DELETE FROM employees_employee
        WHERE id NOT IN (
            SELECT MAX(id) 
            FROM employees_employee 
            GROUP BY email
        )
    """)
    deleted = cursor.rowcount
    print(f"\n삭제된 중복 데이터: {deleted}명")

# 정리 후 상태
total_after = Employee.objects.count()
print(f"\n정리 후 직원 수: {total_after}명")

# 샘플 데이터 확인
print("\n직원 데이터 샘플 (10명):")
for emp in Employee.objects.all().order_by('id')[:10]:
    print(f"  - {emp.name} ({emp.company}/{emp.department}) - {emp.email}")

print("\n" + "=" * 80)
print(f"목표: 1,790명")
print(f"현재: {total_after}명")
if total_after == 1790:
    print("✅ 목표 달성!")
else:
    print(f"차이: {total_after - 1790}명")
print("=" * 80)