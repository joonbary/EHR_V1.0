"""
Simplified Excel Migration Script
더 간단하고 안정적인 마이그레이션
"""

import os
import sys
import django
import pandas as pd
import random
from datetime import date

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

# Excel 파일 읽기
excel_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK_dummy_employee_250801.xlsx"
df = pd.read_excel(excel_path)

print(f"총 {len(df)}개 행 로드")

# 기존 데이터 삭제
print("기존 데이터 삭제 중...")
Employee.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

# 한국 이름 생성용 데이터
last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
first_names = ['민준', '서준', '도윤', '예준', '시우', '서연', '서윤', '지우', '서현', '민서']

success = 0
failed = 0

print("마이그레이션 시작...")

# 배치 크기 설정
batch_size = 100
total_batches = (len(df) - 1) // batch_size + 1

for batch_num in range(total_batches):
    start_idx = batch_num * batch_size
    end_idx = min((batch_num + 1) * batch_size, len(df))
    
    print(f"\n배치 {batch_num + 1}/{total_batches} 처리 중 (행 {start_idx + 1}-{end_idx})...")
    
    for idx in range(start_idx, end_idx):
        row = df.iloc[idx]
        
        try:
            # 간단한 더미 데이터 생성
            name = random.choice(last_names) + random.choice(first_names)
            emp_id = f"emp{idx + 1:04d}"
            email = f"{emp_id}@okfg.co.kr"
            
            # User 생성
            user = User.objects.create_user(
                username=emp_id,
                email=email,
                password='okfg2024!'
            )
            
            # Employee 생성 (최소 필드만)
            employee = Employee.objects.create(
                user=user,
                name=name,
                email=email,
                phone=f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                department='OPERATIONS',  # 기본값
                position='STAFF',  # 기본값
                hire_date=date.today()
            )
            
            success += 1
            
        except Exception as e:
            failed += 1
            if failed <= 5:  # 처음 5개 오류만 출력
                print(f"  오류 (행 {idx + 1}): {str(e)[:100]}")
    
    print(f"  배치 완료: 성공 {success}, 실패 {failed}")

print(f"\n=== 마이그레이션 완료 ===")
print(f"성공: {success}")
print(f"실패: {failed}")
print(f"전체: {len(df)}")

# 관리자 계정 확인
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@okfg.co.kr',
        password='admin123!@#'
    )
    print("\n관리자 계정 생성: admin / admin123!@#")