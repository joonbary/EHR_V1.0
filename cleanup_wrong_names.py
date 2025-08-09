#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
잘못된 이름 데이터 정리
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import connection

print("=" * 80)
print("잘못된 이름 데이터 정리")
print("=" * 80)

# 잘못된 이름 패턴
wrong_names = ['PL', 'Non-PL', '관타', '지점', '아시아', 'NPL영업1팀', 'NPL영업2팀', 
               'PL영업팀', '채권관리팀', '온라인금융실', '경영지원팀', '금융소비자보호팀']

# 잘못된 이름을 가진 직원 수 확인
for name in wrong_names:
    count = Employee.objects.filter(name=name).count()
    if count > 0:
        print(f"  '{name}': {count}명 삭제 예정")

# 삭제 실행
total_deleted = 0
with connection.cursor() as cursor:
    for name in wrong_names:
        cursor.execute("DELETE FROM employees_employee WHERE name = %s", [name])
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"  '{name}': {deleted}명 삭제 완료")
            total_deleted += deleted

print(f"\n총 {total_deleted}명 삭제")

# 최종 확인
final_total = Employee.objects.count()
print(f"\n최종 직원 수: {final_total}명")

print("\n" + "=" * 80)