#!/usr/bin/env python
"""
권한 관리 시스템 초기 데이터 생성 스크립트
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from permissions.models import HRRole, DataAccessRule
from employees.models import Employee
from django.contrib.auth.models import User

def create_hr_roles():
    """HR 역할 생성"""
    print("HR 역할 생성 중...")
    
    roles_data = [
        ('HR_ADMIN', 'HR 시스템 전체 관리자'),
        ('HR_MANAGER', 'HR 업무 담당자'),
        ('DEPT_HEAD', '부서장 - 부서 인원 관리'),
        ('TEAM_LEADER', '팀장 - 팀 인원 관리'),
        ('EMPLOYEE', '일반 직원 - 본인 정보만'),
        ('EXECUTIVE', '임원 - 전사 데이터 조회'),
    ]
    
    for role_name, desc in roles_data:
        role, created = HRRole.objects.get_or_create(
            name=role_name,
            defaults={'description': desc}
        )
        if created:
            print(f"  ✓ {role.get_name_display()} 생성")
        else:
            print(f"  ○ {role.get_name_display()} 이미 존재")

def create_data_access_rules():
    """데이터 접근 규칙 설정"""
    print("\n데이터 접근 규칙 설정 중...")
    
    access_rules = [
        # HR_ADMIN은 모든 권한
        ('HR_ADMIN', 'Employee', 'COMPANY', True, True, True, True),
        ('HR_ADMIN', 'ComprehensiveEvaluation', 'COMPANY', True, True, True, True),
        ('HR_ADMIN', 'EmployeeCompensation', 'COMPANY', True, True, True, True),
        ('HR_ADMIN', 'PromotionRequest', 'COMPANY', True, True, True, True),
        
        # HR_MANAGER는 HR 관련 모든 권한
        ('HR_MANAGER', 'Employee', 'COMPANY', True, True, False, True),
        ('HR_MANAGER', 'ComprehensiveEvaluation', 'COMPANY', True, True, False, True),
        ('HR_MANAGER', 'EmployeeCompensation', 'COMPANY', True, True, False, True),
        ('HR_MANAGER', 'PromotionRequest', 'COMPANY', True, True, False, True),
        
        # DEPT_HEAD는 부서 데이터 조회/수정
        ('DEPT_HEAD', 'Employee', 'DEPT', True, True, False, True),
        ('DEPT_HEAD', 'ComprehensiveEvaluation', 'DEPT', True, True, False, True),
        ('DEPT_HEAD', 'EmployeeCompensation', 'DEPT', True, False, False, False),
        ('DEPT_HEAD', 'PromotionRequest', 'DEPT', True, True, False, True),
        
        # TEAM_LEADER는 팀 데이터 조회/수정
        ('TEAM_LEADER', 'Employee', 'TEAM', True, True, False, False),
        ('TEAM_LEADER', 'ComprehensiveEvaluation', 'TEAM', True, True, False, False),
        ('TEAM_LEADER', 'EmployeeCompensation', 'TEAM', True, False, False, False),
        ('TEAM_LEADER', 'PromotionRequest', 'TEAM', True, True, False, False),
        
        # EXECUTIVE는 전사 데이터 조회
        ('EXECUTIVE', 'Employee', 'COMPANY', True, False, False, False),
        ('EXECUTIVE', 'ComprehensiveEvaluation', 'COMPANY', True, False, False, False),
        ('EXECUTIVE', 'EmployeeCompensation', 'COMPANY', True, False, False, False),
        ('EXECUTIVE', 'PromotionRequest', 'COMPANY', True, False, False, False),
        
        # EMPLOYEE는 본인 데이터만
        ('EMPLOYEE', 'Employee', 'SELF', True, True, False, False),
        ('EMPLOYEE', 'ComprehensiveEvaluation', 'SELF', True, False, False, False),
        ('EMPLOYEE', 'EmployeeCompensation', 'SELF', True, False, False, False),
        ('EMPLOYEE', 'PromotionRequest', 'SELF', True, True, False, False),
    ]
    
    for role_name, model, level, view, edit, delete, approve in access_rules:
        try:
            role = HRRole.objects.get(name=role_name)
            rule, created = DataAccessRule.objects.get_or_create(
                role=role,
                model_name=model,
                defaults={
                    'access_level': level,
                    'can_view': view,
                    'can_edit': edit,
                    'can_delete': delete,
                    'can_approve': approve,
                }
            )
            if created:
                print(f"  ✓ {role.get_name_display()} - {model} 규칙 생성")
            else:
                print(f"  ○ {role.get_name_display()} - {model} 규칙 이미 존재")
        except HRRole.DoesNotExist:
            print(f"  ❌ 역할 {role_name}을 찾을 수 없습니다")

def assign_default_roles():
    """기본 역할 할당"""
    print("\n기본 역할 할당 중...")
    
    try:
        # 모든 직원에게 기본 EMPLOYEE 역할 할당
        from permissions.models import EmployeeRole
        
        employees = Employee.objects.all()
        employee_role = HRRole.objects.get(name='EMPLOYEE')
        
        for employee in employees:
            emp_role, created = EmployeeRole.objects.get_or_create(
                employee=employee,
                role=employee_role,
                defaults={'is_active': True}
            )
            if created:
                print(f"  ✓ {employee.name}에게 EMPLOYEE 역할 할당")
        
        print(f"총 {employees.count()}명의 직원에게 기본 역할 할당 완료")
        
    except Exception as e:
        print(f"  ❌ 역할 할당 중 오류: {e}")

def main():
    """메인 실행 함수"""
    print("=== 권한 관리 시스템 초기 데이터 생성 ===")
    
    try:
        # HR 역할 생성
        create_hr_roles()
        
        # 데이터 접근 규칙 설정
        create_data_access_rules()
        
        # 기본 역할 할당
        assign_default_roles()
        
        print("\n=== 초기 데이터 생성 완료 ===")
        print("이제 /permissions/ 경로에서 권한 관리 시스템을 확인할 수 있습니다.")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 