from django.core.management.base import BaseCommand
from django.utils import timezone
import pandas as pd
from io import BytesIO
import os
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = '업로드 기능 테스트를 위한 테스트 데이터 생성'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['normal', 'error', 'large', 'empty', 'sample'],
            default='normal',
            help='생성할 테스트 데이터 타입'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='test_data',
            help='출력 파일명 (확장자 제외)'
        )

    def handle(self, *args, **options):
        data_type = options['type']
        output_name = options['output']
        
        if data_type == 'normal':
            self.create_normal_data(output_name)
        elif data_type == 'error':
            self.create_error_data(output_name)
        elif data_type == 'large':
            self.create_large_data(output_name)
        elif data_type == 'empty':
            self.create_empty_data(output_name)
        elif data_type == 'sample':
            self.create_sample_upload_data(output_name)
        
        self.stdout.write(
            self.style.SUCCESS(f'{data_type} 테스트 데이터가 생성되었습니다: {output_name}.xlsx')
        )

    def create_normal_data(self, output_name):
        """정상 데이터 5명 생성"""
        headers = ['이름', '이메일', '부서', '직급', '입사일', '전화번호']
        data = [
            ['김철수', 'kim.cs@okgroup.com', '인사팀', '사원', '2024-01-15', '010-1234-5678'],
            ['이영희', 'lee.yh@okgroup.com', '총무팀', '대리', '2023-08-20', '010-2345-6789'],
            ['박민수', 'park.ms@okgroup.com', 'IT팀', '과장', '2022-12-01', '010-3456-7890'],
            ['최지영', 'choi.jy@okgroup.com', '마케팅팀', '팀장', '2021-06-15', '010-4567-8901'],
            ['정현우', 'jung.hw@okgroup.com', '영업팀', '부장', '2020-03-10', '010-5678-9012'],
        ]
        
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(f'{output_name}.xlsx', index=False)

    def create_error_data(self, output_name):
        """오류 데이터 7명 생성 (중복, 필수값 누락, 날짜 오류 등)"""
        headers = ['이름', '이메일', '부서', '직급', '입사일', '전화번호']
        data = [
            # 정상 데이터 2명
            ['김정상', 'kim.normal@okgroup.com', '인사팀', '사원', '2024-01-15', '010-1111-1111'],
            ['이정상', 'lee.normal@okgroup.com', '총무팀', '대리', '2023-08-20', '010-2222-2222'],
            
            # 오류 데이터 5명
            ['', 'empty.name@okgroup.com', '인사팀', '사원', '2024-01-15', '010-3333-3333'],  # 이름 누락
            ['박이메일', '', 'IT팀', '과장', '2022-12-01', '010-4444-4444'],  # 이메일 누락
            ['최부서', 'choi.dept@okgroup.com', '', '팀장', '2021-06-15', '010-5555-5555'],  # 부서 누락
            ['정날짜', 'jung.date@okgroup.com', '영업팀', '부장', '2024-13-45', '010-6666-6666'],  # 날짜 형식 오류
            ['김중복', 'kim.normal@okgroup.com', '인사팀', '사원', '2024-01-15', '010-7777-7777'],  # 중복 이메일
        ]
        
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(f'{output_name}.xlsx', index=False)

    def create_large_data(self, output_name):
        """대용량 데이터 120명 생성"""
        headers = ['이름', '이메일', '부서', '직급', '입사일', '전화번호']
        
        departments = ['인사팀', '총무팀', 'IT팀', '마케팅팀', '영업팀', '재무팀', '기획팀', '개발팀']
        positions = ['사원', '대리', '과장', '팀장', '부장', '이사']
        
        data = []
        for i in range(120):
            name = f'테스트{i+1:03d}'
            email = f'test{i+1:03d}@okgroup.com'
            dept = random.choice(departments)
            pos = random.choice(positions)
            
            # 랜덤 입사일 (2020년~2024년)
            start_date = datetime(2020, 1, 1)
            end_date = datetime(2024, 12, 31)
            days_between = (end_date - start_date).days
            random_days = random.randint(0, days_between)
            hire_date = start_date + timedelta(days=random_days)
            
            phone = f'010-{random.randint(1000,9999):04d}-{random.randint(1000,9999):04d}'
            
            data.append([name, email, dept, pos, hire_date.strftime('%Y-%m-%d'), phone])
        
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(f'{output_name}.xlsx', index=False)

    def create_empty_data(self, output_name):
        """빈 파일 생성 (헤더만)"""
        headers = ['이름', '이메일', '부서', '직급', '입사일', '전화번호']
        df = pd.DataFrame(columns=headers)
        df.to_excel(f'{output_name}.xlsx', index=False) 

    def create_sample_upload_data(self, output_name):
        """실제 업로드 테스트용 10명짜리 정상 더미 데이터"""
        headers = ['이름', '이메일', '부서', '직급', '입사일', '전화번호']
        data = [
            ['홍길동', 'hong1@okgroup.com', '인사팀', '사원', '2022-01-10', '010-1000-1000'],
            ['김영희', 'kim2@okgroup.com', '총무팀', '대리', '2021-03-15', '010-2000-2000'],
            ['박철수', 'park3@okgroup.com', 'IT팀', '과장', '2020-05-20', '010-3000-3000'],
            ['이민수', 'lee4@okgroup.com', '마케팅팀', '팀장', '2019-07-25', '010-4000-4000'],
            ['최지우', 'choi5@okgroup.com', '영업팀', '부장', '2018-09-30', '010-5000-5000'],
            ['정현우', 'jung6@okgroup.com', '재무팀', '이사', '2017-11-05', '010-6000-6000'],
            ['오세훈', 'oh7@okgroup.com', '기획팀', '사원', '2023-02-14', '010-7000-7000'],
            ['유재석', 'yoo8@okgroup.com', '개발팀', '대리', '2022-04-18', '010-8000-8000'],
            ['강호동', 'kang9@okgroup.com', '인사팀', '과장', '2021-06-22', '010-9000-9000'],
            ['신동엽', 'shin10@okgroup.com', '총무팀', '팀장', '2020-08-26', '010-1010-1010'],
        ]
        import pandas as pd
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(f'{output_name}.xlsx', index=False) 