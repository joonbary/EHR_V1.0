"""
교육 추천 Django 서비스
교육 추천 엔진과 Django 모델을 연결하는 서비스 레이어
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg, F, Prefetch
from django.contrib.auth.models import User
from django.core.cache import cache
import logging

from employees.models import Employee
from job_profiles.models import JobProfile
from .models import (
    TrainingCategory, TrainingCourse, TrainingEnrollment,
    TrainingRecommendation, SkillTrainingMapping
)
from .training_recommender import TrainingRecommender, filter_courses_by_criteria, generate_training_roadmap

logger = logging.getLogger(__name__)


class TrainingRecommendationService:
    """교육 추천 서비스"""
    
    def __init__(self):
        self.recommender = TrainingRecommender()
    
    def get_employee_training_recommendations(
        self,
        employee: Employee,
        target_job: Optional[str] = None,
        missing_skills: Optional[List[str]] = None,
        include_completed: bool = False,
        max_recommendations: int = 10
    ) -> Dict:
        """
        직원별 맞춤 교육 추천
        
        Args:
            employee: 직원 객체
            target_job: 목표 직무 (없으면 리더 추천에서 가져옴)
            missing_skills: 부족 스킬 목록 (없으면 자동 분석)
            include_completed: 완료 교육 포함 여부
            max_recommendations: 최대 추천 수
        
        Returns:
            추천 결과 딕셔너리
        """
        # 캐시 확인
        cache_key = f"training_recommendations_{employee.id}_{target_job}"
        cached_result = cache.get(cache_key)
        
        if cached_result and not include_completed:
            return cached_result
        
        # 1. 컨텍스트 정보 수집
        context = self._get_recommendation_context(employee, target_job, missing_skills)
        
        if not context['missing_skills']:
            return {
                'status': 'no_recommendations',
                'message': '현재 추천할 교육이 없습니다.',
                'context': context,
                'recommendations': []
            }
        
        # 2. 이수 완료 교육 조회
        completed_course_ids = []
        if not include_completed:
            completed_course_ids = list(
                TrainingEnrollment.objects.filter(
                    employee=employee,
                    status='COMPLETED'
                ).values_list('course_id', flat=True)
            )
        
        # 3. 추천 가능한 교육과정 조회
        available_courses = self._get_available_courses(
            missing_skills=context['missing_skills'],
            current_level=context['current_level']
        )
        
        # 4. 교육 추천 실행
        recommendations = self.recommender.recommend_trainings(
            missing_skills=context['missing_skills'],
            current_level=context['current_level'],
            target_job=context['target_job'],
            available_courses=available_courses,
            completed_courses=[str(id) for id in completed_course_ids],
            max_recommendations=max_recommendations
        )
        
        # 5. 추가 정보 보강
        enriched_recommendations = self._enrich_recommendations(
            recommendations, employee
        )
        
        # 6. 학습 로드맵 생성
        roadmap = generate_training_roadmap(
            enriched_recommendations,
            available_time_per_month=20
        )
        
        result = {
            'status': 'success',
            'context': context,
            'recommendations': enriched_recommendations,
            'roadmap': roadmap,
            'summary': self._generate_summary(enriched_recommendations, context)
        }
        
        # 캐시 저장 (1시간)
        cache.set(cache_key, result, 3600)
        
        # 추천 이력 저장
        self._save_recommendations(employee, enriched_recommendations, context)
        
        return result
    
    def _get_recommendation_context(
        self,
        employee: Employee,
        target_job: Optional[str] = None,
        missing_skills: Optional[List[str]] = None
    ) -> Dict:
        """추천 컨텍스트 정보 수집"""
        context = {
            'employee_id': employee.id,
            'current_position': employee.position,
            'department': employee.department,
            'current_level': self._get_employee_level(employee),
            'target_job': target_job,
            'missing_skills': missing_skills or []
        }
        
        # 목표 직무와 부족 스킬이 없으면 리더 추천에서 가져오기
        if not target_job or not missing_skills:
            # Import here to avoid circular import
            from job_profiles.ess_leader_api import get_my_leader_recommendation_summary
            leader_summary = get_my_leader_recommendation_summary(employee.id)
            
            if leader_summary.get('has_recommendation'):
                context['target_job'] = leader_summary.get('best_match_job', target_job)
                
                # 부족 스킬은 ESS API에서 가져오기
                from job_profiles.ess_leader_api import MyLeaderGrowthStatusAPI
                # 실제로는 API 호출 대신 서비스 메서드 사용
                growth_status = self._get_growth_status_data(employee)
                
                if growth_status and growth_status.get('leadership_recommendations'):
                    top_recommendation = growth_status['leadership_recommendations'][0]
                    context['missing_skills'] = top_recommendation.get('missing_skills', [])
        
        return context
    
    def _get_employee_level(self, employee: Employee) -> str:
        """직원 성장레벨 추정"""
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
    
    def _get_growth_status_data(self, employee: Employee) -> Dict:
        """성장 상태 데이터 조회 (더미)"""
        # 실제로는 ESS API 서비스 호출
        return {
            'leadership_recommendations': [
                {
                    'job_name': '팀장',
                    'missing_skills': ['전략수립', '조직운영', '예산관리']
                }
            ]
        }
    
    def _get_available_courses(
        self,
        missing_skills: List[str],
        current_level: str
    ) -> List[Dict]:
        """추천 가능한 교육과정 조회"""
        # 스킬 매핑 테이블에서 관련 교육 찾기
        skill_mappings = SkillTrainingMapping.objects.filter(
            skill_name__in=missing_skills
        ).prefetch_related('courses')
        
        # 관련 교육과정 ID 수집
        course_ids = set()
        for mapping in skill_mappings:
            course_ids.update(mapping.courses.values_list('id', flat=True))
        
        # 추가로 스킬 키워드로 직접 검색
        skill_query = Q()
        for skill in missing_skills:
            skill_query |= Q(related_skills__icontains=skill)
            skill_query |= Q(title__icontains=skill)
            skill_query |= Q(description__icontains=skill)
        
        # 교육과정 조회
        courses = TrainingCourse.objects.filter(
            Q(id__in=course_ids) | skill_query,
            is_active=True
        ).distinct()
        
        # 딕셔너리로 변환
        course_list = []
        for course in courses:
            course_dict = {
                'id': str(course.id),
                'course_code': course.course_code,
                'title': course.title,
                'category': course.category.name if course.category else '일반',
                'description': course.description,
                'objectives': course.objectives,
                'related_skills': course.related_skills,
                'skill_level': course.skill_level,
                'duration_hours': course.duration_hours,
                'course_type': course.course_type,
                'provider': course.provider,
                'cost': float(course.cost),
                'is_mandatory': course.is_mandatory,
                'certification_eligible': course.certification_eligible,
                'growth_level_impact': course.growth_level_impact
            }
            course_list.append(course_dict)
        
        return course_list
    
    def _enrich_recommendations(
        self,
        recommendations: List[Dict],
        employee: Employee
    ) -> List[Dict]:
        """추천 결과에 추가 정보 보강"""
        enriched = []
        
        for rec in recommendations:
            # 과거 수강 이력 확인
            past_enrollments = TrainingEnrollment.objects.filter(
                employee=employee,
                course_id=rec['course_id']
            ).order_by('-enrolled_date')
            
            # 수강 가능 여부 확인
            can_enroll = True
            enrollment_message = ""
            
            if past_enrollments.exists():
                last_enrollment = past_enrollments.first()
                if last_enrollment.status in ['APPLIED', 'APPROVED', 'IN_PROGRESS']:
                    can_enroll = False
                    enrollment_message = f"현재 {last_enrollment.get_status_display()} 상태입니다"
                elif last_enrollment.status == 'COMPLETED':
                    # 재수강 가능 기간 확인 (1년)
                    if last_enrollment.completion_date:
                        days_since = (datetime.now() - last_enrollment.completion_date).days
                        if days_since < 365:
                            can_enroll = False
                            enrollment_message = f"재수강은 {365 - days_since}일 후 가능합니다"
            
            # 다음 기수 정보 (더미)
            next_session = self._get_next_session_info(rec['course_id'])
            
            rec.update({
                'can_enroll': can_enroll,
                'enrollment_message': enrollment_message,
                'past_attempts': past_enrollments.count(),
                'last_enrollment_date': past_enrollments.first().enrolled_date.isoformat() if past_enrollments.exists() else None,
                'next_session': next_session,
                'completion_rate': self._calculate_completion_rate(rec['course_id']),
                'average_satisfaction': self._get_average_satisfaction(rec['course_id'])
            })
            
            enriched.append(rec)
        
        return enriched
    
    def _get_next_session_info(self, course_id: str) -> Dict:
        """다음 교육 기수 정보 (더미)"""
        # 실제로는 교육 일정 모델에서 조회
        next_month = datetime.now() + timedelta(days=30)
        return {
            'start_date': next_month.strftime('%Y-%m-%d'),
            'end_date': (next_month + timedelta(days=5)).strftime('%Y-%m-%d'),
            'enrollment_deadline': (next_month - timedelta(days=7)).strftime('%Y-%m-%d'),
            'seats_available': 20,
            'location': '온라인'
        }
    
    def _calculate_completion_rate(self, course_id: str) -> float:
        """교육 이수율 계산"""
        enrollments = TrainingEnrollment.objects.filter(
            course_id=course_id,
            status__in=['COMPLETED', 'INCOMPLETE']
        )
        
        if not enrollments.exists():
            return 0.0
        
        completed = enrollments.filter(status='COMPLETED').count()
        total = enrollments.count()
        
        return (completed / total) * 100 if total > 0 else 0.0
    
    def _get_average_satisfaction(self, course_id: str) -> float:
        """평균 만족도 조회"""
        avg_satisfaction = TrainingEnrollment.objects.filter(
            course_id=course_id,
            satisfaction_score__isnull=False
        ).aggregate(avg=Avg('satisfaction_score'))['avg']
        
        return avg_satisfaction or 0.0
    
    def _generate_summary(
        self,
        recommendations: List[Dict],
        context: Dict
    ) -> Dict:
        """추천 요약 생성"""
        total_hours = sum(r['duration_hours'] for r in recommendations)
        total_cost = sum(r['cost'] for r in recommendations)
        
        # 스킬 커버리지 계산
        all_covered_skills = set()
        for rec in recommendations:
            all_covered_skills.update(rec.get('matched_skills', []))
        
        coverage = len(all_covered_skills) / len(context['missing_skills']) if context['missing_skills'] else 0
        
        # 예상 완료 기간
        if recommendations:
            roadmap = generate_training_roadmap(recommendations)
            estimated_months = len(roadmap)
        else:
            estimated_months = 0
        
        return {
            'total_courses': len(recommendations),
            'total_hours': total_hours,
            'total_cost': total_cost,
            'skill_coverage': coverage,
            'covered_skills': list(all_covered_skills),
            'uncovered_skills': list(set(context['missing_skills']) - all_covered_skills),
            'estimated_completion_months': estimated_months,
            'priority_courses': [r for r in recommendations if r['priority'] >= 80][:3]
        }
    
    def _save_recommendations(
        self,
        employee: Employee,
        recommendations: List[Dict],
        context: Dict
    ):
        """추천 이력 저장"""
        for idx, rec in enumerate(recommendations):
            try:
                course = TrainingCourse.objects.get(id=rec['course_id'])
                
                TrainingRecommendation.objects.update_or_create(
                    employee=employee,
                    course=course,
                    target_job=context['target_job'],
                    defaults={
                        'missing_skills': context['missing_skills'],
                        'match_score': rec['match_score'],
                        'priority': rec['priority'],
                        'recommendation_type': rec['recommendation_type'],
                        'recommendation_comment': rec['recommendation_reason'],
                        'expires_at': datetime.now() + timedelta(days=90)
                    }
                )
            except Exception as e:
                logger.error(f"Failed to save recommendation: {str(e)}")
    
    def enroll_in_course(
        self,
        employee: Employee,
        course_id: str,
        notes: str = ""
    ) -> Dict:
        """교육 수강 신청"""
        try:
            course = TrainingCourse.objects.get(id=course_id)
            
            # 중복 신청 확인
            existing = TrainingEnrollment.objects.filter(
                employee=employee,
                course=course,
                status__in=['APPLIED', 'APPROVED', 'IN_PROGRESS']
            ).exists()
            
            if existing:
                return {
                    'success': False,
                    'message': '이미 신청한 교육입니다.'
                }
            
            # 수강 신청 생성
            enrollment = TrainingEnrollment.objects.create(
                employee=employee,
                course=course,
                status='APPLIED',
                notes=notes
            )
            
            # 추천에서 신청한 경우 업데이트
            TrainingRecommendation.objects.filter(
                employee=employee,
                course=course
            ).update(
                is_enrolled=True,
                enrolled_date=datetime.now()
            )
            
            return {
                'success': True,
                'enrollment_id': str(enrollment.id),
                'message': '수강 신청이 완료되었습니다.'
            }
            
        except TrainingCourse.DoesNotExist:
            return {
                'success': False,
                'message': '교육과정을 찾을 수 없습니다.'
            }
        except Exception as e:
            logger.error(f"Enrollment error: {str(e)}")
            return {
                'success': False,
                'message': '수강 신청 중 오류가 발생했습니다.'
            }
    
    def get_my_training_history(
        self,
        employee: Employee,
        status_filter: Optional[List[str]] = None
    ) -> List[Dict]:
        """내 교육 이력 조회"""
        query = TrainingEnrollment.objects.filter(
            employee=employee
        ).select_related('course', 'course__category')
        
        if status_filter:
            query = query.filter(status__in=status_filter)
        
        history = []
        for enrollment in query.order_by('-enrolled_date'):
            history.append({
                'enrollment_id': str(enrollment.id),
                'course': {
                    'id': str(enrollment.course.id),
                    'code': enrollment.course.course_code,
                    'title': enrollment.course.title,
                    'category': enrollment.course.category.name if enrollment.course.category else '일반'
                },
                'status': enrollment.status,
                'status_display': enrollment.get_status_display(),
                'enrolled_date': enrollment.enrolled_date.isoformat(),
                'start_date': enrollment.start_date.isoformat() if enrollment.start_date else None,
                'completion_date': enrollment.completion_date.isoformat() if enrollment.completion_date else None,
                'attendance_rate': enrollment.attendance_rate,
                'test_score': enrollment.test_score,
                'satisfaction_score': enrollment.satisfaction_score
            })
        
        return history