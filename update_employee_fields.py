#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직원 데이터 부서/직급 수정
"""
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import transaction

print("=" * 80)
print("직원 데이터 부서/직급 수정")
print("=" * 80)

# 현재 상태
print("\n수정 전 상태:")
print(f"  전체 직원: {Employee.objects.count()}명")
print(f"  부서 없음: {Employee.objects.filter(department='').count() + Employee.objects.filter(department__isnull=True).count()}명")
print(f"  직급 없음: {Employee.objects.filter(position='').count() + Employee.objects.filter(position__isnull=True).count()}명")

# 엑셀 파일에서 데이터 읽어서 업데이트
excel_files = [
    'OK_employee_new_part1_08051039.xlsx',
    'OK_employee_new_part2_08051039.xlsx',
]

updated_count = 0
error_count = 0

for file_path in excel_files:
    if not os.path.exists(file_path):
        print(f"\n파일 없음: {file_path}")
        continue
    
    print(f"\n처리 중: {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    # 이메일로 직원 찾기
                    email = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                    
                    if not email or '@' not in email:
                        continue
                    
                    try:
                        employee = Employee.objects.get(email=email)
                    except Employee.DoesNotExist:
                        continue
                    
                    updated = False
                    
                    # 부서 업데이트 (3번 컬럼)
                    if pd.notna(row.iloc[3]):
                        dept = str(row.iloc[3]).strip()
                        if dept and dept != '-' and dept != 'nan':
                            # 부서명에서 department 필드 매핑
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
                            updated = True
                    
                    # 최종소속 업데이트 (8번 컬럼)
                    if pd.notna(row.iloc[8]):
                        final_dept = str(row.iloc[8]).strip()
                        if final_dept and final_dept != '-' and final_dept != 'nan':
                            employee.final_department = final_dept[:100]
                            updated = True
                    
                    # 직급 업데이트 (9번 컬럼)
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
                            elif '과장' in position:
                                employee.position = 'MANAGER'
                            elif '차장' in position:
                                employee.position = 'MANAGER'
                            elif '부장' in position:
                                employee.position = 'DIRECTOR'
                            elif '이사' in position or '대표' in position or '임원' in position:
                                employee.position = 'EXECUTIVE'
                            else:
                                # 기본값
                                employee.position = 'STAFF'
                            updated = True
                    
                    # 직책 업데이트 (10번 컬럼)
                    if pd.notna(row.iloc[10]):
                        job_title = str(row.iloc[10]).strip()
                        if job_title and job_title != 'nan' and job_title != '해당없음':
                            employee.job_title = job_title[:50]
                            updated = True
                    
                    if updated:
                        employee.save()
                        updated_count += 1
                        
                        if updated_count % 100 == 0:
                            print(f"  진행: {updated_count}명 업데이트")
                
                except Exception as e:
                    error_count += 1
                    if error_count <= 3:
                        print(f"  오류 (행 {idx}): {e}")
        
        print(f"  완료: 이 파일에서 업데이트됨")
        
    except Exception as e:
        print(f"  파일 오류: {e}")

# 최종 확인
print(f"\n총 {updated_count}명 업데이트")

print("\n수정 후 상태:")
print(f"  전체 직원: {Employee.objects.count()}명")
print(f"  부서 없음: {Employee.objects.filter(department='').count() + Employee.objects.filter(department__isnull=True).count()}명")
print(f"  직급 없음: {Employee.objects.filter(position='').count() + Employee.objects.filter(position__isnull=True).count()}명")

# 분포 확인
from django.db.models import Count

print("\n부서 분포:")
dept_stats = Employee.objects.values('department').annotate(count=Count('id')).order_by('-count')
for stat in dept_stats:
    if stat['department']:
        print(f"  {stat['department']}: {stat['count']}명")

print("\n직급 분포:")
pos_stats = Employee.objects.values('position').annotate(count=Count('id')).order_by('-count')
for stat in pos_stats:
    if stat['position']:
        print(f"  {stat['position']}: {stat['count']}명")

print("\n샘플 직원 (5명):")
for emp in Employee.objects.exclude(department='').exclude(position='')[:5]:
    print(f"  {emp.name}: {emp.department}/{emp.position} ({emp.final_department}/{emp.current_position})")