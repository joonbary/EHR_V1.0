#!/usr/bin/env python
"""
프로덕션 직원 데이터 간단 업로드 스크립트
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

def upload_employees():
    """엑셀 파일에서 직원 데이터 업로드"""
    
    files = ['OK_employee_new_part1.xlsx', 'OK_employee_new_part2.xlsx']
    total_created = 0
    total_updated = 0
    
    for file_path in files:
        print(f"\n처리 중: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            print(f"총 {len(df)}개 행 발견")
            
            with transaction.atomic():
                for idx, row in df.iterrows():
                    # 이메일 확인
                    email = str(row.get('이메일', '')).strip()
                    if not email or email == 'nan':
                        continue
                    
                    # 기본 데이터
                    data = {
                        'email': email,
                        'name': str(row.get('성명', '')).strip(),
                        'phone': str(row.get('전화번호', '010-0000-0000')).strip()[:15],
                    }
                    
                    # 회사 정보
                    company = str(row.get('회사', '')).strip()
                    if company and company != 'nan':
                        data['company'] = company
                    
                    # 부서 정보
                    dept = str(row.get('부서', row.get('최종소속', ''))).strip()
                    if dept and dept != 'nan':
                        data['final_department'] = dept[:100]  # 최대 100자
                    
                    # 직급 정보
                    position = str(row.get('직급', '')).strip()
                    if position and position != 'nan':
                        data['current_position'] = position[:50]  # 최대 50자
                    
                    # 입사일
                    hire_date_val = row.get('입사일')
                    if pd.notna(hire_date_val):
                        try:
                            if isinstance(hire_date_val, str):
                                data['hire_date'] = datetime.strptime(hire_date_val, '%Y%m%d').date()
                            elif hasattr(hire_date_val, 'date'):
                                data['hire_date'] = hire_date_val.date()
                        except:
                            pass
                    
                    # dummy 필드들
                    dummy_fields = {
                        'dummy_성명': 'dummy_name',
                        'dummy_한자': 'dummy_chinese_name',
                        'dummy_email': 'dummy_email',
                        'dummy_휴대전화': 'dummy_mobile',
                        'dummy_등록기준지': 'dummy_registered_address',
                        'dummy_기숙사': 'dummy_residence_address',
                    }
                    
                    for excel_field, model_field in dummy_fields.items():
                        value = row.get(excel_field)
                        if pd.notna(value):
                            data[model_field] = str(value).strip()
                    
                    # 생성 또는 업데이트
                    employee, created = Employee.objects.update_or_create(
                        email=email,
                        defaults=data
                    )
                    
                    if created:
                        total_created += 1
                    else:
                        total_updated += 1
                    
                    if (idx + 1) % 100 == 0:
                        print(f"  진행: {idx + 1}/{len(df)}")
                        
        except Exception as e:
            print(f"오류 발생: {e}")
            continue
    
    print(f"\n=== 완료 ===")
    print(f"생성: {total_created}명")
    print(f"업데이트: {total_updated}명")
    print(f"전체 직원: {Employee.objects.count()}명")

if __name__ == "__main__":
    upload_employees()