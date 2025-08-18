"""
커스텀 예외 클래스 정의 - Enhanced with Type Hints
"""
from typing import Optional, Dict, Any
from django.http import JsonResponse


class EHRBaseException(Exception):
    """eHR 시스템 기본 예외 클래스"""
    default_message: str = "시스템 오류가 발생했습니다."
    error_code: str = "EHR_ERROR"
    status_code: int = 500
    
    def __init__(
        self, 
        message: Optional[str] = None, 
        code: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message or self.default_message
        self.code = code or self.error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error_code": self.code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }
    
    def to_response(self) -> JsonResponse:
        """Convert exception to JsonResponse"""
        return JsonResponse(self.to_dict(), status=self.status_code)


class ValidationError(EHRBaseException):
    """데이터 검증 실패"""
    default_message: str = "입력 데이터가 올바르지 않습니다."
    error_code: str = "VALIDATION_ERROR"
    status_code: int = 400


class AuthorizationError(EHRBaseException):
    """권한 부족"""
    default_message: str = "이 작업을 수행할 권한이 없습니다."
    error_code: str = "AUTHORIZATION_ERROR"
    status_code: int = 403


class EmployeeNotFoundError(EHRBaseException):
    """직원 정보 없음"""
    default_message: str = "직원 정보를 찾을 수 없습니다."
    error_code: str = "EMPLOYEE_NOT_FOUND"
    status_code: int = 404


class FileProcessingError(EHRBaseException):
    """파일 처리 오류"""
    default_message: str = "파일 처리 중 오류가 발생했습니다."
    error_code: str = "FILE_PROCESSING_ERROR"
    status_code: int = 400


class EvaluationError(EHRBaseException):
    """평가 처리 오류"""
    default_message: str = "평가 처리 중 오류가 발생했습니다."
    error_code: str = "EVALUATION_ERROR"
    status_code: int = 422


class PromotionError(EHRBaseException):
    """승진 처리 오류"""
    default_message: str = "승진 처리 중 오류가 발생했습니다."
    error_code: str = "PROMOTION_ERROR"
    status_code: int = 422


class CompensationError(EHRBaseException):
    """보상 처리 오류"""
    default_message: str = "보상 처리 중 오류가 발생했습니다."
    error_code: str = "COMPENSATION_ERROR"
    status_code: int = 422


class DuplicateError(EHRBaseException):
    """중복 데이터 오류"""
    default_message: str = "이미 존재하는 데이터입니다."
    error_code: str = "DUPLICATE_ERROR"
    status_code: int = 409


class RateLimitError(EHRBaseException):
    """요청 제한 초과"""
    default_message: str = "요청 제한을 초과했습니다. 잠시 후 다시 시도해주세요."
    error_code: str = "RATE_LIMIT_ERROR"
    status_code: int = 429