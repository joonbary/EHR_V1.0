"""
AI 인사이트 서비스
조직 전반의 인사이트 분석 및 추천
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Avg, Count, Sum, F, Max, Min
from django.core.cache import cache
import json
import numpy as np
from collections import defaultdict

from .models import AIInsight, ActionItem, DailyMetrics, InsightTrend
from employees.models import Employee
from ai_services.base import AIServiceBase, AIAnalyzer
from ai_predictions.models import TurnoverRisk

logger = logging.getLogger(__name__)


class AIInsightService:
    """AI 기반 인사이트 생성 서비스"""
    
    def __init__(self):
        self.ai_service = AIServiceBase()
        self.analyzer = AIAnalyzer()
        self.cache_timeout = 3600
        
    def generate_organizational_insights(self) -> Dict[str, Any]:
        """조직 전반의 인사이트 생성"""
        
        try:
            insights = []
            
            # 1. 인력 관련 인사이트
            workforce_insights = self._analyze_workforce()
            insights.extend(workforce_insights)
            
            # 2. 성과 관련 인사이트
            performance_insights = self._analyze_performance()
            insights.extend(performance_insights)
            
            # 3. 이직 위험 인사이트
            turnover_insights = self._analyze_turnover_risks()
            insights.extend(turnover_insights)
            
            # 4. 다양성 인사이트
            diversity_insights = self._analyze_diversity()
            insights.extend(diversity_insights)
            
            # 5. 교육 및 개발 인사이트
            development_insights = self._analyze_development()
            insights.extend(development_insights)
            
            # 인사이트 저장
            saved_insights = []
            for insight_data in insights:
                insight = self._save_insight(insight_data)
                if insight:
                    saved_insights.append(insight)
            
            # 일일 메트릭 업데이트
            self._update_daily_metrics()
            
            return {
                'success': True,
                'total_insights': len(saved_insights),
                'categories': self._categorize_insights(saved_insights),
                'priority_breakdown': self._get_priority_breakdown(saved_insights),
                'top_insights': self._get_top_insights(saved_insights, 5),
                'action_items_generated': self._count_action_items(saved_insights)
            }
            
        except Exception as e:
            logger.error(f"Error generating organizational insights: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_workforce(self) -> List[Dict]:
        """인력 분석 인사이트"""
        
        insights = []
        
        # 전체 직원 수
        total_employees = Employee.objects.filter(status='ACTIVE').count()
        
        # 부서별 분포
        dept_distribution = Employee.objects.filter(
            status='ACTIVE'
        ).values('department').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 불균형 체크
        if dept_distribution:
            max_dept = dept_distribution[0]['count']
            min_dept = dept_distribution[len(dept_distribution)-1]['count']
            
            if max_dept > min_dept * 2:
                insights.append({
                    'title': '부서 간 인력 불균형 감지',
                    'category': 'workforce',
                    'priority': 'HIGH',
                    'confidence_score': 0.85,
                    'key_findings': {
                        'max_department_size': max_dept,
                        'min_department_size': min_dept,
                        'imbalance_ratio': max_dept / min_dept
                    },
                    'recommendations': [
                        '부서 간 인력 재배치 검토',
                        '채용 계획 조정',
                        '업무량 분석 실시'
                    ],
                    'impact_score': 0.7
                })
        
        # 신입 비율
        new_employees = Employee.objects.filter(
            status='ACTIVE',
            hire_date__gte=timezone.now() - timedelta(days=365)
        ).count()
        
        new_ratio = (new_employees / total_employees * 100) if total_employees > 0 else 0
        
        if new_ratio > 30:
            insights.append({
                'title': '높은 신입 직원 비율',
                'category': 'workforce',
                'priority': 'MEDIUM',
                'confidence_score': 0.9,
                'key_findings': {
                    'new_employee_ratio': new_ratio,
                    'new_employees': new_employees,
                    'total_employees': total_employees
                },
                'recommendations': [
                    '온보딩 프로그램 강화',
                    '멘토링 시스템 활성화',
                    '신입 직원 적응도 모니터링'
                ],
                'impact_score': 0.6
            })
        
        return insights
    
    def _analyze_performance(self) -> List[Dict]:
        """성과 분석 인사이트"""
        
        insights = []
        
        # 여기서는 더미 데이터 사용 (실제로는 성과 테이블에서 조회)
        import random
        avg_performance = random.uniform(65, 85)
        
        if avg_performance < 70:
            insights.append({
                'title': '전사 성과 개선 필요',
                'category': 'performance',
                'priority': 'CRITICAL',
                'confidence_score': 0.75,
                'key_findings': {
                    'average_performance': avg_performance,
                    'below_average_percentage': 45
                },
                'recommendations': [
                    '성과 관리 시스템 재검토',
                    '목표 설정 프로세스 개선',
                    '성과 코칭 프로그램 도입'
                ],
                'impact_score': 0.9
            })
        
        # 부서별 성과 격차
        performance_variance = random.uniform(10, 30)
        
        if performance_variance > 20:
            insights.append({
                'title': '부서 간 성과 격차 확대',
                'category': 'performance',
                'priority': 'HIGH',
                'confidence_score': 0.8,
                'key_findings': {
                    'performance_variance': performance_variance,
                    'top_department': 'Sales',
                    'bottom_department': 'Operations'
                },
                'recommendations': [
                    '우수 부서 벤치마킹',
                    '부진 부서 집중 지원',
                    '성과 격차 원인 분석'
                ],
                'impact_score': 0.75
            })
        
        return insights
    
    def _analyze_turnover_risks(self) -> List[Dict]:
        """이직 위험 분석 인사이트"""
        
        insights = []
        
        # 고위험군 직원 수
        high_risk_employees = TurnoverRisk.objects.filter(
            status='ACTIVE',
            risk_level__in=['HIGH', 'CRITICAL']
        ).count()
        
        total_employees = Employee.objects.filter(status='ACTIVE').count()
        risk_ratio = (high_risk_employees / total_employees * 100) if total_employees > 0 else 0
        
        if risk_ratio > 15:
            insights.append({
                'title': '이직 위험 증가 경고',
                'category': 'retention',
                'priority': 'CRITICAL',
                'confidence_score': 0.85,
                'key_findings': {
                    'high_risk_employees': high_risk_employees,
                    'risk_ratio': risk_ratio,
                    'estimated_cost': high_risk_employees * 100000  # 예상 비용
                },
                'recommendations': [
                    '긴급 리텐션 프로그램 실행',
                    '1:1 면담 실시',
                    '보상 체계 재검토'
                ],
                'impact_score': 0.95
            })
        
        # 부서별 이직 위험
        dept_risks = TurnoverRisk.objects.filter(
            status='ACTIVE',
            risk_level__in=['HIGH', 'CRITICAL']
        ).values('employee__department').annotate(
            count=Count('id')
        ).order_by('-count')
        
        if dept_risks and dept_risks[0]['count'] > 5:
            insights.append({
                'title': f"{dept_risks[0]['employee__department']} 부서 이직 위험 집중",
                'category': 'retention',
                'priority': 'HIGH',
                'confidence_score': 0.8,
                'key_findings': {
                    'department': dept_risks[0]['employee__department'],
                    'at_risk_count': dept_risks[0]['count']
                },
                'recommendations': [
                    '부서별 맞춤 대응책 수립',
                    '부서장 면담 실시',
                    '근무 환경 개선'
                ],
                'impact_score': 0.8
            })
        
        return insights
    
    def _analyze_diversity(self) -> List[Dict]:
        """다양성 분석 인사이트"""
        
        insights = []
        
        # 성별 다양성 (더미 데이터)
        import random
        gender_ratio = random.uniform(0.3, 0.7)
        
        if gender_ratio < 0.4 or gender_ratio > 0.6:
            insights.append({
                'title': '성별 다양성 개선 필요',
                'category': 'diversity',
                'priority': 'MEDIUM',
                'confidence_score': 0.7,
                'key_findings': {
                    'gender_ratio': gender_ratio,
                    'diversity_index': 0.65
                },
                'recommendations': [
                    '다양성 채용 정책 강화',
                    '포용적 문화 구축',
                    '다양성 교육 실시'
                ],
                'impact_score': 0.5
            })
        
        # 연령 다양성
        age_groups = Employee.objects.filter(status='ACTIVE').extra(
            select={'age_group': 
                "CASE WHEN EXTRACT(year FROM age(birth_date)) < 30 THEN '20대' "
                "WHEN EXTRACT(year FROM age(birth_date)) < 40 THEN '30대' "
                "WHEN EXTRACT(year FROM age(birth_date)) < 50 THEN '40대' "
                "ELSE '50대 이상' END"}
        ).values('age_group').annotate(count=Count('id')) if Employee.objects.filter(status='ACTIVE').exists() else []
        
        if len(age_groups) < 3:
            insights.append({
                'title': '연령 다양성 부족',
                'category': 'diversity',
                'priority': 'LOW',
                'confidence_score': 0.65,
                'key_findings': {
                    'age_group_count': len(age_groups)
                },
                'recommendations': [
                    '다양한 연령대 채용',
                    '세대 간 협업 프로그램',
                    '멘토링 시스템 구축'
                ],
                'impact_score': 0.4
            })
        
        return insights
    
    def _analyze_development(self) -> List[Dict]:
        """교육 및 개발 인사이트"""
        
        insights = []
        
        # 교육 참여율 (더미 데이터)
        import random
        training_participation = random.uniform(40, 80)
        
        if training_participation < 50:
            insights.append({
                'title': '낮은 교육 참여율',
                'category': 'development',
                'priority': 'MEDIUM',
                'confidence_score': 0.75,
                'key_findings': {
                    'participation_rate': training_participation,
                    'average_hours': 15
                },
                'recommendations': [
                    '교육 프로그램 재설계',
                    '학습 인센티브 제공',
                    '업무 시간 중 교육 시간 보장'
                ],
                'impact_score': 0.6
            })
        
        # 스킬 갭 분석
        skill_gap = random.uniform(20, 50)
        
        if skill_gap > 30:
            insights.append({
                'title': '핵심 역량 격차 확대',
                'category': 'development',
                'priority': 'HIGH',
                'confidence_score': 0.7,
                'key_findings': {
                    'skill_gap_percentage': skill_gap,
                    'critical_skills': ['디지털', 'AI', '데이터분석']
                },
                'recommendations': [
                    '역량 개발 로드맵 수립',
                    '외부 전문가 초빙',
                    '실무 중심 교육 강화'
                ],
                'impact_score': 0.75
            })
        
        return insights
    
    def _save_insight(self, insight_data: Dict) -> Optional[AIInsight]:
        """인사이트 저장"""
        
        try:
            # 중복 체크 (같은 제목의 인사이트가 오늘 이미 있는지)
            existing = AIInsight.objects.filter(
                title=insight_data['title'],
                created_at__date=timezone.now().date()
            ).first()
            
            if existing:
                # 기존 인사이트 업데이트
                existing.confidence_score = insight_data['confidence_score']
                existing.impact_score = insight_data['impact_score']
                existing.save()
                return existing
            
            # 새 인사이트 생성
            insight = AIInsight.objects.create(
                title=insight_data['title'],
                category=insight_data['category'],
                priority=insight_data['priority'].upper(),
                confidence_score=insight_data['confidence_score'],
                data_sources=['Employee Data', 'Performance Metrics', 'AI Analysis'],
                key_findings=insight_data['key_findings'],
                recommendations=insight_data['recommendations'],
                impact_score=insight_data['impact_score'],
                created_by='AI_ENGINE',
                status='NEW'
            )
            
            # 액션 아이템 생성
            for idx, recommendation in enumerate(insight_data['recommendations'][:3]):
                ActionItem.objects.create(
                    insight=insight,
                    title=recommendation,
                    description=f"AI 추천 액션: {recommendation}",
                    priority=insight_data['priority'].upper(),
                    status='PENDING',
                    assigned_to='HR Team',
                    due_date=timezone.now().date() + timedelta(days=7 * (idx + 1))
                )
            
            return insight
            
        except Exception as e:
            logger.error(f"Error saving insight: {e}")
            return None
    
    def _update_daily_metrics(self):
        """일일 메트릭 업데이트"""
        
        try:
            today = timezone.now().date()
            
            # 오늘의 메트릭 계산
            total_employees = Employee.objects.filter(status='ACTIVE').count()
            new_hires = Employee.objects.filter(
                hire_date=today
            ).count()
            
            # 이직 위험
            high_risk = TurnoverRisk.objects.filter(
                status='ACTIVE',
                risk_level__in=['HIGH', 'CRITICAL']
            ).count()
            
            # 메트릭 저장 또는 업데이트
            metrics, created = DailyMetrics.objects.update_or_create(
                date=today,
                defaults={
                    'total_employees': total_employees,
                    'new_hires': new_hires,
                    'terminations': 0,  # 실제 데이터 필요
                    'headcount_change': new_hires,
                    'avg_tenure': Employee.objects.filter(
                        status='ACTIVE'
                    ).aggregate(
                        avg=Avg(F('years_of_service'))
                    )['avg'] or 0,
                    'turnover_rate': (high_risk / total_employees * 100) if total_employees > 0 else 0,
                    'performance_index': 75.0,  # 더미
                    'engagement_score': 70.0,  # 더미
                    'training_hours': 8.0,  # 더미
                    'diversity_index': 0.65  # 더미
                }
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error updating daily metrics: {e}")
            return None
    
    def _categorize_insights(self, insights: List[AIInsight]) -> Dict[str, int]:
        """인사이트 카테고리별 분류"""
        
        categories = defaultdict(int)
        for insight in insights:
            categories[insight.category] += 1
        return dict(categories)
    
    def _get_priority_breakdown(self, insights: List[AIInsight]) -> Dict[str, int]:
        """우선순위별 분류"""
        
        priorities = defaultdict(int)
        for insight in insights:
            priorities[insight.priority] += 1
        return dict(priorities)
    
    def _get_top_insights(self, insights: List[AIInsight], limit: int = 5) -> List[Dict]:
        """상위 인사이트 추출"""
        
        # 영향도와 신뢰도 기준 정렬
        sorted_insights = sorted(
            insights,
            key=lambda x: x.impact_score * x.confidence_score,
            reverse=True
        )
        
        return [
            {
                'id': insight.id,
                'title': insight.title,
                'category': insight.category,
                'priority': insight.priority,
                'impact_score': insight.impact_score,
                'confidence_score': insight.confidence_score
            }
            for insight in sorted_insights[:limit]
        ]
    
    def _count_action_items(self, insights: List[AIInsight]) -> int:
        """액션 아이템 수 계산"""
        
        return ActionItem.objects.filter(
            insight__in=insights
        ).count()
    
    def get_insight_trends(self, days: int = 30) -> Dict[str, Any]:
        """인사이트 트렌드 분석"""
        
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            # 일별 인사이트 수
            daily_counts = AIInsight.objects.filter(
                created_at__gte=start_date
            ).extra(
                select={'date': 'DATE(created_at)'}
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date')
            
            # 카테고리별 트렌드
            category_trends = AIInsight.objects.filter(
                created_at__gte=start_date
            ).values('category').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # 평균 영향도 추이
            impact_trend = AIInsight.objects.filter(
                created_at__gte=start_date
            ).extra(
                select={'date': 'DATE(created_at)'}
            ).values('date').annotate(
                avg_impact=Avg('impact_score')
            ).order_by('date')
            
            return {
                'success': True,
                'period_days': days,
                'total_insights': sum(d['count'] for d in daily_counts),
                'daily_average': sum(d['count'] for d in daily_counts) / max(len(daily_counts), 1),
                'daily_counts': list(daily_counts),
                'category_distribution': list(category_trends),
                'impact_trend': list(impact_trend),
                'top_categories': [c['category'] for c in category_trends[:3]]
            }
            
        except Exception as e:
            logger.error(f"Error getting insight trends: {e}")
            return {'success': False, 'error': str(e)}