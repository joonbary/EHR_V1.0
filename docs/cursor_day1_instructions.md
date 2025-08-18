# Day 1-2: Cursor AI 성과평가 모델 구현 지시서

## 🎯 **작업 목표**
OK금융그룹 신인사제도에 맞는 성과평가 Django 앱 생성 및 핵심 모델 8개 구현

---

## 📋 **작업 순서**

### **Step 1: Performance 앱 생성**
```bash
# 터미널에서 실행
cd e-hr-system
python manage.py startapp performance
```

### **Step 2: settings.py 앱 등록**
```python
# e_hr_system/settings.py 파일 수정
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'employees',  # 기존 앱
    'performance',  # 새로 추가
]
```

### **Step 3: Employee 모델 확장**
```python
# employees/models.py 파일에 추가할 필드들
# 기존 Employee 모델에 다음 필드들을 추가해주세요

class Employee(models.Model):
    # 기존 필드들은 그대로 유지하고 아래 필드들을 추가
    
    # OK금융그룹 조직 정보
    job_group = models.CharField(max_length=20, choices=[
        ('PL', 'PL직군'),
        ('Non-PL', 'Non-PL직군'),
    ], default='Non-PL')
    
    job_type = models.CharField(max_length=50, choices=[
        # PL직군
        ('고객지원', '고객지원'),
        
        # Non-PL직군  
        ('IT기획', 'IT기획'),
        ('IT개발', 'IT개발'),
        ('IT운영', 'IT운영'),
        ('경영관리', '경영관리'),
        ('기업영업', '기업영업'),
        ('기업금융', '기업금융'),
        ('리테일금융', '리테일금융'),
        ('투자금융', '투자금융'),
    ], default='경영관리')
    
    job_role = models.CharField(max_length=100, blank=True, help_text="구체적인 직무")
    
    # 성장레벨 (기존 직급 대체)
    growth_level = models.IntegerField(default=1, help_text="성장레벨 1-6")
    
    # 직책 (성장레벨과 분리 운영)
    position = models.CharField(max_length=50, choices=[
        ('사원', '사원'),
        ('대리', '대리'),
        ('과장', '과장'),
        ('차장', '차장'),
        ('부장', '부장'),
        ('팀장', '팀장'),
        ('지점장', '지점장'),
        ('본부장', '본부장'),
    ], default='사원')
    
    # 직속 상사 (평가권자)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='subordinates')
    
    def __str__(self):
        return f"{self.name} ({self.job_type}/{self.position}/Lv.{self.growth_level})"
    
    class Meta:
        db_table = 'employees_employee'
```

### **Step 4: 성과평가 모델들 구현**
```python
# performance/models.py 파일 전체 내용

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from employees.models import Employee

class GrowthLevelStandard(models.Model):
    """성장레벨별 평가 기준"""
    job_group = models.CharField(max_length=20, choices=[
        ('PL', 'PL직군'),
        ('Non-PL', 'Non-PL직군'),
    ])
    job_type = models.CharField(max_length=50)
    level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    
    # 각 평가축별 기준
    contribution_criteria = models.TextField(help_text="기여도 평가 기준")
    expertise_criteria = models.TextField(help_text="전문성 평가 기준")
    impact_criteria = models.TextField(help_text="영향력 평가 기준")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.job_type} Level {self.level} 기준"
    
    class Meta:
        unique_together = ['job_type', 'level']
        ordering = ['job_type', 'level']


class EvaluationPeriod(models.Model):
    """평가 기간 관리"""
    year = models.IntegerField()
    period_type = models.CharField(max_length=20, choices=[
        ('Q1', '1분기'),
        ('Q2', '2분기'), 
        ('Q3', '3분기'),
        ('Q4', '4분기'),
        ('H1', '상반기'),
        ('H2', '하반기'),
        ('ANNUAL', '연간'),
    ])
    period_number = models.IntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.year}년 {self.get_period_type_display()}"
    
    class Meta:
        unique_together = ['year', 'period_type', 'period_number']
        ordering = ['-year', 'period_type']


class Task(models.Model):
    """업무 과제 관리"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='tasks')
    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200, help_text="Task명")
    description = models.TextField(blank=True, help_text="상세 내용")
    weight = models.DecimalField(max_digits=5, decimal_places=2, 
                               validators=[MinValueValidator(0), MaxValueValidator(100)],
                               help_text="비중 (%)")
    
    contribution_method = models.CharField(max_length=20, choices=[
        ('충분', '충분'),
        ('리딩', '리딩'),
        ('실무', '실무'),
        ('지원', '지원'),
    ], help_text="기여방식")
    
    # 목표 설정
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    target_unit = models.CharField(max_length=50, default='억원', help_text="목표 단위")
    
    # 실적 입력
    actual_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    achievement_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, 
                                         help_text="달성률 (%)")
    
    # 승인 상태
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', '등록'),
        ('APPROVED', '승인'),
        ('COMPLETED', '완료'),
    ], default='DRAFT')
    
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_tasks')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_achievement_rate(self):
        """달성률 자동 계산"""
        if self.target_value and self.target_value > 0 and self.actual_value:
            self.achievement_rate = (self.actual_value / self.target_value) * 100
        return self.achievement_rate
    
    def __str__(self):
        return f"{self.employee.name} - {self.title} ({self.weight}%)"
    
    class Meta:
        ordering = ['-created_at']


class ContributionEvaluation(models.Model):
    """기여도 평가"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE)
    
    # 전체 달성률 (모든 Task의 가중평균)
    total_achievement_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # 기여도 점수 (1-4점, OK금융그룹 Scoring Chart 기반)
    contribution_score = models.DecimalField(max_digits=3, decimal_places=1, 
                                           validators=[MinValueValidator(1), MaxValueValidator(4)])
    
    # 달성 여부 (성장레벨 기준 대비)
    is_achieved = models.BooleanField(default=False)
    
    # 평가자
    evaluator = models.ForeignKey(Employee, on_delete=models.CASCADE, 
                                related_name='contribution_evaluations_done')
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    comments = models.TextField(blank=True, help_text="평가 의견")
    
    def __str__(self):
        return f"{self.employee.name} 기여도평가 ({self.evaluation_period})"
    
    class Meta:
        unique_together = ['employee', 'evaluation_period']


class ExpertiseEvaluation(models.Model):
    """전문성 평가"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE)
    
    # 성장레벨별 전문성 기준 대비 평가
    required_level = models.IntegerField()  # 요구 성장레벨
    
    # 세부 평가 항목들
    strategic_contribution = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)],
                                               help_text="전략적 기여 (1-4점)")
    interactive_contribution = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)],
                                                 help_text="상호적 기여 (1-4점)")
    
    # 자가진단 의견
    self_assessment = models.TextField(blank=True, help_text="자가진단 의견")
    
    # 총합 평가
    total_score = models.DecimalField(max_digits=3, decimal_places=1)
    is_achieved = models.BooleanField(default=False)
    
    evaluator = models.ForeignKey(Employee, on_delete=models.CASCADE, 
                                related_name='expertise_evaluations_done')
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.name} 전문성평가 ({self.evaluation_period})"
    
    class Meta:
        unique_together = ['employee', 'evaluation_period']


class ImpactEvaluation(models.Model):
    """영향력 평가"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE)
    
    # 핵심가치 평가 (각각 1-4점)
    customer_focus = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)],
                                       help_text="고객중심 (1-4점)")
    collaboration = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)],
                                      help_text="상생협력 (1-4점)")
    innovation = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)],
                                   help_text="혁신도전 (1-4점)")
    
    # 리더십 평가
    team_leadership = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)],
                                        help_text="팀 리더십 (1-4점)")
    organizational_impact = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)],
                                              help_text="조직 영향력 (1-4점)")
    external_networking = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)],
                                            help_text="대외 네트워킹 (1-4점)")
    
    # 영향력 발휘 사례
    impact_examples = models.TextField(blank=True, help_text="영향력 발휘 사례")
    
    # 총합 평가
    total_score = models.DecimalField(max_digits=3, decimal_places=1)
    is_achieved = models.BooleanField(default=False)
    
    evaluator = models.ForeignKey(Employee, on_delete=models.CASCADE, 
                                related_name='impact_evaluations_done')
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_total_score(self):
        """총점 자동 계산"""
        core_values_avg = (self.customer_focus + self.collaboration + self.innovation) / 3
        leadership_avg = (self.team_leadership + self.organizational_impact + self.external_networking) / 3
        self.total_score = (core_values_avg + leadership_avg) / 2
        return self.total_score
    
    def __str__(self):
        return f"{self.employee.name} 영향력평가 ({self.evaluation_period})"
    
    class Meta:
        unique_together = ['employee', 'evaluation_period']


class ComprehensiveEvaluation(models.Model):
    """종합 평가 (최종 결과)"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE)
    
    # 3대 평가 결과 참조
    contribution_evaluation = models.ForeignKey(ContributionEvaluation, on_delete=models.CASCADE)
    expertise_evaluation = models.ForeignKey(ExpertiseEvaluation, on_delete=models.CASCADE)
    impact_evaluation = models.ForeignKey(ImpactEvaluation, on_delete=models.CASCADE)
    
    # 달성 현황
    contribution_achieved = models.BooleanField()
    expertise_achieved = models.BooleanField()
    impact_achieved = models.BooleanField()
    
    # 1차 부서장 등급 (A/B/C)
    manager_grade = models.CharField(max_length=1, choices=[
        ('A', 'A - 기대 수준 초과'),
        ('B', 'B - 기대 수준 상응'), 
        ('C', 'C - 기대 수준 이하'),
    ])
    manager_comments = models.TextField(blank=True)
    
    # 2차 Calibration 결과 (S/A+/A/B+/B/C/D)
    final_grade = models.CharField(max_length=2, choices=[
        ('S', 'S - 업계 최고수준'),
        ('A+', 'A+ - 기대수준 매우 초과'),
        ('A', 'A - 기대수준 초과'),
        ('B+', 'B+ - 기대수준 이상'),
        ('B', 'B - 기대수준 부합'),
        ('C', 'C - 기대수준 미만'),
        ('D', 'D - 개선필요'),
    ], null=True, blank=True)
    
    calibration_comments = models.TextField(blank=True, help_text="Calibration Session 논의 내용")
    
    # 평가자 정보
    manager = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='managed_evaluations')
    calibration_committee = models.TextField(blank=True, help_text="Calibration 참여 위원")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def auto_calculate_manager_grade(self):
        """1차 등급 자동 산출"""
        achieved_count = sum([
            self.contribution_achieved,
            self.expertise_achieved, 
            self.impact_achieved
        ])
        
        if achieved_count >= 2:
            self.manager_grade = 'A'
        elif achieved_count == 1:
            self.manager_grade = 'B'
        else:
            self.manager_grade = 'C'
        
        return self.manager_grade
    
    def __str__(self):
        return f"{self.employee.name} 종합평가 ({self.evaluation_period}) - {self.manager_grade}"
    
    class Meta:
        unique_together = ['employee', 'evaluation_period']
        ordering = ['-evaluation_period__year', '-updated_at']


class CheckInRecord(models.Model):
    """수시 Check-in 기록"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    
    check_date = models.DateField()
    progress_rate = models.DecimalField(max_digits=5, decimal_places=2, 
                                      help_text="진행률 (%)")
    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # 상황 보고
    issues = models.TextField(blank=True, help_text="이슈사항")
    support_needed = models.TextField(blank=True, help_text="지원필요사항") 
    next_action = models.TextField(blank=True, help_text="향후 액션")
    
    # 관리자 피드백
    manager_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.name} - {self.task.title} Check-in ({self.check_date})"
    
    class Meta:
        ordering = ['-check_date']
```

### **Step 5: Admin 페이지 설정**
```python
# performance/admin.py 파일 전체 내용

from django.contrib import admin
from .models import *

@admin.register(GrowthLevelStandard)
class GrowthLevelStandardAdmin(admin.ModelAdmin):
    list_display = ['job_type', 'level', 'created_at']
    list_filter = ['job_group', 'job_type', 'level']
    search_fields = ['job_type']
    ordering = ['job_type', 'level']

@admin.register(EvaluationPeriod)
class EvaluationPeriodAdmin(admin.ModelAdmin):
    list_display = ['year', 'period_type', 'start_date', 'end_date', 'is_active']
    list_filter = ['year', 'period_type', 'is_active']
    ordering = ['-year', 'period_type']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'weight', 'contribution_method', 'status', 'achievement_rate']
    list_filter = ['status', 'contribution_method', 'evaluation_period']
    search_fields = ['employee__name', 'title']
    raw_id_fields = ['employee', 'approved_by']

@admin.register(ContributionEvaluation)
class ContributionEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_period', 'contribution_score', 'is_achieved']
    list_filter = ['is_achieved', 'evaluation_period']
    search_fields = ['employee__name']

@admin.register(ExpertiseEvaluation)
class ExpertiseEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_period', 'total_score', 'is_achieved']
    list_filter = ['is_achieved', 'evaluation_period']
    search_fields = ['employee__name']

@admin.register(ImpactEvaluation)
class ImpactEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_period', 'total_score', 'is_achieved']
    list_filter = ['is_achieved', 'evaluation_period']
    search_fields = ['employee__name']

@admin.register(ComprehensiveEvaluation)
class ComprehensiveEvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'evaluation_period', 'manager_grade', 'final_grade', 'updated_at']
    list_filter = ['manager_grade', 'final_grade', 'evaluation_period']
    search_fields = ['employee__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CheckInRecord)
class CheckInRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'task', 'check_date', 'progress_rate']
    list_filter = ['check_date']
    search_fields = ['employee__name', 'task__title']
    date_hierarchy = 'check_date'
```

### **Step 6: 마이그레이션 생성 및 적용**
```bash
# 터미널에서 순서대로 실행
python manage.py makemigrations employees
python manage.py makemigrations performance
python manage.py migrate
```

### **Step 7: 슈퍼유저 생성 (필요시)**
```bash
# 기존에 없다면 생성
python manage.py createsuperuser
```

### **Step 8: 서버 실행 및 테스트**
```bash
python manage.py runserver
# 브라우저에서 http://127.0.0.1:8000/admin/ 접속하여 모든 모델이 정상 등록되었는지 확인
```

---

## ✅ **완료 확인 체크리스트**

- [ ] Performance 앱 생성 완료
- [ ] Employee 모델에 OK금융그룹 필드 추가 완료  
- [ ] 8개 성과평가 모델 생성 완료
- [ ] Admin 페이지 등록 완료
- [ ] 마이그레이션 적용 완료
- [ ] Admin 페이지에서 모든 모델 확인 가능
- [ ] 오류 없이 서버 실행 가능

---

## 🚨 **주의사항**

1. **기존 Employee 모델 수정 시**: 기존 데이터가 있다면 migration 시 default 값 설정 필요
2. **외래키 관계**: Employee 모델을 참조하는 모든 관계가 올바르게 설정되어야 함
3. **유효성 검사**: 모든 점수 필드에 1-4점 범위 제한 적용
4. **한글 필드명**: help_text로 한글 설명 추가하여 관리자 편의성 확보

---

## 🎯 **다음 단계 예고**

Day 3-4에서는 이 모델들을 활용한 **기본 View와 URL 구성**을 진행합니다:
- 성과평가 메인 대시보드 View
- Task 등록/수정 View  
- 각 평가축별 입력 화면 View
- 기본 템플릿 구조 설계

**이 지시서대로 Cursor AI에서 구현 후 결과를 공유해주세요!** 🚀