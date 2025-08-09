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
    template_name = 'employees/employee_list_revolutionary.html'
    context_object_name = 'employees'
    paginate_by = 20
    
    def get_queryset(self):
        # Optimize query with select_related and prefetch_related to avoid N+1 problem
        queryset = Employee.objects.select_related(
            'user',
            'manager',
            'job_role',
            'job_role__job_type',
            'job_role__job_type__category'
        ).prefetch_related(
            'subordinates',
            'certifications',
            'trainings'
        )
        
        # 검색어 가져오기
        search_query = self.request.GET.get('q', '')
        search_type = self.request.GET.get('search_type', 'all')
        
        # 필터링 파라미터들
        company = self.request.GET.get('company', '')
        headquarters1 = self.request.GET.get('headquarters1', '')
        position = self.request.GET.get('position', '')
        employment_status = self.request.GET.get('employment_status', '')
        
        # 검색 필터링
        if search_query:
            if search_type == 'name':
                queryset = queryset.filter(name__icontains=search_query)
            elif search_type == 'email':
                queryset = queryset.filter(email__icontains=search_query)
            elif search_type == 'department':
                queryset = queryset.filter(
                    Q(department__icontains=search_query) |
                    Q(final_department__icontains=search_query) |
                    Q(headquarters1__icontains=search_query) |
                    Q(headquarters2__icontains=search_query)
                )
            elif search_type == 'position':
                queryset = queryset.filter(
                    Q(position__icontains=search_query) |
                    Q(current_position__icontains=search_query) |
                    Q(new_position__icontains=search_query)
                )
            else:  # all
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(email__icontains=search_query) |
                    Q(department__icontains=search_query) |
                    Q(final_department__icontains=search_query) |
                    Q(headquarters1__icontains=search_query) |
                    Q(headquarters2__icontains=search_query) |
                    Q(position__icontains=search_query) |
                    Q(current_position__icontains=search_query) |
                    Q(new_position__icontains=search_query) |
                    Q(responsibility__icontains=search_query) |
                    Q(job_type__icontains=search_query)
                )
        
        # 회사 필터링
        if company:
            queryset = queryset.filter(company=company)
        
        # 본부 필터링
        if headquarters1:
            queryset = queryset.filter(headquarters1__icontains=headquarters1)
        
        # 직급 필터링
        if position:
            queryset = queryset.filter(
                Q(current_position=position) |
                Q(new_position=position) |
                Q(position=position)
            )
        
        # 재직상태 필터링
        if employment_status:
            queryset = queryset.filter(employment_status=employment_status)
        
        # 정렬 (회사 > 본부1 > 최종소속 > 직급 > 이름 순)
        return queryset.order_by('company', 'headquarters1', 'final_department', 'current_position', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 전체 직원 수
        context['total_count'] = Employee.objects.count()
        # 현재 쿼리셋의 수
        context['queryset_count'] = self.get_queryset().count()
        
        # 검색 관련 컨텍스트
        context['search_query'] = self.request.GET.get('q', '')
        context['search_type'] = self.request.GET.get('search_type', 'all')
        
        # 필터 관련 컨텍스트
        context['filter_company'] = self.request.GET.get('company', '')
        context['filter_headquarters1'] = self.request.GET.get('headquarters1', '')
        context['filter_position'] = self.request.GET.get('position', '')
        context['filter_employment_status'] = self.request.GET.get('employment_status', '')
        
        # 필터 옵션용 데이터
        context['companies'] = Employee.objects.exclude(company__isnull=True).exclude(company='').values_list('company', flat=True).distinct().order_by('company')
        context['headquarters1_list'] = Employee.objects.exclude(headquarters1__isnull=True).exclude(headquarters1='').values_list('headquarters1', flat=True).distinct().order_by('headquarters1')
        context['positions'] = Employee.objects.exclude(current_position__isnull=True).exclude(current_position='').values_list('current_position', flat=True).distinct().order_by('current_position')
        context['employment_statuses'] = Employee.objects.exclude(employment_status__isnull=True).exclude(employment_status='').values_list('employment_status', flat=True).distinct().order_by('employment_status')
        
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
        
        # 전체 데이터
        full_data = df.to_dict(orient='records')
        
        # 검증 (전체 데이터에 대해, 미리보기는 10개까지만 오류 표시)
        errors = []
        for idx, row in df.iterrows():
            if idx >= 10:  # 10개 이후는 검증만 하고 오류는 표시 안함
                break
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
            'full_data': full_data,  # 전체 데이터 추가
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
            
            # 기본 필수 필드
            name = str(row.get('이름', '')).strip()
            email = str(row.get('이메일', '')).strip()
            hire_date = str(row.get('입사일', '')).strip()
            
            # 선택 필드들
            phone = str(row.get('전화번호', '') or row.get('연락처', '')).strip()
            company = str(row.get('회사', '')).strip()
            headquarters1 = str(row.get('본부1', '')).strip()
            headquarters2 = str(row.get('본부2', '')).strip()
            final_department = str(row.get('최종소속', '') or row.get('부서', '')).strip()
            current_position = str(row.get('직급', '')).strip()
            responsibility = str(row.get('직책', '')).strip()
            gender = str(row.get('성별', '')).strip()
            age = row.get('나이', None)
            employment_status = str(row.get('재직상태', '재직')).strip()
            job_group = str(row.get('직군', '') or row.get('직군/계열', '')).strip()
            job_type = str(row.get('직종', '')).strip()
            
            # 필수값 체크
            if not name:
                row_errors.append('이름 필수')
            if not email:
                row_errors.append('이메일 필수')
            if not hire_date:
                row_errors.append('입사일 필수')
            
            # 이메일 중복 체크
            if email and Employee.objects.filter(email=email).exists():
                row_errors.append('이메일 중복')
            
            # 날짜 형식 체크 (YYYY-MM-DD)
            if hire_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', hire_date):
                row_errors.append('입사일 형식 오류(YYYY-MM-DD)')
            
            # 성별 값 검증
            if gender and gender.upper() not in ['M', 'F', '남', '여', '남성', '여성']:
                row_errors.append('성별 형식 오류(M/F 또는 남/여)')
            
            # 나이 검증
            if age:
                try:
                    age = int(age)
                    if age < 18 or age > 70:
                        row_errors.append('나이는 18-70 사이여야 합니다')
                except (ValueError, TypeError):
                    row_errors.append('나이는 숫자여야 합니다')
                    age = None
            
            if row_errors:
                errors.append({'row': idx+2, 'name': name, 'email': email, 'errors': row_errors})
                fail_count += 1
                continue
            
            # 성별 값 변환
            if gender:
                if gender.upper() in ['M', '남', '남성']:
                    gender = 'M'
                elif gender.upper() in ['F', '여', '여성']:
                    gender = 'F'
                else:
                    gender = ''
            
            # 실제 저장
            try:
                employee_data = {
                    'name': name,
                    'email': email,
                    'hire_date': hire_date,
                    'phone': phone,
                    'company': company if company else None,
                    'headquarters1': headquarters1 if headquarters1 else None,
                    'headquarters2': headquarters2 if headquarters2 else None,
                    'final_department': final_department if final_department else None,
                    'current_position': current_position if current_position else None,
                    'responsibility': responsibility if responsibility else None,
                    'gender': gender if gender else None,
                    'age': age,
                    'employment_status': employment_status,
                    'job_group': job_group if job_group else 'Non-PL',
                    'job_type': job_type if job_type else '경영관리',
                }
                
                # 기존 필드도 호환성을 위해 설정
                employee_data['department'] = final_department if final_department else 'OPERATIONS'
                employee_data['position'] = current_position if current_position else 'STAFF'
                employee_data['new_position'] = current_position if current_position else '사원'
                
                Employee.objects.create(**employee_data)
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
    
    # 확장된 헤더 (필수 + 선택 필드)
    headers = [
        '이름', '이메일', '입사일',  # 필수 필드
        '전화번호', '회사', '본부1', '본부2', '최종소속', '직급', '직책',  # 기본 선택 필드
        '성별', '나이', '재직상태', '직군/계열', '직종'  # 추가 선택 필드
    ]
    
    # 샘플 데이터 (3명 분량)
    sample = [
        ['홍길동', 'hong@ok.co.kr', '2024-01-01', '010-1234-5678', 'OK', 'IT본부', 'AI개발본부', '개발1팀', '대리', '팀장', 'M', '35', '재직', 'Non-PL', 'IT개발'],
        ['김영희', 'kim@oci.co.kr', '2023-12-01', '010-8765-4321', 'OCI', '기획본부', '전략기획본부', '기획팀', '과장', '주임', 'F', '38', '재직', 'Non-PL', '경영관리'],
        ['박민수', 'park@okds.co.kr', '2024-03-15', '010-5555-7777', 'OKDS', '영업본부', '리테일영업본부', '고객지원팀', '사원', '', 'M', '28', '재직', 'PL', '고객지원'],
    ]
    
    df = pd.DataFrame(sample, columns=headers)
    
    # 설명용 시트 추가
    with pd.ExcelWriter(BytesIO(), engine='openpyxl') as writer:
        # 메인 데이터 시트
        df.to_excel(writer, sheet_name='직원데이터', index=False)
        
        # 설명 시트
        help_data = [
            ['컬럼명', '필수여부', '설명', '예시값'],
            ['이름', 'O', '직원 성명 (한글/영문)', '홍길동'],
            ['이메일', 'O', '회사 이메일 주소 (중복불가)', 'hong@ok.co.kr'],
            ['입사일', 'O', '입사일자 (YYYY-MM-DD 형식)', '2024-01-01'],
            ['전화번호', 'X', '휴대폰 번호', '010-1234-5678'],
            ['회사', 'X', '소속 회사', 'OK, OCI, OC, OFI, OKDS, OKH, ON, OKIP, OT, OKV, EX'],
            ['본부1', 'X', '1차 본부', 'IT본부, 기획본부, 영업본부'],
            ['본부2', 'X', '2차 본부', 'AI개발본부, 전략기획본부'],
            ['최종소속', 'X', '최종 소속 부서/팀', '개발1팀, 기획팀'],
            ['직급', 'X', '직급', '사원, 선임, 주임, 대리, 과장, 차장, 부부장, 부장, 팀장, 지점장, 본부장'],
            ['직책', 'X', '직책/역할', '팀장, 주임, 선임 등'],
            ['성별', 'X', '성별', 'M(남성), F(여성), 남, 여, 남성, 여성'],
            ['나이', 'X', '나이 (숫자)', '35'],
            ['재직상태', 'X', '현재 재직 상태', '재직, 휴직, 파견, 퇴직'],
            ['직군/계열', 'X', '직군 분류', 'PL, Non-PL'],
            ['직종', 'X', '직종 분류', 'IT개발, IT기획, IT운영, 경영관리, 기업영업, 기업금융, 리테일금융, 투자금융, 고객지원'],
        ]
        
        help_df = pd.DataFrame(help_data[1:], columns=help_data[0])
        help_df.to_excel(writer, sheet_name='입력가이드', index=False)
        
        # BytesIO 객체 생성
        output = BytesIO()
        writer.book.save(output)
        output.seek(0)
    
    response = HttpResponse(
        output.read(), 
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('OK금융그룹_직원업로드_템플릿.xlsx')
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
