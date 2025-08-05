#!/usr/bin/env python
"""
AIRISS 대시보드 통합 테스트 스크립트
"""
import os
import sys
import django
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from employees.models import Employee
from airiss.models import AIAnalysisType, AIAnalysisResult

def test_dashboards():
    """대시보드 URL 테스트"""
    print("=" * 60)
    print("AIRISS 대시보드 통합 테스트")
    print("=" * 60)
    
    client = Client()
    
    # 테스트할 URL 목록
    urls_to_test = [
        ('airiss:executive_dashboard', '경영진 대시보드'),
        ('airiss:employee_analysis_all', '전직원 분석'),
        ('airiss:msa_integration', 'AI 직원 분석'),
    ]
    
    print("\n1. URL 접근 테스트")
    print("-" * 60)
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            response = client.get(url)
            
            if response.status_code == 200:
                print(f"✅ {description}: {url} - 성공")
            elif response.status_code == 302:
                print(f"⚠️ {description}: {url} - 리다이렉트 (로그인 필요)")
            else:
                print(f"❌ {description}: {url} - 오류 ({response.status_code})")
        except Exception as e:
            print(f"❌ {description}: URL 오류 - {str(e)}")
    
    print("\n2. 데이터 확인")
    print("-" * 60)
    
    # 직원 데이터 확인
    total_employees = Employee.objects.filter(employment_status='재직').count()
    print(f"재직 중인 직원: {total_employees}명")
    
    # AI 분석 데이터 확인
    total_analyses = AIAnalysisResult.objects.count()
    print(f"AI 분석 결과: {total_analyses}건")
    
    # 분석 유형 확인
    analysis_types = AIAnalysisType.objects.filter(is_active=True).count()
    print(f"활성 분석 유형: {analysis_types}개")
    
    # 샘플 데이터 생성 제안
    if total_employees == 0:
        print("\n⚠️ 직원 데이터가 없습니다.")
        print("다음 명령으로 샘플 데이터를 생성할 수 있습니다:")
        print("python manage.py shell")
        print(">>> from employees.models import Employee")
        print(">>> Employee.objects.create(employee_id='EMP001', name='홍길동', department='개발팀', position='과장', employment_status='재직')")
    
    if total_analyses == 0:
        print("\n⚠️ AI 분석 데이터가 없습니다.")
        print("MSA 통합 페이지에서 AI 분석을 실행해보세요.")
    
    print("\n3. 개인별 분석 테스트")
    print("-" * 60)
    
    # 첫 번째 직원으로 테스트
    first_employee = Employee.objects.filter(employment_status='재직').first()
    if first_employee:
        try:
            url = reverse('airiss:employee_analysis_detail', args=[first_employee.id])
            response = client.get(url)
            
            if response.status_code == 200:
                print(f"✅ {first_employee.name}님 분석 페이지: {url} - 성공")
            elif response.status_code == 302:
                print(f"⚠️ {first_employee.name}님 분석 페이지: 로그인 필요")
            else:
                print(f"❌ {first_employee.name}님 분석 페이지: 오류 ({response.status_code})")
        except Exception as e:
            print(f"❌ 개인별 분석 페이지 오류: {str(e)}")
    else:
        print("⚠️ 테스트할 직원 데이터가 없습니다.")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
    
    print("\n📌 접속 방법:")
    print("1. Django 서버 시작: python manage.py runserver")
    print("2. 브라우저에서 접속: http://localhost:8000")
    print("3. AIRISS 메뉴에서 원하는 기능 선택:")
    print("   - 경영진 대시보드: /airiss/executive/")
    print("   - 전직원 분석: /airiss/employees/")
    print("   - AI 직원 분석: /airiss/msa/")
    print()

if __name__ == "__main__":
    test_dashboards()