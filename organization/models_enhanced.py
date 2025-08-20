"""
Enhanced Organization Models for Advanced Org Chart Management
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db import transaction
import uuid
import json

# Django 3.1+ has JSONField for all databases
try:
    from django.db.models import JSONField
except ImportError:
    # For older Django versions, use TextField with JSON serialization
    from django.contrib.postgres.fields import JSONField


class OrgUnit(models.Model):
    """
    조직 단위 모델 - 회사의 각 조직 단위를 표현
    """
    COMPANY_CHOICES = [
        ('OK저축은행', 'OK저축은행'),
        ('OK캐피탈', 'OK캐피탈'),
        ('OK금융그룹', 'OK금융그룹'),
        ('ALL', '전체'),
    ]
    
    # Primary Keys
    id = models.CharField(max_length=50, primary_key=True, verbose_name="조직 ID")
    
    # Organization Info
    company = models.CharField(
        max_length=50, 
        choices=COMPANY_CHOICES,
        db_index=True,
        verbose_name="회사"
    )
    name = models.CharField(max_length=100, verbose_name="조직명")
    function = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="기능",
        help_text="HR, IT, Finance 등"
    )
    
    # Hierarchy
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name="상위 조직",
        db_index=True
    )
    
    # Headcount
    headcount = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="인원수"
    )
    
    # Leader Information (Embedded)
    leader_title = models.CharField(max_length=50, blank=True, verbose_name="리더 직책")
    leader_rank = models.CharField(max_length=50, blank=True, verbose_name="리더 직급")
    leader_name = models.CharField(max_length=100, blank=True, verbose_name="리더 성명")
    leader_age = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(20), MaxValueValidator(100)],
        verbose_name="리더 나이"
    )
    
    # Members Composition (JSONB)
    members = models.JSONField(
        default=list,
        blank=True,
        verbose_name="구성원",
        help_text='[{"grade": "차장", "count": 3}, {"grade": "대리", "count": 5}]'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_org_units'
    )
    
    class Meta:
        verbose_name = '조직 단위'
        verbose_name_plural = '조직 단위'
        ordering = ['company', 'name']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['reports_to']),
            models.Index(fields=['function']),
            models.Index(fields=['company', 'name']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(id=models.F('reports_to')),
                name='prevent_self_reporting'
            )
        ]
    
    def __str__(self):
        return f"{self.company} - {self.name}"
    
    def get_tree_data(self):
        """트리 구조 데이터 생성"""
        data = {
            'id': self.id,
            'data': {
                'id': self.id,
                'company': self.company,
                'name': self.name,
                'function': self.function,
                'reportsTo': self.reports_to_id,
                'headcount': self.headcount,
                'leader': {
                    'title': self.leader_title,
                    'rank': self.leader_rank,
                    'name': self.leader_name,
                    'age': self.leader_age
                } if self.leader_name else None,
                'members': self.members
            },
            'children': []
        }
        
        # Recursively add children
        for child in self.subordinates.all():
            data['children'].append(child.get_tree_data())
        
        return data
    
    def get_all_subordinates(self):
        """모든 하위 조직 반환 (재귀)"""
        subordinates = list(self.subordinates.all())
        for sub in self.subordinates.all():
            subordinates.extend(sub.get_all_subordinates())
        return subordinates
    
    def get_total_headcount(self):
        """하위 조직 포함 총 인원수"""
        total = self.headcount
        for sub in self.subordinates.all():
            total += sub.get_total_headcount()
        return total
    
    def validate_hierarchy(self):
        """순환 참조 방지 검증"""
        if not self.reports_to:
            return True
        
        parent = self.reports_to
        visited = {self.id}
        
        while parent:
            if parent.id in visited:
                return False  # Circular reference detected
            visited.add(parent.id)
            parent = parent.reports_to
        
        return True
    
    def get_depth(self):
        """조직 깊이 계산"""
        depth = 0
        parent = self.reports_to
        while parent and depth < 10:  # Max depth safety
            depth += 1
            parent = parent.reports_to
        return depth
    
    def save(self, *args, **kwargs):
        """저장 시 검증"""
        if not self.validate_hierarchy():
            raise ValueError("순환 참조가 감지되었습니다.")
        
        if self.get_depth() > 8:
            raise ValueError("조직 깊이는 최대 8단계까지만 허용됩니다.")
        
        super().save(*args, **kwargs)


class OrgScenario(models.Model):
    """
    조직 개편 시나리오 저장
    """
    scenario_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4,
        verbose_name="시나리오 ID"
    )
    name = models.CharField(max_length=200, verbose_name="시나리오명")
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='org_scenarios',
        verbose_name="작성자"
    )
    
    # Scenario Data (JSONB)
    payload = models.JSONField(
        default=list,
        verbose_name="시나리오 데이터",
        help_text="조직 단위 배열"
    )
    
    # Metadata
    description = models.TextField(blank=True, verbose_name="설명")
    tags = models.CharField(max_length=200, blank=True, verbose_name="태그")
    is_active = models.BooleanField(default=False, verbose_name="활성 시나리오")
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '조직 시나리오'
        verbose_name_plural = '조직 시나리오'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.author.username if self.author else 'Anonymous'}"
    
    def apply_scenario(self):
        """시나리오를 실제 조직에 적용"""
        with transaction.atomic():
            # Clear existing org units for the companies in scenario
            companies = set()
            for unit_data in self.payload:
                companies.add(unit_data.get('company'))
            
            if companies:
                OrgUnit.objects.filter(company__in=companies).delete()
            
            # Create new org units from scenario
            units_map = {}
            
            # First pass: Create all units without hierarchy
            for unit_data in self.payload:
                unit = OrgUnit(
                    id=unit_data['id'],
                    company=unit_data['company'],
                    name=unit_data['name'],
                    function=unit_data.get('function', ''),
                    headcount=unit_data.get('headcount', 0),
                    leader_title=unit_data.get('leader', {}).get('title', ''),
                    leader_rank=unit_data.get('leader', {}).get('rank', ''),
                    leader_name=unit_data.get('leader', {}).get('name', ''),
                    leader_age=unit_data.get('leader', {}).get('age'),
                    members=unit_data.get('members', []),
                    created_by=self.author
                )
                unit.save()
                units_map[unit.id] = unit
            
            # Second pass: Set up hierarchy
            for unit_data in self.payload:
                if unit_data.get('reportsTo'):
                    unit = units_map[unit_data['id']]
                    unit.reports_to = units_map.get(unit_data['reportsTo'])
                    unit.save()
            
            # Mark this scenario as active
            OrgScenario.objects.filter(is_active=True).update(is_active=False)
            self.is_active = True
            self.save()
            
            return True
    
    def get_diff(self, other_scenario):
        """두 시나리오 간 차이점 분석"""
        diffs = []
        
        # Convert to dict for easier comparison
        current_units = {u['id']: u for u in self.payload}
        other_units = {u['id']: u for u in other_scenario.payload}
        
        # Check for new units
        for uid, unit in other_units.items():
            if uid not in current_units:
                diffs.append({
                    'type': 'new',
                    'message': f"{unit['name']}: (신규)",
                    'unit': unit
                })
        
        # Check for deleted units
        for uid, unit in current_units.items():
            if uid not in other_units:
                diffs.append({
                    'type': 'deleted',
                    'message': f"{unit['name']}: (삭제)",
                    'unit': unit
                })
        
        # Check for changes
        for uid, unit in current_units.items():
            if uid in other_units:
                other_unit = other_units[uid]
                
                # Check reporting structure
                if unit.get('reportsTo') != other_unit.get('reportsTo'):
                    old_parent = unit.get('reportsTo', '(최상위)')
                    new_parent = other_unit.get('reportsTo', '(최상위)')
                    diffs.append({
                        'type': 'hierarchy',
                        'message': f"{unit['name']} 보고체계 변경: {old_parent} → {new_parent}",
                        'unit': unit
                    })
                
                # Check headcount
                if unit.get('headcount') != other_unit.get('headcount'):
                    diffs.append({
                        'type': 'headcount',
                        'message': f"{unit['name']} 인원: {unit.get('headcount')} → {other_unit.get('headcount')}",
                        'unit': unit
                    })
                
                # Check leader change
                old_leader = unit.get('leader', {}).get('name', '')
                new_leader = other_unit.get('leader', {}).get('name', '')
                if old_leader != new_leader:
                    diffs.append({
                        'type': 'leader',
                        'message': f"{unit['name']} 리더: {old_leader or '(없음)'} → {new_leader or '(없음)'}",
                        'unit': unit
                    })
        
        return diffs


class OrgSnapshot(models.Model):
    """
    조직 스냅샷 - 특정 시점의 조직 상태 저장
    """
    SNAPSHOT_TYPE_CHOICES = [
        ('CURRENT', '현재 상태'),
        ('WHATIF', 'What-if 분석'),
        ('BACKUP', '백업'),
        ('COMPARISON', '비교용'),
    ]
    
    snapshot_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        verbose_name="스냅샷 ID"
    )
    name = models.CharField(max_length=200, verbose_name="스냅샷명")
    snapshot_type = models.CharField(
        max_length=20,
        choices=SNAPSHOT_TYPE_CHOICES,
        default='WHATIF',
        verbose_name="스냅샷 유형"
    )
    
    # Snapshot Data
    data = models.JSONField(
        default=list,
        verbose_name="스냅샷 데이터"
    )
    
    # Related Scenario
    scenario = models.ForeignKey(
        OrgScenario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='snapshots',
        verbose_name="관련 시나리오"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="생성자"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '조직 스냅샷'
        verbose_name_plural = '조직 스냅샷'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_snapshot_type_display()})"
    
    @classmethod
    def create_from_current(cls, name, user, snapshot_type='CURRENT'):
        """현재 조직 상태로부터 스냅샷 생성"""
        units = OrgUnit.objects.all()
        data = []
        
        for unit in units:
            data.append({
                'id': unit.id,
                'company': unit.company,
                'name': unit.name,
                'function': unit.function,
                'reportsTo': unit.reports_to_id,
                'headcount': unit.headcount,
                'leader': {
                    'title': unit.leader_title,
                    'rank': unit.leader_rank,
                    'name': unit.leader_name,
                    'age': unit.leader_age
                } if unit.leader_name else None,
                'members': unit.members
            })
        
        snapshot = cls.objects.create(
            name=name,
            snapshot_type=snapshot_type,
            data=data,
            created_by=user
        )
        
        return snapshot


class OrgChangeLog(models.Model):
    """
    조직 변경 감사 로그
    """
    ACTION_CHOICES = [
        ('CREATE', '생성'),
        ('UPDATE', '수정'),
        ('DELETE', '삭제'),
        ('REORG', '재편'),
        ('IMPORT', '임포트'),
        ('EXPORT', '익스포트'),
        ('WHATIF', 'What-if 분석'),
        ('SCENARIO', '시나리오 적용'),
    ]
    
    # Action Info
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="액션"
    )
    org_unit_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="대상 조직 ID"
    )
    
    # Change Details
    changes = models.JSONField(
        default=dict,
        verbose_name="변경 내역"
    )
    
    # User Info
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="수행자"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP 주소"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = '조직 변경 로그'
        verbose_name_plural = '조직 변경 로그'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.user.username if self.user else 'System'} - {self.created_at}"