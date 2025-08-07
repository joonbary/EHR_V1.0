"""
Test cases for utility modules
"""
import os
import tempfile
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from utils.file_upload import FileUploadHandler, ExcelProcessor, create_standard_response
from utils.dashboard_utils import (
    DashboardAggregator,
    ChartDataFormatter,
    calculate_growth_rate,
    format_currency,
    format_percentage
)


class FileUploadHandlerTestCase(TestCase):
    """Test cases for FileUploadHandler"""
    
    def setUp(self):
        self.handler = FileUploadHandler(file_type='excel')
        self.test_user = User.objects.create_user('testuser', 'test@test.com', 'pass')
    
    def test_validate_excel_file(self):
        """Test Excel file validation"""
        # Create a mock Excel file
        file_content = b'test excel content'
        file = SimpleUploadedFile(
            "test.xlsx",
            file_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        success, result = self.handler.validate_and_save(
            file=file,
            upload_path='test_uploads',
            user=self.test_user
        )
        
        self.assertTrue(success)
        self.assertIn('file_path', result)
        self.assertIn('original_name', result)
        self.assertEqual(result['original_name'], 'test.xlsx')
    
    def test_reject_invalid_extension(self):
        """Test rejection of invalid file extension"""
        file = SimpleUploadedFile(
            "test.txt",
            b"test content",
            content_type="text/plain"
        )
        
        success, result = self.handler.validate_and_save(
            file=file,
            upload_path='test_uploads'
        )
        
        self.assertFalse(success)
        self.assertIn('error', result)
    
    def test_file_size_limit(self):
        """Test file size limit enforcement"""
        # Create a file larger than the limit
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        file = SimpleUploadedFile(
            "large.xlsx",
            large_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        success, result = self.handler.validate_and_save(
            file=file,
            upload_path='test_uploads'
        )
        
        self.assertFalse(success)
        self.assertIn('error', result)


class ExcelProcessorTestCase(TestCase):
    """Test cases for ExcelProcessor"""
    
    def setUp(self):
        self.processor = ExcelProcessor()
    
    def test_validate_columns(self):
        """Test column validation"""
        import pandas as pd
        
        # Create test DataFrame
        df = pd.DataFrame({
            'column1': [1, 2, 3],
            'column2': ['a', 'b', 'c']
        })
        
        # Test with required columns
        self.processor.required_columns = ['column1', 'column2']
        is_valid, error = self.processor.validate_columns(df)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Test with missing columns
        self.processor.required_columns = ['column1', 'column3']
        is_valid, error = self.processor.validate_columns(df)
        self.assertFalse(is_valid)
        self.assertIn('column3', error)
    
    def test_clean_data(self):
        """Test data cleaning"""
        import pandas as pd
        import numpy as np
        
        # Create DataFrame with dirty data
        df = pd.DataFrame({
            'text': ['  hello  ', 'world  ', '  test'],
            'numbers': [1, 2, np.nan],
            'empty': [np.nan, np.nan, np.nan]
        })
        
        cleaned = self.processor.clean_data(df)
        
        # Check that whitespace is stripped
        self.assertEqual(cleaned['text'].iloc[0], 'hello')
        self.assertEqual(cleaned['text'].iloc[1], 'world')
        self.assertEqual(cleaned['text'].iloc[2], 'test')


class DashboardAggregatorTestCase(TestCase):
    """Test cases for DashboardAggregator"""
    
    def setUp(self):
        from employees.models import Employee
        from compensation.models import EmployeeCompensation
        
        # Create test data
        self.employee1 = Employee.objects.create(
            name='Test Employee 1',
            department='IT',
            employment_status='재직'
        )
        self.employee2 = Employee.objects.create(
            name='Test Employee 2',
            department='HR',
            employment_status='재직'
        )
        
        EmployeeCompensation.objects.create(
            employee=self.employee1,
            total_compensation=5000000
        )
        EmployeeCompensation.objects.create(
            employee=self.employee2,
            total_compensation=4000000
        )
    
    def test_get_employee_statistics(self):
        """Test employee statistics calculation"""
        from employees.models import Employee
        
        stats = DashboardAggregator.get_employee_statistics(
            Employee.objects.all()
        )
        
        self.assertEqual(stats['total_employees'], 2)
        self.assertEqual(stats['active_employees'], 2)
        self.assertEqual(len(stats['department_distribution']), 2)
    
    def test_get_compensation_statistics(self):
        """Test compensation statistics calculation"""
        from compensation.models import EmployeeCompensation
        
        stats = DashboardAggregator.get_compensation_statistics(
            EmployeeCompensation.objects.all()
        )
        
        self.assertEqual(stats['total_payroll'], 9000000.0)
        self.assertEqual(stats['avg_salary'], 4500000.0)
        self.assertEqual(stats['max_salary'], 5000000.0)
        self.assertEqual(stats['min_salary'], 4000000.0)
    
    def test_format_kpi_card(self):
        """Test KPI card formatting"""
        kpi = DashboardAggregator.format_kpi_card(
            title='Test KPI',
            value='100',
            icon='fa-test',
            trend_direction='up',
            trend_value=5.5,
            period='Monthly'
        )
        
        self.assertEqual(kpi['title'], 'Test KPI')
        self.assertEqual(kpi['value'], '100')
        self.assertEqual(kpi['icon'], 'fa-test')
        self.assertEqual(kpi['trend_direction'], 'up')
        self.assertEqual(kpi['trend_value'], 5.5)
        self.assertEqual(kpi['period'], 'Monthly')


class ChartDataFormatterTestCase(TestCase):
    """Test cases for ChartDataFormatter"""
    
    def test_format_bar_chart(self):
        """Test bar chart formatting"""
        chart_data = ChartDataFormatter.format_bar_chart(
            labels=['A', 'B', 'C'],
            data=[10, 20, 30],
            label='Test Data'
        )
        
        self.assertEqual(chart_data['labels'], ['A', 'B', 'C'])
        self.assertEqual(chart_data['datasets'][0]['data'], [10, 20, 30])
        self.assertEqual(chart_data['datasets'][0]['label'], 'Test Data')
        self.assertIn('backgroundColor', chart_data['datasets'][0])
    
    def test_format_pie_chart(self):
        """Test pie chart formatting"""
        chart_data = ChartDataFormatter.format_pie_chart(
            labels=['Slice 1', 'Slice 2'],
            data=[60, 40]
        )
        
        self.assertEqual(chart_data['labels'], ['Slice 1', 'Slice 2'])
        self.assertEqual(chart_data['datasets'][0]['data'], [60, 40])
        self.assertIn('backgroundColor', chart_data['datasets'][0])


class UtilityFunctionsTestCase(TestCase):
    """Test cases for utility functions"""
    
    def test_calculate_growth_rate(self):
        """Test growth rate calculation"""
        result = calculate_growth_rate(110, 100)
        self.assertEqual(result['rate'], 10.0)
        self.assertEqual(result['direction'], 'up')
        self.assertEqual(result['percentage'], '10.0%')
        
        result = calculate_growth_rate(90, 100)
        self.assertEqual(result['rate'], -10.0)
        self.assertEqual(result['direction'], 'down')
        
        result = calculate_growth_rate(100, 100)
        self.assertEqual(result['rate'], 0.0)
        self.assertEqual(result['direction'], 'stable')
    
    def test_format_currency(self):
        """Test currency formatting"""
        self.assertEqual(format_currency(1000000), '₩1,000,000')
        self.assertEqual(format_currency(1234.56, decimal_places=2), '₩1,234.56')
        self.assertEqual(format_currency(5000, currency='$'), '$5,000')
    
    def test_format_percentage(self):
        """Test percentage formatting"""
        self.assertEqual(format_percentage(5.5), '+5.5%')
        self.assertEqual(format_percentage(-3.2), '-3.2%')
        self.assertEqual(format_percentage(2.345, decimal_places=2), '+2.35%')
        self.assertEqual(format_percentage(1.5, include_sign=False), '1.5%')
    
    def test_create_standard_response(self):
        """Test standard response creation"""
        response = create_standard_response(
            success=True,
            message='Success',
            data={'test': 'data'}
        )
        
        self.assertEqual(response.status_code, 200)
        content = response.json()
        self.assertTrue(content['success'])
        self.assertEqual(content['message'], 'Success')
        self.assertEqual(content['data'], {'test': 'data'})
        
        # Test error response
        response = create_standard_response(
            success=False,
            error='Test error',
            status_code=400
        )
        
        self.assertEqual(response.status_code, 400)
        content = response.json()
        self.assertFalse(content['success'])
        self.assertEqual(content['error'], 'Test error')