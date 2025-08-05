"""
리더 추천 리포트 Django 서비스
PDF 리포트 생성을 Django와 통합하는 서비스 레이어
"""

from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
import os
import json
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, FileResponse
from django.db.models import Q
import logging

from employees.models import Employee
from evaluations.models import (
    EvaluationPeriod, ComprehensiveEvaluation
)
from .models import JobProfile
from .leader_report_generator import LeaderReportGenerator
from .leader_services import LeaderRecommendationService
from .growth_services import GrowthPathService
from .recommendation_comment_generator import generate_recommendation_comment

logger = logging.getLogger(__name__)


class LeaderReportService:
    """리더 추천 리포트 서비스"""
    
    def __init__(self):
        self.report_generator = LeaderReportGenerator()
        self.leader_service = LeaderRecommendationService()
        self.growth_service = GrowthPathService()
        
        # 리포트 저장 경로 설정
        self.report_dir = os.path.join(
            settings.MEDIA_ROOT, 
            'reports', 
            'leadership'
        )
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_candidate_report(
        self,
        employee_id: int,
        target_job_profile_id: int,
        include_growth_path: bool = True,
        include_evaluation_history: bool = True,
        save_to_db: bool = True
    ) -> Dict[str, Union[str, bool]]:
        """
        개별 후보자 리포트 생성
        
        Args:
            employee_id: 직원 ID
            target_job_profile_id: 목표 직무 프로파일 ID
            include_growth_path: 성장 경로 포함 여부
            include_evaluation_history: 평가 이력 포함 여부
            save_to_db: DB 저장 여부
        
        Returns:
            생성 결과 딕셔너리
        """
        try:
            # 직원 정보 조회
            employee = Employee.objects.get(id=employee_id)
            target_job_profile = JobProfile.objects.get(id=target_job_profile_id)
            
            # 리더 후보 평가
            candidates = self.leader_service.find_leader_candidates(
                target_job_profile=target_job_profile,
                department=employee.department,
                top_n=10
            )
            
            # 해당 직원 찾기
            candidate_data = next(
                (c for c in candidates if str(c['employee_id']) == str(employee_id)),
                None
            )
            
            if not candidate_data:
                # 직접 평가
                candidate_data = self._evaluate_single_candidate(
                    employee, 
                    target_job_profile
                )
            
            # 목표 직무 정보
            target_job = {
                'name': target_job_profile.job_role.name,
                'required_skills': target_job_profile.basic_skills + target_job_profile.applied_skills,
                'qualification': target_job_profile.qualification
            }
            
            # 성장 경로 정보
            growth_path = None
            if include_growth_path:
                growth_paths = self.growth_service.get_employee_growth_paths(
                    employee=employee,
                    target_job_ids=[str(target_job_profile_id)],
                    include_evaluation=True,
                    top_n=1
                )
                
                if growth_paths:
                    gp = growth_paths[0]['growth_path']
                    growth_path = {
                        'target_job': gp.target_job,
                        'total_years': gp.total_years,
                        'success_probability': gp.success_probability,
                        'difficulty_score': gp.difficulty_score,
                        'stages': [
                            {
                                'job_name': stage.job_name,
                                'expected_years': stage.expected_years,
                                'required_skills': stage.required_skills
                            }
                            for stage in gp.stages
                        ]
                    }
            
            # 평가 이력
            evaluation_history = None
            if include_evaluation_history:
                evaluation_history = self._get_evaluation_history(employee)
            
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"leader_report_{employee.name}_{timestamp}.pdf"
            output_path = os.path.join(self.report_dir, filename)
            
            # PDF 생성
            report_path = self.report_generator.generate_leader_recommendation_report(
                candidate=candidate_data,
                target_job=target_job,
                growth_path=growth_path,
                evaluation_history=evaluation_history,
                output_path=output_path
            )
            
            # DB 저장
            if save_to_db:
                self._save_report_to_db(
                    employee=employee,
                    target_job_profile=target_job_profile,
                    report_path=report_path,
                    candidate_data=candidate_data
                )
            
            return {
                'success': True,
                'report_path': report_path,
                'filename': filename,
                'download_url': f"/media/reports/leadership/{filename}",
                'candidate_score': candidate_data.get('match_score', 0)
            }
            
        except Employee.DoesNotExist:
            return {
                'success': False,
                'error': 'Employee not found'
            }
        except JobProfile.DoesNotExist:
            return {
                'success': False,
                'error': 'Job profile not found'
            }
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_batch_reports(
        self,
        target_job_profile_id: int,
        department: Optional[str] = None,
        min_evaluation_grade: str = "B+",
        top_n: int = 10
    ) -> Dict[str, Union[bool, List[str]]]:
        """
        배치로 여러 후보자 리포트 생성
        
        Args:
            target_job_profile_id: 목표 직무 ID
            department: 부서 제한
            min_evaluation_grade: 최소 평가 등급
            top_n: 상위 N명
        
        Returns:
            생성 결과
        """
        try:
            target_job_profile = JobProfile.objects.get(id=target_job_profile_id)
            
            # 리더 후보 찾기
            candidates = self.leader_service.find_leader_candidates(
                target_job_profile=target_job_profile,
                department=department,
                min_evaluation_grade=min_evaluation_grade,
                top_n=top_n
            )
            
            if not candidates:
                return {
                    'success': False,
                    'error': 'No candidates found',
                    'generated_files': []
                }
            
            # 배치 디렉토리 생성
            batch_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            batch_dir = os.path.join(
                self.report_dir, 
                f"batch_{target_job_profile.job_role.name}_{batch_timestamp}"
            )
            os.makedirs(batch_dir, exist_ok=True)
            
            # 목표 직무 정보
            target_job = {
                'name': target_job_profile.job_role.name,
                'required_skills': target_job_profile.basic_skills + target_job_profile.applied_skills
            }
            
            # 리포트 생성
            generated_files = self.report_generator.generate_batch_reports(
                candidates=candidates[:top_n],
                target_job=target_job,
                output_dir=batch_dir,
                include_growth_path=True,
                include_evaluation_history=True
            )
            
            # 요약 파일 생성
            summary_path = self._create_batch_summary(
                candidates[:top_n],
                target_job_profile,
                batch_dir
            )
            
            return {
                'success': True,
                'generated_files': generated_files,
                'summary_file': summary_path,
                'batch_directory': batch_dir
            }
            
        except Exception as e:
            logger.error(f"Error in batch report generation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'generated_files': []
            }
    
    def get_report_download_response(
        self,
        report_path: str,
        as_attachment: bool = True
    ) -> HttpResponse:
        """
        리포트 다운로드 응답 생성
        
        Args:
            report_path: 리포트 파일 경로
            as_attachment: 첨부파일로 다운로드 여부
        
        Returns:
            파일 응답
        """
        if not os.path.exists(report_path):
            return HttpResponse("Report not found", status=404)
        
        response = FileResponse(
            open(report_path, 'rb'),
            content_type='application/pdf'
        )
        
        filename = os.path.basename(report_path)
        if as_attachment:
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
    
    def _evaluate_single_candidate(
        self,
        employee: Employee,
        target_job_profile: JobProfile
    ) -> dict:
        """단일 후보자 평가"""
        # 직원 정보를 후보자 데이터 형식으로 변환
        emp_dict = self.leader_service._convert_employee_to_dict(employee)
        target_job = self.leader_service._convert_job_profile_to_dict(target_job_profile)
        
        # 평가 수행
        readiness = self.leader_service.recommender.evaluate_leadership_readiness(
            emp_dict,
            target_job
        )
        
        # 스킬 갭 계산
        skill_gap = readiness['qualification_details']['skills'].get('missing_skills', [])
        
        # 승진 준비 여부
        promotion_ready = readiness['total_score'] >= 80 and readiness['is_qualified']
        
        # 자연어 추천 코멘트 생성
        natural_language_comment = generate_recommendation_comment(
            employee_profile=emp_dict,
            target_job_profile=target_job,
            match_score=readiness['total_score'],
            skill_gap=skill_gap,
            promotion_ready=promotion_ready,
            language="ko"
        )
        
        # 후보자 데이터 구성
        candidate_data = {
            'employee_id': str(employee.id),
            'name': employee.name,
            'current_position': employee.position,
            'department': employee.department,
            'growth_level': emp_dict.get('level', 'N/A'),
            'evaluation_grade': emp_dict.get('recent_evaluation', {}).get('overall_grade', 'N/A'),
            'experience_years': emp_dict.get('career_years', 0),
            'match_score': readiness['total_score'],
            'skill_match_rate': readiness['qualification_details']['skills'].get('match_rate', 0),
            'matched_skills': readiness['qualification_details']['skills'].get('matched_skills', []),
            'missing_skills': skill_gap,
            'qualifications': emp_dict.get('certifications', []),
            'recommendation_reason': natural_language_comment,  # 자연어 코멘트 사용
            'risk_factors': self.leader_service.recommender.identify_risk_factors(
                emp_dict, target_job
            )
        }
        
        return candidate_data
    
    def _get_evaluation_history(self, employee: Employee) -> List[dict]:
        """직원 평가 이력 조회"""
        evaluations = ComprehensiveEvaluation.objects.filter(
            employee=employee
        ).order_by('-created_at')[:10]
        
        history = []
        for eval in evaluations:
            period = f"{eval.evaluation_period.start_date.year} "
            if eval.evaluation_period.evaluation_type == 'QUARTERLY':
                quarter = (eval.evaluation_period.start_date.month - 1) // 3 + 1
                period += f"Q{quarter}"
            else:
                period += f"H{1 if eval.evaluation_period.start_date.month <= 6 else 2}"
            
            history.append({
                'period': period,
                'overall_grade': eval.final_grade,
                'professionalism': eval.expertise_grade,
                'contribution': self._get_contribution_text(eval),
                'impact': self._get_impact_text(eval)
            })
        
        return history
    
    def _get_contribution_text(self, evaluation) -> str:
        """기여도 텍스트 변환"""
        # 실제 모델 구조에 따라 조정
        if hasattr(evaluation, 'contribution_evaluation'):
            contrib = evaluation.contribution_evaluation
            if hasattr(contrib, 'ranking_percent'):
                return f"Top {contrib.ranking_percent}%"
        return "N/A"
    
    def _get_impact_text(self, evaluation) -> str:
        """영향력 텍스트 변환"""
        # 실제 모델 구조에 따라 조정
        if hasattr(evaluation, 'impact_evaluation'):
            impact = evaluation.impact_evaluation
            if hasattr(impact, 'impact_scope'):
                scope_map = {
                    'PERSONAL': '개인',
                    'TEAM': '조직 내',
                    'CROSS_TEAM': '조직 간',
                    'COMPANY': '전사'
                }
                return scope_map.get(impact.impact_scope, 'N/A')
        return "N/A"
    
    def _save_report_to_db(
        self,
        employee: Employee,
        target_job_profile: JobProfile,
        report_path: str,
        candidate_data: dict
    ):
        """리포트 정보를 DB에 저장"""
        # ReportHistory 모델이 있다고 가정
        # 실제로는 모델 생성 필요
        try:
            from .models import LeadershipReportHistory
            
            LeadershipReportHistory.objects.create(
                employee=employee,
                target_job_profile=target_job_profile,
                report_path=report_path,
                match_score=candidate_data.get('match_score', 0),
                recommendation_grade=self._get_recommendation_grade(
                    candidate_data.get('match_score', 0)
                ),
                generated_by=None,  # 시스템 자동 생성
                metadata=json.dumps({
                    'skill_match_rate': candidate_data.get('skill_match_rate', 0),
                    'evaluation_grade': candidate_data.get('evaluation_grade'),
                    'growth_level': candidate_data.get('growth_level')
                })
            )
        except Exception as e:
            logger.warning(f"Could not save report to DB: {str(e)}")
    
    def _get_recommendation_grade(self, score: float) -> str:
        """점수 기반 추천 등급"""
        if score >= 80:
            return 'STRONG'
        elif score >= 60:
            return 'CONSIDER'
        else:
            return 'NOT_RECOMMENDED'
    
    def _create_batch_summary(
        self,
        candidates: List[dict],
        target_job_profile: JobProfile,
        output_dir: str
    ) -> str:
        """배치 요약 파일 생성"""
        summary_path = os.path.join(output_dir, 'batch_summary.json')
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'target_position': target_job_profile.job_role.name,
            'total_candidates': len(candidates),
            'candidates': []
        }
        
        # 추천 등급별 집계
        grade_counts = {'STRONG': 0, 'CONSIDER': 0, 'NOT_RECOMMENDED': 0}
        
        for candidate in candidates:
            score = candidate.get('match_score', 0)
            grade = self._get_recommendation_grade(score)
            grade_counts[grade] += 1
            
            summary['candidates'].append({
                'name': candidate['name'],
                'department': candidate['department'],
                'score': score,
                'recommendation': grade
            })
        
        summary['grade_distribution'] = grade_counts
        
        # 저장
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return summary_path


# 뷰에서 사용할 헬퍼 함수
def generate_leader_report_view(request, employee_id: int, job_profile_id: int):
    """
    리더 추천 리포트 생성 뷰
    
    사용 예:
    from job_profiles.report_services import generate_leader_report_view
    
    urlpatterns = [
        path('leader-report/<int:employee_id>/<int:job_profile_id>/', 
             generate_leader_report_view, name='generate_leader_report'),
    ]
    """
    from django.shortcuts import redirect
    from django.contrib import messages
    
    service = LeaderReportService()
    
    # 리포트 생성
    result = service.generate_candidate_report(
        employee_id=employee_id,
        target_job_profile_id=job_profile_id,
        include_growth_path=True,
        include_evaluation_history=True
    )
    
    if result['success']:
        # 다운로드 응답 반환
        return service.get_report_download_response(
            result['report_path'],
            as_attachment=True
        )
    else:
        messages.error(request, f"Report generation failed: {result.get('error')}")
        return redirect('job_profiles:leader_candidates')


# 사용 예시
if __name__ == "__main__":
    # Django 환경 설정
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    django.setup()
    
    try:
        service = LeaderReportService()
        
        # 첫 번째 직원과 팀장 직무로 테스트
        employee = Employee.objects.filter(employment_status='재직').first()
        job_profile = JobProfile.objects.filter(
            job_role__name__icontains='팀장'
        ).first()
        
        if employee and job_profile:
            print(f"\nGenerating report for {employee.name}...")
            
            result = service.generate_candidate_report(
                employee_id=employee.id,
                target_job_profile_id=job_profile.id,
                include_growth_path=True,
                include_evaluation_history=True
            )
            
            if result['success']:
                print(f"Report generated successfully!")
                print(f"Path: {result['report_path']}")
                print(f"Score: {result['candidate_score']}")
            else:
                print(f"Error: {result.get('error')}")
                
    except Exception as e:
        print(f"Test error: {e}")