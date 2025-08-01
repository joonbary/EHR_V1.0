"""
외주인력 파싱 테스트
"""
from employees.services.excel_parser import HRExcelAutoParser

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

try:
    parser = HRExcelAutoParser()
    results = parser.parse_outsourced_staff(file_path)
    
    print(f"총 {len(results)}개 항목 파싱됨\n")
    
    # 회사별 집계
    companies = {}
    resident_count = 0
    non_resident_count = 0
    
    for staff in results:
        company = staff['company_name']
        if company not in companies:
            companies[company] = {'상주': 0, '비상주': 0}
        
        if staff['is_resident']:
            companies[company]['상주'] += staff['headcount']
            resident_count += staff['headcount']
        else:
            companies[company]['비상주'] += staff['headcount']
            non_resident_count += staff['headcount']
    
    print("=== 회사별 집계 ===")
    for company, counts in companies.items():
        print(f"{company}: 상주 {counts['상주']}명, 비상주 {counts['비상주']}명")
    
    print(f"\n전체: 상주 {resident_count}명, 비상주 {non_resident_count}명, 총 {resident_count + non_resident_count}명")
    
    print("\n=== 처음 5개 항목 ===")
    for i, staff in enumerate(results[:5]):
        print(f"\n{i+1}. {staff['company_name']} - {staff['project_name']}")
        print(f"   상주여부: {'상주' if staff['is_resident'] else '비상주'}")
        print(f"   인원: {staff['headcount']}명")
        print(f"   기준일: {staff['report_date']}")
    
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()