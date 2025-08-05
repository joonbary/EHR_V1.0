"""
주간 인력현황 API Views
"""

import pandas as pd
import json
import io
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.db.models import Sum, Count, Q, F
from openpyxl import load_workbook

from .models_workforce import (
    WeeklyWorkforceSnapshot, 
    WeeklyJoinLeave, 
    WeeklyWorkforceChange
)


@csrf_exempt
@require_POST
def upload_workforce_snapshot(request):
    """주간 인력현황 스냅샷 엑셀 파일 업로드"""
    try:
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': '파일이 없습니다.'}, status=400)
        
        # 파일 확장자 검증
        if not file.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({'error': '엑셀 파일만 업로드 가능합니다.'}, status=400)
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file, engine='openpyxl')
        
        # 컬럼명 설정 (한글 인코딩 문제 해결)
        if len(df.columns) == 4:
            df.columns = ['직급구분', '회사', '직책', '직위']
        
        # 필수 컬럼 확인
        required_columns = ['직급구분', '회사', '직책', '직위']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({
                'error': f'필수 컬럼이 없습니다: {", ".join(missing_columns)}'
            }, status=400)
        
        # 데이터 처리
        from datetime import date
        snapshot_date = date.today()  # 기준일자는 오늘 날짜 사용
        
        # 기존 데이터 삭제
        WeeklyWorkforceSnapshot.objects.filter(snapshot_date=snapshot_date).delete()
        
        # 회사별, 직급구분별, 직책별, 직위별 집계
        grouped = df.groupby(['회사', '직급구분', '직책', '직위']).size().reset_index(name='인원수')
        
        snapshot_count = 0
        with transaction.atomic():
            for _, row in grouped.iterrows():
                try:
                    # 스냅샷 데이터 생성
                    WeeklyWorkforceSnapshot.objects.create(
                        snapshot_date=snapshot_date,
                        company=str(row['회사']).strip(),
                        job_group=str(row['직급구분']).strip(),  # 직급구분을 직군으로 사용
                        grade=str(row['직위']).strip(),  # 직위를 직급으로 사용
                        position=str(row['직책']).strip() if row['직책'] != '사원' else None,
                        contract_type='정규직' if '(N)' not in str(row['직위']) else '계약직',
                        headcount=int(row['인원수']),
                        uploaded_by=None  # request.user 제거 (로그인 기능 없음)
                    )
                    snapshot_count += 1
                    
                except Exception as e:
                    print(f"행 처리 오류: {str(e)}")
                    continue
        
        # 증감 분석 계산
        if snapshot_count > 0:
            print(f"Calculating workforce changes for {snapshot_date}")
            result = calculate_workforce_changes(snapshot_date)
            print(f"Calculation result: {result}")
        
        return JsonResponse({
            'success': True,
            'message': f'{snapshot_count}개의 데이터가 업로드되었습니다.'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def upload_join_leave(request):
    """주간 입/퇴사자 엑셀 파일 업로드"""
    try:
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': '파일이 없습니다.'}, status=400)
        
        # 파일 확장자 검증
        if not file.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({'error': '엑셀 파일만 업로드 가능합니다.'}, status=400)
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file, engine='openpyxl')
        
        # 필수 컬럼 확인
        required_columns = ['구분', '성명', '계열사', '소속부서', '직급', '일자']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({
                'error': f'필수 컬럼이 없습니다: {", ".join(missing_columns)}'
            }, status=400)
        
        # 데이터 처리
        record_count = 0
        with transaction.atomic():
            for _, row in df.iterrows():
                try:
                    # 구분 매핑
                    type_mapping = {
                        '입사': 'join',
                        '퇴사': 'leave',
                        '퇴사예정': 'leave_planned'
                    }
                    type_value = type_mapping.get(str(row['구분']).strip())
                    if not type_value:
                        continue
                    
                    # 일자 파싱
                    date = pd.to_datetime(row['일자']).date()
                    
                    # 입/퇴사자 데이터 생성
                    WeeklyJoinLeave.objects.create(
                        type=type_value,
                        name=str(row['성명']).strip(),
                        company=str(row['계열사']).strip(),
                        org_unit=str(row['소속부서']).strip(),
                        grade=str(row['직급']).strip(),
                        position=str(row.get('직책', '')).strip() or None,
                        job_group=str(row.get('직군', '')).strip() or None,
                        date=date,
                        reason=str(row.get('사유', '')).strip() or None,
                        uploaded_by=request.user
                    )
                    record_count += 1
                    
                except Exception as e:
                    print(f"행 처리 오류: {str(e)}")
                    continue
        
        return JsonResponse({
            'success': True,
            'message': f'{record_count}개의 데이터가 업로드되었습니다.'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def get_workforce_summary(request):
    """주간 인력현황 요약 정보 조회"""
    try:
        # 최신 기준일자
        latest_snapshot = WeeklyWorkforceSnapshot.objects.order_by('-snapshot_date').first()
        if not latest_snapshot:
            return JsonResponse({
                'snapshot_date': None,
                'total_headcount': 0,
                'join_count': 0,
                'leave_count': 0,
                'change_rate': 0
            })
        
        snapshot_date = latest_snapshot.snapshot_date
        
        # 전체 인원수
        total_headcount = WeeklyWorkforceSnapshot.objects.filter(
            snapshot_date=snapshot_date
        ).aggregate(total=Sum('headcount'))['total'] or 0
        
        # 주간 입/퇴사자
        week_start = snapshot_date - timedelta(days=6)
        join_count = WeeklyJoinLeave.objects.filter(
            type='join',
            date__range=[week_start, snapshot_date]
        ).count()
        
        leave_count = WeeklyJoinLeave.objects.filter(
            type__in=['leave', 'leave_planned'],
            date__range=[week_start, snapshot_date]
        ).count()
        
        # 전주 대비 증감율
        change_rate = 0
        prev_week_date = snapshot_date - timedelta(days=7)
        prev_total = WeeklyWorkforceSnapshot.objects.filter(
            snapshot_date=prev_week_date
        ).aggregate(total=Sum('headcount'))['total'] or 0
        
        if prev_total > 0:
            change_rate = ((total_headcount - prev_total) / prev_total) * 100
        
        return JsonResponse({
            'snapshot_date': snapshot_date.strftime('%Y-%m-%d'),
            'total_headcount': total_headcount,
            'join_count': join_count,
            'leave_count': leave_count,
            'change_rate': round(change_rate, 1)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def get_workforce_trend(request):
    """인력 추이 차트 데이터 조회"""
    try:
        # 최근 12주 데이터
        end_date = WeeklyWorkforceSnapshot.objects.order_by('-snapshot_date').first()
        if not end_date:
            return JsonResponse({'labels': [], 'datasets': []})
        
        end_date = end_date.snapshot_date
        start_date = end_date - timedelta(weeks=11)
        
        # 주별 데이터 집계
        weekly_data = WeeklyWorkforceSnapshot.objects.filter(
            snapshot_date__range=[start_date, end_date]
        ).values('snapshot_date').annotate(
            total=Sum('headcount')
        ).order_by('snapshot_date')
        
        # 차트 데이터 구성
        labels = []
        values = []
        
        for data in weekly_data:
            labels.append(data['snapshot_date'].strftime('%m/%d'))
            values.append(data['total'])
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'label': '전체 인원',
                'data': values,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.1
            }]
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def get_workforce_changes(request):
    """인력 증감 분석 데이터 조회"""
    try:
        # 최신 기준일자
        latest_snapshot = WeeklyWorkforceSnapshot.objects.order_by('-snapshot_date').first()
        if not latest_snapshot:
            return JsonResponse({'changes': []})
        
        current_date = latest_snapshot.snapshot_date
        
        # 증감 데이터 조회
        changes = WeeklyWorkforceChange.objects.filter(
            current_date=current_date
        ).select_related().order_by(
            'company', 'job_group', 'grade'
        )
        
        # 데이터 구성
        result = []
        for change in changes:
            # 증감 계산
            change_count = change.current_headcount - change.base_headcount
            if change.base_headcount > 0:
                change_rate = (change_count / change.base_headcount) * 100
            else:
                change_rate = 100.0 if change_count > 0 else 0.0
            
            # base_type 표시
            base_type_display = {
                'week': '전주 대비',
                'month': '전월 대비',
                'year_end': '전년말 대비'
            }.get(change.base_type, change.base_type)
            
            result.append({
                'company': change.company,
                'job_group': change.job_group,
                'grade': change.grade,
                'position': change.position,
                'contract_type': change.contract_type,
                'current_headcount': change.current_headcount,
                'base_headcount': change.base_headcount,
                'change_count': change_count,
                'change_rate': change_rate,
                'base_type': base_type_display
            })
        
        return JsonResponse({'changes': result})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# 증감 분석 계산 함수
def calculate_workforce_changes(current_date):
    """인력 증감 분석 계산 및 저장"""
    try:
        print(f"Starting calculate_workforce_changes for {current_date}")
        
        # 비교 기준일 계산
        prev_week = current_date - timedelta(days=7)
        prev_month = current_date - timedelta(days=30)
        prev_year_end = datetime(current_date.year - 1, 12, 31).date()
        
        print(f"Base dates - Week: {prev_week}, Month: {prev_month}, Year-end: {prev_year_end}")
        
        base_dates = [
            ('week', prev_week),
            ('month', prev_month),
            ('year_end', prev_year_end)
        ]
        
        # 현재 스냅샷 데이터
        current_snapshots = WeeklyWorkforceSnapshot.objects.filter(
            snapshot_date=current_date
        )
        print(f"Current snapshots count: {current_snapshots.count()}")
        
        with transaction.atomic():
            # 기존 증감 데이터 삭제
            WeeklyWorkforceChange.objects.filter(current_date=current_date).delete()
            
            for base_type, base_date in base_dates:
                # 기준 스냅샷 데이터
                base_snapshots = WeeklyWorkforceSnapshot.objects.filter(
                    snapshot_date=base_date
                )
                
                print(f"Processing {base_type} with base date {base_date}, base snapshots: {base_snapshots.count()}")
                
                # 그룹별 집계
                for snapshot in current_snapshots:
                    # 기준 인원수 조회
                    base_headcount = base_snapshots.filter(
                        company=snapshot.company,
                        job_group=snapshot.job_group,
                        grade=snapshot.grade,
                        position=snapshot.position,
                        contract_type=snapshot.contract_type
                    ).aggregate(total=Sum('headcount'))['total'] or 0
                    
                    # 증감 데이터 생성
                    try:
                        WeeklyWorkforceChange.objects.create(
                            current_date=current_date,
                            base_date=base_date,
                            base_type=base_type,
                            company=snapshot.company,
                            job_group=snapshot.job_group,
                            grade=snapshot.grade,
                            position=snapshot.position,
                            contract_type=snapshot.contract_type,
                            current_headcount=snapshot.headcount,
                            base_headcount=base_headcount
                        )
                    except Exception as e:
                        print(f"Error creating change record: {e}")
        
        return True
        
    except Exception as e:
        print(f"증감 분석 계산 오류: {str(e)}")
        return False