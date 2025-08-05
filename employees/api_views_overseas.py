"""
해외 인력현황 API Views
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
    from .models_hr import OverseasWorkforce, HRFileUpload
    from .services.excel_parser_overseas_v2 import OverseasWorkforceParserV2
    logger.info("Successfully imported OverseasWorkforceParserV2")
except ImportError as e:
    logger.error(f"Import error: {e}")
    # Fallback to old parser if V2 fails
    try:
        from .services.excel_parser_overseas import OverseasWorkforceParser as OverseasWorkforceParserV2
        logger.warning("Using fallback OverseasWorkforceParser")
    except ImportError as e2:
        logger.error(f"Fallback import error: {e2}")
        raise e


@csrf_exempt
def upload_overseas_file(request):
    """해외 인력현황 파일 업로드"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': '파일이 없습니다.'}, status=400)
        
        file = request.FILES['file']
        
        # 파일 저장
        file_name = f"overseas/{uuid.uuid4()}_{file.name}"
        file_path = default_storage.save(file_name, file)
        full_path = default_storage.path(file_path)
        
        # 파서 초기화
        try:
            parser = OverseasWorkforceParserV2()
            logger.info("Parser initialized successfully")
        except Exception as e:
            logger.error(f"Parser initialization failed: {e}")
            return JsonResponse({'error': f'파서 초기화 실패: {str(e)}'}, status=500)
        
        # 파일 업로드 기록 생성
        upload_record = HRFileUpload.objects.create(
            file_name=file.name,
            file_type='overseas_workforce',
            report_date=timezone.now().date(),
            uploaded_by=request.user if request.user.is_authenticated else None,
            processed_status='processing'
        )
        
        # 파싱 및 저장
        try:
            result = parser.parse_file(full_path)
            logger.info(f"파싱 결과: {len(result)}개 법인")
        except Exception as e:
            logger.error(f"파일 파싱 실패: {e}")
            import traceback
            logger.error(f"파싱 오류 상세:\\n{traceback.format_exc()}")
            return JsonResponse({'error': f'파일 파싱 실패: {str(e)}'}, status=500)
        
        success_count = 0
        error_count = 0
        errors = []
        
        for idx, workforce_data in enumerate(result):
            try:
                logger.debug(f"처리 중 [{idx+1}/{len(result)}]: {workforce_data['corporation']}")
                logger.debug(f"Data keys: {list(workforce_data.keys())}")
                if 'structure' in workforce_data:
                    logger.debug("Structure found in data")
                else:
                    logger.debug("No structure in data")
                
                # 날짜 변환 처리
                report_date_str = workforce_data['report_date']
                if isinstance(report_date_str, str):
                    from datetime import datetime
                    report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
                else:
                    report_date = report_date_str
                
                # 기존 레코드 확인
                existing = OverseasWorkforce.objects.filter(
                    corporation=workforce_data['corporation'],
                    report_date=report_date
                ).first()
                
                if existing:
                    # 업데이트
                    existing.raw_data = workforce_data
                    existing.total_count = workforce_data.get('total', 0)
                    existing.save()
                    logger.debug(f"기존 레코드 업데이트: {existing.id}")
                else:
                    # 신규 생성 - 기존 필드들은 0으로 설정
                    new_workforce = OverseasWorkforce.objects.create(
                        corporation=workforce_data['corporation'],
                        report_date=report_date,  # 변환된 날짜 사용
                        raw_data=workforce_data,
                        total_count=workforce_data.get('total', 0),
                        # 기존 필드들은 모두 0으로 설정
                        executive_count=workforce_data.get('ranks', {}).get('이사', 0),
                        general_manager_count=workforce_data.get('ranks', {}).get('부장급', 0),
                        deputy_manager_count=workforce_data.get('ranks', {}).get('차장', 0),
                        manager_count=workforce_data.get('ranks', {}).get('과장', 0),
                        assistant_manager_count=workforce_data.get('ranks', {}).get('대리', 0),
                        staff_count=workforce_data.get('ranks', {}).get('사원', 0),
                        ceo_count=workforce_data.get('positions', {}).get('대표이사', 0),
                        division_head_count=workforce_data.get('positions', {}).get('본부장', 0),
                        department_head_count=workforce_data.get('positions', {}).get('부서장', 0),
                        branch_manager_count=workforce_data.get('positions', {}).get('지점장', 0),
                        team_leader_count=workforce_data.get('positions', {}).get('팀장', 0),
                        cbo_count=workforce_data.get('positions', {}).get('최고사업책임자', 0),
                        evp_count=workforce_data.get('positions', {}).get('부문장', 0),
                        svp_count=workforce_data.get('positions', {}).get('수석부사장', 0),
                        vp_count=workforce_data.get('positions', {}).get('상무이사', 0)
                    )
                    logger.debug(f"신규 레코드 생성: {new_workforce.id}")
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_msg = f"데이터 처리 오류 [{idx+1}]: {workforce_data.get('corporation', 'Unknown')}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                import traceback
                logger.error(f"상세 오류:\n{traceback.format_exc()}")
        
        # 업로드 기록 업데이트
        upload_record.processed_status = 'completed'
        upload_record.total_records = success_count + error_count
        upload_record.success_records = success_count
        upload_record.error_records = error_count
        upload_record.error_log = '\n'.join(errors) if errors else None
        upload_record.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{success_count}개 법인 데이터 처리 완료',
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"파일 업로드 오류: {e}")
        import traceback
        logger.error(f"상세 오류:\n{traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # 임시 파일 삭제
        if 'full_path' in locals() and os.path.exists(full_path):
            try:
                import time
                time.sleep(0.1)
                os.remove(full_path)
            except Exception as e:
                logger.warning(f"임시 파일 삭제 실패 (나중에 정리됨): {e}")


@require_http_methods(["GET"])
def get_overseas_current(request):
    """현재 해외 인력현황 조회"""
    corporation = request.GET.get('corporation')
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
            
            latest_date = OverseasWorkforce.objects.filter(
                report_date__gte=start_date,
                report_date__lt=end_date
            ).aggregate(latest=Max('report_date'))['latest']
        except ValueError:
            latest_date = None
    else:
        # 최신 기준일 조회
        latest_date = OverseasWorkforce.objects.aggregate(
            latest=Max('report_date')
        )['latest']
    
    if not latest_date:
        return JsonResponse({'data': [], 'summary': {}, 'report_date': None})
    
    # 쿼리 빌드
    queryset = OverseasWorkforce.objects.filter(report_date=latest_date)
    
    if corporation:
        queryset = queryset.filter(corporation=corporation)
    
    # 데이터 직렬화 - raw_data 사용
    data = []
    for workforce in queryset:
        # raw_data가 있으면 그대로 사용
        if workforce.raw_data:
            corp_data = workforce.raw_data.copy()
            corp_data['report_date'] = workforce.report_date.strftime('%Y-%m-%d')
            data.append(corp_data)
        else:
            # 기존 방식 (호환성을 위해)
            data.append({
                'corporation': workforce.corporation,
                'report_date': workforce.report_date.strftime('%Y-%m-%d'),
                'positions': {},
                'ranks': {
                    '이사': workforce.executive_count,
                    '부장급': workforce.general_manager_count,
                    '차장': workforce.deputy_manager_count,
                    '과장': workforce.manager_count,
                    '대리': workforce.assistant_manager_count,
                    '사원': workforce.staff_count,
                },
                'total': workforce.total_count
            })
    
    # 요약 정보
    summary = queryset.aggregate(
        total_count=Sum('total_count'),
        total_executive=Sum('executive_count'),
        total_general_manager=Sum('general_manager_count'),
        total_deputy_manager=Sum('deputy_manager_count'),
        total_manager=Sum('manager_count'),
        total_assistant_manager=Sum('assistant_manager_count'),
        total_staff=Sum('staff_count'),
        corporation_count=Count('corporation', distinct=True)
    )
    
    return JsonResponse({
        'data': data,
        'summary': summary,
        'report_date': latest_date.strftime('%Y-%m-%d')
    })


@require_http_methods(["GET"])
def get_overseas_months(request):
    """해외 인력현황 사용 가능한 월 목록 조회"""
    months = OverseasWorkforce.objects.values_list(
        'report_date', flat=True
    ).distinct().order_by('-report_date')
    
    # 월별로 그룹화
    month_list = []
    seen_months = set()
    
    for date in months:
        month_str = date.strftime('%Y-%m')
        if month_str not in seen_months:
            seen_months.add(month_str)
            month_list.append({
                'value': month_str,
                'display': date.strftime('%Y년 %m월')
            })
    
    return JsonResponse({'months': month_list})


def overseas_workforce_view(request):
    """월간 해외인력현황 뷰"""
    return render(request, 'hr/overseas_workforce.html')