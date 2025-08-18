from django.contrib import admin
from .models import JobCategory, JobType, JobRole, JobProfile, JobProfileHistory


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(JobType)
class JobTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['code', 'name', 'category__name']
    ordering = ['category__code', 'code']


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'job_type', 'is_active', 'created_at']
    list_filter = ['job_type__category', 'job_type', 'is_active', 'created_at']
    search_fields = ['code', 'name', 'job_type__name', 'job_type__category__name']
    ordering = ['job_type__category__code', 'job_type__code', 'code']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job_type__category')


class JobProfileHistoryInline(admin.TabularInline):
    model = JobProfileHistory
    extra = 0
    readonly_fields = ['changed_by', 'changed_at', 'change_reason', 'previous_data']
    can_delete = False


@admin.register(JobProfile)
class JobProfileAdmin(admin.ModelAdmin):
    list_display = ['job_role', 'get_skill_count', 'is_active', 'updated_at']
    list_filter = ['is_active', 'job_role__job_type__category', 'job_role__job_type']
    search_fields = ['job_role__name', 'role_responsibility', 'qualification']
    readonly_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']
    inlines = [JobProfileHistoryInline]
    
    fieldsets = [
        ('직무 정보', {
            'fields': ['job_role', 'is_active']
        }),
        ('직무기술서 내용', {
            'fields': ['role_responsibility', 'qualification', 'growth_path']
        }),
        ('스킬 정보', {
            'fields': ['basic_skills', 'applied_skills', 'related_certifications']
        }),
        ('메타 정보', {
            'fields': ['created_by', 'created_at', 'updated_by', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        
        # 변경 이력 저장을 위해 이전 데이터 백업
        if change:
            old_obj = JobProfile.objects.get(pk=obj.pk)
            JobProfileHistory.objects.create(
                job_profile=obj,
                previous_data={
                    'role_responsibility': old_obj.role_responsibility,
                    'qualification': old_obj.qualification,
                    'basic_skills': old_obj.basic_skills,
                    'applied_skills': old_obj.applied_skills,
                    'growth_path': old_obj.growth_path,
                    'related_certifications': old_obj.related_certifications,
                },
                changed_by=request.user,
                change_reason=request.POST.get('change_reason', '')
            )
        
        super().save_model(request, obj, form, change)
    
    def get_skill_count(self, obj):
        return obj.get_skill_count()
    get_skill_count.short_description = '스킬 개수'