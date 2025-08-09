"""
AI Coaching Views - AI 실시간 코칭 어시스턴트 뷰
"""
import json
import logging
from typing import Dict, List, Any
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.utils import timezone
from employees.models import Employee
from .models import (
    CoachingSession, CoachingMessage, CoachingGoal, CoachingActionItem,
    CoachingFeedback, CoachingTemplate, CoachingMetrics
)

logger = logging.getLogger(__name__)


class CoachingDashboardView(TemplateView):
    """코칭 대시보드"""
    template_name = 'ai_coaching/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # 기본 통계 - 안전한 초기화
            context.update({
                'stats': self._get_coaching_stats(),
                'active_sessions': self._get_active_sessions(),
                'recent_sessions': self._get_recent_sessions(),
                'coaching_goals': self._get_coaching_goals(),
                'templates': self._get_templates()
            })
            
        except Exception as e:
            logger.error(f"코칭 대시보드 데이터 로드 오류: {e}")
            # 안전한 기본값 설정
            context.update({
                'stats': {
                    'total_sessions': 0,
                    'active_sessions': 0,
                    'completed_sessions': 0,
                    'completion_rate': 0,
                    'avg_satisfaction': 0
                },
                'active_sessions': [],
                'recent_sessions': [],
                'coaching_goals': [],
                'templates': []
            })
            context['error'] = '데이터베이스 초기화가 필요합니다.'
        
        return context
    
    def _get_coaching_stats(self):
        """코칭 통계 조회"""
        try:
            total_sessions = CoachingSession.objects.count()
            active_sessions = CoachingSession.objects.filter(status='ACTIVE').count()
            completed_sessions = CoachingSession.objects.filter(status='COMPLETED').count()
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'completed_sessions': completed_sessions,
                'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                'avg_satisfaction': CoachingSession.objects.filter(
                    satisfaction_score__gt=0
                ).aggregate(Avg('satisfaction_score'))['satisfaction_score__avg'] or 0
            }
        except Exception as e:
            logger.error(f"코칭 통계 조회 오류: {e}")
            return {
                'total_sessions': 0,
                'active_sessions': 0,
                'completed_sessions': 0,
                'completion_rate': 0,
                'avg_satisfaction': 0
            }
    
    def _get_active_sessions(self):
        """활성 세션 조회"""
        try:
            return CoachingSession.objects.filter(
                status__in=['SCHEDULED', 'ACTIVE']
            ).select_related('employee').order_by('scheduled_at')[:5]
        except Exception as e:
            logger.error(f"활성 세션 조회 오류: {e}")
            return []
    
    def _get_recent_sessions(self):
        """최근 세션 조회"""
        try:
            return CoachingSession.objects.filter(
                status='COMPLETED'
            ).select_related('employee').order_by('-ended_at')[:5]
        except Exception as e:
            logger.error(f"최근 세션 조회 오류: {e}")
            return []
    
    def _get_coaching_goals(self):
        """코칭 목표 조회"""
        try:
            return CoachingGoal.objects.filter(
                status__in=['NOT_STARTED', 'IN_PROGRESS']
            ).select_related('session', 'session__employee').order_by('target_date')[:10]
        except Exception as e:
            logger.error(f"코칭 목표 조회 오류: {e}")
            return []
    
    def _get_templates(self):
        """코칭 템플릿 조회"""
        try:
            return CoachingTemplate.objects.filter(is_active=True)[:5]
        except Exception as e:
            logger.error(f"코칭 템플릿 조회 오류: {e}")
            return []


@method_decorator(csrf_exempt, name='dispatch')
class StartCoachingView(View):
    """코칭 세션 시작 API"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            employee_id = data.get('employee_id')
            session_type = data.get('session_type', 'PERFORMANCE')
            title = data.get('title', 'AI 코칭 세션')
            
            employee = get_object_or_404(Employee, id=employee_id)
            
            # 코칭 세션 생성
            session = CoachingSession.objects.create(
                employee=employee,
                session_type=session_type,
                title=title,
                description=f"{employee.name}님의 {session_type} 코칭 세션",
                scheduled_at=timezone.now(),
                started_at=timezone.now(),
                status='ACTIVE',
                coaching_objectives=data.get('objectives', []),
                focus_areas=data.get('focus_areas', [])
            )
            
            # 환영 메시지 생성
            welcome_message = self._generate_welcome_message(session)
            CoachingMessage.objects.create(
                session=session,
                sender='AI_COACH',
                message_type='TEXT',
                content=welcome_message
            )
            
            return JsonResponse({
                'success': True,
                'session_id': str(session.session_id),
                'message': '코칭 세션이 시작되었습니다.',
                'welcome_message': welcome_message
            })
            
        except Exception as e:
            logger.error(f"코칭 세션 시작 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '코칭 세션 시작 중 오류가 발생했습니다.',
                'error': str(e)
            })
    
    def _generate_welcome_message(self, session):
        """환영 메시지 생성"""
        messages = {
            'PERFORMANCE': f"안녕하세요 {session.employee.name}님! 성과 코칭 세션을 시작합니다. 오늘은 어떤 성과 목표에 대해 이야기하고 싶으신가요?",
            'LEADERSHIP': f"반갑습니다 {session.employee.name}님! 리더십 코칭 세션입니다. 현재 리더로서 어떤 도전을 겪고 계신지 들어보겠습니다.",
            'SKILL_DEVELOPMENT': f"안녕하세요 {session.employee.name}님! 역량 개발 코칭을 시작합니다. 어떤 스킬을 향상시키고 싶으신가요?",
            'CAREER_PATH': f"환영합니다 {session.employee.name}님! 커리어 패스 코칭 세션입니다. 현재 커리어 목표와 계획에 대해 이야기해보세요."
        }
        return messages.get(session.session_type, f"안녕하세요 {session.employee.name}님! AI 코칭 세션을 시작합니다.")


@method_decorator(csrf_exempt, name='dispatch')
class SendMessageView(View):
    """메시지 전송 API"""
    
    def post(self, request, session_id):
        try:
            session = get_object_or_404(CoachingSession, session_id=session_id)
            data = json.loads(request.body)
            
            content = data.get('content', '').strip()
            if not content:
                return JsonResponse({
                    'success': False,
                    'message': '메시지 내용이 비어있습니다.'
                })
            
            # 직원 메시지 저장
            employee_message = CoachingMessage.objects.create(
                session=session,
                sender='EMPLOYEE',
                message_type='TEXT',
                content=content
            )
            
            # AI 응답 생성
            ai_response = self._generate_ai_response(session, content)
            ai_message = CoachingMessage.objects.create(
                session=session,
                sender='AI_COACH',
                message_type=ai_response['type'],
                content=ai_response['content'],
                key_insights=ai_response.get('insights', [])
            )
            
            return JsonResponse({
                'success': True,
                'employee_message': {
                    'id': employee_message.id,
                    'content': employee_message.content,
                    'timestamp': employee_message.timestamp.isoformat()
                },
                'ai_response': {
                    'id': ai_message.id,
                    'content': ai_message.content,
                    'type': ai_message.message_type,
                    'insights': ai_message.key_insights,
                    'timestamp': ai_message.timestamp.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"메시지 전송 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '메시지 전송 중 오류가 발생했습니다.',
                'error': str(e)
            })
    
    def _generate_ai_response(self, session, user_message):
        """AI 응답 생성"""
        try:
            # AI 응답 생성 로직 (실제로는 OpenAI API 호출)
            response_templates = {
                'PERFORMANCE': [
                    "성과에 대해 구체적으로 어떤 부분이 가장 중요하다고 생각하시나요?",
                    "목표 달성을 위해 어떤 지원이 필요하신가요?",
                    "현재 진행하고 있는 업무 중 가장 만족스러운 부분은 무엇인가요?"
                ],
                'LEADERSHIP': [
                    "팀을 이끌면서 가장 어려운 점은 무엇인가요?",
                    "리더로서 어떤 스타일을 선호하시나요?",
                    "팀원들과의 소통에서 개선하고 싶은 부분이 있나요?"
                ],
                'SKILL_DEVELOPMENT': [
                    "어떤 스킬을 가장 먼저 개발하고 싶으신가요?",
                    "현재 스킬 중 가장 자신 있는 분야는 무엇인가요?",
                    "스킬 개발을 위해 어떤 방법을 선호하시나요?"
                ],
                'CAREER_PATH': [
                    "3년 후 어떤 모습이 되고 싶으신가요?",
                    "현재 커리어에서 가장 중요하게 생각하는 가치는 무엇인가요?",
                    "커리어 발전을 위해 필요한 것들은 무엇이라고 생각하시나요?"
                ]
            }
            
            # 간단한 키워드 기반 응답
            templates = response_templates.get(session.session_type, [
                "더 자세히 설명해주실 수 있나요?",
                "그 부분에 대해 어떻게 생각하시나요?",
                "구체적인 예시를 들어주실 수 있나요?"
            ])
            
            import random
            response_content = random.choice(templates)
            
            return {
                'type': 'QUESTION',
                'content': response_content,
                'insights': ['사용자 참여도 높음', '추가 질문 필요']
            }
            
        except Exception as e:
            logger.error(f"AI 응답 생성 오류: {e}")
            return {
                'type': 'TEXT',
                'content': '죄송합니다. 응답을 생성하는 중 문제가 발생했습니다. 다시 시도해주세요.',
                'insights': []
            }


class SessionDetailView(TemplateView):
    """코칭 세션 상세"""
    template_name = 'ai_coaching/session_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = kwargs.get('session_id')
        
        try:
            session = get_object_or_404(CoachingSession, session_id=session_id)
            
            context.update({
                'session': session,
                'messages': session.messages.all().order_by('timestamp'),
                'goals': session.goals.all(),
                'action_items': session.action_items_detailed.all(),
                'feedback': session.feedback.all()
            })
            
        except Exception as e:
            logger.error(f"세션 상세 조회 오류: {e}")
            context['error'] = str(e)
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class EndSessionView(View):
    """세션 종료 API"""
    
    def post(self, request, session_id):
        try:
            session = get_object_or_404(CoachingSession, session_id=session_id)
            
            # 세션 종료 처리
            session.status = 'COMPLETED'
            session.ended_at = timezone.now()
            session.save()
            
            # 세션 요약 생성
            summary = self._generate_session_summary(session)
            
            # 요약 메시지 저장
            CoachingMessage.objects.create(
                session=session,
                sender='SYSTEM',
                message_type='SUMMARY',
                content=summary['content'],
                key_insights=summary['insights']
            )
            
            return JsonResponse({
                'success': True,
                'message': '코칭 세션이 종료되었습니다.',
                'session': {
                    'id': str(session.session_id),
                    'status': session.get_status_display(),
                    'duration': session.get_actual_duration(),
                    'summary': summary['content']
                }
            })
            
        except Exception as e:
            logger.error(f"세션 종료 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '세션 종료 중 오류가 발생했습니다.',
                'error': str(e)
            })
    
    def _generate_session_summary(self, session):
        """세션 요약 생성"""
        try:
            message_count = session.messages.count()
            goal_count = session.goals.count()
            duration = session.get_actual_duration()
            
            summary_content = f"""
세션 요약:
- 총 대화 수: {message_count}개
- 설정된 목표: {goal_count}개
- 세션 시간: {duration}분
- 주요 논의사항: {session.session_type} 관련 코칭

다음 세션까지 실행할 액션 아이템들을 검토해보시기 바랍니다.
            """
            
            insights = [
                f'총 {message_count}개 메시지 교환',
                f'{goal_count}개 목표 설정',
                f'{duration}분 세션 진행'
            ]
            
            return {
                'content': summary_content.strip(),
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"세션 요약 생성 오류: {e}")
            return {
                'content': '세션이 완료되었습니다.',
                'insights': []
            }


@method_decorator(csrf_exempt, name='dispatch')
class CreateGoalView(View):
    """목표 생성 API"""
    
    def post(self, request, session_id):
        try:
            session = get_object_or_404(CoachingSession, session_id=session_id)
            data = json.loads(request.body)
            
            goal = CoachingGoal.objects.create(
                session=session,
                goal_type=data.get('goal_type', 'PERFORMANCE'),
                title=data.get('title', ''),
                description=data.get('description', ''),
                priority=data.get('priority', 'MEDIUM'),
                target_date=data.get('target_date'),
                success_criteria=data.get('success_criteria', []),
                feasibility_score=data.get('feasibility_score', 8.0)
            )
            
            return JsonResponse({
                'success': True,
                'message': '목표가 생성되었습니다.',
                'goal': {
                    'id': goal.id,
                    'title': goal.title,
                    'type': goal.get_goal_type_display(),
                    'priority': goal.get_priority_display(),
                    'target_date': goal.target_date.isoformat() if goal.target_date else None
                }
            })
            
        except Exception as e:
            logger.error(f"목표 생성 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '목표 생성 중 오류가 발생했습니다.',
                'error': str(e)
            })


@method_decorator(csrf_exempt, name='dispatch')
class CreateActionItemView(View):
    """액션 아이템 생성 API"""
    
    def post(self, request, session_id):
        try:
            session = get_object_or_404(CoachingSession, session_id=session_id)
            data = json.loads(request.body)
            
            action_item = CoachingActionItem.objects.create(
                session=session,
                goal_id=data.get('goal_id'),
                category=data.get('category', 'TASK'),
                title=data.get('title', ''),
                description=data.get('description', ''),
                due_date=data.get('due_date'),
                estimated_hours=data.get('estimated_hours', 1.0),
                steps=data.get('steps', []),
                expected_outcome=data.get('expected_outcome', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': '액션 아이템이 생성되었습니다.',
                'action_item': {
                    'id': action_item.id,
                    'title': action_item.title,
                    'category': action_item.get_category_display(),
                    'due_date': action_item.due_date.isoformat() if action_item.due_date else None,
                    'status': action_item.get_status_display()
                }
            })
            
        except Exception as e:
            logger.error(f"액션 아이템 생성 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '액션 아이템 생성 중 오류가 발생했습니다.',
                'error': str(e)
            })


class GoalsListView(TemplateView):
    """목표 목록"""
    template_name = 'ai_coaching/goals_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # 목표 필터링
            goals = CoachingGoal.objects.select_related('session', 'session__employee')
            
            status_filter = self.request.GET.get('status', '')
            if status_filter:
                goals = goals.filter(status=status_filter)
            
            employee_filter = self.request.GET.get('employee', '')
            if employee_filter:
                goals = goals.filter(session__employee_id=employee_filter)
            
            # 페이지네이션
            paginator = Paginator(goals.order_by('-created_at'), 20)
            page = self.request.GET.get('page', 1)
            goals_page = paginator.get_page(page)
            
            context.update({
                'goals': goals_page,
                'status_filter': status_filter,
                'employee_filter': employee_filter,
                'status_choices': CoachingGoal.STATUS_CHOICES,
                'employees': Employee.objects.all()[:50]
            })
            
        except Exception as e:
            logger.error(f"목표 목록 조회 오류: {e}")
            context['error'] = str(e)
        
        return context


class SessionHistoryView(TemplateView):
    """세션 히스토리"""
    template_name = 'ai_coaching/session_history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # 세션 히스토리 조회
            sessions = CoachingSession.objects.select_related('employee')
            
            # 필터링
            employee_filter = self.request.GET.get('employee', '')
            if employee_filter:
                sessions = sessions.filter(employee_id=employee_filter)
            
            session_type_filter = self.request.GET.get('session_type', '')
            if session_type_filter:
                sessions = sessions.filter(session_type=session_type_filter)
            
            status_filter = self.request.GET.get('status', '')
            if status_filter:
                sessions = sessions.filter(status=status_filter)
            
            # 페이지네이션
            paginator = Paginator(sessions.order_by('-scheduled_at'), 15)
            page = self.request.GET.get('page', 1)
            sessions_page = paginator.get_page(page)
            
            context.update({
                'sessions': sessions_page,
                'employee_filter': employee_filter,
                'session_type_filter': session_type_filter,
                'status_filter': status_filter,
                'employees': Employee.objects.all()[:50],
                'session_types': CoachingSession.SESSION_TYPE_CHOICES,
                'status_choices': CoachingSession.STATUS_CHOICES
            })
            
        except Exception as e:
            logger.error(f"세션 히스토리 조회 오류: {e}")
            context['error'] = str(e)
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class SubmitFeedbackView(View):
    """피드백 제출 API"""
    
    def post(self, request, session_id):
        try:
            session = get_object_or_404(CoachingSession, session_id=session_id)
            data = json.loads(request.body)
            
            feedback = CoachingFeedback.objects.create(
                session=session,
                feedback_type=data.get('feedback_type', 'SESSION'),
                overall_rating=data.get('overall_rating', 5),
                coaching_quality=data.get('coaching_quality', 5),
                ai_helpfulness=data.get('ai_helpfulness', 5),
                goal_achievement=data.get('goal_achievement', 5),
                positive_aspects=data.get('positive_aspects', ''),
                areas_for_improvement=data.get('areas_for_improvement', ''),
                suggestions=data.get('suggestions', ''),
                would_recommend=data.get('would_recommend', True),
                future_coaching_interest=data.get('future_coaching_interest', True)
            )
            
            # 세션 만족도 점수 업데이트
            session.satisfaction_score = feedback.get_average_rating()
            session.save()
            
            return JsonResponse({
                'success': True,
                'message': '피드백이 제출되었습니다.',
                'feedback': {
                    'id': feedback.id,
                    'average_rating': feedback.get_average_rating(),
                    'submitted_at': feedback.created_at.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"피드백 제출 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '피드백 제출 중 오류가 발생했습니다.',
                'error': str(e)
            })
