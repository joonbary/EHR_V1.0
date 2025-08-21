#!/usr/bin/env python
"""
Production용 샘플 직원 데이터 생성 스크립트
Railway에서 실행 가능한 버전
"""
import os
import sys
import django
from datetime import date, datetime, timedelta
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_evaluation.settings')
django.setup()

from employees.models import Employee

def create_sample_employees():
    """샘플 직원 데이터 생성"""
    
    # 현재 직원 수 확인
    current_count = Employee.objects.count()
    print(f"현재 직원 수: {current_count}")
    
    if current_count > 0:
        print("이미 직원 데이터가 존재합니다.")
        return
    
    # 샘플 데이터 정의
    companies = ['OK금융지주', 'OK저축은행', 'OK캐피탈', 'OK신용정보', 'OK데이터시스템']
    departments = ['경영지원부', 'IT개발부', '영업부', '기획부', '인사부', '재무부', '리스크관리부', '디지털본부', '고객지원부']
    positions = ['사원', '대리', '과장', '차장', '부장']
    
    created_count = 0
    
    for i in range(50):  # 50명의 샘플 직원 생성
        try:
            # 랜덤 데이터 생성
            company = random.choice(companies)
            department = f"{company} {random.choice(departments)}"
            position = random.choice(positions)
            
            # 입사일: 2015-2024년 사이 랜덤
            start_date = date(2015, 1, 1)
            end_date = date(2024, 12, 31)
            random_days = random.randint(0, (end_date - start_date).days)
            hire_date = start_date + timedelta(days=random_days)
            
            employee = Employee.objects.create(
                name=f"직원{i+1:03d}",
                email=f"employee{i+1:03d}@{company.lower().replace(' ', '')}.co.kr",
                company=company,
                department=department,
                final_department=random.choice(departments),
                position=position,
                current_position=position,
                new_position=position,
                hire_date=hire_date,
                phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                employment_status='재직',
                job_group=random.choice(['PL', 'Non-PL']),
                job_type=random.choice(['IT개발', '경영관리', '영업', '기획', '인사']),
                age=random.randint(25, 55),
                gender=random.choice(['M', 'F'])
            )
            created_count += 1
            
            if created_count % 10 == 0:
                print(f"진행 중... {created_count}명 생성")
                
        except Exception as e:
            print(f"직원 {i+1} 생성 실패: {e}")
            continue
    
    print(f"\n=== 샘플 데이터 생성 완료 ===")
    print(f"생성된 직원 수: {created_count}명")
    print(f"총 직원 수: {Employee.objects.count()}명")
    print(f"부서 수: {Employee.objects.values_list('department', flat=True).distinct().count()}개")
    print(f"재직자 수: {Employee.objects.filter(employment_status='재직').count()}명")

if __name__ == '__main__':
    print("Production 샘플 데이터 생성을 시작합니다...")
    create_sample_employees()