#!/usr/bin/env python
"""
Startup script for initial data loading
"""
import os
import sys
import django
import traceback

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehr_evaluation.settings")
    
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
        
        # Check for active evaluation period
        from evaluations.models import EvaluationPeriod
        from datetime import date, timedelta
        
        active_period = EvaluationPeriod.objects.filter(is_active=True).first()
        if not active_period:
            print("[STARTUP] No active evaluation period found, creating one...")
            try:
                today = date.today()
                start_date = today - timedelta(days=30)
                end_date = today + timedelta(days=90)
                
                period = EvaluationPeriod.objects.create(
                    year=today.year,
                    period_type='H2' if today.month > 6 else 'H1',
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True,
                    status='ONGOING',
                )
                print(f"[STARTUP] Created evaluation period: {period.year} {period.period_type}")
            except Exception as e:
                print(f"[STARTUP] Error creating evaluation period: {e}")
        else:
            print(f"[STARTUP] Active evaluation period exists: {active_period.year} {active_period.period_type}")
        
    except Exception as e:
        print(f"[STARTUP] Critical error: {e}")
        traceback.print_exc()