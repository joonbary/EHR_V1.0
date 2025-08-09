#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직원 데이터 수정 스크립트
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

def fix_employee_data():
    """직원 데이터 수정"""
    
    print("=" * 80)
    print("직원 데이터 수정 시작")
    print("=" * 80)
    
    # 잘못된 데이터 삭제 (이름이 없는 데이터)
    print("\n[1단계] 잘못된 데이터 삭제")
    bad_employees = Employee.objects.filter(name='')
    bad_count = bad_employees.count()
    print(f"  - 이름이 없는 직원: {bad_count}명")
    
    if bad_count > 0:
        bad_employees.delete()
        print(f"  ✅ {bad_count}명 삭제 완료")
    
    # 정상 데이터 재업로드
    print("\n[2단계] 정상 데이터 업로드")
    
    excel_files = [
        'OK_employee_new_part1_08051039.xlsx',
        'OK_employee_new_part2_08051039.xlsx',
    ]
    
    total_created = 0
    total_updated = 0
    
    for file_path in excel_files:
        if not os.path.exists(file_path):
            print(f"  ❌ 파일 없음: {file_path}")
            continue
        
        print(f"\n  파일 처리: {file_path}")
        
        try:
            # 엑셀 파일 읽기 (헤더 있음)
            df = pd.read_excel(file_path)
            print(f"    - {len(df)}행 발견")
            
            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        # 이름과 이메일 확인
                        name = str(row.get('성명', row.get('이름', ''))).strip()
                        email = str(row.get('이메일', row.get('email', ''))).strip()
                        
                        if not name or name == 'nan' or not email or email == 'nan':
                            continue
                        
                        # 데이터 매핑
                        data = {
                            'name': name[:100],
                            'email': email[:254],
                        }
                        
                        # 전화번호
                        phone = str(row.get('전화번호', row.get('휴대전화', '010-0000-0000'))).strip()
                        if phone and phone != 'nan':
                            data['phone'] = phone[:15]
                        else:
                            data['phone'] = '010-0000-0000'
                        
                        # 회사
                        company = str(row.get('회사', '')).strip()
                        if company and company != 'nan':
                            # COMPANY_CHOICES에 맞게 매핑
                            company_map = {
                                'OK': 'OK', 'OCI': 'OCI', 'OC': 'OC',
                                'OFI': 'OFI', 'OKDS': 'OKDS', 'OKH': 'OKH',
                                'ON': 'ON', 'OKIP': 'OKIP', 'OT': 'OT',
                                'OKV': 'OKV', 'EX': 'EX'
                            }
                            if company in company_map:
                                data['company'] = company
                            else:
                                data['company'] = 'OK'  # 기본값
                        
                        # 부서 - department 필드에 적절한 값 설정
                        dept = str(row.get('부서', row.get('최종소속', ''))).strip()
                        if dept and dept != 'nan' and dept != '-':
                            # DEPARTMENT_CHOICES에 맞게 매핑
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
                            elif '운영' in dept or 'NPL' in dept or '채권' in dept:
                                data['department'] = 'OPERATIONS'
                            elif '전략' in dept or '기획' in dept:
                                data['department'] = 'STRATEGY'
                            elif '법' in dept or '준법' in dept:
                                data['department'] = 'LEGAL'
                            elif '리스크' in dept or '위험' in dept:
                                data['department'] = 'RISK'
                            else:
                                data['department'] = 'OTHER'
                            
                            # final_department에는 원본 값 저장
                            data['final_department'] = dept[:100]
                        else:
                            data['department'] = 'OTHER'
                            data['final_department'] = '미지정'
                        
                        # 직급 - position 필드
                        position = str(row.get('직급', row.get('직책', ''))).strip()
                        current_pos = str(row.get('호칭', row.get('직책', ''))).strip()
                        
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
                                data['position'] = 'STAFF'  # 기본값
                        else:
                            data['position'] = 'STAFF'
                        
                        # current_position
                        if current_pos and current_pos != 'nan':
                            data['current_position'] = current_pos[:50]
                        elif position and position != 'nan':
                            data['current_position'] = position[:50]
                        else:
                            data['current_position'] = '사원'
                        
                        # 입사일
                        hire_date_val = row.get('입사일', row.get('입사년월일'))
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
                        
                        # 성별
                        gender = str(row.get('성별', '')).strip()
                        if gender and gender != 'nan':
                            if '남' in gender or gender == 'M' or gender == '남자':
                                data['gender'] = 'M'
                            elif '여' in gender or gender == 'F' or gender == '여자':
                                data['gender'] = 'F'
                        
                        # 나이
                        age_val = row.get('나이')
                        if pd.notna(age_val):
                            try:
                                age = int(float(str(age_val)))
                                if 20 <= age <= 70:
                                    data['age'] = age
                            except:
                                pass
                        
                        # 결혼여부
                        marital = str(row.get('결혼여부', '')).strip()
                        if marital and marital != 'nan':
                            if '기혼' in marital or marital == 'Y':
                                data['marital_status'] = 'Y'
                            elif '미혼' in marital or marital == 'N':
                                data['marital_status'] = 'N'
                        
                        # 재직 상태
                        data['employment_status'] = '재직'
                        data['employment_type'] = '정규직'
                        
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
                            print(f"    진행: {idx + 1}/{len(df)}")
                    
                    except Exception as e:
                        print(f"    오류 (행 {idx}): {e}")
                        continue
            
            print(f"    ✅ 완료 - 생성: {total_created}, 업데이트: {total_updated}")
            
        except Exception as e:
            print(f"  ❌ 파일 처리 오류: {e}")
    
    # 최종 점검
    print("\n[3단계] 최종 점검")
    final_count = Employee.objects.count()
    name_filled = Employee.objects.exclude(name='').exclude(name__isnull=True).count()
    dept_filled = Employee.objects.exclude(department='').exclude(department__isnull=True).count()
    pos_filled = Employee.objects.exclude(position='').exclude(position__isnull=True).count()
    
    print(f"  - 전체 직원: {final_count}명")
    print(f"  - 이름 있는 직원: {name_filled}명")
    print(f"  - 부서 있는 직원: {dept_filled}명")
    print(f"  - 직급 있는 직원: {pos_filled}명")
    
    print("\n" + "=" * 80)
    print("직원 데이터 수정 완료!")
    print("=" * 80)

if __name__ == "__main__":
    fix_employee_data()