"""
Production 환경에 Excel 데이터 업로드
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from employees.management.commands.load_okfg_excel import Command
import sys

if __name__ == '__main__':
    # Excel 파일 경로
    excel_path = 'OK_employee_template_format.xlsx'
    
    print(f"Excel 파일 업로드 시작: {excel_path}")
    
    # Command 인스턴스 생성
    cmd = Command()
    
    try:
        # handle 메서드 직접 호출
        cmd.handle(excel_path=excel_path)
        print("업로드 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)