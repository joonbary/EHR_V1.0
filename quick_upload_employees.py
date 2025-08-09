#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
빠른 직원 데이터 업로드 스크립트
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

def quick_upload():
    """빠른 직원 데이터 업로드"""
    
    # 파일 선택 (최신 파일 사용)
    file_path = 'emp_upload_250801.xlsx'
    
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return
    
    print(f"파일 읽는 중: {file_path}")
    # 여러 파일 시도
    files_to_try = [
        'OK_employee_new_part1_08051039.xlsx',
        'OK_employee_new_part2_08051039.xlsx',
        'emp_upload_250801.xlsx'
    ]
    
    df_list = []
    for file in files_to_try:
        if os.path.exists(file):
            print(f"  - {file} 읽는 중...")
            try:
                temp_df = pd.read_excel(file)
                # 컬럼명 수정 (인코딩 문제 해결)
                column_mapping = {
                    '�̸�': 'name',
                    '�̸���': 'email', 
                    '�Ի���': 'hire_date',
                    '�μ�': 'department',
                    '��ȭ��ȣ': 'phone',
                    'ȸ��': 'company',
                    '����1': 'headquarters1',
                    '����2': 'headquarters2',
                    '�����Ҽ�': 'final_department',
                    '����': 'position',
                    '��å': 'current_position',
                    '����': 'gender',
                    '����': 'age',
                    '��������': 'marital_status',
                    '����/�迭': 'job_series',
                    '����': 'job_group',
                    'dummy_email': 'dummy_email'
                }
                temp_df.rename(columns=column_mapping, inplace=True)
                df_list.append(temp_df)
                print(f"    {len(temp_df)} 행 추가")
            except Exception as e:
                print(f"    오류: {e}")
    
    if not df_list:
        print("처리할 파일이 없습니다")
        return
    
    df = pd.concat(df_list, ignore_index=True)
    print(f"총 {len(df)} 행 발견")
    
    # 컬럼명 확인
    print(f"컬럼: {list(df.columns)[:10]}...")
    
    total_created = 0
    total_updated = 0
    errors = 0
    
    with transaction.atomic():
        for idx, row in df.iterrows():
            try:
                # 필수 필드 확인
                email = str(row.get('이메일', row.get('email', ''))).strip()
                name = str(row.get('성명', row.get('name', ''))).strip()
                
                if not email or email == 'nan' or not name or name == 'nan':
                    continue
                
                # 기본 데이터
                data = {
                    'name': name[:100],
                    'email': email[:254],
                    'phone': str(row.get('전화번호', row.get('phone', '010-0000-0000'))).strip()[:15],
                }
                
                # 회사 정보
                company = str(row.get('회사', row.get('company', ''))).strip()
                if company and company != 'nan':
                    data['company'] = company[:10]
                
                # 부서 정보 - 여러 컬럼 확인
                dept = str(row.get('부서', row.get('최종소속', row.get('department', '')))).strip()
                if dept and dept != 'nan':
                    data['department'] = dept[:20]  # DEPARTMENT_CHOICES에 맞게
                    data['final_department'] = dept[:100]
                
                # 직급 정보
                position = str(row.get('직급', row.get('position', ''))).strip()
                if position and position != 'nan':
                    data['position'] = position[:20]  # POSITION_CHOICES에 맞게
                    data['current_position'] = position[:50]
                
                # 입사일 처리
                hire_date_val = row.get('입사일', row.get('hire_date'))
                if pd.notna(hire_date_val):
                    try:
                        if isinstance(hire_date_val, str):
                            # 다양한 날짜 형식 처리
                            for fmt in ['%Y%m%d', '%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d']:
                                try:
                                    data['hire_date'] = datetime.strptime(hire_date_val, fmt).date()
                                    break
                                except:
                                    continue
                        elif hasattr(hire_date_val, 'date'):
                            data['hire_date'] = hire_date_val.date()
                        else:
                            data['hire_date'] = hire_date_val
                    except:
                        pass
                
                # 추가 필드들
                additional_fields = {
                    'no': 'no',
                    'NO': 'no',
                    '성별': 'gender',
                    'gender': 'gender',
                    '나이': 'age',
                    'age': 'age',
                    '직급(전)': 'previous_position',
                    '본부1': 'headquarters1',
                    '본부2': 'headquarters2',
                    '소속1': 'department1',
                    '소속2': 'department2',
                    '소속3': 'department3',
                    '소속4': 'department4',
                    '직군/계열': 'job_series',
                    '호칭': 'title',
                    '직책': 'responsibility',
                    '급호': 'salary_grade',
                    '학력': 'education',
                    '결혼여부': 'marital_status',
                }
                
                for excel_field, model_field in additional_fields.items():
                    value = row.get(excel_field)
                    if pd.notna(value) and str(value).strip() != 'nan':
                        if model_field == 'no' or model_field == 'age':
                            try:
                                data[model_field] = int(float(str(value)))
                            except:
                                pass
                        elif model_field == 'gender' or model_field == 'marital_status':
                            # 1글자만 저장
                            data[model_field] = str(value).strip()[:1]
                        else:
                            data[model_field] = str(value).strip()[:100]
                
                # 재직 상태 기본값
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
                    print(f"진행: {idx + 1}/{len(df)} - 생성: {total_created}, 업데이트: {total_updated}")
                    
            except Exception as e:
                errors += 1
                if errors <= 5:  # 처음 5개 에러만 출력
                    print(f"행 {idx} 오류: {e}")
    
    print(f"\n완료!")
    print(f"생성: {total_created}")
    print(f"업데이트: {total_updated}")
    print(f"오류: {errors}")
    print(f"총 처리: {total_created + total_updated}/{len(df)}")

if __name__ == "__main__":
    quick_upload()