from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Employee
from .serializers import (
    EmployeeListSerializer, EmployeeDetailSerializer, 
    EmployeeCreateSerializer, EmployeeUpdateSerializer, EmployeeRetireSerializer
)


class ReadOnlyOrAuthenticated(BasePermission):
    """
    읽기는 모든 사용자에게 허용, 쓰기는 인증된 사용자만 허용
    """
    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS 요청은 모든 사용자에게 허용
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # 그 외의 요청(POST, PUT, DELETE 등)은 인증된 사용자만 허용
        return request.user and request.user.is_authenticated


class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    """
    직원 목록 조회 및 신규 직원 등록 API
    GET /api/employees/ - 직원 목록 조회 (필터링 지원)
    POST /api/employees/ - 신규 직원 등록
    """
    queryset = Employee.objects.all()
    permission_classes = [ReadOnlyOrAuthenticated]  # 읽기는 모든 사용자, 쓰기는 인증된 사용자만
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'department': ['exact', 'icontains'],
        'position': ['exact', 'icontains'],
        'new_position': ['exact', 'icontains'],
        'job_group': ['exact'],
        'job_type': ['exact', 'icontains'],
        'employment_status': ['exact'],
        'employment_type': ['exact'],
        'growth_level': ['exact', 'gte', 'lte'],
        'hire_date': ['exact', 'gte', 'lte'],
    }
    search_fields = ['name', 'email', 'job_role', 'phone']
    ordering_fields = ['name', 'hire_date', 'growth_level', 'department']
    ordering = ['department', 'growth_level', 'name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateSerializer
        return EmployeeListSerializer
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            
            # 재직자만 조회 (쿼리 파라미터로 제어 가능)
            if self.request.query_params.get('include_retired') != 'true':
                queryset = queryset.filter(employment_status__in=['재직', '휴직', '파견'])
            
            # 검색어 처리 (search 파라미터)
            search = self.request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(employee_id__icontains=search) |
                    Q(department__icontains=search)
                )
            
            # 고용형태 필터링 (employment_type 파라미터)
            employment_type = self.request.query_params.get('employment_type')
            if employment_type and employment_type != '':
                # Non-PL, PL 등의 값을 정확히 매칭
                queryset = queryset.filter(employment_type__iexact=employment_type)
            
            # 부서별 필터링
            department = self.request.query_params.get('department')
            if department:
                queryset = queryset.filter(department=department)
            
            # 직급별 필터링
            position = self.request.query_params.get('position')
            if position:
                queryset = queryset.filter(new_position=position)
            
            # 관리자별 부하직원 조회
            manager_id = self.request.query_params.get('manager_id')
            if manager_id:
                queryset = queryset.filter(manager_id=manager_id)
            
            return queryset
        except Exception as e:
            # 에러 발생 시 빈 쿼리셋 반환
            print(f"Error in get_queryset: {str(e)}")
            return Employee.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            # results 키로 감싸서 반환 (프론트엔드 호환성)
            return Response({'results': serializer.data})
        except Exception as e:
            # 에러 발생 시 빈 결과 반환
            print(f"Error in list: {str(e)}")
            return Response({'results': [], 'error': str(e)}, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        
        # 생성된 직원 정보를 상세 시리얼라이저로 반환
        detail_serializer = EmployeeDetailSerializer(employee)
        
        return Response(
            {
                'message': '직원이 성공적으로 등록되었습니다.',
                'data': detail_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class EmployeeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    직원 상세 조회/수정/삭제 API
    GET /api/employees/{id}/ - 직원 상세 조회
    PUT /api/employees/{id}/ - 직원 정보 수정
    PATCH /api/employees/{id}/ - 직원 정보 부분 수정
    DELETE /api/employees/{id}/ - 직원 삭제 (실제로는 비활성화)
    """
    queryset = Employee.objects.all()
    permission_classes = [ReadOnlyOrAuthenticated]  # 읽기는 모든 사용자, 쓰기는 인증된 사용자만
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeUpdateSerializer
        return EmployeeDetailSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        
        # 수정된 직원 정보를 상세 시리얼라이저로 반환
        detail_serializer = EmployeeDetailSerializer(employee)
        
        return Response({
            'message': '직원 정보가 성공적으로 수정되었습니다.',
            'data': detail_serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """직원 삭제 대신 비활성화 처리"""
        instance = self.get_object()
        instance.employment_status = '퇴직'
        instance.save()
        
        return Response({
            'message': '직원이 성공적으로 퇴사 처리되었습니다.',
            'employee_id': instance.id,
            'name': instance.name
        }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])  # 퇴사 처리는 인증된 사용자만
def employee_retire_view(request, pk):
    """
    직원 퇴사 처리 API
    PATCH /api/employees/{id}/retire/
    """
    employee = get_object_or_404(Employee, pk=pk)
    
    if employee.employment_status == '퇴직':
        return Response({
            'error': '이미 퇴사 처리된 직원입니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = EmployeeRetireSerializer(employee, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response({
        'message': f'{employee.name} 직원이 성공적으로 퇴사 처리되었습니다.',
        'employee_id': employee.id,
        'name': employee.name,
        'employment_status': employee.employment_status
    })


@api_view(['GET'])
@permission_classes([AllowAny])  # 통계는 모든 사용자에게 공개
def employee_statistics_view(request):
    """
    직원 통계 정보 API
    GET /api/employees/statistics/
    """
    from django.db.models import Count
    
    # 기본 통계
    total_employees = Employee.objects.filter(employment_status__in=['재직', '휴직', '파견']).count()
    active_employees = Employee.objects.filter(employment_status='재직').count()
    retired_employees = Employee.objects.filter(employment_status='퇴직').count()
    
    # 부서별 통계
    department_stats = Employee.objects.filter(
        employment_status__in=['재직', '휴직', '파견']
    ).values('department').annotate(count=Count('id')).order_by('-count')
    
    # 직급별 통계
    position_stats = Employee.objects.filter(
        employment_status__in=['재직', '휴직', '파견']
    ).values('new_position').annotate(count=Count('id')).order_by('-count')
    
    # 성장레벨별 통계
    growth_level_stats = Employee.objects.filter(
        employment_status__in=['재직', '휴직', '파견']
    ).values('growth_level').annotate(count=Count('id')).order_by('growth_level')
    
    # 직군별 통계
    job_group_stats = Employee.objects.filter(
        employment_status__in=['재직', '휴직', '파견']
    ).values('job_group').annotate(count=Count('id'))
    
    return Response({
        'summary': {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'retired_employees': retired_employees,
        },
        'department_distribution': list(department_stats),
        'position_distribution': list(position_stats),
        'growth_level_distribution': list(growth_level_stats),
        'job_group_distribution': list(job_group_stats),
    })


@api_view(['GET'])
@permission_classes([AllowAny])  # 관리자 목록은 모든 사용자에게 공개
def employee_managers_view(request):
    """
    관리자 목록 API (직원 등록/수정 시 사용)
    GET /api/employees/managers/
    """
    managers = Employee.objects.filter(
        employment_status='재직'
    ).filter(
        # 부하직원이 있거나 관리직급인 경우
        Q(subordinates__isnull=False) | 
        Q(new_position__in=['과장', '차장', '부부장', '부장', '팀장', '지점장', '본부장'])
    ).distinct().order_by('department', 'growth_level')
    
    serializer = EmployeeListSerializer(managers, many=True)
    return Response({
        'managers': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])  # 조직도는 모든 사용자에게 공개
def employee_organization_tree_view(request):
    """
    조직도 트리 구조 API
    GET /api/employees/organization-tree/
    """
    def build_tree(manager_id=None):
        employees = Employee.objects.filter(
            manager_id=manager_id,
            employment_status='재직'
        ).select_related('user').order_by('growth_level', 'name')
        
        tree = []
        for employee in employees:
            node = {
                'id': employee.id,
                'name': employee.name,
                'position': employee.new_position,
                'job_type': employee.job_type,
                'growth_level': employee.growth_level,
                'department': employee.department,
                'email': employee.email,
                'children': build_tree(employee.id)
            }
            tree.append(node)
        return tree
    
    # 최상위 관리자들부터 시작 (manager가 없는 직원들)
    organization_tree = build_tree(None)
    
    return Response({
        'organization_tree': organization_tree
    })