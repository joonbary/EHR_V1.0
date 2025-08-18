"""
알림 시스템 서비스 모듈
"""
from django.utils import timezone
from django.template import Template, Context
from django.core.mail import send_mail
from django.conf import settings
from typing import List, Dict, Any, Optional
import logging

from .models import (
    NotificationType, Notification, NotificationPreference,
    NotificationLog, AnnouncementBoard
)
from employees.models import Employee

logger = logging.getLogger(__name__)


class NotificationService:
    """알림 서비스 클래스"""
    
    @staticmethod
    def create_notification(
        notification_type: NotificationType,
        recipient: Employee,
        context_data: Dict[str, Any],
        sender: Optional[Employee] = None,
        action_url: str = "",
        action_text: str = "",
        scheduled_at: Optional[timezone.datetime] = None
    ) -> Notification:
        """
        알림 생성
        
        Args:
            notification_type: 알림 유형
            recipient: 수신자
            context_data: 템플릿 컨텍스트 데이터
            sender: 발신자 (선택사항)
            action_url: 액션 URL
            action_text: 액션 버튼 텍스트
            scheduled_at: 예약 발송 시간
            
        Returns:
            생성된 알림 객체
        """
        # 수신자 설정 확인
        preference = NotificationService.get_or_create_preference(recipient)
        
        if not preference.should_receive_notification(notification_type):
            logger.info(f"User {recipient.name} has disabled {notification_type.category} notifications")
            return None
        
        # 템플릿 렌더링
        template = Template(notification_type.template)
        context = Context(context_data)
        message = template.render(context)
        
        # 제목 생성 (템플릿에서 첫 번째 줄을 제목으로 사용)
        lines = message.split('\n', 1)
        title = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ""
        
        # 만료 시간 계산
        expires_at = None
        if notification_type.auto_expire_days > 0:
            expires_at = timezone.now() + timezone.timedelta(
                days=notification_type.auto_expire_days
            )
        
        # 알림 생성
        notification = Notification.objects.create(
            notification_type=notification_type,
            recipient=recipient,
            sender=sender,
            title=title,
            message=content,
            data=context_data,
            action_url=action_url,
            action_text=action_text,
            scheduled_at=scheduled_at,
            expires_at=expires_at
        )
        
        # 즉시 발송 또는 예약
        if scheduled_at is None or scheduled_at <= timezone.now():
            NotificationService.send_notification(notification)
        
        return notification
    
    @staticmethod
    def send_notification(notification: Notification) -> bool:
        """
        알림 발송
        
        Args:
            notification: 발송할 알림
            
        Returns:
            발송 성공 여부
        """
        try:
            preference = NotificationService.get_or_create_preference(
                notification.recipient
            )
            
            success = True
            
            # 푸시 알림 발송
            if notification.notification_type.send_push and preference.enable_push:
                success &= NotificationService._send_push_notification(notification)
            
            # 이메일 발송
            if notification.notification_type.send_email and preference.enable_email:
                success &= NotificationService._send_email_notification(notification)
            
            # SMS 발송
            if notification.notification_type.send_sms and preference.enable_sms:
                success &= NotificationService._send_sms_notification(notification)
            
            if success:
                notification.mark_as_sent()
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {str(e)}")
            return False
    
    @staticmethod
    def _send_push_notification(notification: Notification) -> bool:
        """푸시 알림 발송"""
        try:
            # 실제 구현에서는 WebSocket이나 Firebase 등을 사용
            # 여기서는 로그만 기록
            logger.info(f"Push notification sent to {notification.recipient.name}")
            
            NotificationLog.objects.create(
                notification=notification,
                channel='PUSH',
                status='SUCCESS'
            )
            return True
            
        except Exception as e:
            NotificationLog.objects.create(
                notification=notification,
                channel='PUSH',
                status='FAILED',
                error_message=str(e)
            )
            return False
    
    @staticmethod
    def _send_email_notification(notification: Notification) -> bool:
        """이메일 알림 발송"""
        try:
            if not notification.recipient.email:
                return False
            
            subject = f"[OK Financial HRIS] {notification.title}"
            message = notification.message
            
            # HTML 메시지 구성
            html_message = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #3b82f6;">{notification.title}</h2>
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p>{message}</p>
                </div>
                {f'<p><a href="{notification.action_url}" style="background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">{notification.action_text}</a></p>' if notification.action_url else ''}
                <hr style="margin: 30px 0;">
                <p style="color: #64748b; font-size: 14px;">
                    OK Financial Group HRIS 시스템에서 발송된 알림입니다.
                </p>
            </div>
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient.email],
                html_message=html_message,
                fail_silently=False
            )
            
            NotificationLog.objects.create(
                notification=notification,
                channel='EMAIL',
                status='SUCCESS'
            )
            return True
            
        except Exception as e:
            NotificationLog.objects.create(
                notification=notification,
                channel='EMAIL',
                status='FAILED',
                error_message=str(e)
            )
            return False
    
    @staticmethod
    def _send_sms_notification(notification: Notification) -> bool:
        """SMS 알림 발송"""
        try:
            if not notification.recipient.phone:
                return False
            
            # 실제 구현에서는 SMS 게이트웨이 API 사용
            # 여기서는 로그만 기록
            logger.info(f"SMS sent to {notification.recipient.phone}")
            
            NotificationLog.objects.create(
                notification=notification,
                channel='SMS',
                status='SUCCESS'
            )
            return True
            
        except Exception as e:
            NotificationLog.objects.create(
                notification=notification,
                channel='SMS',
                status='FAILED',
                error_message=str(e)
            )
            return False
    
    @staticmethod
    def get_or_create_preference(employee: Employee) -> NotificationPreference:
        """직원 알림 설정 조회 또는 생성"""
        preference, created = NotificationPreference.objects.get_or_create(
            employee=employee
        )
        return preference
    
    @staticmethod
    def mark_notifications_as_read(recipient: Employee, notification_ids: List[str]):
        """다중 알림을 읽음으로 표시"""
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            recipient=recipient,
            status__in=['SENT', 'PENDING']
        )
        
        for notification in notifications:
            notification.mark_as_read()
    
    @staticmethod
    def get_unread_count(recipient: Employee) -> int:
        """읽지 않은 알림 수 조회"""
        return Notification.objects.filter(
            recipient=recipient,
            status__in=['SENT', 'PENDING']
        ).count()
    
    @staticmethod
    def process_scheduled_notifications():
        """예약된 알림 처리 (cron job으로 실행)"""
        scheduled_notifications = Notification.objects.filter(
            status='PENDING',
            scheduled_at__lte=timezone.now()
        )
        
        for notification in scheduled_notifications:
            NotificationService.send_notification(notification)
    
    @staticmethod
    def expire_old_notifications():
        """만료된 알림 처리 (cron job으로 실행)"""
        expired_notifications = Notification.objects.filter(
            expires_at__lte=timezone.now(),
            status__in=['SENT', 'PENDING']
        )
        
        expired_notifications.update(status='EXPIRED')


class AnnouncementService:
    """공지사항 서비스 클래스"""
    
    @staticmethod
    def create_announcement_notification(announcement: AnnouncementBoard):
        """공지사항 알림 생성"""
        # 공지사항 알림 유형 조회
        try:
            notification_type = NotificationType.objects.get(
                category='ANNOUNCEMENT',
                name='새 공지사항'
            )
        except NotificationType.DoesNotExist:
            # 기본 공지사항 알림 유형 생성
            notification_type = NotificationType.objects.create(
                name='새 공지사항',
                category='ANNOUNCEMENT',
                priority='NORMAL' if not announcement.is_urgent else 'URGENT',
                template='새 공지사항: {{ title }}\n{{ content|truncatewords:20 }}',
                send_push=True
            )
        
        # 대상 직원 목록 생성
        target_employees = AnnouncementService.get_target_employees(announcement)
        
        # 각 대상 직원에게 알림 발송
        for employee in target_employees:
            NotificationService.create_notification(
                notification_type=notification_type,
                recipient=employee,
                context_data={
                    'title': announcement.title,
                    'content': announcement.content,
                    'author': announcement.author.name,
                    'announcement_id': str(announcement.id)
                },
                sender=announcement.author,
                action_url=f"/notifications/announcements/{announcement.id}/",
                action_text="공지사항 보기"
            )
    
    @staticmethod
    def get_target_employees(announcement: AnnouncementBoard) -> List[Employee]:
        """공지사항 대상 직원 목록 조회"""
        if announcement.visibility == 'ALL':
            return Employee.objects.filter(employment_status='재직')
        elif announcement.visibility == 'DEPARTMENT':
            dept_codes = announcement.target_departments.values_list('code', flat=True)
            return Employee.objects.filter(
                department__in=dept_codes,
                employment_status='재직'
            )
        elif announcement.visibility == 'POSITION':
            position_names = announcement.target_positions.values_list('name', flat=True)
            return Employee.objects.filter(
                new_position__in=position_names,
                employment_status='재직'
            )
        elif announcement.visibility == 'CUSTOM':
            return announcement.target_employees.filter(employment_status='재직')
        
        return []


# 빠른 알림 생성 함수들
def send_hr_notification(recipient: Employee, title: str, message: str, **kwargs):
    """HR 관련 알림 발송"""
    notification_type, _ = NotificationType.objects.get_or_create(
        category='HR',
        name='HR 알림',
        defaults={
            'template': '{{ title }}\n{{ message }}',
            'priority': 'NORMAL',
            'send_push': True
        }
    )
    
    return NotificationService.create_notification(
        notification_type=notification_type,
        recipient=recipient,
        context_data={'title': title, 'message': message},
        **kwargs
    )


def send_system_notification(recipient: Employee, title: str, message: str, **kwargs):
    """시스템 알림 발송"""
    notification_type, _ = NotificationType.objects.get_or_create(
        category='SYSTEM',
        name='시스템 알림',
        defaults={
            'template': '{{ title }}\n{{ message }}',
            'priority': 'NORMAL',
            'send_push': True
        }
    )
    
    return NotificationService.create_notification(
        notification_type=notification_type,
        recipient=recipient,
        context_data={'title': title, 'message': message},
        **kwargs
    )


def send_evaluation_notification(recipient: Employee, title: str, message: str, **kwargs):
    """평가 관련 알림 발송"""
    notification_type, _ = NotificationType.objects.get_or_create(
        category='EVALUATION',
        name='평가 알림',
        defaults={
            'template': '{{ title }}\n{{ message }}',
            'priority': 'HIGH',
            'send_push': True,
            'send_email': True
        }
    )
    
    return NotificationService.create_notification(
        notification_type=notification_type,
        recipient=recipient,
        context_data={'title': title, 'message': message},
        **kwargs
    )