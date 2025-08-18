import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.urls import reverse

# Test URLs
urls = [
    ('evaluations:dashboard', 'Evaluation Dashboard'),
    ('evaluations:my_evaluations', 'My Evaluations'),
    ('evaluations:evaluator_dashboard', 'Evaluator Dashboard'),
    ('evaluations:hr_admin_dashboard', 'HR Admin Dashboard'),
]

print("=== Evaluation URL Test ===")
for url_name, description in urls:
    try:
        url = reverse(url_name)
        print(f"✓ {description}: {url}")
    except Exception as e:
        print(f"✗ {description}: ERROR - {e}")