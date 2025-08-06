from django.core.management.base import BaseCommand
from django.db import transaction
from job_profiles.models import JobRole, JobProfile
from employees.models import Employee


class Command(BaseCommand):
    help = 'Create minimal job profiles data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample job profiles...')
        
        try:
            with transaction.atomic():
                # 시스템 사용자 가져오기 또는 생성
                system_user = Employee.objects.filter(email='system@okfg.com').first()
                if not system_user:
                    system_user = Employee.objects.first()  # 첫 번째 직원 사용
                
                if not system_user:
                    self.stdout.write(self.style.ERROR('No employees found. Please create an employee first.'))
                    return
                
                # 간단한 직무 데이터 (JobRole만 생성)
                sample_jobs = [
                    {'name': '시스템기획', 'code': 'SYS_PLAN', 'description': 'IT 시스템 기획 업무'},
                    {'name': '시스템개발', 'code': 'SYS_DEV', 'description': 'IT 시스템 개발 업무'},
                    {'name': 'HRM', 'code': 'HRM', 'description': '인사 관리 업무'},
                    {'name': '여신영업', 'code': 'LOAN_SALES', 'description': '기업 여신 영업 업무'},
                ]
                
                created_count = 0
                
                for job_data in sample_jobs:
                    # JobRole 생성 (JobCategory, JobType 없이)
                    job_role, created = JobRole.objects.get_or_create(
                        name=job_data['name'],
                        defaults={
                            'code': job_data['code'],
                            'description': job_data['description'],
                            'is_active': True,
                            'job_type': None  # JobType 없이 생성
                        }
                    )
                    
                    if created:
                        # JobProfile 생성
                        JobProfile.objects.create(
                            job_role=job_role,
                            role_responsibility=f"{job_data['name']} 관련 주요 업무 수행\n• 업무 기획 및 실행\n• 성과 관리 및 개선",
                            qualification=f"{job_data['name']} 관련 경험 및 역량\n• 관련 분야 전문성\n• 커뮤니케이션 능력",
                            basic_skills=[f"{job_data['name']} 기본 역량", "문제 해결 능력", "협업 능력"],
                            applied_skills=[f"{job_data['name']} 전문 역량", "프로젝트 관리", "데이터 분석"],
                            related_certifications=["관련 자격증"],
                            growth_path=f"{job_data['name']} → 시니어 {job_data['name']} → 팀장 → 부서장",
                            created_by=system_user,
                            updated_by=system_user
                        )
                        created_count += 1
                        self.stdout.write(f"Created: {job_data['name']}")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nSuccessfully created {created_count} job profiles!\n'
                        f'Total JobRoles: {JobRole.objects.count()}\n'
                        f'Total JobProfiles: {JobProfile.objects.count()}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise