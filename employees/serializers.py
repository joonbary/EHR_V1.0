from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']
        read_only_fields = ['id']


class EmployeeListSerializer(serializers.ModelSerializer):
    """직원 목록 조회용 시리얼라이저 (최소 정보)"""
    manager_name = serializers.CharField(source='manager.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    full_position = serializers.CharField(source='get_full_position', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'email', 'department', 'position', 'new_position',
            'job_group', 'job_type', 'job_role', 'growth_level', 'employment_status',
            'hire_date', 'phone', 'manager_name', 'user_username', 'full_position'
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """직원 상세 조회용 시리얼라이저 (전체 정보)"""
    user = UserSerializer(read_only=True)
    manager = EmployeeListSerializer(read_only=True)
    subordinates = EmployeeListSerializer(many=True, read_only=True, source='get_subordinates')
    is_manager_flag = serializers.BooleanField(source='is_manager', read_only=True)
    full_position = serializers.CharField(source='get_full_position', read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """직원 등록용 시리얼라이저"""
    user_id = serializers.IntegerField(required=False, allow_null=True)
    manager_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Employee
        fields = [
            'name', 'email', 'department', 'position', 'new_position',
            'job_group', 'job_type', 'job_role', 'growth_level', 'grade_level',
            'employment_type', 'employment_status', 'hire_date', 'phone',
            'address', 'emergency_contact', 'emergency_phone', 
            'user_id', 'manager_id'
        ]
    
    def validate_email(self, value):
        """이메일 중복 검증"""
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 등록된 이메일입니다.")
        return value
    
    def validate_user_id(self, value):
        """사용자 ID 검증"""
        if value and not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")
        return value
    
    def validate_manager_id(self, value):
        """관리자 ID 검증"""
        if value and not Employee.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 관리자입니다.")
        return value
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        manager_id = validated_data.pop('manager_id', None)
        
        employee = Employee.objects.create(**validated_data)
        
        if user_id:
            employee.user_id = user_id
        if manager_id:
            employee.manager_id = manager_id
        
        employee.save()
        return employee


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """직원 정보 수정용 시리얼라이저"""
    user_id = serializers.IntegerField(required=False, allow_null=True)
    manager_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Employee
        fields = [
            'name', 'email', 'department', 'position', 'new_position',
            'job_group', 'job_type', 'job_role', 'growth_level', 'grade_level',
            'employment_type', 'employment_status', 'phone',
            'address', 'emergency_contact', 'emergency_phone', 
            'user_id', 'manager_id'
        ]
    
    def validate_email(self, value):
        """이메일 중복 검증 (자신 제외)"""
        if Employee.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("이미 등록된 이메일입니다.")
        return value
    
    def validate_user_id(self, value):
        """사용자 ID 검증"""
        if value and not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")
        return value
    
    def validate_manager_id(self, value):
        """관리자 ID 검증 (자기 자신을 관리자로 설정 불가)"""
        if value:
            if value == self.instance.id:
                raise serializers.ValidationError("자기 자신을 관리자로 설정할 수 없습니다.")
            if not Employee.objects.filter(id=value).exists():
                raise serializers.ValidationError("존재하지 않는 관리자입니다.")
        return value
    
    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id', None)
        manager_id = validated_data.pop('manager_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if user_id is not None:
            instance.user_id = user_id
        if manager_id is not None:
            instance.manager_id = manager_id
        
        instance.save()
        return instance


class EmployeeRetireSerializer(serializers.ModelSerializer):
    """직원 퇴사 처리용 시리얼라이저"""
    retire_date = serializers.DateField(required=False)
    retire_reason = serializers.CharField(max_length=200, required=False)
    
    class Meta:
        model = Employee
        fields = ['employment_status', 'retire_date', 'retire_reason']
    
    def validate_employment_status(self, value):
        """퇴사 상태만 허용"""
        if value not in ['퇴직']:
            raise serializers.ValidationError("퇴사 처리는 '퇴직' 상태만 가능합니다.")
        return value
    
    def update(self, instance, validated_data):
        instance.employment_status = '퇴직'
        instance.save()
        return instance