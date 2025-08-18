"""
API 엔드포인트 실제 테스트
Django 서버가 실행 중일 때 API 호출 테스트
"""

import requests
import json
from datetime import datetime

# 서버 URL (Django 개발 서버)
BASE_URL = "http://localhost:8000"

# 세션 생성 (로그인 상태 유지)
session = requests.Session()


def login():
    """관리자로 로그인"""
    login_url = f"{BASE_URL}/accounts/login/"
    
    # CSRF 토큰 가져오기
    response = session.get(login_url)
    csrftoken = session.cookies.get('csrftoken')
    
    # 로그인 시도
    login_data = {
        'username': 'admin',
        'password': 'admin',
        'csrfmiddlewaretoken': csrftoken
    }
    
    response = session.post(login_url, data=login_data)
    
    if response.status_code == 302:  # 리다이렉트 = 성공
        print("✓ 로그인 성공")
        return True
    else:
        print("✗ 로그인 실패")
        return False


def test_growth_level_status():
    """내 성장레벨 상태 조회 테스트"""
    print("\n" + "="*50)
    print("1. 내 성장레벨 상태 조회 테스트")
    print("="*50)
    
    url = f"{BASE_URL}/certifications/api/my-growth-level-status/"
    
    try:
        response = session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API 호출 성공")
            print(f"  - 현재 레벨: {data.get('growth_level', {}).get('current')}")
            print(f"  - 목표 레벨: {data.get('growth_level', {}).get('target')}")
            print(f"  - 인증 상태: {data.get('growth_level', {}).get('certification_status')}")
            
            progress = data.get('progress', {})
            if progress:
                print(f"  - 전체 진행률: {progress.get('overall', 0)}%")
        else:
            print(f"✗ API 호출 실패: {response.status_code}")
            print(f"  응답: {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ 오류 발생: {str(e)}")


def test_certification_check():
    """성장레벨 인증 체크 테스트"""
    print("\n" + "="*50)
    print("2. 성장레벨 인증 체크 테스트")
    print("="*50)
    
    url = f"{BASE_URL}/certifications/api/growth-level-certification-check/"
    
    # 테스트 데이터
    test_data = {
        "employee_id": "1",  # 첫 번째 직원 ID 사용
        "target_level": "Lv.3",
        "target_job_id": None
    }
    
    try:
        # CSRF 토큰 필요
        csrftoken = session.cookies.get('csrftoken')
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
        
        response = session.post(url, 
                              data=json.dumps(test_data),
                              headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API 호출 성공")
            print(f"  - 인증 결과: {data.get('certification_result')}")
            print(f"  - 부족한 교육: {data.get('missing_courses', [])}")
            print(f"  - 부족한 스킬: {data.get('missing_skills', [])}")
            print(f"  - 평가 충족: {data.get('eval_ok')}")
        else:
            print(f"✗ API 호출 실패: {response.status_code}")
            print(f"  응답: {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ 오류 발생: {str(e)}")


def test_training_recommendations():
    """교육 추천 API 테스트"""
    print("\n" + "="*50)
    print("3. 교육 추천 API 테스트")
    print("="*50)
    
    url = f"{BASE_URL}/trainings/api/my-growth-training-recommendations/"
    
    try:
        response = session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API 호출 성공")
            print(f"  - 상태: {data.get('status')}")
            
            context = data.get('context', {})
            if context:
                print(f"  - 목표 직무: {context.get('target_job')}")
                print(f"  - 부족 스킬: {context.get('missing_skills', [])}")
            
            recommendations = data.get('recommendations', [])
            print(f"  - 추천 교육 수: {len(recommendations)}")
            
            if recommendations:
                print("\n  추천 교육 TOP 3:")
                for i, course in enumerate(recommendations[:3], 1):
                    print(f"    {i}. {course.get('title')} (매칭: {course.get('match_score', 0)}%)")
                    
        else:
            print(f"✗ API 호출 실패: {response.status_code}")
            print(f"  응답: {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ 오류 발생: {str(e)}")


def test_progress_api():
    """진행률 조회 API 테스트"""
    print("\n" + "="*50)
    print("4. 성장레벨 진행률 조회 테스트")
    print("="*50)
    
    url = f"{BASE_URL}/certifications/api/growth-level-progress/"
    params = {"target_level": "Lv.3"}
    
    try:
        response = session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API 호출 성공")
            
            employee = data.get('employee', {})
            print(f"  - 직원: {employee.get('name')} (현재: {employee.get('current_level')})")
            print(f"  - 목표 레벨: {data.get('target_level')}")
            
            progress = data.get('progress', {})
            print("\n  진행률 상세:")
            print(f"    - 평가: {progress.get('evaluation', 0)}%")
            print(f"    - 교육: {progress.get('training', 0)}%")
            print(f"    - 스킬: {progress.get('skills', 0)}%")
            print(f"    - 경력: {progress.get('experience', 0)}%")
            print(f"    - 종합: {progress.get('overall', 0)}%")
            
            print(f"\n  인증 신청 가능: {'예' if data.get('can_apply') else '아니오'}")
            
        else:
            print(f"✗ API 호출 실패: {response.status_code}")
            print(f"  응답: {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ 오류 발생: {str(e)}")


def main():
    """메인 테스트 실행"""
    print("="*50)
    print("eHR API 엔드포인트 테스트")
    print(f"서버: {BASE_URL}")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # 로그인
    if not login():
        print("로그인 실패로 테스트를 중단합니다.")
        return
    
    # API 테스트 실행
    test_growth_level_status()
    test_certification_check()
    test_training_recommendations()
    test_progress_api()
    
    print("\n" + "="*50)
    print("테스트 완료!")
    print("="*50)


if __name__ == "__main__":
    print("Django 서버가 실행 중인지 확인하세요 (python manage.py runserver)")
    print("계속하려면 Enter를 누르세요...")
    input()
    
    main()