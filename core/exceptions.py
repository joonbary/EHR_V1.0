"""
커스텀 예외 클래스 정의
"""


class EHRBaseException(Exception):
    """eHR 시스템 기본 예외 클래스"""
    default_message = "시스템 오류가 발생했습니다."
    
    def __init__(self, message=None, code=None, details=None):
        self.message = message or self.default_message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(EHRBaseException):
    """데이터 검증 실패"""
    default_message = "입력 데이터가 올바르지 않습니다."


class AuthorizationError(EHRBaseException):
    """권한 부족"""
    default_message = "이 작업을 수행할 권한이 없습니다."


class EmployeeNotFoundError(EHRBaseException):
    """직원 정보 없음"""
    default_message = "직원 정보를 찾을 수 없습니다."


class FileProcessingError(EHRBaseException):
    """파일 처리 오류"""
    default_message = "파일 처리 중 오류가 발생했습니다."


class EvaluationError(EHRBaseException):
    """평가 처리 오류"""
    default_message = "평가 처리 중 오류가 발생했습니다."


class PromotionError(EHRBaseException):
    """승진 처리 오류"""
    default_message = "승진 처리 중 오류가 발생했습니다."


class CompensationError(EHRBaseException):
    """보상 처리 오류"""
    default_message = "보상 처리 중 오류가 발생했습니다."