"""
최소한의 데이터로 테스트 Excel 생성
"""

import pandas as pd

# 최소 데이터 (10명만)
data = {
    '이름': ['김민준', '이서연', '박도윤', '최서윤', '정시우', '강지우', '조하준', '윤서현', '장지호', '임민서'],
    '이메일': [f'test{i:03d}@okfg.co.kr' for i in range(1, 11)],
    '부서': ['IT', 'HR', 'FINANCE', 'IT', 'HR', 'FINANCE', 'IT', 'HR', 'FINANCE', 'IT'],
    '직급': ['STAFF', 'STAFF', 'ASSISTANT_MANAGER', 'STAFF', 'MANAGER', 'STAFF', 'STAFF', 'ASSISTANT_MANAGER', 'STAFF', 'STAFF'],
    '입사일': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01', 
               '2023-06-01', '2023-07-01', '2023-08-01', '2023-09-01', '2023-10-01'],
    '전화번호': ['010-1111-1111', '010-2222-2222', '010-3333-3333', '010-4444-4444', '010-5555-5555',
                 '010-6666-6666', '010-7777-7777', '010-8888-8888', '010-9999-9999', '010-0000-0000']
}

df = pd.DataFrame(data)

# 파일 저장
output_file = 'test_minimal.xlsx'
df.to_excel(output_file, index=False)

print(f"테스트 파일 생성 완료: {output_file}")
print(f"레코드 수: {len(df)}")
print("\n데이터 미리보기:")
print(df)