#!/usr/bin/env python
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

def connect_employee_user():
    try:
        # 김철수 직원 찾기 (id=15)
        kim = Employee.objects.get(id=15)
        print(f"직원 찾음: {kim.name} (ID: {kim.id})")
        
        # kimcs 사용자 찾기 (없으면 생성)
        try:
            user = User.objects.get(username='kimcs')
            print(f"기존 사용자 찾음: {user.username}")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='kimcs',
                password='test1234!',
                email='kimcs@okfg.com',
                first_name='김철수'
            )
            print(f"새 사용자 생성: {user.username}")
        
        # 연결
        kim.user = user
        kim.save()
        
        print(f"✅ 연결 완료: {kim.name} - {user.username}")
        
        # 연결 확인
        connected_employee = Employee.objects.get(user=user)
        print(f"✅ 확인: {connected_employee.name}의 사용자 계정은 {connected_employee.user.username}")
        
    except Employee.DoesNotExist:
        print("❌ 직원 id=15를 찾을 수 없습니다.")
        print("사용 가능한 직원들:")
        for emp in Employee.objects.all()[:5]:
            print(f"  - {emp.name} (ID: {emp.id})")
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == '__main__':
    connect_employee_user() 