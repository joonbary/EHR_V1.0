from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """Notification model for system alerts"""
    
    TYPE_CHOICES = [
        ('evaluation_assigned', _('Evaluation Assigned')),
        ('evaluation_submitted', _('Evaluation Submitted')),
        ('evaluation_approved', _('Evaluation Approved')),
        ('evaluation_rejected', _('Evaluation Rejected')),
        ('task_assigned', _('Task Assigned')),
        ('task_completed', _('Task Completed')),
        ('feedback_received', _('Feedback Received')),
        ('goal_updated', _('Goal Updated')),
        ('deadline_reminder', _('Deadline Reminder')),
        ('system', _('System Notification')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
            
    @classmethod
    def create_notification(cls, recipient, type, title, message, sender=None, priority='medium', link=''):
        """Create a new notification"""
        return cls.objects.create(
            recipient=recipient,
            sender=sender,
            type=type,
            priority=priority,
            title=title,
            message=message,
            link=link
        )
