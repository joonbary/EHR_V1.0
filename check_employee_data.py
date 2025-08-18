#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직원 데이터베이스 점검 스크립트
"""

import os
import django
import sys
from datetime import datetime

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection
from django.db.models import Count, Q, Avg, Min, Max
from employees.models import Employee

def check_employee_database():
    """직원 데이터베이스 상태 점검"""
    
    print("=" * 80)
    print("직원 데이터베이스 점검 시작")
    print("=" * 80)
    
    # 1. 전체 직원 수
    total_employees = Employee.objects.count()
    print(f"\n[전체 직원 수] {total_employees:,}명")
    
    # 2. 재직 상태별 통계
    print("\n[재직 상태별 통계]")
    employment_status = Employee.objects.values('employment_status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for status in employment_status:
        status_name = status['employment_status'] or '미지정'
        print(f"  - {status_name}: {status['count']:,}명")
    
    # 3. 회사별 통계
    print("\n[회사별 통계]")
    company_stats = Employee.objects.exclude(company__isnull=True).exclude(company='').values('company').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for comp in company_stats[:15]:  # 상위 15개 회사만
        print(f"  - {comp['company']}: {comp['count']:,}명")
    
    # 4. 부서별 통계
    print("\n[부서별 통계 - department 필드]")
    dept_stats = Employee.objects.exclude(department__isnull=True).exclude(department='').values('department').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for dept in dept_stats[:10]:  # 상위 10개 부서만
        print(f"  - {dept['department']}: {dept['count']:,}명")
    
    # 5. 최종소속별 통계
    print("\n[최종소속별 통계 - final_department 필드]")
    final_dept_stats = Employee.objects.exclude(final_department__isnull=True).exclude(final_department='').values('final_department').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for dept in final_dept_stats[:10]:  # 상위 10개 부서만
        print(f"  - {dept['final_department']}: {dept['count']:,}명")
    
    # 6. 직급별 통계
    print("\n[직급별 통계 - position 필드]")
    position_stats = Employee.objects.exclude(position__isnull=True).exclude(position='').values('position').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for pos in position_stats[:10]:
        print(f"  - {pos['position']}: {pos['count']:,}명")
    
    # 7. 현재직급별 통계
    print("\n[현재직급별 통계 - current_position 필드]")
    current_pos_stats = Employee.objects.exclude(current_position__isnull=True).exclude(current_position='').values('current_position').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for pos in current_pos_stats[:10]:
        print(f"  - {pos['current_position']}: {pos['count']:,}명")
    
    # 8. 성별 통계
    print("\n[성별 통계]")
    gender_stats = Employee.objects.values('gender').annotate(
        count=Count('id')
    ).order_by('gender')
    
    for gender in gender_stats:
        gender_name = {'M': '남성', 'F': '여성', None: '미지정', '': '미지정'}.get(gender['gender'], gender['gender'])
        print(f"  - {gender_name}: {gender['count']:,}명")
    
    # 9. 나이 통계
    print("\n[나이 통계]")
    age_stats = Employee.objects.exclude(age__isnull=True).aggregate(
        avg_age=Avg('age'),
        min_age=Min('age'),
        max_age=Max('age')
    )
    
    if age_stats['avg_age']:
        print(f"  - 평균 나이: {age_stats['avg_age']:.1f}세")
        print(f"  - 최소 나이: {age_stats['min_age']}세")
        print(f"  - 최대 나이: {age_stats['max_age']}세")
    
    age_ranges = [
        (20, 29, '20대'),
        (30, 39, '30대'),
        (40, 49, '40대'),
        (50, 59, '50대'),
        (60, 70, '60대 이상')
    ]
    
    for min_age, max_age, label in age_ranges:
        count = Employee.objects.filter(age__gte=min_age, age__lte=max_age).count()
        if count > 0:
            print(f"  - {label}: {count:,}명")
    
    # 10. 입사년도 통계
    print("\n[입사년도 통계 - 최근 5년]")
    current_year = datetime.now().year
    for year in range(current_year, current_year - 5, -1):
        count = Employee.objects.filter(hire_date__year=year).count()
        if count > 0:
            print(f"  - {year}년: {count:,}명")
    
    # 11. 데이터 품질 점검
    print("\n[데이터 품질 점검]")
    
    # 필수 필드 누락 체크
    no_name = Employee.objects.filter(Q(name__isnull=True) | Q(name='')).count()
    no_email = Employee.objects.filter(Q(email__isnull=True) | Q(email='')).count()
    no_department = Employee.objects.filter(Q(department__isnull=True) | Q(department='')).count()
    no_position = Employee.objects.filter(Q(position__isnull=True) | Q(position='')).count()
    
    print(f"  - 이름 누락: {no_name}명")
    print(f"  - 이메일 누락: {no_email}명")
    print(f"  - 부서 누락: {no_department}명")
    print(f"  - 직급 누락: {no_position}명")
    
    # 12. 중복 데이터 체크
    print("\n[중복 데이터 체크]")
    
    # 이메일 중복
    duplicate_emails = Employee.objects.values('email').annotate(
        count=Count('id')
    ).filter(count__gt=1).exclude(email='').exclude(email__isnull=True)
    
    if duplicate_emails:
        print(f"  [경고] 중복 이메일 발견: {len(duplicate_emails)}개")
        for dup in duplicate_emails[:5]:  # 상위 5개만 표시
            print(f"    - {dup['email']}: {dup['count']}개")
    else:
        print("  [OK] 이메일 중복 없음")
    
    # 13. 샘플 데이터 표시
    print("\n[샘플 직원 데이터 - 최근 입사 5명]")
    recent_employees = Employee.objects.exclude(hire_date__isnull=True).order_by('-hire_date')[:5]
    
    for emp in recent_employees:
        print(f"  - {emp.name} ({emp.company or '회사미지정'}/{emp.department or '부서미지정'}/{emp.current_position or emp.position or '직급미지정'})")
        print(f"    입사일: {emp.hire_date}, 이메일: {emp.email}")
    
    print("\n" + "=" * 80)
    print("직원 데이터베이스 점검 완료")
    print("=" * 80)

if __name__ == "__main__":
    check_employee_database()