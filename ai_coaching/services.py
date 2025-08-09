"""
AI 코칭 서비스 레이어
개인별 맞춤 코칭 및 성장 계획 수립
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Avg, Count, Sum
from django.core.cache import cache

from .models import (
    CoachingSession, CoachingGoal, CoachingActionItem,
    CoachingFeedback, CoachingNote, CoachingResource
)
from employees.models import Employee
from ai_services.base import AIServiceBase, PerformancePredictor
from ai_predictions.models import TurnoverRisk

logger = logging.getLogger(__name__)


class AICoachingService:
    """AI 기반 코칭 서비스"""
    
    def __init__(self):
        self.ai_service = AIServiceBase()
        self.performance_predictor = PerformancePredictor()
        self.cache_timeout = 3600  # 1시간
        
    def create_personalized_coaching_plan(self, employee: Employee) -> Dict[str, Any]:
        """개인별 맞춤 코칭 계획 수립"""
        
        try:
            # 1. 직원 프로파일 분석
            profile_analysis = self._analyze_employee_profile(employee)
            
            # 2. 성장 필요 영역 식별
            growth_areas = self._identify_growth_areas(employee, profile_analysis)
            
            # 3. 코칭 세션 생성
            session = self._create_coaching_session(employee, growth_areas)
            
            # 4. 코칭 목표 설정
            goals = self._create_coaching_goals(session, growth_areas)
            
            # 5. 액션 아이템 생성
            action_items = self._create_action_items(session, goals)
            
            # 6. 리소스 추천
            resources = self._recommend_resources(session, growth_areas)
            
            return {
                'success': True,
                'session_id': str(session.session_id),
                'employee_name': employee.name,
                'coaching_type': session.session_type,
                'goals_count': len(goals),
                'action_items_count': len(action_items),
                'resources_count': len(resources),
                'estimated_duration_weeks': self._estimate_duration(goals),
                'priority_areas': [area['name'] for area in growth_areas[:3]],
                'ai_insights': self._generate_coaching_insights(employee, growth_areas)
            }
            
        except Exception as e:
            logger.error(f"Error creating coaching plan: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_employee_profile(self, employee: Employee) -> Dict[str, Any]:
        """직원 프로파일 종합 분석"""
        
        # 캐시 확인
        cache_key = f'employee_profile_{employee.id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': [],
            'performance_trend': 'stable',
            'engagement_level': 'medium',
            'learning_style': 'mixed'
        }
        
        # 강점 분석
        if employee.years_of_service > 5:
            analysis['strengths'].append({'area': '조직 충성도', 'score': 85})
        
        # 약점 분석 (이직 위험도 연계)
        recent_risk = TurnoverRisk.objects.filter(
            employee=employee,
            status='ACTIVE'
        ).first()
        
        if recent_risk and recent_risk.risk_score > 0.6:
            analysis['weaknesses'].append({'area': '이직 위험', 'score': recent_risk.risk_score * 100})
            analysis['threats'].append('높은 이직 가능성')
        
        # 기회 분석
        if employee.position in ['대리', '과장']:
            analysis['opportunities'].append({'area': '승진 가능성', 'score': 70})
        
        # 성과 추세
        # 실제로는 성과 데이터에서 계산
        import random
        analysis['performance_trend'] = random.choice(['improving', 'stable', 'declining'])
        
        # 캐시 저장
        cache.set(cache_key, analysis, self.cache_timeout)
        
        return analysis
    
    def _identify_growth_areas(self, employee: Employee, profile: Dict) -> List[Dict]:
        """성장 필요 영역 식별"""
        
        growth_areas = []
        
        # 리더십 개발 필요성
        if employee.position in ['과장', '차장', '부장']:
            growth_areas.append({
                'name': '리더십 역량',
                'priority': 'high',
                'current_level': 60,
                'target_level': 85,
                'gap': 25,
                'recommendations': [
                    '리더십 워크숍 참여',
                    '멘토링 프로그램 등록',
                    '팀 관리 실습'
                ]
            })
        
        # 기술 역량 개발
        growth_areas.append({
            'name': '디지털 역량',
            'priority': 'medium',
            'current_level': 50,
            'target_level': 80,
            'gap': 30,
            'recommendations': [
                'AI/ML 기초 교육',
                '데이터 분석 과정',
                '디지털 트랜스포메이션 이해'
            ]
        })
        
        # 소프트 스킬
        if profile['performance_trend'] == 'declining':
            growth_areas.append({
                'name': '커뮤니케이션',
                'priority': 'high',
                'current_level': 55,
                'target_level': 75,
                'gap': 20,
                'recommendations': [
                    '효과적인 소통 기법',
                    '프레젠테이션 스킬',
                    '갈등 관리'
                ]
            })
        
        # 우선순위 정렬
        growth_areas.sort(key=lambda x: x['gap'], reverse=True)
        
        return growth_areas
    
    def _create_coaching_session(self, employee: Employee, growth_areas: List[Dict]) -> CoachingSession:
        """코칭 세션 생성"""
        
        # 코칭 유형 결정
        if any(area['name'] == '리더십 역량' for area in growth_areas):
            session_type = 'LEADERSHIP'
        elif any(area['priority'] == 'high' for area in growth_areas):
            session_type = 'PERFORMANCE'
        else:
            session_type = 'SKILL_DEVELOPMENT'
        
        # AI 페르소나 선택
        ai_personality = 'SUPPORTIVE' if employee.years_of_service < 2 else 'CHALLENGING'
        
        session = CoachingSession.objects.create(
            employee=employee,
            session_type=session_type,
            title=f"{employee.name}님의 성장 여정",
            description=f"AI 기반 맞춤형 코칭 프로그램 - {', '.join([a['name'] for a in growth_areas[:3]])} 중심",
            scheduled_at=timezone.now() + timedelta(days=3),
            duration_minutes=60,
            status='SCHEDULED',
            ai_personality=ai_personality,
            session_format='HYBRID',
            coaching_objectives=[area['name'] for area in growth_areas[:5]],
            preparation_materials={
                'readings': [],
                'videos': [],
                'assessments': []
            }
        )
        
        return session
    
    def _create_coaching_goals(self, session: CoachingSession, growth_areas: List[Dict]) -> List[CoachingGoal]:
        """코칭 목표 생성"""
        
        goals = []
        
        for idx, area in enumerate(growth_areas[:5]):  # 최대 5개 목표
            # 목표 유형 결정
            if 'leadership' in area['name'].lower():
                goal_type = 'LEADERSHIP'
            elif 'performance' in area['name'].lower():
                goal_type = 'PERFORMANCE'
            else:
                goal_type = 'SKILL'
            
            goal = CoachingGoal.objects.create(
                session=session,
                goal_type=goal_type,
                title=f"{area['name']} 향상",
                description=f"현재 {area['current_level']}점에서 {area['target_level']}점으로 향상",
                priority=area['priority'].upper(),
                status='NOT_STARTED',
                target_date=timezone.now().date() + timedelta(days=30 * (idx + 1)),
                current_level=area['current_level'],
                target_level=area['target_level'],
                progress_percentage=0,
                feasibility_score=self._calculate_feasibility(area),
                required_resources=area['recommendations'],
                ai_recommendations=self._generate_goal_recommendations(area),
                success_criteria=[
                    f"{area['name']} 역량 {area['target_level']}점 달성",
                    "관련 교육 프로그램 이수",
                    "실무 적용 사례 3건 이상"
                ]
            )
            
            goals.append(goal)
        
        return goals
    
    def _calculate_feasibility(self, growth_area: Dict) -> float:
        """목표 달성 가능성 계산"""
        
        # 갭이 작을수록 달성 가능성 높음
        gap_score = max(0, 10 - growth_area['gap'] / 10)
        
        # 우선순위가 높을수록 지원이 많아 달성 가능성 높음
        priority_score = {'high': 9, 'medium': 7, 'low': 5}.get(growth_area['priority'], 5)
        
        return (gap_score + priority_score) / 2
    
    def _generate_goal_recommendations(self, growth_area: Dict) -> List[str]:
        """목표별 AI 추천사항 생성"""
        
        recommendations = growth_area['recommendations'].copy()
        
        # AI 추가 추천
        if growth_area['gap'] > 20:
            recommendations.append("집중 코칭 프로그램 참여 권장")
        
        if growth_area['priority'] == 'high':
            recommendations.append("주간 진척도 모니터링 필요")
        
        return recommendations
    
    def _create_action_items(self, session: CoachingSession, goals: List[CoachingGoal]) -> List[CoachingActionItem]:
        """액션 아이템 생성"""
        
        action_items = []
        
        for goal in goals:
            # 각 목표당 2-3개의 액션 아이템
            for i in range(min(3, len(goal.required_resources))):
                action_item = CoachingActionItem.objects.create(
                    session=session,
                    goal=goal,
                    category='TRAINING' if 'education' in goal.title.lower() else 'PRACTICE',
                    title=goal.required_resources[i] if i < len(goal.required_resources) else f"{goal.title} 실습 {i+1}",
                    description=f"{goal.title}을 위한 구체적 실행 계획",
                    due_date=timezone.now().date() + timedelta(days=7 * (i + 1)),
                    status='PENDING',
                    priority=goal.priority,
                    estimated_hours=8.0,
                    completion_criteria=[
                        "과정 이수 완료",
                        "실습 과제 제출",
                        "피드백 반영"
                    ]
                )
                
                action_items.append(action_item)
        
        return action_items
    
    def _recommend_resources(self, session: CoachingSession, growth_areas: List[Dict]) -> List[CoachingResource]:
        """학습 리소스 추천"""
        
        resources = []
        
        for area in growth_areas[:3]:
            # 각 성장 영역별 리소스 추천
            if 'leadership' in area['name'].lower():
                resource = CoachingResource.objects.create(
                    session=session,
                    resource_type='BOOK',
                    title='리더십의 5가지 원칙',
                    description='효과적인 리더십 개발을 위한 필독서',
                    url='https://example.com/leadership-book',
                    provider='HBR Press',
                    duration_hours=10.0,
                    difficulty_level='INTERMEDIATE',
                    is_mandatory=area['priority'] == 'high',
                    relevance_score=0.9
                )
            elif 'digital' in area['name'].lower():
                resource = CoachingResource.objects.create(
                    session=session,
                    resource_type='COURSE',
                    title='디지털 트랜스포메이션 마스터클래스',
                    description='DT 시대의 핵심 역량 개발',
                    url='https://example.com/dt-course',
                    provider='Coursera',
                    duration_hours=20.0,
                    difficulty_level='BEGINNER',
                    is_mandatory=True,
                    relevance_score=0.85
                )
            else:
                resource = CoachingResource.objects.create(
                    session=session,
                    resource_type='VIDEO',
                    title=f'{area["name"]} 스킬 향상 가이드',
                    description='실무 적용 가능한 스킬 개발 영상',
                    url='https://example.com/skill-video',
                    provider='LinkedIn Learning',
                    duration_hours=3.0,
                    difficulty_level='BEGINNER',
                    is_mandatory=False,
                    relevance_score=0.75
                )
            
            resources.append(resource)
        
        return resources
    
    def _estimate_duration(self, goals: List[CoachingGoal]) -> int:
        """코칭 기간 예측 (주 단위)"""
        
        if not goals:
            return 4
        
        # 목표 수와 난이도에 따라 기간 산정
        base_weeks = len(goals) * 2
        
        # 우선순위 높은 목표가 많으면 기간 증가
        high_priority_count = sum(1 for g in goals if g.priority == 'HIGH')
        
        return base_weeks + high_priority_count * 2
    
    def _generate_coaching_insights(self, employee: Employee, growth_areas: List[Dict]) -> List[str]:
        """AI 코칭 인사이트 생성"""
        
        insights = []
        
        # 직원 특성 기반 인사이트
        if employee.years_of_service < 2:
            insights.append("신입 직원으로서 기초 역량 구축이 중요합니다.")
        elif employee.years_of_service > 10:
            insights.append("경험을 바탕으로 리더십 역량 개발을 고려하세요.")
        
        # 성장 영역 기반 인사이트
        total_gap = sum(area['gap'] for area in growth_areas[:3])
        if total_gap > 60:
            insights.append("집중적인 코칭이 필요한 시기입니다.")
        
        # 우선순위 기반 인사이트
        high_priority = [a for a in growth_areas if a['priority'] == 'high']
        if len(high_priority) > 2:
            insights.append(f"{len(high_priority)}개의 긴급 개발 영역이 있습니다.")
        
        return insights
    
    def get_coaching_progress(self, session_id: str) -> Dict[str, Any]:
        """코칭 진행 상황 조회"""
        
        try:
            session = CoachingSession.objects.get(session_id=session_id)
            
            # 목표별 진행률
            goals = CoachingGoal.objects.filter(session=session)
            total_progress = goals.aggregate(avg=Avg('progress_percentage'))['avg'] or 0
            
            # 액션 아이템 완료율
            action_items = CoachingActionItem.objects.filter(session=session)
            completed_items = action_items.filter(status='COMPLETED').count()
            total_items = action_items.count()
            completion_rate = (completed_items / total_items * 100) if total_items > 0 else 0
            
            # 다음 마일스톤
            next_milestone = action_items.filter(
                status__in=['PENDING', 'IN_PROGRESS']
            ).order_by('due_date').first()
            
            return {
                'session_id': str(session.session_id),
                'status': session.status,
                'overall_progress': total_progress,
                'goals_count': goals.count(),
                'completed_goals': goals.filter(status='COMPLETED').count(),
                'action_items_completion': completion_rate,
                'next_milestone': {
                    'title': next_milestone.title if next_milestone else None,
                    'due_date': next_milestone.due_date.isoformat() if next_milestone else None
                },
                'insights': self._generate_progress_insights(session, total_progress, completion_rate)
            }
            
        except CoachingSession.DoesNotExist:
            return {'error': 'Session not found'}
        except Exception as e:
            logger.error(f"Error getting coaching progress: {e}")
            return {'error': str(e)}
    
    def _generate_progress_insights(self, session: CoachingSession, progress: float, completion: float) -> List[str]:
        """진행 상황 인사이트 생성"""
        
        insights = []
        
        if progress >= 75:
            insights.append("우수한 진행률을 보이고 있습니다!")
        elif progress >= 50:
            insights.append("순조롭게 진행 중입니다.")
        elif progress >= 25:
            insights.append("진행 속도를 높일 필요가 있습니다.")
        else:
            insights.append("코칭 참여도를 높여주세요.")
        
        if completion >= 80:
            insights.append("액션 아이템 실행력이 뛰어납니다.")
        elif completion < 30:
            insights.append("액션 아이템 실행에 집중이 필요합니다.")
        
        return insights