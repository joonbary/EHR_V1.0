"""
HR Dashboard API Views
OK금융그룹 인력현황 대시보드 API 엔드포인트
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import os
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)

try:
    from .models_hr import HREmployee, HRMonthlySnapshot, HRContractor, HRFileUpload
    from .services.excel_parser import HRExcelAutoParser
except ImportError as e:
    logger.error(f"Import error: {e}")
    raise


@csrf_exempt
def upload_hr_file(request):
    """HR 파일 업로드 및 자동 분류 처리"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        logger.info(f"Upload request received: {request.method}")
        logger.info(f"Files in request: {list(request.FILES.keys())}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        if 'file' not in request.FILES:
            return JsonResponse({'error': '파일이 없습니다.'}, status=400)
        
        file = request.FILES['file']
        
        # 파일 저장
        file_name = f"hr_uploads/{uuid.uuid4()}_{file.name}"
        file_path = default_storage.save(file_name, file)
        full_path = default_storage.path(file_path)
        
        # 파서 초기화 및 파일 타입 식별
        parser = HRExcelAutoParser()
        file_type = parser.identify_file_type(full_path)
        
        # 파일 업로드 기록 생성
        upload_record = HRFileUpload.objects.create(
            file_name=file.name,
            file_type=file_type,
            report_date=timezone.now().date(),
            uploaded_by=request.user if request.user.is_authenticated else None,
            processed_status='processing'
        )
        
        # 비동기 처리를 위한 백그라운드 작업 시작
        task_id = str(upload_record.id)
        
        # 동기 방식으로 처리 (간단한 구현)
        process_hr_file_sync(full_path, file_type, upload_record)
        
        return JsonResponse({
            'task_id': task_id,
            'file_type': file_type,
            'message': f'{file_type} 파일로 식별되어 처리 중입니다.'
        })
        
    except Exception as e:
        logger.error(f"파일 업로드 오류: {e}", exc_info=True)
        import traceback
        return JsonResponse({
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }, status=500)


def process_hr_file_sync(file_path, file_type, upload_record):
    """동기 파일 처리"""
    logger.info(f"파일 처리 시작: {file_path}, 타입: {file_type}")
    parser = HRExcelAutoParser()
    try:
        # 파일 파싱
        result = parser.parse_excel_file(file_path, file_type)
        logger.info(f"파싱 결과: {result.keys() if result else 'None'}")
        
        success_count = 0
        error_count = 0
        errors = []
        
        if file_type == 'domestic':
            # 국내 인력 처리
            # 신규 입사자 처리
            for hire_data in result.get('new_hires', []):
                try:
                    HREmployee.objects.update_or_create(
                        employee_no=hire_data.get('employee_no'),
                        defaults=hire_data
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"입사자 처리 오류: {e}")
            
            # 퇴사자 처리
            for resign_data in result.get('resignations', []):
                try:
                    if resign_data.get('employee_no'):
                        HREmployee.objects.filter(
                            employee_no=resign_data['employee_no']
                        ).update(
                            status='resigned',
                            resignation_date=resign_data.get('resignation_date')
                        )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"퇴사자 처리 오류: {e}")
                    
        elif file_type == 'overseas':
            # 해외 인력 처리
            for emp_data in result.get('employees', []):
                try:
                    # 기존 직원 확인 또는 생성
                    HREmployee.objects.create(
                        name=f"{emp_data['company']}_{emp_data['position']}_{success_count}",
                        company=emp_data['company'],
                        position=emp_data['position'],
                        job_level=emp_data.get('job_level'),
                        location_type='overseas',
                        country=emp_data['country'],
                        branch=emp_data['branch'],
                        status='active'
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"해외 인력 처리 오류: {e}")
                    
        elif file_type == 'contractor':
            # 외주 인력 처리
            contractors = result.get('contractors', [])
            logger.info(f"외주 인력 처리 시작: {len(contractors)}개 데이터")
            for contractor_data in contractors:
                try:
                    logger.debug(f"외주 인력 데이터: {contractor_data}")
                    # 모델에 없는 필드 제거
                    save_data = contractor_data.copy()
                    save_data.pop('company', None)
                    save_data.pop('count', None)
                    save_data.pop('period', None)
                    
                    HRContractor.objects.update_or_create(
                        contractor_name=save_data['contractor_name'],
                        vendor_company=save_data['vendor_company'],
                        project_name=save_data.get('project_name', ''),
                        defaults=save_data
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"외주 인력 처리 오류: {e}")
        
        # 업로드 기록 업데이트
        upload_record.processed_status = 'completed'
        upload_record.total_records = success_count + error_count
        upload_record.success_records = success_count
        upload_record.error_records = error_count
        upload_record.error_log = '\n'.join(errors) if errors else None
        upload_record.save()
        
    except Exception as e:
        logger.error(f"파일 처리 오류: {e}")
        upload_record.processed_status = 'failed'
        upload_record.error_log = str(e)
        upload_record.save()
    finally:
        # 임시 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)


@require_http_methods(["GET"])
def get_employees(request):
    """직원 목록 조회"""
    location_type = request.GET.get('location_type')
    company = request.GET.get('company')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 50))
    
    # 쿼리 빌드
    queryset = HREmployee.objects.filter(status='active')
    
    if location_type:
        queryset = queryset.filter(location_type=location_type)
    if company:
        queryset = queryset.filter(company=company)
    
    # 페이지네이션
    offset = (page - 1) * limit
    employees = queryset[offset:offset + limit]
    total_count = queryset.count()
    
    # 직원 데이터 직렬화
    employee_list = []
    for emp in employees:
        emp_data = {
            'id': emp.id,
            'employee_no': emp.employee_no,
            'name': emp.name,
            'company': emp.company,
            'department': emp.department,
            'position': emp.position,
            'job_level': emp.job_level,
            'location_type': emp.location_type,
            'country': emp.country,
            'hire_date': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else None,
            'status_label': '신규' if emp.hire_date and emp.hire_date > timezone.now().date() - timedelta(days=30) else '재직'
        }
        employee_list.append(emp_data)
    
    return JsonResponse({
        'data': employee_list,
        'page': page,
        'total': total_count,
        'total_pages': (total_count + limit - 1) // limit
    })


@require_http_methods(["GET"])
def get_contractors(request):
    """외주 인력 목록 조회"""
    status = request.GET.get('status', 'active')
    vendor = request.GET.get('vendor')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 50))
    
    # 쿼리 빌드
    queryset = HRContractor.objects.filter(status=status)
    
    if vendor:
        queryset = queryset.filter(vendor_company=vendor)
    
    # 페이지네이션
    offset = (page - 1) * limit
    contractors = queryset[offset:offset + limit]
    total_count = queryset.count()
    
    # 외주 인력 데이터 직렬화
    contractor_list = []
    for contractor in contractors:
        contractor_data = {
            'id': contractor.id,
            'contractor_name': contractor.contractor_name,
            'vendor_company': contractor.vendor_company,
            'project_name': contractor.project_name,
            'department': contractor.department,
            'role': contractor.role,
            'start_date': contractor.start_date.strftime('%Y-%m-%d') if contractor.start_date else None,
            'end_date': contractor.end_date.strftime('%Y-%m-%d') if contractor.end_date else None,
            'monthly_rate': float(contractor.monthly_rate) if contractor.monthly_rate else 0,
            'project_status': contractor.project_status
        }
        contractor_list.append(contractor_data)
    
    return JsonResponse({
        'data': contractor_list,
        'page': page,
        'total': total_count,
        'total_pages': (total_count + limit - 1) // limit
    })


@require_http_methods(["GET"])
def get_dashboard_summary(request):
    """대시보드 요약 데이터"""
    # 전체 통계
    domestic_count = HREmployee.objects.filter(
        location_type='domestic', 
        status='active'
    ).count()
    
    overseas_count = HREmployee.objects.filter(
        location_type='overseas', 
        status='active'
    ).count()
    
    # 최근 30일 입퇴사자
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    new_hires = HREmployee.objects.filter(
        hire_date__gte=thirty_days_ago
    ).count()
    
    resignations = HREmployee.objects.filter(
        resignation_date__gte=thirty_days_ago
    ).count()
    
    # 외주 통계
    active_contractors = HRContractor.objects.filter(
        Q(end_date__isnull=True) | Q(end_date__gte=timezone.now().date())
    )
    
    contractor_stats = active_contractors.aggregate(
        total_contractors=Count('id'),
        total_vendors=Count('vendor_company', distinct=True),
        active_projects=Count('project_name', distinct=True),
        total_monthly_cost=Sum('monthly_rate')
    )
    
    # 회사별 분포
    company_distribution = HREmployee.objects.filter(
        status='active'
    ).values('company').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return JsonResponse({
        'summary': {
            'domestic_count': domestic_count,
            'overseas_count': overseas_count,
            'new_hires': new_hires,
            'resignations': resignations,
            'total_contractors': contractor_stats['total_contractors'] or 0,
            'total_vendors': contractor_stats['total_vendors'] or 0,
            'active_projects': contractor_stats['active_projects'] or 0,
            'total_monthly_cost': float(contractor_stats['total_monthly_cost'] or 0)
        },
        'company_distribution': list(company_distribution)
    })


@require_http_methods(["GET"])
def get_monthly_trend(request):
    """월별 인력 변동 추이"""
    # 최근 12개월 데이터
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    # 월별 입사자 집계
    monthly_hires = HREmployee.objects.filter(
        hire_date__range=[start_date, end_date]
    ).extra(
        select={'month': "date_trunc('month', hire_date)"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # 월별 퇴사자 집계
    monthly_resignations = HREmployee.objects.filter(
        resignation_date__range=[start_date, end_date]
    ).extra(
        select={'month': "date_trunc('month', resignation_date)"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    return JsonResponse({
        'hires': list(monthly_hires),
        'resignations': list(monthly_resignations)
    })


@require_http_methods(["GET"])
def get_task_status(request, task_id):
    """파일 처리 상태 확인"""
    try:
        upload_record = HRFileUpload.objects.get(id=task_id)
        
        return JsonResponse({
            'task_id': task_id,
            'status': upload_record.processed_status,
            'total_records': upload_record.total_records,
            'success_records': upload_record.success_records,
            'error_records': upload_record.error_records,
            'completed': upload_record.processed_status in ['completed', 'failed']
        })
    except HRFileUpload.DoesNotExist:
        return JsonResponse({'error': '작업을 찾을 수 없습니다.'}, status=404)