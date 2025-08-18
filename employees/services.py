"""
Employee Service Layer
"""
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.contrib.auth.models import User
from .models import Employee
from .repositories import EmployeeRepository


class EmployeeService:
    """Service layer for employee-related business logic"""
    
    def __init__(self):
        self.repository = EmployeeRepository()
    
    @transaction.atomic
    def create_employee_with_user(
        self,
        username: str,
        email: str,
        password: str,
        employee_data: Dict[str, Any]
    ) -> Employee:
        """Create a new employee with associated user account"""
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=employee_data.get('first_name', ''),
            last_name=employee_data.get('last_name', '')
        )
        
        # Create employee
        employee_data['user'] = user
        employee = self.repository.create(**employee_data)
        
        return employee
    
    def get_employee_details(self, employee_id: int) -> Optional[Employee]:
        """Get employee with all related data"""
        return self.repository.get_with_relations(employee_id)
    
    def search_employees(self, query: str) -> List[Employee]:
        """Search employees by various criteria"""
        return list(self.repository.search_employees(query))
    
    def get_department_summary(self) -> List[Dict[str, Any]]:
        """Get summary statistics for each department"""
        stats = self.repository.get_department_statistics()
        
        # Enhance with additional calculations
        for dept in stats:
            dept['avg_salary_formatted'] = f"₩{dept.get('avg_salary', 0):,.0f}" if dept.get('avg_salary') else "N/A"
        
        return stats
    
    @transaction.atomic
    def transfer_employee(
        self,
        employee_id: int,
        new_department: str,
        new_position: Optional[str] = None,
        new_job_role_id: Optional[int] = None
    ) -> Employee:
        """Transfer employee to new department/position"""
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        # Update employee
        update_data = {'department': new_department}
        if new_position:
            update_data['position'] = new_position
        if new_job_role_id:
            update_data['job_role_id'] = new_job_role_id
        
        return self.repository.update(employee, **update_data)
    
    def get_team_members(self, manager_id: int) -> List[Employee]:
        """Get all team members for a manager"""
        manager = self.repository.get_by_id(manager_id)
        if not manager:
            return []
        
        # Get employees in the same department
        team = self.repository.get_by_department(manager.department)
        
        # Filter out the manager themselves
        return [emp for emp in team if emp.id != manager_id]
    
    def calculate_tenure(self, employee_id: int) -> Optional[Dict[str, int]]:
        """Calculate employee tenure in years, months, and days"""
        from datetime import datetime
        
        employee = self.repository.get_by_id(employee_id)
        if not employee or not employee.hire_date:
            return None
        
        today = datetime.now().date()
        delta = today - employee.hire_date
        
        years = delta.days // 365
        months = (delta.days % 365) // 30
        days = (delta.days % 365) % 30
        
        return {
            'years': years,
            'months': months,
            'days': days,
            'total_days': delta.days
        }
    
    def get_promotion_eligible_employees(
        self,
        min_tenure_years: int = 3,
        min_evaluation_grade: str = 'B'
    ) -> List[Employee]:
        """Get employees eligible for promotion"""
        candidates = self.repository.get_promotion_candidates(min_tenure_years)
        
        # Filter by evaluation grade if available
        eligible = []
        for candidate in candidates:
            # Check latest evaluation
            latest_eval = candidate.evaluations.order_by('-evaluation_period__year').first()
            if latest_eval and latest_eval.final_grade >= min_evaluation_grade:
                eligible.append(candidate)
            elif not latest_eval:
                # Include if no evaluation exists (new system)
                eligible.append(candidate)
        
        return eligible
    
    @transaction.atomic
    def bulk_update_department(
        self,
        employee_ids: List[int],
        new_department: str
    ) -> int:
        """Bulk update department for multiple employees"""
        return self.repository.bulk_update_department(employee_ids, new_department)
    
    def get_skills_distribution(self) -> Dict[str, int]:
        """Get distribution of skills across all employees"""
        all_employees = self.repository.get_all()
        skills_count = {}
        
        for employee in all_employees:
            if employee.skills:
                for skill in employee.skills.split(','):
                    skill = skill.strip()
                    if skill:
                        skills_count[skill] = skills_count.get(skill, 0) + 1
        
        return dict(sorted(skills_count.items(), key=lambda x: x[1], reverse=True))
    
    def validate_employee_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate employee data before creation/update"""
        errors = {}
        
        # Required fields
        required_fields = ['name', 'email', 'employee_id', 'department']
        for field in required_fields:
            if not data.get(field):
                errors.setdefault(field, []).append(f"{field} is required")
        
        # Email validation
        if data.get('email'):
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(data['email'])
            except ValidationError:
                errors.setdefault('email', []).append("Invalid email format")
        
        # Employee ID uniqueness
        if data.get('employee_id'):
            existing = self.repository.filter(
                employee_id=data['employee_id']
            ).exclude(id=data.get('id'))
            if existing.exists():
                errors.setdefault('employee_id', []).append("Employee ID already exists")
        
        return errors