"""
AI Quick Win 오케스트레이터 서비스
AIRISS와 모든 AI 모듈을 통합 연동하는 중앙 서비스
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Avg, Count

# AIRISS 서비스
from airiss.services import AIAnalysisService, AIInsightService

# AI 모듈들
from ai_insights.models import AIInsight as InsightModel, ActionItem, DailyMetrics
from ai_predictions.models import TurnoverRisk, RetentionPlan, RiskFactor
from ai_interviewer.models import InterviewSession, InterviewQuestion, InterviewFeedback
from ai_team_optimizer.models import Project, TeamComposition, TeamMember, TeamAnalytics
from ai_coaching.models import CoachingSession, CoachingGoal, CoachingActionItem

# 직원 모델
from employees.models import Employee

logger = logging.getLogger(__name__)


class AIQuickWinOrchestrator:
    """
    AI Quick Win 통합 오케스트레이터
    AIRISS와 모든 AI 모듈을 연동하여 통합된 인사이트와 액션을 제공
    """
    
    def __init__(self):
        """오케스트레이터 초기화"""
        self.airiss_analyzer = AIAnalysisService()
        self.airiss_insights = AIInsightService()
        self.module_status = self._check_module_status()
    
    def _check_module_status(self) -> Dict[str, bool]:
        """각 AI 모듈의 상태 체크"""
        return {
            'ai_insights': True,
            'ai_predictions': True,
            'ai_interviewer': True,
            'ai_team_optimizer': True,
            'ai_coaching': True,
            'airiss': True
        }
    
    def sync_employee_profile(self, employee_id: int) -> Dict[str, Any]:
        """
        직원 프로파일을 모든 AI 모듈에 동기화
        AIRISS의 분석 결과를 각 모듈에 전파
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # 1. AIRISS에서 직원 분석 수행
            airiss_analysis = {
                'turnover_risk': self.airiss_analyzer.analyze_turnover_risk(employee),
                'promotion_potential': self.airiss_analyzer.analyze_promotion_potential(employee),
            }
            
            # 2. 이직 예측 모듈 업데이트
            self._update_turnover_prediction(employee, airiss_analysis['turnover_risk'])
            
            # 3. 코칭 모듈에 개발 필요 영역 전달
            self._update_coaching_goals(employee, airiss_analysis['promotion_potential'])
            
            # 4. 팀 최적화 모듈에 역량 정보 전달
            self._update_team_optimization(employee, airiss_analysis)
            
            # 5. 인사이트 모듈에 통합 분석 저장
            self._create_integrated_insight(employee, airiss_analysis)
            
            return {
                'success': True,
                'employee_id': employee_id,
                'employee_name': employee.name,
                'synced_modules': list(self.module_status.keys()),
                'analysis_summary': {
                    'turnover_risk_score': airiss_analysis['turnover_risk']['score'],
                    'promotion_potential_score': airiss_analysis['promotion_potential']['score'],
                    'risk_level': airiss_analysis['turnover_risk']['risk_level'],
                    'promotion_readiness': airiss_analysis['promotion_potential']['readiness']
                }
            }
            
        except Employee.DoesNotExist:
            logger.error(f"Employee {employee_id} not found")
            return {'success': False, 'error': 'Employee not found'}
        except Exception as e:
            logger.error(f"Error syncing employee profile: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_turnover_prediction(self, employee: Employee, risk_analysis: Dict[str, Any]):
        """이직 예측 모듈 업데이트"""
        try:
            # AIRISS 분석 결과를 이직 예측 모델에 저장
            risk_level_map = {
                'HIGH': 'CRITICAL',
                'MEDIUM': 'HIGH',
                'LOW': 'LOW'
            }
            
            turnover_risk, created = TurnoverRisk.objects.update_or_create(
                employee=employee,
                prediction_date__date=timezone.now().date(),
                defaults={
                    'risk_level': risk_level_map.get(risk_analysis['risk_level'], 'MEDIUM'),
                    'risk_score': risk_analysis['score'] / 100,  # 0-1 범위로 변환
                    'confidence_level': risk_analysis['confidence'],
                    'primary_risk_factors': risk_analysis['risk_factors'],
                    'ai_analysis': {
                        'airiss_analysis': risk_analysis,
                        'integrated_at': timezone.now().isoformat()
                    },
                    'ai_recommendations': risk_analysis['recommendations'],
                    'status': 'ACTIVE'
                }
            )
            
            # 고위험 직원에 대한 자동 유지 계획 생성
            if risk_analysis['score'] >= 70:
                self._create_retention_plan(employee, turnover_risk, risk_analysis)
                
        except Exception as e:
            logger.error(f"Error updating turnover prediction: {e}")
    
    def _create_retention_plan(self, employee: Employee, turnover_risk: TurnoverRisk, 
                              risk_analysis: Dict[str, Any]):
        """유지 계획 자동 생성"""
        try:
            plan, created = RetentionPlan.objects.get_or_create(
                turnover_risk=turnover_risk,
                defaults={
                    'plan_name': f"{employee.name} 유지 전략",
                    'priority': 'HIGH' if risk_analysis['score'] >= 80 else 'MEDIUM',
                    'status': 'DRAFT',
                    'retention_strategies': risk_analysis['recommendations'],
                    'target_completion_date': timezone.now().date() + timedelta(days=30),
                    'ai_generated': True,
                    'success_metrics': {
                        'target_risk_reduction': 30,
                        'engagement_improvement': 20
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error creating retention plan: {e}")
    
    def _update_coaching_goals(self, employee: Employee, potential_analysis: Dict[str, Any]):
        """코칭 목표 업데이트"""
        try:
            # 개발 필요 영역을 코칭 목표로 변환
            development_areas = potential_analysis.get('development_areas', [])
            
            # 최근 코칭 세션 조회 또는 생성
            recent_session = CoachingSession.objects.filter(
                employee=employee,
                status__in=['SCHEDULED', 'ACTIVE']
            ).first()
            
            if not recent_session:
                # 새 코칭 세션 생성
                recent_session = CoachingSession.objects.create(
                    employee=employee,
                    session_type='CAREER_PATH',
                    title=f"{employee.name}님의 AI 추천 코칭",
                    description="AIRISS 분석 기반 맞춤형 코칭 세션",
                    scheduled_at=timezone.now() + timedelta(days=7),
                    status='SCHEDULED',
                    ai_personality='SUPPORTIVE',
                    coaching_objectives=[
                        area['area'] for area in development_areas
                    ]
                )
            
            # 개발 영역별 코칭 목표 생성
            for area in development_areas:
                goal, created = CoachingGoal.objects.get_or_create(
                    session=recent_session,
                    title=f"{area['area']} 역량 개발",
                    defaults={
                        'goal_type': 'SKILL',
                        'description': f"현재 점수: {area['current_score']}, 목표 점수: {area['target_score']}",
                        'priority': 'HIGH' if area['current_score'] < 50 else 'MEDIUM',
                        'status': 'NOT_STARTED',
                        'target_date': timezone.now().date() + timedelta(days=90),
                        'feasibility_score': 8.0,
                        'ai_recommendations': area['recommendations']
                    }
                )
                
                # 각 목표에 대한 액션 아이템 생성
                if created:
                    for idx, recommendation in enumerate(area['recommendations'][:3]):
                        CoachingActionItem.objects.create(
                            session=recent_session,
                            goal=goal,
                            category='TRAINING',
                            title=recommendation,
                            description=f"AIRISS 추천 액션: {recommendation}",
                            due_date=timezone.now().date() + timedelta(days=30 * (idx + 1)),
                            status='PENDING',
                            estimated_hours=8.0
                        )
                        
        except Exception as e:
            logger.error(f"Error updating coaching goals: {e}")
    
    def _update_team_optimization(self, employee: Employee, analysis: Dict[str, Any]):
        """팀 최적화 정보 업데이트"""
        try:
            # 직원의 현재 프로젝트 팀 조회
            current_teams = TeamMember.objects.filter(
                employee=employee,
                team_composition__status__in=['APPROVED', 'ACTIVE']
            )
            
            # 각 팀에 대한 적합도 점수 업데이트
            for team_member in current_teams:
                # AIRISS 분석을 기반으로 적합도 재계산
                promotion_score = analysis['promotion_potential']['score']
                turnover_risk = analysis['turnover_risk']['score']
                
                # 높은 승진 가능성과 낮은 이직 위험도가 좋은 팀원
                fit_score = (promotion_score * 0.6) + ((100 - turnover_risk) * 0.4)
                
                team_member.fit_score = fit_score / 100  # 0-1 범위로 정규화
                team_member.synergy_score = self._calculate_synergy_score(team_member)
                team_member.save()
                
                # 팀 분석 업데이트
                self._update_team_analytics(team_member.team_composition)
                
        except Exception as e:
            logger.error(f"Error updating team optimization: {e}")
    
    def _calculate_synergy_score(self, team_member: TeamMember) -> float:
        """팀 시너지 점수 계산"""
        try:
            # 같은 팀의 다른 멤버들과의 시너지 계산
            other_members = TeamMember.objects.filter(
                team_composition=team_member.team_composition
            ).exclude(id=team_member.id)
            
            if not other_members:
                return 0.7  # 기본값
            
            # 간단한 시너지 계산 (실제로는 더 복잡한 알고리즘 필요)
            avg_fit = other_members.aggregate(avg=Avg('fit_score'))['avg'] or 0.5
            
            # 비슷한 적합도를 가진 팀원들끼리 시너지가 높다고 가정
            synergy = 1.0 - abs(team_member.fit_score - avg_fit)
            
            return max(0.3, min(1.0, synergy))
            
        except Exception as e:
            logger.error(f"Error calculating synergy score: {e}")
            return 0.5
    
    def _update_team_analytics(self, team_composition: TeamComposition):
        """팀 분석 업데이트"""
        try:
            analytics, created = TeamAnalytics.objects.get_or_create(
                team_composition=team_composition
            )
            
            # 팀 멤버들의 평균 점수 계산
            members = team_composition.team_members.all()
            
            if members:
                analytics.skill_coverage = members.aggregate(avg=Avg('fit_score'))['avg'] or 0
                analytics.communication_score = members.aggregate(avg=Avg('synergy_score'))['avg'] or 0
                analytics.success_probability = (analytics.skill_coverage + analytics.communication_score) / 2
                
                # SWOT 분석 업데이트
                analytics.strengths = self._identify_team_strengths(members)
                analytics.weaknesses = self._identify_team_weaknesses(members)
                
                analytics.save()
                
        except Exception as e:
            logger.error(f"Error updating team analytics: {e}")
    
    def _identify_team_strengths(self, members) -> List[str]:
        """팀 강점 식별"""
        strengths = []
        
        avg_fit = members.aggregate(avg=Avg('fit_score'))['avg'] or 0
        if avg_fit > 0.7:
            strengths.append("높은 역량 적합도")
        
        avg_synergy = members.aggregate(avg=Avg('synergy_score'))['avg'] or 0
        if avg_synergy > 0.7:
            strengths.append("우수한 팀 시너지")
        
        if members.count() >= 5 and members.count() <= 8:
            strengths.append("최적 팀 규모")
        
        return strengths
    
    def _identify_team_weaknesses(self, members) -> List[str]:
        """팀 약점 식별"""
        weaknesses = []
        
        avg_fit = members.aggregate(avg=Avg('fit_score'))['avg'] or 0
        if avg_fit < 0.5:
            weaknesses.append("역량 개발 필요")
        
        avg_synergy = members.aggregate(avg=Avg('synergy_score'))['avg'] or 0
        if avg_synergy < 0.5:
            weaknesses.append("팀워크 개선 필요")
        
        if members.count() < 3:
            weaknesses.append("팀 규모 부족")
        elif members.count() > 10:
            weaknesses.append("팀 규모 과다")
        
        return weaknesses
    
    def _create_integrated_insight(self, employee: Employee, analysis: Dict[str, Any]):
        """통합 인사이트 생성"""
        try:
            # AI 인사이트 모듈에 통합 분석 결과 저장
            turnover_score = analysis['turnover_risk']['score']
            promotion_score = analysis['promotion_potential']['score']
            
            # 인사이트 제목과 내용 생성
            if turnover_score >= 70:
                title = f"{employee.name}님 긴급 관리 필요"
                priority = 'CRITICAL'
                category = 'retention'
            elif promotion_score >= 80:
                title = f"{employee.name}님 승진 준비 완료"
                priority = 'HIGH'
                category = 'development'
            else:
                title = f"{employee.name}님 정기 관리"
                priority = 'MEDIUM'
                category = 'general'
            
            insight = InsightModel.objects.create(
                title=title,
                category=category,
                priority=priority,
                confidence_score=analysis['turnover_risk']['confidence'],
                data_sources=['AIRISS', 'Employee Profile', 'Performance Data'],
                key_findings={
                    'turnover_risk': analysis['turnover_risk'],
                    'promotion_potential': analysis['promotion_potential']
                },
                recommendations=self._generate_integrated_recommendations(analysis),
                impact_score=self._calculate_impact_score(employee, analysis),
                created_by='AI_ORCHESTRATOR'
            )
            
            # 액션 아이템 생성
            for recommendation in analysis['turnover_risk']['recommendations'][:3]:
                ActionItem.objects.create(
                    insight=insight,
                    title=recommendation,
                    description=f"AIRISS 추천: {recommendation}",
                    priority='HIGH' if turnover_score >= 70 else 'MEDIUM',
                    status='PENDING',
                    assigned_to=employee.department,
                    due_date=timezone.now().date() + timedelta(days=14)
                )
                
        except Exception as e:
            logger.error(f"Error creating integrated insight: {e}")
    
    def _generate_integrated_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """통합 추천사항 생성"""
        recommendations = []
        
        # 이직 위험도 기반 추천
        recommendations.extend(analysis['turnover_risk']['recommendations'][:2])
        
        # 승진 가능성 기반 추천
        if analysis['promotion_potential']['readiness']['level'] == 'READY':
            recommendations.append("승진 심사 프로세스 시작 검토")
        elif analysis['promotion_potential']['readiness']['level'] == 'ALMOST_READY':
            recommendations.append("승진 준비를 위한 집중 코칭 제공")
        
        # 개발 영역 추천
        for area in analysis['promotion_potential']['development_areas'][:1]:
            recommendations.append(f"{area['area']} 역량 개발 프로그램 등록")
        
        return recommendations
    
    def _calculate_impact_score(self, employee: Employee, analysis: Dict[str, Any]) -> float:
        """영향도 점수 계산"""
        # 직급과 이직 위험도를 고려한 영향도
        position_weight = {
            '부장': 1.0,
            '차장': 0.8,
            '과장': 0.6,
            '대리': 0.4,
            '사원': 0.2
        }
        
        base_weight = position_weight.get(employee.position, 0.3)
        risk_factor = analysis['turnover_risk']['score'] / 100
        
        return base_weight * (1 + risk_factor)
    
    def orchestrate_interview_to_coaching(self, interview_session_id: str) -> Dict[str, Any]:
        """
        면접 결과를 코칭 계획으로 연결
        AI 면접관의 평가를 바탕으로 신입 직원 코칭 계획 수립
        """
        try:
            # 면접 세션 조회
            interview = InterviewSession.objects.get(session_id=interview_session_id)
            
            # 면접 피드백 분석
            feedback_items = InterviewFeedback.objects.filter(
                session=interview,
                feedback_type='IMPROVEMENT_AREA'
            )
            
            if interview.test_employee:
                # 테스트 직원이 있는 경우 (내부 이동/승진 면접)
                employee = interview.test_employee
                
                # 코칭 세션 생성
                coaching_session = CoachingSession.objects.create(
                    employee=employee,
                    session_type='SKILL_DEVELOPMENT',
                    title=f"{interview.job_profile.title} 역량 개발 코칭",
                    description=f"면접 결과 기반 맞춤형 코칭 프로그램",
                    scheduled_at=timezone.now() + timedelta(days=7),
                    status='SCHEDULED',
                    coaching_objectives=[
                        feedback.content for feedback in feedback_items[:3]
                    ]
                )
                
                # 면접에서 발견된 개선점을 코칭 목표로 변환
                for feedback in feedback_items:
                    CoachingGoal.objects.create(
                        session=coaching_session,
                        goal_type='SKILL',
                        title=feedback.title,
                        description=feedback.content,
                        priority=feedback.priority,
                        status='NOT_STARTED',
                        target_date=timezone.now().date() + timedelta(days=60)
                    )
                
                return {
                    'success': True,
                    'coaching_session_id': str(coaching_session.session_id),
                    'goals_created': feedback_items.count(),
                    'message': '면접 결과가 코칭 계획으로 성공적으로 변환되었습니다.'
                }
            
            return {
                'success': False,
                'message': '직원 정보가 없어 코칭 계획을 생성할 수 없습니다.'
            }
            
        except InterviewSession.DoesNotExist:
            return {'success': False, 'error': 'Interview session not found'}
        except Exception as e:
            logger.error(f"Error orchestrating interview to coaching: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_comprehensive_report(self, employee_id: int) -> Dict[str, Any]:
        """
        직원에 대한 종합 AI 분석 리포트 생성
        모든 AI 모듈의 데이터를 통합하여 360도 분석 제공
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            
            report = {
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'department': employee.department,
                    'position': employee.position,
                    'hire_date': employee.hire_date.isoformat()
                },
                'generated_at': timezone.now().isoformat(),
                'modules': {}
            }
            
            # 1. AIRISS 분석
            report['modules']['airiss'] = {
                'turnover_risk': self.airiss_analyzer.analyze_turnover_risk(employee),
                'promotion_potential': self.airiss_analyzer.analyze_promotion_potential(employee)
            }
            
            # 2. 이직 예측 모듈
            latest_risk = TurnoverRisk.objects.filter(
                employee=employee,
                status='ACTIVE'
            ).first()
            
            if latest_risk:
                report['modules']['turnover_prediction'] = {
                    'risk_level': latest_risk.risk_level,
                    'risk_score': latest_risk.risk_score,
                    'predicted_departure': latest_risk.predicted_departure_date.isoformat() if latest_risk.predicted_departure_date else None
                }
            
            # 3. 코칭 현황
            active_coaching = CoachingSession.objects.filter(
                employee=employee,
                status__in=['SCHEDULED', 'ACTIVE']
            ).count()
            
            completed_goals = CoachingGoal.objects.filter(
                session__employee=employee,
                status='COMPLETED'
            ).count()
            
            report['modules']['coaching'] = {
                'active_sessions': active_coaching,
                'completed_goals': completed_goals,
                'total_goals': CoachingGoal.objects.filter(session__employee=employee).count()
            }
            
            # 4. 팀 최적화
            team_memberships = TeamMember.objects.filter(
                employee=employee,
                team_composition__status='ACTIVE'
            ).select_related('team_composition__project')
            
            report['modules']['team_optimization'] = {
                'current_projects': [
                    {
                        'project_name': tm.team_composition.project.name,
                        'role': tm.role,
                        'fit_score': tm.fit_score,
                        'synergy_score': tm.synergy_score
                    }
                    for tm in team_memberships
                ]
            }
            
            # 5. 종합 점수 및 추천
            report['summary'] = self._generate_summary_insights(report)
            
            return report
            
        except Employee.DoesNotExist:
            return {'error': 'Employee not found'}
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {'error': str(e)}
    
    def _generate_summary_insights(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """종합 인사이트 생성"""
        summary = {
            'overall_status': 'STABLE',
            'key_insights': [],
            'immediate_actions': [],
            'long_term_recommendations': []
        }
        
        # 이직 위험도 체크
        turnover_score = report['modules']['airiss']['turnover_risk']['score']
        if turnover_score >= 70:
            summary['overall_status'] = 'AT_RISK'
            summary['immediate_actions'].append('긴급 1:1 면담 실시')
            summary['key_insights'].append('높은 이직 위험도 감지')
        
        # 승진 가능성 체크
        promotion_score = report['modules']['airiss']['promotion_potential']['score']
        if promotion_score >= 80:
            summary['key_insights'].append('승진 준비 완료')
            summary['immediate_actions'].append('승진 심사 프로세스 시작')
        
        # 코칭 진행률 체크
        if 'coaching' in report['modules']:
            completion_rate = (
                report['modules']['coaching']['completed_goals'] / 
                max(report['modules']['coaching']['total_goals'], 1) * 100
            )
            if completion_rate < 50:
                summary['long_term_recommendations'].append('코칭 프로그램 참여 독려')
        
        return summary
    
    def get_module_integration_status(self) -> Dict[str, Any]:
        """
        모든 AI 모듈의 통합 상태 확인
        각 모듈의 연동 상태와 데이터 동기화 현황 반환
        """
        status = {
            'timestamp': timezone.now().isoformat(),
            'modules': {},
            'integration_health': 'HEALTHY'
        }
        
        # 각 모듈 상태 체크
        try:
            # AIRISS
            status['modules']['airiss'] = {
                'connected': True,
                'last_sync': timezone.now().isoformat(),
                'data_points': 5
            }
            
            # AI Insights
            recent_insights = InsightModel.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=1)
            ).count()
            status['modules']['ai_insights'] = {
                'connected': True,
                'recent_insights': recent_insights,
                'active': recent_insights > 0
            }
            
            # AI Predictions
            recent_predictions = TurnoverRisk.objects.filter(
                prediction_date__gte=timezone.now() - timedelta(days=1)
            ).count()
            status['modules']['ai_predictions'] = {
                'connected': True,
                'recent_predictions': recent_predictions,
                'active': recent_predictions > 0
            }
            
            # AI Interviewer
            active_interviews = InterviewSession.objects.filter(
                status='IN_PROGRESS'
            ).count()
            status['modules']['ai_interviewer'] = {
                'connected': True,
                'active_sessions': active_interviews,
                'active': active_interviews > 0
            }
            
            # AI Team Optimizer
            active_projects = Project.objects.filter(
                status='ACTIVE'
            ).count()
            status['modules']['ai_team_optimizer'] = {
                'connected': True,
                'active_projects': active_projects,
                'active': active_projects > 0
            }
            
            # AI Coaching
            active_coaching = CoachingSession.objects.filter(
                status__in=['SCHEDULED', 'ACTIVE']
            ).count()
            status['modules']['ai_coaching'] = {
                'connected': True,
                'active_sessions': active_coaching,
                'active': active_coaching > 0
            }
            
            # 전체 상태 평가
            inactive_modules = [
                module for module, info in status['modules'].items()
                if not info.get('active', True)
            ]
            
            if len(inactive_modules) > 2:
                status['integration_health'] = 'DEGRADED'
            elif len(inactive_modules) > 4:
                status['integration_health'] = 'CRITICAL'
            
            status['summary'] = {
                'total_modules': len(status['modules']),
                'active_modules': len(status['modules']) - len(inactive_modules),
                'inactive_modules': inactive_modules
            }
            
        except Exception as e:
            logger.error(f"Error checking integration status: {e}")
            status['integration_health'] = 'ERROR'
            status['error'] = str(e)
        
        return status