"""
Simple test script for job search API
"""

import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from job_profiles.models import JobProfile, JobRole, JobType, JobCategory
from job_search_recommend_api import (
    JobSearchEngine, 
    CareerPathAnalyzer, 
    JobSearchChatbotIntegration,
    SearchContext,
    SearchIntent
)


def test_basic_functionality():
    """Basic functionality test"""
    print("Job Search API Basic Test")
    print("=" * 40)
    
    try:
        # Test 1: Database data check
        categories = JobCategory.objects.filter(is_active=True).count()
        job_profiles = JobProfile.objects.filter(is_active=True).count()
        employees = Employee.objects.count()
        
        print(f"Job categories: {categories}")
        print(f"Job profiles: {job_profiles}")
        print(f"Employees: {employees}")
        
        # Test 2: Search engine test
        if job_profiles > 0:
            engine = JobSearchEngine()
            
            context = SearchContext(
                user_id="test_user",
                session_id="test_session",
                intent=SearchIntent.JOB_SEARCH,
                query="test",
                filters={}
            )
            
            results = engine.search_jobs(context)
            print(f"Search results: {len(results)}")
            
            if results:
                result = results[0]
                print(f"Sample result: {result.job_name}")
                print(f"Match score: {result.match_score:.1f}%")
            
            print("PASS: Search engine working")
        else:
            print("SKIP: No job profiles for testing")
        
        # Test 3: Chatbot test
        chatbot = JobSearchChatbotIntegration()
        response = chatbot.process_chat_query(
            user_query="test query",
            user_id="test_user",
            session_id="test_session"
        )
        
        print(f"Chatbot response intent: {response['intent']}")
        print("PASS: Chatbot integration working")
        
        print("\nAll basic tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    test_basic_functionality()