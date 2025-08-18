from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Extended User model for EHR Evaluation System"""
    
    ROLE_CHOICES = [
        ('employee', _('Employee')),
        ('evaluator', _('Evaluator')),
        ('hr', _('HR Manager')),
        ('admin', _('Administrator')),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"
    
    def get_evaluations_as_employee(self):
        """Get all evaluations where this user is the employee"""
        return self.evaluations_received.all()
    
    def get_evaluations_as_evaluator(self):
        """Get all evaluations where this user is the evaluator"""
        return self.evaluations_given.all()
