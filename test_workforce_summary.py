"""
인력현황 요약 정보 확인
"""
import requests
import json

# 요약 정보 API
summary_url = 'http://localhost:8000/employees/hr/api/workforce/summary/'
response = requests.get(summary_url)

if response.status_code == 200:
    data = response.json()
    print("=== 인력현황 요약 ===")
    print(f"기준일자: {data.get('snapshot_date', '-')}")
    print(f"전체 인원: {data.get('total_headcount', 0):,}명")
    print(f"주간 입사: {data.get('join_count', 0)}명")
    print(f"주간 퇴사: {data.get('leave_count', 0)}명")
    print(f"증감률: {data.get('change_rate', 0)}%")
    
    # 추이 데이터
    trend_url = 'http://localhost:8000/employees/hr/api/workforce/trend/'
    trend_response = requests.get(trend_url)
    if trend_response.status_code == 200:
        trend_data = trend_response.json()
        print(f"\n=== 추이 데이터 ===")
        print(f"데이터 포인트 수: {len(trend_data.get('labels', []))}")
        
    # 증감 분석
    changes_url = 'http://localhost:8000/employees/hr/api/workforce/changes/'
    changes_response = requests.get(changes_url)
    if changes_response.status_code == 200:
        changes_data = changes_response.json()
        print(f"\n=== 증감 분석 ===")
        print(f"분석 데이터 수: {len(changes_data.get('changes', []))}")
else:
    print(f"요청 실패: {response.status_code}")
    print(response.text)