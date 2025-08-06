#!/usr/bin/env python
"""
Startup script for initial data loading
"""
import os
import sys
import django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehr_system.settings")
    django.setup()
    
    from django.core.management import call_command
    from job_profiles.models import JobCategory
    
    # Check if job profiles data exists
    if JobCategory.objects.count() == 0:
        print("Loading job profiles data...")
        try:
            call_command('load_all_jobs', '--noinput')
            print("Job profiles data loaded successfully!")
        except Exception as e:
            print(f"Error loading job profiles: {e}")
    else:
        print(f"Job profiles data already exists: {JobCategory.objects.count()} categories")