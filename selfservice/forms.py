from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from employees.models import Employee

class ProfileUpdateForm(forms.ModelForm):
    """직원 프로필 수정 폼"""
    class Meta:
        model = Employee
        fields = ['phone', 'email', 'address', 'emergency_contact', 
                 'emergency_phone', 'profile_image']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'phone': '휴대전화',
            'email': '이메일',
            'address': '주소',
            'emergency_contact': '비상연락처(이름)',
            'emergency_phone': '비상연락처(번호)',
            'profile_image': '프로필 사진',
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """비밀번호 변경 폼"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['old_password'].label = '현재 비밀번호'
        self.fields['new_password1'].label = '새 비밀번호'
        self.fields['new_password2'].label = '새 비밀번호 확인' 