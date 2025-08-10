"""
AI Predictions Views - 이직 위험도 분석 뷰
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg
from employees.models import Employee
from .models import TurnoverRisk, RetentionPlan, TurnoverAlert, RiskFactor
from .services import TurnoverRiskAnalyzer, TurnoverAlertSystem
from utils.airiss_api_service import AIRISSAPIService
import json
import logging

logger = logging.getLogger(__name__)


class TurnoverRiskDashboard(TemplateView):
    """이직 위험도 대시보드"""
    template_name = 'ai_predictions/turnover_dashboard_revolutionary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # AIRISS API 서비스 사용 (정제된 데이터)
            airiss_api = AIRISSAPIService()
            
            # AIRISS API에서 위험 직원 데이터 가져오기
            airiss_risk_employees = airiss_api.get_risk_employees(limit=20)
            
            # AIRISS API에서 부서별 통계 가져오기
            department_stats = airiss_api.get_department_statistics()
            
            # AI 추천사항 가져오기
            ai_recommendations = airiss_api.get_ai_recommendations()
            
            # 배치 분석 실행
            batch_analysis = airiss_api.get_batch_analysis()
            
            # 위험도 레벨별 통계 (AIRISS API 데이터 기반)
            risk_stats = {
                'critical': sum(1 for e in airiss_risk_employees if e['risk_level'] == 'CRITICAL'),
                'high': sum(1 for e in airiss_risk_employees if e['risk_level'] == 'HIGH'),
                'medium': sum(1 for e in airiss_risk_employees if e['risk_level'] == 'MEDIUM'),
                'low': sum(1 for e in airiss_risk_employees if e['risk_level'] == 'LOW'),
                'total': len(airiss_risk_employees)
            }
            
            # 배치 분석 통계 추가
            risk_stats['total_analyzed'] = batch_analysis.get('total_analyzed', 0)
            risk_stats['high_risk_identified'] = batch_analysis.get('high_risk_identified', 0)
            
            # 기존 DB 데이터와 병합 (선택적)
            today = timezone.now().date()
            recent_risks = TurnoverRisk.objects.filter(
                prediction_date__date=today,
                status='ACTIVE'
            )
            
            # 최근 알림
            recent_alerts = TurnoverAlert.objects.filter(
                created_at__date=today,
                is_acknowledged=False
            ).select_related('turnover_risk__employee')[:5]
            
            # 유지 계획 현황
            active_plans = RetentionPlan.objects.filter(
                status='ACTIVE'
            ).count()
            
            completed_plans_today = RetentionPlan.objects.filter(
                actual_completion_date=today
            ).count()
            
            # 부서별 리스크 히트맵 데이터 준비 (정제된 API 데이터)
            heatmap_data = []
            for dept_name, stats in department_stats.items():
                heatmap_data.append({
                    'department': dept_name,
                    'risk_ratio': stats.get('risk_ratio', 0),
                    'high_risk_count': stats.get('high_risk_count', 0),
                    'total_count': stats.get('total_employees', 0),
                    'avg_score': stats.get('average_score', 0),
                    'trend': stats.get('trend', 'stable'),
                    'top_risks': stats.get('top_risks', [])
                })
            
            # 상위 리스크 부서 정렬
            heatmap_data = sorted(heatmap_data, key=lambda x: x['risk_ratio'], reverse=True)[:10]
            
            context.update({
                'risk_stats': risk_stats,
                'airiss_risk_employees': airiss_risk_employees[:10],  # 상위 10명만
                'high_risk_employees': recent_risks.filter(
                    risk_score__gte=0.6
                ).select_related('employee').order_by('-risk_score')[:10],
                'recent_alerts': recent_alerts,
                'active_retention_plans': active_plans,
                'completed_plans_today': completed_plans_today,
                'department_heatmap': heatmap_data,
                'ai_recommendations': ai_recommendations,
                'batch_analysis': batch_analysis,
                'airiss_integrated': True,
                'dashboard_updated': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"이직 위험도 대시보드 오류: {e}")
            context.update({
                'risk_stats': {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'airiss_risk_employees': [],
                'high_risk_employees': [],
                'recent_alerts': [],
                'active_retention_plans': 0,
                'completed_plans_today': 0,
                'department_heatmap': [],
                'airiss_integrated': False,
                'error_message': 'AI 분석 서비스에 일시적인 문제가 발생했습니다.'
            })
        
        return context


class EmployeeRiskDetailView(TemplateView):
    """개별 직원 위험도 상세 뷰"""
    template_name = 'ai_predictions/employee_risk_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_id = kwargs.get('employee_id')
        
        try:
            employee = get_object_or_404(Employee, id=employee_id)
            
            # 최신 위험도 분석 조회
            latest_risk = TurnoverRisk.objects.filter(
                employee=employee,
                status='ACTIVE'
            ).order_by('-prediction_date').first()
            
            # 위험도 히스토리
            risk_history = TurnoverRisk.objects.filter(
                employee=employee
            ).order_by('-prediction_date')[:12]
            
            # 유지 계획
            retention_plan = None
            if latest_risk:
                try:
                    retention_plan = latest_risk.retention_plan
                except RetentionPlan.DoesNotExist:
                    pass
            
            # 관련 알림
            alerts = TurnoverAlert.objects.filter(
                turnover_risk__employee=employee
            ).order_by('-created_at')[:5]
            
            # 실시간 분석 수행 (캐시 활용)
            analyzer = TurnoverRiskAnalyzer()
            current_analysis = analyzer.analyze_employee_risk(employee)
            
            context.update({
                'employee': employee,
                'latest_risk': latest_risk,
                'current_analysis': current_analysis,
                'risk_history': risk_history,
                'retention_plan': retention_plan,
                'alerts': alerts
            })
            
        except Exception as e:
            logger.error(f"직원 위험도 상세 뷰 오류: {e}")
            context.update({
                'employee': None,
                'error_message': '직원 정보를 불러올 수 없습니다.'
            })
        
        return context


@require_http_methods(["GET"])
def api_analyze_employee_risk(request, employee_id):
    """개별 직원 위험도 분석 API"""
    try:
        employee = get_object_or_404(Employee, id=employee_id)
        analyzer = TurnoverRiskAnalyzer()
        
        # 실시간 분석 수행
        analysis = analyzer.analyze_employee_risk(employee)
        
        # DB에 저장
        risk_record, created = TurnoverRisk.objects.update_or_create(
            employee=employee,
            prediction_date__date=timezone.now().date(),
            defaults={
                'risk_level': analysis['risk_level'],
                'risk_score': analysis['risk_score'],
                'confidence_level': analysis['confidence_level'],
                'primary_risk_factors': analysis['primary_risk_factors'],
                'secondary_risk_factors': analysis['secondary_risk_factors'],
                'protective_factors': analysis['protective_factors'],
                'predicted_departure_date': analysis['predicted_departure_date'],
                'ai_analysis': analysis['ai_analysis'],
                'ai_recommendations': analysis['recommendations'],
                'ai_model_version': analysis['model_version'],
                'status': 'ACTIVE'
            }
        )
        
        # 알림 시스템 확인
        alert_system = TurnoverAlertSystem()
        alerts = alert_system.check_and_create_alerts(employee, analysis)
        
        return JsonResponse({
            'success': True,
            'analysis': {
                'employee_id': analysis['employee_id'],
                'employee_name': analysis['employee_name'],
                'risk_score': analysis['risk_score'],
                'risk_level': analysis['risk_level'],
                'confidence': analysis['confidence_level'],
                'predicted_departure': analysis['predicted_departure_date'].isoformat() if analysis['predicted_departure_date'] else None,
                'primary_factors': analysis['primary_risk_factors'],
                'recommendations': analysis['recommendations'],
                'ai_insights': analysis['ai_analysis'].get('key_insights', [])
            },
            'alerts_created': len(alerts),
            'record_created': created,
            'analysis_timestamp': timezone.now().isoformat()
        })
        
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '직원을 찾을 수 없습니다.'
        }, status=404)
        
    except Exception as e:
        logger.error(f"직원 위험도 분석 API 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_high_risk_employees(request):
    """고위험 직원 목록 API"""
    try:
        threshold = float(request.GET.get('threshold', 0.6))
        limit = int(request.GET.get('limit', 20))
        
        analyzer = TurnoverRiskAnalyzer()
        high_risk_data = analyzer.get_high_risk_employees(threshold)
        
        # 제한된 수만 반환
        limited_data = high_risk_data[:limit]
        
        return JsonResponse({
            'success': True,
            'data': limited_data,
            'total_count': len(high_risk_data),
            'threshold': threshold,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"고위험 직원 API 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_batch_analyze(request):
    """일괄 위험도 분석 API"""
    try:
        data = json.loads(request.body)
        department = data.get('department')
        position = data.get('position')
        
        # 필터 조건 적용
        employees_query = Employee.objects.filter(employment_status='재직')
        
        if department:
            employees_query = employees_query.filter(department=department)
        if position:
            employees_query = employees_query.filter(position__icontains=position)
        
        employees = employees_query[:50]  # 최대 50명 제한
        
        analyzer = TurnoverRiskAnalyzer()
        results = analyzer.batch_analyze_employees(employees)
        
        # DB에 결과 저장
        saved_count = 0
        for result in results:
            try:
                risk_record, created = TurnoverRisk.objects.update_or_create(
                    employee_id=result['employee_id'],
                    prediction_date__date=timezone.now().date(),
                    defaults={
                        'risk_level': result['risk_level'],
                        'risk_score': result['risk_score'],
                        'confidence_level': result['confidence_level'],
                        'primary_risk_factors': result['primary_risk_factors'],
                        'secondary_risk_factors': result['secondary_risk_factors'],
                        'protective_factors': result['protective_factors'],
                        'predicted_departure_date': result['predicted_departure_date'],
                        'ai_analysis': result['ai_analysis'],
                        'ai_recommendations': result['recommendations'],
                        'ai_model_version': result['model_version'],
                        'status': 'ACTIVE'
                    }
                )
                if created:
                    saved_count += 1
            except Exception as e:
                logger.error(f"일괄 분석 결과 저장 오류 (직원 {result['employee_id']}): {e}")
                continue
        
        # 요약 통계
        risk_summary = {
            'critical': sum(1 for r in results if r['risk_level'] == 'CRITICAL'),
            'high': sum(1 for r in results if r['risk_level'] == 'HIGH'),
            'medium': sum(1 for r in results if r['risk_level'] == 'MEDIUM'),
            'low': sum(1 for r in results if r['risk_level'] == 'LOW')
        }
        
        return JsonResponse({
            'success': True,
            'analyzed_count': len(results),
            'saved_count': saved_count,
            'risk_summary': risk_summary,
            'high_risk_employees': [r for r in results if r['risk_score'] >= 0.7][:5],
            'analysis_timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"일괄 분석 API 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_risk_statistics(request):
    """위험도 통계 API"""
    try:
        period_days = int(request.GET.get('period', 7))
        start_date = timezone.now().date() - timezone.timedelta(days=period_days)
        
        # 기간별 위험도 통계
        risks = TurnoverRisk.objects.filter(
            prediction_date__date__gte=start_date,
            status='ACTIVE'
        )
        
        # 전체 통계
        total_stats = {
            'total_employees': risks.values('employee').distinct().count(),
            'critical_risk': risks.filter(risk_level='CRITICAL').count(),
            'high_risk': risks.filter(risk_level='HIGH').count(),
            'medium_risk': risks.filter(risk_level='MEDIUM').count(),
            'low_risk': risks.filter(risk_level='LOW').count(),
            'avg_risk_score': risks.aggregate(avg=Avg('risk_score'))['avg'] or 0
        }
        
        # 부서별 통계
        dept_stats = {}
        departments = Employee.objects.filter(
            employment_status='재직'
        ).values_list('department', flat=True).distinct()
        
        for dept in departments:
            dept_risks = risks.filter(employee__department=dept)
            dept_stats[dept] = {
                'total': dept_risks.count(),
                'avg_score': dept_risks.aggregate(avg=Avg('risk_score'))['avg'] or 0,
                'high_risk_count': dept_risks.filter(risk_score__gte=0.6).count()
            }
        
        # 최근 알림 통계
        alert_stats = TurnoverAlert.objects.filter(
            created_at__date__gte=start_date
        ).values('severity').annotate(count=Count('id'))
        
        alert_summary = {item['severity']: item['count'] for item in alert_stats}
        
        return JsonResponse({
            'success': True,
            'period_days': period_days,
            'total_statistics': total_stats,
            'department_statistics': dept_stats,
            'alert_statistics': alert_summary,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"위험도 통계 API 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_acknowledge_alert(request, alert_id):
    """알림 확인 처리 API"""
    try:
        alert = get_object_or_404(TurnoverAlert, id=alert_id)
        
        # 알림 확인 처리
        alert.is_acknowledged = True
        alert.acknowledged_at = timezone.now()
        # alert.acknowledged_by = request.user if request.user.is_authenticated else None
        alert.save()
        
        return JsonResponse({
            'success': True,
            'message': '알림이 확인되었습니다.',
            'acknowledged_at': alert.acknowledged_at.isoformat()
        })
        
    except TurnoverAlert.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '알림을 찾을 수 없습니다.'
        }, status=404)
        
    except Exception as e:
        logger.error(f"알림 확인 API 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


class RetentionPlanListView(ListView):
    """유지 계획 목록 뷰"""
    model = RetentionPlan
    template_name = 'ai_predictions/retention_plans.html'
    context_object_name = 'retention_plans'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = RetentionPlan.objects.select_related(
            'turnover_risk__employee',
            'assigned_manager',
            'assigned_hr'
        ).order_by('-priority', '-created_at')
        
        # 필터 적용
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        department = self.request.GET.get('department')
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if department:
            queryset = queryset.filter(turnover_risk__employee__department=department)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 필터 옵션
        context['status_choices'] = RetentionPlan.PLAN_STATUS_CHOICES
        context['priority_choices'] = RetentionPlan.PRIORITY_CHOICES
        context['departments'] = Employee.objects.values_list('department', flat=True).distinct()
        
        # 현재 필터값
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'priority': self.request.GET.get('priority', ''),
            'department': self.request.GET.get('department', '')
        }
        
        return context