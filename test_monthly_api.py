"""
월간 인력현황 API 테스트
"""
import requests

# API 호출
url = 'http://localhost:8000/employees/hr/api/monthly-workforce/'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("=== API Response ===")
    print(f"Title: {data.get('title', 'N/A')}")
    print(f"Companies: {len(data.get('companies', []))}")
    
    if 'summary' in data:
        print(f"\n=== Summary ===")
        print(f"Total Current: {data['summary']['total_current']}")
        print(f"Total Previous: {data['summary']['total_previous']}")
        print(f"Total Change: {data['summary']['total_change']}")
    
    # 첫 번째 회사 데이터 샘플
    if data.get('companies'):
        first_company = data['companies'][0]
        print(f"\n=== First Company: {first_company['name']} ===")
        print(f"Positions: {len(first_company['positions'])}")
        if first_company['positions']:
            print("Sample position:", first_company['positions'][0])
else:
    print(f"Error: {response.status_code}")
    print(response.text)