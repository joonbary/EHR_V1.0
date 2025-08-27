#!/usr/bin/env python
"""
초기 직원 데이터 로드 스크립트
Railway 배포 시 자동으로 실행되도록 설정 가능
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
import json
from datetime import date

def load_sample_employees():
    """최소한의 샘플 직원 데이터 로드"""
    
    # 이미 데이터가 있는지 확인
    if Employee.objects.count() > 0:
        print(f"Already have {Employee.objects.count()} employees. Skipping.")
        return
    
    print("Loading sample employees...")
    
    # 샘플 직원 데이터
    sample_employees = [
        {
            "no": 1001,
            "name": "김철수",
            "email": "kim.cs@okgroup.kr",
            "phone": "010-1234-5678",
            "department": "IT",
            "position": "MANAGER",
            "company": "OK",
            "headquarters1": "IT본부",
            "final_department": "시스템개발부",
            "current_position": "과장",
            "employment_status": "재직",
            "hire_date": date(2020, 3, 1),
            "gender": "M",
            "job_group": "Non-PL",
            "growth_level": 3
        },
        {
            "no": 1002,
            "name": "이영희",
            "email": "lee.yh@okgroup.kr",
            "phone": "010-2345-6789",
            "department": "HR",
            "position": "SENIOR",
            "company": "OK",
            "headquarters1": "경영지원본부",
            "final_department": "인사총무부",
            "current_position": "대리",
            "employment_status": "재직",
            "hire_date": date(2021, 5, 15),
            "gender": "F",
            "job_group": "Non-PL",
            "growth_level": 2
        },
        {
            "no": 1003,
            "name": "박민수",
            "email": "park.ms@okgroup.kr",
            "phone": "010-3456-7890",
            "department": "SALES",
            "position": "STAFF",
            "company": "OK",
            "headquarters1": "영업본부",
            "final_department": "리테일영업부",
            "current_position": "사원",
            "employment_status": "재직",
            "hire_date": date(2022, 9, 1),
            "gender": "M",
            "job_group": "Non-PL",
            "growth_level": 1
        },
        {
            "no": 1004,
            "name": "정수진",
            "email": "jung.sj@okgroup.kr",
            "phone": "010-4567-8901",
            "department": "FINANCE",
            "position": "DIRECTOR",
            "company": "OK",
            "headquarters1": "여신본부",
            "final_department": "여신심사부",
            "current_position": "부장",
            "employment_status": "재직",
            "hire_date": date(2018, 1, 10),
            "gender": "F",
            "job_group": "PL",
            "growth_level": 5
        },
        {
            "no": 1005,
            "name": "최동훈",
            "email": "choi.dh@okgroup.kr",
            "phone": "010-5678-9012",
            "department": "IT",
            "position": "EXECUTIVE",
            "company": "OK",
            "headquarters1": "디지털혁신본부",
            "final_department": "디지털전략부",
            "current_position": "상무",
            "employment_status": "재직",
            "hire_date": date(2015, 7, 1),
            "gender": "M",
            "job_group": "PL",
            "growth_level": 6
        }
    ]
    
    created_count = 0
    for emp_data in sample_employees:
        try:
            emp, created = Employee.objects.get_or_create(
                email=emp_data['email'],
                defaults=emp_data
            )
            if created:
                created_count += 1
                print(f"Created: {emp.name} ({emp.email})")
        except Exception as e:
            print(f"Error creating {emp_data['name']}: {e}")
    
    print(f"Created {created_count} new employees")
    print(f"Total employees now: {Employee.objects.count()}")

if __name__ == "__main__":
    load_sample_employees()