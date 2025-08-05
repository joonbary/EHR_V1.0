"""
공통 믹스인 클래스
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import QuerySet
from typing import Dict, Any

from .exceptions import EmployeeNotFoundError, AuthorizationError
from .responses import ResponseFormatter


class EmployeeRequiredMixin(LoginRequiredMixin):
    """직원 정보가 필요한 뷰 믹스인"""
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'employee'):
            raise EmployeeNotFoundError()
        return super().dispatch(request, *args, **kwargs)


class HRPermissionMixin(UserPassesTestMixin):
    """HR 권한이 필요한 뷰 믹스인"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        raise AuthorizationError("HR 권한이 필요합니다.")


class PaginationMixin:
    """페이지네이션 믹스인"""
    paginate_by = 20
    
    def paginate_queryset(self, queryset: QuerySet, page_size: int = None) -> Dict[str, Any]:
        """쿼리셋 페이지네이션"""
        page_size = page_size or self.paginate_by
        paginator = Paginator(queryset, page_size)
        
        page = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        return {
            'page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': paginator.num_pages > 1,
            'page_range': paginator.get_elided_page_range(
                page_obj.number, on_each_side=2, on_ends=1
            )
        }


class AjaxResponseMixin:
    """AJAX 응답 믹스인"""
    
    def json_success(self, data: Any = None, message: str = "Success") -> JsonResponse:
        """JSON 성공 응답"""
        return ResponseFormatter.success_response(data, message)
    
    def json_error(self, error: str, code: str = None, details: Dict = None, status: int = 400) -> JsonResponse:
        """JSON 에러 응답"""
        return ResponseFormatter.error_response(error, code, details, status)
    
    def is_ajax(self) -> bool:
        """AJAX 요청 여부 확인"""
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'


class FilterMixin:
    """필터링 믹스인"""
    
    def apply_filters(self, queryset: QuerySet) -> QuerySet:
        """쿼리셋에 필터 적용"""
        # 검색어 필터
        search = self.request.GET.get('search')
        if search and hasattr(self, 'search_fields'):
            from django.db.models import Q
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': search})
            queryset = queryset.filter(query)
        
        # 추가 필터
        for key, value in self.request.GET.items():
            if key in getattr(self, 'filter_fields', []) and value:
                queryset = queryset.filter(**{key: value})
        
        # 정렬
        ordering = self.request.GET.get('ordering')
        if ordering and ordering.lstrip('-') in getattr(self, 'ordering_fields', []):
            queryset = queryset.order_by(ordering)
        
        return queryset


class ExportMixin:
    """데이터 내보내기 믹스인"""
    
    def export_to_excel(self, queryset: QuerySet, filename: str, columns: Dict[str, str]):
        """Excel 파일로 내보내기"""
        import pandas as pd
        from django.http import HttpResponse
        from io import BytesIO
        
        # 데이터 준비
        data = []
        for obj in queryset:
            row = {}
            for field, label in columns.items():
                value = obj
                for attr in field.split('.'):
                    value = getattr(value, attr, '')
                row[label] = value
            data.append(row)
        
        # DataFrame 생성
        df = pd.DataFrame(data)
        
        # Excel 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        output.seek(0)
        
        # HTTP 응답
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response