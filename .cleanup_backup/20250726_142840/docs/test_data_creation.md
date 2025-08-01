# OK금융그룹 테스트 데이터 생성 지시서

## 🎯 **작업 목표**
실제 OK금융그룹 조직구조를 반영한 테스트 데이터 생성으로 시스템 검증

---

## 📝 **Cursor AI 작업 지시**

### **파일: `performance/management/commands/create_test_data.py`**

먼저 management 디렉토리 구조를 생성해주세요:

```bash
mkdir -p performance/management/commands
touch performance/management/__init__.py
touch performance/management/commands/__init__.py
```

그 다음 아래 코드를 `create_test_data.py` 파일로 생성해주세요:

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from employees.models import Employee
from performance.models import *

class Command(BaseCommand):
    help = 'OK금융그룹 테스트 데이터 생성'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('OK금융그룹 테스트 데이터 생성 시작...'))
        
        # 1. 평가 기간 생성
        self.create_evaluation_periods()
        
        # 2. 성장레벨 기준 생성  
        self.create_growth_level_standards()
        
        # 3. 직원 데이터 생성
        self.create_employees()
        
        # 4. Task 및 평가 데이터 생성
        self.create_tasks_and_evaluations()
        
        self.stdout.write(self.style.SUCCESS('테스트 데이터 생성 완료!'))

    def create_evaluation_periods(self):
        """평가 기간 생성"""
        periods = [
            (2024, 'Q1', date(2024, 1, 1), date(2024, 3, 31)),
            (2024, 'Q2', date(2024, 4, 1), date(2024, 6, 30)),
            (2024, 'Q3', date(2024, 7, 1), date(2024, 9, 30)),
            (2024, 'Q4', date(2024, 10, 1), date(2024, 12, 31), True),  # 현재 활성
            (2024, 'ANNUAL', date(2024, 1, 1), date(2024, 12, 31)),
        ]
        
        for year, period_type, start, end, *active in periods:
            is_active = len(active) > 0 and active[0]
            period, created = EvaluationPeriod.objects.get_or_create(
                year=year,
                period_type=period_type,
                defaults={
                    'start_date': start,
                    'end_date': end,
                    'is_active': is_active,
                    'status': 'ONGOING' if is_active else 'COMPLETED'
                }
            )
            if created:
                self.stdout.write(f'평가기간 생성: {period}')

    def create_growth_level_standards(self):
        """성장레벨별 평가 기준 생성"""
        standards_data = [
            # Non-PL 직군
            ('Non-PL', '기업영업', 1, '신입 수준의 기여', '기본 업무 지식', '팀내 협조'),
            ('Non-PL', '기업영업', 2, '담당 업무 완수', '업무 숙련도 향상', '부서내 영향력'),
            ('Non-PL', '기업영업', 3, '팀 목표 달성 기여', '전문 지식 보유', '조직 리더십'),
            ('Non-PL', '기업영업', 4, '부서 목표 초과 달성', '고도 전문성', '조직 영향력'),
            
            ('Non-PL', '경영관리', 1, '기본 업무 수행', 'HR 기초 지식', '팀 협조'),
            ('Non-PL', '경영관리', 2, '담당 업무 완료', 'HR 실무 능력', '부서 기여'),
            ('Non-PL', '경영관리', 3, '팀 성과 기여', 'HR 전문 역량', '조직 개선'),
            
            ('Non-PL', 'IT기획', 1, '시스템 기초 업무', 'IT 기본 지식', '팀내 소통'),
            ('Non-PL', 'IT기획', 2, '시스템 기획 참여', 'IT 기획 능력', '프로젝트 기여'),
            ('Non-PL', 'IT기획', 3, '시스템 기획 주도', 'IT 전문성', '조직 혁신'),
            
            # PL 직군
            ('PL', '고객지원', 1, '기본 고객 응대', '상품 기초 지식', '고객 만족'),
            ('PL', '고객지원', 2, '고객 문제 해결', '상품 전문 지식', '팀 협력'),
            ('PL', '고객지원', 3, '고객 만족 향상', '업무 전문성', '지점 기여'),
        ]
        
        for job_group, job_type, level, contrib, expert, impact in standards_data:
            standard, created = GrowthLevelStandard.objects.get_or_create(
                job_group=job_group,
                job_type=job_type,
                level=level,
                defaults={
                    'contribution_criteria': contrib,
                    'expertise_criteria': expert,
                    'impact_criteria': impact,
                }
            )
            if created:
                self.stdout.write(f'평가기준 생성: {job_type} Level {level}')

    def create_employees(self):
        """OK금융그룹 조직구조 기반 직원 생성"""
        # 본부장급
        ceo = Employee.objects.create(
            name='김대표',
            email='ceo@okfinance.co.kr',
            job_group='Non-PL',
            job_type='경영관리',
            job_role='경영총괄',
            growth_level=6,
            position='본부장',
            department='경영본부'
        )
        
        # 기업금융본부
        corp_head = Employee.objects.create(
            name='박본부장',
            email='park.head@okfinance.co.kr',
            job_group='Non-PL',
            job_type='기업금융',
            job_role='기업금융총괄',
            growth_level=5,
            position='본부장',
            department='기업금융본부',
            manager=ceo
        )
        
        # 기업영업팀
        corp_teams = [
            ('기업금융1팀', '이팀장', 'lee.team1@okfinance.co.kr'),
            ('기업금융2팀', '정팀장', 'jung.team2@okfinance.co.kr'),
            ('기업금융3팀', '최팀장', 'choi.team3@okfinance.co.kr'),
        ]
        
        team_leaders = []
        for dept, name, email in corp_teams:
            leader = Employee.objects.create(
                name=name,
                email=email,
                job_group='Non-PL',
                job_type='기업영업',
                job_role='기업영업관리',
                growth_level=4,
                position='팀장',
                department=dept,
                manager=corp_head
            )
            team_leaders.append(leader)
        
        # 팀원들 생성
        team_members_data = [
            ('김철수', 'kim.cs@okfinance.co.kr', '기업금융1팀', 3, '지점장'),
            ('박영희', 'park.yh@okfinance.co.kr', '기업금융1팀', 2, '과장'),
            ('정민수', 'jung.ms@okfinance.co.kr', '기업금융2팀', 3, '차장'),
            ('최지원', 'choi.jw@okfinance.co.kr', '기업금융2팀', 2, '대리'),
            ('한상호', 'han.sh@okfinance.co.kr', '기업금융3팀', 2, '과장'),
            ('조미영', 'jo.my@okfinance.co.kr', '기업금융3팀', 1, '사원'),
        ]
        
        for name, email, dept, level, position in team_members_data:
            # 해당 팀의 팀장 찾기
            manager = next((tl for tl in team_leaders if tl.department == dept), None)
            
            Employee.objects.create(
                name=name,
                email=email,
                job_group='Non-PL',
                job_type='기업영업',
                job_role='기업영업',
                growth_level=level,
                position=position,
                department=dept,
                manager=manager
            )
        
        # IT부서
        it_head = Employee.objects.create(
            name='김IT본부장',
            email='kim.it@okfinance.co.kr',
            job_group='Non-PL',
            job_type='IT기획',
            job_role='IT총괄',
            growth_level=5,
            position='본부장',
            department='IT본부',
            manager=ceo
        )
        
        it_members = [
            ('이개발', 'lee.dev@okfinance.co.kr', 'IT개발', 'IT개발', 3, '팀장'),
            ('박시스템', 'park.sys@okfinance.co.kr', 'IT운영', 'IT운영', 2, '과장'),
        ]
        
        for name, email, job_type, job_role, level, position in it_members:
            Employee.objects.create(
                name=name,
                email=email,
                job_group='Non-PL',
                job_type=job_type,
                job_role=job_role,
                growth_level=level,
                position=position,
                department='IT본부',
                manager=it_head
            )
        
        # 경영관리부
        hr_head = Employee.objects.create(
            name='안사팀',
            email='ahn.hr@okfinance.co.kr',
            job_group='Non-PL',
            job_type='경영관리',
            job_role='HRM',
            growth_level=3,
            position='팀장',
            department='경영관리팀',
            manager=ceo
        )
        
        # PL직군 (고객지원)
        branch_manager = Employee.objects.create(
            name='고지점장',
            email='go.branch@okfinance.co.kr',
            job_group='PL',
            job_type='고객지원',
            job_role='지점관리',
            growth_level=3,
            position='지점장',
            department='○○지점',
            manager=ceo
        )
        
        cs_members = [
            ('서고객', 'seo.cs@okfinance.co.kr', '고객지원', '수신고객지원', 2, '대리'),
            ('문상담', 'moon.cs@okfinance.co.kr', '고객지원', '여신고객지원', 1, '사원'),
        ]
        
        for name, email, job_type, job_role, level, position in cs_members:
            Employee.objects.create(
                name=name,
                email=email,
                job_group='PL',
                job_type=job_type,
                job_role=job_role,
                growth_level=level,
                position=position,
                department='○○지점',
                manager=branch_manager
            )
        
        self.stdout.write(f'직원 데이터 생성 완료: 총 {Employee.objects.count()}명')

    def create_tasks_and_evaluations(self):
        """Task 및 평가 데이터 생성"""
        current_period = EvaluationPeriod.objects.filter(is_active=True).first()
        annual_period = EvaluationPeriod.objects.filter(period_type='ANNUAL', year=2024).first()
        
        if not current_period or not annual_period:
            self.stdout.write('평가기간이 없어 Task 생성을 건너뜁니다.')
            return
        
        # 기업영업팀 직원들의 Task 생성
        corp_employees = Employee.objects.filter(job_type='기업영업')
        
        for employee in corp_employees:
            # 분기별 Task 생성
            tasks_data = [
                ('○○동 오피스텔 PF', '리딩', 10, 300, 350),
                ('○○동 클루센터 B/L', '리딩', 30, 300, 50),
                ('○○동 오피스텔 증도', '실무', 30, 200, 200),
                ('○○동 상가담보대출', '지원', 30, 150, 180),
            ]
            
            for title, method, weight, target, actual in tasks_data:
                task = Task.objects.create(
                    employee=employee,
                    evaluation_period=current_period,
                    title=title,
                    description=f'{employee.name}의 {title} 담당 업무',
                    weight=Decimal(str(weight)),
                    contribution_method=method,
                    target_value=Decimal(str(target)),
                    target_unit='억원',
                    actual_value=Decimal(str(actual)),
                    status='COMPLETED',
                    approved_by=employee.manager,
                    approved_at=timezone.now()
                )
                task.calculate_achievement_rate()
                task.save()
            
            # 기여도 평가 생성
            total_achievement = sum([350/300, 50/300, 200/200, 180/150]) * 25  # 가중평균
            
            ContributionEvaluation.objects.create(
                employee=employee,
                evaluation_period=current_period,
                total_achievement_rate=Decimal(str(total_achievement)),
                contribution_score=Decimal('3.1'),
                is_achieved=True,
                evaluator=employee.manager,
                comments=f'{employee.name}의 우수한 기여도 성과'
            )
            
            # 전문성 평가 생성 (연간)
            ExpertiseEvaluation.objects.create(
                employee=employee,
                evaluation_period=annual_period,
                required_level=employee.growth_level,
                strategic_contribution=random.randint(2, 4),
                interactive_contribution=random.randint(2, 4),
                technical_expertise=random.randint(2, 4),
                business_understanding=random.randint(2, 4),
                total_score=Decimal('3.2'),
                is_achieved=True,
                evaluator=employee.manager
            )
            
            # 영향력 평가 생성 (연간)
            ImpactEvaluation.objects.create(
                employee=employee,
                evaluation_period=annual_period,
                customer_focus=random.randint(2, 4),
                collaboration=random.randint(2, 4),
                innovation=random.randint(2, 4),
                team_leadership=random.randint(2, 4),
                organizational_impact=random.randint(2, 3),
                external_networking=random.randint(2, 3),
                total_score=Decimal('2.8'),
                is_achieved=False if employee.name == '김철수' else True,
                evaluator=employee.manager
            )
            
            # 종합 평가 생성
            comp_eval = ComprehensiveEvaluation.objects.create(
                employee=employee,
                evaluation_period=annual_period,
                contribution_achieved=True,
                expertise_achieved=True,
                impact_achieved=False if employee.name == '김철수' else True,
                manager=employee.manager,
                manager_comments=f'{employee.name}의 연간 종합 평가'
            )
            comp_eval.auto_calculate_manager_grade()
            comp_eval.save()
            
            # Check-in 기록 생성
            for i in range(3):
                check_date = current_period.start_date + timedelta(days=30*i)
                CheckInRecord.objects.create(
                    employee=employee,
                    task=Task.objects.filter(employee=employee).first(),
                    check_date=check_date,
                    progress_rate=Decimal(str(25 * (i+1))),
                    current_value=Decimal(str(100 * (i+1))),
                    issues='진행 중 이슈 없음',
                    next_action='계속 추진',
                    manager_feedback='좋은 진행상황'
                )
        
        self.stdout.write('Task 및 평가 데이터 생성 완료')
```

---

## 🚀 **실행 명령어**

```bash
python manage.py create_test_data
```

---

## ✅ **생성될 테스트 데이터**

### **조직 구조**
- **경영본부**: CEO + 본부장급
- **기업금융본부**: 본부장 + 3개팀 (팀장 + 팀원 6명)
- **IT본부**: 본부장 + IT개발/운영 담당자
- **경영관리팀**: HRM 담당자
- **○○지점**: PL직군 고객지원 담당자

### **평가 데이터**
- **2024년 분기별/연간 평가기간**
- **성장레벨별 평가기준** (실제 OK금융그룹 기준 반영)
- **Task 및 실적**: 기업영업팀 실제 업무 사례
- **3대 평가축**: 기여도/전문성/영향력 샘플 데이터
- **종합평가**: 1차 등급 자동 산출 결과
- **Check-in 기록**: 분기별 진도 관리 샘플

---

## 🎯 **검증 방법**

테스트 데이터 생성 후 Admin 페이지에서 확인:
1. **직원 목록**: OK금융그룹 조직도 반영
2. **Task 현황**: 실제 기업영업 업무 사례  
3. **평가 결과**: 3대 평가축 통합 결과
4. **종합평가**: A/B/C 등급 자동 산출 확인