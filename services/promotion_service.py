"""
승진 관리 서비스
"""
from typing import Dict, List, Optional, Tuple
from django.db import transaction, models
from datetime import date, datetime
import logging

from promotions.models import (
    PromotionRequest, PromotionRequirement,
    JobTransfer, OrganizationChart
)
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from core.exceptions import ValidationError, PromotionError
from core.utils import DateCalculator
from core.mcp import MCPSequentialService


logger = logging.getLogger(__name__)


class PromotionService:
    """승진 관리 비즈니스 로직"""
    
    def __init__(self):
        self.sequential_service = MCPSequentialService()
        
        # 기본 승진 요건
        self.default_requirements = {
            'Level_1_to_2': {
                'min_years': 2,
                'consecutive_a_grades': 1,
                'min_avg_score': 3.0
            },
            'Level_2_to_3': {
                'min_years': 3,
                'consecutive_a_grades': 2,
                'min_avg_score': 3.2
            },
            'Level_3_to_4': {
                'min_years': 4,
                'consecutive_a_grades': 2,
                'min_avg_score': 3.5
            },
            'Level_4_to_5': {
                'min_years': 5,
                'consecutive_a_grades': 3,
                'min_avg_score': 3.7
            },
            'Level_5_to_6': {
                'min_years': 7,
                'consecutive_a_grades': 3,
                'min_avg_score': 4.0
            }
        }
    
    def check_promotion_eligibility(self, employee_id: int) -> Dict:
        """승진 자격 확인"""
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # 현재 레벨에서 다음 레벨로의 요건 확인
            current_level = employee.growth_level
            next_level = self._get_next_level(current_level)
            
            if not next_level:
                return {
                    'eligible': False,
                    'reason': '최고 레벨에 도달했습니다.',
                    'current_level': current_level
                }
            
            # 재직 기간 계산
            years, months, days = DateCalculator.calculate_work_period(employee.hire_date)
            
            # 평가 이력 조회
            evaluations = ComprehensiveEvaluation.objects.filter(
                employee=employee,
                is_completed=True
            ).order_by('-evaluation_period__end_date')
            
            # 연속 A등급 이상 횟수 계산
            consecutive_a = self._count_consecutive_a_grades(evaluations)
            
            # 평균 성과 점수 계산
            avg_score = self._calculate_average_score(evaluations[:4])  # 최근 4개 평가
            
            # 요건 조회
            req_key = f"{current_level}_to_{next_level.split('_')[1]}"
            requirements = self.default_requirements.get(req_key, {})
            
            # 자격 판단
            is_eligible = (
                years >= requirements.get('min_years', 0) and
                consecutive_a >= requirements.get('consecutive_a_grades', 0) and
                avg_score >= requirements.get('min_avg_score', 0)
            )
            
            result = {
                'eligible': is_eligible,
                'current_level': current_level,
                'next_level': next_level,
                'requirements': requirements,
                'current_status': {
                    'years_of_service': years,
                    'consecutive_a_grades': consecutive_a,
                    'average_score': avg_score
                }
            }
            
            if not is_eligible:
                missing = []
                if years < requirements.get('min_years', 0):
                    missing.append(f"재직기간 {requirements['min_years'] - years}년 부족")
                if consecutive_a < requirements.get('consecutive_a_grades', 0):
                    missing.append(f"연속 A등급 {requirements['consecutive_a_grades'] - consecutive_a}회 부족")
                if avg_score < requirements.get('min_avg_score', 0):
                    missing.append(f"평균점수 {requirements['min_avg_score'] - avg_score:.1f}점 부족")
                
                result['missing_requirements'] = missing
            
            return result
            
        except Employee.DoesNotExist:
            raise PromotionError(f"직원 ID {employee_id}를 찾을 수 없습니다.")
    
    def _get_next_level(self, current_level: str) -> Optional[str]:
        """다음 성장 레벨 반환"""
        level_map = {
            'Level_1': 'Level_2',
            'Level_2': 'Level_3',
            'Level_3': 'Level_4',
            'Level_4': 'Level_5',
            'Level_5': 'Level_6',
            'Level_6': None
        }
        return level_map.get(current_level)
    
    def _count_consecutive_a_grades(self, evaluations) -> int:
        """연속 A등급 이상 횟수 계산"""
        count = 0
        for eval in evaluations:
            grade = eval.final_grade or eval.manager_grade
            if grade in ['S', 'A+', 'A']:
                count += 1
            else:
                break
        return count
    
    def _calculate_average_score(self, evaluations) -> float:
        """평균 성과 점수 계산"""
        if not evaluations:
            return 0.0
        
        scores = [eval.total_score for eval in evaluations if eval.total_score]
        if not scores:
            return 0.0
        
        return sum(scores) / len(scores)
    
    @transaction.atomic
    def create_promotion_request(
        self,
        employee_id: int,
        target_level: str,
        recommendation_reason: str,
        requested_by_id: int
    ) -> PromotionRequest:
        """승진 요청 생성"""
        employee = Employee.objects.get(id=employee_id)
        requested_by = Employee.objects.get(id=requested_by_id)
        
        # 자격 확인
        eligibility = self.check_promotion_eligibility(employee_id)
        
        if not eligibility['eligible']:
            raise ValidationError(
                f"승진 자격 미달: {', '.join(eligibility.get('missing_requirements', []))}"
            )
        
        # 중복 요청 확인
        existing = PromotionRequest.objects.filter(
            employee=employee,
            status='PENDING'
        ).exists()
        
        if existing:
            raise ValidationError("이미 진행 중인 승진 요청이 있습니다.")
        
        # 승진 요청 생성
        request = PromotionRequest.objects.create(
            employee=employee,
            current_level=employee.growth_level,
            target_level=target_level,
            requested_by=requested_by,
            request_date=date.today(),
            status='PENDING',
            years_of_service=eligibility['current_status']['years_of_service'],
            consecutive_a_grades=eligibility['current_status']['consecutive_a_grades'],
            average_performance_score=eligibility['current_status']['average_score'],
            recommendation_reason=recommendation_reason
        )
        
        logger.info(f"Promotion request created for {employee.employee_number}")
        return request
    
    @transaction.atomic
    def approve_promotion(
        self,
        request_id: int,
        approved_by_id: int,
        approval_comments: str = ""
    ) -> PromotionRequest:
        """승진 승인"""
        promotion_request = PromotionRequest.objects.get(id=request_id)
        approved_by = Employee.objects.get(id=approved_by_id)
        
        if promotion_request.status != 'PENDING':
            raise ValidationError("대기 중인 요청만 승인할 수 있습니다.")
        
        # 승진 처리
        promotion_request.status = 'APPROVED'
        promotion_request.approved_by = approved_by
        promotion_request.approval_date = date.today()
        promotion_request.approval_comments = approval_comments
        promotion_request.save()
        
        # 직원 레벨 업데이트
        employee = promotion_request.employee
        employee.growth_level = promotion_request.target_level
        employee.save()
        
        # 인사이동 기록 생성
        JobTransfer.objects.create(
            employee=employee,
            transfer_type='PROMOTION',
            transfer_date=date.today(),
            from_position=employee.position,
            to_position=employee.position,  # 직급은 동일
            from_department=employee.department,
            to_department=employee.department,  # 부서는 동일
            reason=f"승진: {promotion_request.current_level} → {promotion_request.target_level}"
        )
        
        logger.info(f"Promotion approved for {employee.employee_number}")
        return promotion_request
    
    def reject_promotion(
        self,
        request_id: int,
        rejected_by_id: int,
        rejection_reason: str
    ) -> PromotionRequest:
        """승진 거절"""
        promotion_request = PromotionRequest.objects.get(id=request_id)
        rejected_by = Employee.objects.get(id=rejected_by_id)
        
        if promotion_request.status != 'PENDING':
            raise ValidationError("대기 중인 요청만 거절할 수 있습니다.")
        
        promotion_request.status = 'REJECTED'
        promotion_request.approved_by = rejected_by  # 거절자 기록
        promotion_request.approval_date = date.today()
        promotion_request.approval_comments = rejection_reason
        promotion_request.save()
        
        logger.info(f"Promotion rejected for {promotion_request.employee.employee_number}")
        return promotion_request
    
    def analyze_promotion_candidates(self, target_year: Optional[int] = None) -> Dict:
        """승진 후보자 분석"""
        # 시퀀셜 서비스로 복잡한 분석 처리
        context = self.sequential_service.execute_process(
            'promotion_analysis',
            {'target_year': target_year or date.today().year}
        )
        
        return context.get_summary()
    
    @transaction.atomic
    def process_job_transfer(
        self,
        employee_id: int,
        transfer_type: str,
        to_department: str,
        to_position: Optional[str] = None,
        transfer_date: date = None,
        reason: str = ""
    ) -> JobTransfer:
        """인사이동 처리"""
        employee = Employee.objects.get(id=employee_id)
        
        if not transfer_date:
            transfer_date = date.today()
        
        # 인사이동 기록 생성
        transfer = JobTransfer.objects.create(
            employee=employee,
            transfer_type=transfer_type,
            transfer_date=transfer_date,
            from_department=employee.department,
            to_department=to_department,
            from_position=employee.position,
            to_position=to_position or employee.position,
            reason=reason
        )
        
        # 직원 정보 업데이트
        employee.department = to_department
        if to_position:
            employee.position = to_position
        employee.save()
        
        logger.info(f"Job transfer processed for {employee.employee_number}")
        return transfer
    
    def get_promotion_statistics(self, year: Optional[int] = None) -> Dict:
        """승진 통계 조회"""
        if not year:
            year = date.today().year
        
        # 연도별 승진 요청
        requests = PromotionRequest.objects.filter(
            request_date__year=year
        )
        
        # 상태별 통계
        status_stats = dict(
            requests.values_list('status').annotate(
                count=models.Count('id')
            )
        )
        
        # 레벨별 승진 통계
        level_stats = {}
        for level_transition in requests.values('current_level', 'target_level').annotate(
            count=models.Count('id')
        ):
            key = f"{level_transition['current_level']} → {level_transition['target_level']}"
            level_stats[key] = level_transition['count']
        
        # 부서별 승진 통계
        dept_stats = dict(
            requests.values_list('employee__department').annotate(
                count=models.Count('id')
            )
        )
        
        # 평균 처리 시간
        approved_requests = requests.filter(status='APPROVED')
        if approved_requests.exists():
            processing_times = [
                (req.approval_date - req.request_date).days
                for req in approved_requests
                if req.approval_date
            ]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        else:
            avg_processing_time = 0
        
        return {
            'year': year,
            'total_requests': requests.count(),
            'status_distribution': status_stats,
            'level_transitions': level_stats,
            'department_distribution': dept_stats,
            'approval_rate': (
                (status_stats.get('APPROVED', 0) / requests.count() * 100)
                if requests.count() > 0 else 0
            ),
            'average_processing_days': avg_processing_time
        }
    
    def get_transfer_history(
        self,
        employee_id: Optional[int] = None,
        department: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[JobTransfer]:
        """인사이동 이력 조회"""
        queryset = JobTransfer.objects.select_related('employee')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        if department:
            queryset = queryset.filter(
                models.Q(from_department=department) |
                models.Q(to_department=department)
            )
        
        if start_date:
            queryset = queryset.filter(transfer_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(transfer_date__lte=end_date)
        
        return queryset.order_by('-transfer_date')