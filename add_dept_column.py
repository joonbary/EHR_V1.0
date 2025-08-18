"""
템플릿 형식 Excel에 '부서' 컬럼 추가
"""

import pandas as pd

# 기존 파일 읽기
df = pd.read_excel('OK_employee_template_format.xlsx')

# '부서' 컬럼을 '최종소속' 값으로 추가
df.insert(3, '부서', df['최종소속'])  # '전화번호' 다음에 삽입

# 파일 저장
output_file = 'OK_employee_with_dept.xlsx'
df.to_excel(output_file, index=False)

print(f"파일 생성 완료: {output_file}")
print(f"컬럼: {list(df.columns)}")
print(f"\n처음 3개 레코드:")
print(df[['이름', '이메일', '부서', '최종소속', '직급']].head(3))