from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class EvaluationPeriod(models.Model):
    """Evaluation period management"""
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'evaluation_periods'
        ordering = ['-start_date']
        
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class Task(models.Model):
    """Task or project to be evaluated"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.assigned_to.get_full_name()}"


class Evaluation(models.Model):
    """Main evaluation model"""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('reviewed', _('Reviewed')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    
    period = models.ForeignKey(
        EvaluationPeriod,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations_received'
    )
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evaluations_given'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    overall_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'evaluations'
        ordering = ['-created_at']
        unique_together = ['period', 'employee', 'evaluator']
        
    def __str__(self):
        return f"Evaluation: {self.employee.get_full_name()} - {self.period.name}"
    
    def calculate_overall_score(self):
        """Calculate overall score from individual scores"""
        scores = self.scores.all()
        if scores:
            total_weight = sum(score.criterion.weight for score in scores)
            weighted_sum = sum(score.score * score.criterion.weight for score in scores)
            if total_weight > 0:
                self.overall_score = weighted_sum / total_weight
                self.save()
                return self.overall_score
        return 0


class EvaluationCriterion(models.Model):
    """Evaluation criteria"""
    
    CATEGORY_CHOICES = [
        ('technical', _('Technical Skills')),
        ('soft_skills', _('Soft Skills')),
        ('performance', _('Performance')),
        ('contribution', _('Contribution')),
        ('growth', _('Growth & Development')),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.0,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'evaluation_criteria'
        ordering = ['category', 'name']
        
    def __str__(self):
        return f"{self.category}: {self.name}"


class Score(models.Model):
    """Individual scores for each criterion"""
    
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name='scores'
    )
    criterion = models.ForeignKey(
        EvaluationCriterion,
        on_delete=models.CASCADE,
        related_name='scores'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scores'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scores'
        unique_together = ['evaluation', 'criterion', 'task']
        ordering = ['criterion__category', 'criterion__name']
        
    def __str__(self):
        return f"{self.evaluation.employee.get_full_name()} - {self.criterion.name}: {self.score}"


class Feedback(models.Model):
    """AI-generated and manual feedback"""
    
    TYPE_CHOICES = [
        ('ai', _('AI Generated')),
        ('manual', _('Manual')),
        ('combined', _('Combined')),
    ]
    
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='manual')
    content = models.TextField()
    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    ai_prompt = models.TextField(blank=True)
    ai_response = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='feedbacks_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'feedbacks'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Feedback for {self.evaluation.employee.get_full_name()} - {self.type}"


class Goal(models.Model):
    """Employee goals and objectives"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('achieved', _('Achieved')),
        ('partial', _('Partially Achieved')),
        ('not_achieved', _('Not Achieved')),
    ]
    
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='goals'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    achievement_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'goals'
        ordering = ['target_date', '-created_at']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.title}"
