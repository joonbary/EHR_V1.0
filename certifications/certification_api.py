"""
성장레벨 인증 체크 API
직원의 성장레벨 인증 요건 충족 여부를 확인하는 API
"""

from typing import Dict, Optional
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
from job_profiles.models import JobProfile
from .certification_services import CertificationService

logger = logging.getLogger(__name__)


class GrowthLevelCertificationCheckAPI(View):
    """성장레벨 인증 체크 API"""
    
    @method_decorator(login_required)
    def post(self, request):
        """
        POST /api/growth-level-certification-check/
        
        Request Body:
            {
                "employee_id": "E1001",
                "target_level": "Lv.3",
                "target_job_id": "J-TM-01" (optional)
            }
        
        Returns:
            인증 요건 충족 여부 및 부족 사항
        """
        try:
            # 요청 데이터 파싱
            data = json.loads(request.body)
            employee_id = data.get('employee_id')
            target_level = data.get('target_level')
            target_job_id = data.get('target_job_id')
            
            # 필수 파라미터 검증
            if not employee_id or not target_level:
                return JsonResponse({
                    'status': 'error',
                    'message': 'employee_id와 target_level은 필수입니다.'
                }, status=400)
            
            # 직원 조회
            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': '직원을 찾을 수 없습니다.'
                }, status=404)
            
            # 권한 체크 (본인 또는 HR 담당자)
            if not self._has_permission(request.user, employee):
                return JsonResponse({
                    'status': 'error',
                    'message': '권한이 없습니다.'
                }, status=403)
            
            # 서비스 호출
            service = CertificationService()
            result = service.check_growth_level_certification(
                employee=employee,
                target_level=target_level,
                target_job_id=target_job_id
            )
            
            if result['status'] == 'error':
                return JsonResponse(result, status=400)
            
            # API 응답 포맷
            response_data = {
                'status': 'success',
                'certification_result': result['certification_result'],
                'missing_courses': result['details']['missing_courses'],
                'missing_skills': result['details']['missing_skills'],
                'eval_ok': result['details']['eval_ok'],
                'current_level': result['details']['current_level'],
                'required_level': result['details']['required_level'],
                'expected_certification_date': result['expected_certification_date'],
                'checks': result['checks'],
                'progress': result.get('progress', {}),
                'recommendations': result['recommendations']
            }
            
            # 평가 상세 정보 추가
            if 'evaluation' in result['details']:
                response_data['evaluation_details'] = result['details']['evaluation']
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '잘못된 요청 형식입니다.'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Certification check API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '인증 체크 중 오류가 발생했습니다.'
            }, status=500)
    
    def _has_permission(self, user, employee):
        """권한 확인"""
        # 본인이거나 HR 권한이 있는 경우
        return (
            user == employee.user or
            user.groups.filter(name='HR').exists() or
            user.is_superuser
        )


class MyGrowthLevelStatusAPI(View):
    """내 성장레벨 상태 조회 API"""
    
    @method_decorator(login_required)
    def get(self, request):
        """
        GET /api/my-growth-level-status/
        
        Query Parameters:
            - target_level: 체크할 목표 레벨 (optional)
            - target_job_id: 목표 직무 ID (optional)
        
        Returns:
            현재 성장레벨 상태 및 다음 레벨 요건
        """
        try:
            # 현재 로그인한 직원
            employee = Employee.objects.get(user=request.user)
            
            # 파라미터
            target_level = request.GET.get('target_level')
            target_job_id = request.GET.get('target_job_id')
            
            # 서비스 초기화
            service = CertificationService()
            
            # 현재 레벨 확인
            current_level = service._get_current_level(employee)
            
            # 목표 레벨이 없으면 다음 레벨로 설정
            if not target_level:
                level_map = {
                    'Lv.1': 'Lv.2', 'Lv.2': 'Lv.3',
                    'Lv.3': 'Lv.4', 'Lv.4': 'Lv.5'
                }
                target_level = level_map.get(current_level, 'Lv.5')
            
            # 인증 체크
            check_result = service.check_growth_level_certification(
                employee=employee,
                target_level=target_level,
                target_job_id=target_job_id
            )
            
            # 인증 이력
            certification_history = service.get_certification_history(employee)
            
            response_data = {
                'status': 'success',
                'employee': {
                    'id': str(employee.id),
                    'name': employee.name,
                    'position': employee.position,
                    'department': employee.department
                },
                'growth_level': {
                    'current': current_level,
                    'target': target_level,
                    'certification_status': check_result['certification_result']
                },
                'requirements': {
                    'evaluation': check_result['checks']['evaluation'],
                    'training': check_result['checks']['training'],
                    'skills': check_result['checks']['skills'],
                    'experience': check_result['checks']['experience']
                },
                'missing': {
                    'courses': check_result['details']['missing_courses'],
                    'skills': check_result['details']['missing_skills']
                },
                'progress': check_result.get('progress', {}),
                'expected_certification_date': check_result['expected_certification_date'],
                'recommendations': check_result['recommendations'],
                'certification_history': certification_history[:5]  # 최근 5개
            }
            
            return JsonResponse(response_data)
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '직원 정보를 찾을 수 없습니다.'
            }, status=404)
            
        except Exception as e:
            logger.error(f"Growth level status API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '성장레벨 상태 조회 중 오류가 발생했습니다.'
            }, status=500)


class GrowthLevelCertificationApplyAPI(View):
    """성장레벨 인증 신청 API"""
    
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """
        POST /api/growth-level-certification-apply/
        
        Request Body:
            {
                "target_level": "Lv.3",
                "notes": "인증 신청 사유 (optional)"
            }
        """
        try:
            employee = Employee.objects.get(user=request.user)
            
            # 요청 데이터 파싱
            data = json.loads(request.body)
            target_level = data.get('target_level')
            notes = data.get('notes', '')
            
            if not target_level:
                return JsonResponse({
                    'status': 'error',
                    'message': 'target_level은 필수입니다.'
                }, status=400)
            
            # 서비스 호출
            service = CertificationService()
            result = service.apply_for_certification(
                employee=employee,
                target_level=target_level,
                notes=notes
            )
            
            if result['success']:
                return JsonResponse({
                    'status': 'success',
                    'certification_id': result['certification_id'],
                    'message': result['message']
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': result['message'],
                    'missing_requirements': result.get('missing_requirements')
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
            logger.error(f"Certification apply API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '인증 신청 중 오류가 발생했습니다.'
            }, status=500)


class GrowthLevelProgressAPI(View):
    """성장레벨 진행률 조회 API"""
    
    @method_decorator(login_required)
    def get(self, request):
        """
        GET /api/growth-level-progress/
        
        Query Parameters:
            - employee_id: 직원 ID (HR 권한 필요, 없으면 본인)
            - target_level: 목표 레벨
        
        Returns:
            각 영역별 진행률 및 종합 진행률
        """
        try:
            # 직원 결정
            employee_id = request.GET.get('employee_id')
            
            if employee_id:
                # HR 권한 체크
                if not request.user.groups.filter(name='HR').exists() and not request.user.is_superuser:
                    return JsonResponse({
                        'status': 'error',
                        'message': '권한이 없습니다.'
                    }, status=403)
                
                try:
                    employee = Employee.objects.get(id=employee_id)
                except Employee.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': '직원을 찾을 수 없습니다.'
                    }, status=404)
            else:
                employee = Employee.objects.get(user=request.user)
            
            target_level = request.GET.get('target_level', 'Lv.3')
            
            # 서비스 호출
            service = CertificationService()
            check_result = service.check_growth_level_certification(
                employee=employee,
                target_level=target_level
            )
            
            progress = check_result.get('progress', {})
            
            response_data = {
                'status': 'success',
                'employee': {
                    'id': str(employee.id),
                    'name': employee.name,
                    'current_level': check_result['details']['current_level']
                },
                'target_level': target_level,
                'progress': {
                    'evaluation': round(progress.get('evaluation', 0), 1),
                    'training': round(progress.get('training', 0), 1),
                    'skills': round(progress.get('skills', 0), 1),
                    'experience': round(progress.get('experience', 0), 1),
                    'overall': round(progress.get('overall', 0), 1)
                },
                'can_apply': check_result['certification_result'] == '충족'
            }
            
            return JsonResponse(response_data)
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '직원 정보를 찾을 수 없습니다.'
            }, status=404)
            
        except Exception as e:
            logger.error(f"Growth level progress API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '진행률 조회 중 오류가 발생했습니다.'
            }, status=500)


# URL 패턴
"""
from django.urls import path
from .certification_api import (
    GrowthLevelCertificationCheckAPI,
    MyGrowthLevelStatusAPI,
    GrowthLevelCertificationApplyAPI,
    GrowthLevelProgressAPI
)

urlpatterns = [
    path('api/growth-level-certification-check/', 
         GrowthLevelCertificationCheckAPI.as_view(), 
         name='growth_level_certification_check'),
    
    path('api/my-growth-level-status/', 
         MyGrowthLevelStatusAPI.as_view(), 
         name='my_growth_level_status'),
    
    path('api/growth-level-certification-apply/', 
         GrowthLevelCertificationApplyAPI.as_view(), 
         name='growth_level_certification_apply'),
    
    path('api/growth-level-progress/', 
         GrowthLevelProgressAPI.as_view(), 
         name='growth_level_progress'),
]
"""