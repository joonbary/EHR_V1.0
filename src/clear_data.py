#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation, ContributionEvaluation, ExpertiseEvaluation, ImpactEvaluation
from compensation.models import EmployeeCompensation
from promotions.models import PromotionRequest
from permissions.models import EmployeeRole

def clear_all_data():
    print("기존 테스트 데이터 삭제를 시작합니다...")
    
    # 데이터 삭제 순서 (외래키 의존성 고려)
    print("1. 권한 데이터 삭제 중...")
    EmployeeRole.objects.all().delete()
    
    print("2. 승진 요청 데이터 삭제 중...")
    PromotionRequest.objects.all().delete()
    
    print("3. 보상 데이터 삭제 중...")
    EmployeeCompensation.objects.all().delete()
    
    print("4. 평가 데이터 삭제 중...")
    ComprehensiveEvaluation.objects.all().delete()
    ContributionEvaluation.objects.all().delete()
    ExpertiseEvaluation.objects.all().delete()
    ImpactEvaluation.objects.all().delete()
    
    print("5. 직원 데이터 삭제 중...")
    Employee.objects.all().delete()
    
    print("6. 일반 사용자 데이터 삭제 중...")
    User.objects.filter(is_superuser=False).delete()
    
    print("기존 테스트 데이터 삭제가 완료되었습니다!")
    
    # 삭제 후 데이터 확인
    print(f"\n삭제 후 데이터 현황:")
    print(f"- 직원 수: {Employee.objects.count()}")
    print(f"- 사용자 수: {User.objects.count()}")
    print(f"- 평가 수: {ComprehensiveEvaluation.objects.count()}")
    print(f"- 보상 수: {EmployeeCompensation.objects.count()}")
    print(f"- 승진 요청 수: {PromotionRequest.objects.count()}")

if __name__ == "__main__":
    clear_all_data() 