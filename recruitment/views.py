from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
from .models import (
    JobPosting, Applicant, Application, 
    InterviewSchedule, RecruitmentStage, ApplicationHistory
)
from .forms import (
    JobPostingForm, ApplicantForm, ApplicationForm, 
    InterviewScheduleForm, ApplicationEvaluationForm
)


def recruitment_dashboard(request):
    """채용 대시보드"""
    # 채용공고 통계
    total_postings = JobPosting.objects.count()
    active_postings = JobPosting.objects.filter(status='open').count()
    
    # 지원자 통계
    total_applications = Application.objects.count()
    pending_applications = Application.objects.filter(status='submitted').count()
    scheduled_interviews = Application.objects.filter(status='interview_scheduled').count()
    
    # 오늘의 면접 일정
    today = timezone.now().date()
    today_interviews = InterviewSchedule.objects.filter(
        scheduled_date__date=today,
        status='scheduled'
    ).select_related('application__applicant', 'application__job_posting')
    
    # 최근 지원자
    recent_applications = Application.objects.select_related(
        'applicant', 'job_posting'
    ).order_by('-applied_date')[:5]
    
    # 진행중인 채용공고
    active_job_postings = JobPosting.objects.filter(
        status='open'
    ).annotate(
        application_count=Count('applications')
    ).order_by('-created_at')[:5]
    
    # 채용 단계별 현황
    stage_statistics = Application.objects.filter(
        job_posting__status='open'
    ).values('current_stage__name').annotate(
        count=Count('id')
    ).order_by('current_stage__order')
    
    context = {
        'total_postings': total_postings,
        'active_postings': active_postings,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'scheduled_interviews': scheduled_interviews,
        'today_interviews': today_interviews,
        'recent_applications': recent_applications,
        'active_job_postings': active_job_postings,
        'stage_statistics': stage_statistics,
    }
    
    return render(request, 'recruitment/dashboard.html', context)


def job_posting_list(request):
    """채용공고 목록"""
    postings = JobPosting.objects.annotate(
        application_count=Count('applications')
    ).order_by('-created_at')
    
    # 필터링
    status = request.GET.get('status')
    if status:
        postings = postings.filter(status=status)
    
    department = request.GET.get('department')
    if department:
        postings = postings.filter(department=department)
    
    context = {
        'postings': postings,
    }
    
    return render(request, 'recruitment/job_posting_list.html', context)


def job_posting_detail(request, pk):
    """채용공고 상세"""
    posting = get_object_or_404(
        JobPosting.objects.select_related('created_by', 'job_role'),
        pk=pk
    )
    
    # 지원자 통계
    applications = posting.applications.select_related('applicant', 'current_stage')
    total_applications = applications.count()
    
    # 단계별 현황
    stage_breakdown = applications.values(
        'current_stage__name', 'current_stage__order'
    ).annotate(
        count=Count('id')
    ).order_by('current_stage__order')
    
    # 상태별 현황
    status_breakdown = applications.values('status').annotate(
        count=Count('id')
    )
    
    context = {
        'posting': posting,
        'total_applications': total_applications,
        'applications': applications.order_by('-applied_date')[:10],
        'stage_breakdown': stage_breakdown,
        'status_breakdown': status_breakdown,
    }
    
    return render(request, 'recruitment/job_posting_detail.html', context)


def job_posting_create(request):
    """채용공고 생성"""
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            posting = form.save(commit=False)
            posting.created_by = None  # 로그인 기능 없음
            posting.save()
            messages.success(request, '채용공고가 생성되었습니다.')
            return redirect('recruitment:job_posting_detail', pk=posting.pk)
    else:
        form = JobPostingForm()
    
    return render(request, 'recruitment/job_posting_form.html', {
        'form': form,
        'title': '채용공고 등록'
    })


def job_posting_update(request, pk):
    """채용공고 수정"""
    posting = get_object_or_404(JobPosting, pk=pk)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=posting)
        if form.is_valid():
            form.save()
            messages.success(request, '채용공고가 수정되었습니다.')
            return redirect('recruitment:job_posting_detail', pk=posting.pk)
    else:
        form = JobPostingForm(instance=posting)
    
    return render(request, 'recruitment/job_posting_form.html', {
        'form': form,
        'posting': posting,
        'title': '채용공고 수정'
    })


def application_list(request):
    """지원서 목록"""
    applications = Application.objects.select_related(
        'applicant', 'job_posting', 'current_stage', 'assigned_to'
    ).order_by('-applied_date')
    
    # 필터링
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)
    
    job_posting = request.GET.get('job_posting')
    if job_posting:
        applications = applications.filter(job_posting_id=job_posting)
    
    stage = request.GET.get('stage')
    if stage:
        applications = applications.filter(current_stage_id=stage)
    
    context = {
        'applications': applications,
        'job_postings': JobPosting.objects.filter(status='open'),
        'stages': RecruitmentStage.objects.filter(is_active=True),
    }
    
    return render(request, 'recruitment/application_list.html', context)


def application_detail(request, pk):
    """지원서 상세"""
    application = get_object_or_404(
        Application.objects.select_related(
            'applicant', 'job_posting', 'current_stage', 'assigned_to'
        ),
        pk=pk
    )
    
    # 면접 일정
    interviews = application.interviews.select_related(
        'created_by'
    ).prefetch_related('interviewers').order_by('scheduled_date')
    
    # 이력
    history = application.history.select_related(
        'stage', 'changed_by'
    ).order_by('-changed_at')
    
    context = {
        'application': application,
        'interviews': interviews,
        'history': history,
    }
    
    return render(request, 'recruitment/application_detail.html', context)


def application_evaluate(request, pk):
    """지원서 평가"""
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        form = ApplicationEvaluationForm(request.POST, instance=application)
        if form.is_valid():
            old_status = application.status
            old_stage = application.current_stage
            
            application = form.save()
            
            # 이력 추가
            if old_status != application.status or old_stage != application.current_stage:
                ApplicationHistory.objects.create(
                    application=application,
                    stage=application.current_stage,
                    status=application.status,
                    notes=form.cleaned_data.get('evaluation_notes', ''),
                    changed_by=None  # 로그인 기능 없음
                )
            
            messages.success(request, '평가가 저장되었습니다.')
            return redirect('recruitment:application_detail', pk=application.pk)
    else:
        form = ApplicationEvaluationForm(instance=application)
    
    return render(request, 'recruitment/application_evaluate.html', {
        'form': form,
        'application': application,
    })


def interview_schedule_create(request, application_id):
    """면접 일정 생성"""
    application = get_object_or_404(Application, pk=application_id)
    
    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.created_by = None  # 로그인 기능 없음
            interview.save()
            form.save_m2m()  # ManyToMany 필드 저장
            
            # 지원서 상태 업데이트
            if application.status in ['submitted', 'reviewing']:
                application.status = 'interview_scheduled'
                application.save()
                
                ApplicationHistory.objects.create(
                    application=application,
                    stage=application.current_stage,
                    status='interview_scheduled',
                    notes=f'{interview.get_interview_type_display()} 일정 예약',
                    changed_by=None  # 로그인 기능 없음
                )
            
            messages.success(request, '면접 일정이 생성되었습니다.')
            return redirect('recruitment:application_detail', pk=application.pk)
    else:
        form = InterviewScheduleForm()
    
    return render(request, 'recruitment/interview_schedule_form.html', {
        'form': form,
        'application': application,
        'title': '면접 일정 등록'
    })


def interview_schedule_update(request, pk):
    """면접 일정 수정"""
    interview = get_object_or_404(InterviewSchedule, pk=pk)
    
    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()
            messages.success(request, '면접 일정이 수정되었습니다.')
            return redirect('recruitment:application_detail', pk=interview.application.pk)
    else:
        form = InterviewScheduleForm(instance=interview)
    
    return render(request, 'recruitment/interview_schedule_form.html', {
        'form': form,
        'interview': interview,
        'application': interview.application,
        'title': '면접 일정 수정'
    })


def interview_evaluate(request, pk):
    """면접 평가"""
    interview = get_object_or_404(InterviewSchedule, pk=pk)
    
    if request.method == 'POST':
        # 면접 평가 저장
        interview.interview_notes = request.POST.get('interview_notes', '')
        interview.technical_assessment = request.POST.get('technical_assessment', '')
        interview.cultural_assessment = request.POST.get('cultural_assessment', '')
        interview.recommendation = request.POST.get('recommendation', '')
        interview.status = 'completed'
        interview.save()
        
        # 지원서 상태 업데이트
        application = interview.application
        if application.status == 'interview_scheduled':
            application.status = 'interviewed'
            application.save()
            
            ApplicationHistory.objects.create(
                application=application,
                stage=application.current_stage,
                status='interviewed',
                notes=f'{interview.get_interview_type_display()} 완료',
                changed_by=None  # Authentication removed
            )
        
        messages.success(request, '면접 평가가 저장되었습니다.')
        return redirect('recruitment:application_detail', pk=application.pk)
    
    return render(request, 'recruitment/interview_evaluate.html', {
        'interview': interview,
    })


def applicant_create(request):
    """지원자 등록"""
    if request.method == 'POST':
        form = ApplicantForm(request.POST, request.FILES)
        if form.is_valid():
            applicant = form.save()
            
            # 지원서 생성 페이지로 이동
            job_posting_id = request.GET.get('job_posting')
            if job_posting_id:
                return redirect(
                    reverse('recruitment:application_create') + 
                    f'?applicant={applicant.pk}&job_posting={job_posting_id}'
                )
            
            messages.success(request, '지원자 정보가 등록되었습니다.')
            return redirect('recruitment:applicant_detail', pk=applicant.pk)
    else:
        form = ApplicantForm()
    
    return render(request, 'recruitment/applicant_form.html', {
        'form': form,
        'title': '지원자 등록'
    })


def applicant_detail(request, pk):
    """지원자 상세"""
    applicant = get_object_or_404(Applicant, pk=pk)
    applications = applicant.applications.select_related(
        'job_posting', 'current_stage'
    ).order_by('-applied_date')
    
    context = {
        'applicant': applicant,
        'applications': applications,
    }
    
    return render(request, 'recruitment/applicant_detail.html', context)


def application_create(request):
    """지원서 생성"""
    applicant_id = request.GET.get('applicant')
    job_posting_id = request.GET.get('job_posting')
    
    initial = {}
    if applicant_id:
        initial['applicant'] = applicant_id
    if job_posting_id:
        initial['job_posting'] = job_posting_id
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            
            # 초기 단계 설정
            first_stage = RecruitmentStage.objects.filter(
                is_active=True
            ).order_by('order').first()
            if first_stage:
                application.current_stage = first_stage
            
            application.save()
            
            # 이력 추가
            ApplicationHistory.objects.create(
                application=application,
                stage=application.current_stage,
                status='submitted',
                notes='지원서 접수',
                changed_by=None  # Authentication removed
            )
            
            messages.success(request, '지원서가 접수되었습니다.')
            return redirect('recruitment:application_detail', pk=application.pk)
    else:
        form = ApplicationForm(initial=initial)
    
    return render(request, 'recruitment/application_form.html', {
        'form': form,
        'title': '지원서 접수'
    })
