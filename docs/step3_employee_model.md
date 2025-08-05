# Step 3: Employee 모델 OK금융그룹 필드 추가

## 🎯 **작업 목표**
기존 Employee 모델에 OK금융그룹 신인사제도에 맞는 필드들을 추가

---

## 📝 **Cursor AI 작업 지시**

### **파일: `employees/models.py`**

기존 Employee 모델에 다음 필드들을 **추가**해주세요:

```python
# employees/models.py 파일 수정
# 기존 코드는 그대로 유지하고, Employee 클래스에 아래 필드들을 추가

from django.db import models

class Employee(models.Model):
    # === 기존 필드들은 그대로 유지 ===
    # name, email, phone, department, hire_date 등
    
    # === 추가할 OK금융그룹 신인사제도 필드들 ===
    
    # 직군 분류 (PL/Non-PL)
    job_group = models.CharField(
        max_length=20, 
        choices=[
            ('PL', 'PL직군'),
            ('Non-PL', 'Non-PL직군'),
        ], 
        default='Non-PL',
        help_text="PL직군(고객지원) 또는 Non-PL직군"
    )
    
    # 직종 분류
    job_type = models.CharField(
        max_length=50, 
        choices=[
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
        ], 
        default='경영관리',
        help_text="세부 직종 분류"
    )
    
    # 구체적 직무 (자유 입력)
    job_role = models.CharField(
        max_length=100, 
        blank=True,
        help_text="구체적인 직무 (예: 수신고객지원, 시스템기획, HRM 등)"
    )
    
    # 성장레벨 (기존 직급 대체)
    growth_level = models.IntegerField(
        default=1,
        choices=[
            (1, 'Level 1'),
            (2, 'Level 2'),
            (3, 'Level 3'),
            (4, 'Level 4'),
            (5, 'Level 5'),
            (6, 'Level 6'),
        ],
        help_text="성장레벨 1-6단계"
    )
    
    # 직책 (성장레벨과 분리 운영)
    position = models.CharField(
        max_length=50, 
        choices=[
            ('사원', '사원'),
            ('선임', '선임'),
            ('주임', '주임'),
            ('대리', '대리'),
            ('과장', '과장'),
            ('차장', '차장'),
            ('부부장', '부부장'),
            ('부장', '부장'),
            ('팀장', '팀장'),
            ('지점장', '지점장'),
            ('본부장', '본부장'),
        ], 
        default='사원',
        help_text="조직 내 직책"
    )
    
    # 직속 상사 (평가권자)
    manager = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='subordinates',
        help_text="직속 상사 (평가권자)"
    )
    
    # 급호 (호봉)
    grade_level = models.IntegerField(
        default=1,
        help_text="급호 (호봉)"
    )
    
    # 입사구분
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('정규직', '정규직'),
            ('계약직', '계약직'),
            ('파견', '파견'),
            ('인턴', '인턴'),
        ],
        default='정규직'
    )
    
    # 재직상태
    employment_status = models.CharField(
        max_length=20,
        choices=[
            ('재직', '재직'),
            ('휴직', '휴직'),
            ('퇴직', '퇴직'),
            ('파견', '파견'),
        ],
        default='재직'
    )
    
    def __str__(self):
        return f"{self.name} ({self.job_type}/{self.position}/Lv.{self.growth_level})"
    
    def get_full_position(self):
        """전체 직책 정보 반환"""
        return f"{self.job_group} > {self.job_type} > {self.position} (Level {self.growth_level})"
    
    def get_subordinates(self):
        """부하직원 목록 반환"""
        return self.subordinates.filter(employment_status='재직')
    
    def is_manager(self):
        """관리자 여부 확인"""
        return self.subordinates.exists()
    
    class Meta:
        db_table = 'employees_employee'  # 기존 테이블명 유지
        ordering = ['department', 'growth_level', 'name']
        verbose_name = '직원'
        verbose_name_plural = '직원관리'
```

---

## 🔧 **Admin 페이지 업데이트**

### **파일: `employees/admin.py`**

Admin 페이지도 새로운 필드들을 반영하여 업데이트해주세요:

```python
# employees/admin.py 파일 수정

from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'job_group', 'job_type', 'position', 
        'growth_level', 'department', 'manager', 'employment_status'
    ]
    
    list_filter = [
        'job_group', 'job_type', 'position', 'growth_level', 
        'employment_status', 'employment_type', 'department'
    ]
    
    search_fields = ['name', 'email', 'job_role']
    
    raw_id_fields = ['manager']  # 관리자 선택을 위한 검색 인터페이스
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'email', 'phone', 'hire_date')
        }),
        ('조직 정보', {
            'fields': (
                'job_group', 'job_type', 'job_role', 
                'department', 'position', 'growth_level', 'grade_level'
            )
        }),
        ('관계 정보', {
            'fields': ('manager',)
        }),
        ('고용 정보', {
            'fields': ('employment_type', 'employment_status')
        }),
    )
    
    ordering = ['job_group', 'job_type', 'growth_level', 'name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('manager')
```

---

## 📊 **마이그레이션 생성**

Employee 모델 수정 후 마이그레이션을 생성해주세요:

```bash
python manage.py makemigrations employees
```

⚠️ **주의**: 기존 데이터가 있다면 새 필드들의 기본값을 설정하라는 프롬프트가 나올 수 있습니다. 다음과 같이 응답하세요:

1. `job_group` 기본값: `2` (Non-PL 선택)
2. `job_type` 기본값: `7` (경영관리 선택)  
3. `growth_level` 기본값: `1` (Level 1 선택)
4. `position` 기본값: `1` (사원 선택)

---

## ✅ **완료 확인 체크리스트**

- [ ] Employee 모델에 OK금융그룹 필드 10개 추가 완료
- [ ] EmployeeAdmin 클래스 업데이트 완료  
- [ ] 마이그레이션 생성 완료 (오류 없음)
- [ ] `__str__` 메서드에 새로운 필드들 반영 완료
- [ ] Admin 페이지에서 새 필드들 확인 가능

---

## 🎯 **다음 단계 예고**

Step 3 완료 후에는 **Step 4: 성과평가 모델 8개 구현**을 진행합니다:
- GrowthLevelStandard (성장레벨 기준)
- EvaluationPeriod (평가기간)  
- Task (업무과제)
- ContributionEvaluation (기여도평가)
- ExpertiseEvaluation (전문성평가)
- ImpactEvaluation (영향력평가)
- ComprehensiveEvaluation (종합평가)
- CheckInRecord (체크인 기록)

**이 단계 완료 후 결과를 알려주세요!** 🚀