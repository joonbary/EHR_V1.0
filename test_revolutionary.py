"""
Revolutionary 템플릿 적용 테스트 스크립트
"""
# -*- coding: utf-8 -*-
import requests
from django.test import Client
import time
import sys
import io

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_pages():
    """각 페이지 접속 테스트"""
    
    base_url = "http://localhost:8000"
    test_urls = [
        "/employees/org-chart/",
        "/organization/chart/",
        "/evaluations/contribution/",
    ]
    
    print("="*50)
    print("Revolutionary 템플릿 테스트 시작")
    print("="*50)
    
    for url in test_urls:
        full_url = base_url + url
        print(f"\n테스트 중: {full_url}")
        
        try:
            response = requests.get(full_url, timeout=5)
            
            # 상태 코드 확인
            if response.status_code == 200:
                print(f"[OK] 접속 성공 (200 OK)")
                
                # Revolutionary 템플릿 키워드 확인
                content = response.text.lower()
                checks = {
                    "base_revolutionary.html": "Revolutionary 템플릿 상속",
                    "#00d4ff": "시안색 강조",
                    "rgba(26, 31, 46": "다크 배경 그라데이션",
                    "linear-gradient": "그라데이션 효과"
                }
                
                for keyword, description in checks.items():
                    if keyword.lower() in content:
                        print(f"  [OK] {description} 확인")
                    else:
                        print(f"  [X] {description} 미확인")
                        
            elif response.status_code == 302:
                print(f"[!] 리다이렉션 (302) - 로그인 필요할 수 있음")
            else:
                print(f"[X] 접속 실패 (상태 코드: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"[X] 서버 연결 실패 - Django 서버가 실행 중인지 확인하세요")
        except requests.exceptions.Timeout:
            print(f"[!] 응답 시간 초과")
        except Exception as e:
            print(f"[X] 오류 발생: {str(e)}")
    
    print("\n" + "="*50)
    print("테스트 완료!")
    print("="*50)
    print("\n[TIP] 브라우저에서 직접 확인하려면 시크릿 모드를 사용하세요")
    print("   - Chrome: Ctrl+Shift+N (Windows) / Cmd+Shift+N (Mac)")
    print("   - Firefox: Ctrl+Shift+P (Windows) / Cmd+Shift+P (Mac)")

if __name__ == "__main__":
    test_pages()