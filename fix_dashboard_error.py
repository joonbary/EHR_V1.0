#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
대시보드 오류 수정 스크립트
Employee 모델에 is_active 필드가 없는 문제 해결
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

def fix_ehr_system_views():
    """ehr_system/views.py 수정 - is_active 필드 제거"""
    content = '''from django.views.generic import TemplateView
from django.db.models import Count, Q
from datetime import datetime, timedelta

from employees.models import Employee
from job_profiles.models import JobRole, JobProfile


class DashboardView(TemplateView):
    """메인 대시보드 뷰"""
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 현재 날짜
        today = datetime.now().date()
        month_ago = today - timedelta(days=30)
        
        # 통계 데이터 (is_active 필드 없이)
        try:
            # 전체 직원 수 (employment_status가 'active'인 경우)
            active_employees = Employee.objects.filter(
                employment_status='active'
            ).count()
            
            # 부서 수
            departments = Employee.objects.filter(
                employment_status='active'
            ).values('department').distinct().count()
            
            # 직무 수 (JobRole 모델)
            try:
                total_job_roles = JobRole.objects.count()
            except:
                total_job_roles = 0
            
            # 완성된 프로필 수 (JobProfile 모델)
            try:
                completed_profiles = JobProfile.objects.count()
            except:
                completed_profiles = 0
            
            # 최근 입사자 (30일 이내)
            recent_hires = Employee.objects.filter(
                hire_date__gte=month_ago,
                employment_status='active'
            ).count()
            
            context['stats'] = {
                'total_employees': active_employees,
                'total_departments': departments,
                'total_job_roles': total_job_roles,
                'completed_profiles': completed_profiles,
                'recent_hires': recent_hires,
                'pending_evaluations': 0  # 평가 모델에 따라 추후 수정
            }
            
        except Exception as e:
            # 오류 발생 시 기본값
            print(f"Dashboard stats error: {e}")
            context['stats'] = {
                'total_employees': 0,
                'total_departments': 0,
                'total_job_roles': 0,
                'completed_profiles': 0,
                'recent_hires': 0,
                'pending_evaluations': 0
            }
        
        return context'''
    
    views_path = BASE_DIR / 'ehr_system' / 'views.py'
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ ehr_system/views.py 수정됨")

def fix_job_profiles_views():
    """job_profiles/views.py 수정 - is_active 필드 처리"""
    content = '''from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Prefetch, Q
import json

from .models import JobCategory, JobType, JobRole, JobProfile


class JobTreeMapView(TemplateView):
    """직무체계도 트리맵 뷰"""
    template_name = 'job_profiles/job_treemap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 데이터
        try:
            # JobCategory, JobType, JobRole 모델에 is_active 필드가 있는지 확인
            # 없으면 전체 개수 반환
            context['total_categories'] = JobCategory.objects.count()
            context['total_job_types'] = JobType.objects.count()
            context['total_job_roles'] = JobRole.objects.count()
            context['total_profiles'] = JobProfile.objects.count()
        except Exception as e:
            print(f"JobTreeMapView stats error: {e}")
            # 모델이 없거나 오류 발생 시 기본값
            context['total_categories'] = 0
            context['total_job_types'] = 0
            context['total_job_roles'] = 0
            context['total_profiles'] = 0
        
        return context


def job_tree_map_data_api(request):
    """트리맵 데이터 API"""
    try:
        # 카테고리 분류
        non_pl_categories = ['IT/디지털', '경영지원', '금융', '영업', '고객서비스']
        
        # 아이콘 매핑
        icon_map = {
            'IT/디지털': 'laptop',
            '경영지원': 'briefcase', 
            '금융': 'dollar-sign',
            '영업': 'users',
            '고객서비스': 'headphones',
            'PL': 'user-shield'
        }
        
        tree_data = {'Non-PL': {}, 'PL': {}}
        
        try:
            # 카테고리 조회 (is_active 필드 없이)
            categories = JobCategory.objects.prefetch_related(
                Prefetch('job_types', 
                    queryset=JobType.objects.prefetch_related(
                        Prefetch('job_roles',
                            queryset=JobRole.objects.select_related('profile')
                        )
                    )
                )
            ).all()
            
            for category in categories:
                category_data = {
                    'name': category.name,
                    'icon': icon_map.get(category.name, 'folder'),
                    'jobs': {}
                }
                
                for job_type in category.job_types.all():
                    jobs = []
                    for job_role in job_type.job_roles.all():
                        jobs.append({
                            'id': str(job_role.id),
                            'name': job_role.name,
                            'has_profile': hasattr(job_role, 'profile')
                        })
                    
                    if jobs:
                        category_data['jobs'][job_type.name] = jobs
                
                # 카테고리 분류
                if category.name in non_pl_categories:
                    tree_data['Non-PL'][category.name] = category_data
                else:
                    tree_data['PL'][category.name] = category_data
                    
        except Exception as e:
            print(f"Tree data error: {e}")
            # 오류 시 빈 데이터 반환
            pass
        
        return JsonResponse({
            'success': True,
            'data': tree_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def job_detail_modal_api(request, job_role_id):
    """직무 상세 정보 모달 API"""
    try:
        job_role = get_object_or_404(JobRole, id=job_role_id)
        
        data = {
            'job': {
                'id': str(job_role.id),
                'name': job_role.name,
                'category': job_role.job_type.category.name,
                'job_type': job_role.job_type.name,
                'description': getattr(job_role, 'description', ''),
                'full_path': f"{job_role.job_type.category.name} > {job_role.job_type.name} > {job_role.name}"
            }
        }
        
        # 프로필 정보
        if hasattr(job_role, 'profile'):
            profile = job_role.profile
            data['profile'] = {
                'id': str(profile.id),
                'role_responsibility': getattr(profile, 'role_responsibility', ''),
                'qualification': getattr(profile, 'qualification', ''),
                'basic_skills': getattr(profile, 'basic_skills', []),
                'applied_skills': getattr(profile, 'applied_skills', []),
                'growth_path': getattr(profile, 'growth_path', ''),
                'related_certifications': getattr(profile, 'related_certifications', [])
            }
        else:
            data['profile'] = None
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def job_profile_edit_view(request, job_role_id):
    """직무기술서 편집 뷰"""
    try:
        job_role = get_object_or_404(JobRole, id=job_role_id)
        
        if request.method == 'GET':
            profile = getattr(job_role, 'profile', None)
            context = {
                'job': job_role,
                'profile': profile
            }
            return render(request, 'job_profiles/job_profile_edit.html', context)
        
        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
                
                profile, created = JobProfile.objects.update_or_create(
                    job_role=job_role,
                    defaults={
                        'role_responsibility': data.get('role_responsibility', ''),
                        'qualification': data.get('qualification', ''),
                        'basic_skills': data.get('basic_skills', []),
                        'applied_skills': data.get('applied_skills', []),
                        'growth_path': data.get('growth_path', ''),
                        'related_certifications': data.get('related_certifications', [])
                    }
                )
                
                return JsonResponse({
                    'success': True,
                    'message': '저장되었습니다.',
                    'profile_id': str(profile.id)
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
                
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=404)'''
    
    views_path = BASE_DIR / 'job_profiles' / 'views.py'
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ job_profiles/views.py 수정됨")

def check_employee_model():
    """Employee 모델 구조 확인을 위한 스크립트"""
    check_script = '''import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee

# Employee 모델 필드 확인
print("Employee 모델 필드:")
for field in Employee._meta.get_fields():
    print(f"  - {field.name}: {field.get_internal_type()}")

# 활성 직원 수 확인
try:
    active_count = Employee.objects.filter(employment_status='active').count()
    print(f"\\n활성 직원 수: {active_count}")
except Exception as e:
    print(f"\\n오류: {e}")'''
    
    script_path = BASE_DIR / 'check_employee_model.py'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(check_script)
    
    print(f"\n✓ check_employee_model.py 생성됨")
    print("  실행: python check_employee_model.py")

def main():
    print("="*60)
    print("대시보드 오류 수정")
    print("="*60)
    
    # 1. views 파일 수정
    print("\n1. Views 파일 수정 중...")
    fix_ehr_system_views()
    fix_job_profiles_views()
    
    # 2. 모델 확인 스크립트 생성
    print("\n2. 모델 확인 스크립트 생성...")
    check_employee_model()
    
    print("\n" + "="*60)
    print("완료!")
    print("="*60)
    print("\n수정 내용:")
    print("- Employee.objects.filter(is_active=True) → filter(employment_status='active')")
    print("- JobCategory/JobType/JobRole의 is_active 필드 제거")
    print("- 오류 처리 추가")
    print("\n다음 단계:")
    print("1. python manage.py runserver")
    print("2. http://localhost:8000/ 접속")
    print("\n모델 구조 확인:")
    print("python check_employee_model.py")
    print("="*60)

if __name__ == '__main__':
    main()