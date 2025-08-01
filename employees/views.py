from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Employee
from .forms import EmployeeForm
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import pandas as pd
from django.core.files.storage import default_storage
from django.conf import settings
import os
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.encoding import smart_str
import re
import json
from datetime import date
from utils.file_manager import ExcelFileHandler
from django.contrib.auth.decorators import login_required
from django.db.models import Q

class EmployeeListView(ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Employee.objects.all()
        
        # 검색어 가져오기
        search_query = self.request.GET.get('q', '')
        search_type = self.request.GET.get('search_type', 'all')
        
        if search_query:
            if search_type == 'name':
                queryset = queryset.filter(name__icontains=search_query)
            elif search_type == 'department':
                queryset = queryset.filter(department__icontains=search_query)
            elif search_type == 'position':
                queryset = queryset.filter(position__icontains=search_query)
            elif search_type == 'email':
                queryset = queryset.filter(email__icontains=search_query)
            else:  # all
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(department__icontains=search_query) |
                    Q(position__icontains=search_query) |
                    Q(email__icontains=search_query)
                )
        
        return queryset.order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 전체 직원 수
        context['total_count'] = Employee.objects.count()
        # 현재 쿼리셋의 수
        context['queryset_count'] = self.get_queryset().count()
        # 검색 관련 컨텍스트
        context['search_query'] = self.request.GET.get('q', '')
        context['search_type'] = self.request.GET.get('search_type', 'all')
        return context

class EmployeeDetailView(DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        emp = self.object
        today = date.today()
        # 근무기간 계산
        years = today.year - emp.hire_date.year
        months = today.month - emp.hire_date.month
        days = today.day - emp.hire_date.day
        if days < 0:
            months -= 1
        if months < 0:
            years -= 1
            months += 12
        work_period_text = f"{years}년 {months}개월"
        context['today'] = today
        context['work_period_text'] = work_period_text
        return context

class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, '직원이 성공적으로 등록되었습니다.')
        return super().form_valid(form)

class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, '직원 정보가 성공적으로 수정되었습니다.')
        return super().form_valid(form)

class EmployeeDeleteView(DeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '직원이 성공적으로 삭제되었습니다.')
        return super().delete(request, *args, **kwargs)

class BulkUploadView(View):
    template_name = 'employees/bulk_upload.html'
    sample_headers = ['이름', '부서', '직급', '입사일', '이메일', '전화번호']

    def get(self, request):
        # 샘플 템플릿 다운로드
        if 'download' in request.GET:
            df = pd.DataFrame(columns=self.sample_headers)
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=employee_bulk_upload_sample.xlsx'
            df.to_excel(response, index=False)
            return response
        return render(request, self.template_name, {'sample_headers': self.sample_headers})

    def post(self, request):
        # AJAX 요청인지 확인
        if request.headers.get('Content-Type') == 'application/json':
            return self.handle_ajax_save(request)
        
        # 일반 파일 업로드 (미리보기)
        return self.handle_preview(request)
    
    def handle_preview(self, request):
        """미리보기 처리 - DB 저장 없이 검증만"""
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': '파일을 선택해주세요.'}, status=400)
        
        excel_handler = ExcelFileHandler()
        
        try:
            # Excel 파일 처리 및 검증
            records, total_rows = excel_handler.process_employee_excel(file)
            df = pd.DataFrame(records)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'파일을 읽는 중 오류가 발생했습니다: {e}'}, status=400)

        # 미리보기(최대 10개)
        preview = df.head(10).to_dict(orient='records')
        
        # 검증 (DB 저장 없이)
        errors = []
        for idx, row in df.head(10).iterrows():
            row_errors = []
            name = row.get('이름', '')
            email = row.get('이메일', '')
            department = row.get('부서', '')
            position = row.get('직급', '')
            hire_date = row.get('입사일', '')
            phone = row.get('전화번호', '')
            # 필수값 체크 (NaN 포함)
            if pd.isna(name) or not str(name).strip():
                row_errors.append('이름 필수')
            if pd.isna(email) or not str(email).strip():
                row_errors.append('이메일 필수')
            if pd.isna(department) or not str(department).strip():
                row_errors.append('부서 필수')
            if pd.isna(position) or not str(position).strip():
                row_errors.append('직급 필수')
            if pd.isna(hire_date) or not str(hire_date).strip():
                row_errors.append('입사일 필수')
            # 이메일 중복 체크
            if email and not pd.isna(email) and Employee.objects.filter(email=str(email).strip()).exists():
                row_errors.append('이메일 중복')
            # 날짜 형식 체크 (YYYY-MM-DD) 및 유효성 검증
            if hire_date and not pd.isna(hire_date):
                hire_date_str = str(hire_date).strip()
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', hire_date_str):
                    row_errors.append('입사일 형식 오류(YYYY-MM-DD)')
                else:
                    # 실제 유효한 날짜인지 확인
                    try:
                        from datetime import datetime
                        datetime.strptime(hire_date_str, '%Y-%m-%d')
                    except ValueError:
                        row_errors.append('입사일 형식 오류(YYYY-MM-DD)')
            if row_errors:
                errors.append({'row': idx+2, 'name': str(name), 'email': str(email), 'errors': row_errors})
        return JsonResponse({
            'columns': df.columns.tolist(),
            'preview': preview,
            'errors': errors,
            'total_rows': len(df)
        })
    
    def handle_ajax_save(self, request):
        """최종 저장 처리"""
        try:
            data = json.loads(request.body)
            columns = data.get('columns', [])
            rows = data.get('rows', [])
        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 데이터 형식입니다.'}, status=400)
        
        # 검증 및 저장
        errors = []
        success_count = 0
        fail_count = 0
        created = []
        
        for idx, row in enumerate(rows):
            row_errors = []
            name = str(row.get('이름', '')).strip()
            email = str(row.get('이메일', '')).strip()
            department = str(row.get('부서', '')).strip()
            position = str(row.get('직급', '')).strip()
            hire_date = str(row.get('입사일', '')).strip()
            phone = str(row.get('전화번호', '')).strip()
            
            # 필수값 체크
            if not (name and email and department and position and hire_date):
                row_errors.append('필수값 누락')
            
            # 이메일 중복 체크
            if email and Employee.objects.filter(email=email).exists():
                row_errors.append('이메일 중복')
            
            # 날짜 형식 체크 (YYYY-MM-DD)
            if hire_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', hire_date):
                row_errors.append('입사일 형식 오류(YYYY-MM-DD)')
            
            if row_errors:
                errors.append({'row': idx+2, 'name': name, 'email': email, 'errors': row_errors})
                fail_count += 1
                continue
            
            # 실제 저장
            try:
                Employee.objects.create(
                    name=name,
                    department=department,
                    position=position,
                    hire_date=hire_date,
                    email=email,
                    phone=phone
                )
                success_count += 1
                created.append(email)
            except Exception as e:
                errors.append({'row': idx+2, 'name': name, 'email': email, 'errors': [str(e)]})
                fail_count += 1
        
        return JsonResponse({
            'success_count': success_count,
            'fail_count': fail_count,
            'errors': errors,
            'created': created
        })

def download_template(request):
    import pandas as pd
    from io import BytesIO
    headers = ['이름', '이메일', '부서', '직급', '입사일', '전화번호']
    sample = [
        ['홍길동', 'hong@okgroup.com', '인사', '사원', '2024-01-01', '01012345678'],
        ['김영희', 'kim@okgroup.com', '총무', '대리', '2023-12-01', '01087654321'],
    ]
    df = pd.DataFrame(sample, columns=headers)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('직원업로드_샘플.xlsx')
    return response

def organization_chart(request):
    """D3.js 기반 조직도 페이지"""
    return render(request, 'employees/organization_chart.html')

def hierarchy_organization_view(request):
    """계층별 조직도 페이지"""
    return render(request, 'employees/hierarchy_organization.html')

def hierarchy_organization_api(request):
    """계층별 조직 데이터 API"""
    level = request.GET.get('level', 'all')  # executive, department, team, member
    department = request.GET.get('department', '')
    parent_id = request.GET.get('parent_id', '')
    
    try:
        if level == 'executive':
            # 임원급 (부사장 이상)
            executives = Employee.objects.filter(
                new_position__in=['회장', '부사장', '사장', '전무', '상무'],
                employment_status='재직'
            ).select_related('manager')
            
            data = []
            for exec in executives:
                subordinates = exec.get_subordinates()
                data.append({
                    'id': exec.id,
                    'name': exec.name,
                    'position': exec.new_position,
                    'department': exec.department,
                    'job_type': exec.job_type,
                    'level': exec.growth_level,
                    'age': calculate_age(exec.hire_date) if exec.hire_date else None,
                    'email': exec.email,
                    'phone': exec.phone,
                    'profile_image': exec.profile_image.url if exec.profile_image else None,
                    'subordinate_count': subordinates.count(),
                    'subordinate_departments': list(subordinates.values_list('department', flat=True).distinct()),
                    'manager': exec.manager.name if exec.manager else None
                })
        
        elif level == 'department':
            # 부서장급 (본부장, 부장급)
            dept_heads = Employee.objects.filter(
                new_position__in=['본부장', '부장'],
                employment_status='재직'
            ).select_related('manager')
            
            data = []
            for dept in dept_heads:
                subordinates = dept.get_subordinates()
                teams = subordinates.filter(new_position__in=['팀장', '지점장']).count()
                
                data.append({
                    'id': dept.id,
                    'name': dept.name,
                    'position': dept.new_position,
                    'department': dept.department,
                    'job_type': dept.job_type,
                    'level': dept.growth_level,
                    'age': calculate_age(dept.hire_date) if dept.hire_date else None,
                    'email': dept.email,
                    'phone': dept.phone,
                    'profile_image': dept.profile_image.url if dept.profile_image else None,
                    'total_members': subordinates.count(),
                    'team_count': teams,
                    'manager': dept.manager.name if dept.manager else None,
                    'organization_name': f"{dept.department} {dept.new_position}"
                })
        
        elif level == 'team':
            # 팀장급
            team_heads = Employee.objects.filter(
                new_position__in=['팀장', '지점장'],
                employment_status='재직'
            ).select_related('manager')
            
            if department:
                team_heads = team_heads.filter(department=department)
            
            data = []
            for team in team_heads:
                subordinates = team.get_subordinates()
                
                data.append({
                    'id': team.id,
                    'name': team.name,
                    'position': team.new_position,
                    'department': team.department,
                    'job_type': team.job_type,
                    'level': team.growth_level,
                    'age': calculate_age(team.hire_date) if team.hire_date else None,
                    'email': team.email,
                    'phone': team.phone,
                    'profile_image': team.profile_image.url if team.profile_image else None,
                    'team_members': subordinates.count(),
                    'manager': team.manager.name if team.manager else None,
                    'organization_name': f"{team.department} {team.job_type}팀",
                    'members': [
                        {
                            'id': member.id,
                            'name': member.name,
                            'position': member.new_position,
                            'level': member.growth_level,
                            'job_type': member.job_type
                        } for member in subordinates
                    ]
                })
        
        elif level == 'member':
            # 특정 상사의 직속 부하들
            if parent_id:
                members = Employee.objects.filter(
                    manager_id=parent_id,
                    employment_status='재직'
                ).select_related('manager')
            else:
                # 일반 직원들 (팀장급 제외)
                members = Employee.objects.filter(
                    new_position__in=['사원', '선임', '주임', '대리', '과장', '차장'],
                    employment_status='재직'
                ).select_related('manager')
                
                if department:
                    members = members.filter(department=department)
            
            data = []
            for member in members:
                data.append({
                    'id': member.id,
                    'name': member.name,
                    'position': member.new_position,
                    'department': member.department,
                    'job_type': member.job_type,
                    'level': member.growth_level,
                    'age': calculate_age(member.hire_date) if member.hire_date else None,
                    'email': member.email,
                    'phone': member.phone,
                    'profile_image': member.profile_image.url if member.profile_image else None,
                    'manager': member.manager.name if member.manager else None,
                    'hire_date': member.hire_date.strftime('%Y-%m-%d') if member.hire_date else None
                })
        
        else:  # level == 'all'
            # 전체 조직 요약
            data = {
                'executives': Employee.objects.filter(
                    new_position__in=['회장', '부사장', '사장', '전무', '상무'],
                    employment_status='재직'
                ).count(),
                'departments': Employee.objects.filter(
                    new_position__in=['본부장', '부장'],
                    employment_status='재직'
                ).count(),
                'teams': Employee.objects.filter(
                    new_position__in=['팀장', '지점장'],
                    employment_status='재직'
                ).count(),
                'members': Employee.objects.filter(
                    new_position__in=['사원', '선임', '주임', '대리', '과장', '차장'],
                    employment_status='재직'
                ).count(),
                'total': Employee.objects.filter(employment_status='재직').count(),
                'departments_list': list(Employee.objects.filter(
                    employment_status='재직'
                ).values_list('department', flat=True).distinct())
            }
        
        return JsonResponse({
            'success': True,
            'level': level,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def calculate_age(hire_date):
    """입사일로부터 근무 연수 계산"""
    from datetime import date
    today = date.today()
    return today.year - hire_date.year

def organization_data_api(request):
    """조직도 데이터 JSON API"""
    def build_tree(manager_id=None, processed=None):
        if processed is None:
            processed = set()
        
        # 순환 참조 방지
        if manager_id in processed:
            return []
        
        processed.add(manager_id)
        
        # 해당 관리자의 직속 부하들 조회
        if manager_id is None:
            # 최상위 관리자들 (manager가 None인 직원들)
            employees = Employee.objects.filter(
                manager__isnull=True,
                employment_status='재직'
            ).order_by('department', 'growth_level')
        else:
            employees = Employee.objects.filter(
                manager_id=manager_id,
                employment_status='재직'
            ).order_by('department', 'growth_level')
        
        nodes = []
        for emp in employees:
            node = {
                'id': emp.id,
                'name': emp.name,
                'position': emp.new_position,
                'department': emp.department,
                'job_type': emp.job_type,
                'level': emp.growth_level,
                'email': emp.email,
                'phone': emp.phone,
                'profile_image': emp.profile_image.url if emp.profile_image else None,
                'children': build_tree(emp.id, processed.copy())
            }
            nodes.append(node)
        
        return nodes
    
    try:
        org_data = build_tree()
        return JsonResponse({
            'success': True,
            'data': org_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# HR Dashboard View
def hr_dashboard_view(request):
    """HR 인력현황 대시보드 뷰"""
    return render(request, 'hr/dashboard.html')


def outsourced_dashboard_view(request):
    """외주인력 현황관리 대시보드 뷰"""
    return render(request, 'hr/outsourced_dashboard.html')


def workforce_dashboard_view(request):
    """주간 인력현황 대시보드"""
    return render(request, 'hr/workforce_dashboard.html')


def monthly_workforce_view(request):
    """월간 인력현황 대시보드"""
    return render(request, 'hr/monthly_workforce.html')


def full_workforce_view(request):
    """전체 인력현황 대시보드"""
    return render(request, 'hr/full_workforce.html')


def overseas_workforce_view(request):
    """월간 해외인력현황 뷰"""
    return render(request, 'hr/overseas_workforce.html')
