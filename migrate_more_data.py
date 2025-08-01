#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django
import sqlite3
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.models import Employee

def migrate_additional_employees():
    """추가 직원 데이터 마이그레이션 (101번째부터 500번째까지)"""
    
    # SQLite 연결
    conn = sqlite3.connect('hris_dummy.db')
    cursor = conn.cursor()
    
    # 기존 이메일 목록 가져오기
    existing_emails = set(Employee.objects.values_list('email', flat=True))
    
    # 101번째부터 500번째 직원 가져오기
    cursor.execute('SELECT * FROM employee LIMIT 400 OFFSET 100')
    employees = cursor.fetchall()
    
    success = 0
    skip = 0
    
    # 직급 매핑
    position_map = {
        '사원': ('사원', 1),
        '주임': ('주임', 1),
        '대리': ('대리', 2),
        '과장': ('과장', 3),
        '차장': ('차장', 3),
        '팀장': ('팀장', 4),
        '부장': ('부장', 4),
        '부부장': ('부부장', 4),
        '상무': ('상무', 5),
        '전무': ('전무', 5),
        '부사장': ('부사장', 5),
        '사장': ('사장', 6),
        '회장': ('회장', 6)
    }
    
    # 부서 매핑
    dept_map = {
        'IT': ['IT기획', 'IT개발', 'IT운영'],
        'HR': ['경영관리'],
        'FINANCE': ['경영관리'],
        'MARKETING': ['경영관리'],
        'SALES': ['기업영업'],
        'OPERATIONS': ['경영관리']
    }
    
    for emp in employees:
        try:
            emp_id = emp[0]
            name = emp[1]
            birth_date = emp[2]
            gender = emp[3]
            join_date = emp[4]
            company = emp[5]
            division = emp[6]
            department = emp[7]
            position = emp[8]
            role = emp[9]
            employment_type = emp[10]
            status = emp[11]
            
            email = f"emp{emp_id}@okgroup.com"
            
            # 중복 체크
            if email in existing_emails:
                skip += 1
                continue
            
            # 부서 매핑
            dept = 'IT'
            if '인사' in department:
                dept = 'HR'
            elif '재무' in department:
                dept = 'FINANCE'
            elif '마케팅' in department:
                dept = 'MARKETING'
            elif '영업' in department:
                dept = 'SALES'
            elif '운영' in department:
                dept = 'OPERATIONS'
            
            # 직급과 레벨
            new_pos, level = position_map.get(position, ('사원', 1))
            
            # job_type 결정
            job_types = dept_map.get(dept, ['경영관리'])
            job_type = random.choice(job_types)
            
            # Employee 생성
            Employee.objects.create(
                name=name,
                email=email,
                department=dept,
                position=position,
                new_position=new_pos,
                growth_level=level,
                hire_date=join_date,
                phone=f"010-{emp_id[-4:]}-{random.randint(1000, 9999)}",
                job_group='Non-PL',
                job_type=job_type,
                job_role=role,
                grade_level=random.randint(1, 5),
                employment_type='정규직' if employment_type == '정규직' else '계약직',
                employment_status='재직' if status == '재직' else status,
                address=f"{division} {department}"
            )
            
            success += 1
            existing_emails.add(email)
            
            if success % 50 == 0:
                print(f"{success}명 완료...")
            
        except Exception as e:
            continue
    
    conn.close()
    
    print(f"\n추가 마이그레이션 완료:")
    print(f"  성공: {success}명")
    print(f"  건너뜀: {skip}명")
    print(f"  총 직원 수: {Employee.objects.count()}명")
    
    # 조직 구조 업데이트
    update_organization_structure()

def update_organization_structure():
    """조직 구조 업데이트"""
    print("\n조직 구조 업데이트 중...")
    
    departments = ['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']
    
    for dept in departments:
        # 부서별 최고 직급자 찾기
        dept_head = Employee.objects.filter(
            department=dept,
            new_position__in=['부장', '본부장', '부사장']
        ).order_by('-growth_level').first()
        
        if dept_head:
            # 팀장들을 부서장 아래에
            team_leaders = Employee.objects.filter(
                department=dept,
                new_position='팀장',
                manager__isnull=True
            )[:5]  # 부서별 최대 5명의 팀장
            
            for tl in team_leaders:
                tl.manager = dept_head
                tl.save()
            
            # 각 팀장 아래에 팀원들 배치
            for tl in team_leaders:
                members = Employee.objects.filter(
                    department=dept,
                    new_position__in=['사원', '주임', '대리', '과장', '차장'],
                    manager__isnull=True
                )[:10]  # 팀당 최대 10명
                
                for member in members:
                    member.manager = tl
                    member.save()
    
    print("조직 구조 업데이트 완료!")

if __name__ == '__main__':
    migrate_additional_employees()