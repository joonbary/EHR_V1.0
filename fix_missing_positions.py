#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
누락된 직급 데이터 수정
"""
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import transaction

print("=" * 80)
print("누락된 직급 데이터 수정")
print("=" * 80)

# 직급이 없는 직원들 확인
no_position = Employee.objects.filter(position='') | Employee.objects.filter(position__isnull=True)
print(f"\n직급 없는 직원: {no_position.count()}명")

# 엑셀 파일에서 직급 정보 다시 읽기
excel_files = [
    'OK_employee_new_part1_08051039.xlsx',
    'OK_employee_new_part2_08051039.xlsx',
]

updated_count = 0

for file_path in excel_files:
    if not os.path.exists(file_path):
        continue
    
    print(f"\n처리 중: {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    email = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                    
                    if not email or '@' not in email:
                        continue
                    
                    try:
                        employee = Employee.objects.get(email=email)
                        
                        # 직급이 비어있는 경우만 업데이트
                        if not employee.position or employee.position == '':
                            # 9번 컬럼: 직급
                            if pd.notna(row.iloc[9]):
                                position = str(row.iloc[9]).strip()
                                if position and position != 'nan':
                                    # current_position에 원본 저장
                                    employee.current_position = position[:50]
                                    
                                    # position 필드 매핑
                                    if '사원' in position:
                                        employee.position = 'STAFF'
                                    elif '대리' in position:
                                        employee.position = 'SENIOR'
                                    elif '과장' in position or '차장' in position:
                                        employee.position = 'MANAGER'
                                    elif '부장' in position:
                                        employee.position = 'DIRECTOR'
                                    elif '이사' in position or '대표' in position or '임원' in position:
                                        employee.position = 'EXECUTIVE'
                                    else:
                                        # 기본값을 STAFF로 설정
                                        employee.position = 'STAFF'
                                    
                                    employee.save()
                                    updated_count += 1
                            else:
                                # 직급 정보가 없으면 기본값 설정
                                employee.position = 'STAFF'
                                employee.save()
                                updated_count += 1
                        
                        # 부서가 비어있는 경우도 체크
                        if not employee.department or employee.department == '':
                            if pd.notna(row.iloc[3]):
                                dept = str(row.iloc[3]).strip()
                                if dept == '-' or dept == 'nan' or not dept:
                                    employee.department = 'OTHER'
                                else:
                                    # 부서명 매핑
                                    if 'IT' in dept or '디지털' in dept or '데이터' in dept:
                                        employee.department = 'IT'
                                    elif 'HR' in dept or '인사' in dept or '인재' in dept:
                                        employee.department = 'HR'
                                    elif '재무' in dept or '회계' in dept or '경리' in dept:
                                        employee.department = 'FINANCE'
                                    elif '영업' in dept or '세일즈' in dept or 'NPL' in dept or 'PL' in dept:
                                        employee.department = 'SALES'
                                    elif '마케팅' in dept or '홍보' in dept or '브랜드' in dept:
                                        employee.department = 'MARKETING'
                                    else:
                                        employee.department = 'OTHER'
                            else:
                                employee.department = 'OTHER'
                            
                            employee.save()
                        
                        if updated_count % 100 == 0 and updated_count > 0:
                            print(f"  진행: {updated_count}명 업데이트")
                    
                    except Employee.DoesNotExist:
                        continue
                
                except Exception as e:
                    continue
        
    except Exception as e:
        print(f"  파일 오류: {e}")

# 남은 빈 직급들은 모두 STAFF로 설정
remaining = Employee.objects.filter(position='') | Employee.objects.filter(position__isnull=True)
if remaining.exists():
    print(f"\n남은 빈 직급 {remaining.count()}명을 STAFF로 설정")
    remaining.update(position='STAFF')
    updated_count += remaining.count()

# 남은 빈 부서들은 모두 OTHER로 설정
remaining_dept = Employee.objects.filter(department='') | Employee.objects.filter(department__isnull=True)
if remaining_dept.exists():
    print(f"남은 빈 부서 {remaining_dept.count()}명을 OTHER로 설정")
    remaining_dept.update(department='OTHER')

print(f"\n총 {updated_count}명 업데이트")

# 최종 확인
from django.db.models import Count

print("\n최종 상태:")
print(f"  전체 직원: {Employee.objects.count()}명")

print("\n부서 분포:")
dept_stats = Employee.objects.values('department').annotate(count=Count('id')).order_by('-count')
for stat in dept_stats:
    print(f"  {stat['department'] or '없음'}: {stat['count']}명")

print("\n직급 분포:")
pos_stats = Employee.objects.values('position').annotate(count=Count('id')).order_by('-count')
for stat in pos_stats:
    print(f"  {stat['position'] or '없음'}: {stat['count']}명")

print("\n샘플 직원 (10명):")
for emp in Employee.objects.all()[:10]:
    print(f"  {emp.name}: {emp.department}/{emp.position}")