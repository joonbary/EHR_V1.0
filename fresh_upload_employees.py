#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직원 데이터 새로 업로드 - 잘못된 데이터 삭제 후 정상 업로드
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import transaction, connection

def fresh_upload():
    """직원 데이터 새로 업로드"""
    
    print("=" * 80)
    print("직원 데이터 새로 업로드")
    print("=" * 80)
    
    # 1단계: 잘못된 데이터 삭제
    print("\n[1단계] 잘못된 데이터 삭제")
    
    # Raw SQL로 직접 삭제 (CASCADE 문제 회피)
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM employees_employee WHERE name = '' OR name IS NULL")
        deleted = cursor.rowcount
        print(f"  - {deleted}개 레코드 삭제 완료")
    
    # 2단계: 엑셀 파일에서 새 데이터 업로드
    print("\n[2단계] 엑셀 파일에서 새 데이터 업로드")
    
    excel_files = [
        'OK_employee_new_part1_08051039.xlsx',
        'OK_employee_new_part2_08051039.xlsx',
    ]
    
    total_created = 0
    total_errors = 0
    
    for file_path in excel_files:
        if not os.path.exists(file_path):
            print(f"  [주의] 파일 없음: {file_path}")
            continue
        
        print(f"\n  파일 처리: {file_path}")
        
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path)
            print(f"    - {len(df)}행 발견")
            
            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        # 컬럼명이 깨질 수 있으므로 인덱스로도 접근
                        # 0: 성명, 1: 이메일, 2: 입사일, 3: 부서, 4: 전화번호, 5: 회사
                        # 8: 최종소속, 9: 직급, 10: 직책, 11: 성별, 12: 나이
                        
                        # 이름과 이메일 (필수)
                        name = str(row.iloc[0]).strip() if len(row) > 0 else ''
                        email = str(row.iloc[1]).strip() if len(row) > 1 else ''
                        
                        if not name or name == 'nan' or name == '성명':
                            continue
                        if not email or email == 'nan' or email == '이메일':
                            continue
                        
                        # 기본 데이터
                        data = {
                            'name': name[:100],
                            'email': email[:254],
                            'employment_status': '재직',
                            'employment_type': '정규직',
                        }
                        
                        # 입사일 (2번 인덱스)
                        if len(row) > 2:
                            hire_date_val = row.iloc[2]
                            if pd.notna(hire_date_val):
                                try:
                                    if hasattr(hire_date_val, 'date'):
                                        data['hire_date'] = hire_date_val.date()
                                    else:
                                        date_str = str(hire_date_val).strip()
                                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y%m%d']:
                                            try:
                                                data['hire_date'] = datetime.strptime(date_str, fmt).date()
                                                break
                                            except:
                                                continue
                                except:
                                    pass
                        
                        # 부서 (3번 인덱스)
                        if len(row) > 3:
                            dept = str(row.iloc[3]).strip()
                            if dept and dept != 'nan' and dept != '-':
                                # 부서명이 있으면 저장하되, department는 간단한 코드로
                                if 'IT' in dept or '개발' in dept or '디지털' in dept:
                                    data['department'] = 'IT'
                                elif 'HR' in dept or '인사' in dept:
                                    data['department'] = 'HR'
                                elif '재무' in dept or '회계' in dept:
                                    data['department'] = 'FINANCE'
                                elif '영업' in dept or '세일즈' in dept:
                                    data['department'] = 'SALES'
                                elif '마케팅' in dept:
                                    data['department'] = 'MARKETING'
                                elif 'NPL' in dept or '채권' in dept or '운영' in dept:
                                    data['department'] = 'OPERATIONS'
                                else:
                                    data['department'] = 'OTHER'
                                    
                                data['final_department'] = dept[:100]
                        
                        # 전화번호 (4번 인덱스)
                        if len(row) > 4:
                            phone = str(row.iloc[4]).strip()
                            if phone and phone != 'nan':
                                data['phone'] = phone[:15]
                            else:
                                data['phone'] = '010-0000-0000'
                        else:
                            data['phone'] = '010-0000-0000'
                        
                        # 회사 (5번 인덱스)
                        if len(row) > 5:
                            company = str(row.iloc[5]).strip()
                            if company and company != 'nan':
                                # COMPANY_CHOICES에 맞게
                                if company in ['OK', 'OC', 'OCI', 'OFI', 'OKDS', 'OKH', 'ON', 'OKIP', 'OT', 'OKV', 'EX']:
                                    data['company'] = company
                                else:
                                    data['company'] = 'OK'
                        
                        # 최종소속 (8번 인덱스) - 없으면 부서값 사용
                        if len(row) > 8:
                            final_dept = str(row.iloc[8]).strip()
                            if final_dept and final_dept != 'nan' and final_dept != '-':
                                data['final_department'] = final_dept[:100]
                        
                        # 직급 (9번 인덱스)
                        if len(row) > 9:
                            position = str(row.iloc[9]).strip()
                            if position and position != 'nan':
                                # POSITION_CHOICES에 맞게 매핑
                                if '인턴' in position:
                                    data['position'] = 'INTERN'
                                elif '사원' in position or '주임' in position:
                                    data['position'] = 'STAFF'
                                elif '대리' in position:
                                    data['position'] = 'SENIOR'
                                elif '과장' in position or '차장' in position:
                                    data['position'] = 'MANAGER'
                                elif '부장' in position:
                                    data['position'] = 'DIRECTOR'
                                elif '임원' in position or '이사' in position or '상무' in position:
                                    data['position'] = 'EXECUTIVE'
                                else:
                                    data['position'] = 'STAFF'
                                    
                                data['current_position'] = position[:50]
                        else:
                            data['position'] = 'STAFF'
                        
                        # 직책 (10번 인덱스)
                        if len(row) > 10:
                            job_title = str(row.iloc[10]).strip()
                            if job_title and job_title != 'nan':
                                # current_position이 없으면 직책 사용
                                if 'current_position' not in data:
                                    data['current_position'] = job_title[:50]
                        
                        # 성별 (11번 인덱스)
                        if len(row) > 11:
                            gender = str(row.iloc[11]).strip()
                            if gender and gender != 'nan':
                                if '남' in gender or gender == 'M' or gender == '남자':
                                    data['gender'] = 'M'
                                elif '여' in gender or gender == 'F' or gender == '여자':
                                    data['gender'] = 'F'
                        
                        # 나이 (12번 인덱스)
                        if len(row) > 12:
                            try:
                                age_val = row.iloc[12]
                                if pd.notna(age_val):
                                    age = int(float(str(age_val)))
                                    if 20 <= age <= 70:
                                        data['age'] = age
                            except:
                                pass
                        
                        # 결혼여부 (13번 인덱스)
                        if len(row) > 13:
                            marital = str(row.iloc[13]).strip()
                            if marital and marital != 'nan':
                                if '기혼' in marital or marital == 'Y':
                                    data['marital_status'] = 'Y'
                                elif '미혼' in marital or marital == 'N':
                                    data['marital_status'] = 'N'
                        
                        # Employee 생성
                        employee = Employee.objects.create(**data)
                        total_created += 1
                        
                        if total_created % 100 == 0:
                            print(f"    진행: {total_created}명 생성")
                    
                    except Exception as e:
                        total_errors += 1
                        if total_errors <= 5:
                            print(f"    오류 (행 {idx}): {e}")
                        continue
            
            print(f"    완료 - {total_created}명 생성")
            
        except Exception as e:
            print(f"  파일 처리 오류: {e}")
    
    # 3단계: 최종 확인
    print("\n[3단계] 최종 확인")
    
    total_employees = Employee.objects.count()
    name_filled = Employee.objects.exclude(name='').exclude(name__isnull=True).count()
    dept_filled = Employee.objects.exclude(department='').exclude(department__isnull=True).count()
    pos_filled = Employee.objects.exclude(position='').exclude(position__isnull=True).count()
    
    print(f"  - 전체 직원: {total_employees}명")
    print(f"  - 이름 있는 직원: {name_filled}명")
    print(f"  - 부서 있는 직원: {dept_filled}명")
    print(f"  - 직급 있는 직원: {pos_filled}명")
    
    # 샘플 데이터 확인
    print("\n[샘플 데이터]")
    for emp in Employee.objects.all().order_by('-id')[:5]:
        print(f"  - {emp.name} ({emp.company}/{emp.department}/{emp.position})")
        print(f"    이메일: {emp.email}, 최종소속: {emp.final_department}")
    
    print("\n" + "=" * 80)
    print("직원 데이터 업로드 완료!")
    print("=" * 80)
    print(f"총 {total_created}명 생성, {total_errors}개 오류")

if __name__ == "__main__":
    fresh_upload()