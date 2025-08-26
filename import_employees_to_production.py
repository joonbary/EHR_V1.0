#!/usr/bin/env python
"""
Railway 프로덕션에 직원 데이터 임포트 스크립트
"""
import os
import sys
import csv
import django
from datetime import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection, transaction
from employees.models import Employee
from django.contrib.auth import get_user_model

User = get_user_model()

def import_employees():
    """CSV 파일에서 직원 데이터 임포트"""
    csv_file = 'OK저축은행_직원명부_1000명.csv'
    
    if not os.path.exists(csv_file):
        print(f"CSV 파일을 찾을 수 없습니다: {csv_file}")
        return
    
    print("=" * 60)
    print("직원 데이터 임포트 시작")
    print("=" * 60)
    
    # 기존 직원 수 확인
    existing_count = Employee.objects.count()
    print(f"기존 직원 수: {existing_count}명")
    
    created_count = 0
    updated_count = 0
    
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        with transaction.atomic():
            for row in reader:
                try:
                    # 사번으로 기존 직원 확인
                    employee_id = row['사번']
                    
                    # 성별 변환
                    gender = 'M' if row['성별'] == '남성' else 'F'
                    
                    # 날짜 처리
                    birth_date = datetime.strptime(row['생년월일'], '%Y-%m-%d').date() if row['생년월일'] else None
                    hire_date = datetime.strptime(row['입사일'], '%Y-%m-%d').date() if row['입사일'] else None
                    group_join_date = datetime.strptime(row['그룹입사일'], '%Y-%m-%d').date() if row['그룹입사일'] else None
                    
                    # 숫자 필드 처리
                    annual_salary = Decimal(row['연봉']) if row['연봉'] else Decimal('0')
                    performance_bonus = Decimal(row['성과급']) if row['성과급'] else Decimal('0')
                    total_compensation = Decimal(row['총보수']) if row['총보수'] else Decimal('0')
                    children_count = int(row['자녀수']) if row['자녀수'] else 0
                    
                    # Employee 생성
                    # 사번을 id로 사용
                    employee = Employee(
                        id=int(employee_id.replace('20250', '')),  # 20250001 -> 1
                        name=row['이름'],
                        gender=gender,
                        birth_date=birth_date,
                        age=int(row['나이']) if row['나이'] else None,
                        company=row['회사'],
                        department=row['부서'],
                        team=row['팀'],
                        job_family=row['직군'],
                        hire_date=hire_date,
                        group_join_date=group_join_date,
                        email=row['이메일'],
                        phone=row['휴대폰'],
                        emergency_phone=row['비상연락처'],
                        address=row['주소'],
                        employment_status=row['재직상태'],
                        employment_type=row['고용형태'],
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    if (created_count + updated_count) % 100 == 0:
                        print(f"처리 중... {created_count + updated_count}명 완료")
                        
                except Exception as e:
                    print(f"직원 {row.get('사번', 'unknown')} 처리 중 오류: {e}")
                    continue
    
    print("\n" + "=" * 60)
    print("직원 데이터 임포트 완료!")
    print("=" * 60)
    print(f"신규 생성: {created_count}명")
    print(f"업데이트: {updated_count}명")
    print(f"현재 총 직원 수: {Employee.objects.count()}명")

if __name__ == '__main__':
    try:
        import_employees()
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)