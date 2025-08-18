#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
나머지 직원 데이터 완성 업로드
"""
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import transaction

print("=" * 80)
print("직원 데이터 완성 업로드")
print("=" * 80)

# 현재 상태 확인
current_count = Employee.objects.count()
print(f"\n현재 직원 수: {current_count}명")
print(f"목표: 1,790명")
print(f"부족: {1790 - current_count}명")

if current_count >= 1790:
    print("\n이미 목표 달성!")
    exit()

# 엑셀 파일 다시 읽어서 누락된 직원 찾기
excel_files = [
    'OK_employee_new_part1_08051039.xlsx',  # 900명
    'OK_employee_new_part2_08051039.xlsx',  # 890명
]

print("\n누락된 직원 찾기...")

total_added = 0
total_updated = 0

for file_path in excel_files:
    if not os.path.exists(file_path):
        print(f"파일 없음: {file_path}")
        continue
    
    print(f"\n처리 중: {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        print(f"  {len(df)}행 발견")
        
        added_in_file = 0
        updated_in_file = 0
        
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    # 첫 번째 행이 헤더인지 확인
                    name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                    email = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                    
                    # 유효성 검사
                    if not name or name == '성명' or name == '이름' or name == 'nan':
                        continue
                    if not email or '@' not in email:
                        continue
                    
                    # 이미 존재하는지 확인
                    exists = Employee.objects.filter(email=email).exists()
                    
                    if not exists:
                        # 기본 데이터
                        data = {
                            'name': name[:100],
                            'email': email[:254],
                            'employment_status': '재직',
                            'employment_type': '정규직',
                        }
                        
                        # 회사 (5번 인덱스)
                        if len(row) > 5 and pd.notna(row.iloc[5]):
                            company = str(row.iloc[5]).strip()
                            if company in ['OK', 'OC', 'OCI', 'OFI', 'OKDS', 'OKH', 'ON', 'OKIP', 'OT', 'OKV', 'EX']:
                                data['company'] = company
                        
                        # 부서 (8번 인덱스 - 최종소속)
                        if len(row) > 8 and pd.notna(row.iloc[8]):
                            dept = str(row.iloc[8]).strip()
                            if dept and dept != '-' and dept != 'nan':
                                data['final_department'] = dept[:100]
                                # department 필드 매핑
                                if 'IT' in dept or '개발' in dept:
                                    data['department'] = 'IT'
                                elif '인사' in dept or 'HR' in dept:
                                    data['department'] = 'HR'
                                elif '재무' in dept or '회계' in dept:
                                    data['department'] = 'FINANCE'
                                elif '영업' in dept:
                                    data['department'] = 'SALES'
                                elif '마케팅' in dept:
                                    data['department'] = 'MARKETING'
                                else:
                                    data['department'] = 'OTHER'
                        
                        # 직급 (9번 인덱스)
                        if len(row) > 9 and pd.notna(row.iloc[9]):
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
                        
                        # 전화번호 (4번 인덱스)
                        if len(row) > 4 and pd.notna(row.iloc[4]):
                            phone = str(row.iloc[4]).strip()
                            data['phone'] = phone[:15] if phone and phone != 'nan' else '010-0000-0000'
                        else:
                            data['phone'] = '010-0000-0000'
                        
                        # Employee 생성
                        Employee.objects.create(**data)
                        added_in_file += 1
                        total_added += 1
                        
                        if added_in_file % 50 == 0:
                            print(f"    진행: {added_in_file}명 추가")
                
                except Exception as e:
                    continue
        
        print(f"  완료: {added_in_file}명 추가")
        
    except Exception as e:
        print(f"  파일 오류: {e}")

# 최종 확인
final_total = Employee.objects.count()

print("\n" + "=" * 80)
print("업로드 완료!")
print("=" * 80)
print(f"시작: {current_count}명")
print(f"추가: {total_added}명")
print(f"최종: {final_total}명")
print(f"목표: 1,790명")

if final_total >= 1790:
    print("✅ 목표 달성!")
else:
    print(f"⚠️ 아직 {1790 - final_total}명 부족")

# 회사별 통계
from django.db.models import Count
company_stats = Employee.objects.values('company').annotate(count=Count('id')).order_by('-count')
print("\n회사별 분포:")
for stat in company_stats[:5]:
    if stat['company']:
        print(f"  {stat['company']}: {stat['count']}명")