"""
Employee Repository Implementation
"""
from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, Q, Prefetch, Count, Avg
from core.repositories.base import BaseRepository
from .models import Employee


class EmployeeRepository(BaseRepository[Employee]):
    """Repository for Employee model"""
    
    @property
    def model(self) -> type[Employee]:
        return Employee
    
    def get_with_relations(self, id: Any) -> Optional[Employee]:
        """Get employee with all related data to avoid N+1 queries"""
        try:
            return self.model.objects.select_related(
                'user',
                'job_role',
                'job_role__job_type',
                'job_role__job_type__category'
            ).prefetch_related(
                'compensations',
                'evaluations',
                'trainings',
                'certifications'
            ).get(pk=id)
        except self.model.DoesNotExist:
            return None
    
    def get_active_employees(self) -> QuerySet[Employee]:
        """Get all active employees"""
        return self.filter(employment_status='재직').select_related('user', 'job_role')
    
    def get_by_department(self, department: str) -> QuerySet[Employee]:
        """Get employees by department"""
        return self.filter(department=department).select_related('user', 'job_role')
    
    def get_by_position(self, position: str) -> QuerySet[Employee]:
        """Get employees by position"""
        return self.filter(position=position).select_related('user', 'job_role')
    
    def search_employees(self, query: str) -> QuerySet[Employee]:
        """Search employees by name, email, or employee ID"""
        return self.model.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(employee_id__icontains=query)
        ).select_related('user', 'job_role')
    
    def get_employees_with_compensation(self) -> QuerySet[Employee]:
        """Get employees with their compensation data (optimized query)"""
        from compensation.models import EmployeeCompensation
        
        return self.model.objects.select_related(
            'user',
            'job_role'
        ).prefetch_related(
            Prefetch(
                'compensations',
                queryset=EmployeeCompensation.objects.order_by('-year'),
                to_attr='latest_compensations'
            )
        )
    
    def get_employees_for_evaluation(self, evaluation_period_id: int) -> QuerySet[Employee]:
        """Get employees for a specific evaluation period"""
        from evaluations.models import ComprehensiveEvaluation
        
        return self.model.objects.filter(
            employment_status='재직'
        ).select_related(
            'user',
            'job_role'
        ).prefetch_related(
            Prefetch(
                'evaluations',
                queryset=ComprehensiveEvaluation.objects.filter(
                    evaluation_period_id=evaluation_period_id
                ),
                to_attr='period_evaluations'
            )
        )
    
    def get_department_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics by department"""
        return self.model.objects.values('department').annotate(
            employee_count=Count('id'),
            avg_salary=Avg('compensations__total_compensation')
        ).order_by('-employee_count')
    
    def bulk_update_department(self, employee_ids: List[int], new_department: str) -> int:
        """Bulk update department for multiple employees"""
        return self.model.objects.filter(id__in=employee_ids).update(
            department=new_department
        )
    
    def get_managers(self) -> QuerySet[Employee]:
        """Get all employees who are managers"""
        manager_positions = ['팀장', '부장', '본부장', '실장', '임원']
        return self.model.objects.filter(
            position__in=manager_positions,
            employment_status='재직'
        ).select_related('user', 'job_role').order_by('department', 'position')
    
    def get_recent_hires(self, days: int = 30) -> QuerySet[Employee]:
        """Get employees hired in the last N days"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        return self.model.objects.filter(
            hire_date__gte=cutoff_date
        ).select_related('user', 'job_role').order_by('-hire_date')
    
    def get_employees_by_skill(self, skill: str) -> QuerySet[Employee]:
        """Get employees with a specific skill"""
        return self.model.objects.filter(
            Q(skills__icontains=skill) | Q(certifications__name__icontains=skill)
        ).distinct().select_related('user', 'job_role')
    
    def get_promotion_candidates(self, min_years: int = 3) -> QuerySet[Employee]:
        """Get employees eligible for promotion based on tenure"""
        from datetime import datetime, timedelta
        min_hire_date = datetime.now().date() - timedelta(days=min_years * 365)
        
        return self.model.objects.filter(
            hire_date__lte=min_hire_date,
            employment_status='재직'
        ).select_related('user', 'job_role').order_by('hire_date')