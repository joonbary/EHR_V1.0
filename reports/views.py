from django.views.generic import ListView, View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from permissions.mixins import HRPermissionMixin
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from compensation.models import EmployeeCompensation
from promotions.models import PromotionRequest
from .utils import ExcelReportGenerator
from .models import ReportTemplate, ReportGeneration
from datetime import datetime
from utils.file_manager import FileManager, ExcelFileHandler
from utils.airiss_api_service import AIRISSAPIService
import os
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)

class ReportDashboardView(ListView):
    """리포트 대시보드"""
    model = ReportTemplate
    template_name = 'reports/dashboard_revolutionary.html'
    context_object_name = 'templates'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_reports'] = ReportGeneration.objects.select_related(
            'template'
        ).order_by('-generated_at')[:10]  # removed 'generated_by'
        return context

class EmployeeListReportView(View):
    """직원 명부 리포트"""
    
    def get(self, request):
        # 필터 파라미터
        department = request.GET.get('department')
        position = request.GET.get('position')
        growth_level = request.GET.get('growth_level')
        
        # 데이터 조회
        employees = Employee.objects.all()
        if department:
            employees = employees.filter(department=department)
        if position:
            employees = employees.filter(position=position)
        if growth_level:
            employees = employees.filter(growth_level=growth_level)
            
        # Excel 생성
        generator = ExcelReportGenerator("직원 명부")
        generator.add_title(
            "OK금융그룹 직원 명부",
            f"생성일: {datetime.now().strftime('%Y년 %m월 %d일')}"
        )
        
        # 헤더
        headers = ['사번', '이름', '부서', '팀', '직책', '성장레벨', '직종', 
                  '입사일', '전화번호', '이메일']
        generator.add_headers(headers)
        
        # 데이터
        for emp in employees:
            generator.add_data_row([
                emp.employee_id,
                emp.name,
                emp.department,
                emp.team,
                emp.position,
                emp.growth_level,
                emp.job_type,
                emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else '',
                emp.phone,
                emp.email
            ])
            
        # 요약 정보
        generator.current_row += 1
        generator.add_data_row(['총 인원:', employees.count(), '', '', '', '', '', '', '', ''])
        
        # 리포트 생성 이력 저장
        ReportGeneration.objects.create(
            template_id=1,  # 직원 명부 템플릿
            generated_by=None,  # Authentication removed
            parameters_used={'department': department, 'position': position},
            record_count=employees.count(),
            file_format='excel'
        )
        
        # 파일 매니저를 통해 exports 폴더에 저장
        file_manager = FileManager()
        filename = f"직원명부_{datetime.now().strftime('%Y%m%d')}.xlsx"
        export_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
        
        # 임시 파일로 저장 후 exports 폴더로 이동
        response = generator.save_to_response(filename)
        
        # exports 폴더에 복사본 저장 (선택적)
        with open(export_path, 'wb') as f:
            f.write(response.content)
        
        return response

class EvaluationSummaryReportView(View):
    """평가 결과 요약 리포트"""
    
    def get(self, request):
        year = request.GET.get('year', datetime.now().year)
        
        # 평가 데이터 조회
        evaluations = ComprehensiveEvaluation.objects.filter(year=year).select_related('employee')
        
        # Excel 생성
        generator = ExcelReportGenerator("평가 결과")
        generator.add_title(
            f"{year}년 평가 결과 요약",
            f"생성일: {datetime.now().strftime('%Y년 %m월 %d일')}"
        )
        
        # 상세 데이터
        headers = ['사번', '이름', '부서', '직책', '성장레벨', 
                  '기여도', '전문성', '영향력', '종합등급', 'PI 지급률']
        generator.add_headers(headers)
        
        grade_counts = {'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for eval in evaluations:
            emp = eval.employee
            pi_rate = self.get_pi_rate(emp.growth_level, eval.final_grade)
            
            generator.add_data_row([
                emp.employee_id,
                emp.name,
                emp.department,
                emp.position,
                emp.growth_level,
                f"{eval.contribution_score}점",
                f"{eval.expertise_score}점",
                f"{eval.impact_score}점",
                eval.final_grade,
                f"{pi_rate}%"
            ])
            
            if eval.final_grade in grade_counts:
                grade_counts[eval.final_grade] += 1
                
        # 통계 섹션
        generator.current_row += 2
        generator.add_headers(['등급', '인원', '비율'])
        
        total = evaluations.count()
        for grade, count in grade_counts.items():
            ratio = (count / total * 100) if total > 0 else 0
            generator.add_data_row([grade, count, f"{ratio:.1f}%"])
            
        # 파일 매니저를 통해 exports 폴더에 저장
        file_manager = FileManager()
        filename = f"평가결과_{year}년.xlsx"
        export_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
        
        response = generator.save_to_response(filename)
        
        # exports 폴더에 복사본 저장
        with open(export_path, 'wb') as f:
            f.write(response.content)
        
        return response
    
    def get_pi_rate(self, level, grade):
        """PI 지급률 조회"""
        pi_rates = {
            'Level_1': {'S': 25.0, 'A+': 22.0, 'A': 20.0, 'B+': 17.0, 
                       'B': 15.0, 'C': 10.0, 'D': 0.0},
            'Level_2': {'S': 32.0, 'A+': 29.0, 'A': 27.0, 'B+': 24.0, 
                       'B': 22.0, 'C': 17.0, 'D': 0.0},
            'Level_3': {'S': 39.5, 'A+': 32.5, 'A': 30.0, 'B+': 27.5, 
                       'B': 25.0, 'C': 18.0, 'D': 0.0},
            'Level_4': {'S': 39.5, 'A+': 32.5, 'A': 30.0, 'B+': 27.5, 
                       'B': 25.0, 'C': 18.0, 'D': 0.0},
        }
        return pi_rates.get(level, {}).get(grade, 0)

class CompensationAnalysisReportView(View):
    """보상 분석 리포트"""
    
    def get(self, request):
        # 보상 데이터 분석
        compensations = EmployeeCompensation.objects.select_related('employee')
        
        generator = ExcelReportGenerator("보상 분석")
        generator.add_title(
            "보상 현황 분석 리포트",
            f"생성일: {datetime.now().strftime('%Y년 %m월 %d일')}"
        )
        
        # 개인별 보상 현황
        headers = ['사번', '이름', '부서', '성장레벨', '기본급', '역량급', 
                  '직책급', 'PI', '총 보상']
        generator.add_headers(headers)
        
        dept_totals = {}
        level_totals = {}
        
        for comp in compensations:
            emp = comp.employee
            total = comp.total_compensation
            
            generator.add_data_row([
                emp.employee_id,
                emp.name,
                emp.department,
                emp.growth_level,
                comp.base_salary,
                comp.competency_pay,
                comp.position_allowance or 0,
                comp.pi_amount,
                total
            ])
            
            # 부서별 집계
            if emp.department not in dept_totals:
                dept_totals[emp.department] = {'count': 0, 'total': 0}
            dept_totals[emp.department]['count'] += 1
            dept_totals[emp.department]['total'] += total
            
            # 레벨별 집계
            if emp.growth_level not in level_totals:
                level_totals[emp.growth_level] = {'count': 0, 'total': 0}
            level_totals[emp.growth_level]['count'] += 1
            level_totals[emp.growth_level]['total'] += total
            
        # 부서별 평균 보상
        generator.current_row += 2
        generator.add_headers(['부서', '인원', '평균 보상'])
        
        for dept, data in dept_totals.items():
            avg = data['total'] / data['count'] if data['count'] > 0 else 0
            generator.add_data_row([dept, data['count'], round(avg)])
            
        # 레벨별 평균 보상
        generator.current_row += 2
        generator.add_headers(['성장레벨', '인원', '평균 보상'])
        
        for level, data in level_totals.items():
            avg = data['total'] / data['count'] if data['count'] > 0 else 0
            generator.add_data_row([level, data['count'], round(avg)])
            
        return generator.save_to_response(f"보상분석_{datetime.now().strftime('%Y%m%d')}.xlsx")

class PromotionCandidatesReportView(View):
    """승진 대상자 리포트"""
    
    def get(self, request):
        # 승진 대상자 조회
        candidates = PromotionRequest.objects.filter(
            status='PENDING'
        ).select_related('employee')
        
        generator = ExcelReportGenerator("승진 대상자")
        generator.add_title(
            "승진 대상자 목록",
            f"생성일: {datetime.now().strftime('%Y년 %m월 %d일')}"
        )
        
        # 헤더
        headers = ['사번', '이름', '부서', '현재 직책', '현재 레벨', 
                  '목표 레벨', '재직기간', '연속A등급', '평균성과점수', '상태']
        generator.add_headers(headers)
        
        # 데이터
        for candidate in candidates:
            emp = candidate.employee
            generator.add_data_row([
                emp.employee_id,
                emp.name,
                emp.department,
                emp.position,
                candidate.current_level,
                candidate.target_level,
                f"{candidate.years_of_service}년",
                f"{candidate.consecutive_a_grades}회",
                f"{candidate.average_performance_score}점",
                candidate.get_status_display()
            ])
            
        return generator.save_to_response(f"승진대상자_{datetime.now().strftime('%Y%m%d')}.xlsx")

class DepartmentStatisticsReportView(View):
    """부서별 통계 리포트"""
    
    def get(self, request):
        # 부서별 통계 데이터
        employees = Employee.objects.all()
        
        generator = ExcelReportGenerator("부서별 통계")
        generator.add_title(
            "부서별 인원 및 현황 통계",
            f"생성일: {datetime.now().strftime('%Y년 %m월 %d일')}"
        )
        
        # 부서별 인원 현황
        dept_stats = {}
        for emp in employees:
            if emp.department not in dept_stats:
                dept_stats[emp.department] = {
                    'total': 0, 'Level_1': 0, 'Level_2': 0, 
                    'Level_3': 0, 'Level_4': 0
                }
            dept_stats[emp.department]['total'] += 1
            dept_stats[emp.department][emp.growth_level] += 1
        
        # 헤더
        headers = ['부서', '총 인원', 'Level 1', 'Level 2', 'Level 3', 'Level 4']
        generator.add_headers(headers)
        
        # 데이터
        for dept, stats in dept_stats.items():
            generator.add_data_row([
                dept,
                stats['total'],
                stats['Level_1'],
                stats['Level_2'],
                stats['Level_3'],
                stats['Level_4']
            ])
            
        return generator.save_to_response(f"부서통계_{datetime.now().strftime('%Y%m%d')}.xlsx")


class TurnoverRiskReportView(View):
    """이직 위험도 리포트 뷰"""
    
    def get(self, request):
        """이직 위험도 리포트 페이지 렌더링 또는 Excel 다운로드"""
        
        # Excel 다운로드 요청인지 확인
        if request.GET.get('format') == 'excel':
            return self.generate_excel_report(request)
        
        # HTML 페이지 렌더링
        try:
            # AIRISS API 서비스 사용
            airiss_api = AIRISSAPIService()
            
            # 위험 직원 데이터 가져오기
            risk_employees = airiss_api.get_risk_employees(limit=50)
            
            # 부서별 통계 가져오기
            department_stats = airiss_api.get_department_statistics()
            
            # KPI 통계 가져오기
            kpi_stats = airiss_api.get_kpi_stats()
            
            # AI 추천사항 가져오기
            ai_recommendations = airiss_api.get_ai_recommendations()
            
            # 위험도 레벨별 통계
            risk_summary = {
                'critical': sum(1 for e in risk_employees if e.get('risk_level') == 'CRITICAL'),
                'high': sum(1 for e in risk_employees if e.get('risk_level') == 'HIGH'),
                'medium': sum(1 for e in risk_employees if e.get('risk_level') == 'MEDIUM'),
                'low': sum(1 for e in risk_employees if e.get('risk_level') == 'LOW'),
                'total': len(risk_employees)
            }
            
            context = {
                'risk_employees': risk_employees[:20],  # 상위 20명만 표시
                'department_stats': department_stats,
                'risk_summary': risk_summary,
                'kpi_stats': kpi_stats,
                'ai_recommendations': ai_recommendations,
                'report_date': datetime.now()
            }
            
            # 템플릿이 있으면 렌더링, 없으면 JSON 응답
            try:
                return render(request, 'reports/turnover_risk_report.html', context)
            except:
                # 템플릿이 없는 경우 JSON 응답
                return JsonResponse({
                    'success': True,
                    'data': {
                        'risk_summary': risk_summary,
                        'high_risk_count': risk_summary.get('high', 0) + risk_summary.get('critical', 0),
                        'total_analyzed': risk_summary.get('total', 0),
                        'department_count': len(department_stats),
                        'report_generated': datetime.now().isoformat()
                    },
                    'message': 'Turnover risk report data retrieved successfully'
                })
                
        except Exception as e:
            logger.error(f"이직 위험도 리포트 조회 오류: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Failed to generate turnover risk report'
            }, status=500)
    
    def generate_excel_report(self, request):
        """Excel 형식의 이직 위험도 리포트 생성"""
        try:
            # AIRISS API 서비스 사용
            airiss_api = AIRISSAPIService()
            
            # 데이터 조회
            risk_employees = airiss_api.get_risk_employees(limit=100)
            department_stats = airiss_api.get_department_statistics()
            
            # Excel 생성
            generator = ExcelReportGenerator("이직 위험도 분석")
            generator.add_title(
                "이직 위험도 분석 리포트",
                f"생성일: {datetime.now().strftime('%Y년 %m월 %d일')}"
            )
            
            # 요약 정보
            generator.add_headers(['구분', '인원수', '비율'])
            
            total = len(risk_employees)
            critical_count = sum(1 for e in risk_employees if e.get('risk_level') == 'CRITICAL')
            high_count = sum(1 for e in risk_employees if e.get('risk_level') == 'HIGH')
            medium_count = sum(1 for e in risk_employees if e.get('risk_level') == 'MEDIUM')
            low_count = sum(1 for e in risk_employees if e.get('risk_level') == 'LOW')
            
            generator.add_data_row(['고위험(Critical)', critical_count, f"{(critical_count/total*100) if total > 0 else 0:.1f}%"])
            generator.add_data_row(['위험(High)', high_count, f"{(high_count/total*100) if total > 0 else 0:.1f}%"])
            generator.add_data_row(['주의(Medium)', medium_count, f"{(medium_count/total*100) if total > 0 else 0:.1f}%"])
            generator.add_data_row(['안정(Low)', low_count, f"{(low_count/total*100) if total > 0 else 0:.1f}%"])
            generator.add_data_row(['총계', total, '100.0%'])
            
            # 고위험 직원 상세
            generator.current_row += 2
            generator.add_headers(['사번', '이름', '부서', '직책', '위험도', '위험점수', '등급', '주요 위험 요인'])
            
            for emp in risk_employees[:50]:  # 상위 50명만
                key_factors = ', '.join(emp.get('key_factors', [])[:3]) if emp.get('key_factors') else ''
                generator.add_data_row([
                    emp.get('employee_id', ''),
                    emp.get('name', ''),
                    emp.get('department', ''),
                    emp.get('position', ''),
                    emp.get('risk_level', ''),
                    f"{emp.get('risk_score', 0):.2f}",
                    emp.get('grade', ''),
                    key_factors
                ])
            
            # 부서별 위험도 분석
            generator.current_row += 2
            generator.add_headers(['부서', '전체 인원', '고위험 인원', '위험 비율', '평균 점수', '추세'])
            
            for dept_name, stats in department_stats.items():
                generator.add_data_row([
                    dept_name,
                    stats.get('total_employees', 0),
                    stats.get('high_risk_count', 0),
                    f"{stats.get('risk_ratio', 0):.1f}%",
                    f"{stats.get('average_score', 0):.0f}",
                    stats.get('trend', 'stable')
                ])
            
            # 리포트 생성 이력 저장
            ReportGeneration.objects.create(
                template_id=1,  # 이직 위험도 템플릿
                generated_by=None,
                parameters_used={
                    'risk_threshold': request.GET.get('threshold', 0.6),
                    'limit': request.GET.get('limit', 100)
                },
                record_count=len(risk_employees),
                file_format='excel'
            )
            
            # 파일 응답
            filename = f"이직위험도분석_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            return generator.save_to_response(filename)
            
        except Exception as e:
            logger.error(f"Excel 리포트 생성 오류: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Failed to generate Excel report'
            }, status=500)
