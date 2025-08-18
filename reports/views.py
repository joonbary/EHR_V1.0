from django.views.generic import ListView, View
from permissions.mixins import HRPermissionMixin
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from compensation.models import EmployeeCompensation
from promotions.models import PromotionRequest
from .utils import ExcelReportGenerator
from .models import ReportTemplate, ReportGeneration
from datetime import datetime
from utils.file_manager import FileManager, ExcelFileHandler
import os
from django.conf import settings

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
