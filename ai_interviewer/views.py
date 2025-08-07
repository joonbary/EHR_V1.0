"""
AI Interviewer Views - AI 채용 면접관 뷰
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator

from .models import (
    InterviewSession, InterviewQuestion, InterviewResponse,
    InterviewFeedback, InterviewTemplate, InterviewMetrics
)
from .services import AIInterviewer, InterviewTemplateManager, InterviewAnalyzer
from job_profiles.models import JobProfile
from employees.models import Employee

import json
import logging
import uuid

logger = logging.getLogger(__name__)


class InterviewDashboard(TemplateView):
    """AI 면접 대시보드"""
    template_name = 'ai_interviewer/interview_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # 면접 통계
            stats = InterviewAnalyzer.get_session_statistics()
            
            # 최근 면접 세션
            recent_sessions = InterviewSession.objects.select_related(
                'job_profile', 'test_employee'
            ).order_by('-created_at')[:10]
            
            # 진행 중인 면접
            active_sessions = InterviewSession.objects.filter(
                status='IN_PROGRESS'
            ).select_related('job_profile')[:5]
            
            # 템플릿 목록
            templates = InterviewTemplate.objects.filter(
                is_active=True
            ).order_by('-usage_count')[:5]
            
            # 채용공고 목록
            job_profiles = JobProfile.objects.filter(
                status='ACTIVE'
            ).order_by('-created_at')[:10]
            
            context.update({
                'stats': stats,
                'recent_sessions': recent_sessions,
                'active_sessions': active_sessions,
                'templates': templates,
                'job_profiles': job_profiles,
                'dashboard_updated': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"면접 대시보드 오류: {e}")
            context.update({
                'error_message': 'AI 면접 서비스에 일시적인 문제가 발생했습니다.'
            })
        
        return context


class InterviewSessionDetailView(DetailView):
    """면접 세션 상세 뷰"""
    model = InterviewSession
    template_name = 'ai_interviewer/session_detail.html'
    context_object_name = 'session'
    pk_url_kwarg = 'session_id'
    
    def get_object(self, queryset=None):
        session_id = self.kwargs.get('session_id')
        return get_object_or_404(InterviewSession, session_id=session_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # 질문과 응답
        questions_with_responses = []
        for question in session.questions.order_by('question_number'):
            try:
                response = question.response
            except InterviewResponse.DoesNotExist:
                response = None
            
            questions_with_responses.append({
                'question': question,
                'response': response
            })
        
        # 면접 지표
        try:
            metrics = session.metrics
        except InterviewMetrics.DoesNotExist:
            metrics = None
        
        # 피드백
        feedback_list = session.feedback.order_by('-priority_level', '-created_at')
        
        context.update({
            'questions_with_responses': questions_with_responses,
            'metrics': metrics,
            'feedback_list': feedback_list,
            'completion_rate': session.get_completion_rate(),
            'duration_minutes': session.get_duration_minutes()
        })
        
        return context


class LiveInterviewView(TemplateView):
    """실시간 면접 뷰"""
    template_name = 'ai_interviewer/live_interview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = kwargs.get('session_id')
        
        try:
            session = get_object_or_404(InterviewSession, session_id=session_id)
            
            # 현재 질문 확인
            current_question = None
            if session.status == 'IN_PROGRESS':
                questions = session.questions.order_by('question_number')
                for question in questions:
                    if not hasattr(question, 'response'):
                        current_question = question
                        break
            
            context.update({
                'session': session,
                'current_question': current_question,
                'websocket_url': f'ws://localhost:8000/ws/interview/{session_id}/'
            })
            
        except Exception as e:
            logger.error(f"실시간 면접 뷰 오류: {e}")
            context.update({
                'error_message': '면접 세션을 찾을 수 없습니다.'
            })
        
        return context


class InterviewSessionListView(ListView):
    """면접 세션 목록 뷰"""
    model = InterviewSession
    template_name = 'ai_interviewer/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = InterviewSession.objects.select_related(
            'job_profile', 'test_employee'
        ).order_by('-created_at')
        
        # 검색 필터
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(candidate_name__icontains=search) |
                Q(job_profile__title__icontains=search)
            )
        
        # 상태 필터
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # 유형 필터
        session_type = self.request.GET.get('type')
        if session_type:
            queryset = queryset.filter(session_type=session_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'status_choices': InterviewSession.SESSION_STATUS_CHOICES,
            'type_choices': InterviewSession.SESSION_TYPE_CHOICES,
            'current_filters': {
                'search': self.request.GET.get('search', ''),
                'status': self.request.GET.get('status', ''),
                'type': self.request.GET.get('type', '')
            }
        })
        return context


# API Views

@require_http_methods(["POST"])
@csrf_exempt
def api_create_session(request):
    """면접 세션 생성 API"""
    try:
        data = json.loads(request.body)
        
        # 필수 필드 검증
        required_fields = ['job_profile_id', 'candidate_name', 'candidate_email']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'{field} 필드가 필요합니다.'
                }, status=400)
        
        # 채용공고 확인
        try:
            job_profile = JobProfile.objects.get(id=data['job_profile_id'])
        except JobProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '채용공고를 찾을 수 없습니다.'
            }, status=404)
        
        # 테스트 직원 확인 (선택사항)
        test_employee = None
        if data.get('test_employee_id'):
            try:
                test_employee = Employee.objects.get(id=data['test_employee_id'])
            except Employee.DoesNotExist:
                pass
        
        # 세션 생성
        session = InterviewSession.objects.create(
            title=data.get('title', f"{job_profile.title} 면접"),
            job_profile=job_profile,
            candidate_name=data['candidate_name'],
            candidate_email=data['candidate_email'],
            candidate_phone=data.get('candidate_phone', ''),
            test_employee=test_employee,
            session_type=data.get('session_type', 'BEHAVIORAL'),
            difficulty_level=data.get('difficulty_level', 'INTERMEDIATE'),
            expected_duration=data.get('expected_duration', 30),
            max_questions=data.get('max_questions', 10),
            ai_personality=data.get('ai_personality', 'PROFESSIONAL'),
            custom_instructions=data.get('custom_instructions', '')
        )
        
        return JsonResponse({
            'success': True,
            'session_id': str(session.session_id),
            'message': '면접 세션이 생성되었습니다.',
            'live_interview_url': f'/ai-interviewer/live/{session.session_id}/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
        
    except Exception as e:
        logger.error(f"면접 세션 생성 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_start_interview(request, session_id):
    """면접 시작 API"""
    try:
        session = get_object_or_404(InterviewSession, session_id=session_id)
        
        if session.status != 'SCHEDULED':
            return JsonResponse({
                'success': False,
                'error': f'면접을 시작할 수 없습니다. 현재 상태: {session.get_status_display()}'
            }, status=400)
        
        # AI 면접관 초기화 및 시작
        interviewer = AIInterviewer(session)
        result = interviewer.start_interview()
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"면접 시작 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_submit_response(request, session_id):
    """응답 제출 API"""
    try:
        session = get_object_or_404(InterviewSession, session_id=session_id)
        data = json.loads(request.body)
        
        # 필수 필드 검증
        if 'question_id' not in data or 'response_text' not in data:
            return JsonResponse({
                'success': False,
                'error': 'question_id와 response_text가 필요합니다.'
            }, status=400)
        
        question = get_object_or_404(InterviewQuestion, id=data['question_id'], session=session)
        
        # 이미 응답이 있는지 확인
        if hasattr(question, 'response'):
            return JsonResponse({
                'success': False,
                'error': '이미 응답이 제출된 질문입니다.'
            }, status=400)
        
        # 응답 생성
        response_started_at = timezone.datetime.fromisoformat(
            data.get('started_at', timezone.now().isoformat())
        )
        
        response = InterviewResponse.objects.create(
            question=question,
            response_text=data['response_text'],
            started_at=response_started_at,
            response_time_seconds=data.get('response_time', 0)
        )
        
        # AI 평가 수행
        interviewer = AIInterviewer(session)
        evaluation_result = interviewer.evaluate_response(response)
        
        # 다음 질문 생성 또는 면접 완료
        if interviewer._should_continue_interview():
            next_question = interviewer.generate_next_question(response)
            return JsonResponse({
                'success': True,
                'evaluation': evaluation_result.get('evaluation', {}),
                'next_question': interviewer._format_question(next_question),
                'interview_continues': True
            })
        else:
            # 면접 완료
            completion_result = interviewer.complete_interview()
            return JsonResponse({
                'success': True,
                'evaluation': evaluation_result.get('evaluation', {}),
                'interview_continues': False,
                'completion_result': completion_result
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
        
    except Exception as e:
        logger.error(f"응답 제출 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_session_status(request, session_id):
    """면접 세션 상태 API"""
    try:
        session = get_object_or_404(InterviewSession, session_id=session_id)
        
        # 현재 진행 상황
        total_questions = session.questions.count()
        completed_responses = session.questions.filter(
            response__isnull=False
        ).count()
        
        # 현재 질문 확인
        current_question = None
        if session.status == 'IN_PROGRESS':
            for question in session.questions.order_by('question_number'):
                if not hasattr(question, 'response'):
                    current_question = {
                        'id': question.id,
                        'number': question.question_number,
                        'text': question.question_text,
                        'type': question.get_question_type_display(),
                        'time_limit': question.estimated_response_time
                    }
                    break
        
        return JsonResponse({
            'success': True,
            'session_info': {
                'session_id': str(session.session_id),
                'status': session.status,
                'status_display': session.get_status_display(),
                'candidate_name': session.candidate_name,
                'job_title': session.job_profile.title,
                'progress': {
                    'total_questions': total_questions,
                    'completed_responses': completed_responses,
                    'completion_rate': (completed_responses / max(total_questions, 1)) * 100
                },
                'timing': {
                    'started_at': session.started_at.isoformat() if session.started_at else None,
                    'duration_minutes': session.get_duration_minutes(),
                    'expected_duration': session.expected_duration
                },
                'current_question': current_question
            }
        })
        
    except Exception as e:
        logger.error(f"세션 상태 조회 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_pause_interview(request, session_id):
    """면접 일시정지 API"""
    try:
        session = get_object_or_404(InterviewSession, session_id=session_id)
        
        if session.status != 'IN_PROGRESS':
            return JsonResponse({
                'success': False,
                'error': '진행 중인 면접만 일시정지할 수 있습니다.'
            }, status=400)
        
        session.status = 'PAUSED'
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': '면접이 일시정지되었습니다.',
            'status': session.status
        })
        
    except Exception as e:
        logger.error(f"면접 일시정지 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_resume_interview(request, session_id):
    """면접 재개 API"""
    try:
        session = get_object_or_404(InterviewSession, session_id=session_id)
        
        if session.status != 'PAUSED':
            return JsonResponse({
                'success': False,
                'error': '일시정지된 면접만 재개할 수 있습니다.'
            }, status=400)
        
        session.status = 'IN_PROGRESS'
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': '면접이 재개되었습니다.',
            'status': session.status
        })
        
    except Exception as e:
        logger.error(f"면접 재개 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_interview_statistics(request):
    """면접 통계 API"""
    try:
        days = int(request.GET.get('days', 30))
        stats = InterviewAnalyzer.get_session_statistics(days)
        
        return JsonResponse({
            'success': True,
            'statistics': stats,
            'period_days': days,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"면접 통계 조회 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_candidate_insights(request, session_id):
    """후보자 인사이트 API"""
    try:
        insights = InterviewAnalyzer.get_candidate_insights(session_id)
        
        if 'error' in insights:
            return JsonResponse({
                'success': False,
                'error': insights['error']
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'insights': insights,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"후보자 인사이트 조회 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt  
def api_generate_templates(request):
    """기본 템플릿 생성 API"""
    try:
        InterviewTemplateManager.create_default_templates()
        
        templates_count = InterviewTemplate.objects.filter(is_active=True).count()
        
        return JsonResponse({
            'success': True,
            'message': '기본 템플릿이 생성되었습니다.',
            'templates_count': templates_count
        })
        
    except Exception as e:
        logger.error(f"템플릿 생성 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


class InterviewTemplateListView(ListView):
    """면접 템플릿 목록"""
    model = InterviewTemplate
    template_name = 'ai_interviewer/template_list.html'
    context_object_name = 'templates'
    paginate_by = 10
    
    def get_queryset(self):
        return InterviewTemplate.objects.filter(is_active=True).order_by('-usage_count', 'name')