from django import forms
from django.utils import timezone
from .models import (
    JobPosting, Applicant, Application, 
    InterviewSchedule, RecruitmentStage
)
from employees.models import Employee


class JobPostingForm(forms.ModelForm):
    """채용공고 폼"""
    closing_date = forms.DateTimeField(
        label='마감일',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    class Meta:
        model = JobPosting
        fields = [
            'title', 'department', 'position', 'employment_type', 'job_role',
            'description', 'requirements', 'preferred_qualifications',
            'min_experience_years', 'max_experience_years',
            'vacancies', 'location', 'salary_range_min', 'salary_range_max',
            'closing_date', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'job_role': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'preferred_qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'min_experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'max_experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'vacancies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_range_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_range_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_exp = cleaned_data.get('min_experience_years')
        max_exp = cleaned_data.get('max_experience_years')
        min_salary = cleaned_data.get('salary_range_min')
        max_salary = cleaned_data.get('salary_range_max')
        
        if min_exp and max_exp and min_exp > max_exp:
            raise forms.ValidationError('최소 경력이 최대 경력보다 클 수 없습니다.')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise forms.ValidationError('최소 급여가 최대 급여보다 클 수 없습니다.')
        
        return cleaned_data


class ApplicantForm(forms.ModelForm):
    """지원자 폼"""
    birth_date = forms.DateField(
        label='생년월일',
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Applicant
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'gender', 'birth_date', 'address',
            'linkedin_url', 'portfolio_url',
            'resume_file', 'cover_letter'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control'}),
            'resume_file': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class ApplicationForm(forms.ModelForm):
    """지원서 폼"""
    class Meta:
        model = Application
        fields = ['job_posting', 'applicant', 'notes']
        widgets = {
            'job_posting': forms.Select(attrs={'class': 'form-control'}),
            'applicant': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 진행중인 채용공고만 표시
        self.fields['job_posting'].queryset = JobPosting.objects.filter(status='open')


class ApplicationEvaluationForm(forms.ModelForm):
    """지원서 평가 폼"""
    evaluation_notes = forms.CharField(
        label='평가 메모',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    class Meta:
        model = Application
        fields = [
            'current_stage', 'status', 'assigned_to',
            'technical_score', 'cultural_fit_score', 'overall_rating',
            'notes', 'rejection_reason'
        ]
        widgets = {
            'current_stage': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'technical_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'cultural_fit_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'overall_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_stage'].queryset = RecruitmentStage.objects.filter(is_active=True)


class InterviewScheduleForm(forms.ModelForm):
    """면접 일정 폼"""
    scheduled_date = forms.DateTimeField(
        label='면접 일시',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    interviewers = forms.ModelMultipleChoiceField(
        label='면접관',
        queryset=Employee.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': 5})
    )
    
    class Meta:
        model = InterviewSchedule
        fields = [
            'interview_type', 'scheduled_date', 'duration_minutes',
            'location', 'meeting_link', 'interviewers'
        ]
        widgets = {
            'interview_type': forms.Select(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 15}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < timezone.now():
            raise forms.ValidationError('과거 날짜로 면접을 예약할 수 없습니다.')
        return scheduled_date