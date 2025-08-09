#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
강제 직원 데이터 업로드 - 컬럼 인덱스 기반
모든 가능한 방법을 동원한 마이그레이션
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import transaction

def clean_text(text):
    """텍스트 정리 함수"""
    if pd.isna(text):
        return ''
    text = str(text).strip()
    if text in ['nan', 'None', 'NaN', 'NaT']:
        return ''
    return text

def parse_date(date_val):
    """날짜 파싱 함수"""
    if pd.isna(date_val):
        return None
    
    if hasattr(date_val, 'date'):
        return date_val.date()
    
    date_str = str(date_val).strip()
    
    # 다양한 날짜 형식 시도
    formats = [
        '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',
        '%Y%m%d', '%d/%m/%Y', '%d-%m-%Y',
        '%m/%d/%Y', '%m-%d-%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue
    
    # 숫자만 추출해서 시도
    numbers = re.findall(r'\d+', date_str)
    if len(numbers) == 3:
        try:
            year = int(numbers[0])
            month = int(numbers[1])
            day = int(numbers[2])
            
            # 년도가 2자리인 경우
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            
            # 일/월이 바뀐 경우 처리
            if month > 12:
                month, day = day, month
            
            return datetime(year, month, day).date()
        except:
            pass
    
    return None

def force_upload_employees():
    """강제 직원 데이터 업로드"""
    
    print("=" * 80)
    print("강제 직원 데이터 마이그레이션 시작")
    print("=" * 80)
    
    # 모든 가능한 엑셀 파일 확인
    excel_files = [
        'emp_upload_250801.xlsx',  # 이 파일부터 시작
        'OK_employee_new_part1_08051039.xlsx',
        'OK_employee_new_part2_08051039.xlsx',
        'OK_employee_new_part1.xlsx',
        'OK_employee_new_part2.xlsx',
    ]
    
    all_data = []
    
    for file_path in excel_files:
        if not os.path.exists(file_path):
            continue
            
        print(f"\n파일 처리: {file_path}")
        
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path)
            print(f"  - {len(df)} 행 발견")
            
            # 첫 번째 행 확인으로 컬럼 구조 파악
            if len(df) > 0:
                first_row = df.iloc[0]
                print(f"  - 컬럼 수: {len(df.columns)}")
                
                # 컬럼 인덱스로 접근
                for idx, row in df.iterrows():
                    employee_data = {}
                    
                    # 인덱스 기반 데이터 추출 (위치는 파일 구조에 따라 조정)
                    try:
                        # 이름 (보통 0번째 컬럼)
                        name = clean_text(row.iloc[0] if len(row) > 0 else '')
                        if not name:
                            continue
                        employee_data['name'] = name[:100]
                        
                        # 이메일 (보통 1번째 컬럼)
                        email = clean_text(row.iloc[1] if len(row) > 1 else '')
                        if not email:
                            # 이메일이 없으면 자동 생성
                            email = f"emp{idx:06d}@okfg.kr"
                        employee_data['email'] = email[:254]
                        
                        # 입사일 (보통 2번째 컬럼)
                        if len(row) > 2:
                            hire_date = parse_date(row.iloc[2])
                            if hire_date:
                                employee_data['hire_date'] = hire_date
                        
                        # 부서 (보통 3번째 컬럼)
                        if len(row) > 3:
                            dept = clean_text(row.iloc[3])
                            if dept:
                                employee_data['department'] = 'IT'  # 기본값
                                employee_data['final_department'] = dept[:100]
                        
                        # 전화번호 (보통 4번째 컬럼)
                        if len(row) > 4:
                            phone = clean_text(row.iloc[4])
                            if phone:
                                employee_data['phone'] = phone[:15]
                            else:
                                employee_data['phone'] = '010-0000-0000'
                        else:
                            employee_data['phone'] = '010-0000-0000'
                        
                        # 회사 (보통 5번째 컬럼)
                        if len(row) > 5:
                            company = clean_text(row.iloc[5])
                            if company:
                                # COMPANY_CHOICES에 맞게 매핑
                                company_map = {
                                    'OK': 'OK', 'OCI': 'OCI', 'OC': 'OC', 
                                    'OFI': 'OFI', 'OKDS': 'OKDS', 'OKH': 'OKH',
                                    'ON': 'ON', 'OKIP': 'OKIP', 'OT': 'OT',
                                    'OKV': 'OKV', 'EX': 'EX'
                                }
                                for key in company_map:
                                    if key in company.upper():
                                        employee_data['company'] = company_map[key]
                                        break
                        
                        # 직급 (보통 9-10번째 컬럼)
                        if len(row) > 9:
                            position = clean_text(row.iloc[9])
                            if not position and len(row) > 10:
                                position = clean_text(row.iloc[10])
                            if position:
                                # POSITION_CHOICES에 맞게 매핑
                                position_map = {
                                    '인턴': 'INTERN', '사원': 'STAFF', '대리': 'SENIOR',
                                    '과장': 'MANAGER', '부장': 'DIRECTOR', '임원': 'EXECUTIVE'
                                }
                                employee_data['position'] = 'STAFF'  # 기본값
                                for key, val in position_map.items():
                                    if key in position:
                                        employee_data['position'] = val
                                        break
                                employee_data['current_position'] = position[:50]
                        
                        # 성별 (보통 11번째 컬럼)
                        if len(row) > 11:
                            gender = clean_text(row.iloc[11])
                            if gender:
                                if '남' in gender or gender.upper() == 'M':
                                    employee_data['gender'] = 'M'
                                elif '여' in gender or gender.upper() == 'F':
                                    employee_data['gender'] = 'F'
                        
                        # 나이 (보통 12번째 컬럼)
                        if len(row) > 12:
                            try:
                                age = int(float(str(row.iloc[12])))
                                if 20 <= age <= 70:
                                    employee_data['age'] = age
                            except:
                                pass
                        
                        # 추가 필드들
                        if len(row) > 13:
                            marital = clean_text(row.iloc[13])
                            if marital:
                                if '기혼' in marital or marital == 'Y':
                                    employee_data['marital_status'] = 'Y'
                                elif '미혼' in marital or marital == 'N':
                                    employee_data['marital_status'] = 'N'
                        
                        # 기본값 설정
                        employee_data['employment_status'] = '재직'
                        employee_data['employment_type'] = '정규직'
                        
                        all_data.append(employee_data)
                        
                    except Exception as e:
                        print(f"    행 {idx} 처리 오류: {e}")
                        continue
                        
        except Exception as e:
            print(f"  파일 읽기 오류: {e}")
            continue
    
    print(f"\n총 {len(all_data)}개 데이터 준비 완료")
    
    if not all_data:
        print("처리할 데이터가 없습니다!")
        return
    
    # 데이터베이스에 업로드
    print("\n데이터베이스 업로드 시작...")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    with transaction.atomic():
        for i, data in enumerate(all_data):
            try:
                employee, created = Employee.objects.update_or_create(
                    email=data['email'],
                    defaults=data
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                
                if (i + 1) % 100 == 0:
                    print(f"  진행: {i + 1}/{len(all_data)} - 생성: {created_count}, 업데이트: {updated_count}")
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    print(f"  업로드 오류: {e}")
                    print(f"  데이터: {data}")
    
    print("\n" + "=" * 80)
    print("마이그레이션 완료!")
    print("=" * 80)
    print(f"✅ 생성: {created_count}명")
    print(f"📝 업데이트: {updated_count}명")
    print(f"❌ 오류: {error_count}건")
    print(f"📊 총 처리: {created_count + updated_count}/{len(all_data)}")
    
    # 최종 확인
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(employment_status='재직').count()
    
    print(f"\n📊 데이터베이스 현황:")
    print(f"  - 전체 직원: {total_employees}명")
    print(f"  - 재직 직원: {active_employees}명")

if __name__ == "__main__":
    force_upload_employees()