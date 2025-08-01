"""
공통 데코레이터
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
import logging
import time
from typing import Callable, Any

from .exceptions import EmployeeNotFoundError, AuthorizationError


logger = logging.getLogger(__name__)


def require_employee(view_func: Callable) -> Callable:
    """직원 정보가 필요한 뷰에 사용하는 데코레이터"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not hasattr(request.user, 'employee'):
            messages.error(request, "직원 정보를 찾을 수 없습니다.")
            return redirect('home')
            
        return view_func(request, *args, **kwargs)
    return wrapped_view


def require_hr_permission(view_func: Callable) -> Callable:
    """HR 권한이 필요한 뷰에 사용하는 데코레이터"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not request.user.is_staff:
            messages.error(request, "이 페이지에 접근할 권한이 없습니다.")
            return redirect('home')
            
        return view_func(request, *args, **kwargs)
    return wrapped_view


def handle_exceptions(view_func: Callable) -> Callable:
    """예외 처리 데코레이터"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except EmployeeNotFoundError as e:
            messages.error(request, str(e))
            return redirect('home')
        except AuthorizationError as e:
            messages.error(request, str(e))
            return redirect('home')
        except Exception as e:
            logger.error(f"Unhandled exception in {view_func.__name__}: {str(e)}", exc_info=True)
            messages.error(request, "시스템 오류가 발생했습니다. 관리자에게 문의하세요.")
            return redirect('home')
    return wrapped_view


def ajax_response(view_func: Callable) -> Callable:
    """AJAX 응답 표준화 데코레이터"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        try:
            result = view_func(request, *args, **kwargs)
            
            # 이미 JsonResponse인 경우 그대로 반환
            if isinstance(result, JsonResponse):
                return result
                
            # dict인 경우 성공 응답으로 변환
            if isinstance(result, dict):
                return JsonResponse({
                    'success': True,
                    'data': result
                })
                
            # 기타 경우 그대로 반환
            return result
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'code': e.code,
                'details': e.details
            }, status=400)
        except AuthorizationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=403)
        except Exception as e:
            logger.error(f"AJAX exception in {view_func.__name__}: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': '서버 오류가 발생했습니다.'
            }, status=500)
    return wrapped_view


def log_access(model_name: str) -> Callable:
    """접근 로그를 기록하는 데코레이터"""
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            start_time = time.time()
            
            # 접근 로그
            logger.info(
                f"Access: {model_name} by {request.user.username} "
                f"from {request.META.get('REMOTE_ADDR', 'unknown')}"
            )
            
            result = view_func(request, *args, **kwargs)
            
            # 응답 시간 로그
            elapsed = time.time() - start_time
            logger.info(f"Response time for {model_name}: {elapsed:.2f}s")
            
            return result
        return wrapped_view
    return decorator


def measure_performance(view_func: Callable) -> Callable:
    """성능 측정 데코레이터"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        start_time = time.time()
        
        result = view_func(request, *args, **kwargs)
        
        elapsed = time.time() - start_time
        if elapsed > 1.0:  # 1초 이상 걸린 경우 경고
            logger.warning(
                f"Slow response in {view_func.__name__}: {elapsed:.2f}s"
            )
        
        return result
    return wrapped_view


def atomic_transaction(view_func: Callable) -> Callable:
    """트랜잭션 처리 데코레이터"""
    @wraps(view_func)
    @transaction.atomic
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapped_view


def cache_result(timeout: int = 300) -> Callable:
    """결과 캐싱 데코레이터"""
    def decorator(view_func: Callable) -> Callable:
        from django.core.cache import cache
        
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{view_func.__name__}:{request.user.id}:{args}:{kwargs}"
            
            # 캐시에서 확인
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return result
            
            # 실행 및 캐싱
            result = view_func(request, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapped_view
    return decorator