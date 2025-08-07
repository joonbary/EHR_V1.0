from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.generic import DetailView, UpdateView
# from django.contrib.auth.mixins import LoginRequiredMixin  # Removed
from django.db.models import Avg, Count, Q, Sum
import json
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation, EvaluationPeriod
from compensation.models import EmployeeCompensation
from promotions.models import PromotionRequest, JobTransfer
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.db.models import Sum, Avg
import calendar
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils import timezone
from .forms import ProfileUpdateForm, CustomPasswordChangeForm
import os
from utils.file_manager import FileManager

def my_dashboard(request):
    """직원 개인 대시보드"""
    # employee = get_object_or_404(Employee, user=request.user)  # Authentication removed
    employee = Employee.objects.first()  # Fallback for testing
    # 내 정보, 평가, 보상, 승진 이력 등 요약
    return render(request, 'selfservice/dashboard.html', {
        'employee': employee,
    })

class ProfileUpdateView(SuccessMessageMixin, UpdateView):
    """프로필 수정"""
    model = Employee
    form_class = ProfileUpdateForm
    template_name = 'selfservice/profile_update.html'
    success_message = "프로필이 성공적으로 업데이트되었습니다."
    success_url = reverse_lazy('selfservice:dashboard')
    
    def get_object(self):
        # return self.request.user.employee  # Authentication removed
        return Employee.objects.first()  # Fallback for testing
    
    def form_valid(self, form):
        # 프로필 이미지 처리
        if 'profile_image' in form.changed_data and form.cleaned_data.get('profile_image'):
            file_manager = FileManager()
            
            # 기존 이미지 삭제
            old_image = self.get_object().profile_image
            if old_image:
                file_manager.delete_file(old_image.name)
            
            # 새 이미지 저장
            try:
                new_image_path = file_manager.save_profile_image(
                    form.cleaned_data['profile_image'],
                    self.get_object().employee_number
                )
                form.instance.profile_image = new_image_path
            except ValueError as e:
                form.add_error('profile_image', str(e))
                return self.form_invalid(form)
        
        # 변경 이력 저장 (간단한 로그)
        self.log_profile_change(form.changed_data)
        
        return super().form_valid(form)
    
    def log_profile_change(self, changed_fields):
        """프로필 변경 이력 기록 (간단한 버전)"""
        print(f"프로필 변경: {changed_fields} - {timezone.now()}")

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """비밀번호 변경"""
    form_class = CustomPasswordChangeForm
    template_name = 'selfservice/password_change.html'
    success_message = "비밀번호가 성공적으로 변경되었습니다."
    success_url = reverse_lazy('selfservice:dashboard')
    
    def form_valid(self, form):
        # 비밀번호 변경 이력 기록 (간단한 로그)
        self.log_password_change()
        return super().form_valid(form)
    
    def log_password_change(self):
        """비밀번호 변경 이력 기록 (간단한 버전)"""
        ip_address = self.get_client_ip()
        print(f"비밀번호 변경: {self.request.user.username} - {ip_address} - {timezone.now()}")
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

def profile_update(request):
    """프로필 수정 (기존 함수형 뷰 - 호환성 유지)"""
    view = ProfileUpdateView()
    return view.get(request)

def password_change(request):
    """비밀번호 변경 (기존 함수형 뷰 - 호환성 유지)"""
    view = CustomPasswordChangeView()
    return view.get(request)

class EvaluationHistoryView(DetailView):
    """평가 이력 상세 조회"""
    template_name = 'selfservice/evaluation_history.html'
    
    def get(self, request):
        # employee = get_object_or_404(Employee, user=request.user)  # Authentication removed
    employee = Employee.objects.first()  # Fallback for testing
        
        # 최근 5년간 평가 데이터
        evaluations = ComprehensiveEvaluation.objects.filter(
            employee=employee
        ).order_by('-evaluation_period__year')[:5]
        
        # 차트 데이터 준비
        chart_data = {
            'years': [e.evaluation_period.year for e in evaluations],
            'grades': [e.final_grade for e in evaluations if e.final_grade],
            'contribution_scores': [float(e.contribution_evaluation.contribution_score) if e.contribution_evaluation else 0 for e in evaluations],
            'expertise_scores': [float(e.expertise_evaluation.total_score) if e.expertise_evaluation else 0 for e in evaluations],
            'impact_scores': [float(e.impact_evaluation.total_score) if e.impact_evaluation else 0 for e in evaluations],
        }
        
        # 동료 대비 위치 (백분위)
        peer_comparison = self.calculate_peer_percentile(employee)
        
        # 성장 추이 분석
        growth_analysis = self.analyze_growth_trend(evaluations)
        
        context = {
            'employee': employee,
            'evaluations': evaluations,
            'chart_data': json.dumps(chart_data),
            'peer_comparison': peer_comparison,
            'growth_analysis': growth_analysis,
            'current_evaluation': evaluations.first() if evaluations else None,
        }
        
        return render(request, self.template_name, context)
    
    def calculate_peer_percentile(self, employee):
        """동료 대비 백분위 계산"""
        # 같은 레벨의 직원들 조회
        same_level_employees = Employee.objects.filter(
            growth_level=employee.growth_level,
            department=employee.department,
            employment_status='ACTIVE'
        )
        
        # 최근 평가 데이터 조회
        latest_period = EvaluationPeriod.objects.filter(
            status='COMPLETED'
        ).order_by('-year').first()
        
        if not latest_period:
            return {
                'percentile': 50,
                'total_peers': 0,
                'rank': 0
            }
        
        # 동료들의 최근 평가 점수
        peer_scores = []
        for peer in same_level_employees:
            eval = ComprehensiveEvaluation.objects.filter(
                employee=peer,
                evaluation_period=latest_period
            ).first()
            if eval and eval.final_grade:
                # 등급을 숫자로 변환
                grade_map = {'S': 7, 'A+': 6, 'A': 5, 'B+': 4, 'B': 3, 'C': 2, 'D': 1}
                peer_scores.append(grade_map.get(eval.final_grade, 0))
        
        if not peer_scores:
            return {
                'percentile': 50,
                'total_peers': 0,
                'rank': 0
            }
        
        # 내 점수
        my_eval = ComprehensiveEvaluation.objects.filter(
            employee=employee,
            evaluation_period=latest_period
        ).first()
        
        if not my_eval or not my_eval.final_grade:
            return {
                'percentile': 50,
                'total_peers': len(peer_scores),
                'rank': 0
            }
        
        grade_map = {'S': 7, 'A+': 6, 'A': 5, 'B+': 4, 'B': 3, 'C': 2, 'D': 1}
        my_score = grade_map.get(my_eval.final_grade, 0)
        
        # 백분위 계산
        peer_scores.append(my_score)
        peer_scores.sort(reverse=True)
        my_rank = peer_scores.index(my_score) + 1
        percentile = ((len(peer_scores) - my_rank) / len(peer_scores)) * 100
        
        return {
            'percentile': round(percentile, 1),
            'total_peers': len(peer_scores) - 1,
            'rank': my_rank
        }
    
    def analyze_growth_trend(self, evaluations):
        """성장 추이 분석"""
        if len(evaluations) < 2:
            return {
                'trend': '평가 데이터 부족',
                'improvement': 0,
                'consistency': '평가 데이터 부족'
            }
        
        # 등급을 숫자로 변환
        grade_map = {'S': 7, 'A+': 6, 'A': 5, 'B+': 4, 'B': 3, 'C': 2, 'D': 1}
        grades = [grade_map.get(e.final_grade, 0) for e in evaluations if e.final_grade]
        
        if len(grades) < 2:
            return {
                'trend': '평가 데이터 부족',
                'improvement': 0,
                'consistency': '평가 데이터 부족'
            }
        
        # 개선도 계산
        improvement = grades[0] - grades[-1]
        
        # 일관성 계산 (표준편차)
        if len(grades) > 1:
            mean_grade = sum(grades) / len(grades)
            variance = sum((g - mean_grade) ** 2 for g in grades) / len(grades)
            consistency_score = variance ** 0.5
        else:
            consistency_score = 0
        
        # 트렌드 판단
        if improvement > 0.5:
            trend = "상승"
        elif improvement < -0.5:
            trend = "하락"
        else:
            trend = "안정"
        
        # 일관성 판단
        if consistency_score < 0.5:
            consistency = "매우 안정적"
        elif consistency_score < 1.0:
            consistency = "안정적"
        else:
            consistency = "변동적"
        
        return {
            'trend': trend,
            'improvement': round(improvement, 1),
            'consistency': consistency
        }

def evaluation_history(request):
    """평가 이력 조회 (기존 함수형 뷰 - 호환성 유지)"""
    view = EvaluationHistoryView()
    return view.get(request)

class CompensationStatementView(DetailView):
    """보상 명세서 조회"""
    template_name = 'selfservice/compensation_statement.html'
    
    def get(self, request, year=None, month=None):
        # employee = get_object_or_404(Employee, user=request.user)  # Authentication removed
    employee = Employee.objects.first()  # Fallback for testing
        # 연도/월 파라미터 처리
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        else:
            year = int(year)
            month = int(month)
        # 현재 보상 정보 (해당 연월)
        current_compensation = EmployeeCompensation.objects.filter(
            employee=employee, year=year, month=month
        ).first()
        # 월별 상세 내역
        monthly_breakdown = self.calculate_monthly_breakdown(
            employee, year, month, current_compensation
        )
        # 연간 총 보상 요약
        annual_summary = self.calculate_annual_summary(employee, year)
        # 최근 12개월 추이
        monthly_trend = self.get_monthly_trend(employee, year)
        # 동료 대비 보상 수준
        peer_comparison = self.compare_with_peers(employee, year)
        context = {
            'employee': employee,
            'year': year,
            'month': month,
            'current_compensation': current_compensation,
            'monthly_breakdown': monthly_breakdown,
            'annual_summary': annual_summary,
            'monthly_trend': monthly_trend,
            'peer_comparison': peer_comparison,
            'months': [(i, f"{i}") for i in range(1, 13)],
            'years': list(range(datetime.now().year - 2, datetime.now().year + 1)),
        }
        return render(request, self.template_name, context)
    
    def calculate_monthly_breakdown(self, employee, year, month, comp):
        """월별 상세 보상 계산"""
        if not comp:
            return None
        # 기본 월급여
        monthly_base = float(comp.base_salary) / 12
        monthly_ot = float(comp.fixed_overtime) / 12
        monthly_capability = float(comp.competency_pay) / 12
        monthly_position = float(comp.position_allowance) / 12 if comp.position_allowance else 0
        # PI는 연 1회 지급 (12월)
        pi_amount = float(comp.pi_amount) if int(month) == 12 else 0
        # 추석상여는 9월 지급 (예시)
        chuseok_bonus = 0  # 실제 필드가 없으므로 0 처리
        # 세금 계산 (간소화)
        gross_total = monthly_base + monthly_ot + monthly_capability + monthly_position + pi_amount + chuseok_bonus
        income_tax = gross_total * 0.15
        local_tax = income_tax * 0.1
        pension = gross_total * 0.045
        health = gross_total * 0.0335
        employment = gross_total * 0.008
        total_deductions = income_tax + local_tax + pension + health + employment
        net_pay = gross_total - total_deductions
        return {
            'base_salary': monthly_base,
            'fixed_ot': monthly_ot,
            'capability_pay': monthly_capability,
            'position_pay': monthly_position,
            'pi_amount': pi_amount,
            'chuseok_bonus': chuseok_bonus,
            'gross_total': gross_total,
            'income_tax': income_tax,
            'local_tax': local_tax,
            'pension': pension,
            'health': health,
            'employment': employment,
            'total_deductions': total_deductions,
            'net_pay': net_pay,
        }
    def calculate_annual_summary(self, employee, year):
        """연간 총 보상 요약"""
        qs = EmployeeCompensation.objects.filter(employee=employee, year=year)
        annual_salary = sum([float(c.base_salary) for c in qs])
        total_pi = sum([float(c.pi_amount) for c in qs])
        other_compensation = sum([float(c.position_allowance or 0) + float(c.competency_pay) + float(c.fixed_overtime) for c in qs])
        total_compensation = sum([float(c.total_compensation) for c in qs if c.total_compensation])
        return {
            'annual_salary': annual_salary,
            'total_pi': total_pi,
            'other_compensation': other_compensation,
            'total_compensation': total_compensation,
        }
    def get_monthly_trend(self, employee, year):
        """최근 12개월 실수령액/특별보상 추이"""
        labels = []
        net_pay = []
        special_pay = []
        for m in range(1, 13):
            comp = EmployeeCompensation.objects.filter(employee=employee, year=year, month=m).first()
            if comp:
                breakdown = self.calculate_monthly_breakdown(employee, year, m, comp)
                labels.append(f"{m}월")
                net_pay.append(int(breakdown['net_pay']))
                special_pay.append(int(breakdown['pi_amount']))
            else:
                labels.append(f"{m}월")
                net_pay.append(0)
                special_pay.append(0)
        return {'labels': labels, 'net_pay': net_pay, 'special_pay': special_pay}
    def compare_with_peers(self, employee, year):
        """동일 레벨/직종 평균과 비교"""
        my_salary = EmployeeCompensation.objects.filter(employee=employee, year=year).aggregate(s=Sum('base_salary'))['s'] or 0
        peers = Employee.objects.filter(growth_level=employee.growth_level, job_type=employee.job_type).exclude(id=employee.id)
        peer_ids = [p.id for p in peers]
        avg_salary = EmployeeCompensation.objects.filter(employee_id__in=peer_ids, year=year).aggregate(s=Avg('base_salary'))['s'] or 0
        # 내 연봉이 상위 몇 %인지 계산
        all_salaries = list(EmployeeCompensation.objects.filter(year=year).values_list('base_salary', flat=True))
        all_salaries = sorted([float(s) for s in all_salaries if s is not None], reverse=True)
        my_rank = all_salaries.index(float(my_salary)) + 1 if my_salary in all_salaries else len(all_salaries)
        percentile = ((len(all_salaries) - my_rank) / len(all_salaries)) * 100 if all_salaries else 0
        return {
            'percentile': round(percentile, 1),
            'my_salary': my_salary,
            'avg_salary': avg_salary,
        }

def compensation_statement(request, year=None, month=None):
    view = CompensationStatementView()
    return view.get(request, year, month)

def career_path(request):
    """경력 개발/승진 경로"""
    # employee = get_object_or_404(Employee, user=request.user)  # Authentication removed
    employee = Employee.objects.first()  # Fallback for testing
    promotion_history = PromotionRequest.objects.filter(employee=employee, status='APPROVED').order_by('-final_decision_date')
    return render(request, 'selfservice/career_path.html', {
        'employee': employee,
        'promotion_history': promotion_history,
    })
