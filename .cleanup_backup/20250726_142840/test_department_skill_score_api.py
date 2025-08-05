"""
부서별 스킬 점수 API 테스트
Department Skill Score API Test
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

from django.contrib.auth.models import User
from employees.models import Employee
from django.test import Client

def test_department_skill_score_api():
    """부서별 스킬 점수 API 테스트"""
    print("\n" + "="*60)
    print("부서별 스킬 점수 API 테스트")
    print("="*60 + "\n")
    
    # 테스트 클라이언트 생성
    client = Client()
    
    # 테스트용 사용자 로그인
    try:
        # 관리자 계정으로 로그인
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("[ERROR] 관리자 계정을 찾을 수 없습니다.")
            return
        
        client.force_login(user)
        print(f"[OK] 로그인 완료: {user.username}")
        
    except Exception as e:
        print(f"[ERROR] 로그인 실패: {str(e)}")
        return
    
    # 1. 특정 부서 스킬 점수 조회 테스트
    print("\n[ 1. 특정 부서 스킬 점수 조회 ]")
    try:
        response = client.get('/api/skillmap/department-skill-score/IT/')
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] 상태: {data.get('status')}")
            if data.get('status') == 'success':
                summary = data.get('summary', {})
                print(f"[OK] 부서: {data.get('department')}")
                print(f"[OK] 직원 수: {summary.get('total_employees')}")
                print(f"[OK] 분석된 스킬: {summary.get('total_skills')}")
                print(f"[OK] 평균 숙련도: {summary.get('avg_proficiency')}%")
                print(f"[OK] 평균 갭: {summary.get('avg_gap')}%")
                
                # 상위 갭 스킬
                top_gaps = data.get('top_gaps', [])
                if top_gaps:
                    print("\n상위 갭 스킬:")
                    for i, gap in enumerate(top_gaps[:3], 1):
                        print(f"  {i}. {gap['skill_name']} - 갭: {gap['gap_score']}%")
            else:
                print(f"[WARNING] 경고: {data.get('message')}")
        else:
            print(f"[ERROR] API 호출 실패: {response.status_code}")
            print(f"응답: {response.content.decode('utf-8')}")
            
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
    
    # 2. 현재 사용자 부서 스킬 점수 조회
    print("\n[ 2. 현재 사용자 부서 스킬 점수 조회 ]")
    try:
        # 테스트용 직원 생성 또는 조회
        employee = Employee.objects.filter(user=user).first()
        if not employee:
            # 직원 데이터가 없으면 임시 생성
            employee = Employee.objects.create(
                user=user,
                employee_id=f"TEST{user.id}",
                name="테스트 직원",
                department="IT",
                position="STAFF",
                job_group="PL",
                job_type="IT개발",
                growth_level=3
            )
            print(f"[OK] 테스트 직원 생성: {employee.name}")
        
        response = client.get('/api/skillmap/department-skill-score/')
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] 자동 감지된 부서: {data.get('department', employee.department)}")
            print(f"[OK] 상태: {data.get('status')}")
        else:
            print(f"[ERROR] API 호출 실패: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
    
    # 3. 요약 정보만 조회
    print("\n[ 3. 요약 정보만 조회 ]")
    try:
        response = client.get('/api/skillmap/department-skill-score/IT/?include_details=false')
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] 요약 모드 응답 수신")
            print(f"[OK] 포함된 필드: {list(data.keys())}")
        else:
            print(f"[ERROR] API 호출 실패: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
    
    # 4. 여러 부서 일괄 처리
    print("\n[ 4. 여러 부서 일괄 처리 ]")
    try:
        request_data = {
            "departments": ["IT", "SALES", "FINANCE"],
            "skill_requirements": {
                "Python": {"required_level": 3, "category": "technical", "weight": 1.5},
                "프로젝트관리": {"required_level": 2, "category": "business", "weight": 1.0}
            }
        }
        
        response = client.post(
            '/api/skillmap/department-skill-score/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] 일괄 처리 완료")
            results = data.get('results', {})
            for dept, result in results.items():
                if result.get('status') == 'success':
                    summary = result.get('summary', {})
                    print(f"  - {dept}: 직원 {summary.get('total_employees')}명, "
                          f"평균 숙련도 {summary.get('avg_proficiency')}%")
                else:
                    print(f"  - {dept}: {result.get('message')}")
        else:
            print(f"[ERROR] API 호출 실패: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
    
    # 5. 잘못된 부서명 테스트
    print("\n[ 5. 오류 처리 테스트 ]")
    try:
        response = client.get('/api/skillmap/department-skill-score/INVALID_DEPT/')
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] 상태: {data.get('status')}")
            print(f"[OK] 메시지: {data.get('message')}")
        else:
            print(f"[OK] 예상된 오류 응답: {response.status_code}")
            
    except Exception as e:
        print(f"[OK] 예상된 오류: {str(e)}")
    
    print("\n" + "="*60)
    print("테스트 완료!")
    print("="*60)

if __name__ == "__main__":
    test_department_skill_score_api()