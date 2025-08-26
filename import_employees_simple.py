#!/usr/bin/env python
"""
Railway 프로덕션에 직원 데이터 임포트 (단순화 버전)
"""
import os
import sys
import csv
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import transaction

def import_employees():
    """CSV 파일에서 직원 데이터 임포트"""
    csv_file = 'OK저축은행_직원명부_1000명.csv'
    
    if not os.path.exists(csv_file):
        print(f"CSV 파일을 찾을 수 없습니다: {csv_file}")
        return
    
    print("=" * 60)
    print("직원 데이터 임포트 시작")
    print("=" * 60)
    
    # 기존 직원 삭제
    Employee.objects.all().delete()
    print("기존 직원 데이터 삭제 완료")
    
    created_count = 0
    
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        with transaction.atomic():
            for row in reader:
                try:
                    # 필수 필드만 처리
                    employee = Employee.objects.create(
                        name=row['이름'],
                        gender='M' if row['성별'] == '남성' else 'F',
                        company=row['회사'] or 'OK저축은행',
                        department=row['부서'] or '미지정',
                        team=row['팀'] or '',
                        position=row['직급'] or '사원',
                        email=row['이메일'],
                        phone=row['휴대폰'] or '',
                        employment_status=row['재직상태'] or '재직',
                        employment_type=row['고용형태'] or '정규직',
                    )
                    
                    created_count += 1
                    
                    if created_count % 100 == 0:
                        print(f"처리 중... {created_count}명 완료")
                        
                except Exception as e:
                    print(f"직원 {row.get('사번', 'unknown')} 처리 중 오류: {e}")
                    continue
    
    print("\n" + "=" * 60)
    print("직원 데이터 임포트 완료!")
    print("=" * 60)
    print(f"생성된 직원: {created_count}명")
    print(f"현재 총 직원 수: {Employee.objects.count()}명")

if __name__ == '__main__':
    try:
        import_employees()
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)