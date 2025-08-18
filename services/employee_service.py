"""
직원 관리 서비스
"""
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django.contrib.auth.models import User
from datetime import date
import logging

from employees.models import Employee
from core.exceptions import ValidationError, EmployeeNotFoundError
from core.validators import HRValidators
from core.utils import StringUtils, QueryUtils
from core.mcp import MCPFileService, MCPTaskService


logger = logging.getLogger(__name__)


class EmployeeService:
    """직원 관리 비즈니스 로직"""
    
    def __init__(self):
        self.validator = HRValidators()
        self.file_service = MCPFileService()
        self.task_service = MCPTaskService()
    
    @transaction.atomic
    def create_employee(self, data: Dict) -> Employee:
        """직원 생성"""
        try:
            # 데이터 검증
            validated_data = self.validator.validate_employee_data(data)
            
            # 사용자 계정 생성
            user = self._create_user_account(validated_data)
            
            # 직원 번호 생성
            employee_number = StringUtils.generate_employee_number()
            
            # 직원 정보 생성
            employee = Employee.objects.create(
                user=user,
                employee_number=employee_number,
                name=validated_data['name'],
                email=validated_data['email'],
                department=validated_data['department'],
                position=validated_data['position'],
                phone=validated_data.get('phone', ''),
                address=validated_data.get('address', ''),
                hire_date=validated_data.get('hire_date', date.today()),
                job_family=validated_data.get('job_family', 'PL'),
                job_category=validated_data.get('job_category', ''),
                growth_level=validated_data.get('growth_level', 'Level_1')
            )
            
            logger.info(f"Employee created: {employee.employee_number}")
            return employee
            
        except Exception as e:
            logger.error(f"Employee creation failed: {str(e)}")
            raise
    
    def _create_user_account(self, data: Dict) -> User:
        """사용자 계정 생성"""
        username = data['email'].split('@')[0]
        
        # 중복 확인
        if User.objects.filter(username=username).exists():
            username = f"{username}_{StringUtils.generate_hash(data['email'])[:6]}"
        
        user = User.objects.create_user(
            username=username,
            email=data['email'],
            first_name=data['name'].split()[0] if ' ' in data['name'] else data['name'],
            last_name=data['name'].split()[-1] if ' ' in data['name'] else ''
        )
        
        # 임시 비밀번호 설정
        temp_password = StringUtils.generate_hash(username)[:12]
        user.set_password(temp_password)
        user.save()
        
        return user
    
    @transaction.atomic
    def update_employee(self, employee_id: int, data: Dict) -> Employee:
        """직원 정보 수정"""
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # 수정 가능한 필드만 업데이트
            updatable_fields = [
                'phone', 'email', 'address', 'emergency_contact',
                'emergency_phone', 'department', 'position',
                'job_category', 'growth_level'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(employee, field, data[field])
            
            # 이메일 변경 시 검증
            if 'email' in data:
                data['email'] = self.validator.validate_email(data['email'])
                employee.email = data['email']
                employee.user.email = data['email']
                employee.user.save()
            
            employee.save()
            
            logger.info(f"Employee updated: {employee.employee_number}")
            return employee
            
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"직원 ID {employee_id}를 찾을 수 없습니다.")
    
    def process_profile_image(self, employee_id: int, image_file) -> str:
        """프로필 이미지 처리"""
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # 기존 이미지 삭제
            if employee.profile_image:
                self.file_service.delete_file(employee.profile_image.name)
            
            # 새 이미지 처리
            image_path = self.file_service.process_profile_image(
                image_file,
                employee.employee_number
            )
            
            # 직원 정보 업데이트
            employee.profile_image = image_path
            employee.save()
            
            return image_path
            
        except Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"직원 ID {employee_id}를 찾을 수 없습니다.")
    
    def bulk_import_employees(self, file_path: str) -> Dict:
        """직원 대량 등록"""
        # 비동기 작업으로 처리
        task_id = self.task_service.submit_task(
            'bulk_import',
            {
                'file_path': file_path,
                'import_type': 'employees'
            }
        )
        
        return {
            'task_id': task_id,
            'message': '직원 대량 등록 작업이 시작되었습니다.'
        }
    
    def get_employee_statistics(self, department: Optional[str] = None) -> Dict:
        """직원 통계 조회"""
        queryset = Employee.objects.filter(is_active=True)
        
        if department:
            queryset = queryset.filter(department=department)
        
        total_count = queryset.count()
        
        # 부서별 통계
        department_stats = dict(
            queryset.values_list('department').annotate(
                count=models.Count('id')
            )
        )
        
        # 직급별 통계
        position_stats = dict(
            queryset.values_list('position').annotate(
                count=models.Count('id')
            )
        )
        
        # 성장레벨별 통계
        level_stats = dict(
            queryset.values_list('growth_level').annotate(
                count=models.Count('id')
            )
        )
        
        return {
            'total_count': total_count,
            'department_stats': department_stats,
            'position_stats': position_stats,
            'level_stats': level_stats,
            'new_hires_this_month': queryset.filter(
                hire_date__gte=date.today().replace(day=1)
            ).count()
        }
    
    def search_employees(
        self,
        query: str = None,
        department: str = None,
        position: str = None,
        growth_level: str = None
    ) -> List[Employee]:
        """직원 검색"""
        queryset = Employee.objects.filter(is_active=True)
        
        if query:
            queryset = queryset.filter(
                models.Q(name__icontains=query) |
                models.Q(employee_number__icontains=query) |
                models.Q(email__icontains=query)
            )
        
        if department:
            queryset = queryset.filter(department=department)
        
        if position:
            queryset = queryset.filter(position=position)
        
        if growth_level:
            queryset = queryset.filter(growth_level=growth_level)
        
        return queryset.select_related('user').order_by('name')
    
    def get_organizational_chart(self, department: Optional[str] = None) -> List[Dict]:
        """조직도 데이터 생성"""
        queryset = Employee.objects.filter(is_active=True)
        
        if department:
            queryset = queryset.filter(department=department)
        
        # 계층 구조 생성
        org_data = []
        
        # 부서장 찾기
        managers = queryset.filter(
            models.Q(position__icontains='부서장') |
            models.Q(position__icontains='팀장')
        )
        
        for manager in managers:
            node = {
                'id': manager.id,
                'name': manager.name,
                'position': manager.position,
                'department': manager.department,
                'children': []
            }
            
            # 부하직원 찾기
            subordinates = queryset.filter(manager=manager)
            for subordinate in subordinates:
                node['children'].append({
                    'id': subordinate.id,
                    'name': subordinate.name,
                    'position': subordinate.position
                })
            
            org_data.append(node)
        
        return org_data
    
    def export_employee_data(self, filters: Dict = None) -> str:
        """직원 데이터 내보내기"""
        # 데이터 조회
        queryset = self.search_employees(**filters) if filters else Employee.objects.all()
        
        # 데이터 준비
        data = []
        for emp in queryset:
            data.append({
                '사번': emp.employee_number,
                '이름': emp.name,
                '이메일': emp.email,
                '부서': emp.department,
                '직급': emp.position,
                '직군': emp.get_job_family_display(),
                '성장레벨': emp.get_growth_level_display(),
                '입사일': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else '',
                '전화번호': emp.phone,
                '주소': emp.address
            })
        
        # Excel 파일 생성
        file_path = self.file_service.generate_excel_export(
            data,
            'employee_list.xlsx',
            sheet_name='직원목록'
        )
        
        return file_path