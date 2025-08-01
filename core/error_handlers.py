"""
전역 에러 핸들러
"""
import logging
import traceback
from typing import Optional
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from django.utils.translation import gettext as _

from .exceptions import (
    EHRBaseException, ValidationError, AuthorizationError,
    EmployeeNotFoundError, FileProcessingError,
    EvaluationError, PromotionError, CompensationError
)


logger = logging.getLogger(__name__)


class ErrorHandler:
    """에러 처리 클래스"""
    
    @staticmethod
    def handle_exception(request: HttpRequest, exception: Exception):
        """예외 처리"""
        # 에러 로깅
        logger.error(
            f"Unhandled exception: {type(exception).__name__}: {str(exception)}",
            exc_info=True,
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': request.user.username if request.user.is_authenticated else 'anonymous'
            }
        )
        
        # AJAX 요청 여부 확인
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # EHR 기본 예외 처리
        if isinstance(exception, EHRBaseException):
            return ErrorHandler._handle_ehr_exception(request, exception, is_ajax)
        
        # 기타 예외 처리
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': '시스템 오류가 발생했습니다.',
                'code': 'system_error'
            }, status=500)
        else:
            return render(request, 'errors/500.html', {
                'error_message': '시스템 오류가 발생했습니다.'
            }, status=500)
    
    @staticmethod
    def _handle_ehr_exception(
        request: HttpRequest,
        exception: EHRBaseException,
        is_ajax: bool
    ):
        """EHR 예외 처리"""
        # 예외 타입별 상태 코드 매핑
        status_map = {
            ValidationError: 400,
            AuthorizationError: 403,
            EmployeeNotFoundError: 404,
            FileProcessingError: 400,
            EvaluationError: 400,
            PromotionError: 400,
            CompensationError: 400
        }
        
        status_code = status_map.get(type(exception), 400)
        
        if is_ajax:
            response_data = {
                'success': False,
                'error': str(exception),
                'code': exception.code or type(exception).__name__
            }
            
            if exception.details:
                response_data['details'] = exception.details
            
            return JsonResponse(response_data, status=status_code)
        else:
            template_map = {
                403: 'errors/403.html',
                404: 'errors/404.html'
            }
            
            template = template_map.get(status_code, 'errors/400.html')
            
            return render(request, template, {
                'error_message': str(exception),
                'error_code': exception.code
            }, status=status_code)


class ErrorMiddleware:
    """에러 처리 미들웨어"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return ErrorHandler.handle_exception(request, e)
    
    def process_exception(self, request, exception):
        """예외 처리"""
        return ErrorHandler.handle_exception(request, exception)


def handle_400(request, exception=None):
    """400 Bad Request 핸들러"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax:
        return JsonResponse({
            'success': False,
            'error': '잘못된 요청입니다.'
        }, status=400)
    
    return render(request, 'errors/400.html', {
        'error_message': '잘못된 요청입니다.'
    }, status=400)


def handle_403(request, exception=None):
    """403 Forbidden 핸들러"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax:
        return JsonResponse({
            'success': False,
            'error': '접근 권한이 없습니다.'
        }, status=403)
    
    return render(request, 'errors/403.html', {
        'error_message': '접근 권한이 없습니다.'
    }, status=403)


def handle_404(request, exception=None):
    """404 Not Found 핸들러"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax:
        return JsonResponse({
            'success': False,
            'error': '요청한 페이지를 찾을 수 없습니다.'
        }, status=404)
    
    return render(request, 'errors/404.html', {
        'error_message': '요청한 페이지를 찾을 수 없습니다.'
    }, status=404)


def handle_500(request):
    """500 Internal Server Error 핸들러"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # 에러 로깅
    logger.error(
        '500 error occurred',
        extra={
            'request_path': request.path,
            'request_method': request.method,
            'user': request.user.username if request.user.is_authenticated else 'anonymous'
        }
    )
    
    if is_ajax:
        return JsonResponse({
            'success': False,
            'error': '서버 오류가 발생했습니다.'
        }, status=500)
    
    return render(request, 'errors/500.html', {
        'error_message': '서버 오류가 발생했습니다.'
    }, status=500)