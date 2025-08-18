#!/usr/bin/env python
"""
엑셀 파일의 이메일을 새로운 타임스탬프로 재생성
"""
import pandas as pd
from datetime import datetime

def regenerate_emails():
    """이메일 재생성"""
    
    # 새로운 타임스탬프 (MMDDHHMM 형식)
    timestamp = datetime.now().strftime('%m%d%H%M')  # 예: 08051030
    
    files = ['OK_employee_new_part1.xlsx', 'OK_employee_new_part2.xlsx']
    
    for file_path in files:
        print(f"\n처리 중: {file_path}")
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file_path)
        print(f"총 {len(df)}개 행")
        
        # 새로운 이메일 생성
        for idx, row in df.iterrows():
            company = str(row.get('회사', 'OKFG')).strip().lower()
            
            # 회사별 도메인 매핑
            domain_map = {
                'ok': 'okfg.co.kr',
                'oci': 'okci.co.kr',
                'oc': 'okcapital.co.kr',
                'ofi': 'okfi.co.kr',
                'okds': 'okds.co.kr',
                'okh': 'okh.co.kr',
                'on': 'on.co.kr',
                'okip': 'okip.co.kr',
                'ot': 'ot.co.kr',
                'okv': 'okv.co.kr',
                'ex': 'okfg.co.kr'
            }
            
            domain = domain_map.get(company, 'okfg.co.kr')
            
            # 새로운 이메일 생성 (emp + 타임스탬프 + 번호)
            new_email = f"emp{timestamp}{idx+1:04d}@{domain}"
            df.at[idx, '이메일'] = new_email
            df.at[idx, 'dummy_email'] = new_email
        
        # 새 파일로 저장
        new_file_path = file_path.replace('.xlsx', f'_{timestamp}.xlsx')
        df.to_excel(new_file_path, index=False)
        print(f"저장 완료: {new_file_path}")
        print(f"첫 번째 이메일: {df.iloc[0]['이메일']}")
        print(f"마지막 이메일: {df.iloc[-1]['이메일']}")

if __name__ == "__main__":
    regenerate_emails()