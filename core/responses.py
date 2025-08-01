"""
표준화된 응답 클래스
"""
from typing import Any, Dict, Optional
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages


class ResponseFormatter:
    """응답 포맷터"""
    
    @staticmethod
    def success_response(
        data: Any = None,
        message: str = "Success",
        status: int = 200
    ) -> JsonResponse:
        """성공 응답"""
        response_data = {
            'success': True,
            'message': message
        }
        if data is not None:
            response_data['data'] = data
            
        return JsonResponse(response_data, status=status)
    
    @staticmethod
    def error_response(
        error: str,
        code: Optional[str] = None,
        details: Optional[Dict] = None,
        status: int = 400
    ) -> JsonResponse:
        """에러 응답"""
        response_data = {
            'success': False,
            'error': error
        }
        if code:
            response_data['code'] = code
        if details:
            response_data['details'] = details
            
        return JsonResponse(response_data, status=status)
    
    @staticmethod
    def validation_error_response(errors: Dict, status: int = 400) -> JsonResponse:
        """검증 에러 응답"""
        return JsonResponse({
            'success': False,
            'error': '입력 데이터 검증 실패',
            'code': 'validation_error',
            'details': errors
        }, status=status)
    
    @staticmethod
    def paginated_response(
        data: list,
        page: int,
        total_pages: int,
        total_count: int,
        per_page: int
    ) -> JsonResponse:
        """페이지네이션 응답"""
        return JsonResponse({
            'success': True,
            'data': data,
            'pagination': {
                'page': page,
                'total_pages': total_pages,
                'total_count': total_count,
                'per_page': per_page,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })


class TemplateResponseMixin:
    """템플릿 응답 믹스인"""
    
    def render_with_message(
        self,
        request,
        template_name: str,
        context: Dict,
        message: Optional[str] = None,
        message_type: str = 'info'
    ):
        """메시지와 함께 템플릿 렌더링"""
        if message:
            getattr(messages, message_type)(request, message)
        return render(request, template_name, context)
    
    def render_error_page(
        self,
        request,
        error_message: str,
        template_name: str = 'error.html',
        status_code: int = 400
    ):
        """에러 페이지 렌더링"""
        context = {
            'error_message': error_message,
            'status_code': status_code
        }
        response = render(request, template_name, context)
        response.status_code = status_code
        return response