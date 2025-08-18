#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터 품질 점검 스크립트
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db.models import Count, Q

def check_data_quality():
    """데이터 품질 점검"""
    
    print("=" * 80)
    print("직원 데이터 품질 점검")
    print("=" * 80)
    
    # 1. 전체 직원 수
    total = Employee.objects.count()
    print(f"\n[전체 직원 수] {total}명")
    
    # 2. 이름 필드 점검
    print("\n[이름 필드 점검]")
    
    # 이메일이 이름에 들어간 케이스
    email_in_name = Employee.objects.filter(name__contains='@').count()
    print(f"  - 이름에 @ 포함: {email_in_name}명")
    
    # 빈 이름
    empty_name = Employee.objects.filter(Q(name='') | Q(name__isnull=True)).count()
    print(f"  - 빈 이름: {empty_name}명")
    
    # 샘플 출력
    if email_in_name > 0:
        print("\n  [문제 샘플 - 이름에 이메일]")
        for emp in Employee.objects.filter(name__contains='@')[:3]:
            print(f"    ID {emp.id}: 이름={emp.name}, 이메일={emp.email}")
    
    # 3. 부서 필드 점검
    print("\n[부서 필드 점검]")
    
    # department 필드
    dept_empty = Employee.objects.filter(Q(department='') | Q(department__isnull=True)).count()
    dept_it = Employee.objects.filter(department='IT').count()
    dept_other = Employee.objects.exclude(department='IT').exclude(department='').exclude(department__isnull=True).count()
    
    print(f"  - department 필드:")
    print(f"    * 비어있음: {dept_empty}명")
    print(f"    * IT: {dept_it}명")
    print(f"    * 기타: {dept_other}명")
    
    # final_department 필드
    final_dept_empty = Employee.objects.filter(Q(final_department='') | Q(final_department__isnull=True)).count()
    final_dept_filled = Employee.objects.exclude(final_department='').exclude(final_department__isnull=True).count()
    
    print(f"\n  - final_department 필드:")
    print(f"    * 비어있음: {final_dept_empty}명")
    print(f"    * 값 있음: {final_dept_filled}명")
    
    # 4. 직급 필드 점검
    print("\n[직급 필드 점검]")
    
    # position 분포
    position_stats = Employee.objects.values('position').annotate(count=Count('id')).order_by('-count')
    print("  - position 필드 분포:")
    for stat in position_stats:
        if stat['position']:
            print(f"    * {stat['position']}: {stat['count']}명")
    
    # current_position 분포
    current_pos_empty = Employee.objects.filter(Q(current_position='') | Q(current_position__isnull=True)).count()
    current_pos_filled = Employee.objects.exclude(current_position='').exclude(current_position__isnull=True).count()
    
    print(f"\n  - current_position 필드:")
    print(f"    * 비어있음: {current_pos_empty}명")
    print(f"    * 값 있음: {current_pos_filled}명")
    
    if current_pos_filled > 0:
        print("\n  [current_position 샘플]")
        for pos in Employee.objects.exclude(current_position='').exclude(current_position__isnull=True).values('current_position').annotate(count=Count('id')).order_by('-count')[:5]:
            print(f"    * {pos['current_position']}: {pos['count']}명")
    
    # 5. 회사 필드 점검
    print("\n[회사 필드 점검]")
    company_stats = Employee.objects.values('company').annotate(count=Count('id')).order_by('-count')
    for stat in company_stats[:10]:
        if stat['company']:
            print(f"  - {stat['company']}: {stat['count']}명")
    
    # 6. 정상 데이터 샘플
    print("\n[정상 데이터 샘플 - 최근 5명]")
    for emp in Employee.objects.all().order_by('-id')[:5]:
        print(f"\n  ID {emp.id}:")
        print(f"    이름: {emp.name}")
        print(f"    이메일: {emp.email}")
        print(f"    회사: {emp.company}")
        print(f"    부서: {emp.department} / {emp.final_department}")
        print(f"    직급: {emp.position} / {emp.current_position}")
        print(f"    입사일: {emp.hire_date}")
    
    print("\n" + "=" * 80)
    print("데이터 품질 점검 완료")
    print("=" * 80)

if __name__ == "__main__":
    check_data_quality()