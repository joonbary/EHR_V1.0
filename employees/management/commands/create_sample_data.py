from django.core.management.base import BaseCommand
from employees.models import Employee
from datetime import date, datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Production용 샘플 직원 데이터 생성'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='생성할 직원 수 (기본값: 50)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='기존 데이터가 있어도 강제로 생성',
        )

    def handle(self, *args, **options):
        count = options['count']
        force = options['force']
        
        # 현재 직원 수 확인
        current_count = Employee.objects.count()
        self.stdout.write(f"현재 직원 수: {current_count}")
        
        if current_count > 0 and not force:
            self.stdout.write(
                self.style.WARNING("이미 직원 데이터가 존재합니다. --force 옵션을 사용하여 강제 생성할 수 있습니다.")
            )
            return
        
        # 샘플 데이터 정의
        companies = ['OK금융지주', 'OK저축은행', 'OK캐피탈', 'OK신용정보', 'OK데이터시스템']
        departments = ['경영지원부', 'IT개발부', '영업부', '기획부', '인사부', '재무부', '리스크관리부', '디지털본부', '고객지원부']
        positions = ['사원', '대리', '과장', '차장', '부장']
        
        created_count = 0
        errors = 0
        
        self.stdout.write(f"{count}명의 샘플 직원 생성을 시작합니다...")
        
        for i in range(count):
            try:
                # 랜덤 데이터 생성
                company = random.choice(companies)
                department = f"{company} {random.choice(departments)}"
                position = random.choice(positions)
                
                # 입사일: 2015-2024년 사이 랜덤
                start_date = date(2015, 1, 1)
                end_date = date(2024, 12, 31)
                random_days = random.randint(0, (end_date - start_date).days)
                hire_date = start_date + timedelta(days=random_days)
                
                # 최근 30일 입사자도 몇 명 포함
                if i < 3:  # 처음 3명은 최근 입사자로
                    hire_date = date.today() - timedelta(days=random.randint(1, 29))
                
                employee = Employee.objects.create(
                    name=f"직원{i+1:03d}",
                    email=f"employee{i+1:03d}@{company.lower().replace(' ', '').replace('금융지주', 'group')}.co.kr",
                    company=company,
                    department=department,
                    final_department=random.choice(departments),
                    position=position,
                    current_position=position,
                    new_position=position,
                    hire_date=hire_date,
                    phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    employment_status='재직',
                    job_group=random.choice(['PL', 'Non-PL']),
                    job_type=random.choice(['IT개발', '경영관리', '영업', '기획', '인사']),
                    age=random.randint(25, 55),
                    gender=random.choice(['M', 'F'])
                )
                created_count += 1
                
                if created_count % 10 == 0:
                    self.stdout.write(f"진행 중... {created_count}명 생성")
                    
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f"직원 {i+1} 생성 실패: {e}")
                )
                continue
        
        # 결과 출력
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("샘플 데이터 생성 완료"))
        self.stdout.write("="*50)
        self.stdout.write(f"생성된 직원 수: {created_count}명")
        self.stdout.write(f"실패 건수: {errors}명")
        self.stdout.write(f"총 직원 수: {Employee.objects.count()}명")
        
        # 통계 정보
        total_employees = Employee.objects.count()
        unique_departments = Employee.objects.values_list('department', flat=True).distinct().count()
        active_employees = Employee.objects.filter(employment_status='재직').count()
        
        # 최근 30일 입사자
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_hires = Employee.objects.filter(hire_date__gte=thirty_days_ago).count()
        
        self.stdout.write(f"부서 수: {unique_departments}개")
        self.stdout.write(f"재직자 수: {active_employees}명")
        self.stdout.write(f"최근 30일 입사자: {recent_hires}명")
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"\n샘플 데이터 생성이 완료되었습니다! 이제 직원 목록 페이지를 새로고침해보세요.")
            )