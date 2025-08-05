"""
ESS 개인별 리더 성장 상태 API
직원이 자신의 리더십 성장 가능성과 추천 상태를 확인할 수 있는 API
"""

from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.core.cache import cache
import json
import logging

from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from .models import JobProfile, JobRole
from .leader_services import LeaderRecommendationService
from .growth_services import GrowthPathService
from .report_services import LeaderReportService
from .recommendation_comment_generator import generate_recommendation_comment

logger = logging.getLogger(__name__)


class MyLeaderGrowthStatusAPI(View):
    """개인 리더 성장 상태 API"""
    
    @method_decorator(login_required)
    def get(self, request):
        """
        GET /api/my-leader-growth-status/
        
        Returns:
            {
                "employee_info": {...},
                "leadership_recommendations": [...],
                "growth_paths": [...],
                "development_needs": {...}
            }
        """
        try:
            # 현재 로그인한 직원 정보
            employee = Employee.objects.get(user=request.user)
            
            # 캐시 키
            cache_key = f"leader_growth_status_{employee.id}"
            cached_data = cache.get(cache_key)
            
            if cached_data and not request.GET.get('refresh'):
                return JsonResponse(cached_data)
            
            # 서비스 초기화
            leader_service = LeaderRecommendationService()
            growth_service = GrowthPathService()
            
            # 1. 직원 기본 정보
            employee_info = self._get_employee_info(employee)
            
            # 2. 리더십 추천 상태
            leadership_recommendations = self._get_leadership_recommendations(
                employee, leader_service
            )
            
            # 3. 성장 경로 분석
            growth_paths = self._get_growth_paths(employee, growth_service)
            
            # 4. 개발 필요 영역
            development_needs = self._analyze_development_needs(
                employee, leadership_recommendations
            )
            
            response_data = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "employee_info": employee_info,
                "leadership_recommendations": leadership_recommendations,
                "growth_paths": growth_paths,
                "development_needs": development_needs,
                "report_available": self._check_report_availability(employee)
            }
            
            # 캐시 저장 (1시간)
            cache.set(cache_key, response_data, 3600)
            
            return JsonResponse(response_data)
            
        except Employee.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "직원 정보를 찾을 수 없습니다."
            }, status=404)
            
        except Exception as e:
            logger.error(f"Error in MyLeaderGrowthStatusAPI: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": "서버 오류가 발생했습니다."
            }, status=500)
    
    def _get_employee_info(self, employee: Employee) -> dict:
        """직원 기본 정보 조회"""
        # 최신 평가 정보
        latest_eval = ComprehensiveEvaluation.objects.filter(
            employee=employee
        ).order_by('-created_at').first()
        
        # 성장 레벨 추정
        growth_level = self._estimate_growth_level(employee)
        
        return {
            "employee_id": str(employee.id),
            "name": employee.name,
            "current_position": employee.position,
            "department": employee.department,
            "career_years": self._calculate_career_years(employee),
            "growth_level": growth_level,
            "recent_evaluation": {
                "overall_grade": latest_eval.final_grade if latest_eval else "N/A",
                "evaluation_date": latest_eval.created_at.isoformat() if latest_eval else None
            }
        }
    
    def _get_leadership_recommendations(
        self, 
        employee: Employee, 
        leader_service: LeaderRecommendationService
    ) -> List[dict]:
        """리더십 추천 상태 조회"""
        recommendations = []
        
        # 관련 리더 직무 찾기 (같은 부서 또는 인접 분야)
        potential_leader_roles = JobProfile.objects.filter(
            is_active=True,
            job_role__name__icontains='장'  # 팀장, 파트장 등
        ).select_related('job_role')[:5]
        
        for job_profile in potential_leader_roles:
            # 적합도 평가
            candidates = leader_service.find_leader_candidates(
                target_job_profile=job_profile,
                department=employee.department,
                top_n=20  # 더 많이 조회해서 현재 직원 포함 확인
            )
            
            # 현재 직원이 후보에 포함되는지 확인
            my_candidate = next(
                (c for c in candidates if str(c['employee_id']) == str(employee.id)),
                None
            )
            
            if my_candidate:
                # 자연어 추천 코멘트 생성
                recommendation_comment = my_candidate.get('recommendation_reason', '')
                
                recommendations.append({
                    "job_id": str(job_profile.id),
                    "job_name": job_profile.job_role.name,
                    "match_score": my_candidate['match_score'],
                    "skill_match_rate": my_candidate['skill_match_rate'],
                    "matched_skills": my_candidate['matched_skills'],
                    "missing_skills": my_candidate['missing_skills'],
                    "recommendation_comment": recommendation_comment,
                    "promotion_ready": my_candidate['match_score'] >= 80,
                    "rank_among_candidates": candidates.index(my_candidate) + 1,
                    "total_candidates": len(candidates)
                })
        
        # 점수 순으로 정렬
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:3]  # 상위 3개만 반환
    
    def _get_growth_paths(
        self, 
        employee: Employee, 
        growth_service: GrowthPathService
    ) -> List[dict]:
        """성장 경로 분석"""
        # 추천된 리더 직무에 대한 성장 경로
        growth_paths_data = []
        
        # 주요 리더 직무
        target_jobs = JobProfile.objects.filter(
            is_active=True,
            job_role__name__icontains='장'
        )[:3]
        
        for target_job in target_jobs:
            growth_paths = growth_service.get_employee_growth_paths(
                employee=employee,
                target_job_ids=[str(target_job.id)],
                include_evaluation=True,
                top_n=1
            )
            
            if growth_paths:
                path = growth_paths[0]
                growth_path = path['growth_path']
                
                # 단계별 정보 간소화
                stages = []
                for stage in growth_path.stages:
                    stages.append({
                        "job_name": stage.job_name,
                        "expected_years": stage.expected_years,
                        "required_skills": stage.required_skills[:3]  # 상위 3개만
                    })
                
                growth_paths_data.append({
                    "target_job": target_job.job_role.name,
                    "total_years": growth_path.total_years,
                    "difficulty_score": growth_path.difficulty_score,
                    "success_probability": growth_path.success_probability,
                    "stages": stages
                })
        
        return growth_paths_data
    
    def _analyze_development_needs(
        self, 
        employee: Employee,
        recommendations: List[dict]
    ) -> dict:
        """개발 필요 영역 분석"""
        # 모든 추천 직무에서 부족한 스킬 수집
        all_missing_skills = []
        for rec in recommendations:
            all_missing_skills.extend(rec.get('missing_skills', []))
        
        # 빈도 계산
        skill_frequency = {}
        for skill in all_missing_skills:
            skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        # 우선순위 스킬
        priority_skills = sorted(
            skill_frequency.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # 개발 추천
        development_recommendations = []
        for skill, freq in priority_skills:
            if freq >= 2:  # 2개 이상 직무에서 필요
                priority = "높음"
            else:
                priority = "보통"
            
            development_recommendations.append({
                "skill": skill,
                "priority": priority,
                "required_by_jobs": freq,
                "suggested_actions": self._suggest_development_actions(skill)
            })
        
        return {
            "priority_skills": [skill for skill, _ in priority_skills],
            "development_recommendations": development_recommendations,
            "estimated_preparation_time": self._estimate_preparation_time(priority_skills)
        }
    
    def _suggest_development_actions(self, skill: str) -> List[str]:
        """스킬별 개발 액션 제안"""
        skill_actions = {
            "리더십": ["리더십 아카데미 수료", "팀 프로젝트 리딩", "멘토링 프로그램"],
            "성과관리": ["성과관리 교육", "KPI 설정 워크샵", "평가자 교육"],
            "전략기획": ["전략기획 과정", "사업계획 수립 참여", "전략 사례 연구"],
            "조직운영": ["조직관리 교육", "팀빌딩 활동 주도", "HR 기초 과정"],
            "예산관리": ["재무관리 기초", "예산편성 실무", "원가관리 교육"],
            "의사결정": ["의사결정 프로세스 교육", "케이스 스터디", "시뮬레이션"],
            "커뮤니케이션": ["프레젠테이션 스킬", "협상 기법", "갈등관리"],
            "변화관리": ["변화관리 프로세스", "조직문화 이해", "혁신 워크샵"]
        }
        
        # 기본 액션
        default_actions = ["관련 교육 수강", "실무 프로젝트 참여", "멘토링 받기"]
        
        # 스킬 매칭
        for key, actions in skill_actions.items():
            if key in skill:
                return actions
        
        return default_actions
    
    def _estimate_preparation_time(self, priority_skills: List[tuple]) -> str:
        """준비 기간 추정"""
        skill_count = len(priority_skills)
        
        if skill_count <= 2:
            return "6개월 이내"
        elif skill_count <= 4:
            return "6-12개월"
        else:
            return "12-18개월"
    
    def _estimate_growth_level(self, employee: Employee) -> str:
        """성장 레벨 추정"""
        position = employee.position
        
        if 'STAFF' in position or '사원' in position:
            return 'Lv.1'
        elif 'SENIOR' in position or '대리' in position:
            return 'Lv.2'
        elif 'MANAGER' in position or '과장' in position:
            return 'Lv.3'
        elif 'DIRECTOR' in position or '차장' in position or '부장' in position:
            return 'Lv.4'
        elif 'EXECUTIVE' in position or '임원' in position:
            return 'Lv.5'
        
        return 'Lv.2'
    
    def _calculate_career_years(self, employee: Employee) -> int:
        """경력 년수 계산"""
        if employee.employment_date:
            years = (datetime.now().date() - employee.employment_date).days / 365
            return int(years)
        return 0
    
    def _check_report_availability(self, employee: Employee) -> bool:
        """리포트 생성 가능 여부"""
        # 평가 등급 확인
        latest_eval = ComprehensiveEvaluation.objects.filter(
            employee=employee
        ).order_by('-created_at').first()
        
        if not latest_eval:
            return False
        
        # B+ 이상이고 Lv.3 이상인 경우
        grade_ok = latest_eval.final_grade in ['S', 'A+', 'A', 'B+']
        level_ok = self._estimate_growth_level(employee) >= 'Lv.3'
        
        return grade_ok and level_ok


class MyLeaderReportAPI(View):
    """개인 리더십 리포트 API"""
    
    @method_decorator(login_required)
    def get(self, request, format='json'):
        """
        GET /api/my-leader-report/
        GET /api/my-leader-report/pdf/
        
        Query Parameters:
            - job_id: 특정 직무에 대한 리포트 (optional)
        """
        try:
            employee = Employee.objects.get(user=request.user)
            
            # PDF 요청인 경우
            if format == 'pdf':
                return self._generate_pdf_report(request, employee)
            
            # JSON 리포트 데이터
            return self._get_report_data(request, employee)
            
        except Employee.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "직원 정보를 찾을 수 없습니다."
            }, status=404)
            
        except Exception as e:
            logger.error(f"Error in MyLeaderReportAPI: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": "리포트 생성 중 오류가 발생했습니다."
            }, status=500)
    
    def _get_report_data(self, request, employee: Employee) -> JsonResponse:
        """리포트 데이터 조회"""
        job_id = request.GET.get('job_id')
        
        # 대상 직무 결정
        if job_id:
            try:
                target_job = JobProfile.objects.get(id=job_id)
            except JobProfile.DoesNotExist:
                return JsonResponse({
                    "status": "error",
                    "message": "직무를 찾을 수 없습니다."
                }, status=404)
        else:
            # 가장 적합한 직무 자동 선택
            leader_service = LeaderRecommendationService()
            potential_jobs = JobProfile.objects.filter(
                is_active=True,
                job_role__name__icontains='장'
            )[:10]
            
            best_match = None
            best_score = 0
            
            for job in potential_jobs:
                candidates = leader_service.find_leader_candidates(
                    target_job_profile=job,
                    department=employee.department,
                    top_n=20
                )
                
                my_candidate = next(
                    (c for c in candidates if str(c['employee_id']) == str(employee.id)),
                    None
                )
                
                if my_candidate and my_candidate['match_score'] > best_score:
                    best_score = my_candidate['match_score']
                    best_match = job
            
            if not best_match:
                return JsonResponse({
                    "status": "error",
                    "message": "적합한 리더 직무를 찾을 수 없습니다."
                }, status=404)
            
            target_job = best_match
        
        # 리포트 데이터 생성
        report_service = LeaderReportService()
        
        # 후보자 평가
        candidate_data = report_service._evaluate_single_candidate(
            employee, target_job
        )
        
        # 평가 이력
        evaluation_history = report_service._get_evaluation_history(employee)
        
        # 성장 경로
        growth_service = GrowthPathService()
        growth_paths = growth_service.get_employee_growth_paths(
            employee=employee,
            target_job_ids=[str(target_job.id)],
            include_evaluation=True,
            top_n=1
        )
        
        growth_path_data = None
        if growth_paths:
            gp = growth_paths[0]['growth_path']
            growth_path_data = {
                "total_years": gp.total_years,
                "success_probability": gp.success_probability,
                "stages": [
                    {
                        "job_name": stage.job_name,
                        "expected_years": stage.expected_years,
                        "required_skills": stage.required_skills
                    }
                    for stage in gp.stages
                ]
            }
        
        return JsonResponse({
            "status": "success",
            "report_data": {
                "employee": {
                    "name": employee.name,
                    "position": employee.position,
                    "department": employee.department
                },
                "target_job": {
                    "id": str(target_job.id),
                    "name": target_job.job_role.name
                },
                "assessment": {
                    "match_score": candidate_data['match_score'],
                    "skill_match_rate": candidate_data['skill_match_rate'],
                    "recommendation_comment": candidate_data['recommendation_reason'],
                    "matched_skills": candidate_data['matched_skills'],
                    "missing_skills": candidate_data['missing_skills']
                },
                "evaluation_history": evaluation_history[:5],
                "growth_path": growth_path_data,
                "pdf_available": True
            }
        })
    
    def _generate_pdf_report(self, request, employee: Employee) -> HttpResponse:
        """PDF 리포트 생성 및 다운로드"""
        job_id = request.GET.get('job_id')
        
        # 대상 직무
        if job_id:
            try:
                target_job = JobProfile.objects.get(id=job_id)
            except JobProfile.DoesNotExist:
                return HttpResponse("직무를 찾을 수 없습니다.", status=404)
        else:
            # 기본 직무 선택 로직
            target_job = JobProfile.objects.filter(
                is_active=True,
                job_role__name__icontains='장'
            ).first()
            
            if not target_job:
                return HttpResponse("적합한 직무를 찾을 수 없습니다.", status=404)
        
        # PDF 생성
        report_service = LeaderReportService()
        result = report_service.generate_candidate_report(
            employee_id=employee.id,
            target_job_profile_id=target_job.id,
            include_growth_path=True,
            include_evaluation_history=True,
            save_to_db=True
        )
        
        if result['success']:
            # PDF 다운로드 응답
            return report_service.get_report_download_response(
                result['report_path'],
                as_attachment=True
            )
        else:
            return HttpResponse(
                f"리포트 생성 실패: {result.get('error', 'Unknown error')}", 
                status=500
            )


def get_my_leader_recommendation_summary(employee_id: int) -> dict:
    """
    직원의 리더 추천 요약 정보 조회 (다른 서비스에서 사용)
    
    Args:
        employee_id: 직원 ID
        
    Returns:
        요약 정보 딕셔너리
    """
    try:
        employee = Employee.objects.get(id=employee_id)
        
        # 최신 평가
        latest_eval = ComprehensiveEvaluation.objects.filter(
            employee=employee
        ).order_by('-created_at').first()
        
        # 가장 적합한 리더 직무 찾기
        leader_service = LeaderRecommendationService()
        best_match = None
        best_score = 0
        
        potential_jobs = JobProfile.objects.filter(
            is_active=True,
            job_role__name__icontains='장'
        )[:5]
        
        for job in potential_jobs:
            candidates = leader_service.find_leader_candidates(
                target_job_profile=job,
                department=employee.department,
                top_n=20
            )
            
            my_candidate = next(
                (c for c in candidates if str(c['employee_id']) == str(employee.id)),
                None
            )
            
            if my_candidate and my_candidate['match_score'] > best_score:
                best_score = my_candidate['match_score']
                best_match = {
                    'job': job,
                    'score': my_candidate['match_score'],
                    'comment': my_candidate['recommendation_reason']
                }
        
        return {
            'has_recommendation': best_match is not None,
            'best_match_job': best_match['job'].job_role.name if best_match else None,
            'match_score': best_match['score'] if best_match else 0,
            'recommendation_comment': best_match['comment'] if best_match else None,
            'evaluation_grade': latest_eval.final_grade if latest_eval else 'N/A',
            'is_ready': best_match and best_match['score'] >= 80
        }
        
    except Exception as e:
        logger.error(f"Error getting leader recommendation summary: {str(e)}")
        return {
            'has_recommendation': False,
            'error': str(e)
        }


# URL 패턴
"""
urlpatterns = [
    path('api/my-leader-growth-status/', MyLeaderGrowthStatusAPI.as_view(), name='my_leader_growth_status'),
    path('api/my-leader-report/', MyLeaderReportAPI.as_view(), {'format': 'json'}, name='my_leader_report'),
    path('api/my-leader-report/pdf/', MyLeaderReportAPI.as_view(), {'format': 'pdf'}, name='my_leader_report_pdf'),
]
"""