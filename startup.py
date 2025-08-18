#!/usr/bin/env python
"""
Startup script for initial data loading
"""
import os
import sys
import django
import traceback

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehr_system.settings")
    
    print("[STARTUP] Initializing Django...")
    django.setup()
    print("[STARTUP] Django setup complete")
    
    try:
        from django.core.management import call_command
        from job_profiles.models import JobCategory, JobType, JobRole, JobProfile
        
        print("[STARTUP] Models imported successfully")
        
        # Check if job profiles data exists
        category_count = JobCategory.objects.count()
        print(f"[STARTUP] Current categories: {category_count}")
        
        if category_count == 0:
            print("[STARTUP] No data found, loading job profiles...")
            try:
                call_command('load_all_jobs', '--noinput')
                new_count = JobCategory.objects.count()
                print(f"[STARTUP] Job profiles data loaded! Categories: {new_count}")
            except Exception as e:
                print(f"[STARTUP] Error loading job profiles: {e}")
                traceback.print_exc()
        else:
            print(f"[STARTUP] Job profiles data exists: {category_count} categories")
            
        # Final verification
        final_stats = {
            'categories': JobCategory.objects.count(),
            'types': JobType.objects.count(), 
            'roles': JobRole.objects.count(),
            'profiles': JobProfile.objects.count()
        }
        print(f"[STARTUP] Final stats: {final_stats}")
        
    except Exception as e:
        print(f"[STARTUP] Critical error: {e}")
        traceback.print_exc()