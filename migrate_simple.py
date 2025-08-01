#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django
import sqlite3

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

def quick_migrate():
    """빠른 마이그레이션 (처음 100명만)"""
    
    # SQLite 연결
    conn = sqlite3.connect('hris_dummy.db')
    cursor = conn.cursor()
    
    # 처음 100명만 가져오기
    cursor.execute('SELECT * FROM employee LIMIT 100')
    employees = cursor.fetchall()
    
    success = 0
    
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
    
    for emp in employees:
        try:
            emp_id = emp[0]
            name = emp[1]
            position = emp[8]
            department = emp[7]
            
            # 부서 간단 매핑
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
            
            # Employee 생성 (User 없이)
            Employee.objects.create(
                name=name,
                email=f"emp{emp_id}@okgroup.com",
                department=dept,
                position=position,
                new_position=new_pos,
                growth_level=level,
                hire_date=emp[4],
                phone=f"010-{emp_id[-4:]}-0000",
                job_group='Non-PL',
                job_type='경영관리',
                employment_status='재직'
            )
            
            success += 1
            
        except Exception as e:
            pass
    
    conn.close()
    
    print(f"마이그레이션 완료: {success}명")
    print(f"총 직원 수: {Employee.objects.count()}명")

if __name__ == '__main__':
    quick_migrate()