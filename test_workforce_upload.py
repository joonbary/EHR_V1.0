"""
인력현황 업로드 테스트 스크립트
"""
import requests
import os

# 파일 경로
file_path = 'emp_upload.xlsx'

# API 엔드포인트
url = 'http://localhost:8000/employees/hr/api/workforce/upload/snapshot/'

# 파일 업로드
if os.path.exists(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': ('emp_upload.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        
        try:
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("\n✅ 업로드 성공!")
                
                # 요약 정보 확인
                summary_url = 'http://localhost:8000/employees/hr/api/workforce/summary/'
                summary_response = requests.get(summary_url)
                if summary_response.status_code == 200:
                    print("\n📊 요약 정보:")
                    print(summary_response.json())
            else:
                print("\n❌ 업로드 실패!")
                
        except Exception as e:
            print(f"\n오류 발생: {e}")
else:
    print(f"파일을 찾을 수 없습니다: {file_path}")