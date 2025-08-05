from django import forms
from .models import JobProfile, JobRole
import json


class JobProfileForm(forms.ModelForm):
    """직무기술서 폼"""
    # JSON 필드를 textarea로 처리하기 위한 커스텀 필드
    basic_skills_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'form-control',
            'placeholder': '기본 스킬을 한 줄에 하나씩 입력하세요'
        }),
        required=False,
        label='기본 기술/지식'
    )
    
    applied_skills_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'form-control',
            'placeholder': '응용 스킬을 한 줄에 하나씩 입력하세요'
        }),
        required=False,
        label='응용 기술/지식'
    )
    
    related_certifications_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': '관련 자격증을 한 줄에 하나씩 입력하세요'
        }),
        required=False,
        label='관련 자격증'
    )
    
    class Meta:
        model = JobProfile
        fields = [
            'job_role', 'role_responsibility', 'qualification',
            'growth_path', 'is_active'
        ]
        widgets = {
            'job_role': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'role_responsibility': forms.Textarea(attrs={
                'rows': 8,
                'class': 'form-control',
                'placeholder': '이 직무의 핵심 역할과 책임을 상세히 기술하세요'
            }),
            'qualification': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-control',
                'placeholder': '이 직무 수행에 필요한 자격요건을 기술하세요'
            }),
            'growth_path': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': '이 직무에서의 성장 경로를 기술하세요 (선택사항)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'job_role': '직무',
            'role_responsibility': '역할과 책임',
            'qualification': '자격요건',
            'growth_path': '성장경로',
            'is_active': '활성화'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 직무 선택 필드 쿼리셋 최적화
        self.fields['job_role'].queryset = JobRole.objects.filter(
            is_active=True
        ).select_related('job_type__category').order_by(
            'job_type__category__name',
            'job_type__name',
            'name'
        )
        
        # 기존 인스턴스가 있는 경우 JSON 필드를 텍스트로 변환
        if self.instance.pk:
            self.fields['basic_skills_text'].initial = '\n'.join(self.instance.basic_skills or [])
            self.fields['applied_skills_text'].initial = '\n'.join(self.instance.applied_skills or [])
            self.fields['related_certifications_text'].initial = '\n'.join(self.instance.related_certifications or [])
            
            # 수정 모드에서는 job_role 필드를 읽기 전용으로
            self.fields['job_role'].disabled = True
    
    def clean_basic_skills_text(self):
        """기본 스킬 텍스트를 리스트로 변환"""
        text = self.cleaned_data.get('basic_skills_text', '')
        skills = [skill.strip() for skill in text.split('\n') if skill.strip()]
        return skills
    
    def clean_applied_skills_text(self):
        """응용 스킬 텍스트를 리스트로 변환"""
        text = self.cleaned_data.get('applied_skills_text', '')
        skills = [skill.strip() for skill in text.split('\n') if skill.strip()]
        return skills
    
    def clean_related_certifications_text(self):
        """관련 자격증 텍스트를 리스트로 변환"""
        text = self.cleaned_data.get('related_certifications_text', '')
        certs = [cert.strip() for cert in text.split('\n') if cert.strip()]
        return certs
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # 텍스트 필드를 JSON 필드로 변환
        instance.basic_skills = self.cleaned_data.get('basic_skills_text', [])
        instance.applied_skills = self.cleaned_data.get('applied_skills_text', [])
        instance.related_certifications = self.cleaned_data.get('related_certifications_text', [])
        
        if commit:
            instance.save()
        
        return instance


class JobProfileSearchForm(forms.Form):
    """직무기술서 검색 폼"""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '직무명, 역할, 자격요건으로 검색'
        }),
        label='검색어'
    )
    
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='전체 직군',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'loadJobTypes(this.value)'
        }),
        label='직군'
    )
    
    job_type = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='전체 직종',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='직종'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import JobCategory, JobType
        
        self.fields['category'].queryset = JobCategory.objects.filter(is_active=True)
        
        # 직군이 선택된 경우 해당 직군의 직종만 표시
        if 'category' in self.data:
            try:
                category_id = self.data.get('category')
                self.fields['job_type'].queryset = JobType.objects.filter(
                    category_id=category_id,
                    is_active=True
                )
            except:
                self.fields['job_type'].queryset = JobType.objects.none()
        else:
            self.fields['job_type'].queryset = JobType.objects.none()