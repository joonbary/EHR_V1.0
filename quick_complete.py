#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
빠른 완성 업로드 - bulk_create 사용
"""
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import transaction

print("=" * 80)
print("빠른 완성 업로드")
print("=" * 80)

# 현재 상태
current = Employee.objects.count()
print(f"현재: {current}명, 목표: 1,790명, 부족: {1790 - current}명")

if current >= 1790:
    print("이미 목표 달성!")
    exit()

# 기존 이메일 목록
existing_emails = set(Employee.objects.values_list('email', flat=True))
print(f"기존 이메일: {len(existing_emails)}개")

# 엑셀에서 누락된 직원 찾기
new_employees = []

for file_path in ['OK_employee_new_part1_08051039.xlsx', 'OK_employee_new_part2_08051039.xlsx']:
    if not os.path.exists(file_path):
        continue
    
    df = pd.read_excel(file_path)
    
    for idx, row in df.iterrows():
        name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
        email = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
        
        if not name or name in ['성명', '이름', 'nan'] or not email or '@' not in email:
            continue
        
        if email not in existing_emails:
            emp = Employee(
                name=name[:100],
                email=email[:254],
                employment_status='재직',
                employment_type='정규직',
                phone='010-0000-0000',
                department='OTHER',
                position='STAFF'
            )
            
            # 회사
            if len(row) > 5 and pd.notna(row.iloc[5]):
                company = str(row.iloc[5]).strip()
                if company in ['OK', 'OC', 'OCI', 'OFI', 'OKDS', 'OKH', 'ON', 'OKIP', 'OT', 'OKV', 'EX']:
                    emp.company = company
            
            new_employees.append(emp)
            existing_emails.add(email)
            
            if len(new_employees) >= (1790 - current):
                break
    
    if len(new_employees) >= (1790 - current):
        break

print(f"\n추가할 직원: {len(new_employees)}명")

if new_employees:
    with transaction.atomic():
        Employee.objects.bulk_create(new_employees, batch_size=100)
    print("업로드 완료!")

# 최종 확인
final = Employee.objects.count()
print(f"\n최종: {final}명")
print("✅ 성공!" if final >= 1790 else f"⚠️ {1790 - final}명 부족")