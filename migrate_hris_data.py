#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django
import sqlite3
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

# 직급 매핑
POSITION_MAPPING = {
    '회장': '회장',
    '부회장': '부사장',
    '사장': '사장',
    '부사장': '부사장',
    '전무': '전무',
    '상무': '상무',
    '부장': '부장',
    '팀장': '팀장',
    '차장': '차장',
    '과장': '과장',
    '대리': '대리',
    '주임': '주임',
    '사원': '사원',
    '계약직': '사원',
    '인턴': '사원'
}

# 부서 매핑
DEPARTMENT_MAPPING = {
    'IT기획팀': 'IT',
    'IT개발팀': 'IT',
    'IT운영팀': 'IT',
    '인사기획팀': 'HR',
    '인사운영팀': 'HR',
    '인사관리팀': 'HR',
    '재무기획팀': 'FINANCE',
    '재무관리팀': 'FINANCE',
    '마케팅기획팀': 'MARKETING',
    '마케팅운영팀': 'MARKETING',
    '영업기획팀': 'SALES',
    '영업운영팀': 'SALES',
    '운영기획팀': 'OPERATIONS',
    '경영기획팀': '경영진',
    '경영전략팀': '경영진'
}

# 직종 매핑 (role -> job_type)
JOB_TYPE_MAPPING = {
    'PM': 'IT기획',
    '개발': 'IT개발',
    '운영': 'IT운영',
    'AM': '경영관리',
    '관리': '경영관리',
    '영업': '기업영업',
    '기획': '경영관리'
}

def migrate_employees():
    """직원 데이터 마이그레이션"""
    
    # 기존 데이터 확인
    existing_count = Employee.objects.count()
    print(f"기존 직원 데이터: {existing_count}명")
    
    # SQLite 연결
    conn = sqlite3.connect('hris_dummy.db')
    cursor = conn.cursor()
    
    # 전체 직원 데이터 가져오기
    cursor.execute('SELECT * FROM employee ORDER BY employee_id')
    employees = cursor.fetchall()
    
    success_count = 0
    error_count = 0
    skip_count = 0
    
    print(f"\n총 {len(employees)}명의 직원 데이터 마이그레이션 시작...")
    
    # 관리자 정보를 저장할 딕셔너리 (나중에 관계 설정용)
    manager_relations = {}
    
    for emp in employees:
        try:
            employee_id = emp[0]
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
            
            # 이메일 생성 (employee_id 기반)
            email = f"emp{employee_id}@okgroup.com"
            
            # 중복 체크
            if Employee.objects.filter(email=email).exists():
                skip_count += 1
                continue
            
            # 부서 매핑
            dept_mapped = 'IT'  # 기본값
            for key, value in DEPARTMENT_MAPPING.items():
                if key in department:
                    dept_mapped = value
                    break
            
            # 직급 매핑
            position_mapped = POSITION_MAPPING.get(position, '사원')
            
            # 직종 매핑
            job_type_mapped = JOB_TYPE_MAPPING.get(role, '경영관리')
            
            # 성장레벨 결정 (직급 기반)
            growth_level = 1
            if position in ['사원', '주임', '계약직', '인턴']:
                growth_level = 1
            elif position in ['대리']:
                growth_level = 2
            elif position in ['과장', '차장']:
                growth_level = 3
            elif position in ['팀장', '부장']:
                growth_level = 4
            elif position in ['상무', '전무']:
                growth_level = 5
            elif position in ['사장', '부사장', '부회장', '회장']:
                growth_level = 6
            
            # User 객체 생성
            username = f"user{employee_id}"
            user = User.objects.create_user(
                username=username,
                email=email,
                password='okfinance2025!',  # 기본 비밀번호
                first_name=name[1:] if len(name) > 1 else name,
                last_name=name[0] if len(name) > 0 else ''
            )
            
            # Employee 객체 생성
            employee = Employee.objects.create(
                user=user,
                name=name,
                email=email,
                department=dept_mapped,
                position=position,  # 원래 직급 (나중에 삭제 예정)
                new_position=position_mapped,
                hire_date=join_date,
                phone=f"010-{employee_id[-4:]}-{employee_id[-4:]}",
                job_group='Non-PL',  # 기본값
                job_type=job_type_mapped,
                job_role=role,
                growth_level=growth_level,
                grade_level=1,
                employment_type='정규직' if employment_type == '정규직' else '계약직',
                employment_status='재직' if status == '재직' else status,
                address=f"{division} {department}",
                emergency_contact='',
                emergency_phone=''
            )
            
            success_count += 1
            
            # 진행 상황 출력
            if success_count % 100 == 0:
                print(f"  {success_count}명 완료...")
                
        except Exception as e:
            error_count += 1
            print(f"  오류 발생 - {name} ({employee_id}): {str(e)}")
    
    conn.close()
    
    print(f"\n=== 마이그레이션 완료 ===")
    print(f"성공: {success_count}명")
    print(f"건너뜀: {skip_count}명")
    print(f"실패: {error_count}명")
    print(f"총 직원 수: {Employee.objects.count()}명")
    
    # 조직 구조 설정 (간단한 예시)
    set_organization_structure()

def set_organization_structure():
    """조직 구조(상사-부하 관계) 설정"""
    print("\n조직 구조 설정 중...")
    
    try:
        # 회장 찾기
        ceos = Employee.objects.filter(new_position='회장')
        if not ceos.exists():
            print("회장을 찾을 수 없습니다.")
            return
        
        ceo = ceos.first()
        
        # 부사장들을 회장 아래에
        vps = Employee.objects.filter(new_position__in=['부사장', '부회장'])
        for vp in vps:
            vp.manager = ceo
            vp.save()
        
        # 부장들을 부사장 아래에 (부서별로)
        for dept in ['IT', 'HR', 'FINANCE', 'MARKETING', 'SALES', 'OPERATIONS']:
            dept_vp = vps.filter(department=dept).first()
            if dept_vp:
                directors = Employee.objects.filter(
                    department=dept,
                    new_position__in=['부장', '본부장']
                )
                for director in directors:
                    director.manager = dept_vp
                    director.save()
                
                # 팀장들을 부장 아래에
                dept_director = directors.first()
                if dept_director:
                    team_leaders = Employee.objects.filter(
                        department=dept,
                        new_position='팀장'
                    )
                    for team_leader in team_leaders:
                        team_leader.manager = dept_director
                        team_leader.save()
        
        print("조직 구조 설정 완료!")
        
    except Exception as e:
        print(f"조직 구조 설정 중 오류: {str(e)}")

if __name__ == '__main__':
    print("=== HRIS 더미 데이터 마이그레이션 시작 ===")
    
    # 자동 진행 (기존 데이터 유지)
    print("\n기존 데이터를 유지하면서 새 데이터를 추가합니다.")
    
    migrate_employees()
    print("\n마이그레이션이 완료되었습니다!")