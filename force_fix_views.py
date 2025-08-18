#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Views 파일 강제 재생성 및 캐시 완전 삭제
"""

import os
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent

def delete_all_pycache():
    """모든 __pycache__ 디렉토리 삭제"""
    print("1. 모든 Python 캐시 삭제 중...")
    
    count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                count += 1
                print(f"   삭제: {pycache_path}")
            except Exception as e:
                print(f"   실패: {pycache_path} - {e}")
    
    # .pyc 파일도 삭제
    pyc_count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    pyc_count += 1
                except:
                    pass
    
    print(f"   총 {count}개의 __pycache__ 디렉토리 삭제")
    print(f"   총 {pyc_count}개의 .pyc 파일 삭제")

def backup_and_recreate_views():
    """기존 views 백업 후 재생성"""
    print("\n2. Views 파일 백업 및 재생성...")
    
    # ehr_system/views.py 백업 및 재생성
    ehr_views_path = BASE_DIR / 'ehr_system' / 'views.py'
    if ehr_views_path.exists():
        backup_path = ehr_views_path.with_suffix('.py.bak')
        shutil.copy2(ehr_views_path, backup_path)
        print(f"   백업: {backup_path}")
    
    # 새로운 ehr_system/views.py 생성
    ehr_views_content = '''from django.views.generic import TemplateView
from django.db.models import Count, Q
from datetime import datetime, timedelta


class DashboardView(TemplateView):
    """메인 대시보드 뷰"""
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Employee 모델 임포트를 여기서 수행
        try:
            from employees.models import Employee
            
            # employment_status='active'인 직원만 카운트
            active_employees = Employee.objects.filter(
                employment_status='active'
            ).count()
            
            # 부서 수 (중복 제거)
            departments = Employee.objects.filter(
                employment_status='active'
            ).values('department').distinct().count()
            
            # 최근 30일 신규 입사자
            today = datetime.now().date()
            month_ago = today - timedelta(days=30)
            recent_hires = Employee.objects.filter(
                hire_date__gte=month_ago,
                employment_status='active'
            ).count()
            
        except Exception as e:
            print(f"Employee 통계 오류: {e}")
            active_employees = 0
            departments = 0
            recent_hires = 0
        
        # JobRole, JobProfile 통계
        try:
            from job_profiles.models import JobRole, JobProfile
            
            total_job_roles = JobRole.objects.count()
            completed_profiles = JobProfile.objects.count()
            
        except Exception as e:
            print(f"Job 통계 오류: {e}")
            total_job_roles = 0
            completed_profiles = 0
        
        # 컨텍스트에 통계 추가
        context['stats'] = {
            'total_employees': active_employees,
            'total_departments': departments,
            'total_job_roles': total_job_roles,
            'completed_profiles': completed_profiles,
            'recent_hires': recent_hires,
            'pending_evaluations': 0
        }
        
        return context
'''
    
    with open(ehr_views_path, 'w', encoding='utf-8') as f:
        f.write(ehr_views_content)
    print("   ✓ ehr_system/views.py 재생성됨")
    
    # job_profiles/views.py도 재생성
    job_views_path = BASE_DIR / 'job_profiles' / 'views.py'
    if job_views_path.exists():
        backup_path = job_views_path.with_suffix('.py.bak')
        shutil.copy2(job_views_path, backup_path)
        print(f"   백업: {backup_path}")
    
    job_views_content = '''from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Prefetch
import json


class JobTreeMapView(TemplateView):
    """직무체계도 트리맵 뷰"""
    template_name = 'job_profiles/job_treemap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 데이터 - 모델이 있으면 사용, 없으면 0
        try:
            from .models import JobCategory, JobType, JobRole, JobProfile
            
            context['total_categories'] = JobCategory.objects.count()
            context['total_job_types'] = JobType.objects.count()
            context['total_job_roles'] = JobRole.objects.count()
            context['total_profiles'] = JobProfile.objects.count()
            
        except Exception as e:
            print(f"Job 모델 통계 오류: {e}")
            context['total_categories'] = 0
            context['total_job_types'] = 0
            context['total_job_roles'] = 0
            context['total_profiles'] = 0
        
        return context


def job_tree_map_data_api(request):
    """트리맵 데이터 API"""
    try:
        from .models import JobCategory, JobType, JobRole, JobProfile
        
        # 카테고리별 데이터 구성
        non_pl_categories = ['IT/디지털', '경영지원', '금융', '영업', '고객서비스']
        icon_map = {
            'IT/디지털': 'laptop',
            '경영지원': 'briefcase',
            '금융': 'dollar-sign',
            '영업': 'users',
            '고객서비스': 'headphones',
            'PL': 'user-shield'
        }
        
        tree_data = {'Non-PL': {}, 'PL': {}}
        
        # 모든 카테고리 조회
        categories = JobCategory.objects.all()
        
        for category in categories:
            category_data = {
                'name': category.name,
                'icon': icon_map.get(category.name, 'folder'),
                'jobs': {}
            }
            
            # 카테고리별 직종과 직무 조회
            job_types = JobType.objects.filter(category=category)
            
            for job_type in job_types:
                jobs = []
                job_roles = JobRole.objects.filter(job_type=job_type)
                
                for job_role in job_roles:
                    # 프로필 존재 여부 확인
                    try:
                        has_profile = JobProfile.objects.filter(job_role=job_role).exists()
                    except:
                        has_profile = False
                    
                    jobs.append({
                        'id': str(job_role.id),
                        'name': job_role.name,
                        'has_profile': has_profile
                    })
                
                if jobs:
                    category_data['jobs'][job_type.name] = jobs
            
            # Non-PL 또는 PL로 분류
            if category.name in non_pl_categories:
                tree_data['Non-PL'][category.name] = category_data
            else:
                tree_data['PL'][category.name] = category_data
        
        return JsonResponse({
            'success': True,
            'data': tree_data
        })
        
    except Exception as e:
        print(f"API 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': {'Non-PL': {}, 'PL': {}}
        })


def job_detail_modal_api(request, job_role_id):
    """직무 상세 정보 API"""
    try:
        from .models import JobRole, JobProfile
        
        job_role = get_object_or_404(JobRole, id=job_role_id)
        
        data = {
            'job': {
                'id': str(job_role.id),
                'name': job_role.name,
                'category': job_role.job_type.category.name,
                'job_type': job_role.job_type.name,
                'description': '',
                'full_path': f"{job_role.job_type.category.name} > {job_role.job_type.name} > {job_role.name}"
            }
        }
        
        # 프로필 정보 확인
        try:
            profile = JobProfile.objects.get(job_role=job_role)
            data['profile'] = {
                'id': str(profile.id),
                'role_responsibility': getattr(profile, 'role_responsibility', ''),
                'qualification': getattr(profile, 'qualification', ''),
                'basic_skills': getattr(profile, 'basic_skills', []),
                'applied_skills': getattr(profile, 'applied_skills', []),
                'growth_path': getattr(profile, 'growth_path', ''),
                'related_certifications': getattr(profile, 'related_certifications', [])
            }
        except JobProfile.DoesNotExist:
            data['profile'] = None
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=404)


def job_profile_edit_view(request, job_role_id):
    """직무기술서 편집 뷰"""
    from .models import JobRole, JobProfile
    
    job_role = get_object_or_404(JobRole, id=job_role_id)
    
    if request.method == 'GET':
        try:
            profile = JobProfile.objects.get(job_role=job_role)
        except JobProfile.DoesNotExist:
            profile = None
        
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
                defaults=data
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
'''
    
    with open(job_views_path, 'w', encoding='utf-8') as f:
        f.write(job_views_content)
    print("   ✓ job_profiles/views.py 재생성됨")

def restart_django():
    """Django 재시작 안내"""
    print("\n3. Django 서버 재시작 안내")
    print("="*60)
    print("아래 단계를 순서대로 실행하세요:")
    print("\n1) 현재 실행 중인 서버를 완전히 중지:")
    print("   - Ctrl+C를 여러 번 눌러 완전히 종료")
    print("   - 작업 관리자에서 python.exe 프로세스 확인")
    print("\n2) 포트 확인 (Windows):")
    print("   netstat -ano | findstr :8000")
    print("   taskkill /PID [PID번호] /F")
    print("\n3) Django 쉘에서 확인:")
    print("   python manage.py shell")
    print("   >>> from employees.models import Employee")
    print("   >>> Employee._meta.get_fields()")
    print("   >>> exit()")
    print("\n4) 서버 재시작:")
    print("   python manage.py runserver")
    print("="*60)

def create_test_script():
    """테스트 스크립트 생성"""
    test_content = '''import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

print("="*60)
print("모델 필드 확인")
print("="*60)

try:
    from employees.models import Employee
    print("\\nEmployee 모델 필드:")
    for field in Employee._meta.get_fields():
        if not field.many_to_many and not field.one_to_many:
            print(f"  - {field.name}: {field.get_internal_type()}")
    
    # employment_status 필드 확인
    print("\\nemployment_status 필드 타입:")
    status_field = Employee._meta.get_field('employment_status')
    print(f"  타입: {status_field.get_internal_type()}")
    if hasattr(status_field, 'choices') and status_field.choices:
        print("  선택지:", dict(status_field.choices))
    
    # 테스트 쿼리
    print("\\n테스트 쿼리:")
    active_count = Employee.objects.filter(employment_status='active').count()
    print(f"  활성 직원 수: {active_count}")
    
except Exception as e:
    print(f"\\n오류 발생: {e}")
    import traceback
    traceback.print_exc()

print("\\n" + "="*60)
'''
    
    test_path = BASE_DIR / 'test_models.py'
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    print(f"\n테스트 스크립트 생성: {test_path}")
    print("실행: python test_models.py")

def main():
    print("="*60)
    print("Views 파일 강제 재생성 및 캐시 삭제")
    print("="*60)
    
    # 1. 캐시 삭제
    delete_all_pycache()
    
    # 2. Views 재생성
    backup_and_recreate_views()
    
    # 3. 테스트 스크립트 생성
    create_test_script()
    
    # 4. 재시작 안내
    restart_django()

if __name__ == '__main__':
    main()