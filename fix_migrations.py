#!/usr/bin/env python
"""Fix migration issues by faking initial migrations for AI modules."""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.core.management import call_command

def fake_initial_migrations():
    """Fake apply initial migrations for AI modules that already have tables."""
    
    ai_apps = [
        'ai_chatbot',
        'ai_coaching', 
        'ai_insights',
        'ai_interviewer',
        'ai_predictions',
        'ai_team_optimizer',
        'compensation'
    ]
    
    for app in ai_apps:
        try:
            print(f"Faking initial migration for {app}...")
            call_command('migrate', app, '0001_initial', '--fake')
            print(f"[OK] {app} initial migration faked")
        except Exception as e:
            print(f"[WARN] {app}: {str(e)}")
    
    # Now run full migration
    print("\nRunning full migrations...")
    try:
        call_command('migrate')
        print("[SUCCESS] All migrations completed successfully!")
    except Exception as e:
        print(f"[ERROR] Migration error: {str(e)}")

if __name__ == "__main__":
    fake_initial_migrations()