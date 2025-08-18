"""
Serializers for Organization API
"""
from rest_framework import serializers
from .models_enhanced import OrgUnit, OrgScenario, OrgSnapshot, OrgChangeLog
from django.contrib.auth.models import User


class LeaderSerializer(serializers.Serializer):
    """리더 정보 시리얼라이저"""
    title = serializers.CharField(max_length=50, required=False, allow_blank=True)
    rank = serializers.CharField(max_length=50, required=False, allow_blank=True)
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    age = serializers.IntegerField(min_value=20, max_value=100, required=False, allow_null=True)


class MemberCountSerializer(serializers.Serializer):
    """구성원 수 시리얼라이저"""
    grade = serializers.CharField(max_length=50)
    count = serializers.IntegerField(min_value=0)


class OrgUnitSerializer(serializers.ModelSerializer):
    """조직 단위 시리얼라이저"""
    leader = LeaderSerializer(source='*', read_only=True)
    members = MemberCountSerializer(many=True, required=False)
    reportsTo = serializers.CharField(source='reports_to_id', required=False, allow_null=True)
    
    class Meta:
        model = OrgUnit
        fields = [
            'id', 'company', 'name', 'function', 'reportsTo',
            'headcount', 'leader', 'members'
        ]
    
    def to_representation(self, instance):
        """출력 형식 커스터마이징"""
        data = super().to_representation(instance)
        
        # Leader 정보 구조화
        if instance.leader_name:
            data['leader'] = {
                'title': instance.leader_title,
                'rank': instance.leader_rank,
                'name': instance.leader_name,
                'age': instance.leader_age
            }
        else:
            data['leader'] = None
        
        return data
    
    def create(self, validated_data):
        """조직 단위 생성"""
        # Extract leader data
        leader_data = {
            'leader_title': validated_data.pop('leader_title', ''),
            'leader_rank': validated_data.pop('leader_rank', ''),
            'leader_name': validated_data.pop('leader_name', ''),
            'leader_age': validated_data.pop('leader_age', None)
        }
        
        # Extract members data
        members_data = validated_data.pop('members', [])
        
        # Create org unit
        org_unit = OrgUnit.objects.create(
            **validated_data,
            **leader_data,
            members=members_data
        )
        
        return org_unit
    
    def update(self, instance, validated_data):
        """조직 단위 업데이트"""
        # Update leader fields
        instance.leader_title = validated_data.pop('leader_title', instance.leader_title)
        instance.leader_rank = validated_data.pop('leader_rank', instance.leader_rank)
        instance.leader_name = validated_data.pop('leader_name', instance.leader_name)
        instance.leader_age = validated_data.pop('leader_age', instance.leader_age)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class OrgTreeSerializer(serializers.Serializer):
    """조직 트리 구조 시리얼라이저"""
    id = serializers.CharField()
    data = OrgUnitSerializer()
    children = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class OrgMatrixCellSerializer(serializers.Serializer):
    """매트릭스 셀 시리얼라이저"""
    leader = serializers.CharField()
    headcount = serializers.IntegerField()
    units = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class OrgMatrixRowSerializer(serializers.Serializer):
    """매트릭스 행 시리얼라이저"""
    function = serializers.CharField()
    cells = OrgMatrixCellSerializer(many=True)


class OrgMatrixSerializer(serializers.Serializer):
    """조직 매트릭스 시리얼라이저"""
    headers = serializers.ListField(child=serializers.CharField())
    rows = OrgMatrixRowSerializer(many=True)


class OrgScenarioSerializer(serializers.ModelSerializer):
    """조직 시나리오 시리얼라이저"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = OrgScenario
        fields = [
            'scenario_id', 'name', 'author', 'author_name',
            'payload', 'description', 'tags', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['scenario_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """시나리오 생성"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class OrgSnapshotSerializer(serializers.ModelSerializer):
    """조직 스냅샷 시리얼라이저"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = OrgSnapshot
        fields = [
            'snapshot_id', 'name', 'snapshot_type', 'data',
            'scenario', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['snapshot_id', 'created_at']


class WhatIfReassignSerializer(serializers.Serializer):
    """What-if 재배치 시리얼라이저"""
    unitId = serializers.CharField()
    newReportsTo = serializers.CharField(required=False, allow_null=True)
    
    def validate(self, attrs):
        """순환 참조 및 제약 검증"""
        unit_id = attrs['unitId']
        new_reports_to = attrs.get('newReportsTo')
        
        # Check if unit exists
        try:
            unit = OrgUnit.objects.get(id=unit_id)
        except OrgUnit.DoesNotExist:
            raise serializers.ValidationError(f"조직 단위 {unit_id}를 찾을 수 없습니다.")
        
        # Check if new parent exists (if provided)
        if new_reports_to:
            try:
                parent = OrgUnit.objects.get(id=new_reports_to)
            except OrgUnit.DoesNotExist:
                raise serializers.ValidationError(f"상위 조직 {new_reports_to}를 찾을 수 없습니다.")
            
            # Check for circular reference
            if self._would_create_cycle(unit, parent):
                raise serializers.ValidationError("순환 참조가 발생합니다.")
            
            # Check depth limit
            if self._get_new_depth(unit, parent) > 8:
                raise serializers.ValidationError("조직 깊이는 최대 8단계까지만 허용됩니다.")
        
        return attrs
    
    def _would_create_cycle(self, unit, new_parent):
        """순환 참조 체크"""
        current = new_parent
        while current:
            if current.id == unit.id:
                return True
            current = current.reports_to
        return False
    
    def _get_new_depth(self, unit, new_parent):
        """새로운 깊이 계산"""
        # Calculate parent depth
        parent_depth = 0
        current = new_parent
        while current and parent_depth < 10:
            parent_depth += 1
            current = current.reports_to
        
        # Calculate unit's max child depth
        max_child_depth = self._get_max_child_depth(unit)
        
        return parent_depth + max_child_depth + 1
    
    def _get_max_child_depth(self, unit):
        """최대 하위 깊이 계산"""
        if not unit.subordinates.exists():
            return 0
        
        max_depth = 0
        for child in unit.subordinates.all():
            child_depth = 1 + self._get_max_child_depth(child)
            max_depth = max(max_depth, child_depth)
        
        return max_depth


class DiffItemSerializer(serializers.Serializer):
    """차이점 항목 시리얼라이저"""
    type = serializers.ChoiceField(choices=['new', 'deleted', 'hierarchy', 'headcount', 'leader'])
    message = serializers.CharField()
    unit = serializers.DictField()


class ExcelImportSerializer(serializers.Serializer):
    """엑셀 임포트 시리얼라이저"""
    file = serializers.FileField()
    
    def validate_file(self, value):
        """파일 형식 검증"""
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.")
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("파일 크기는 10MB를 초과할 수 없습니다.")
        
        return value


class OrgChangeLogSerializer(serializers.ModelSerializer):
    """조직 변경 로그 시리얼라이저"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = OrgChangeLog
        fields = [
            'action', 'action_display', 'org_unit_id', 'changes',
            'user', 'user_name', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['created_at']