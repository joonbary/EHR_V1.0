"""
통합 검색 서비스 모듈
"""
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import (
    SearchIndex, SearchQuery, PopularSearch, 
    SearchSuggestion, SavedSearch
)
from employees.models import Employee
from organization.models import Department, Position
from notifications.models import AnnouncementBoard


class SearchIndexManager:
    """검색 인덱스 관리자"""
    
    @staticmethod
    def index_employee(employee: Employee):
        """직원 정보 인덱싱"""
        content_type = ContentType.objects.get_for_model(Employee)
        
        # 기존 인덱스 삭제
        SearchIndex.objects.filter(
            content_type=content_type,
            object_id=str(employee.id)
        ).delete()
        
        # 새 인덱스 생성
        keywords = [
            employee.name,
            employee.name_en or "",
            employee.department or "",
            employee.new_position or "",
            employee.phone or "",
            employee.email or "",
            f"Lv.{employee.growth_level}",
            employee.employment_status
        ]
        
        SearchIndex.objects.create(
            content_type=content_type,
            object_id=str(employee.id),
            search_type='EMPLOYEE',
            title=employee.name,
            content=f"{employee.name} ({employee.new_position}) - {employee.department}",
            keywords=" ".join(filter(None, keywords)),
            url=f"/employees/{employee.id}/",
            priority=5 if employee.employment_status == '재직' else 1
        )
    
    @staticmethod
    def index_department(department: Department):
        """부서 정보 인덱싱"""
        from organization.models import Department
        content_type = ContentType.objects.get_for_model(Department)
        
        SearchIndex.objects.filter(
            content_type=content_type,
            object_id=str(department.id)
        ).delete()
        
        keywords = [
            department.name,
            department.name_en or "",
            department.code,
            department.get_department_type_display(),
            department.manager.name if department.manager else "",
            department.location or ""
        ]
        
        SearchIndex.objects.create(
            content_type=content_type,
            object_id=str(department.id),
            search_type='DEPARTMENT',
            title=department.name,
            content=f"{department.name} ({department.code}) - {department.get_department_type_display()}",
            keywords=" ".join(filter(None, keywords)),
            url=f"/organization/departments/{department.id}/",
            priority=3 if department.is_active else 1
        )
    
    @staticmethod
    def index_announcement(announcement: AnnouncementBoard):
        """공지사항 인덱싱"""
        content_type = ContentType.objects.get_for_model(AnnouncementBoard)
        
        SearchIndex.objects.filter(
            content_type=content_type,
            object_id=str(announcement.id)
        ).delete()
        
        keywords = [
            announcement.title,
            announcement.author.name,
            announcement.get_visibility_display(),
            "중요" if announcement.is_important else "",
            "긴급" if announcement.is_urgent else ""
        ]
        
        # 접근 권한 설정
        department_restricted = ""
        if announcement.visibility == 'DEPARTMENT' and announcement.target_departments.exists():
            department_restricted = announcement.target_departments.first().code
        
        SearchIndex.objects.create(
            content_type=content_type,
            object_id=str(announcement.id),
            search_type='ANNOUNCEMENT',
            title=announcement.title,
            content=announcement.content[:1000],  # 내용 일부만
            keywords=" ".join(filter(None, keywords)),
            url=f"/notifications/announcements/{announcement.id}/",
            department_restricted=department_restricted,
            is_public=announcement.is_published,
            priority=10 if announcement.is_urgent else 5 if announcement.is_important else 3
        )
    
    @staticmethod
    def rebuild_all_indexes():
        """모든 인덱스 재구축"""
        # 기존 인덱스 삭제
        SearchIndex.objects.all().delete()
        
        # 직원 인덱싱
        for employee in Employee.objects.all():
            SearchIndexManager.index_employee(employee)
        
        # 부서 인덱싱
        from organization.models import Department
        for department in Department.objects.all():
            SearchIndexManager.index_department(department)
        
        # 공지사항 인덱싱
        for announcement in AnnouncementBoard.objects.filter(is_published=True):
            SearchIndexManager.index_announcement(announcement)


class SearchService:
    """통합 검색 서비스"""
    
    @staticmethod
    def search(
        query: str,
        search_type: str = "",
        user: Employee = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        통합 검색 실행
        
        Args:
            query: 검색어
            search_type: 검색 분류 (선택사항)
            user: 검색 사용자
            limit: 결과 수 제한
            
        Returns:
            검색 결과 딕셔너리
        """
        start_time = time.time()
        
        # 검색어 정규화
        normalized_query = SearchService._normalize_query(query)
        
        if not normalized_query:
            return {
                'results': [],
                'total_count': 0,
                'execution_time': 0,
                'suggestions': []
            }
        
        # 기본 쿼리셋
        queryset = SearchIndex.objects.filter(is_public=True)
        
        # 검색 분류 필터
        if search_type:
            queryset = queryset.filter(search_type=search_type)
        
        # 접근 권한 필터
        if user:
            # 부서 제한 필터
            queryset = queryset.filter(
                Q(department_restricted="") | 
                Q(department_restricted=user.department)
            )
        
        # 텍스트 검색
        search_terms = normalized_query.split()
        search_q = Q()
        
        for term in search_terms:
            term_q = (
                Q(title__icontains=term) |
                Q(content__icontains=term) |
                Q(keywords__icontains=term)
            )
            search_q &= term_q
        
        queryset = queryset.filter(search_q)
        
        # 우선순위 정렬
        queryset = queryset.order_by('-priority', '-search_count', '-updated_at')
        
        # 결과 제한
        results = queryset[:limit]
        total_count = queryset.count()
        
        # 검색 통계 업데이트
        for result in results:
            result.increment_search_count()
        
        # 검색 로그 기록
        execution_time = time.time() - start_time
        if user:
            SearchService._log_search(
                user=user,
                query=query,
                normalized_query=normalized_query,
                search_type=search_type,
                results_count=total_count,
                execution_time=execution_time
            )
        
        # 인기 검색어 업데이트
        SearchService._update_popular_search(normalized_query)
        
        # 검색 제안 생성
        suggestions = SearchService._get_suggestions(normalized_query, search_type)
        
        return {
            'results': [SearchService._format_result(result) for result in results],
            'total_count': total_count,
            'execution_time': execution_time,
            'suggestions': suggestions
        }
    
    @staticmethod
    def _normalize_query(query: str) -> str:
        """검색어 정규화"""
        if not query:
            return ""
        
        # 공백 정리
        normalized = re.sub(r'\s+', ' ', query.strip())
        
        # 특수문자 제거 (한글, 영문, 숫자, 기본 구두점만 유지)
        normalized = re.sub(r'[^\w\s\.\-\@]', '', normalized, flags=re.UNICODE)
        
        return normalized
    
    @staticmethod
    def _format_result(result: SearchIndex) -> Dict[str, Any]:
        """검색 결과 포맷팅"""
        return {
            'id': str(result.id),
            'type': result.search_type,
            'type_display': result.get_search_type_display(),
            'title': result.title,
            'content': result.content[:200] + '...' if len(result.content) > 200 else result.content,
            'url': result.url,
            'image_url': result.image_url,
            'priority': result.priority,
            'search_count': result.search_count,
            'last_searched': result.last_searched
        }
    
    @staticmethod
    def _log_search(
        user: Employee,
        query: str,
        normalized_query: str,
        search_type: str,
        results_count: int,
        execution_time: float
    ):
        """검색 로그 기록"""
        SearchQuery.objects.create(
            user=user,
            query=query,
            query_normalized=normalized_query,
            search_type=search_type,
            results_count=results_count,
            execution_time=execution_time
        )
    
    @staticmethod
    def _update_popular_search(query: str):
        """인기 검색어 업데이트"""
        if len(query) < 2:  # 너무 짧은 검색어는 제외
            return
        
        popular_search, created = PopularSearch.objects.get_or_create(
            query=query
        )
        popular_search.increment_count()
    
    @staticmethod
    def _get_suggestions(query: str, search_type: str = "") -> List[Dict[str, Any]]:
        """검색 제안 조회"""
        suggestions = []
        
        if len(query) >= 2:
            # 자동완성 제안
            auto_suggestions = SearchSuggestion.objects.filter(
                query__icontains=query,
                is_active=True
            )
            
            if search_type:
                auto_suggestions = auto_suggestions.filter(
                    suggestion_type=search_type
                )
            
            for suggestion in auto_suggestions[:5]:
                suggestions.append({
                    'text': suggestion.display_text,
                    'query': suggestion.query,
                    'type': suggestion.suggestion_type,
                    'usage_count': suggestion.usage_count
                })
        
        # 인기 검색어 제안
        if not suggestions:
            popular_searches = PopularSearch.objects.filter(
                query__icontains=query
            )[:3]
            
            for popular in popular_searches:
                suggestions.append({
                    'text': popular.query,
                    'query': popular.query,
                    'type': 'POPULAR',
                    'usage_count': popular.search_count
                })
        
        return suggestions
    
    @staticmethod
    def get_popular_searches(limit: int = 10) -> List[Dict[str, Any]]:
        """인기 검색어 조회"""
        popular_searches = PopularSearch.objects.order_by('-trend_score')[:limit]
        
        return [
            {
                'query': search.query,
                'count': search.search_count,
                'trend_score': search.trend_score,
                'last_searched': search.last_searched
            }
            for search in popular_searches
        ]
    
    @staticmethod
    def get_recent_searches(user: Employee, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 검색어 조회"""
        recent_searches = SearchQuery.objects.filter(
            user=user
        ).order_by('-created_at')[:limit]
        
        return [
            {
                'query': search.query,
                'search_type': search.search_type,
                'results_count': search.results_count,
                'created_at': search.created_at
            }
            for search in recent_searches
        ]
    
    @staticmethod
    def save_search(
        user: Employee,
        name: str,
        query: str,
        search_type: str = "",
        enable_alerts: bool = False
    ) -> SavedSearch:
        """검색 저장"""
        saved_search = SavedSearch.objects.create(
            user=user,
            name=name,
            query=query,
            search_type=search_type,
            enable_alerts=enable_alerts
        )
        
        return saved_search


class SearchAnalytics:
    """검색 분석 서비스"""
    
    @staticmethod
    def get_search_statistics(days: int = 30) -> Dict[str, Any]:
        """검색 통계 조회"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # 기간별 검색 쿼리
        queries = SearchQuery.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # 총 검색 수
        total_searches = queries.count()
        
        # 고유 사용자 수
        unique_users = queries.values('user').distinct().count()
        
        # 평균 실행 시간
        avg_execution_time = queries.aggregate(
            avg_time=models.Avg('execution_time')
        )['avg_time'] or 0
        
        # 검색 분류별 통계
        type_stats = queries.values('search_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 인기 검색어
        popular_queries = queries.values('query_normalized').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # 검색 결과 없는 쿼리
        no_results_queries = queries.filter(results_count=0).count()
        
        return {
            'total_searches': total_searches,
            'unique_users': unique_users,
            'avg_execution_time': round(avg_execution_time, 3),
            'no_results_rate': round(no_results_queries / total_searches * 100, 1) if total_searches > 0 else 0,
            'type_statistics': list(type_stats),
            'popular_queries': list(popular_queries),
            'no_results_count': no_results_queries
        }
    
    @staticmethod
    def get_user_search_patterns(user: Employee, days: int = 30) -> Dict[str, Any]:
        """사용자 검색 패턴 분석"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        queries = SearchQuery.objects.filter(
            user=user,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        return {
            'total_searches': queries.count(),
            'avg_execution_time': queries.aggregate(
                avg_time=models.Avg('execution_time')
            )['avg_time'] or 0,
            'most_searched_type': queries.values('search_type').annotate(
                count=Count('id')
            ).order_by('-count').first(),
            'recent_queries': queries.order_by('-created_at')[:5].values(
                'query', 'search_type', 'results_count', 'created_at'
            )
        }


# 편의 함수들
def quick_search(query: str, user: Employee = None) -> List[Dict[str, Any]]:
    """빠른 검색 (결과만 반환)"""
    result = SearchService.search(query=query, user=user, limit=20)
    return result['results']


def search_employees(name: str, user: Employee = None) -> List[Dict[str, Any]]:
    """직원 검색"""
    result = SearchService.search(
        query=name,
        search_type='EMPLOYEE',
        user=user,
        limit=20
    )
    return result['results']


def search_departments(name: str, user: Employee = None) -> List[Dict[str, Any]]:
    """부서 검색"""
    result = SearchService.search(
        query=name,
        search_type='DEPARTMENT',
        user=user,
        limit=20
    )
    return result['results']