"""
보상 API 뷰
작업지시서 기반 API 엔드포인트
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models import Q, Avg
from datetime import datetime, date
import logging

from employees.models import Employee
from compensation.services import CompensationCalculationService, CompensationReportService
from compensation.models_enhanced import (
    CompensationSnapshot, EmployeeCompensationProfile,
    PositionAllowanceTable, PositionMaster
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_compensation_statement(request, employee_id):
    """
    직원 보상 명세서 조회
    GET /api/comp/employee/{id}/statement?period=YYYY-MM
    """
    pay_period = request.GET.get('period')
    
    if not pay_period:
        # 기본값: 현재 월
        pay_period = datetime.now().strftime('%Y-%m')
    
    # 형식 검증
    try:
        year, month = map(int, pay_period.split('-'))
        if not (1 <= month <= 12):
            raise ValueError("Invalid month")
    except (ValueError, AttributeError):
        return Response(
            {'error': 'Invalid period format. Use YYYY-MM'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    service = CompensationReportService()
    statement = service.get_compensation_statement(employee_id, pay_period)
    
    if not statement:
        # 스냅샷이 없으면 계산 실행
        try:
            calc_service = CompensationCalculationService()
            calc_service.calculate_monthly_compensation(employee_id, pay_period)
            statement = service.get_compensation_statement(employee_id, pay_period)
        except Exception as e:
            logger.error(f"Failed to calculate compensation: {str(e)}")
            return Response(
                {'error': f'Failed to calculate compensation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(statement, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_compensation_mix_ratio(request):
    """
    보상 구성 비율 KPI
    GET /api/comp/kpi/mix-ratio?period=YYYY-MM
    """
    pay_period = request.GET.get('period')
    
    if not pay_period:
        pay_period = datetime.now().strftime('%Y-%m')
    
    service = CompensationReportService()
    mix_ratio = service.get_compensation_mix_ratio(pay_period)
    
    return Response({
        'period': pay_period,
        'mix_ratio': mix_ratio
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_variance_alerts(request):
    """
    보상 변동 경고 조회
    GET /api/comp/kpi/variance-alerts?period=YYYY-MM&threshold=0.2
    """
    pay_period = request.GET.get('period')
    threshold = float(request.GET.get('threshold', 0.2))
    
    if not pay_period:
        pay_period = datetime.now().strftime('%Y-%m')
    
    service = CompensationReportService()
    alerts = service.get_variance_alerts(pay_period, threshold)
    
    return Response({
        'period': pay_period,
        'threshold': threshold,
        'alerts': alerts,
        'alert_count': len(alerts)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def run_compensation_snapshot(request):
    """
    보상 계산 엔진 실행
    POST /api/comp/snapshot/run
    {
        "period": "YYYY-MM",
        "employee_ids": [1, 2, 3]  // optional, 없으면 전체
    }
    """
    pay_period = request.data.get('period')
    employee_ids = request.data.get('employee_ids')
    
    if not pay_period:
        return Response(
            {'error': 'Period is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        service = CompensationCalculationService()
        run_log = service.run_monthly_calculation(pay_period, employee_ids)
        
        return Response({
            'run_id': run_log.run_id,
            'status': run_log.status,
            'affected_count': run_log.affected_count,
            'errors': run_log.errors,
            'message': f'Compensation calculation {"completed" if run_log.status == "completed" else "completed with errors"}'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Snapshot run failed: {str(e)}")
        return Response(
            {'error': f'Calculation failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_position_allowance(request):
    """
    직책급 조회
    GET /api/positions/allowance?position_code=POS01&tier=A
    """
    position_code = request.GET.get('position_code')
    tier = request.GET.get('tier', 'B')
    
    if not position_code:
        return Response(
            {'error': 'Position code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        position = PositionMaster.objects.get(position_code=position_code)
        
        allowance = PositionAllowanceTable.objects.filter(
            position_code=position,
            allowance_tier=tier
        ).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gte=date.today())
        ).first()
        
        if not allowance:
            # 영업조직은 N/A tier
            allowance = PositionAllowanceTable.objects.filter(
                position_code=position,
                allowance_tier='N/A'
            ).filter(
                Q(valid_to__isnull=True) | Q(valid_to__gte=date.today())
            ).first()
        
        if allowance:
            return Response({
                'position_code': position_code,
                'position_name': position.position_name,
                'tier': allowance.allowance_tier,
                'monthly_amount': float(allowance.monthly_amount),
                'allowance_rate': float(allowance.allowance_rate),
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Position allowance not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except PositionMaster.DoesNotExist:
        return Response(
            {'error': 'Position not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def assign_employee_position(request, employee_id):
    """
    직원 직책 배정
    POST /api/employees/{id}/position/assign
    {
        "position_code": "POS01",
        "position_tier": "A",
        "is_initial": true
    }
    """
    employee = get_object_or_404(Employee, id=employee_id)
    
    position_code = request.data.get('position_code')
    position_tier = request.data.get('position_tier', 'B')
    is_initial = request.data.get('is_initial', False)
    
    if not position_code:
        return Response(
            {'error': 'Position code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        position = PositionMaster.objects.get(position_code=position_code)
        
        # 프로파일 생성/업데이트
        profile, created = EmployeeCompensationProfile.objects.get_or_create(
            employee=employee,
            defaults={
                'grade_code_id': 'GRD11',  # 기본값
                'job_profile_id_id': 'JP001',  # 기본값
                'competency_tier': 'T3',
            }
        )
        
        profile.position_code = position
        profile.position_tier = position_tier
        profile.is_initial_position = is_initial
        
        if is_initial:
            profile.position_start_date = date.today()
        
        profile.save()
        
        return Response({
            'employee_id': employee_id,
            'employee_name': employee.name,
            'position_code': position_code,
            'position_name': position.position_name,
            'position_tier': position_tier,
            'is_initial': is_initial,
            'message': 'Position assigned successfully'
        }, status=status.HTTP_200_OK)
        
    except PositionMaster.DoesNotExist:
        return Response(
            {'error': 'Position not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Position assignment failed: {str(e)}")
        return Response(
            {'error': f'Assignment failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_compensation_dashboard(request):
    """
    보상 대시보드 데이터
    GET /api/comp/dashboard?period=YYYY-MM
    """
    pay_period = request.GET.get('period')
    
    if not pay_period:
        pay_period = datetime.now().strftime('%Y-%m')
    
    try:
        # 스냅샷 통계
        snapshots = CompensationSnapshot.objects.filter(pay_period=pay_period)
        total_count = snapshots.count()
        
        if total_count == 0:
            return Response({
                'period': pay_period,
                'message': 'No compensation data for this period',
                'stats': {}
            }, status=status.HTTP_200_OK)
        
        # 고용형태별 통계
        employment_stats = {}
        for emp_type in ['정규직', 'Non-PL', 'PL', '별정직']:
            type_snapshots = snapshots.filter(employee__employment_type=emp_type)
            if type_snapshots.exists():
                employment_stats[emp_type] = {
                    'count': type_snapshots.count(),
                    'avg_total': float(
                        type_snapshots.aggregate(
                            avg=models.Avg('base_salary') + 
                            models.Avg('fixed_ot') + 
                            models.Avg('position_allowance') +
                            models.Avg('competency_allowance')
                        )['avg'] or 0
                    ),
                }
        
        # KPI
        service = CompensationReportService()
        mix_ratio = service.get_compensation_mix_ratio(pay_period)
        alerts = service.get_variance_alerts(pay_period)
        
        return Response({
            'period': pay_period,
            'stats': {
                'total_employees': total_count,
                'employment_types': employment_stats,
                'mix_ratio': mix_ratio,
                'variance_alert_count': len(alerts),
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Dashboard data fetch failed: {str(e)}")
        return Response(
            {'error': f'Failed to fetch dashboard data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )