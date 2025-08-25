#!/usr/bin/env python
"""Railway의 AIRISS 데이터 확인"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from airiss.models import AIAnalysisResult
from employees.models import Employee

print("=" * 60)
print("Railway AIRISS 데이터 확인")
print("=" * 60)

# AIAnalysisResult 확인
airiss_count = AIAnalysisResult.objects.count()
print(f"\n1. AIAnalysisResult 총 개수: {airiss_count}")

if airiss_count > 0:
    # 샘플 데이터 확인
    sample = AIAnalysisResult.objects.first()
    print(f"\n2. 샘플 데이터:")
    print(f"   - ID: {sample.id}")
    print(f"   - Employee: {sample.employee.name if sample.employee else 'None'}")
    print(f"   - Score: {sample.score}")
    print(f"   - Analyzed at: {sample.analyzed_at}")

# Employee 확인
employee_count = Employee.objects.count()
print(f"\n3. Employee 총 개수: {employee_count}")

if employee_count > 0:
    # 샘플 직원 확인
    sample_emp = Employee.objects.first()
    print(f"\n4. 샘플 직원:")
    print(f"   - ID: {sample_emp.id}")
    print(f"   - Name: {sample_emp.name}")
    print(f"   - Department: {getattr(sample_emp, 'department', 'N/A')}")

print("\n" + "=" * 60)