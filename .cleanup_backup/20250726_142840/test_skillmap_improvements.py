"""
Test script for improved skillmap dashboard
"""

import os
import django
import json
import requests
from datetime import datetime

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from employees.models import Employee


def test_api_endpoints():
    """Test improved API endpoints"""
    print("Testing Improved SkillMap API Endpoints")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Create or get test user
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print("Created test admin user")
    
    # Login
    client.force_login(user)
    
    # Test 1: Basic API call
    print("\n1. Testing basic API call...")
    response = client.get('/api/skillmap/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"   Response status: {data.get('status')}")
        if data.get('status') == 'success':
            metrics = data['data']['metrics']
            print(f"   Total employees: {metrics['total_employees']}")
            print(f"   Total skills: {metrics['total_skills']}")
    
    # Test 2: Filtered API call
    print("\n2. Testing filtered API call...")
    response = client.get('/api/skillmap/', {'department': 'IT', 'format': 'summary'})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"   Format: summary")
        print(f"   Department filter: IT")
        if data.get('status') == 'success':
            metrics = data['data']['metrics']
            print(f"   Filtered employees: {metrics['total_employees']}")
    
    # Test 3: Pagination
    print("\n3. Testing pagination...")
    response = client.get('/api/skillmap/', {'page': 1, 'page_size': 10})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        if 'pagination' in data.get('data', {}):
            pagination = data['data']['pagination']
            print(f"   Total items: {pagination['total_items']}")
            print(f"   Total pages: {pagination['total_pages']}")
            print(f"   Current page: {pagination['current_page']}")
    
    # Test 4: Drill-down
    print("\n4. Testing drill-down...")
    response = client.get('/api/skillmap/drilldown/department/IT/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"   Drill-down level: department")
        print(f"   Drill-down value: IT")
        print(f"   Response status: {data.get('status')}")
    
    # Test 5: Skill gap analysis
    print("\n5. Testing skill gap analysis...")
    response = client.get('/api/skillmap/skill-gaps/', {'threshold': 50, 'top_n': 5})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('status') == 'success':
            analysis = data['analysis']
            print(f"   Skills with gaps: {analysis['skills_with_gaps']}")
            print(f"   Average gap rate: {analysis['avg_gap_rate']}%")
            print(f"   Top gaps found: {len(data['top_skill_gaps'])}")
    
    # Test 6: Export
    print("\n6. Testing export...")
    export_data = {
        'format': 'excel',
        'filters': {'department': 'IT'}
    }
    response = client.post('/api/skillmap/export/', 
                          json.dumps(export_data),
                          content_type='application/json')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"   Export status: {data.get('status')}")
        if data.get('status') == 'success':
            print(f"   Filename: {data['export_info']['filename']}")
            print(f"   Download URL: {data['download_url']}")
    
    # Test 7: Error handling
    print("\n7. Testing error handling...")
    response = client.get('/api/skillmap/', {'growth_level': 'invalid'})
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        data = json.loads(response.content)
        print(f"   Error handling works: {data.get('message')}")
    
    print("\n" + "=" * 50)
    print("All tests completed!")


def test_performance():
    """Test API performance"""
    print("\n\nPerformance Testing")
    print("=" * 50)
    
    client = Client()
    
    # Get admin user
    user = User.objects.get(username='admin')
    client.force_login(user)
    
    import time
    
    # Test response times
    endpoints = [
        ('/api/skillmap/?format=summary', 'Summary format'),
        ('/api/skillmap/?page_size=10', 'Paginated (10 items)'),
        ('/api/skillmap/skill-gaps/', 'Skill gaps analysis'),
    ]
    
    for endpoint, description in endpoints:
        start_time = time.time()
        response = client.get(endpoint)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to ms
        print(f"{description}: {response_time:.0f}ms (Status: {response.status_code})")
    
    print("\nPerformance testing completed!")


if __name__ == "__main__":
    print("SkillMap Dashboard Improvement Test")
    print("=" * 70)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_api_endpoints()
        test_performance()
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")