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

class EmployeeListView(ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10

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
        
        ext = os.path.splitext(file.name)[-1].lower()
        try:
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file, dtype=str)
            elif ext == '.csv':
                df = pd.read_csv(file, dtype=str)
            else:
                return JsonResponse({'error': '지원하지 않는 파일 형식입니다.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'파일을 읽는 중 오류가 발생했습니다: {e}'}, status=400)

        # 컬럼명 체크
        missing_cols = [col for col in self.sample_headers if col not in df.columns]
        if missing_cols:
            return JsonResponse({'error': f'다음 필수 컬럼이 누락되었습니다: {", ".join(missing_cols)}'}, status=400)

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
