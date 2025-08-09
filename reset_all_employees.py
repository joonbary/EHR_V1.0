#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
모든 직원 데이터 삭제 후 새로 시작
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

def reset_and_upload():
    """모든 직원 데이터 삭제 후 새로 업로드"""
    
    print("=" * 80)
    print("직원 데이터 초기화 및 새로 업로드")
    print("=" * 80)
    
    # 1단계: 모든 직원 데이터 삭제
    print("\n[1단계] 모든 직원 데이터 삭제")
    before_count = Employee.objects.count()
    print(f"  삭제 전: {before_count}명")
    
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM employees_employee")
        deleted = cursor.rowcount
        print(f"  삭제 완료: {deleted}명")
    
    after_delete = Employee.objects.count()
    print(f"  삭제 후: {after_delete}명")
    
    if after_delete > 0:
        print("  [경고] 아직 데이터가 남아있습니다!")
        return
    
    # 2단계: 정상적인 엑셀 파일만 업로드
    print("\n[2단계] 정상 엑셀 파일 업로드")
    print("  (emp_upload_250801.xlsx는 제외 - 이름 필드가 없음)")
    
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
            df = pd.read_excel(file_path)
            print(f"    - {len(df)}행 발견")
            
            created_in_file = 0
            
            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        # 컬럼 인덱스로 접근 (컬럼명이 깨질 수 있으므로)
                        # 0: 성명, 1: 이메일, 2: 입사일, 3: 부서, 4: 전화번호
                        # 5: 회사, 8: 최종소속, 9: 직급, 10: 직책, 11: 성별, 12: 나이
                        
                        name = str(row.iloc[0]).strip() if len(row) > 0 else ''
                        email = str(row.iloc[1]).strip() if len(row) > 1 else ''
                        
                        # 헤더 행이거나 유효하지 않은 데이터 건너뛰기
                        if not name or name == 'nan' or '성명' in name or '이름' in name:
                            continue
                        if not email or email == 'nan' or '@' not in email:
                            continue
                        
                        data = {
                            'name': name[:100],
                            'email': email[:254],
                            'employment_status': '재직',
                            'employment_type': '정규직',
                        }
                        
                        # 입사일
                        if len(row) > 2:
                            hire_date_val = row.iloc[2]
                            if pd.notna(hire_date_val):
                                try:
                                    if hasattr(hire_date_val, 'date'):
                                        data['hire_date'] = hire_date_val.date()
                                except:
                                    pass
                        
                        # 부서
                        if len(row) > 3:
                            dept = str(row.iloc[3]).strip()
                            if dept and dept != 'nan' and dept != '-':
                                # department 필드는 선택지가 제한적이므로 매핑
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
                                else:
                                    data['department'] = 'OTHER'
                        
                        # 전화번호
                        if len(row) > 4:
                            phone = str(row.iloc[4]).strip()
                            if phone and phone != 'nan':
                                data['phone'] = phone[:15]
                            else:
                                data['phone'] = '010-0000-0000'
                        
                        # 회사
                        if len(row) > 5:
                            company = str(row.iloc[5]).strip()
                            if company and company != 'nan':
                                if company in ['OK', 'OC', 'OCI', 'OFI', 'OKDS', 'OKH', 'ON', 'OKIP', 'OT', 'OKV', 'EX']:
                                    data['company'] = company
                        
                        # 최종소속
                        if len(row) > 8:
                            final_dept = str(row.iloc[8]).strip()
                            if final_dept and final_dept != 'nan' and final_dept != '-':
                                data['final_department'] = final_dept[:100]
                        
                        # 직급
                        if len(row) > 9:
                            position = str(row.iloc[9]).strip()
                            if position and position != 'nan':
                                # POSITION_CHOICES 매핑
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
                                
                                data['current_position'] = position[:50]
                        
                        # 성별
                        if len(row) > 11:
                            gender = str(row.iloc[11]).strip()
                            if gender and gender != 'nan':
                                if '남' in gender or gender == 'M':
                                    data['gender'] = 'M'
                                elif '여' in gender or gender == 'F':
                                    data['gender'] = 'F'
                        
                        # 나이
                        if len(row) > 12:
                            try:
                                age_val = row.iloc[12]
                                if pd.notna(age_val):
                                    age = int(float(str(age_val)))
                                    if 20 <= age <= 70:
                                        data['age'] = age
                            except:
                                pass
                        
                        # Employee 생성 (중복 체크)
                        employee, created = Employee.objects.get_or_create(
                            email=email,
                            defaults=data
                        )
                        
                        if created:
                            created_in_file += 1
                            total_created += 1
                        
                        if created_in_file % 100 == 0:
                            print(f"      진행: {created_in_file}명 생성")
                    
                    except Exception as e:
                        total_errors += 1
                        if total_errors <= 3:
                            print(f"      오류 (행 {idx}): {e}")
            
            print(f"    완료: {created_in_file}명 생성")
            
        except Exception as e:
            print(f"  파일 오류: {e}")
    
    # 3단계: 최종 확인
    print("\n[3단계] 최종 확인")
    
    final_total = Employee.objects.count()
    with_name = Employee.objects.exclude(name='').exclude(name__isnull=True).count()
    with_dept = Employee.objects.exclude(department='').exclude(department__isnull=True).count()
    with_pos = Employee.objects.exclude(position='').exclude(position__isnull=True).count()
    
    print(f"  전체 직원: {final_total}명")
    print(f"  이름 있는 직원: {with_name}명")
    print(f"  부서 있는 직원: {with_dept}명")
    print(f"  직급 있는 직원: {with_pos}명")
    
    # 회사별 분포
    print("\n[회사별 분포]")
    from django.db.models import Count
    company_stats = Employee.objects.values('company').annotate(count=Count('id')).order_by('-count')
    for stat in company_stats[:5]:
        if stat['company']:
            print(f"  {stat['company']}: {stat['count']}명")
    
    # 샘플 데이터
    print("\n[샘플 데이터 - 처음 5명]")
    for emp in Employee.objects.all()[:5]:
        print(f"  {emp.name} ({emp.company}/{emp.department}/{emp.position}) - {emp.email}")
    
    print("\n" + "=" * 80)
    print("완료!")
    print("=" * 80)
    print(f"목표: 1,790명 (part1: 900 + part2: 890)")
    print(f"실제: {final_total}명")
    if final_total == 1790:
        print("✅ 성공!")
    else:
        print(f"차이: {abs(final_total - 1790)}명")

if __name__ == "__main__":
    reset_and_upload()