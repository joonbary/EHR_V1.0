#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
이름 없는 잘못된 직원 데이터 삭제
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import connection

def delete_bad_employees():
    """이름 없는 직원 데이터 삭제"""
    
    print("=" * 80)
    print("잘못된 직원 데이터 삭제")
    print("=" * 80)
    
    # 현재 상태 확인
    total = Employee.objects.count()
    bad = Employee.objects.filter(name='').count()
    good = Employee.objects.exclude(name='').exclude(name__isnull=True).count()
    
    print(f"\n현재 상태:")
    print(f"  - 전체 직원: {total}명")
    print(f"  - 이름 없는 직원: {bad}명")
    print(f"  - 정상 직원: {good}명")
    
    if bad > 0:
        print(f"\n{bad}명의 잘못된 데이터를 삭제합니다...")
        
        # Raw SQL로 직접 삭제
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM employees_employee WHERE name = '' OR name IS NULL")
            deleted = cursor.rowcount
            print(f"  -> {deleted}개 레코드 삭제 완료")
    
    # 삭제 후 상태 확인
    final_total = Employee.objects.count()
    final_good = Employee.objects.exclude(name='').exclude(name__isnull=True).count()
    
    print(f"\n최종 상태:")
    print(f"  - 전체 직원: {final_total}명")
    print(f"  - 정상 직원: {final_good}명")
    
    print("\n" + "=" * 80)
    print("완료!")
    print("=" * 80)

if __name__ == "__main__":
    delete_bad_employees()