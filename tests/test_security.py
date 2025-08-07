"""
Test cases for security utilities and vulnerabilities
"""
import os
import tempfile
from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from utils.security import (
    validate_file_upload,
    sanitize_input,
    check_sql_injection,
    validate_email,
    generate_secure_token,
    hash_password,
    verify_password,
    rate_limit_check,
    validate_url
)


class FileUploadSecurityTestCase(TestCase):
    """Test cases for file upload security"""
    
    def test_validate_file_extension(self):
        """Test file extension validation"""
        # Test valid extension
        file = SimpleUploadedFile("test.xlsx", b"content")
        is_valid, error = validate_file_upload(
            file,
            allowed_extensions=['.xlsx', '.xls'],
            max_size_mb=10
        )
        self.assertTrue(is_valid)
        
        # Test invalid extension
        file = SimpleUploadedFile("test.exe", b"content")
        is_valid, error = validate_file_upload(
            file,
            allowed_extensions=['.xlsx', '.xls'],
            max_size_mb=10
        )
        self.assertFalse(is_valid)
        self.assertIn('허용되지 않는 파일 형식', error)
    
    def test_validate_file_size(self):
        """Test file size validation"""
        # Test file within limit
        small_file = SimpleUploadedFile("test.xlsx", b"x" * 1024)  # 1KB
        is_valid, error = validate_file_upload(
            small_file,
            allowed_extensions=['.xlsx'],
            max_size_mb=1
        )
        self.assertTrue(is_valid)
        
        # Test file exceeding limit
        large_content = b"x" * (2 * 1024 * 1024)  # 2MB
        large_file = SimpleUploadedFile("test.xlsx", large_content)
        is_valid, error = validate_file_upload(
            large_file,
            allowed_extensions=['.xlsx'],
            max_size_mb=1
        )
        self.assertFalse(is_valid)
        self.assertIn('파일 크기가', error)
    
    def test_prevent_path_traversal(self):
        """Test prevention of path traversal attacks"""
        # Test dangerous filenames
        dangerous_names = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "test/../../../etc/shadow.xlsx",
            "test\\..\\..\\important.xlsx"
        ]
        
        for name in dangerous_names:
            file = SimpleUploadedFile(name, b"content")
            is_valid, error = validate_file_upload(
                file,
                allowed_extensions=['.xlsx'],
                max_size_mb=10
            )
            self.assertFalse(is_valid)
            self.assertIn('잘못된 파일 이름', error)


class InputSanitizationTestCase(TestCase):
    """Test cases for input sanitization"""
    
    def test_sanitize_html_input(self):
        """Test HTML sanitization"""
        # Test XSS attempts
        dangerous_inputs = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>"
        ]
        
        for dangerous in dangerous_inputs:
            sanitized = sanitize_input(dangerous)
            self.assertNotIn('<script>', sanitized)
            self.assertNotIn('javascript:', sanitized)
            self.assertNotIn('onerror=', sanitized)
            self.assertNotIn('onload=', sanitized)
    
    def test_preserve_safe_html(self):
        """Test that safe HTML is preserved"""
        safe_inputs = [
            "<p>This is a paragraph</p>",
            "<strong>Bold text</strong>",
            "<em>Italic text</em>",
            "<a href='https://example.com'>Link</a>"
        ]
        
        for safe in safe_inputs:
            sanitized = sanitize_input(safe, allow_html=True)
            # Basic tags should be preserved
            if '<p>' in safe:
                self.assertIn('<p>', sanitized)
            if '<strong>' in safe:
                self.assertIn('<strong>', sanitized)


class SQLInjectionTestCase(TestCase):
    """Test cases for SQL injection prevention"""
    
    def test_detect_sql_injection(self):
        """Test SQL injection detection"""
        sql_injection_attempts = [
            "1' OR '1'='1",
            "'; DROP TABLE users; --",
            "1 UNION SELECT * FROM passwords",
            "admin'--",
            "' OR 1=1--",
            "1; DELETE FROM employees WHERE 1=1;",
            "Robert'); DROP TABLE Students;--"
        ]
        
        for attempt in sql_injection_attempts:
            is_safe = not check_sql_injection(attempt)
            self.assertFalse(is_safe, f"SQL injection not detected: {attempt}")
    
    def test_allow_safe_input(self):
        """Test that safe input is allowed"""
        safe_inputs = [
            "John Doe",
            "john.doe@example.com",
            "Department of Technology",
            "Employee ID: 12345",
            "This is a normal comment."
        ]
        
        for safe in safe_inputs:
            is_safe = not check_sql_injection(safe)
            self.assertTrue(is_safe, f"Safe input incorrectly flagged: {safe}")


class AuthenticationSecurityTestCase(TestCase):
    """Test cases for authentication security"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "MySecurePassword123!"
        
        # Hash password
        hashed = hash_password(password)
        
        # Verify correct password
        self.assertTrue(verify_password(password, hashed))
        
        # Verify incorrect password
        self.assertFalse(verify_password("WrongPassword", hashed))
        
        # Ensure hash is different each time (salt)
        hashed2 = hash_password(password)
        self.assertNotEqual(hashed, hashed2)
    
    def test_secure_token_generation(self):
        """Test secure token generation"""
        token1 = generate_secure_token()
        token2 = generate_secure_token()
        
        # Tokens should be unique
        self.assertNotEqual(token1, token2)
        
        # Tokens should have sufficient length
        self.assertGreaterEqual(len(token1), 32)
        
        # Tokens should be URL-safe
        self.assertRegex(token1, r'^[A-Za-z0-9_-]+$')
    
    def test_password_requirements(self):
        """Test password strength requirements"""
        weak_passwords = [
            "123456",
            "password",
            "abc",
            "12345678",
            "qwerty"
        ]
        
        strong_passwords = [
            "MyStr0ng!Pass",
            "C0mpl3x&P@ssw0rd",
            "SecureP@ss2024!"
        ]
        
        # Implementation would check password strength
        # This is a placeholder for actual implementation


class ValidationTestCase(TestCase):
    """Test cases for input validation"""
    
    def test_email_validation(self):
        """Test email validation"""
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.kr",
            "admin+test@domain.org",
            "user_name@sub.domain.com"
        ]
        
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
            "user..name@example.com"
        ]
        
        for email in valid_emails:
            self.assertTrue(validate_email(email), f"Valid email rejected: {email}")
        
        for email in invalid_emails:
            self.assertFalse(validate_email(email), f"Invalid email accepted: {email}")
    
    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            "https://example.com",
            "http://sub.domain.com/path",
            "https://example.com:8080/path?query=value",
            "http://localhost:3000"
        ]
        
        invalid_urls = [
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "file:///etc/passwd",
            "not a url",
            "//example.com"  # Protocol-relative URL (potentially dangerous)
        ]
        
        for url in valid_urls:
            self.assertTrue(validate_url(url), f"Valid URL rejected: {url}")
        
        for url in invalid_urls:
            self.assertFalse(validate_url(url), f"Invalid URL accepted: {url}")


class RateLimitingTestCase(TestCase):
    """Test cases for rate limiting"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
    
    def test_rate_limit_by_ip(self):
        """Test rate limiting by IP address"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        # First few requests should pass
        for i in range(5):
            self.assertTrue(rate_limit_check(request, limit=10, window=60))
        
        # After limit, should be blocked
        for i in range(6):
            rate_limit_check(request, limit=10, window=60)
        
        # 11th request should be blocked
        self.assertFalse(rate_limit_check(request, limit=10, window=60))
    
    def test_rate_limit_by_user(self):
        """Test rate limiting by user"""
        request = self.factory.get('/')
        request.user = self.user
        
        # Test user-based rate limiting
        for i in range(5):
            self.assertTrue(rate_limit_check(
                request,
                limit=5,
                window=60,
                by_user=True
            ))
        
        # 6th request should be blocked
        self.assertFalse(rate_limit_check(
            request,
            limit=5,
            window=60,
            by_user=True
        ))


class CSRFProtectionTestCase(TestCase):
    """Test cases for CSRF protection"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
    
    def test_csrf_token_required(self):
        """Test that CSRF token is required for POST requests"""
        from django.middleware.csrf import CsrfViewMiddleware
        from django.http import HttpResponse
        
        def test_view(request):
            return HttpResponse('OK')
        
        # Create POST request without CSRF token
        request = self.factory.post('/', data={'test': 'data'})
        request.user = self.user
        
        middleware = CsrfViewMiddleware(test_view)
        response = middleware(request)
        
        # Should be rejected
        self.assertEqual(response.status_code, 403)