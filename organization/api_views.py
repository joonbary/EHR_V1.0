"""
API Views for Organization Management
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.core.cache import cache
import pandas as pd
import json
import hashlib
from io import BytesIO

from .models_enhanced import OrgUnit, OrgScenario, OrgSnapshot, OrgChangeLog
from .serializers import (
    OrgUnitSerializer, OrgTreeSerializer, OrgMatrixSerializer,
    OrgScenarioSerializer, OrgSnapshotSerializer, WhatIfReassignSerializer,
    DiffItemSerializer, ExcelImportSerializer, OrgChangeLogSerializer
)


class OrgUnitViewSet(viewsets.ModelViewSet):
    """
    조직 단위 관리 ViewSet
    """
    queryset = OrgUnit.objects.all()
    serializer_class = OrgUnitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """필터링된 쿼리셋 반환"""
        queryset = super().get_queryset()
        
        # Company filter
        company = self.request.query_params.get('company', None)
        if company and company != 'ALL':
            queryset = queryset.filter(company=company)
        
        # Search filter (q parameter)
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(function__icontains=search_query) |
                Q(leader_name__icontains=search_query) |
                Q(leader_rank__icontains=search_query)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """조직 단위 목록 조회 (캐싱 적용)"""
        # Generate cache key
        company = request.query_params.get('company', 'ALL')
        q = request.query_params.get('q', '')
        cache_key = f"org:units:{hashlib.md5(f'{company}:{q}'.encode()).hexdigest()}"
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Get fresh data
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # Cache for 5 minutes
        cache.set(cache_key, serializer.data, 300)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """조직 트리 구조 조회"""
        company = request.query_params.get('company', None)
        
        # Get root units (no parent)
        roots = OrgUnit.objects.filter(reports_to__isnull=True)
        if company and company != 'ALL':
            roots = roots.filter(company=company)
        
        # Build tree structure
        tree_data = []
        for root in roots:
            tree_data.append(root.get_tree_data())
        
        return Response(tree_data)
    
    @action(detail=False, methods=['get'], url_path='group/matrix')
    def matrix(self, request):
        """기능 x 리더 매트릭스 조회"""
        company = request.query_params.get('company', None)
        
        # Get all units
        units = OrgUnit.objects.all()
        if company and company != 'ALL':
            units = units.filter(company=company)
        
        # Group by function and leader
        matrix_data = {}
        leaders = set()
        
        for unit in units:
            function = unit.function or '기타'
            leader_key = f"{unit.leader_rank} {unit.leader_name}" if unit.leader_name else '미정'
            
            if function not in matrix_data:
                matrix_data[function] = {}
            
            if leader_key not in matrix_data[function]:
                matrix_data[function][leader_key] = {
                    'headcount': 0,
                    'units': []
                }
            
            matrix_data[function][leader_key]['headcount'] += unit.headcount
            matrix_data[function][leader_key]['units'].append(unit.id)
            leaders.add(leader_key)
        
        # Format response
        headers = sorted(list(leaders))
        rows = []
        
        for function, leader_data in sorted(matrix_data.items()):
            cells = []
            for leader in headers:
                if leader in leader_data:
                    cells.append({
                        'leader': leader,
                        'headcount': leader_data[leader]['headcount'],
                        'units': leader_data[leader]['units']
                    })
                else:
                    cells.append({
                        'leader': leader,
                        'headcount': 0,
                        'units': []
                    })
            
            rows.append({
                'function': function,
                'cells': cells
            })
        
        return Response({
            'headers': headers,
            'rows': rows
        })
    
    def create(self, request, *args, **kwargs):
        """조직 단위 생성 with 로깅"""
        response = super().create(request, *args, **kwargs)
        
        # Log the action
        OrgChangeLog.objects.create(
            action='CREATE',
            org_unit_id=response.data.get('id'),
            changes=response.data,
            user=request.user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Clear cache
        cache.delete_pattern("org:units:*")
        
        return response
    
    def update(self, request, *args, **kwargs):
        """조직 단위 수정 with 로깅"""
        instance = self.get_object()
        old_data = OrgUnitSerializer(instance).data
        
        response = super().update(request, *args, **kwargs)
        
        # Log the changes
        OrgChangeLog.objects.create(
            action='UPDATE',
            org_unit_id=instance.id,
            changes={
                'old': old_data,
                'new': response.data
            },
            user=request.user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Clear cache
        cache.delete_pattern("org:units:*")
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        """조직 단위 삭제 with 로깅"""
        instance = self.get_object()
        old_data = OrgUnitSerializer(instance).data
        
        response = super().destroy(request, *args, **kwargs)
        
        # Log the deletion
        OrgChangeLog.objects.create(
            action='DELETE',
            org_unit_id=instance.id,
            changes=old_data,
            user=request.user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Clear cache
        cache.delete_pattern("org:units:*")
        
        return response
    
    def get_client_ip(self, request):
        """클라이언트 IP 주소 추출"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class OrgScenarioViewSet(viewsets.ModelViewSet):
    """
    조직 시나리오 관리 ViewSet
    """
    queryset = OrgScenario.objects.all()
    serializer_class = OrgScenarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """사용자별 시나리오 필터링"""
        queryset = super().get_queryset()
        
        # Filter by author if not admin
        if not request.user.is_staff:
            queryset = queryset.filter(author=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """시나리오 적용"""
        scenario = self.get_object()
        
        try:
            with transaction.atomic():
                scenario.apply_scenario()
                
                # Log the action
                OrgChangeLog.objects.create(
                    action='SCENARIO',
                    changes={
                        'scenario_id': str(scenario.scenario_id),
                        'scenario_name': scenario.name
                    },
                    user=request.user,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Clear cache
                cache.delete_pattern("org:units:*")
                
                return Response({
                    'status': 'success',
                    'message': f'시나리오 "{scenario.name}"가 적용되었습니다.'
                })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def diff(self, request):
        """두 시나리오 간 차이점 분석"""
        scenario_a_id = request.data.get('scenario_a')
        scenario_b_id = request.data.get('scenario_b')
        
        if not scenario_a_id or not scenario_b_id:
            return Response({
                'error': '두 시나리오 ID가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            scenario_a = OrgScenario.objects.get(scenario_id=scenario_a_id)
            scenario_b = OrgScenario.objects.get(scenario_id=scenario_b_id)
            
            diffs = scenario_a.get_diff(scenario_b)
            serializer = DiffItemSerializer(diffs, many=True)
            
            return Response(serializer.data)
        except OrgScenario.DoesNotExist:
            return Response({
                'error': '시나리오를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def get_client_ip(self, request):
        """클라이언트 IP 주소 추출"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class WhatIfAnalysisViewSet(viewsets.ViewSet):
    """
    What-if 분석 ViewSet
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='reassign')
    def reassign(self, request):
        """조직 재배치 시뮬레이션"""
        serializer = WhatIfReassignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        unit_id = serializer.validated_data['unitId']
        new_reports_to = serializer.validated_data.get('newReportsTo')
        
        # Create snapshot of current state
        current_snapshot = OrgSnapshot.create_from_current(
            name=f"What-if: {unit_id} reassignment",
            user=request.user,
            snapshot_type='WHATIF'
        )
        
        # Apply change to snapshot data
        snapshot_data = current_snapshot.data.copy()
        for unit_data in snapshot_data:
            if unit_data['id'] == unit_id:
                unit_data['reportsTo'] = new_reports_to
                break
        
        # Log the what-if analysis
        OrgChangeLog.objects.create(
            action='WHATIF',
            org_unit_id=unit_id,
            changes={
                'unit_id': unit_id,
                'old_reports_to': OrgUnit.objects.get(id=unit_id).reports_to_id,
                'new_reports_to': new_reports_to
            },
            user=request.user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'snapshot_id': str(current_snapshot.snapshot_id),
            'data': snapshot_data
        })
    
    def get_client_ip(self, request):
        """클라이언트 IP 주소 추출"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ExcelIOViewSet(viewsets.ViewSet):
    """
    엑셀 Import/Export ViewSet
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='import')
    def import_excel(self, request):
        """엑셀 파일 임포트"""
        serializer = ExcelImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = serializer.validated_data['file']
        
        try:
            # Read Excel file
            df = pd.read_excel(file)
            
            # Validate required columns
            required_columns = ['id', 'company', 'name', 'function', 'headcount']
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                return Response({
                    'error': f'필수 컬럼이 누락되었습니다: {", ".join(missing_columns)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process data
            with transaction.atomic():
                created_count = 0
                updated_count = 0
                errors = []
                
                for index, row in df.iterrows():
                    try:
                        # Parse members JSON if exists
                        members = []
                        if 'members_json' in row and pd.notna(row['members_json']):
                            try:
                                members = json.loads(row['members_json'])
                            except json.JSONDecodeError:
                                members = []
                        
                        # Prepare data
                        unit_data = {
                            'id': str(row['id']),
                            'company': row['company'],
                            'name': row['name'],
                            'function': row.get('function', ''),
                            'headcount': int(row.get('headcount', 0)),
                            'leader_title': row.get('leader_title', ''),
                            'leader_rank': row.get('leader_rank', ''),
                            'leader_name': row.get('leader_name', ''),
                            'leader_age': int(row['leader_age']) if pd.notna(row.get('leader_age')) else None,
                            'members': members
                        }
                        
                        # Check if reports_to exists
                        if pd.notna(row.get('reports_to')):
                            unit_data['reports_to_id'] = str(row['reports_to'])
                        
                        # Create or update
                        unit, created = OrgUnit.objects.update_or_create(
                            id=unit_data['id'],
                            defaults=unit_data
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    
                    except Exception as e:
                        errors.append(f"Row {index + 2}: {str(e)}")
                
                # Log the import
                OrgChangeLog.objects.create(
                    action='IMPORT',
                    changes={
                        'filename': file.name,
                        'created': created_count,
                        'updated': updated_count,
                        'errors': errors
                    },
                    user=request.user,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Clear cache
                cache.delete_pattern("org:units:*")
                
                return Response({
                    'status': 'success',
                    'created': created_count,
                    'updated': updated_count,
                    'errors': errors
                })
        
        except Exception as e:
            return Response({
                'error': f'파일 처리 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='export')
    def export_excel(self, request):
        """엑셀 파일 익스포트"""
        # Get filtered units
        company = request.query_params.get('company', None)
        units = OrgUnit.objects.all()
        if company and company != 'ALL':
            units = units.filter(company=company)
        
        # Create DataFrame
        data = []
        for unit in units:
            data.append({
                'id': unit.id,
                'company': unit.company,
                'name': unit.name,
                'function': unit.function,
                'reports_to': unit.reports_to_id,
                'leader_title': unit.leader_title,
                'leader_rank': unit.leader_rank,
                'leader_name': unit.leader_name,
                'leader_age': unit.leader_age,
                'headcount': unit.headcount,
                'members_json': json.dumps(unit.members, ensure_ascii=False)
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='조직도', index=False)
        
        output.seek(0)
        
        # Log the export
        OrgChangeLog.objects.create(
            action='EXPORT',
            changes={
                'company': company or 'ALL',
                'count': len(data)
            },
            user=request.user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return file
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=organization_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return response
    
    def get_client_ip(self, request):
        """클라이언트 IP 주소 추출"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip