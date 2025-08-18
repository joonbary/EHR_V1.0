from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count
from .models import (
    NotificationType, Notification, NotificationPreference,
    NotificationLog, AnnouncementBoard
)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'priority', 'is_active', 'created_at']
    list_filter = ['category', 'priority', 'is_active']
    search_fields = ['name', 'template']
    ordering = ['category', 'priority', 'name']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'category', 'priority', 'template')
        }),
        ('발송 설정', {
            'fields': ('send_email', 'send_sms', 'send_push')
        }),
        ('상태', {
            'fields': ('is_active', 'auto_expire_days')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(notification_count=Count('notification'))


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'status', 'priority_badge', 'created_at']
    list_filter = ['status', 'notification_type__category', 'notification_type__priority', 'created_at']
    search_fields = ['title', 'message', 'recipient__name']
    date_hierarchy = 'created_at'
    raw_id_fields = ['recipient', 'sender', 'notification_type']
    ordering = ['-created_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('notification_type', 'recipient', 'sender')
        }),
        ('내용', {
            'fields': ('title', 'message', 'data')
        }),
        ('액션', {
            'fields': ('action_url', 'action_text')
        }),
        ('일정', {
            'fields': ('scheduled_at', 'expires_at')
        }),
        ('상태', {
            'fields': ('status', 'sent_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['sent_at', 'read_at', 'created_at']
    
    def priority_badge(self, obj):
        colors = {
            'LOW': 'gray',
            'NORMAL': 'blue',
            'HIGH': 'orange',
            'URGENT': 'red'
        }
        color = colors.get(obj.notification_type.priority, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.notification_type.get_priority_display()
        )
    priority_badge.short_description = '우선순위'
    
    actions = ['mark_as_read', 'mark_as_sent']
    
    def mark_as_read(self, request, queryset):
        count = 0
        for notification in queryset:
            if notification.status in ['SENT', 'PENDING']:
                notification.mark_as_read()
                count += 1
        self.message_user(request, f"{count}개의 알림을 읽음으로 표시했습니다.")
    mark_as_read.short_description = "선택한 알림을 읽음으로 표시"
    
    def mark_as_sent(self, request, queryset):
        count = 0
        for notification in queryset:
            if notification.status == 'PENDING':
                notification.mark_as_sent()
                count += 1
        self.message_user(request, f"{count}개의 알림을 발송완료로 표시했습니다.")
    mark_as_sent.short_description = "선택한 알림을 발송완료로 표시"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'enable_notifications', 'enable_email', 'enable_sms', 'weekend_notifications']
    list_filter = ['enable_notifications', 'enable_email', 'enable_sms', 'weekend_notifications']
    search_fields = ['employee__name']
    raw_id_fields = ['employee']
    
    fieldsets = (
        ('직원 정보', {
            'fields': ('employee',)
        }),
        ('전역 설정', {
            'fields': ('enable_notifications', 'enable_email', 'enable_sms', 'enable_push')
        }),
        ('카테고리별 설정', {
            'fields': (
                'hr_notifications', 'system_notifications', 'workflow_notifications',
                'evaluation_notifications', 'training_notifications', 'announcement_notifications'
            )
        }),
        ('시간 설정', {
            'fields': ('quiet_hours_start', 'quiet_hours_end', 'weekend_notifications')
        }),
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification_title', 'channel', 'status', 'sent_at']
    list_filter = ['channel', 'status', 'sent_at']
    search_fields = ['notification__title', 'notification__recipient__name']
    date_hierarchy = 'sent_at'
    raw_id_fields = ['notification']
    ordering = ['-sent_at']
    
    def notification_title(self, obj):
        return obj.notification.title
    notification_title.short_description = '알림 제목'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AnnouncementBoard)
class AnnouncementBoardAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'visibility', 'importance_badge', 'view_count', 'publish_date', 'is_published']
    list_filter = ['visibility', 'is_important', 'is_urgent', 'is_published', 'publish_date']
    search_fields = ['title', 'content', 'author__name']
    date_hierarchy = 'publish_date'
    raw_id_fields = ['author']
    filter_horizontal = ['target_departments', 'target_positions', 'target_employees']
    ordering = ['-is_important', '-is_urgent', '-publish_date']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'author')
        }),
        ('공개 설정', {
            'fields': ('visibility', 'target_departments', 'target_positions', 'target_employees')
        }),
        ('중요도', {
            'fields': ('is_important', 'is_urgent')
        }),
        ('게시 기간', {
            'fields': ('publish_date', 'expire_date', 'is_published')
        }),
        ('첨부파일', {
            'fields': ('attachment',)
        }),
    )
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    
    def importance_badge(self, obj):
        if obj.is_urgent:
            return format_html('<span style="color: red; font-weight: bold;">🚨 긴급</span>')
        elif obj.is_important:
            return format_html('<span style="color: orange; font-weight: bold;">⭐ 중요</span>')
        else:
            return format_html('<span style="color: gray;">일반</span>')
    importance_badge.short_description = '중요도'
    
    actions = ['publish_announcements', 'unpublish_announcements']
    
    def publish_announcements(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"{count}개의 공지사항을 게시했습니다.")
    publish_announcements.short_description = "선택한 공지사항 게시"
    
    def unpublish_announcements(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count}개의 공지사항을 비공개로 설정했습니다.")
    unpublish_announcements.short_description = "선택한 공지사항 비공개"
