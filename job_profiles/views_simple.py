from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import JobRole, JobProfile


def job_profile_edit_simple(request, job_role_id):
    """직무기술서 편집 (인증 불필요 - 심플 버전)"""
    job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
    
    try:
        profile = job_role.profile
    except JobProfile.DoesNotExist:
        # 프로필이 없으면 새로 생성
        profile = JobProfile(job_role=job_role)
    
    if request.method == 'POST':
        try:
            # JSON 데이터 처리
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # 데이터 업데이트
            profile.role_responsibility = data.get('role_responsibility', '')
            profile.qualification = data.get('qualification', '')
            
            # 스킬 처리 (문자열을 리스트로 변환)
            basic_skills = data.get('basic_skills', '')
            if isinstance(basic_skills, str):
                profile.basic_skills = [s.strip() for s in basic_skills.split(',') if s.strip()]
            else:
                profile.basic_skills = basic_skills
                
            applied_skills = data.get('applied_skills', '')
            if isinstance(applied_skills, str):
                profile.applied_skills = [s.strip() for s in applied_skills.split(',') if s.strip()]
            else:
                profile.applied_skills = applied_skills
            
            profile.growth_path = data.get('growth_path', '')
            
            related_certs = data.get('related_certifications', '')
            if isinstance(related_certs, str):
                profile.related_certifications = [s.strip() for s in related_certs.split(',') if s.strip()]
            else:
                profile.related_certifications = related_certs
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': '저장되었습니다.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET 요청시 편집 페이지 렌더링
    context = {
        'job': {
            'id': str(job_role.id),
            'name': job_role.name,
            'category': job_role.job_type.category.name,
            'job_type': job_role.job_type.name,
        },
        'profile': {
            'role_responsibility': profile.role_responsibility if profile.id else '',
            'qualification': profile.qualification if profile.id else '',
            'basic_skills': profile.basic_skills if profile.id else [],
            'applied_skills': profile.applied_skills if profile.id else [],
            'growth_path': profile.growth_path if profile.id else '',
            'related_certifications': profile.related_certifications if profile.id else [],
        }
    }
    
    return render(request, 'job_profiles/job_profile_edit.html', context)


@csrf_exempt
def job_profile_delete_api(request, job_role_id):
    """직무기술서 삭제 API (인증 불필요)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST 메서드만 허용됩니다.'}, status=405)
    
    try:
        job_role = get_object_or_404(JobRole, id=job_role_id)
        
        # 직무기술서가 있으면 삭제
        try:
            profile = job_role.profile
            profile.delete()
            message = '직무기술서가 삭제되었습니다.'
        except JobProfile.DoesNotExist:
            message = '삭제할 직무기술서가 없습니다.'
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def job_profile_create_simple(request):
    """직무기술서 생성 (인증 불필요)"""
    job_role_id = request.GET.get('job_role')
    
    if not job_role_id:
        return redirect('/')
    
    job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
    
    # 이미 프로필이 있으면 편집 페이지로 리다이렉트
    try:
        profile = job_role.profile
        return redirect('job_profile_edit', job_role_id=job_role_id)
    except JobProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        try:
            # JSON 데이터 처리
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # 새 프로필 생성
            profile = JobProfile(
                job_role=job_role,
                role_responsibility=data.get('role_responsibility', ''),
                qualification=data.get('qualification', ''),
            )
            
            # 스킬 처리
            basic_skills = data.get('basic_skills', '')
            if isinstance(basic_skills, str):
                profile.basic_skills = [s.strip() for s in basic_skills.split(',') if s.strip()]
            else:
                profile.basic_skills = basic_skills
                
            applied_skills = data.get('applied_skills', '')
            if isinstance(applied_skills, str):
                profile.applied_skills = [s.strip() for s in applied_skills.split(',') if s.strip()]
            else:
                profile.applied_skills = applied_skills
                
            profile.growth_path = data.get('growth_path', '')
            
            related_certs = data.get('related_certifications', '')
            if isinstance(related_certs, str):
                profile.related_certifications = [s.strip() for s in related_certs.split(',') if s.strip()]
            else:
                profile.related_certifications = related_certs
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': '직무기술서가 생성되었습니다.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET 요청시 생성 페이지 렌더링 (편집 템플릿 재사용)
    context = {
        'job': {
            'id': str(job_role.id),
            'name': job_role.name,
            'category': job_role.job_type.category.name,
            'job_type': job_role.job_type.name,
        },
        'profile': {
            'role_responsibility': '',
            'qualification': '',
            'basic_skills': [],
            'applied_skills': [],
            'growth_path': '',
            'related_certifications': [],
        },
        'is_create': True
    }
    
    return render(request, 'job_profiles/job_profile_edit.html', context)