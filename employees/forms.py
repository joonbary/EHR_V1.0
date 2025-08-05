from django import forms
from .models import Employee
from datetime import date

class EmployeeForm(forms.ModelForm):
    """직원 등록/수정 폼 - 확장된 필드들 포함"""
    
    class Meta:
        model = Employee
        fields = [
            # 기본 정보
            'name', 'email', 'phone', 'gender', 'birth_date', 'age',
            # 조직 정보  
            'company', 'headquarters1', 'headquarters2', 'final_department', 'department',
            # 인사 정보
            'current_position', 'new_position', 'responsibility', 'job_group', 'job_type', 
            'growth_level', 'hire_date', 'employment_status',
            # 추가 정보
            'address', 'emergency_contact', 'emergency_phone', 'education', 'marital_status'
        ]
        
        widgets = {
            # 기본 정보
            'name': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '직원 이름을 입력하세요',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input', 
                'placeholder': '이메일을 입력하세요',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '010-1234-5678'
            }),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-input', 
                'type': 'date'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-input', 
                'min': '18', 
                'max': '70',
                'placeholder': '나이'
            }),
            
            # 조직 정보
            'company': forms.Select(attrs={'class': 'form-input'}),
            'headquarters1': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '본부명을 입력하세요'
            }),
            'headquarters2': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '하위 본부명을 입력하세요'
            }),
            'final_department': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '최종 소속 부서를 입력하세요'
            }),
            'department': forms.Select(attrs={'class': 'form-input'}),
            
            # 인사 정보
            'current_position': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '직급을 입력하세요'
            }),
            'new_position': forms.Select(attrs={'class': 'form-input'}),
            'responsibility': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '직책을 입력하세요'
            }),
            'job_group': forms.Select(attrs={'class': 'form-input'}),
            'job_type': forms.Select(attrs={'class': 'form-input'}),
            'growth_level': forms.Select(attrs={'class': 'form-input'}),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-input', 
                'type': 'date',
                'required': True
            }),
            'employment_status': forms.Select(attrs={'class': 'form-input'}),
            
            # 추가 정보
            'address': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '주소를 입력하세요'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '비상연락처 이름을 입력하세요'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '비상연락처 번호를 입력하세요'
            }),
            'education': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': '학력을 입력하세요'
            }),
            'marital_status': forms.Select(attrs={'class': 'form-input'}),
        }
        
        labels = {
            # 기본 정보
            'name': '이름',
            'email': '이메일',
            'phone': '연락처',
            'gender': '성별',
            'birth_date': '생년월일',
            'age': '나이',
            
            # 조직 정보
            'company': '회사',
            'headquarters1': '본부1',
            'headquarters2': '본부2',
            'final_department': '최종소속',
            'department': '부서 (기존)',
            
            # 인사 정보
            'current_position': '직급',
            'new_position': '신직급',
            'responsibility': '직책',
            'job_group': '직군/계열',
            'job_type': '직종',
            'growth_level': '성장레벨',
            'hire_date': '입사일',
            'employment_status': '재직상태',
            
            # 추가 정보
            'address': '주소',
            'emergency_contact': '비상연락처(이름)',
            'emergency_phone': '비상연락처(번호)',
            'education': '학력',
            'marital_status': '결혼여부',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 선택 필드의 기본값 설정
        self.fields['employment_status'].initial = '재직'
        self.fields['job_group'].initial = 'Non-PL'
        self.fields['job_type'].initial = '경영관리'
        self.fields['growth_level'].initial = 1
        
        # 필수 필드 표시
        required_fields = ['name', 'email', 'hire_date']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def clean_email(self):
        """이메일 중복 검사"""
        email = self.cleaned_data.get('email')
        if email:
            # 수정 시에는 자기 자신을 제외하고 중복 검사
            queryset = Employee.objects.filter(email=email)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('이미 등록된 이메일 주소입니다.')
        return email
    
    def clean_age(self):
        """나이 유효성 검사"""
        age = self.cleaned_data.get('age')
        if age is not None:
            if age < 18 or age > 70:
                raise forms.ValidationError('나이는 18세 이상 70세 이하로 입력해주세요.')
        return age
    
    def clean_hire_date(self):
        """입사일 유효성 검사"""
        hire_date = self.cleaned_data.get('hire_date')
        if hire_date:
            # 미래 날짜 검사
            if hire_date > date.today():
                raise forms.ValidationError('입사일은 오늘 날짜보다 이후일 수 없습니다.')
            
            # 너무 과거 날짜 검사 (1980년 이후)
            if hire_date.year < 1980:
                raise forms.ValidationError('입사일이 너무 과거입니다. 1980년 이후 날짜를 입력해주세요.')
        
        return hire_date
    
    def clean_phone(self):
        """전화번호 형식 검사"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # 숫자, 하이픈, 공백만 허용
            import re
            if not re.match(r'^[\d\-\s]+$', phone):
                raise forms.ValidationError('전화번호는 숫자, 하이픈(-), 공백만 사용할 수 있습니다.')
        return phone
    
    def clean(self):
        """전체 폼 유효성 검사"""
        cleaned_data = super().clean()
        
        # 생년월일과 나이 일치성 검사
        birth_date = cleaned_data.get('birth_date')
        age = cleaned_data.get('age')
        
        if birth_date and age:
            calculated_age = date.today().year - birth_date.year
            # 생일이 지나지 않았으면 1살 빼기
            if date.today() < birth_date.replace(year=date.today().year):
                calculated_age -= 1
            
            # 1살 정도 차이는 허용 (생일이 지났는지 여부로 인한 차이)
            if abs(calculated_age - age) > 1:
                raise forms.ValidationError('나이와 생년월일이 일치하지 않습니다.')
        
        return cleaned_data 