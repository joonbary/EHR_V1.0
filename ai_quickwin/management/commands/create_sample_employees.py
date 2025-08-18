"""
샘플 직원 데이터 생성 커맨드
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random

from employees.models import Employee


class Command(BaseCommand):
    help = '샘플 직원 데이터 생성'

    def handle(self, *args, **options):
        self.stdout.write('샘플 직원 데이터 생성 시작...')
        
        departments = ['개발팀', '마케팅팀', '영업팀', '인사팀', '재무팀', '기획팀']
        positions = ['사원', '주임', '대리', '과장', '차장', '부장']
        
        employees_data = [
            ('김철수', '개발팀', '과장', '남', 'kim@company.com', '010-1234-5678'),
            ('이영희', '마케팅팀', '대리', '여', 'lee@company.com', '010-2345-6789'),
            ('박민수', '개발팀', '부장', '남', 'park@company.com', '010-3456-7890'),
            ('최지영', '인사팀', '차장', '여', 'choi@company.com', '010-4567-8901'),
            ('정대호', '영업팀', '과장', '남', 'jung@company.com', '010-5678-9012'),
            ('강서연', '재무팀', '대리', '여', 'kang@company.com', '010-6789-0123'),
            ('조현우', '기획팀', '차장', '남', 'cho@company.com', '010-7890-1234'),
            ('윤지민', '개발팀', '사원', '여', 'yoon@company.com', '010-8901-2345'),
            ('임재현', '마케팅팀', '주임', '남', 'lim@company.com', '010-9012-3456'),
            ('한소영', '영업팀', '대리', '여', 'han@company.com', '010-0123-4567'),
            ('신동욱', '개발팀', '차장', '남', 'shin@company.com', '010-1111-2222'),
            ('김나래', '인사팀', '과장', '여', 'kim2@company.com', '010-2222-3333'),
            ('이준호', '재무팀', '부장', '남', 'lee2@company.com', '010-3333-4444'),
            ('박서영', '기획팀', '대리', '여', 'park2@company.com', '010-4444-5555'),
            ('최민준', '개발팀', '주임', '남', 'choi2@company.com', '010-5555-6666'),
            ('정유진', '마케팅팀', '사원', '여', 'jung2@company.com', '010-6666-7777'),
            ('강도현', '영업팀', '차장', '남', 'kang2@company.com', '010-7777-8888'),
            ('조예진', '인사팀', '대리', '여', 'cho2@company.com', '010-8888-9999'),
            ('윤성민', '재무팀', '과장', '남', 'yoon2@company.com', '010-9999-0000'),
            ('임하늘', '기획팀', '주임', '여', 'lim2@company.com', '010-1010-1010'),
        ]
        
        created_count = 0
        for name, dept, position, gender, email, phone in employees_data:
            # 입사일 랜덤 생성 (1~10년 전)
            hire_date = date.today() - timedelta(days=random.randint(365, 3650))
            
            # 생년월일 랜덤 생성 (25~55세)
            birth_year = date.today().year - random.randint(25, 55)
            birth_date = date(birth_year, random.randint(1, 12), random.randint(1, 28))
            
            employee, created = Employee.objects.get_or_create(
                name=name,
                defaults={
                    'department': dept,
                    'position': position,
                    'gender': gender,
                    'employment_status': '재직',
                    'email': email,
                    'phone_number': phone,
                    'hire_date': hire_date,
                    'birth_date': birth_date,
                    'address': f'서울시 강남구 테헤란로 {random.randint(1, 500)}',
                    'employee_number': f'EMP{random.randint(10000, 99999)}',
                    'nationality': '한국',
                    'marital_status': random.choice(['미혼', '기혼']),
                    'years_of_experience': (date.today() - hire_date).days // 365,
                    'base_salary': random.randint(3000, 8000) * 10000,
                    'contract_type': '정규직',
                    'bank_name': random.choice(['국민은행', '신한은행', '우리은행', '하나은행']),
                    'account_number': f'{random.randint(100000000000, 999999999999)}',
                    'emergency_contact': phone,
                    'notes': f'{name}님의 인사 정보'
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ {name} ({dept} {position}) 생성 완료')
        
        self.stdout.write(self.style.SUCCESS(f'\n총 {created_count}명의 직원 데이터가 생성되었습니다!'))