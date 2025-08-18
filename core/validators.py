"""
공통 검증 유틸리티
"""
import re
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
from django.core.exceptions import ValidationError as DjangoValidationError

from .exceptions import ValidationError


class HRValidators:
    """HR 데이터 검증 클래스"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """이메일 형식 검증"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError(
                "올바른 이메일 형식이 아닙니다.",
                code="invalid_email",
                details={"email": email}
            )
        return email.lower()
    
    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """전화번호 형식 검증"""
        # 숫자와 하이픈만 허용
        phone = re.sub(r'[^\d-]', '', phone)
        
        # 한국 전화번호 패턴
        patterns = [
            r'^01[0-9]-\d{3,4}-\d{4}$',  # 휴대폰
            r'^0\d{1,2}-\d{3,4}-\d{4}$',  # 일반전화
        ]
        
        if not any(re.match(pattern, phone) for pattern in patterns):
            raise ValidationError(
                "올바른 전화번호 형식이 아닙니다. (예: 010-1234-5678)",
                code="invalid_phone",
                details={"phone": phone}
            )
        return phone
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> Tuple[date, date]:
        """날짜 범위 검증"""
        if start_date > end_date:
            raise ValidationError(
                "시작일이 종료일보다 늦을 수 없습니다.",
                code="invalid_date_range",
                details={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
        return start_date, end_date
    
    @staticmethod
    def validate_employee_data(data: Dict) -> Dict:
        """직원 데이터 종합 검증"""
        errors = {}
        
        # 필수 필드 검증
        required_fields = ['name', 'email', 'department', 'position']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field}은(는) 필수 입력 항목입니다."
        
        # 이메일 검증
        if data.get('email'):
            try:
                data['email'] = HRValidators.validate_email(data['email'])
            except ValidationError as e:
                errors['email'] = str(e)
        
        # 전화번호 검증
        if data.get('phone'):
            try:
                data['phone'] = HRValidators.validate_phone_number(data['phone'])
            except ValidationError as e:
                errors['phone'] = str(e)
        
        # 입사일 검증
        if data.get('hire_date'):
            hire_date = data['hire_date']
            if isinstance(hire_date, str):
                try:
                    hire_date = datetime.strptime(hire_date, '%Y-%m-%d').date()
                    data['hire_date'] = hire_date
                except ValueError:
                    errors['hire_date'] = "날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)"
            
            if hire_date > date.today():
                errors['hire_date'] = "입사일은 미래 날짜일 수 없습니다."
        
        if errors:
            raise ValidationError(
                "입력 데이터 검증 실패",
                code="validation_failed",
                details=errors
            )
        
        return data
    
    @staticmethod
    def validate_score(score: float, min_score: float = 0, max_score: float = 5) -> float:
        """점수 범위 검증"""
        try:
            score = float(score)
        except (TypeError, ValueError):
            raise ValidationError(
                "점수는 숫자여야 합니다.",
                code="invalid_score_type"
            )
        
        if not min_score <= score <= max_score:
            raise ValidationError(
                f"점수는 {min_score}에서 {max_score} 사이여야 합니다.",
                code="score_out_of_range",
                details={"score": score, "min": min_score, "max": max_score}
            )
        
        return score
    
    @staticmethod
    def validate_grade(grade: str) -> str:
        """평가 등급 검증"""
        valid_grades = ['S', 'A+', 'A', 'B+', 'B', 'C', 'D']
        grade = grade.upper()
        
        if grade not in valid_grades:
            raise ValidationError(
                f"유효하지 않은 등급입니다. 가능한 등급: {', '.join(valid_grades)}",
                code="invalid_grade",
                details={"grade": grade}
            )
        
        return grade
    
    @staticmethod
    def validate_percentage(value: float, field_name: str = "비율") -> float:
        """백분율 검증"""
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValidationError(
                f"{field_name}은(는) 숫자여야 합니다.",
                code="invalid_percentage_type"
            )
        
        if not 0 <= value <= 100:
            raise ValidationError(
                f"{field_name}은(는) 0에서 100 사이여야 합니다.",
                code="percentage_out_of_range",
                details={"value": value}
            )
        
        return value


class FileValidators:
    """파일 검증 클래스"""
    
    ALLOWED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ALLOWED_DOCUMENT_TYPES = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv']
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def validate_image_file(cls, file) -> None:
        """이미지 파일 검증"""
        # 파일 확장자 검증
        import os
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in cls.ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                f"허용되지 않은 이미지 형식입니다. 허용 형식: {', '.join(cls.ALLOWED_IMAGE_TYPES)}",
                code="invalid_image_type",
                details={"extension": ext}
            )
        
        # 파일 크기 검증
        if file.size > cls.MAX_IMAGE_SIZE:
            raise ValidationError(
                f"이미지 파일 크기는 {cls.MAX_IMAGE_SIZE // (1024*1024)}MB를 초과할 수 없습니다.",
                code="image_too_large",
                details={"size": file.size}
            )
    
    @classmethod
    def validate_document_file(cls, file) -> None:
        """문서 파일 검증"""
        import os
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in cls.ALLOWED_DOCUMENT_TYPES:
            raise ValidationError(
                f"허용되지 않은 문서 형식입니다. 허용 형식: {', '.join(cls.ALLOWED_DOCUMENT_TYPES)}",
                code="invalid_document_type",
                details={"extension": ext}
            )
        
        if file.size > cls.MAX_DOCUMENT_SIZE:
            raise ValidationError(
                f"문서 파일 크기는 {cls.MAX_DOCUMENT_SIZE // (1024*1024)}MB를 초과할 수 없습니다.",
                code="document_too_large",
                details={"size": file.size}
            )