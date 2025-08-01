import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.urls import reverse

print("=== Checking Evaluation URLs ===")
try:
    print("Dashboard:", reverse('evaluations:dashboard'))
    print("My Evaluations:", reverse('evaluations:my_evaluations'))
    print("Evaluator Dashboard:", reverse('evaluations:evaluator_dashboard'))
    print("HR Admin:", reverse('evaluations:hr_admin_dashboard'))
except Exception as e:
    print("Error:", e)