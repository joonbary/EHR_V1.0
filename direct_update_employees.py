#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직원 데이터 직접 업데이트 - 이름 없는 데이터 수정
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import transaction

def direct_update():
    """직원 데이터 직접 업데이트"""
    
    print("=" * 80)
    print("직원 데이터 직접 업데이트")
    print("=" * 80)
    
    # 이름이 없는 직원들 가져오기
    empty_name_employees = Employee.objects.filter(name='').order_by('id')
    print(f"\n이름이 없는 직원: {empty_name_employees.count()}명")
    
    # 엑셀 파일에서 데이터 읽기
    excel_files = [
        'OK_employee_new_part1_08051039.xlsx',
        'OK_employee_new_part2_08051039.xlsx',
    ]
    
    all_data = []
    
    for file_path in excel_files:
        if not os.path.exists(file_path):
            continue
        
        print(f"\n파일 읽기: {file_path}")
        df = pd.read_excel(file_path)
        
        for idx, row in df.iterrows():
            # 컬럼명이 깨져있을 수 있으므로 인덱스로도 접근
            name = str(row.iloc[0] if len(row) > 0 else row.get('성명', '')).strip()
            email = str(row.iloc[1] if len(row) > 1 else row.get('이메일', '')).strip()
            
            if name and name != 'nan' and email and email != 'nan':
                data = {
                    'name': name[:100],
                    'email': email[:254],
                }
                
                # 회사 (5번 인덱스)
                if len(row) > 5:
                    company = str(row.iloc[5]).strip()
                    if company and company != 'nan':
                        data['company'] = company[:10]
                
                # 부서 (8번 인덱스 - 최종소속)
                if len(row) > 8:
                    dept = str(row.iloc[8]).strip()
                    if dept and dept != 'nan' and dept != '-':
                        data['final_department'] = dept[:100]
                        
                        # department 필드 매핑
                        if 'IT' in dept or '개발' in dept or '디지털' in dept:
                            data['department'] = 'IT'
                        elif 'HR' in dept or '인사' in dept:
                            data['department'] = 'HR'
                        elif '재무' in dept or '회계' in dept:
                            data['department'] = 'FINANCE'
                        elif '영업' in dept:
                            data['department'] = 'SALES'
                        elif '마케팅' in dept:
                            data['department'] = 'MARKETING'
                        elif 'NPL' in dept or '채권' in dept or '운영' in dept:
                            data['department'] = 'OPERATIONS'
                        else:
                            data['department'] = 'OTHER'
                
                # 직급 (9번 인덱스)
                if len(row) > 9:
                    position = str(row.iloc[9]).strip()
                    if position and position != 'nan':
                        data['current_position'] = position[:50]
                        
                        # position 필드 매핑
                        if '사원' in position:
                            data['position'] = 'STAFF'
                        elif '대리' in position:
                            data['position'] = 'SENIOR'
                        elif '과장' in position or '차장' in position:
                            data['position'] = 'MANAGER'
                        elif '부장' in position:
                            data['position'] = 'DIRECTOR'
                        elif '임원' in position or '이사' in position:
                            data['position'] = 'EXECUTIVE'
                        else:
                            data['position'] = 'STAFF'
                
                # 입사일 (2번 인덱스)
                if len(row) > 2:
                    hire_date_val = row.iloc[2]
                    if pd.notna(hire_date_val):
                        try:
                            if hasattr(hire_date_val, 'date'):
                                data['hire_date'] = hire_date_val.date()
                        except:
                            pass
                
                # 성별 (11번 인덱스)
                if len(row) > 11:
                    gender = str(row.iloc[11]).strip()
                    if '남' in gender or gender == 'M':
                        data['gender'] = 'M'
                    elif '여' in gender or gender == 'F':
                        data['gender'] = 'F'
                
                # 나이 (12번 인덱스)
                if len(row) > 12:
                    try:
                        age = int(float(str(row.iloc[12])))
                        if 20 <= age <= 70:
                            data['age'] = age
                    except:
                        pass
                
                all_data.append(data)
    
    print(f"\n총 {len(all_data)}개 데이터 준비됨")
    
    # 이메일로 매칭하여 업데이트
    updated_count = 0
    with transaction.atomic():
        for data in all_data:
            try:
                # 이메일로 찾아서 업데이트
                emp = Employee.objects.filter(email=data['email']).first()
                if emp:
                    emp.name = data.get('name', emp.name)
                    emp.company = data.get('company', emp.company)
                    emp.department = data.get('department', emp.department)
                    emp.final_department = data.get('final_department', emp.final_department)
                    emp.position = data.get('position', emp.position)
                    emp.current_position = data.get('current_position', emp.current_position)
                    if 'gender' in data:
                        emp.gender = data['gender']
                    if 'age' in data:
                        emp.age = data['age']
                    if 'hire_date' in data:
                        emp.hire_date = data['hire_date']
                    emp.save()
                    updated = 1
                else:
                    updated = 0
                if updated:
                    updated_count += updated
                    
                if updated_count % 100 == 0:
                    print(f"  진행: {updated_count}명 업데이트")
                    
            except Exception as e:
                print(f"  오류: {e}")
                continue
    
    print(f"\n업데이트 완료: {updated_count}명")
    
    # 최종 확인
    final_empty = Employee.objects.filter(name='').count()
    total = Employee.objects.count()
    
    print("\n" + "=" * 80)
    print("최종 결과")
    print("=" * 80)
    print(f"전체 직원: {total}명")
    print(f"이름 없는 직원: {final_empty}명")
    print(f"정상 직원: {total - final_empty}명")

if __name__ == "__main__":
    direct_update()