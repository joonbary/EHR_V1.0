from django.test import TestCase, Client
from django.urls import reverse
from .models import Employee
import pandas as pd
from io import BytesIO
import os

class BulkUploadTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('employees:employee_bulk_upload')
        
    def test_1_normal_upload(self):
        """정상 업로드 테스트"""
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
        
        # DB 확인
        saved_count = Employee.objects.filter(email__startswith='test').count()
        self.assertEqual(saved_count, 3)
        
        # 정리
        os.remove('temp_test.xlsx')
        
    def test_2_error_upload(self):
        """오류 데이터 처리 테스트"""
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
        
        # 디버깅: 실제 데이터와 결과 확인
        print(f"\n🔍 디버깅 정보:")
        print(f"   전송된 데이터: {data}")
        print(f"   미리보기: {result['preview']}")
        print(f"   감지된 오류: {result['errors']}")
        print(f"   총 행 수: {result['total_rows']}")
        
        # 오류가 3건 감지되어야 함 (이름 누락, 이메일 누락, 날짜 형식 오류)
        self.assertEqual(len(result['errors']), 3)
        
        # 오류 상세 확인
        error_types = []
        for error in result['errors']:
            error_types.extend(error['errors'])
        
        # 각 오류 타입 확인
        self.assertTrue(any('이름 필수' in error for error in error_types))
        self.assertTrue(any('이메일 필수' in error for error in error_types))
        self.assertTrue(any('입사일 형식 오류' in error for error in error_types))
        
        # 정리
        os.remove('temp_error.xlsx')
        
    def test_3_duplicate_email(self):
        """중복 이메일 처리 테스트"""
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
        
        # 중복 이메일 오류가 1건 감지되어야 함
        duplicate_errors = [e for e in result['errors'] if '이메일 중복' in e['errors']]
        self.assertEqual(len(duplicate_errors), 1)
        
        # 정리
        os.remove('temp_duplicate.xlsx')
        
    def test_4_large_file(self):
        """대용량 파일 테스트"""
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
        
        # 총 50건이 처리되어야 함
        self.assertEqual(result['total_rows'], 50)
        # 미리보기는 최대 10건
        self.assertLessEqual(len(result['preview']), 10)
        
        # 정리
        os.remove('temp_large.xlsx')
        
    def test_5_empty_file(self):
        """빈 파일 테스트"""
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
        
        # 빈 파일이므로 0건
        self.assertEqual(result['total_rows'], 0)
        
        # 정리
        os.remove('temp_empty.xlsx')
