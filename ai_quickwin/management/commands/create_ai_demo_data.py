"""
AI Quick Win 데모 데이터 생성 커맨드
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
import random
import uuid

from employees.models import Employee
from ai_coaching.models import (
    CoachingSession, CoachingGoal, CoachingActionItem,
    CoachingTemplate, CoachingMessage
)
from ai_team_optimizer.models import (
    Project, TeamComposition, TeamMember, SkillRequirement,
    TeamTemplate
)


class Command(BaseCommand):
    help = 'AI Quick Win 모듈용 데모 데이터 생성'

    def handle(self, *args, **options):
        self.stdout.write('AI Quick Win 데모 데이터 생성 시작...')
        
        # 직원 데이터 확인
        employees = Employee.objects.filter(employment_status='재직')[:20]
        if not employees:
            self.stdout.write(self.style.WARNING('직원 데이터가 없습니다. 먼저 직원 데이터를 생성해주세요.'))
            return
        
        # 1. 코칭 세션 데이터 생성
        self.create_coaching_data(employees)
        
        # 2. 팀 최적화 데이터 생성
        self.create_team_optimizer_data(employees)
        
        self.stdout.write(self.style.SUCCESS('AI Quick Win 데모 데이터 생성 완료!'))
    
    def create_coaching_data(self, employees):
        """코칭 관련 데모 데이터 생성"""
        self.stdout.write('코칭 데이터 생성 중...')
        
        # 코칭 템플릿 생성
        templates = [
            {
                'name': '신입 직원 온보딩',
                'category': 'ONBOARDING',
                'description': '신입 직원을 위한 체계적인 온보딩 코칭 프로그램',
                'usage_count': 45,
                'success_rate': 0.92,
                'average_satisfaction': 4.6
            },
            {
                'name': '리더십 개발 프로그램',
                'category': 'LEADERSHIP',
                'description': '팀장 및 관리자를 위한 리더십 역량 강화 프로그램',
                'usage_count': 32,
                'success_rate': 0.88,
                'average_satisfaction': 4.5
            },
            {
                'name': '성과 향상 코칭',
                'category': 'PERFORMANCE',
                'description': '개인 성과 목표 달성을 위한 맞춤형 코칭',
                'usage_count': 78,
                'success_rate': 0.85,
                'average_satisfaction': 4.3
            },
            {
                'name': '커리어 개발 상담',
                'category': 'CAREER_DEVELOPMENT',
                'description': '장기적인 커리어 성장을 위한 전략적 코칭',
                'usage_count': 56,
                'success_rate': 0.90,
                'average_satisfaction': 4.7
            }
        ]
        
        for template_data in templates:
            CoachingTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
        
        # 코칭 세션 생성
        session_types = ['PERFORMANCE', 'LEADERSHIP', 'SKILL_DEVELOPMENT', 'CAREER_PATH', 'COMMUNICATION']
        
        for employee in employees[:10]:  # 10명의 직원에 대해 세션 생성
            # 각 직원당 2-3개의 세션 생성
            num_sessions = random.randint(2, 3)
            
            for i in range(num_sessions):
                scheduled_date = timezone.now() - timedelta(days=random.randint(0, 30))
                session_type = random.choice(session_types)
                
                session = CoachingSession.objects.create(
                    employee=employee,
                    session_type=session_type,
                    title=f"{employee.name}님의 {session_type} 코칭",
                    description=f"{session_type} 향상을 위한 1:1 코칭 세션",
                    scheduled_at=scheduled_date,
                    started_at=scheduled_date if i > 0 else None,
                    ended_at=scheduled_date + timedelta(hours=1) if i > 0 else None,
                    status='COMPLETED' if i > 0 else 'SCHEDULED',
                    duration_minutes=60,
                    ai_personality='SUPPORTIVE',
                    satisfaction_score=random.uniform(4.0, 5.0) if i > 0 else 0,
                    coaching_objectives=[
                        '현재 상황 파악',
                        '목표 설정',
                        '실행 계획 수립'
                    ],
                    focus_areas=[
                        '역량 개발',
                        '성과 향상',
                        '커뮤니케이션'
                    ]
                )
                
                # 세션에 메시지 추가
                if session.status == 'COMPLETED':
                    self.create_coaching_messages(session)
                
                # 목표 생성
                goal = CoachingGoal.objects.create(
                    session=session,
                    goal_type=random.choice(['PERFORMANCE', 'SKILL', 'BEHAVIOR', 'CAREER']),
                    title=f"{session_type} 개선 목표",
                    description=f"다음 분기까지 {session_type} 역량 20% 향상",
                    priority=random.choice(['LOW', 'MEDIUM', 'HIGH']),
                    status=random.choice(['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED']),
                    target_date=date.today() + timedelta(days=random.randint(30, 90)),
                    progress_percentage=random.uniform(0, 100),
                    feasibility_score=random.uniform(6.0, 9.0)
                )
                
                # 액션 아이템 생성
                for j in range(random.randint(2, 4)):
                    CoachingActionItem.objects.create(
                        session=session,
                        goal=goal,
                        category=random.choice(['TASK', 'MEETING', 'TRAINING', 'PRACTICE']),
                        title=f"액션 아이템 {j+1}",
                        description=f"{goal.title} 달성을 위한 구체적인 실행 계획",
                        due_date=date.today() + timedelta(days=random.randint(7, 30)),
                        status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED']),
                        estimated_hours=random.uniform(1, 8)
                    )
        
        self.stdout.write(self.style.SUCCESS(f'✓ 코칭 세션 {CoachingSession.objects.count()}개 생성'))
    
    def create_coaching_messages(self, session):
        """코칭 세션 메시지 생성"""
        messages = [
            ('AI_COACH', '안녕하세요! 오늘 코칭 세션을 시작하겠습니다. 최근 어떻게 지내셨나요?'),
            ('EMPLOYEE', '잘 지내고 있습니다. 최근 프로젝트가 많아서 조금 바쁘네요.'),
            ('AI_COACH', '프로젝트가 많으시군요. 현재 가장 우선순위가 높은 업무는 무엇인가요?'),
            ('EMPLOYEE', '신규 시스템 구축 프로젝트가 가장 중요합니다.'),
            ('AI_COACH', '그렇군요. 해당 프로젝트에서 어떤 도전과제를 겪고 계신가요?'),
        ]
        
        for sender, content in messages:
            CoachingMessage.objects.create(
                session=session,
                sender=sender,
                message_type='TEXT',
                content=content,
                sentiment_score=random.uniform(0.6, 0.9),
                confidence_level=random.uniform(0.7, 0.95)
            )
    
    def create_team_optimizer_data(self, employees):
        """팀 최적화 관련 데모 데이터 생성"""
        self.stdout.write('팀 최적화 데이터 생성 중...')
        
        # 팀 템플릿 생성
        team_templates = [
            {
                'name': '애자일 개발팀',
                'template_type': 'DEVELOPMENT',
                'description': '스크럼 기반 애자일 개발팀 구성 템플릿',
                'usage_count': 15,
                'success_rate': 0.87,
                'average_score': 8.2
            },
            {
                'name': '디자인 스프린트팀',
                'template_type': 'DESIGN',
                'description': '5일 디자인 스프린트를 위한 최적 팀 구성',
                'usage_count': 8,
                'success_rate': 0.92,
                'average_score': 8.5
            },
            {
                'name': '마케팅 캠페인팀',
                'template_type': 'MARKETING',
                'description': '통합 마케팅 캠페인 실행팀 템플릿',
                'usage_count': 12,
                'success_rate': 0.85,
                'average_score': 7.9
            }
        ]
        
        for template_data in team_templates:
            TeamTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
        
        # 프로젝트 생성
        projects_data = [
            {
                'name': 'ERP 시스템 업그레이드',
                'description': '기존 ERP 시스템을 클라우드 기반으로 전환',
                'status': 'ACTIVE',
                'priority': 'HIGH',
                'budget': 500000000,
                'estimated_hours': 2400
            },
            {
                'name': '모바일 앱 개발',
                'description': '회사 서비스용 모바일 애플리케이션 개발',
                'status': 'PLANNING',
                'priority': 'MEDIUM',
                'budget': 200000000,
                'estimated_hours': 1600
            },
            {
                'name': 'AI 챗봇 구축',
                'description': '고객 서비스 자동화를 위한 AI 챗봇 시스템 구축',
                'status': 'ACTIVE',
                'priority': 'HIGH',
                'budget': 300000000,
                'estimated_hours': 1200
            },
            {
                'name': '데이터 분석 플랫폼',
                'description': '빅데이터 분석을 위한 통합 플랫폼 구축',
                'status': 'PLANNING',
                'priority': 'MEDIUM',
                'budget': 400000000,
                'estimated_hours': 2000
            },
            {
                'name': '보안 시스템 강화',
                'description': '전사 보안 시스템 업그레이드 및 강화',
                'status': 'COMPLETED',
                'priority': 'CRITICAL',
                'budget': 150000000,
                'estimated_hours': 800
            }
        ]
        
        for project_data in projects_data:
            start_date = date.today() - timedelta(days=random.randint(30, 180))
            end_date = start_date + timedelta(days=random.randint(90, 365))
            
            project = Project.objects.create(
                name=project_data['name'],
                description=project_data['description'],
                status=project_data['status'],
                priority=project_data['priority'],
                start_date=start_date,
                end_date=end_date,
                budget=project_data['budget'],
                estimated_hours=project_data['estimated_hours'],
                team_size_min=3,
                team_size_max=8,
                required_skills=['Python', 'Django', 'React', 'AWS', '프로젝트 관리'],
                success_criteria=['일정 준수', '예산 내 완료', '품질 기준 충족']
            )
            
            # 스킬 요구사항 생성
            skills = [
                ('Python', 'TECHNICAL', 'ADVANCED', 'REQUIRED'),
                ('Django', 'TECHNICAL', 'ADVANCED', 'REQUIRED'),
                ('React', 'TECHNICAL', 'INTERMEDIATE', 'PREFERRED'),
                ('AWS', 'TECHNICAL', 'INTERMEDIATE', 'REQUIRED'),
                ('프로젝트 관리', 'MANAGEMENT', 'ADVANCED', 'CRITICAL'),
                ('커뮤니케이션', 'SOFT_SKILL', 'INTERMEDIATE', 'REQUIRED')
            ]
            
            for skill_name, category, proficiency, importance in skills[:random.randint(3, 6)]:
                SkillRequirement.objects.create(
                    project=project,
                    skill_name=skill_name,
                    category=category,
                    required_proficiency=proficiency,
                    importance=importance,
                    weight=random.uniform(0.5, 1.0)
                )
            
            # 팀 구성 생성
            if project.status in ['ACTIVE', 'COMPLETED']:
                composition = TeamComposition.objects.create(
                    project=project,
                    name=f"{project.name} 최적팀",
                    description=f"AI가 추천한 {project.name} 프로젝트 최적 팀 구성",
                    status='APPROVED' if project.status == 'ACTIVE' else 'COMPLETED',
                    ai_generated=True,
                    compatibility_score=random.uniform(7.0, 9.5),
                    efficiency_score=random.uniform(7.0, 9.5),
                    risk_score=random.uniform(2.0, 4.0),
                    overall_score=random.uniform(7.5, 9.0),
                    ai_analysis={
                        'strengths': ['높은 기술 역량', '좋은 팀워크', '경험 풍부'],
                        'weaknesses': ['일부 스킬 부족', '일정 압박'],
                        'recommendations': ['추가 교육 필요', '일정 조정 검토']
                    }
                )
                
                # 팀 멤버 할당
                selected_employees = random.sample(list(employees), min(len(employees), random.randint(4, 7)))
                roles = ['LEAD', 'SENIOR', 'JUNIOR', 'SPECIALIST']
                
                for emp in selected_employees:
                    TeamMember.objects.create(
                        team_composition=composition,
                        employee=emp,
                        role=random.choice(roles),
                        allocation_type='FULL_TIME',
                        allocation_percentage=100.0,
                        responsibilities=['개발', '테스트', '문서화'],
                        fit_score=random.uniform(7.0, 9.5),
                        synergy_score=random.uniform(7.0, 9.0),
                        availability_score=random.uniform(6.0, 9.0),
                        is_confirmed=True if composition.status == 'APPROVED' else False
                    )
        
        self.stdout.write(self.style.SUCCESS(f'✓ 프로젝트 {Project.objects.count()}개 생성'))
        self.stdout.write(self.style.SUCCESS(f'✓ 팀 구성 {TeamComposition.objects.count()}개 생성'))