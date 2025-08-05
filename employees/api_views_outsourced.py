"""
외주인력 현황관리 API Views
계열사별 상주/비상주 외주인력 현황 관리
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.db import models
from django.db.models import Sum, Count, Q, F, Max
from django.utils import timezone
from datetime import datetime, timedelta
import json
import os
import uuid
import logging

logger = logging.getLogger(__name__)

try:
    from .models_hr import OutsourcedStaff, HRFileUpload
    from .services.excel_parser import HRExcelAutoParser
except ImportError as e:
    logger.error(f"Import error: {e}")
    raise


@csrf_exempt
def upload_outsourced_file(request):
    """외주인력 현황 파일 업로드"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': '파일이 없습니다.'}, status=400)
        
        file = request.FILES['file']
        
        # 파일 저장
        file_name = f"outsourced/{uuid.uuid4()}_{file.name}"
        file_path = default_storage.save(file_name, file)
        full_path = default_storage.path(file_path)
        
        # 파서 초기화
        parser = HRExcelAutoParser()
        
        # 파일 업로드 기록 생성
        upload_record = HRFileUpload.objects.create(
            file_name=file.name,
            file_type='outsourced_staff',
            report_date=timezone.now().date(),
            uploaded_by=request.user if request.user.is_authenticated else None,
            processed_status='processing'
        )
        
        # 파싱 및 저장
        result = parser.parse_outsourced_staff(full_path)
        
        logger.info(f"파싱 결과: {len(result)}개 항목")
        
        success_count = 0
        error_count = 0
        errors = []
        
        for idx, staff_data in enumerate(result):
            try:
                logger.debug(f"처리 중 [{idx+1}/{len(result)}]: {staff_data}")
                
                # 기존 레코드 확인 - staff_type도 포함
                existing = OutsourcedStaff.objects.filter(
                    company_name=staff_data['company_name'],
                    project_name=staff_data['project_name'],
                    report_date=staff_data['report_date'],
                    staff_type=staff_data['staff_type']
                ).first()
                
                if existing:
                    # 업데이트
                    for key, value in staff_data.items():
                        setattr(existing, key, value)
                    existing.save()
                    logger.debug(f"기존 레코드 업데이트: {existing.id}")
                else:
                    # 신규 생성
                    new_staff = OutsourcedStaff.objects.create(**staff_data)
                    logger.debug(f"신규 레코드 생성: {new_staff.id}")
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_msg = f"데이터 처리 오류 [{idx+1}]: {staff_data.get('company_name', 'Unknown')} - {staff_data.get('project_name', 'Unknown')}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                import traceback
                logger.error(f"상세 오류:\n{traceback.format_exc()}")
        
        # 업로드 기록 업데이트
        upload_record.processed_status = 'completed'
        upload_record.total_records = success_count + error_count
        upload_record.success_records = success_count
        upload_record.error_records = error_count
        upload_record.error_log = '\\n'.join(errors) if errors else None
        upload_record.save()
        
        # 증감 계산 실행
        try:
            calculate_changes()
        except Exception as calc_error:
            logger.warning(f"증감 계산 중 오류 (무시됨): {calc_error}")
        
        return JsonResponse({
            'success': True,
            'message': f'{success_count}개 데이터 처리 완료',
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"파일 업로드 오류: {e}")
        import traceback
        logger.error(f"상세 오류:\n{traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # 임시 파일 삭제 - 잠시 대기 후 삭제
        if 'full_path' in locals() and os.path.exists(full_path):
            try:
                # 파일 시스템이 파일을 완전히 해제할 때까지 잠시 대기
                import time
                time.sleep(0.1)
                os.remove(full_path)
            except Exception as e:
                logger.warning(f"임시 파일 삭제 실패 (나중에 정리됨): {e}")


@require_http_methods(["GET"])
def get_outsourced_current(request):
    """현재 외주인력 현황 조회"""
    company = request.GET.get('company')
    staff_type = request.GET.get('staff_type')
    month = request.GET.get('month')  # YYYY-MM 형식
    
    # 기준일 조회
    if month:
        # 특정 월의 마지막 데이터
        try:
            year, month_num = month.split('-')
            start_date = datetime(int(year), int(month_num), 1).date()
            
            # 다음 달 1일 계산
            if int(month_num) == 12:
                end_date = datetime(int(year) + 1, 1, 1).date()
            else:
                end_date = datetime(int(year), int(month_num) + 1, 1).date()
            
            latest_date = OutsourcedStaff.objects.filter(
                report_date__gte=start_date,
                report_date__lt=end_date
            ).aggregate(latest=Max('report_date'))['latest']
        except ValueError:
            latest_date = None
    else:
        # 최신 기준일 조회
        latest_date = OutsourcedStaff.objects.aggregate(
            latest=Max('report_date')
        )['latest']
    
    if not latest_date:
        return JsonResponse({'data': [], 'summary': {}})
    
    # 쿼리 빌드
    queryset = OutsourcedStaff.objects.filter(report_date=latest_date)
    
    if company:
        queryset = queryset.filter(company_name=company)
    
    if staff_type:
        queryset = queryset.filter(staff_type=staff_type)
    
    # 전년말 대비 데이터도 가져오기
    year_end_data = {}
    if latest_date and latest_date.year > 1:
        last_year_end = datetime(latest_date.year - 1, 12, 31).date()
        year_end_records = OutsourcedStaff.objects.filter(report_date=last_year_end)
        
        for record in year_end_records:
            key = f"{record.company_name}_{record.project_name}_{record.staff_type}"
            year_end_data[key] = record.headcount
    
    # 데이터 직렬화
    data = []
    for staff in queryset:
        # 전년말 대비 계산
        key = f"{staff.company_name}_{staff.project_name}_{staff.staff_type}"
        year_end_headcount = year_end_data.get(key, 0)
        year_end_change = staff.headcount - year_end_headcount if year_end_headcount else staff.headcount
        
        # 전월 대비 계산 (기존 로직 활용)
        month_ago = latest_date - timedelta(days=30)
        month_record = OutsourcedStaff.objects.filter(
            company_name=staff.company_name,
            project_name=staff.project_name,
            staff_type=staff.staff_type,
            report_date=month_ago
        ).first()
        
        month_change = 0
        if month_record:
            month_change = staff.headcount - month_record.headcount
        
        data.append({
            'company_name': staff.company_name,
            'project_name': staff.project_name,
            'staff_type': staff.staff_type,
            'headcount': staff.headcount,
            'previous_headcount': staff.previous_headcount,
            'headcount_change': staff.headcount_change,
            'month_change': month_change,
            'year_end_change': year_end_change,
            'change_rate': float(staff.change_rate),
            'report_date': staff.report_date.strftime('%Y-%m-%d')
        })
    
    # 요약 정보
    summary = queryset.aggregate(
        total_headcount=Sum('headcount'),
        total_resident=Sum(models.Case(
            models.When(staff_type='resident', then='headcount'),
            default=0,
            output_field=models.IntegerField()
        )),
        total_non_resident=Sum(models.Case(
            models.When(staff_type='non_resident', then='headcount'),
            default=0,
            output_field=models.IntegerField()
        )),
        total_project=Sum(models.Case(
            models.When(staff_type='project', then='headcount'),
            default=0,
            output_field=models.IntegerField()
        )),
        company_count=Count('company_name', distinct=True),
        project_count=Count('project_name', distinct=True)
    )
    
    return JsonResponse({
        'data': data,
        'summary': summary,
        'report_date': latest_date.strftime('%Y-%m-%d')
    })


@require_http_methods(["GET"])
def get_outsourced_trend(request):
    """외주인력 추이 조회"""
    company = request.GET.get('company')
    period = request.GET.get('period', '3months')  # 3months, 6months, 1year
    
    # 기간 계산
    end_date = timezone.now().date()
    if period == '3months':
        start_date = end_date - timedelta(days=90)
    elif period == '6months':
        start_date = end_date - timedelta(days=180)
    else:
        start_date = end_date - timedelta(days=365)
    
    # 쿼리
    queryset = OutsourcedStaff.objects.filter(
        report_date__range=[start_date, end_date]
    )
    
    if company:
        queryset = queryset.filter(company_name=company)
    
    # 날짜별 집계
    trend_data = queryset.values('report_date', 'staff_type').annotate(
        total_headcount=Sum('headcount')
    ).order_by('report_date')
    
    # 데이터 포맷팅
    result = {
        'resident': [],
        'non_resident': [],
        'project': [],
        'total': []
    }
    
    # 날짜별로 그룹화
    date_groups = {}
    for item in trend_data:
        date_str = item['report_date'].strftime('%Y-%m-%d')
        if date_str not in date_groups:
            date_groups[date_str] = {'resident': 0, 'non_resident': 0, 'project': 0}
        
        date_groups[date_str][item['staff_type']] = item['total_headcount']
    
    # 결과 포맷팅
    for date_str, counts in sorted(date_groups.items()):
        result['resident'].append({
            'date': date_str,
            'count': counts['resident']
        })
        result['non_resident'].append({
            'date': date_str,
            'count': counts['non_resident']
        })
        result['project'].append({
            'date': date_str,
            'count': counts['project']
        })
        result['total'].append({
            'date': date_str,
            'count': counts['resident'] + counts['non_resident'] + counts['project']
        })
    
    return JsonResponse(result)


@require_http_methods(["GET"])
def get_outsourced_diff(request):
    """기준일 대비 증감현황 조회"""
    base_type = request.GET.get('base_type', 'week')  # week, month, year_end
    company = request.GET.get('company')
    
    # 최신 데이터 조회
    latest_records = OutsourcedStaff.objects.filter(
        base_type=base_type
    )
    
    if company:
        latest_records = latest_records.filter(company_name=company)
    
    # 증감 데이터 집계
    diff_summary = latest_records.aggregate(
        total_increase=Sum(models.Case(
            models.When(headcount_change__gt=0, then='headcount_change'),
            default=0,
            output_field=models.IntegerField()
        )),
        total_decrease=Sum(models.Case(
            models.When(headcount_change__lt=0, then='headcount_change'),
            default=0,
            output_field=models.IntegerField()
        )),
        increase_count=Count(models.Case(
            models.When(headcount_change__gt=0, then=1),
            output_field=models.IntegerField()
        )),
        decrease_count=Count(models.Case(
            models.When(headcount_change__lt=0, then=1),
            output_field=models.IntegerField()
        )),
        # 인력 구분별 증감
        resident_increase=Sum(models.Case(
            models.When(staff_type='resident', headcount_change__gt=0, then='headcount_change'),
            default=0,
            output_field=models.IntegerField()
        )),
        resident_decrease=Sum(models.Case(
            models.When(staff_type='resident', headcount_change__lt=0, then='headcount_change'),
            default=0,
            output_field=models.IntegerField()
        )),
        non_resident_increase=Sum(models.Case(
            models.When(staff_type='non_resident', headcount_change__gt=0, then='headcount_change'),
            default=0,
            output_field=models.IntegerField()
        )),
        non_resident_decrease=Sum(models.Case(
            models.When(staff_type='non_resident', headcount_change__lt=0, then='headcount_change'),
            default=0,
            output_field=models.IntegerField()
        )),
        project_increase=Sum(models.Case(
            models.When(staff_type='project', headcount_change__gt=0, then='headcount_change'),
            default=0,
            output_field=models.IntegerField()
        )),
        project_decrease=Sum(models.Case(
            models.When(staff_type='project', headcount_change__lt=0, then='headcount_change'),
            default=0,
            output_field=models.IntegerField()
        ))
    )
    
    # 상세 데이터
    diff_details = []
    for record in latest_records:
        if record.headcount_change != 0:
            diff_details.append({
                'company_name': record.company_name,
                'project_name': record.project_name,
                'staff_type': record.staff_type,
                'current': record.headcount,
                'previous': record.previous_headcount,
                'change': record.headcount_change,
                'change_rate': float(record.change_rate),
                'status': record.change_status
            })
    
    return JsonResponse({
        'summary': diff_summary,
        'details': sorted(diff_details, key=lambda x: abs(x['change']), reverse=True)
    })


def calculate_changes():
    """증감 계산 (배치 처리)"""
    # 모든 회사의 최신 데이터에 대해 증감 계산
    latest_date = OutsourcedStaff.objects.aggregate(
        latest=Max('report_date')
    )['latest']
    
    if not latest_date:
        return
    
    # latest_date가 datetime 객체인지 확인
    if hasattr(latest_date, 'year'):
        # 전주 데이터 계산
        week_ago = latest_date - timedelta(days=7)
        calculate_changes_for_base(latest_date, week_ago, 'week')
        
        # 전월 데이터 계산
        month_ago = latest_date - timedelta(days=30)
        calculate_changes_for_base(latest_date, month_ago, 'month')
        
        # 전년말 데이터 계산
        if latest_date.year > 1:  # 유효한 연도인지 확인
            last_year_end = datetime(latest_date.year - 1, 12, 31).date()
            calculate_changes_for_base(latest_date, last_year_end, 'year_end')


def calculate_changes_for_base(current_date, base_date, base_type):
    """특정 기준일에 대한 증감 계산"""
    current_records = OutsourcedStaff.objects.filter(report_date=current_date)
    
    for record in current_records:
        # 이전 레코드 찾기
        previous = OutsourcedStaff.objects.filter(
            company_name=record.company_name,
            project_name=record.project_name,
            report_date=base_date
        ).first()
        
        # 증감 계산
        record.base_type = base_type
        
        if previous:
            record.previous_headcount = previous.headcount
            record.headcount_change = record.headcount - previous.headcount
            
            # 증감율 계산
            if previous.headcount > 0:
                record.change_rate = ((record.headcount - previous.headcount) / previous.headcount) * 100
            else:
                record.change_rate = 100 if record.headcount > 0 else 0
        else:
            # 이전 데이터가 없으면 전체가 신규
            record.previous_headcount = 0
            record.headcount_change = record.headcount
            record.change_rate = 100 if record.headcount > 0 else 0
            
        record.save()