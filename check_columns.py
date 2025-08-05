import pandas as pd

df = pd.read_excel('OK_employee_full_data.xlsx')
cols = list(df.columns)

print('모든 컬럼과 인덱스:')
for i, col in enumerate(cols):
    print(f'{i}: {col}')
    
print('\ndummy 컬럼만:')
for i, col in enumerate(cols):
    if 'dummy' in str(col):
        print(f'{i}: {col}')
        print(f'  샘플 데이터: {df[col].iloc[0]}')