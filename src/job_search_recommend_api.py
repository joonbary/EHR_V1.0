"""
직무 정보 탐색·검색·추천 API 및 챗봇 통합 시스템
Job Search, Recommendation API and Chatbot Integration System

UX search designer + LLM HR analyst + API integrator 통합 설계
- 필드 기반 검색 (fieldsearch)
- 관련 직무 추천 (relatedjobs) 
- 커리어 패스 분석 (careerpath)
- 즉시 응답 (instantresponse)
- 컨텍스트 인식 (contextaware)
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.db.models import Q, Count, Avg
from django.utils import timezone

# eHR System Models
from employees.models import Employee
from job_profiles.models import JobProfile, JobRole, JobType, JobCategory
from job_profiles.services import JobProfileService
from job_profiles.growth_services import GrowthPathRecommender
from job_profiles.evaluation_services import EvaluationIntegratedService
from job_profiles.leader_services import LeaderRecommendationService
from certifications.certification_services import CertificationService

logger = logging.getLogger(__name__)


class SearchIntent(Enum):
    """검색 의도 분류"""
    JOB_SEARCH = "job_search"                    # 직무 검색
    SKILL_MATCH = "skill_match"                  # 스킬 매칭
    CAREER_PATH = "career_path"                  # 커리어 경로
    SALARY_INQUIRY = "salary_inquiry"            # 급여 문의
    REQUIREMENT_CHECK = "requirement_check"      # 자격 요건 확인
    GROWTH_PLANNING = "growth_planning"          # 성장 계획
    SIMILAR_JOBS = "similar_jobs"                # 유사 직무
    CERTIFICATION = "certification"              # 자격증 정보


class ResponseFormat(Enum):
    """응답 형식"""
    LIST = "list"                               # 목록형
    CARD = "card"                               # 카드형
    DETAILED = "detailed"                       # 상세형  
    CONVERSATIONAL = "conversational"           # 대화형
    COMPARISON = "comparison"                   # 비교형


@dataclass
class SearchContext:
    """검색 컨텍스트"""
    user_id: str
    session_id: str
    intent: SearchIntent
    query: str
    filters: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class JobSearchResult:
    """직무 검색 결과"""
    job_id: str
    job_name: str
    job_code: str
    category: str
    type_name: str
    match_score: float
    relevance_score: float
    requirements: List[str]
    skills_required: List[str]
    growth_path: str
    certifications: List[str]
    similar_jobs: List[Dict[str, Any]]
    career_level: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class JobSearchEngine:
    """직무 검색 엔진"""
    
    def __init__(self):
        self.job_service = JobProfileService()
        self.growth_recommender = GrowthPathRecommender()
        self.eval_service = EvaluationIntegratedService()
        self.leader_service = LeaderRecommendationService()
        self.cert_service = CertificationService()
        
        # 캐시 설정
        self.cache_timeout = 300  # 5분
        self.search_cache_prefix = "job_search:"
        
    def search_jobs(self, context: SearchContext) -> List[JobSearchResult]:
        """통합 직무 검색"""
        cache_key = f"{self.search_cache_prefix}{hash(str(context.query + str(context.filters)))}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
            
        # 기본 검색
        base_results = self._search_by_query(context.query, context.filters)
        
        # 컨텍스트 기반 향상
        enhanced_results = self._enhance_with_context(base_results, context)
        
        # 관련 직무 추가
        related_results = self._add_related_jobs(enhanced_results, context)
        
        # 최종 결과 정렬 및 스코어링
        final_results = self._score_and_rank(related_results, context)
        
        # 캐시 저장
        cache.set(cache_key, final_results, self.cache_timeout)
        
        return final_results
    
    def _search_by_query(self, query: str, filters: Dict[str, Any]) -> List[JobProfile]:
        """쿼리 기반 기본 검색"""
        queryset = JobProfile.objects.filter(is_active=True).select_related(
            'job_role__job_type__category'
        )
        
        # 텍스트 검색
        if query:
            q_objects = Q()
            keywords = query.split()
            
            for keyword in keywords:
                q_objects |= (
                    Q(job_role__name__icontains=keyword) |
                    Q(job_role__job_type__name__icontains=keyword) |
                    Q(job_role__job_type__category__name__icontains=keyword) |
                    Q(role_responsibility__icontains=keyword) |
                    Q(qualification__icontains=keyword) |
                    Q(basic_skills__icontains=keyword) |
                    Q(applied_skills__icontains=keyword)
                )
            
            queryset = queryset.filter(q_objects)
        
        # 필터 적용
        if filters.get('category'):
            queryset = queryset.filter(
                job_role__job_type__category__name=filters['category']
            )
        
        if filters.get('job_type'):
            queryset = queryset.filter(
                job_role__job_type__name=filters['job_type']
            )
        
        if filters.get('skills'):
            skill_filters = Q()
            for skill in filters['skills']:
                skill_filters |= (
                    Q(basic_skills__icontains=skill) |
                    Q(applied_skills__icontains=skill)
                )
            queryset = queryset.filter(skill_filters)
        
        return list(queryset[:50])  # 최대 50개
    
    def _enhance_with_context(self, jobs: List[JobProfile], context: SearchContext) -> List[JobSearchResult]:
        """컨텍스트 기반 결과 향상"""
        enhanced_results = []
        
        for job in jobs:
            # 기본 매칭 점수 계산
            match_score = self._calculate_match_score(job, context)
            
            # 관련성 점수 계산
            relevance_score = self._calculate_relevance(job, context)
            
            # 유사 직무 찾기
            similar_jobs = self._find_similar_jobs(job)
            
            result = JobSearchResult(
                job_id=str(job.id),
                job_name=job.job_role.name,
                job_code=job.job_role.code,
                category=job.job_role.job_type.category.name,
                type_name=job.job_role.job_type.name,
                match_score=match_score,
                relevance_score=relevance_score,
                requirements=self._extract_requirements(job),
                skills_required=job.get_all_skills(),
                growth_path=job.growth_path,
                certifications=job.related_certifications,
                similar_jobs=similar_jobs,
                career_level=self._determine_career_level(job),
                metadata={
                    'created_at': job.created_at.isoformat(),
                    'updated_at': job.updated_at.isoformat(),
                    'full_path': job.job_role.full_path
                }
            )
            
            enhanced_results.append(result)
        
        return enhanced_results
    
    def _add_related_jobs(self, results: List[JobSearchResult], context: SearchContext) -> List[JobSearchResult]:
        """관련 직무 추가"""
        if not results:
            return results
        
        # 상위 3개 결과를 기준으로 관련 직무 찾기
        top_results = results[:3]
        related_jobs_set = set()
        
        for result in top_results:
            # 같은 카테고리의 다른 직무들
            related_in_category = JobProfile.objects.filter(
                job_role__job_type__category__name=result.category,
                is_active=True
            ).exclude(id=result.job_id)[:5]
            
            for job in related_in_category:
                if str(job.id) not in [r.job_id for r in results]:
                    related_jobs_set.add(job)
        
        # 관련 직무들을 결과에 추가
        for job in list(related_jobs_set)[:10]:  # 최대 10개 추가
            match_score = self._calculate_match_score(job, context) * 0.8  # 관련 직무는 점수 할인
            
            related_result = JobSearchResult(
                job_id=str(job.id),
                job_name=job.job_role.name,
                job_code=job.job_role.code,
                category=job.job_role.job_type.category.name,
                type_name=job.job_role.job_type.name,
                match_score=match_score,
                relevance_score=self._calculate_relevance(job, context) * 0.8,
                requirements=self._extract_requirements(job),
                skills_required=job.get_all_skills(),
                growth_path=job.growth_path,
                certifications=job.related_certifications,
                similar_jobs=[],
                career_level=self._determine_career_level(job),
                metadata={
                    'is_related': True,
                    'full_path': job.job_role.full_path
                }
            )
            
            results.append(related_result)
        
        return results
    
    def _calculate_match_score(self, job: JobProfile, context: SearchContext) -> float:
        """매칭 점수 계산"""
        score = 50.0  # 기본 점수
        
        query_keywords = context.query.lower().split() if context.query else []
        
        # 직무명 매칭
        job_name = job.job_role.name.lower()
        for keyword in query_keywords:
            if keyword in job_name:
                score += 20
        
        # 스킬 매칭
        all_skills = [skill.lower() for skill in job.get_all_skills()]
        for keyword in query_keywords:
            if any(keyword in skill for skill in all_skills):
                score += 15
        
        # 카테고리/타입 매칭
        category_type = f"{job.job_role.job_type.category.name} {job.job_role.job_type.name}".lower()
        for keyword in query_keywords:
            if keyword in category_type:
                score += 10
        
        # 사용자 선호도 반영
        if context.preferences.get('preferred_categories'):
            if job.job_role.job_type.category.name in context.preferences['preferred_categories']:
                score += 10
        
        return min(score, 100.0)  # 최대 100점
    
    def _calculate_relevance(self, job: JobProfile, context: SearchContext) -> float:
        """관련성 점수 계산"""
        relevance = 50.0
        
        # 최근 검색 이력 기반
        if context.history:
            recent_searches = [h.get('query', '') for h in context.history[-5:]]
            for search in recent_searches:
                if search and any(word in job.job_role.name.lower() for word in search.lower().split()):
                    relevance += 5
        
        # 필터 일치도
        if context.filters:
            for key, value in context.filters.items():
                if key == 'category' and value == job.job_role.job_type.category.name:
                    relevance += 15
                elif key == 'job_type' and value == job.job_role.job_type.name:
                    relevance += 10
        
        return min(relevance, 100.0)
    
    def _find_similar_jobs(self, job: JobProfile, limit: int = 3) -> List[Dict[str, Any]]:
        """유사 직무 찾기"""
        # 같은 타입의 다른 직무들
        similar = JobProfile.objects.filter(
            job_role__job_type=job.job_role.job_type,
            is_active=True
        ).exclude(id=job.id)[:limit]
        
        return [
            {
                'id': str(s.id),
                'name': s.job_role.name,
                'code': s.job_role.code,
                'similarity_score': 85.0  # 임시 점수
            }
            for s in similar
        ]
    
    def _extract_requirements(self, job: JobProfile) -> List[str]:
        """자격 요건 추출"""
        requirements = []
        
        if job.qualification:
            # 간단히 줄바꿈으로 분리
            for req in job.qualification.split('\n'):
                req = req.strip()
                if req and len(req) > 5:
                    requirements.append(req)
        
        return requirements[:5]  # 최대 5개
    
    def _determine_career_level(self, job: JobProfile) -> str:
        """커리어 레벨 결정"""
        job_name = job.job_role.name.lower()
        
        if any(word in job_name for word in ['신입', '주니어', 'junior', '인턴']):
            return "신입"
        elif any(word in job_name for word in ['시니어', 'senior', '책임', '선임']):
            return "시니어"
        elif any(word in job_name for word in ['리드', 'lead', '팀장', '매니저', 'manager']):
            return "리더"
        elif any(word in job_name for word in ['임원', '이사', '부장', 'director']):
            return "임원"
        else:
            return "경력"
    
    def _score_and_rank(self, results: List[JobSearchResult], context: SearchContext) -> List[JobSearchResult]:
        """최종 점수화 및 순위 결정"""
        for result in results:
            # 종합 점수 = 매칭 점수 * 0.7 + 관련성 점수 * 0.3
            result.metadata['final_score'] = (
                result.match_score * 0.7 + result.relevance_score * 0.3
            )
        
        # 점수순 정렬
        results.sort(key=lambda x: x.metadata.get('final_score', 0), reverse=True)
        
        return results


class CareerPathAnalyzer:
    """커리어 패스 분석기"""
    
    def __init__(self):
        self.growth_recommender = GrowthPathRecommender()
        self.job_service = JobProfileService()
    
    def analyze_career_path(self, employee: Employee, target_job_id: Optional[str] = None) -> Dict[str, Any]:
        """커리어 패스 분석"""
        current_profile = self._get_employee_profile(employee)
        
        if target_job_id:
            target_job = JobProfile.objects.get(id=target_job_id)
            path_analysis = self._analyze_specific_path(employee, target_job)
        else:
            path_analysis = self._analyze_general_paths(employee)
        
        return {
            'current_profile': current_profile,
            'career_paths': path_analysis,
            'recommendations': self._generate_recommendations(employee, path_analysis),
            'timeline': self._create_career_timeline(employee, path_analysis)
        }
    
    def _get_employee_profile(self, employee: Employee) -> Dict[str, Any]:
        """직원 현재 프로필"""
        return {
            'id': str(employee.id),
            'name': employee.name,
            'position': employee.position,
            'department': employee.department,
            'career_years': getattr(employee, 'career_years', 0),
            'current_skills': [],  # 실제 구현 시 스킬 데이터 연동
            'certifications': []   # 실제 구현 시 자격증 데이터 연동
        }
    
    def _analyze_specific_path(self, employee: Employee, target_job: JobProfile) -> List[Dict[str, Any]]:
        """특정 직무로의 경로 분석"""
        match_result = self.job_service.match_employee_to_job(employee, target_job)
        
        return [{
            'target_job': {
                'id': str(target_job.id),
                'name': target_job.job_role.name,
                'full_path': target_job.job_role.full_path
            },
            'match_score': match_result['match_score'],
            'difficulty': self._determine_difficulty(match_result['match_score']),
            'required_skills': match_result['gaps']['basic_skills'] + match_result['gaps']['applied_skills'],
            'estimated_time': self._estimate_transition_time(match_result['match_score']),
            'intermediate_steps': self._find_intermediate_jobs(employee, target_job)
        }]
    
    def _analyze_general_paths(self, employee: Employee) -> List[Dict[str, Any]]:
        """일반적인 커리어 경로 분석"""
        suitable_jobs = self.job_service.find_suitable_jobs_for_employee(
            employee, min_score=60.0, top_n=10
        )
        
        paths = []
        for job_match in suitable_jobs[:5]:  # 상위 5개
            job_profile = job_match.get('job_profile_object')
            if job_profile:
                paths.append({
                    'target_job': {
                        'id': str(job_profile.id),
                        'name': job_profile.job_role.name,
                        'full_path': job_profile.job_role.full_path
                    },
                    'match_score': job_match['match_score'],
                    'difficulty': self._determine_difficulty(job_match['match_score']),
                    'required_skills': job_match['gaps']['basic_skills'] + job_match['gaps']['applied_skills'],
                    'estimated_time': self._estimate_transition_time(job_match['match_score']),
                    'intermediate_steps': []
                })
        
        return paths
    
    def _determine_difficulty(self, match_score: float) -> str:
        """전환 난이도 결정"""
        if match_score >= 85:
            return "쉬움"
        elif match_score >= 70:
            return "보통"
        elif match_score >= 55:
            return "어려움"
        else:
            return "매우 어려움"
    
    def _estimate_transition_time(self, match_score: float) -> str:
        """전환 예상 시간"""
        if match_score >= 85:
            return "3-6개월"
        elif match_score >= 70:
            return "6-12개월"
        elif match_score >= 55:
            return "1-2년"
        else:
            return "2년 이상"
    
    def _find_intermediate_jobs(self, employee: Employee, target_job: JobProfile) -> List[Dict[str, Any]]:
        """중간 단계 직무 찾기"""
        # 현재 직무와 목표 직무 사이의 중간 단계 직무들
        intermediate = []
        
        # 같은 카테고리 내에서 단계적 직무 찾기
        category_jobs = JobProfile.objects.filter(
            job_role__job_type__category=target_job.job_role.job_type.category,
            is_active=True
        ).exclude(id=target_job.id)
        
        for job in category_jobs[:3]:
            match_result = self.job_service.match_employee_to_job(employee, job)
            
            # 현재보다 매칭 점수가 높고, 목표 직무보다는 낮은 경우
            target_match = self.job_service.match_employee_to_job(employee, target_job)
            
            if match_result['match_score'] > target_match['match_score'] * 0.8:
                intermediate.append({
                    'id': str(job.id),
                    'name': job.job_role.name,
                    'match_score': match_result['match_score'],
                    'step_order': len(intermediate) + 1
                })
        
        return intermediate[:2]  # 최대 2개 중간 단계
    
    def _generate_recommendations(self, employee: Employee, paths: List[Dict[str, Any]]) -> List[str]:
        """추천 사항 생성"""
        recommendations = []
        
        if not paths:
            return ["현재 프로필로는 적합한 커리어 경로를 찾기 어렵습니다. 스킬 개발을 먼저 진행해보세요."]
        
        best_path = paths[0]
        
        if best_path['match_score'] >= 80:
            recommendations.append(f"{best_path['target_job']['name']} 직무로의 즉시 전환을 고려해보세요.")
        else:
            recommendations.append(f"{best_path['target_job']['name']} 직무 전환을 위해 다음 스킬들을 먼저 개발하세요.")
            recommendations.extend(best_path['required_skills'][:3])
        
        # 교육 추천
        recommendations.append("관련 교육 과정 수강을 통한 역량 강화를 추천합니다.")
        
        # 자격증 추천
        recommendations.append("해당 분야 자격증 취득을 통한 전문성 향상을 고려해보세요.")
        
        return recommendations[:5]
    
    def _create_career_timeline(self, employee: Employee, paths: List[Dict[str, Any]]) -> Dict[str, Any]:
        """커리어 타임라인 생성"""
        if not paths:
            return {}
        
        best_path = paths[0]
        
        timeline = {
            'current': {
                'position': employee.position,
                'department': employee.department,
                'date': datetime.now().strftime('%Y-%m')
            },
            'milestones': []
        }
        
        # 중간 단계들
        for i, step in enumerate(best_path.get('intermediate_steps', [])):
            timeline['milestones'].append({
                'step': i + 1,
                'target': step['name'],
                'estimated_date': (datetime.now() + timedelta(days=180 * (i + 1))).strftime('%Y-%m'),
                'key_activities': ['스킬 개발', '실무 경험', '네트워킹']
            })
        
        # 최종 목표
        final_months = 12 if best_path['match_score'] >= 70 else 24
        timeline['milestones'].append({
            'step': len(best_path.get('intermediate_steps', [])) + 1,
            'target': best_path['target_job']['name'],
            'estimated_date': (datetime.now() + timedelta(days=30 * final_months)).strftime('%Y-%m'),
            'key_activities': ['최종 전환', '역할 적응', '성과 창출']
        })
        
        return timeline


class JobSearchChatbotIntegration:
    """직무 검색 챗봇 통합"""
    
    def __init__(self):
        self.search_engine = JobSearchEngine()
        self.career_analyzer = CareerPathAnalyzer()
        self.cert_service = CertificationService()
        
    def process_chat_query(self, user_query: str, user_id: str, session_id: str) -> Dict[str, Any]:
        """채팅 쿼리 처리"""
        # 의도 분석
        intent = self._analyze_intent(user_query)
        
        # 컨텍스트 생성
        context = SearchContext(
            user_id=user_id,
            session_id=session_id,
            intent=intent,
            query=user_query,
            history=self._get_search_history(user_id)
        )
        
        # 의도별 처리
        if intent == SearchIntent.JOB_SEARCH:
            return self._handle_job_search(context)
        elif intent == SearchIntent.CAREER_PATH:
            return self._handle_career_path(context)
        elif intent == SearchIntent.SKILL_MATCH:
            return self._handle_skill_match(context)
        elif intent == SearchIntent.CERTIFICATION:
            return self._handle_certification(context)
        else:
            return self._handle_general_inquiry(context)
    
    def _analyze_intent(self, query: str) -> SearchIntent:
        """쿼리 의도 분석"""
        query_lower = query.lower()
        
        # 키워드 기반 의도 분류
        if any(word in query_lower for word in ['직무', '직업', '일자리', 'job', '포지션']):
            return SearchIntent.JOB_SEARCH
        elif any(word in query_lower for word in ['커리어', '경력', '승진', 'career', '경로']):
            return SearchIntent.CAREER_PATH
        elif any(word in query_lower for word in ['스킬', '기술', '역량', 'skill', '능력']):
            return SearchIntent.SKILL_MATCH
        elif any(word in query_lower for word in ['자격증', '인증', 'certification', '자격']):
            return SearchIntent.CERTIFICATION
        elif any(word in query_lower for word in ['급여', '연봉', 'salary', '임금']):
            return SearchIntent.SALARY_INQUIRY
        else:
            return SearchIntent.JOB_SEARCH  # 기본값
    
    def _handle_job_search(self, context: SearchContext) -> Dict[str, Any]:
        """직무 검색 처리"""
        results = self.search_engine.search_jobs(context)
        
        # 챗봇 형식 응답
        if not results:
            return {
                'intent': 'job_search',
                'response_type': 'no_results',
                'message': f"'{context.query}'에 대한 검색 결과를 찾을 수 없습니다. 다른 키워드로 검색해보시겠어요?",
                'suggestions': [
                    "개발자 직무 검색",
                    "마케팅 관련 직무",
                    "인사 업무 직무",
                    "전체 직무 목록 보기"
                ]
            }
        
        # 상위 3개 결과를 대화형으로 제시
        top_results = results[:3]
        
        message = f"'{context.query}' 검색 결과 {len(results)}개 중 상위 3개를 보여드릴게요:\n\n"
        
        cards = []
        for i, result in enumerate(top_results, 1):
            message += f"{i}. **{result.job_name}** ({result.category})\n"
            message += f"   매칭도: {result.match_score:.1f}% | {result.career_level} 레벨\n"
            message += f"   주요 스킬: {', '.join(result.skills_required[:3])}\n\n"
            
            cards.append({
                'job_id': result.job_id,
                'title': result.job_name,
                'subtitle': f"{result.category} > {result.type_name}",
                'match_score': result.match_score,
                'skills': result.skills_required[:5],
                'requirements': result.requirements[:3]
            })
        
        return {
            'intent': 'job_search',
            'response_type': 'job_list',
            'message': message,
            'cards': cards,
            'total_count': len(results),
            'suggestions': [
                f"{top_results[0].job_name} 자세히 보기",
                "관련 직무 더 보기",
                "커리어 경로 분석",
                "필요 스킬 확인"
            ],
            'quick_actions': [
                {'label': '자세히 보기', 'action': 'view_detail', 'job_id': top_results[0].job_id},
                {'label': '커리어 분석', 'action': 'analyze_career', 'job_id': top_results[0].job_id},
                {'label': '더 많은 결과', 'action': 'show_more', 'query': context.query}
            ]
        }
    
    def _handle_career_path(self, context: SearchContext) -> Dict[str, Any]:
        """커리어 경로 처리"""
        try:
            employee = Employee.objects.get(user_id=context.user_id)
            analysis = self.career_analyzer.analyze_career_path(employee)
            
            if not analysis['career_paths']:
                return {
                    'intent': 'career_path',
                    'response_type': 'no_path',
                    'message': "현재 프로필로는 명확한 커리어 경로를 찾기 어려워요. 먼저 스킬 개발이나 경험 축적을 통해 프로필을 강화해보시는 것을 추천드립니다.",
                    'suggestions': [
                        "스킬 개발 계획 세우기",
                        "교육 과정 추천 받기",
                        "자격증 정보 확인",
                        "멘토링 프로그램 신청"
                    ]
                }
            
            best_path = analysis['career_paths'][0]
            
            message = f"**{employee.name}님의 커리어 분석 결과**\n\n"
            message += f"🎯 **추천 직무**: {best_path['target_job']['name']}\n"
            message += f"📊 **적합도**: {best_path['match_score']:.1f}%\n"
            message += f"⏱️ **예상 기간**: {best_path['estimated_time']}\n"
            message += f"📈 **난이도**: {best_path['difficulty']}\n\n"
            
            if best_path['required_skills']:
                message += f"**개발 필요 스킬**:\n"
                for skill in best_path['required_skills'][:5]:
                    message += f"• {skill}\n"
            
            return {
                'intent': 'career_path',
                'response_type': 'career_analysis',
                'message': message,
                'career_path': best_path,
                'timeline': analysis['timeline'],
                'recommendations': analysis['recommendations'],
                'suggestions': [
                    "스킬 개발 계획 세우기",
                    "관련 교육 과정 찾기",
                    "멘토 연결 요청",
                    "진행 상황 추적 설정"
                ]
            }
            
        except Employee.DoesNotExist:
            return {
                'intent': 'career_path',
                'response_type': 'error',
                'message': "직원 정보를 찾을 수 없어요. 로그인 상태를 확인해주세요."
            }
    
    def _get_search_history(self, user_id: str) -> List[Dict[str, Any]]:
        """검색 이력 조회"""
        cache_key = f"search_history:{user_id}"
        return cache.get(cache_key, [])
    
    def _handle_skill_match(self, context: SearchContext) -> Dict[str, Any]:
        """스킬 매칭 처리"""
        # 스킬 기반 직무 검색
        context.filters['skills'] = context.query.split()
        results = self.search_engine.search_jobs(context)
        
        if not results:
            return {
                'intent': 'skill_match',
                'response_type': 'no_match',
                'message': f"'{context.query}' 스킬과 매칭되는 직무를 찾을 수 없어요. 다른 스킬로 검색해보시거나 관련 직무를 추천받아보세요.",
                'suggestions': [
                    "Python 개발 직무",
                    "프로젝트 관리 직무", 
                    "디자인 관련 직무",
                    "전체 직무 둘러보기"
                ]
            }
        
        top_result = results[0]
        
        message = f"**'{context.query}' 스킬 매칭 결과**\n\n"
        message += f"🏆 **최고 매칭 직무**: {top_result.job_name}\n"
        message += f"📊 **매칭도**: {top_result.match_score:.1f}%\n"
        message += f"🏢 **분야**: {top_result.category}\n\n"
        
        message += f"**요구 스킬**:\n"
        for skill in top_result.skills_required[:5]:
            message += f"• {skill}\n"
        
        return {
            'intent': 'skill_match',
            'response_type': 'skill_match_result',
            'message': message,
            'matched_jobs': [
                {
                    'job_id': r.job_id,
                    'name': r.job_name,
                    'match_score': r.match_score,
                    'category': r.category
                }
                for r in results[:5]
            ],
            'suggestions': [
                f"{top_result.job_name} 상세 정보",
                "스킬 개발 계획",
                "관련 교육 과정",
                "다른 스킬로 검색"
            ]
        }
    
    def _handle_certification(self, context: SearchContext) -> Dict[str, Any]:
        """자격증 정보 처리"""
        try:
            employee = Employee.objects.get(user_id=context.user_id)
            
            # 자격증 관련 직무 검색
            cert_jobs = self.search_engine.search_jobs(context)
            
            message = f"**'{context.query}' 자격증 관련 정보**\n\n"
            
            if cert_jobs:
                message += f"관련 직무 {len(cert_jobs)}개를 찾았어요:\n\n"
                for job in cert_jobs[:3]:
                    message += f"• **{job.job_name}** ({job.category})\n"
                    if job.certifications:
                        message += f"  관련 자격증: {', '.join(job.certifications[:2])}\n"
                    message += "\n"
            
            # 성장레벨 인증 체크
            try:
                cert_check = self.cert_service.check_growth_level_certification(
                    employee=employee,
                    target_level='Lv.3'  # 기본 레벨
                )
                
                message += f"**성장레벨 인증 현황**:\n"
                message += f"• 현재 레벨: {cert_check['details']['current_level']}\n"
                message += f"• 인증 상태: {cert_check['certification_result']}\n"
                
            except Exception as e:
                logger.error(f"Certification check error: {e}")
            
            return {
                'intent': 'certification',
                'response_type': 'certification_info',
                'message': message,
                'related_jobs': [
                    {
                        'job_id': job.job_id,
                        'name': job.job_name,
                        'certifications': job.certifications
                    }
                    for job in cert_jobs[:5]
                ],
                'suggestions': [
                    "인증 요건 확인",
                    "필요 교육 과정",
                    "인증 신청 방법",
                    "관련 직무 탐색"
                ]
            }
            
        except Employee.DoesNotExist:
            return {
                'intent': 'certification',
                'response_type': 'error',
                'message': "직원 정보를 찾을 수 없어요."
            }
    
    def _handle_general_inquiry(self, context: SearchContext) -> Dict[str, Any]:
        """일반 문의 처리"""
        return {
            'intent': 'general',
            'response_type': 'help',
            'message': "안녕하세요! 직무 검색 도우미입니다. 다음과 같은 도움을 드릴 수 있어요:\n\n• 직무 검색 및 추천\n• 커리어 경로 분석\n• 스킬 매칭\n• 자격증 정보\n• 성장 계획 수립\n\n궁금한 것이 있으시면 언제든 말씀해주세요!",
            'suggestions': [
                "직무 검색하기",
                "커리어 분석 받기",
                "스킬 체크하기",
                "인증 현황 확인"
            ]
        }


# API Views

@method_decorator(login_required, name='dispatch')
class JobSearchAPI(View):
    """직무 검색 API"""
    
    def __init__(self):
        super().__init__()
        self.search_engine = JobSearchEngine()
    
    def get(self, request):
        """
        GET /api/job-search/
        
        Parameters:
            - q: 검색 쿼리
            - category: 직군 필터
            - job_type: 직종 필터  
            - skills: 스킬 필터 (쉼표 구분)
            - limit: 결과 개수 (기본 10)
        """
        try:
            # 파라미터 파싱
            query = request.GET.get('q', '')
            category = request.GET.get('category', '')
            job_type = request.GET.get('job_type', '')
            skills_param = request.GET.get('skills', '')
            limit = int(request.GET.get('limit', 10))
            
            # 필터 구성
            filters = {}
            if category:
                filters['category'] = category
            if job_type:
                filters['job_type'] = job_type
            if skills_param:
                filters['skills'] = [s.strip() for s in skills_param.split(',')]
            
            # 검색 컨텍스트 생성
            context = SearchContext(
                user_id=str(request.user.id),
                session_id=request.session.session_key or str(uuid.uuid4()),
                intent=SearchIntent.JOB_SEARCH,
                query=query,
                filters=filters
            )
            
            # 검색 실행
            results = self.search_engine.search_jobs(context)
            
            # 결과 제한
            limited_results = results[:limit]
            
            # 응답 데이터 구성
            response_data = {
                'status': 'success',
                'query': query,
                'total_count': len(results),
                'returned_count': len(limited_results),
                'results': [
                    {
                        'job_id': r.job_id,
                        'job_name': r.job_name,
                        'job_code': r.job_code,
                        'category': r.category,
                        'type_name': r.type_name,
                        'match_score': round(r.match_score, 1),
                        'relevance_score': round(r.relevance_score, 1),
                        'career_level': r.career_level,
                        'skills_required': r.skills_required,
                        'requirements': r.requirements,
                        'certifications': r.certifications,
                        'similar_jobs': r.similar_jobs,
                        'metadata': r.metadata
                    }
                    for r in limited_results
                ]
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Job search API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '검색 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class CareerPathAPI(View):
    """커리어 패스 분석 API"""
    
    def __init__(self):
        super().__init__()
        self.career_analyzer = CareerPathAnalyzer()
    
    def get(self, request):
        """
        GET /api/career-path/
        
        Parameters:
            - target_job_id: 목표 직무 ID (선택사항)
            - employee_id: 직원 ID (HR 권한 필요, 없으면 본인)
        """
        try:
            # 직원 확인
            employee_id = request.GET.get('employee_id')
            
            if employee_id:
                # HR 권한 체크
                if not request.user.groups.filter(name='HR').exists() and not request.user.is_superuser:
                    return JsonResponse({
                        'status': 'error',
                        'message': '권한이 없습니다.'
                    }, status=403)
                
                employee = Employee.objects.get(id=employee_id)
            else:
                employee = Employee.objects.get(user=request.user)
            
            target_job_id = request.GET.get('target_job_id')
            
            # 분석 실행
            analysis = self.career_analyzer.analyze_career_path(
                employee=employee,
                target_job_id=target_job_id
            )
            
            return JsonResponse({
                'status': 'success',
                'employee_profile': analysis['current_profile'],
                'career_paths': analysis['career_paths'],
                'recommendations': analysis['recommendations'],
                'timeline': analysis['timeline']
            })
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '직원 정보를 찾을 수 없습니다.'
            }, status=404)
            
        except Exception as e:
            logger.error(f"Career path API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '커리어 분석 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class JobSearchChatAPI(View):
    """직무 검색 챗봇 API"""
    
    def __init__(self):
        super().__init__()
        self.chatbot = JobSearchChatbotIntegration()
    
    def post(self, request):
        """
        POST /api/job-search-chat/
        
        Request Body:
        {
            "message": "개발자 직무 찾아줘",
            "session_id": "session_uuid"
        }
        """
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id', str(uuid.uuid4()))
            
            if not message:
                return JsonResponse({
                    'status': 'error',
                    'message': '메시지를 입력해주세요.'
                }, status=400)
            
            # 챗봇 처리
            response = self.chatbot.process_chat_query(
                user_query=message,
                user_id=str(request.user.id),
                session_id=session_id
            )
            
            # 검색 이력 저장
            self._save_search_history(request.user.id, message, response, session_id)
            
            return JsonResponse({
                'status': 'success',
                'session_id': session_id,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '잘못된 요청 형식입니다.'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Job search chat API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '채팅 처리 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)
    
    def _save_search_history(self, user_id: int, query: str, response: Dict[str, Any], session_id: str):
        """검색 이력 저장"""
        try:
            cache_key = f"search_history:{user_id}"
            history = cache.get(cache_key, [])
            
            history.append({
                'query': query,
                'intent': response.get('intent'),
                'response_type': response.get('response_type'),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # 최근 20개만 보관
            if len(history) > 20:
                history = history[-20:]
            
            cache.set(cache_key, history, 86400)  # 24시간
            
        except Exception as e:
            logger.error(f"Search history save error: {str(e)}")


@method_decorator(login_required, name='dispatch')
class JobRecommendationAPI(View):
    """직무 추천 API"""
    
    def __init__(self):
        super().__init__()
        self.job_service = JobProfileService()
    
    def get(self, request):
        """
        GET /api/job-recommendations/
        
        Parameters:
            - employee_id: 직원 ID (없으면 본인)
            - min_score: 최소 매칭 점수 (기본 60)
            - limit: 결과 개수 (기본 5)
            - include_similar: 유사 직무 포함 여부 (기본 true)
        """
        try:
            # 직원 확인
            employee_id = request.GET.get('employee_id')
            
            if employee_id:
                if not request.user.groups.filter(name='HR').exists() and not request.user.is_superuser:
                    return JsonResponse({
                        'status': 'error',
                        'message': '권한이 없습니다.'
                    }, status=403)
                
                employee = Employee.objects.get(id=employee_id)
            else:
                employee = Employee.objects.get(user=request.user)
            
            # 파라미터
            min_score = float(request.GET.get('min_score', 60.0))
            limit = int(request.GET.get('limit', 5))
            include_similar = request.GET.get('include_similar', 'true').lower() == 'true'
            
            # 추천 직무 조회
            recommendations = self.job_service.find_suitable_jobs_for_employee(
                employee=employee,
                min_score=min_score,
                top_n=limit * 2 if include_similar else limit
            )
            
            # 결과 구성
            results = []
            for rec in recommendations[:limit]:
                job_profile = rec.get('job_profile_object')
                if job_profile:
                    result = {
                        'job_id': str(job_profile.id),
                        'job_name': job_profile.job_role.name,
                        'job_code': job_profile.job_role.code,
                        'full_path': job_profile.job_role.full_path,
                        'category': job_profile.job_role.job_type.category.name,
                        'type_name': job_profile.job_role.job_type.name,
                        'match_score': round(rec['match_score'], 1),
                        'skills_required': job_profile.get_all_skills(),
                        'missing_skills': rec['gaps']['basic_skills'] + rec['gaps']['applied_skills'],
                        'requirements': job_profile.qualification.split('\n')[:3] if job_profile.qualification else [],
                        'growth_path': job_profile.growth_path,
                        'certifications': job_profile.related_certifications,
                        'readiness_level': self._determine_readiness(rec['match_score'])
                    }
                    
                    # 유사 직무 추가
                    if include_similar:
                        similar_jobs = JobProfile.objects.filter(
                            job_role__job_type=job_profile.job_role.job_type,
                            is_active=True
                        ).exclude(id=job_profile.id)[:3]
                        
                        result['similar_jobs'] = [
                            {
                                'id': str(s.id),
                                'name': s.job_role.name,
                                'code': s.job_role.code
                            }
                            for s in similar_jobs
                        ]
                    
                    results.append(result)
            
            return JsonResponse({
                'status': 'success',
                'employee': {
                    'id': str(employee.id),
                    'name': employee.name,
                    'position': employee.position,
                    'department': employee.department
                },
                'recommendations': results,
                'total_count': len(recommendations),
                'criteria': {
                    'min_score': min_score,
                    'include_similar': include_similar
                }
            })
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '직원 정보를 찾을 수 없습니다.'
            }, status=404)
            
        except Exception as e:
            logger.error(f"Job recommendation API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '추천 조회 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)
    
    def _determine_readiness(self, match_score: float) -> str:
        """준비도 레벨 결정"""
        if match_score >= 85:
            return "즉시 지원 가능"
        elif match_score >= 70:
            return "단기 준비 필요"
        elif match_score >= 60:
            return "중기 준비 필요"
        else:
            return "장기 준비 필요"


# URL 패턴 정의
"""
Django urls.py에 추가할 URL 패턴:

from django.urls import path
from .job_search_recommend_api import (
    JobSearchAPI,
    CareerPathAPI, 
    JobSearchChatAPI,
    JobRecommendationAPI
)

urlpatterns = [
    # 직무 검색
    path('api/job-search/', JobSearchAPI.as_view(), name='job_search_api'),
    
    # 커리어 패스 분석
    path('api/career-path/', CareerPathAPI.as_view(), name='career_path_api'),
    
    # 직무 검색 챗봇
    path('api/job-search-chat/', JobSearchChatAPI.as_view(), name='job_search_chat_api'),
    
    # 직무 추천
    path('api/job-recommendations/', JobRecommendationAPI.as_view(), name='job_recommendation_api'),
]
"""

if __name__ == "__main__":
    print("Job Search & Recommendation API with Chatbot Integration")
    print("=" * 60)
    print("Features:")
    print("✓ Field-based search (fieldsearch)")
    print("✓ Related jobs recommendation (relatedjobs)")
    print("✓ Career path analysis (careerpath)")
    print("✓ Instant response (instantresponse)")
    print("✓ Context-aware responses (contextaware)")
    print("✓ Chatbot integration")
    print("✓ Caching and optimization")
    print("✓ Multi-format API responses")