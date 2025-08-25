"""
AI Insights Views - AI 인사이트 대시보드 뷰
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import models
from .services import AIInsightService
from .models import AIInsight, ActionItem, DailyMetrics
import json
import logging

logger = logging.getLogger(__name__)


class AIExecutiveDashboard(TemplateView):
    """AI 경영진 대시보드"""
    template_name = 'ai_insights/executive_dashboard_revolutionary_with_talent.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            ai_service = AIInsightService()
            
            # 1. 오늘의 핵심 AI 인사이트
            context['daily_insights'] = ai_service.generate_organizational_insights()
            
            # 2. AI 추천 액션 아이템
            # AI 추천 액션 아이템 조회
            action_items = ActionItem.objects.filter(
                status='PENDING'
            ).select_related('insight').order_by('-priority', 'due_date')[:10]
            context['recommended_actions'] = action_items
            
            # 3. 예측 분석
            # 트렌드 예측 분석
            context['predictions'] = ai_service.get_insight_trends(days=30)
            
            # 4. 최근 해결된 인사이트
            context['resolved_insights'] = AIInsight.objects.filter(
                is_resolved=True,
                resolved_at__date=timezone.now().date()
            )[:5]
            
            # 5. 대기중인 액션 아이템 수
            context['pending_actions_count'] = ActionItem.objects.filter(
                status='PENDING'
            ).count()
            
            # 6. 성공 지표
            context['success_metrics'] = self._get_success_metrics()
            
        except Exception as e:
            logger.error(f"AI 대시보드 컨텍스트 로드 오류: {e}")
            context.update(self._get_fallback_context())
        
        return context
    
    def _get_success_metrics(self):
        """성공 지표 계산"""
        try:
            today = timezone.now().date()
            
            # 오늘 생성된 인사이트
            insights_today = AIInsight.objects.filter(
                created_at__date=today
            ).count()
            
            # 오늘 해결된 액션
            actions_completed = ActionItem.objects.filter(
                completed_at__date=today
            ).count()
            
            # 전체 AI 신뢰도 평균
            avg_confidence = AIInsight.objects.filter(
                created_at__date=today
            ).aggregate(avg_conf=models.Avg('ai_confidence'))['avg_conf'] or 0
            
            return {
                'insights_generated': insights_today,
                'actions_completed': actions_completed,
                'avg_ai_confidence': round(avg_confidence * 100, 1),
                'system_health': 'good' if avg_confidence > 0.7 else 'warning'
            }
            
        except Exception as e:
            logger.error(f"성공 지표 계산 오류: {e}")
            return {
                'insights_generated': 0,
                'actions_completed': 0,
                'avg_ai_confidence': 0,
                'system_health': 'unknown'
            }
    
    def _get_fallback_context(self):
        """오류 시 기본 컨텍스트"""
        return {
            'daily_insights': [],
            'recommended_actions': [],
            'predictions': {},
            'resolved_insights': [],
            'pending_actions_count': 0,
            'success_metrics': {
                'insights_generated': 0,
                'actions_completed': 0,
                'avg_ai_confidence': 0,
                'system_health': 'error'
            },
            'error_message': 'AI 서비스에 일시적인 문제가 발생했습니다.'
        }


@require_http_methods(["GET"])
def api_daily_insights(request):
    """일일 인사이트 API"""
    try:
        ai_service = AIInsightService()
        insights = ai_service.generate_organizational_insights()
        
        return JsonResponse({
            'success': True,
            'data': insights,
            'count': len(insights),
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"일일 인사이트 API 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': []
        }, status=500)


@require_http_methods(["GET"])
def api_action_items(request):
    """액션 아이템 API"""
    try:
        ai_service = AIInsightService()
        # 대기 중인 액션 아이템 조회
        actions = ActionItem.objects.filter(
            status='PENDING'
        ).select_related('insight').order_by('-priority', 'due_date')[:20]
        
        # 시리얼라이즈
        actions_data = [
            {
                'id': action.id,
                'title': action.title,
                'description': action.description,
                'priority': action.priority,
                'due_date': action.due_date.isoformat() if action.due_date else None,
                'insight_title': action.insight.title if action.insight else None
            }
            for action in actions
        ]
        
        return JsonResponse({
            'success': True,
            'data': actions_data,
            'count': len(actions_data)
        })
        
    except Exception as e:
        logger.error(f"액션 아이템 API 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': []
        }, status=500)
