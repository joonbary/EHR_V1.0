"""
고급 평가 관리 뷰
시퀀셜싱킹 MCP를 활용한 복잡한 평가 프로세스 처리
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import json

from .models import EvaluationPeriod, ComprehensiveEvaluation
from employees.models import Employee
from utils.evaluation_processor import (
    EvaluationProcessor, CalibrationSession, PerformanceTrendAnalyzer
)


class ProcessEvaluationView(View):
    """평가 처리 뷰 - 상대평가 및 Calibration 준비"""
    
    def post(self, request, period_id):
        """평가 기간에 대한 종합 평가 처리"""
        try:
            period = get_object_or_404(EvaluationPeriod, id=period_id)
            
            # 평가 프로세서 실행
            processor = EvaluationProcessor()
            calibration_data = processor.process_comprehensive_evaluation(period_id)
            
            # 세션에 Calibration 데이터 저장
            request.session['calibration_data'] = {
                'period_id': period_id,
                'period_name': period.name,
                'total_evaluations': calibration_data['total_evaluations'],
                'adjustment_needed': len(calibration_data['adjustment_needed']),
                'department_stats': calibration_data['department_stats'],
                'process_date': datetime.now().isoformat()
            }
            
            messages.success(
                request,
                f"{period.name} 평가 처리가 완료되었습니다. "
                f"총 {calibration_data['total_evaluations']}건 중 "
                f"{len(calibration_data['adjustment_needed'])}건이 조정 검토 대상입니다."
            )
            
            return redirect('evaluations:calibration_dashboard', period_id=period_id)
            
        except Exception as e:
            messages.error(request, f"평가 처리 중 오류가 발생했습니다: {str(e)}")
            return redirect('evaluations:evaluation_list')


class CalibrationDashboardView(TemplateView):
    """Calibration 대시보드"""
    template_name = 'evaluations/calibration_dashboard.html'
    
    def get(self, request, period_id):
        period = get_object_or_404(EvaluationPeriod, id=period_id)
        
        # 세션에서 Calibration 데이터 가져오기
        calibration_data = request.session.get('calibration_data', {})
        
        # 조정 필요 케이스 조회
        processor = EvaluationProcessor()
        full_data = processor.process_comprehensive_evaluation(period_id)
        
        context = {
            'period': period,
            'calibration_data': calibration_data,
            'adjustment_cases': full_data['adjustment_needed'],
            'department_stats': full_data['department_stats']
        }
        
        return render(request, self.template_name, context)


class CalibrationSessionView(View):
    """Calibration 세션 관리"""
    
    def __init__(self):
        self.session = None
    
    def post(self, request, period_id):
        """Calibration 세션 시작"""
        participants = request.POST.getlist('participants')
        
        if not participants:
            participants = [request.user.id]
        
        # 세션 시작
        self.session = CalibrationSession(period_id)
        session_data = self.session.start_session(participants)
        
        # 세션 ID 저장
        request.session['calibration_session_id'] = id(self.session)
        
        return JsonResponse({
            'success': True,
            'session_data': {
                'start_time': session_data['start_time'].isoformat(),
                'total_cases': len(session_data['calibration_data']['adjustment_needed']),
                'participants': len(participants)
            }
        })
    
    def put(self, request, period_id):
        """개별 케이스 결정"""
        data = json.loads(request.body)
        evaluation_id = data.get('evaluation_id')
        decision = data.get('decision')
        
        # 세션에서 CalibrationSession 가져오기
        if not self.session:
            return JsonResponse({
                'success': False,
                'error': '세션이 시작되지 않았습니다.'
            })
        
        # 결정 처리
        result = self.session.review_case(evaluation_id, decision)
        
        return JsonResponse({
            'success': True,
            'decision': result
        })
    
    def delete(self, request, period_id):
        """세션 종료"""
        if not self.session:
            return JsonResponse({
                'success': False,
                'error': '세션이 시작되지 않았습니다.'
            })
        
        # 세션 종료
        final_data = self.session.finalize_session()
        
        # 세션 정리
        if 'calibration_session_id' in request.session:
            del request.session['calibration_session_id']
        
        return JsonResponse({
            'success': True,
            'session_summary': {
                'duration': str(final_data['end_time'] - final_data['start_time']),
                'total_decisions': final_data['total_decisions']
            }
        })


class PerformanceTrendView(View):
    """성과 트렌드 분석 뷰"""
    
    def get(self, request, employee_id=None):
        """개인 또는 부서 성과 트렌드 조회"""
        analyzer = PerformanceTrendAnalyzer()
        
        # 개인 트렌드
        if employee_id:
            employee = get_object_or_404(Employee, id=employee_id)
            
            # 권한 체크 제거 (Authentication removed)
            
            trend_data = analyzer.analyze_individual_trend(employee_id)
            
            return JsonResponse({
                'success': True,
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'department': employee.department,
                    'position': employee.position
                },
                'trend': trend_data
            })
        
        # 부서 트렌드 (Authentication removed)
        else:
            department = request.GET.get('department')
            period_id = request.GET.get('period_id')
            
            if department and period_id:
                dept_analysis = analyzer.analyze_department_performance(
                    department, int(period_id)
                )
                
                return JsonResponse({
                    'success': True,
                    'analysis': dept_analysis
                })
        
        return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)


class EvaluationInsightsView(TemplateView):
    """평가 인사이트 대시보드"""
    template_name = 'evaluations/insights_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 최신 평가 기간
        latest_period = EvaluationPeriod.objects.filter(
            is_active=False
        ).order_by('-end_date').first()
        
        if latest_period:
            processor = EvaluationProcessor()
            analyzer = PerformanceTrendAnalyzer()
            
            # 전체 평가 데이터 처리
            eval_data = processor.process_comprehensive_evaluation(latest_period.id)
            
            # 부서별 분석
            departments = Employee.objects.values_list(
                'department', flat=True
            ).distinct()
            
            dept_insights = []
            for dept in departments:
                analysis = analyzer.analyze_department_performance(
                    dept, latest_period.id
                )
                if analysis:
                    dept_insights.append(analysis)
            
            context.update({
                'period': latest_period,
                'total_evaluations': eval_data['total_evaluations'],
                'adjustment_needed': len(eval_data['adjustment_needed']),
                'department_insights': dept_insights,
                'top_departments': sorted(
                    dept_insights, 
                    key=lambda x: x['average_score'], 
                    reverse=True
                )[:5]
            })
        
        return context


def evaluation_analytics_api(request):
    """평가 분석 API 엔드포인트"""
    action = request.GET.get('action')
    
    if action == 'grade_distribution':
        # 등급 분포 데이터
        period_id = request.GET.get('period_id')
        evaluations = ComprehensiveEvaluation.objects.filter(
            evaluation_period_id=period_id
        )
        
        grade_counts = {}
        for eval in evaluations:
            grade = eval.final_grade or eval.manager_grade
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        return JsonResponse({
            'labels': list(grade_counts.keys()),
            'data': list(grade_counts.values())
        })
    
    elif action == 'score_distribution':
        # 점수 분포 데이터
        period_id = request.GET.get('period_id')
        evaluations = ComprehensiveEvaluation.objects.filter(
            evaluation_period_id=period_id
        ).values('total_score')
        
        scores = [e['total_score'] for e in evaluations if e['total_score']]
        
        # 히스토그램 데이터 생성
        import numpy as np
        hist, bins = np.histogram(scores, bins=10)
        
        return JsonResponse({
            'bins': bins.tolist(),
            'counts': hist.tolist()
        })
    
    elif action == 'department_comparison':
        # 부서별 비교
        period_id = request.GET.get('period_id')
        dept_stats = []
        
        departments = Employee.objects.values_list(
            'department', flat=True
        ).distinct()
        
        for dept in departments:
            avg_score = ComprehensiveEvaluation.objects.filter(
                evaluation_period_id=period_id,
                employee__department=dept
            ).aggregate(
                avg_score=models.Avg('total_score')
            )['avg_score']
            
            if avg_score:
                dept_stats.append({
                    'department': dept,
                    'average_score': round(avg_score, 2)
                })
        
        return JsonResponse({
            'departments': [d['department'] for d in dept_stats],
            'scores': [d['average_score'] for d in dept_stats]
        })
    
    return JsonResponse({'error': 'Invalid action'}, status=400)