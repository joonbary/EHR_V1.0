"""
Test cases for repository pattern implementation
"""
from django.test import TestCase
from django.contrib.auth.models import User
from employees.models import Employee, JobRole
from employees.repositories import EmployeeRepository
from employees.services import EmployeeService
from core.exceptions import ValidationError, BusinessLogicError


class EmployeeRepositoryTestCase(TestCase):
    """Test cases for EmployeeRepository"""
    
    def setUp(self):
        self.repository = EmployeeRepository()
        
        # Create test data
        self.user = User.objects.create_user('john', 'john@test.com', 'pass')
        self.manager = Employee.objects.create(
            name='Manager',
            employee_id='MGR001',
            department='Management'
        )
        self.employee = Employee.objects.create(
            name='Test Employee',
            employee_id='EMP001',
            department='IT',
            user=self.user,
            manager=self.manager
        )
    
    def test_get_by_id(self):
        """Test getting employee by ID"""
        employee = self.repository.get_by_id(self.employee.id)
        self.assertIsNotNone(employee)
        self.assertEqual(employee.name, 'Test Employee')
    
    def test_get_with_relations(self):
        """Test getting employee with related data"""
        employee = self.repository.get_with_relations(self.employee.id)
        self.assertIsNotNone(employee)
        # Check that relations are prefetched (no additional queries)
        with self.assertNumQueries(0):
            _ = employee.user
            _ = employee.manager
    
    def test_get_by_employee_id(self):
        """Test getting employee by employee ID"""
        employee = self.repository.get_by_employee_id('EMP001')
        self.assertIsNotNone(employee)
        self.assertEqual(employee.name, 'Test Employee')
    
    def test_get_active_employees(self):
        """Test getting active employees"""
        # Create inactive employee
        Employee.objects.create(
            name='Inactive Employee',
            employee_id='EMP002',
            employment_status='퇴직'
        )
        
        active_employees = self.repository.get_active_employees()
        self.assertEqual(active_employees.count(), 2)  # Manager and Test Employee
    
    def test_get_by_department(self):
        """Test getting employees by department"""
        # Create another IT employee
        Employee.objects.create(
            name='IT Employee 2',
            employee_id='EMP003',
            department='IT'
        )
        
        it_employees = self.repository.get_by_department('IT')
        self.assertEqual(it_employees.count(), 2)
    
    def test_get_subordinates(self):
        """Test getting subordinates of a manager"""
        subordinates = self.repository.get_subordinates(self.manager.id)
        self.assertEqual(subordinates.count(), 1)
        self.assertEqual(subordinates.first().name, 'Test Employee')
    
    def test_search(self):
        """Test employee search"""
        results = self.repository.search('Test')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().name, 'Test Employee')
        
        # Test search by employee ID
        results = self.repository.search('EMP001')
        self.assertEqual(results.count(), 1)
        
        # Test search by department
        results = self.repository.search('IT')
        self.assertEqual(results.count(), 1)
    
    def test_create(self):
        """Test creating new employee"""
        new_employee = self.repository.create(
            name='New Employee',
            employee_id='EMP004',
            department='HR'
        )
        
        self.assertIsNotNone(new_employee)
        self.assertEqual(new_employee.name, 'New Employee')
        self.assertTrue(Employee.objects.filter(employee_id='EMP004').exists())
    
    def test_update(self):
        """Test updating employee"""
        updated = self.repository.update(
            self.employee,
            department='Finance',
            position='Manager'
        )
        
        self.assertEqual(updated.department, 'Finance')
        self.assertEqual(updated.position, 'Manager')
    
    def test_bulk_update_department(self):
        """Test bulk update of department"""
        # Create more employees in IT
        Employee.objects.create(
            name='IT Employee 2',
            employee_id='EMP005',
            department='IT'
        )
        
        updated_count = self.repository.bulk_update_department('IT', 'Technology')
        self.assertEqual(updated_count, 2)
        
        # Verify update
        tech_employees = Employee.objects.filter(department='Technology')
        self.assertEqual(tech_employees.count(), 2)


class EmployeeServiceTestCase(TestCase):
    """Test cases for EmployeeService"""
    
    def setUp(self):
        self.service = EmployeeService()
        
        # Create test data
        self.manager = Employee.objects.create(
            name='Manager',
            employee_id='MGR001',
            department='Management'
        )
    
    def test_create_employee(self):
        """Test creating employee through service"""
        employee_data = {
            'name': 'Service Employee',
            'employee_id': 'SVC001',
            'department': 'IT',
            'email': 'service@test.com',
            'manager_id': self.manager.id
        }
        
        employee = self.service.create_employee(**employee_data)
        
        self.assertIsNotNone(employee)
        self.assertEqual(employee.name, 'Service Employee')
        self.assertEqual(employee.manager.id, self.manager.id)
    
    def test_create_employee_validation(self):
        """Test employee creation validation"""
        # Test with invalid email
        with self.assertRaises(ValidationError):
            self.service.create_employee(
                name='Invalid',
                employee_id='INV001',
                email='invalid-email'
            )
        
        # Test with duplicate employee ID
        Employee.objects.create(
            name='Existing',
            employee_id='DUP001'
        )
        
        with self.assertRaises(BusinessLogicError):
            self.service.create_employee(
                name='Duplicate',
                employee_id='DUP001'
            )
    
    def test_update_employee(self):
        """Test updating employee through service"""
        employee = Employee.objects.create(
            name='Original Name',
            employee_id='UPD001'
        )
        
        updated = self.service.update_employee(
            employee.id,
            name='Updated Name',
            department='Finance'
        )
        
        self.assertEqual(updated.name, 'Updated Name')
        self.assertEqual(updated.department, 'Finance')
    
    def test_assign_manager(self):
        """Test assigning manager to employee"""
        employee = Employee.objects.create(
            name='Employee',
            employee_id='EMP001'
        )
        
        self.service.assign_manager(employee.id, self.manager.id)
        
        employee.refresh_from_db()
        self.assertEqual(employee.manager.id, self.manager.id)
    
    def test_change_department(self):
        """Test changing employee department"""
        employee = Employee.objects.create(
            name='Employee',
            employee_id='EMP001',
            department='IT'
        )
        
        updated = self.service.change_department(employee.id, 'HR')
        
        self.assertEqual(updated.department, 'HR')
    
    def test_get_team_members(self):
        """Test getting team members"""
        # Create team members
        Employee.objects.create(
            name='Team Member 1',
            employee_id='TM001',
            manager=self.manager
        )
        Employee.objects.create(
            name='Team Member 2',
            employee_id='TM002',
            manager=self.manager
        )
        
        team = self.service.get_team_members(self.manager.id)
        
        self.assertEqual(len(team), 2)
        self.assertEqual(team[0]['name'], 'Team Member 1')
    
    def test_get_employee_details(self):
        """Test getting employee details"""
        employee = Employee.objects.create(
            name='Detailed Employee',
            employee_id='DET001',
            department='IT',
            position='Developer',
            manager=self.manager
        )
        
        details = self.service.get_employee_details(employee.id)
        
        self.assertEqual(details['name'], 'Detailed Employee')
        self.assertEqual(details['department'], 'IT')
        self.assertEqual(details['manager_name'], 'Manager')
    
    def test_search_employees(self):
        """Test searching employees through service"""
        Employee.objects.create(
            name='John Doe',
            employee_id='JD001',
            department='IT'
        )
        Employee.objects.create(
            name='Jane Smith',
            employee_id='JS001',
            department='HR'
        )
        
        # Search by name
        results = self.service.search_employees('John')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'John Doe')
        
        # Search by department
        results = self.service.search_employees(department='IT')
        self.assertEqual(len(results), 1)
        
        # Search with filters
        results = self.service.search_employees(
            query='',
            department='IT',
            status='재직'
        )
        self.assertEqual(len(results), 1)