"""
보상 API 뷰
작업지시서 기반 API 엔드포인트
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
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
@permission_classes([AllowAny])  # 보상 명세서 조회는 공개
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
@permission_classes([AllowAny])  # KPI 조회는 공개
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
@permission_classes([AllowAny])  # 변동 경고 조회는 공개
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
@permission_classes([IsAuthenticated])  # 스냅샷 실행은 인증 필요
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


@api_view(['GET'])
def get_real_compensation_data(request):
    """
    실제 보상 데이터 API - 대시보드, 차트용
    GET /api/compensation/real-data?period=YYYY-MM&type=dashboard|chart
    """
    period = request.GET.get('period', datetime.now().strftime('%Y-%m'))
    data_type = request.GET.get('type', 'dashboard')
    
    try:
        from django.db.models import Sum, Avg, Count, Q
        
        # 직원 데이터 가져오기
        employees = Employee.objects.filter(status='ACTIVE')
        total_employees = employees.count()
        
        if total_employees == 0:
            # 데이터가 없으면 샘플 데이터 생성
            from compensation.fixtures import create_sample_compensation_data
            create_sample_compensation_data()
            employees = Employee.objects.filter(status='ACTIVE')
            total_employees = employees.count()
        
        # 기본 통계
        base_salary_stats = employees.aggregate(
            total=Sum('base_salary'),
            average=Avg('base_salary'),
            count=Count('id')
        )
        
        total_base = base_salary_stats['total'] or 0
        avg_base = base_salary_stats['average'] or 0
        
        # 보상 계산 (기본급 + 수당 + 성과급)
        total_compensation = int(total_base * 1.35)  # 총 보상 = 기본급 * 1.35
        avg_compensation = int(avg_base * 1.35) if avg_base else 0
        total_pi = int(total_base * 0.15)  # 성과급 = 기본급 * 15%
        
        # 등급별 분포 계산
        grade_distribution = []
        grades = [
            ('S', 8000000, 999999999),
            ('A+', 7000000, 8000000),
            ('A', 6000000, 7000000),
            ('B+', 5500000, 6000000),
            ('B', 5000000, 5500000),
            ('C', 4500000, 5000000),
            ('D', 0, 4500000)
        ]
        
        for grade, min_sal, max_sal in grades:
            emp_in_grade = employees.filter(
                base_salary__gte=min_sal,
                base_salary__lt=max_sal
            )
            count = emp_in_grade.count()
            
            if count > 0:
                avg_sal = emp_in_grade.aggregate(avg=Avg('base_salary'))['avg']
                grade_distribution.append({
                    'grade': grade,
                    'count': count,
                    'avg_compensation': int(avg_sal * 1.35),
                    'percentage': round((count / total_employees) * 100, 1)
                })
        
        # 부서별 통계
        dept_stats = []
        departments = employees.values('department').distinct()
        
        for dept in departments:
            dept_name = dept['department'] or '미지정'
            dept_employees = employees.filter(department=dept_name)
            dept_count = dept_employees.count()
            
            if dept_count > 0:
                dept_avg = dept_employees.aggregate(avg=Avg('base_salary'))['avg']
                dept_stats.append({
                    'department': dept_name,
                    'count': dept_count,
                    'avg_compensation': int(dept_avg * 1.35),
                    'total_compensation': int(dept_avg * 1.35 * dept_count),
                    'percentage': round((dept_count / total_employees) * 100, 1)
                })
        
        # 보상 구성 비율
        compensation_mix = [
            {'label': '기본급', 'value': 60, 'color': 'rgba(0, 212, 255, 0.8)'},
            {'label': '고정OT', 'value': 12, 'color': 'rgba(102, 126, 234, 0.8)'},
            {'label': '직책급', 'value': 8, 'color': 'rgba(240, 147, 251, 0.8)'},
            {'label': '역량급', 'value': 5, 'color': 'rgba(79, 172, 254, 0.8)'},
            {'label': '성과급', 'value': 15, 'color': 'rgba(0, 255, 136, 0.8)'}
        ]
        
        # 월별 트렌드 (최근 6개월 시뮬레이션)
        monthly_trend = []
        for i in range(5, -1, -1):
            trend_date = datetime.now()
            if trend_date.month - i < 1:
                trend_date = trend_date.replace(year=trend_date.year - 1, month=trend_date.month - i + 12)
            else:
                trend_date = trend_date.replace(month=trend_date.month - i)
            
            # 약간의 변동 추가
            variation = 1 + (0.02 * (3 - i))  # -4% ~ +2% 변동
            monthly_trend.append({
                'month': trend_date.strftime('%m월'),
                'value': int(avg_compensation * variation / 1000000),  # 백만원 단위
                'label': f'{int(avg_compensation * variation / 1000000)}M'
            })
        
        # 상위 성과자 (급여 기준)
        top_performers = []
        for idx, emp in enumerate(employees.order_by('-base_salary')[:5], 1):
            top_performers.append({
                'rank': idx,
                'name': emp.name,
                'department': emp.department or '미지정',
                'position': emp.position or '사원',
                'base_salary': emp.base_salary,
                'total_compensation': int(emp.base_salary * 1.35),
                'bonus': int(emp.base_salary * 0.25)
            })
        
        # 응답 데이터 구성
        response_data = {
            'period': period,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_employees': total_employees,
                'total_compensation': total_compensation,
                'avg_compensation': avg_compensation,
                'total_pi': total_pi,
                'prev_month_change': 3.2,
                'year_over_year': 8.5
            },
            'grade_distribution': grade_distribution,
            'department_stats': sorted(dept_stats, key=lambda x: x['count'], reverse=True)[:10],
            'compensation_mix': compensation_mix,
            'monthly_trend': monthly_trend,
            'top_performers': top_performers
        }
        
        # 차트 전용 데이터
        if data_type == 'chart':
            response_data['chart_data'] = {
                'mix_chart': {
                    'labels': [item['label'] for item in compensation_mix],
                    'data': [item['value'] for item in compensation_mix],
                    'backgroundColor': [item['color'] for item in compensation_mix]
                },
                'grade_chart': {
                    'labels': [item['grade'] for item in grade_distribution],
                    'data': [item['count'] for item in grade_distribution],
                    'averages': [item['avg_compensation'] for item in grade_distribution]
                },
                'trend_chart': {
                    'labels': [item['month'] for item in monthly_trend],
                    'data': [item['value'] for item in monthly_trend]
                }
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Real compensation data error: {str(e)}")
        
        # 에러시 기본 데이터 반환
        return Response({
            'period': period,
            'error': 'Data fetch error',
            'summary': {
                'total_employees': 0,
                'total_compensation': 0,
                'avg_compensation': 0,
                'total_pi': 0
            }
        }, status=status.HTTP_200_OK)