"""
Security utilities for the EHR system
"""
import html
import json
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder


def safe_json_script(data, element_id=None):
    """
    Safely render JSON data for use in JavaScript.
    Prevents XSS attacks by properly escaping data.
    
    Args:
        data: Python object to be converted to JSON
        element_id: Optional element ID for script tag
    
    Returns:
        Safe HTML string for template rendering
    """
    json_str = json.dumps(data, cls=DjangoJSONEncoder)
    # Escape for safe embedding in HTML
    json_str = json_str.replace('<', '\\u003c')
    json_str = json_str.replace('>', '\\u003e')
    json_str = json_str.replace('&', '\\u0026')
    
    if element_id:
        return mark_safe(f'<script id="{html.escape(element_id)}" type="application/json">{json_str}</script>')
    return mark_safe(json_str)


def sanitize_html(text):
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Args:
        text: Raw HTML text
    
    Returns:
        Sanitized HTML string
    """
    if not text:
        return ''
    
    # HTML escape all content
    return html.escape(text)


def validate_file_upload(file, allowed_extensions, max_size_mb=10):
    """
    Validate uploaded files for security.
    
    Args:
        file: Uploaded file object
        allowed_extensions: List of allowed file extensions (e.g., ['.pdf', '.xlsx'])
        max_size_mb: Maximum file size in megabytes
    
    Returns:
        Tuple (is_valid, error_message)
    """
    import os
    
    # Check file extension
    file_ext = os.path.splitext(file.name)[1].lower()
    if file_ext not in allowed_extensions:
        return False, f'허용되지 않은 파일 형식입니다. {allowed_extensions} 형식만 가능합니다.'
    
    # Check file size
    max_size = max_size_mb * 1024 * 1024  # Convert to bytes
    if file.size > max_size:
        return False, f'파일 크기가 {max_size_mb}MB를 초과합니다.'
    
    # Check for null bytes in filename (path traversal attack)
    if '\x00' in file.name:
        return False, '유효하지 않은 파일명입니다.'
    
    return True, None


def generate_secure_password():
    """
    Generate a secure random password.
    
    Returns:
        A secure random password string
    """
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(16))
    return password


def constant_time_compare(val1, val2):
    """
    Constant time comparison to prevent timing attacks.
    
    Args:
        val1: First value to compare
        val2: Second value to compare
    
    Returns:
        True if values are equal, False otherwise
    """
    import hmac
    return hmac.compare_digest(str(val1), str(val2))