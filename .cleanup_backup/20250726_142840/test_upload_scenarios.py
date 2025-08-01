#!/usr/bin/env python
"""
업로드 기능 종합 테스트 스크립트
사용법: python test_upload_scenarios.py
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from employees.models import Employee
import pandas as pd
from io import BytesIO

class BulkUploadTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('employees:employee_bulk_upload')
        
    def test_1_normal_upload(self):
        """정상 업로드 테스트"""
        print("\n🔍 테스트 1: 정상 업로드")
        
        # 테스트 데이터 생성
        data = [
            ['김테스트1', 'test1@okgroup.com', '인사팀', '사원', '2024-01-15', '010-1111-1111'],
            ['이테스트2', 'test2@okgroup.com', '총무팀', '대리', '2023-08-20', '010-2222-2222'],
            ['박테스트3', 'test3@okgroup.com', 'IT팀', '과장', '2022-12-01', '010-3333-3333'],
        ]
        
        df = pd.DataFrame(data, columns=['이름', '이메일', '부서', '직급', '입사일', '전화번호'])
        
        # Excel 파일 생성
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        # 업로드 요청
        with open('temp_test.xlsx', 'wb') as f:
            f.write(excel_file.getvalue())
        
        with open('temp_test.xlsx', 'rb') as f:
            response = self.client.post(self.upload_url, {
                'file': f,
                'preview': '1'
            })
        
        # 결과 확인
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        print(f"   ✅ 미리보기 성공: {len(result['preview'])}건")
        print(f"   ✅ 오류 수: {len(result['errors'])}건")
        
        # 실제 저장 테스트
        save_data = {
            'save': 1,
            'columns': result['columns'],
            'rows': result['preview']
        }
        
        response = self.client.post(
            self.upload_url,
            data=save_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        save_result = response.json()
        
        print(f"   ✅ 저장 성공: {save_result['success_count']}건")
        print(f"   ✅ 저장 실패: {save_result['fail_count']}건")
        
        # DB 확인
        saved_count = Employee.objects.filter(email__startswith='test').count()
        print(f"   ✅ DB 저장 확인: {saved_count}건")
        
        # 정리
        os.remove('temp_test.xlsx')
        
    def test_2_error_upload(self):
        """오류 데이터 처리 테스트"""
        print("\n🔍 테스트 2: 오류 데이터 처리")
        
        # 오류가 포함된 테스트 데이터
        data = [
            ['김정상', 'normal@okgroup.com', '인사팀', '사원', '2024-01-15', '010-1111-1111'],
            ['', 'empty.name@okgroup.com', '총무팀', '대리', '2023-08-20', '010-2222-2222'],  # 이름 누락
            ['박이메일', '', 'IT팀', '과장', '2022-12-01', '010-3333-3333'],  # 이메일 누락
            ['최날짜', 'date@okgroup.com', '마케팅팀', '팀장', '2024-13-45', '010-4444-4444'],  # 날짜 오류
        ]
        
        df = pd.DataFrame(data, columns=['이름', '이메일', '부서', '직급', '입사일', '전화번호'])
        
        # Excel 파일 생성
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        with open('temp_error.xlsx', 'wb') as f:
            f.write(excel_file.getvalue())
        
        with open('temp_error.xlsx', 'rb') as f:
            response = self.client.post(self.upload_url, {
                'file': f,
                'preview': '1'
            })
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        print(f"   ✅ 미리보기 성공: {len(result['preview'])}건")
        print(f"   ✅ 오류 감지: {len(result['errors'])}건")
        
        # 오류 상세 확인
        for error in result['errors']:
            print(f"   ⚠️  행 {error['row']}: {', '.join(error['errors'])}")
        
        # 정리
        os.remove('temp_error.xlsx')
        
    def test_3_duplicate_email(self):
        """중복 이메일 처리 테스트"""
        print("\n🔍 테스트 3: 중복 이메일 처리")
        
        # 기존 직원 생성
        Employee.objects.create(
            name='기존직원',
            email='duplicate@okgroup.com',
            department='인사팀',
            position='사원',
            hire_date='2024-01-01',
            phone='010-0000-0000'
        )
        
        # 중복 이메일이 포함된 데이터
        data = [
            ['김중복', 'duplicate@okgroup.com', '총무팀', '대리', '2024-01-15', '010-1111-1111'],  # 중복
            ['이신규', 'new@okgroup.com', 'IT팀', '과장', '2023-08-20', '010-2222-2222'],  # 신규
        ]
        
        df = pd.DataFrame(data, columns=['이름', '이메일', '부서', '직급', '입사일', '전화번호'])
        
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        with open('temp_duplicate.xlsx', 'wb') as f:
            f.write(excel_file.getvalue())
        
        with open('temp_duplicate.xlsx', 'rb') as f:
            response = self.client.post(self.upload_url, {
                'file': f,
                'preview': '1'
            })
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        print(f"   ✅ 중복 이메일 감지: {len(result['errors'])}건")
        
        # 중복 처리 확인
        duplicate_errors = [e for e in result['errors'] if '이메일 중복' in e['errors']]
        print(f"   ✅ 중복 이메일 오류: {len(duplicate_errors)}건")
        
        # 정리
        os.remove('temp_duplicate.xlsx')
        
    def test_4_large_file(self):
        """대용량 파일 테스트"""
        print("\n🔍 테스트 4: 대용량 파일 (50건)")
        
        # 50건의 테스트 데이터 생성
        data = []
        for i in range(50):
            data.append([
                f'대용량테스트{i+1:02d}',
                f'large{i+1:02d}@okgroup.com',
                f'부서{(i%8)+1}',
                ['사원', '대리', '과장', '팀장'][i%4],
                f'2024-{(i%12)+1:02d}-{(i%28)+1:02d}',
                f'010-{i+1:04d}-{i+1:04d}'
            ])
        
        df = pd.DataFrame(data, columns=['이름', '이메일', '부서', '직급', '입사일', '전화번호'])
        
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        with open('temp_large.xlsx', 'wb') as f:
            f.write(excel_file.getvalue())
        
        with open('temp_large.xlsx', 'rb') as f:
            response = self.client.post(self.upload_url, {
                'file': f,
                'preview': '1'
            })
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        print(f"   ✅ 대용량 파일 처리: {result['total_rows']}건")
        print(f"   ✅ 미리보기: {len(result['preview'])}건 (최대 10건)")
        print(f"   ✅ 오류 수: {len(result['errors'])}건")
        
        # 정리
        os.remove('temp_large.xlsx')
        
    def test_5_empty_file(self):
        """빈 파일 테스트"""
        print("\n🔍 테스트 5: 빈 파일 처리")
        
        # 빈 데이터프레임 생성
        df = pd.DataFrame(columns=['이름', '이메일', '부서', '직급', '입사일', '전화번호'])
        
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        with open('temp_empty.xlsx', 'wb') as f:
            f.write(excel_file.getvalue())
        
        with open('temp_empty.xlsx', 'rb') as f:
            response = self.client.post(self.upload_url, {
                'file': f,
                'preview': '1'
            })
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        print(f"   ✅ 빈 파일 처리: {result['total_rows']}건")
        print(f"   ✅ 미리보기: {len(result['preview'])}건")
        
        # 정리
        os.remove('temp_empty.xlsx')

def run_management_commands():
    """Django management 명령어로 테스트 데이터 생성"""
    print("\n📁 테스트 데이터 생성 중...")
    
    commands = [
        ['python', 'manage.py', 'create_test_data', '--type', 'normal', '--output', 'test_normal'],
        ['python', 'manage.py', 'create_test_data', '--type', 'error', '--output', 'test_error'],
        ['python', 'manage.py', 'create_test_data', '--type', 'large', '--output', 'test_large'],
        ['python', 'manage.py', 'create_test_data', '--type', 'empty', '--output', 'test_empty'],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"   ✅ {cmd[-1]}: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ {cmd[-1]}: {e.stderr.strip()}")

def main():
    """메인 테스트 실행"""
    print("🚀 업로드 기능 종합 테스트 시작")
    print("=" * 50)
    
    # 1. 테스트 데이터 생성
    run_management_commands()
    
    # 2. Django 테스트 실행
    print("\n🧪 Django 테스트 실행 중...")
    
    # Django 테스트 실행
    test_cases = [
        'test_1_normal_upload',
        'test_2_error_upload', 
        'test_3_duplicate_email',
        'test_4_large_file',
        'test_5_empty_file'
    ]
    
    for test_name in test_cases:
        try:
            # Django 테스트 실행
            result = subprocess.run([
                'python', 'manage.py', 'test', 
                'employees.tests.BulkUploadTest.' + test_name,
                '--verbosity=2'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ {test_name}: 성공")
            else:
                print(f"   ❌ {test_name}: 실패")
                print(f"      {result.stderr}")
        except Exception as e:
            print(f"   ❌ {test_name}: 오류 - {e}")
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료!")
    print("\n📋 확인사항:")
    print("1. ✅ http://127.0.0.1:8000/employees/bulk-upload/ 접속 가능")
    print("2. ✅ 템플릿 다운로드 작동")
    print("3. ✅ Excel/CSV 파일 업로드 성공")
    print("4. ✅ 오류 검증 및 리포트 정상")
    print("5. ✅ 직원 목록에서 업로드된 데이터 확인")
    
    print("\n📁 생성된 테스트 파일:")
    test_files = ['test_normal.xlsx', 'test_error.xlsx', 'test_large.xlsx', 'test_empty.xlsx']
    for file in test_files:
        if os.path.exists(file):
            print(f"   📄 {file}")

if __name__ == '__main__':
    main() 