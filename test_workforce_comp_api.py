#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
인력/보상 대시보드 데이터 바인딩 테스트
Tests the workforce compensation dashboard API and data binding
"""

import os
import sys
import django
import json
from datetime import datetime

# 한글 출력 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from employees.models import Employee
from compensation.models import EmployeeCompensation

User = get_user_model()

def test_workforce_comp_api():
    """API 테스트 실행"""
    print("=== 인력/보상 대시보드 API 테스트 ===\n")
    
    # 테스트 클라이언트 생성
    client = Client()
    
    # 테스트 사용자 로그인
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ admin 사용자가 없습니다. 먼저 관리자 계정을 생성하세요.")
        return
    
    client.force_login(user)
    print("✅ 로그인 성공\n")
    
    # API 호출
    print("[1] API 엔드포인트 테스트")
    response = client.get('/api/workforce-comp/')
    
    if response.status_code == 200:
        print("✅ API 호출 성공 (200 OK)")
        data = response.json()
        
        # 응답 구조 확인
        print("\n[2] 응답 구조 확인")
        if data.get('success'):
            print("✅ success 필드 존재")
        else:
            print("❌ success 필드 누락 또는 false")
        
        # 데이터 필드 확인
        print("\n[3] 데이터 필드 검증")
        if 'data' in data:
            api_data = data['data']
            
            # Workforce 데이터
            if 'workforce' in api_data:
                workforce = api_data['workforce']
                print("\n[Workforce 데이터]")
                print(f"  totalEmployees: {workforce.get('totalEmployees', 'N/A')}")
                print(f"  activeEmployees: {workforce.get('activeEmployees', 'N/A')}")
                print(f"  newHiresMonth: {workforce.get('newHiresMonth', 'N/A')}")
            else:
                print("❌ workforce 데이터 누락")
            
            # Compensation 데이터
            if 'compensation' in api_data:
                compensation = api_data['compensation']
                print("\n[Compensation 데이터]")
                print(f"  totalPayroll: {compensation.get('totalPayroll', 'N/A')}")
                print(f"  avgSalary: {compensation.get('avgSalary', 'N/A')}")
                print(f"  maxSalary: {compensation.get('maxSalary', 'N/A')}")
                print(f"  minSalary: {compensation.get('minSalary', 'N/A')}")
            else:
                print("❌ compensation 데이터 누락")
            
            # Departments 데이터
            if 'departments' in api_data:
                departments = api_data['departments']
                print(f"\n[Departments 데이터]")
                print(f"  부서 수: {len(departments)}")
                if departments:
                    dept = departments[0]
                    print(f"  첫 번째 부서 구조:")
                    print(f"    - departmentName: {dept.get('departmentName', 'N/A')}")
                    print(f"    - employeeCount: {dept.get('employeeCount', 'N/A')}")
                    print(f"    - avgSalary: {dept.get('avgSalary', 'N/A')}")
            else:
                print("❌ departments 데이터 누락")
        else:
            print("❌ data 필드 누락")
        
        # 필드명 변환 확인
        print("\n[4] 필드명 변환 확인")
        json_str = json.dumps(data, indent=2)
        
        snake_case_found = []
        if 'employee_count' in json_str:
            snake_case_found.append('employee_count')
        if 'avg_salary' in json_str:
            snake_case_found.append('avg_salary')
        if 'total_salary' in json_str:
            snake_case_found.append('total_salary')
        
        if snake_case_found:
            print(f"❌ Snake case 필드 발견: {', '.join(snake_case_found)}")
        else:
            print("✅ 모든 필드가 camelCase로 변환됨")
        
        # NULL 처리 확인
        print("\n[5] NULL/undefined 처리 확인")
        null_count = json_str.count('null')
        if null_count > 0:
            print(f"⚠️  {null_count}개의 null 값 발견 (기본값 처리 필요)")
        else:
            print("✅ null 값 없음")
        
    else:
        print(f"❌ API 호출 실패 (상태 코드: {response.status_code})")
        print(f"응답: {response.content.decode('utf-8')}")
    
    # 페이지 렌더링 테스트
    print("\n\n[6] 대시보드 페이지 렌더링 테스트")
    response = client.get('/dashboards/workforce-comp/')
    
    if response.status_code == 200:
        print("✅ 페이지 렌더링 성공")
        
        # JavaScript 유틸리티 확인
        content = response.content.decode('utf-8')
        if 'api_transformer.js' in content:
            print("✅ api_transformer.js 로드됨")
        else:
            print("❌ api_transformer.js 누락")
        
        if 'safe_data_accessor.js' in content:
            print("✅ safe_data_accessor.js 로드됨")
        else:
            print("❌ safe_data_accessor.js 누락")
        
        if 'fetchDashboardData' in content:
            print("✅ API 호출 함수 존재")
        else:
            print("❌ API 호출 함수 누락")
    else:
        print(f"❌ 페이지 렌더링 실패 (상태 코드: {response.status_code})")
    
    print("\n=== 테스트 완료 ===")


def create_test_data():
    """테스트 데이터 생성"""
    print("\n[테스트 데이터 생성]")
    
    # 직원 수 확인
    employee_count = Employee.objects.count()
    print(f"현재 직원 수: {employee_count}")
    
    if employee_count == 0:
        print("⚠️  직원 데이터가 없습니다. 테스트 데이터를 생성하세요.")
    
    # 보상 데이터 확인
    comp_count = EmployeeCompensation.objects.count()
    print(f"현재 보상 데이터 수: {comp_count}")
    
    if comp_count == 0:
        print("⚠️  보상 데이터가 없습니다. 테스트 데이터를 생성하세요.")


if __name__ == '__main__':
    test_workforce_comp_api()
    create_test_data()