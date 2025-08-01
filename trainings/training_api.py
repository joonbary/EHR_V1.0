"""
교육 추천 API
ESS에서 직원이 맞춤형 교육을 추천받고 신청할 수 있는 API
"""

from typing import List, Dict, Optional
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.core.cache import cache
import json
import logging

from employees.models import Employee
from .training_services import TrainingRecommendationService
from .models import TrainingCourse, TrainingEnrollment

logger = logging.getLogger(__name__)


class MyGrowthTrainingRecommendationsAPI(View):
    """개인 성장 교육 추천 API"""
    
    @method_decorator(login_required)
    def get(self, request):
        """
        GET /api/my-growth-training-recommendations/
        
        Query Parameters:
            - target_job: 목표 직무 (optional)
            - refresh: 캐시 새로고침 (optional)
            - max_items: 최대 추천 수 (default: 10)
        
        Returns:
            교육 추천 목록 및 학습 로드맵
        """
        try:
            # 현재 로그인한 직원
            employee = Employee.objects.get(user=request.user)
            
            # 파라미터 추출
            target_job = request.GET.get('target_job')
            refresh = request.GET.get('refresh', '').lower() == 'true'
            max_items = int(request.GET.get('max_items', 10))
            
            # 캐시 처리
            if not refresh:
                cache_key = f"training_recommendations_api_{employee.id}_{target_job}"
                cached_data = cache.get(cache_key)
                if cached_data:
                    return JsonResponse(cached_data)
            
            # 서비스 호출
            service = TrainingRecommendationService()
            result = service.get_employee_training_recommendations(
                employee=employee,
                target_job=target_job,
                include_completed=False,
                max_recommendations=max_items
            )
            
            # API 응답 포맷팅
            response_data = {
                'status': result['status'],
                'employee': {
                    'id': str(employee.id),
                    'name': employee.name,
                    'position': employee.position,
                    'department': employee.department,
                    'current_level': result['context']['current_level']
                },
                'context': {
                    'target_job': result['context']['target_job'],
                    'missing_skills': result['context']['missing_skills']
                },
                'recommendations': self._format_recommendations(
                    result.get('recommendations', [])
                ),
                'roadmap': result.get('roadmap', []),
                'summary': result.get('summary', {}),
                'generated_at': datetime.now().isoformat()
            }
            
            # 캐시 저장 (30분)
            if not refresh:
                cache.set(cache_key, response_data, 1800)
            
            return JsonResponse(response_data)
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '직원 정보를 찾을 수 없습니다.'
            }, status=404)
            
        except Exception as e:
            logger.error(f"Error in training recommendations API: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '교육 추천 중 오류가 발생했습니다.'
            }, status=500)
    
    def _format_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """추천 결과 포맷팅"""
        formatted = []
        
        for rec in recommendations:
            formatted.append({
                'course_id': rec['course_id'],
                'course_code': rec['course_code'],
                'title': rec['title'],
                'category': rec['category'],
                'provider': rec['provider'],
                'course_type': rec['course_type'],
                'duration_hours': rec['duration_hours'],
                'cost': rec['cost'],
                'match_score': round(rec['match_score'], 1),
                'priority': rec['priority'],
                'skill_coverage': round(rec['skill_coverage'] * 100, 1),
                'matched_skills': rec['matched_skills'],
                'recommendation_reason': rec['recommendation_reason'],
                'expected_completion_time': rec['expected_completion_time'],
                'can_enroll': rec.get('can_enroll', True),
                'enrollment_message': rec.get('enrollment_message', ''),
                'next_session': rec.get('next_session', {}),
                'completion_rate': round(rec.get('completion_rate', 0), 1),
                'average_satisfaction': round(rec.get('average_satisfaction', 0), 1),
                'growth_impact': rec.get('growth_impact', {})
            })
        
        return formatted


class TrainingEnrollmentAPI(View):
    """교육 수강 신청 API"""
    
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """
        POST /api/training-enrollment/
        
        Body:
            {
                "course_id": "uuid",
                "notes": "신청 사유 (optional)"
            }
        """
        try:
            employee = Employee.objects.get(user=request.user)
            
            # 요청 데이터 파싱
            data = json.loads(request.body)
            course_id = data.get('course_id')
            notes = data.get('notes', '')
            
            if not course_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'course_id는 필수입니다.'
                }, status=400)
            
            # 서비스 호출
            service = TrainingRecommendationService()
            result = service.enroll_in_course(
                employee=employee,
                course_id=course_id,
                notes=notes
            )
            
            if result['success']:
                return JsonResponse({
                    'status': 'success',
                    'enrollment_id': result['enrollment_id'],
                    'message': result['message']
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': result['message']
                }, status=400)
                
        except Employee.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '직원 정보를 찾을 수 없습니다.'
            }, status=404)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '잘못된 요청 형식입니다.'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error in enrollment API: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '수강 신청 중 오류가 발생했습니다.'
            }, status=500)


class MyTrainingHistoryAPI(View):
    """내 교육 이력 조회 API"""
    
    @method_decorator(login_required)
    def get(self, request):
        """
        GET /api/my-training-history/
        
        Query Parameters:
            - status: 상태 필터 (COMPLETED, IN_PROGRESS 등)
        """
        try:
            employee = Employee.objects.get(user=request.user)
            
            # 상태 필터
            status_filter = request.GET.getlist('status')
            
            # 서비스 호출
            service = TrainingRecommendationService()
            history = service.get_my_training_history(
                employee=employee,
                status_filter=status_filter if status_filter else None
            )
            
            return JsonResponse({
                'status': 'success',
                'total_count': len(history),
                'history': history
            })
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '직원 정보를 찾을 수 없습니다.'
            }, status=404)
            
        except Exception as e:
            logger.error(f"Error in training history API: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '교육 이력 조회 중 오류가 발생했습니다.'
            }, status=500)


class TrainingCourseDetailAPI(View):
    """교육과정 상세 조회 API"""
    
    @method_decorator(login_required)
    def get(self, request, course_id):
        """
        GET /api/training-course/<course_id>/
        
        Returns:
            교육과정 상세 정보
        """
        try:
            course = TrainingCourse.objects.get(id=course_id, is_active=True)
            
            # 이수율 계산
            total_enrollments = TrainingEnrollment.objects.filter(
                course=course,
                status__in=['COMPLETED', 'INCOMPLETE']
            ).count()
            
            completed_enrollments = TrainingEnrollment.objects.filter(
                course=course,
                status='COMPLETED'
            ).count()
            
            completion_rate = (
                (completed_enrollments / total_enrollments * 100)
                if total_enrollments > 0 else 0
            )
            
            # 평균 만족도
            avg_satisfaction = TrainingEnrollment.objects.filter(
                course=course,
                satisfaction_score__isnull=False
            ).aggregate(avg=Avg('satisfaction_score'))['avg'] or 0
            
            response_data = {
                'status': 'success',
                'course': {
                    'id': str(course.id),
                    'course_code': course.course_code,
                    'title': course.title,
                    'category': course.category.name if course.category else '일반',
                    'description': course.description,
                    'objectives': course.objectives,
                    'target_audience': course.target_audience,
                    'related_skills': course.related_skills,
                    'skill_level': course.skill_level,
                    'duration_hours': course.duration_hours,
                    'course_type': course.course_type,
                    'provider': course.provider,
                    'cost': float(course.cost),
                    'is_mandatory': course.is_mandatory,
                    'certification_eligible': course.certification_eligible,
                    'statistics': {
                        'total_enrollments': total_enrollments,
                        'completion_rate': round(completion_rate, 1),
                        'average_satisfaction': round(avg_satisfaction, 1)
                    }
                }
            }
            
            return JsonResponse(response_data)
            
        except TrainingCourse.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '교육과정을 찾을 수 없습니다.'
            }, status=404)
            
        except Exception as e:
            logger.error(f"Error in course detail API: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '교육과정 조회 중 오류가 발생했습니다.'
            }, status=500)


# URL 패턴
"""
from django.urls import path
from .training_api import (
    MyGrowthTrainingRecommendationsAPI,
    TrainingEnrollmentAPI,
    MyTrainingHistoryAPI,
    TrainingCourseDetailAPI
)

urlpatterns = [
    path('api/my-growth-training-recommendations/', 
         MyGrowthTrainingRecommendationsAPI.as_view(), 
         name='my_growth_training_recommendations'),
    
    path('api/training-enrollment/', 
         TrainingEnrollmentAPI.as_view(), 
         name='training_enrollment'),
    
    path('api/my-training-history/', 
         MyTrainingHistoryAPI.as_view(), 
         name='my_training_history'),
    
    path('api/training-course/<uuid:course_id>/', 
         TrainingCourseDetailAPI.as_view(), 
         name='training_course_detail'),
]
"""