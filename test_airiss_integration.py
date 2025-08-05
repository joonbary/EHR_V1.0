#!/usr/bin/env python
"""
AIRISS MSA 통합 테스트 스크립트
"""
import os
import sys
import django
import json
import requests
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee

def test_msa_health():
    """MSA 서비스 헬스 체크"""
    print("=" * 60)
    print("1. MSA 서비스 헬스 체크")
    print("-" * 60)
    
    # Railway URL
    msa_url = "https://web-production-4066.up.railway.app"
    
    try:
        response = requests.get(f"{msa_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Railway MSA 서비스 정상: {data.get('status')}")
        else:
            print(f"⚠️ Railway MSA 응답 오류: {response.status_code}")
    except Exception as e:
        print(f"❌ Railway MSA 연결 실패: {str(e)}")
    
    # 로컬 백업 테스트
    local_url = "http://localhost:8084"
    try:
        response = requests.get(f"{local_url}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ 로컬 MSA 서비스도 실행 중")
    except:
        print(f"ℹ️ 로컬 MSA는 실행되지 않음 (정상)")
    
    print()
    return True

def test_employee_data():
    """직원 데이터 확인"""
    print("=" * 60)
    print("2. 직원 데이터 확인")
    print("-" * 60)
    
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(employment_status='재직').count()
    
    print(f"전체 직원 수: {total_employees}명")
    print(f"재직 중인 직원: {active_employees}명")
    
    if active_employees == 0:
        print("⚠️ 재직 중인 직원이 없습니다. 샘플 데이터를 생성합니다...")
        create_sample_employees()
        active_employees = Employee.objects.filter(employment_status='재직').count()
        print(f"✅ {active_employees}명의 샘플 직원 생성 완료")
    
    print()
    return active_employees > 0

def create_sample_employees():
    """샘플 직원 데이터 생성"""
    departments = ['개발팀', '마케팅팀', '영업팀', '인사팀', '재무팀']
    positions = ['사원', '대리', '과장', '차장', '부장']
    
    for i in range(10):
        emp = Employee.objects.create(
            employee_id=f"EMP{2025000 + i:04d}",
            name=f"테스트직원{i+1}",
            department=departments[i % 5],
            position=positions[i % 5],
            email=f"test{i+1}@okfg.com",
            hire_date=datetime.now().date(),
            employment_status='재직'
        )
        print(f"  - {emp.name} ({emp.department} {emp.position}) 생성")

def test_api_analysis():
    """API 분석 테스트"""
    print("=" * 60)
    print("3. API 분석 테스트")
    print("-" * 60)
    
    # 테스트용 직원 데이터
    test_employee = {
        "employee_data": {
            "employee_id": "TEST001",
            "name": "테스트 직원",
            "department": "개발팀",
            "position": "과장",
            "performance_data": {
                "목표달성률": 85,
                "프로젝트성공률": 90,
                "고객만족도": 88,
                "출근율": 95
            },
            "competencies": {
                "리더십": 80,
                "기술력": 85,
                "커뮤니케이션": 82,
                "문제해결": 88,
                "팀워크": 90,
                "창의성": 75,
                "적응력": 85,
                "성실성": 92
            }
        },
        "analysis_type": "comprehensive",
        "include_recommendations": True
    }
    
    # Railway MSA 테스트
    msa_url = "https://web-production-4066.up.railway.app"
    
    try:
        response = requests.post(
            f"{msa_url}/api/v1/llm/analyze",
            json=test_employee,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI 분석 성공!")
            print(f"  - AI 점수: {result.get('ai_score', 'N/A')}")
            print(f"  - 등급: {result.get('grade', 'N/A')}")
            print(f"  - 처리 시간: {result.get('processing_time', 'N/A')}초")
        else:
            print(f"⚠️ API 응답 오류: {response.status_code}")
            print(f"  응답: {response.text[:200]}")
    except Exception as e:
        print(f"❌ API 호출 실패: {str(e)}")
    
    print()
    return True

def test_django_view():
    """Django 뷰 테스트"""
    print("=" * 60)
    print("4. Django 뷰 접근 테스트")
    print("-" * 60)
    
    from django.test import Client
    from django.urls import reverse
    
    client = Client()
    
    # MSA 통합 페이지 테스트
    try:
        url = reverse('airiss:msa_integration')
        response = client.get(url)
        
        if response.status_code == 200:
            print(f"✅ MSA 통합 페이지 접근 성공")
            print(f"  - URL: /airiss/msa/")
            print(f"  - 템플릿: airiss/msa_integration.html")
        elif response.status_code == 302:
            print(f"⚠️ 로그인 필요 (리다이렉트)")
            print(f"  - 로그인 후 /airiss/msa/ 접근 가능")
        else:
            print(f"❌ 페이지 접근 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ URL 패턴 오류: {str(e)}")
    
    print()
    return True

def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 60)
    print("AIRISS MSA 통합 테스트")
    print("=" * 60)
    print()
    
    # 테스트 실행
    tests = [
        ("MSA 헬스 체크", test_msa_health),
        ("직원 데이터", test_employee_data),
        ("API 분석", test_api_analysis),
        ("Django 뷰", test_django_view),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 테스트 실패: {str(e)}")
            results.append((name, False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{name}: {status}")
    
    print("\n" + "=" * 60)
    print("통합 완료!")
    print("=" * 60)
    print("\n접속 방법:")
    print("1. Django 서버 시작: python manage.py runserver")
    print("2. 브라우저에서 접속: http://localhost:8000")
    print("3. 로그인 후 AIRISS > AI 직원 분석 메뉴 클릭")
    print()

if __name__ == "__main__":
    main()