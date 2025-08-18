"""
평가 시스템 API Views
AI 피드백 생성 및 실시간 기능 API
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import models
import json
import logging

logger = logging.getLogger(__name__)

from .models import (
    ContributionEvaluation, ExpertiseEvaluation, 
    ImpactEvaluation, Task, Employee
)
try:
    from .ai_feedback import ai_feedback_generator, ai_feedback_validator
except Exception as e:
    logger.error(f"AI feedback import failed: {str(e)}")
    # Fallback 객체 생성
    class FallbackFeedbackGenerator:
        def generate_contribution_feedback(self, data):
            return "AI 피드백 서비스가 일시적으로 사용 불가능합니다. 수동으로 피드백을 작성해주세요."
        def generate_expertise_feedback(self, data):
            return "AI 피드백 서비스가 일시적으로 사용 불가능합니다. 수동으로 피드백을 작성해주세요."
        def generate_impact_feedback(self, data):
            return "AI 피드백 서비스가 일시적으로 사용 불가능합니다. 수동으로 피드백을 작성해주세요."
    
    class FallbackValidator:
        def validate_feedback(self, feedback):
            return {'is_valid': True, 'score': 100, 'issues': []}
    
    ai_feedback_generator = FallbackFeedbackGenerator()
    ai_feedback_validator = FallbackValidator()

from notifications.models import Notification


@api_view(['POST'])
@permission_classes([AllowAny])  # 임시로 AllowAny 설정, 추후 IsAuthenticated로 변경 필요
def generate_ai_feedback(request):
    """AI 피드백 생성 API"""
    
    try:
        evaluation_type = request.data.get('type')  # contribution, expertise, impact
        evaluation_id = request.data.get('evaluation_id')
        
        logger.info(f"AI feedback requested - type: {evaluation_type}, id: {evaluation_id}")
        
        if not evaluation_type:
            return Response(
                {'error': '평가 타입이 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
        # evaluation_id가 null인 경우 처리
        if evaluation_id == 'null' or evaluation_id is None:
            # 기본 피드백 반환
            default_feedback = f"""[AI 피드백 - 신규 평가]
            
평가 유형: {evaluation_type}

이 평가는 아직 저장되지 않은 상태입니다.
평가를 먼저 저장한 후 AI 피드백을 생성해주세요.

평가 작성 가이드:
1. 구체적인 업무 성과와 기여도를 기록하세요
2. 측정 가능한 목표와 실적을 입력하세요
3. 건설적인 피드백과 개선 방향을 제시하세요

※ 평가 저장 후 더 정확한 AI 피드백을 받으실 수 있습니다."""
            
            return Response({
                'feedback': default_feedback,
                'validation_score': 100,
                'type': evaluation_type,
                'employee': '신규 평가'
            })
    
        # 정상적인 평가 처리
        # 평가 데이터 조회
        if evaluation_type == 'contribution':
            evaluation = ContributionEvaluation.objects.get(id=evaluation_id)
            tasks = Task.objects.filter(
                employee=evaluation.employee,
                evaluation_period=evaluation.evaluation_period
            )
            
            evaluation_data = {
                'employee_name': evaluation.employee.name,
                'department': evaluation.employee.department,
                'position': evaluation.employee.position,
                'contribution_score': float(evaluation.contribution_score or 0),
                'completed_tasks': tasks.filter(status='completed').count(),
                'achievement_rate': evaluation.achievement_rate or 0,
                'tasks': [
                    {
                        'title': task.title,
                        'achievement': float(task.achievement_rate or 0)
                    }
                    for task in tasks[:5]
                ]
            }
            
            feedback = ai_feedback_generator.generate_contribution_feedback(evaluation_data)
            
        elif evaluation_type == 'expertise':
            evaluation = ExpertiseEvaluation.objects.get(id=evaluation_id)
            
            evaluation_data = {
                'employee_name': evaluation.employee.name,
                'expertise_score': float(evaluation.expertise_score or 0),
                'strengths': ['전문 지식', '문제 해결'],  # 실제 데이터로 교체 필요
                'improvements': ['커뮤니케이션', '리더십'],
                'checklist': {
                    '업무 전문성': evaluation.job_expertise,
                    '문제 해결': evaluation.problem_solving,
                    '혁신성': evaluation.innovation,
                }
            }
            
            feedback = ai_feedback_generator.generate_expertise_feedback(evaluation_data)
            
        elif evaluation_type == 'impact':
            evaluation = ImpactEvaluation.objects.get(id=evaluation_id)
            
            evaluation_data = {
                'employee_name': evaluation.employee.name,
                'impact_score': float(evaluation.impact_score or 0),
                'leadership_style': '협력적',  # 실제 데이터로 교체
                'value_practice': 85,
                'team_impact': 4,
                'org_impact': 3,
                'external_impact': 2,
            }
            
            feedback = ai_feedback_generator.generate_impact_feedback(evaluation_data)
            
        else:
            return Response(
                {'error': '지원하지 않는 평가 타입입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 피드백 검증
        validation = ai_feedback_validator.validate_feedback(feedback)
        
        if not validation['is_valid']:
            return Response(
                {
                    'error': '생성된 피드백이 품질 기준을 충족하지 못했습니다.',
                    'issues': validation['issues']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 피드백 저장 (선택적)
        if evaluation_type == 'contribution':
            evaluation.ai_feedback = feedback
            evaluation.save()
        
        return Response({
            'feedback': feedback,
            'validation_score': validation['score'],
            'type': evaluation_type,
            'employee': evaluation.employee.name
        })
        
    except Exception as e:
        logger.error(f"AI feedback generation error: {str(e)}", exc_info=True)
        
        # 에러 발생 시 기본 피드백 제공
        fallback_feedback = f"""[AI 피드백 생성 오류]

평가 유형: {evaluation_type}

현재 AI 피드백 서비스를 사용할 수 없습니다.
다음과 같은 점을 고려하여 수동으로 피드백을 작성해주세요:

1. 우수한 점:
   - 업무 성과와 달성률
   - 팀 기여도와 협업 능력
   - 전문성과 문제 해결 능력

2. 개선이 필요한 점:
   - 목표 달성을 위한 개선 사항
   - 역량 개발이 필요한 영역
   - 커뮤니케이션 및 협업 개선점

3. 향후 발전 방향:
   - 성장 잠재력과 기회
   - 경력 개발 제안
   - 교육 및 훈련 권장 사항

오류 정보: {str(e)[:100]}..."""
        
        return Response({
            'feedback': fallback_feedback,
            'validation_score': 0,
            'type': evaluation_type,
            'employee': '오류',
            'error': str(e)
        }, status=status.HTTP_200_OK)  # 200으로 반환하여 UI에서 처리 가능하도록


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_evaluation_summary(request, employee_id):
    """직원 평가 요약 API"""
    
    try:
        employee = Employee.objects.get(id=employee_id)
        
        # 최신 평가 데이터 조회
        contribution = ContributionEvaluation.objects.filter(
            employee=employee
        ).order_by('-created_at').first()
        
        expertise = ExpertiseEvaluation.objects.filter(
            employee=employee
        ).order_by('-created_at').first()
        
        impact = ImpactEvaluation.objects.filter(
            employee=employee
        ).order_by('-created_at').first()
        
        summary = {
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'department': employee.department,
                'position': employee.position,
            },
            'evaluations': {
                'contribution': {
                    'score': float(contribution.contribution_score) if contribution else 0,
                    'date': contribution.created_at.isoformat() if contribution else None,
                    'status': contribution.status if contribution else 'not_started'
                },
                'expertise': {
                    'score': float(expertise.expertise_score) if expertise else 0,
                    'date': expertise.created_at.isoformat() if expertise else None,
                    'status': expertise.status if expertise else 'not_started'
                },
                'impact': {
                    'score': float(impact.impact_score) if impact else 0,
                    'date': impact.created_at.isoformat() if impact else None,
                    'status': impact.status if impact else 'not_started'
                }
            },
            'overall_progress': _calculate_overall_progress(contribution, expertise, impact)
        }
        
        return Response(summary)
        
    except Employee.DoesNotExist:
        return Response(
            {'error': '직원을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_evaluation_notification(request):
    """평가 알림 생성 API"""
    
    try:
        recipient_id = request.data.get('recipient_id')
        notification_type = request.data.get('type', 'evaluation')
        title = request.data.get('title')
        message = request.data.get('message')
        
        if not all([recipient_id, title, message]):
            return Response(
                {'error': '필수 필드가 누락되었습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recipient = Employee.objects.get(id=recipient_id)
        
        notification = Notification.objects.create(
            user=recipient.user if hasattr(recipient, 'user') else None,
            type=notification_type,
            title=title,
            message=message,
            data={
                'sender': request.user.username,
                'employee_id': recipient_id
            }
        )
        
        # 실시간 알림 전송 (WebSocket 구현 시 활성화)
        # send_realtime_notification(notification)
        
        return Response({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'created_at': notification.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)
        
    except Employee.DoesNotExist:
        return Response(
            {'error': '수신자를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@require_http_methods(["GET"])
@login_required
def get_evaluation_analytics(request):
    """평가 분석 데이터 API"""
    
    try:
        # 부서별 평균 점수
        department_scores = {}
        
        # 기여도 평가 평균
        contribution_avgs = ContributionEvaluation.objects.values(
            'employee__department'
        ).annotate(
            avg_score=models.Avg('contribution_score')
        )
        
        for item in contribution_avgs:
            dept = item['employee__department']
            if dept not in department_scores:
                department_scores[dept] = {}
            department_scores[dept]['contribution'] = float(item['avg_score'] or 0)
        
        # 월별 평가 추이
        monthly_trends = []
        
        # 평가 완료율
        total_employees = Employee.objects.filter(employment_status='재직').count()
        completed_evaluations = ContributionEvaluation.objects.filter(
            status='completed'
        ).values('employee').distinct().count()
        
        completion_rate = (completed_evaluations / total_employees * 100) if total_employees > 0 else 0
        
        analytics = {
            'department_scores': department_scores,
            'monthly_trends': monthly_trends,
            'completion_rate': round(completion_rate, 1),
            'total_employees': total_employees,
            'completed_evaluations': completed_evaluations
        }
        
        return JsonResponse(analytics)
        
    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=500
        )


def _calculate_overall_progress(contribution, expertise, impact):
    """전체 평가 진행률 계산"""
    
    total = 0
    completed = 0
    
    if contribution:
        total += 1
        if contribution.status == 'completed':
            completed += 1
            
    if expertise:
        total += 1
        if expertise.status == 'completed':
            completed += 1
            
    if impact:
        total += 1
        if impact.status == 'completed':
            completed += 1
    
    if total == 0:
        return 0
        
    return round(completed / total * 100, 1)