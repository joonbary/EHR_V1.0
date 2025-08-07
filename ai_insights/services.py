"""
AI Insights 서비스 - AI 인사이트 생성 및 분석
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Avg, Q
from employees.models import Employee
from compensation.models import EmployeeCompensation
from evaluations.models import ComprehensiveEvaluation
from .models import AIInsight, DailyMetrics, ActionItem

logger = logging.getLogger(__name__)

try:
    import openai
    openai.api_key = settings.OPENAI_API_KEY
except ImportError:
    logger.warning("OpenAI package not installed")
    openai = None

try:
    import anthropic
    anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
except ImportError:
    logger.warning("Anthropic package not installed")
    anthropic_client = None


class AIInsightGenerator:
    """AI 인사이트 생성기"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1시간 캐시
    
    def generate_daily_insights(self) -> List[Dict[str, Any]]:
        """일일 인사이트 생성"""
        cache_key = f"ai_insights_daily_{timezone.now().date()}"
        cached_insights = cache.get(cache_key)
        
        if cached_insights:
            return cached_insights
        
        try:
            # 실시간 HR 데이터 수집
            hr_data = self._collect_hr_metrics()
            
            # AI 인사이트 생성
            insights = self._generate_insights_with_ai(hr_data)
            
            # 데이터베이스에 저장
            self._save_insights_to_db(insights)
            
            # 캐시 저장
            cache.set(cache_key, insights, self.cache_timeout)
            
            return insights
            
        except Exception as e:
            logger.error(f"AI 인사이트 생성 오류: {e}")
            return self._get_fallback_insights()
    
    def get_action_items(self) -> List[Dict[str, Any]]:
        """추천 액션 아이템 조회"""
        cache_key = "ai_action_items_today"
        cached_actions = cache.get(cache_key)
        
        if cached_actions:
            return cached_actions
        
        # 오늘 생성된 인사이트의 액션 아이템
        today = timezone.now().date()
        action_items = ActionItem.objects.filter(
            insight__created_at__date=today,
            status='PENDING'
        ).select_related('insight', 'target_employee')
        
        actions = []
        for item in action_items:
            actions.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'priority': item.priority,
                'target': item.target_employee.name if item.target_employee else item.target_department,
                'due_date': item.due_date.isoformat() if item.due_date else None,
                'expected_impact': item.expected_impact,
                'ai_confidence': item.ai_confidence
            })
        
        cache.set(cache_key, actions, 1800)  # 30분 캐시
        return actions
    
    def predict_trends(self) -> Dict[str, Any]:
        """트렌드 예측"""
        cache_key = "ai_predictions_trends"
        cached_predictions = cache.get(cache_key)
        
        if cached_predictions:
            return cached_predictions
        
        try:
            # 최근 30일 데이터
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            recent_metrics = DailyMetrics.objects.filter(
                date__gte=thirty_days_ago
            ).order_by('date')
            
            if not recent_metrics.exists():
                return self._get_fallback_predictions()
            
            # 트렌드 분석
            predictions = self._analyze_trends_with_ai(recent_metrics)
            
            cache.set(cache_key, predictions, 7200)  # 2시간 캐시
            return predictions
            
        except Exception as e:
            logger.error(f"트렌드 예측 오류: {e}")
            return self._get_fallback_predictions()
    
    def _collect_hr_metrics(self) -> Dict[str, Any]:
        """실시간 HR 지표 수집"""
        try:
            # 기본 인력 현황
            total_employees = Employee.objects.filter(employment_status='재직').count()
            
            # 최근 30일 입퇴사
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            recent_hires = Employee.objects.filter(
                hire_date__gte=thirty_days_ago
            ).count()
            
            # 퇴사자는 employment_status 필드로 추정
            recent_resignations = Employee.objects.filter(
                employment_status='퇴직',
                updated_at__date__gte=thirty_days_ago  # 상태 변경일 기준
            ).count() if Employee.objects.filter(employment_status='퇴직').exists() else 0
            
            # 부서별 분포
            dept_distribution = Employee.objects.filter(
                employment_status='재직'
            ).values('department').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # 보상 통계
            compensation_stats = EmployeeCompensation.objects.aggregate(
                avg_total=Avg('total_compensation'),
                count=Count('id')
            )
            
            # 성과 통계 (최근 평가)
            recent_evaluations = ComprehensiveEvaluation.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=90)
            ).aggregate(
                avg_score=Avg('final_rating_numeric'),
                high_performers=Count('id', filter=Q(final_rating_numeric__gte=4.0)),
                low_performers=Count('id', filter=Q(final_rating_numeric__lt=2.0))
            )
            
            return {
                'total_employees': total_employees,
                'recent_hires': recent_hires,
                'recent_resignations': recent_resignations,
                'department_distribution': list(dept_distribution),
                'avg_compensation': float(compensation_stats.get('avg_total') or 0),
                'avg_performance': float(recent_evaluations.get('avg_score') or 0),
                'high_performers': recent_evaluations.get('high_performers', 0),
                'low_performers': recent_evaluations.get('low_performers', 0),
                'date': timezone.now().date().isoformat()
            }
            
        except Exception as e:
            logger.error(f"HR 지표 수집 오류: {e}")
            return {}
    
    def _generate_insights_with_ai(self, hr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """AI를 사용하여 인사이트 생성"""
        if not openai and not anthropic_client:
            return self._get_fallback_insights()
        
        try:
            # GPT-4 사용
            if openai and settings.OPENAI_API_KEY:
                return self._generate_insights_openai(hr_data)
            # Claude 사용
            elif anthropic_client:
                return self._generate_insights_anthropic(hr_data)
            else:
                return self._get_fallback_insights()
                
        except Exception as e:
            logger.error(f"AI 인사이트 생성 오류: {e}")
            return self._get_fallback_insights()
    
    def _generate_insights_openai(self, hr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """OpenAI GPT-4로 인사이트 생성"""
        prompt = f"""
        다음 HR 데이터를 분석하여 경영진이 즉시 알아야 할 3가지 핵심 인사이트를 생성하세요.
        
        데이터:
        {json.dumps(hr_data, ensure_ascii=False, indent=2)}
        
        각 인사이트는 다음 형식으로 JSON 배열로 응답하세요:
        [
            {{
                "title": "인사이트 제목",
                "description": "상세 설명",
                "category": "TURNOVER|PERFORMANCE|ENGAGEMENT|COMPENSATION|TEAM|LEADERSHIP",
                "priority": "URGENT|HIGH|MEDIUM|LOW",
                "affected_department": "영향받는 부서",
                "ai_confidence": 0.0-1.0,
                "recommended_actions": ["액션1", "액션2"],
                "expected_impact": "예상 효과"
            }}
        ]
        
        한국 기업 문화에 맞는 실용적이고 구체적인 조언을 제공하세요.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # gpt-4는 비용이 높으므로 3.5 사용
                messages=[
                    {"role": "system", "content": "당신은 HR 전문가이자 데이터 분석가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            insights_text = response.choices[0].message.content
            insights = json.loads(insights_text)
            
            return insights
            
        except Exception as e:
            logger.error(f"OpenAI 인사이트 생성 오류: {e}")
            return self._get_fallback_insights()
    
    def _generate_insights_anthropic(self, hr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Anthropic Claude로 인사이트 생성"""
        prompt = f"""
        다음 HR 데이터를 분석하여 경영진이 즉시 알아야 할 3가지 핵심 인사이트를 생성하세요.
        
        데이터:
        {json.dumps(hr_data, ensure_ascii=False, indent=2)}
        
        각 인사이트는 JSON 배열로 응답하세요.
        한국 기업 문화에 맞는 실용적이고 구체적인 조언을 제공하세요.
        """
        
        try:
            message = anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            insights_text = message.content[0].text
            # JSON 추출
            start = insights_text.find('[')
            end = insights_text.rfind(']') + 1
            if start != -1 and end != 0:
                insights = json.loads(insights_text[start:end])
                return insights
            
        except Exception as e:
            logger.error(f"Anthropic 인사이트 생성 오류: {e}")
            
        return self._get_fallback_insights()
    
    def _save_insights_to_db(self, insights: List[Dict[str, Any]]):
        """인사이트를 데이터베이스에 저장"""
        for insight_data in insights:
            try:
                insight = AIInsight.objects.create(
                    title=insight_data.get('title', '제목 없음'),
                    description=insight_data.get('description', ''),
                    category=insight_data.get('category', 'PERFORMANCE'),
                    priority=insight_data.get('priority', 'MEDIUM'),
                    affected_department=insight_data.get('affected_department', ''),
                    ai_confidence=insight_data.get('ai_confidence', 0.0),
                    ai_model_used='gpt-3.5-turbo' if openai else 'claude-3-sonnet',
                    raw_analysis=insight_data,
                    recommended_actions=insight_data.get('recommended_actions', [])
                )
                
                # 액션 아이템 생성
                for action in insight_data.get('recommended_actions', []):
                    ActionItem.objects.create(
                        insight=insight,
                        title=action[:200],  # 길이 제한
                        description=insight_data.get('expected_impact', ''),
                        priority=insight.priority,
                        expected_impact=insight_data.get('expected_impact', ''),
                        ai_confidence=insight.ai_confidence,
                        due_date=timezone.now().date() + timedelta(days=7)
                    )
                    
            except Exception as e:
                logger.error(f"인사이트 저장 오류: {e}")
    
    def _get_fallback_insights(self) -> List[Dict[str, Any]]:
        """AI가 사용 불가능할 때 기본 인사이트"""
        return [
            {
                'title': '인력 현황 모니터링 필요',
                'description': '최근 인력 변동이 감지되었습니다. 상세 분석이 필요합니다.',
                'category': 'PERFORMANCE',
                'priority': 'MEDIUM',
                'affected_department': '전체',
                'ai_confidence': 0.6,
                'recommended_actions': ['인력 현황 리포트 검토', 'HR 담당자 면담'],
                'expected_impact': '인력 운영 효율성 개선'
            },
            {
                'title': '성과 관리 검토',
                'description': '성과 평가 주기에 따른 검토가 필요합니다.',
                'category': 'PERFORMANCE',
                'priority': 'MEDIUM',
                'ai_confidence': 0.7,
                'recommended_actions': ['성과 평가 일정 확인'],
                'expected_impact': '성과 관리 체계화'
            }
        ]
    
    def _get_fallback_predictions(self) -> Dict[str, Any]:
        """기본 예측 데이터"""
        return {
            'turnover_prediction': {
                'next_quarter': '데이터 분석 중',
                'confidence': 0.5
            },
            'performance_trends': {
                'trend': '안정적',
                'confidence': 0.6
            },
            'compensation_outlook': {
                'recommendation': '현재 수준 유지',
                'confidence': 0.7
            }
        }
    
    def _analyze_trends_with_ai(self, metrics_queryset) -> Dict[str, Any]:
        """AI를 사용한 트렌드 분석"""
        # 간단한 트렌드 계산
        metrics_list = list(metrics_queryset)
        if len(metrics_list) < 7:
            return self._get_fallback_predictions()
        
        # 최근 7일 vs 이전 7일 비교
        recent_metrics = metrics_list[-7:]
        previous_metrics = metrics_list[-14:-7] if len(metrics_list) >= 14 else metrics_list[:7]
        
        recent_avg_employees = sum(m.total_employees for m in recent_metrics) / len(recent_metrics)
        previous_avg_employees = sum(m.total_employees for m in previous_metrics) / len(previous_metrics)
        
        employee_trend = (recent_avg_employees - previous_avg_employees) / previous_avg_employees * 100 if previous_avg_employees > 0 else 0
        
        return {
            'employee_count_trend': {
                'change_percent': round(employee_trend, 2),
                'direction': 'up' if employee_trend > 0 else 'down' if employee_trend < 0 else 'stable',
                'confidence': 0.8
            },
            'next_month_prediction': {
                'expected_employees': int(recent_avg_employees + (employee_trend * recent_avg_employees / 100)),
                'confidence': 0.7
            }
        }