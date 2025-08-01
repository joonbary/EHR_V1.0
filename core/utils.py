"""
공통 유틸리티 함수
"""
from datetime import date, datetime, timedelta
from typing import Tuple, Optional, Dict, List
from django.utils import timezone
from django.db.models import Model, QuerySet
import hashlib
import random
import string


class DateCalculator:
    """날짜 계산 유틸리티"""
    
    @staticmethod
    def calculate_work_period(hire_date: date, target_date: Optional[date] = None) -> Tuple[int, int, int]:
        """근무 기간 계산 (년, 월, 일)"""
        if not target_date:
            target_date = date.today()
        
        # 연도 차이
        years = target_date.year - hire_date.year
        
        # 월 조정
        if target_date.month < hire_date.month:
            years -= 1
            months = 12 + target_date.month - hire_date.month
        else:
            months = target_date.month - hire_date.month
        
        # 일 조정
        if target_date.day < hire_date.day:
            months -= 1
            if months < 0:
                years -= 1
                months += 12
            
            # 이전 달의 마지막 날 계산
            prev_month = target_date.replace(day=1) - timedelta(days=1)
            days = prev_month.day - hire_date.day + target_date.day
        else:
            days = target_date.day - hire_date.day
        
        return years, months, days
    
    @staticmethod
    def get_fiscal_year_range(year: int) -> Tuple[date, date]:
        """회계연도 범위 반환"""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        return start_date, end_date
    
    @staticmethod
    def get_quarter_range(year: int, quarter: int) -> Tuple[date, date]:
        """분기 범위 반환"""
        if quarter not in [1, 2, 3, 4]:
            raise ValueError("분기는 1-4 사이의 값이어야 합니다.")
        
        quarter_starts = {
            1: (1, 1),
            2: (4, 1),
            3: (7, 1),
            4: (10, 1)
        }
        
        start_month, start_day = quarter_starts[quarter]
        start_date = date(year, start_month, start_day)
        
        # 분기 종료일
        if quarter == 4:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, start_month + 3, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    @staticmethod
    def is_weekend(check_date: date) -> bool:
        """주말 여부 확인"""
        return check_date.weekday() >= 5  # 5: 토요일, 6: 일요일
    
    @staticmethod
    def add_business_days(start_date: date, business_days: int) -> date:
        """영업일 기준 날짜 계산"""
        current_date = start_date
        days_added = 0
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            if not DateCalculator.is_weekend(current_date):
                days_added += 1
        
        return current_date


class StringUtils:
    """문자열 유틸리티"""
    
    @staticmethod
    def generate_employee_number(prefix: str = "EMP") -> str:
        """직원 번호 생성"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_suffix}"
    
    @staticmethod
    def mask_email(email: str) -> str:
        """이메일 마스킹"""
        if '@' not in email:
            return email
        
        local, domain = email.split('@')
        if len(local) <= 3:
            masked_local = local[0] + '*' * (len(local) - 1)
        else:
            masked_local = local[:2] + '*' * (len(local) - 4) + local[-2:]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """전화번호 마스킹"""
        # 숫자만 추출
        digits = ''.join(filter(str.isdigit, phone))
        
        if len(digits) >= 8:
            return f"{digits[:3]}-****-{digits[-4:]}"
        return phone
    
    @staticmethod
    def generate_hash(value: str) -> str:
        """SHA256 해시 생성"""
        return hashlib.sha256(value.encode()).hexdigest()


class QueryUtils:
    """쿼리 유틸리티"""
    
    @staticmethod
    def get_or_none(model: Model, **kwargs) -> Optional[Model]:
        """객체 조회 또는 None 반환"""
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            return None
        except model.MultipleObjectsReturned:
            return model.objects.filter(**kwargs).first()
    
    @staticmethod
    def bulk_update_or_create(model: Model, objects: List[Dict], lookup_fields: List[str]) -> Tuple[int, int]:
        """대량 업데이트 또는 생성"""
        created_count = 0
        updated_count = 0
        
        for obj_data in objects:
            lookup_kwargs = {field: obj_data[field] for field in lookup_fields}
            obj, created = model.objects.update_or_create(
                defaults=obj_data,
                **lookup_kwargs
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        return created_count, updated_count
    
    @staticmethod
    def get_active_employees(department: Optional[str] = None) -> QuerySet:
        """활성 직원 조회"""
        from employees.models import Employee
        
        queryset = Employee.objects.filter(is_active=True)
        if department:
            queryset = queryset.filter(department=department)
        
        return queryset.select_related('user')


class NumberUtils:
    """숫자 유틸리티"""
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """통화 형식 포맷팅"""
        return f"₩{amount:,.0f}"
    
    @staticmethod
    def calculate_percentage(value: float, total: float) -> float:
        """백분율 계산"""
        if total == 0:
            return 0
        return round((value / total) * 100, 2)
    
    @staticmethod
    def round_to_nearest(value: float, nearest: int = 10) -> int:
        """가장 가까운 값으로 반올림"""
        return int(round(value / nearest) * nearest)