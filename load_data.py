#!/usr/bin/env python
"""
Railway에서 직원 데이터를 로드하는 스크립트
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.core.management import call_command

def load_employee_data():
    """직원 데이터 로드"""
    try:
        # 현재 직원 수 확인
        current_count = Employee.objects.count()
        print(f"Current employee count: {current_count}")
        
        # 5명 이하면 데이터 로드
        if current_count <= 5:
            json_file = 'employees_only.json'
            
            if os.path.exists(json_file):
                print(f"Loading data from {json_file}...")
                call_command('loaddata', json_file)
                new_count = Employee.objects.count()
                print(f"Successfully loaded data. New employee count: {new_count}")
            else:
                print(f"Data file {json_file} not found")
        else:
            print(f"Database already has {current_count} employees. Skipping data load.")
    except Exception as e:
        print(f"Error loading data: {e}")
        # 에러가 발생해도 서버는 시작되도록 함
        pass

if __name__ == "__main__":
    load_employee_data()