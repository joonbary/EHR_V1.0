#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
잘못 업로드된 데이터 제거 (emp_upload_250801.xlsx에서 온 데이터)
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import connection

print("=" * 80)
print("잘못 업로드된 데이터 제거")
print("=" * 80)

# PL, Non-PL 등 직군 정보가 이름에 들어간 데이터 확인
wrong_data = Employee.objects.filter(name__in=['PL', 'Non-PL'])
wrong_count = wrong_data.count()

print(f"\n잘못된 데이터:")
print(f"  - PL이 이름인 직원: {Employee.objects.filter(name='PL').count()}명")
print(f"  - Non-PL이 이름인 직원: {Employee.objects.filter(name='Non-PL').count()}명")

# 정상 데이터 (한글 이름) 확인
# 한글이 포함된 이름만 정상으로 간주
normal_count = 0
for emp in Employee.objects.all()[:100]:
    if emp.name and any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in emp.name):
        normal_count += 1

print(f"\n샘플 100명 중 한글 이름: {normal_count}명")

# emp_upload_250801.xlsx에서 온 것으로 추정되는 데이터 삭제
# (PL, Non-PL이 이름인 데이터 + 기타 부서명이 이름으로 들어간 데이터)
delete_names = ['PL', 'Non-PL']

print(f"\n삭제 대상: {delete_names}")

total_deleted = 0
with connection.cursor() as cursor:
    for name in delete_names:
        cursor.execute("DELETE FROM employees_employee WHERE name = %s", [name])
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"  '{name}': {deleted}명 삭제")
            total_deleted += deleted

print(f"\n총 {total_deleted}명 삭제")

# 최종 확인
final_total = Employee.objects.count()
print(f"\n최종 직원 수: {final_total}명")

# 샘플 데이터 확인
print("\n정상 데이터 샘플 (5명):")
for emp in Employee.objects.exclude(name__in=['PL', 'Non-PL']).order_by('id')[:5]:
    print(f"  - {emp.name} ({emp.company}/{emp.department}) - {emp.email}")

print("\n" + "=" * 80)