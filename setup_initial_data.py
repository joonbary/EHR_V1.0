"""
Initial data setup script for EHR Evaluation System
Run this after migrations: python setup_initial_data.py
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_evaluation.settings')
django.setup()

from django.contrib.auth import get_user_model
from evaluations.models import EvaluationCriterion, EvaluationPeriod
from datetime import date, timedelta

User = get_user_model()

def create_evaluation_criteria():
    """Create default evaluation criteria"""
    criteria_data = [
        # Technical Skills
        {'name': '코드 품질', 'description': '깔끔하고 효율적인 코드 작성 능력', 'category': 'technical', 'weight': 2.0},
        {'name': '문제 해결', 'description': '복잡한 기술적 문제 해결 능력', 'category': 'technical', 'weight': 2.0},
        {'name': '기술 습득', 'description': '새로운 기술 학습 및 적용 능력', 'category': 'technical', 'weight': 1.5},
        {'name': '기술 전문성', 'description': '담당 분야의 전문 지식 수준', 'category': 'technical', 'weight': 2.0},
        
        # Soft Skills
        {'name': '커뮤니케이션', 'description': '효과적인 의사소통 능력', 'category': 'soft_skills', 'weight': 1.5},
        {'name': '팀워크', 'description': '팀원들과의 협업 능력', 'category': 'soft_skills', 'weight': 2.0},
        {'name': '리더십', 'description': '팀을 이끌고 동기부여하는 능력', 'category': 'soft_skills', 'weight': 1.5},
        {'name': '시간 관리', 'description': '효율적인 시간 관리와 우선순위 설정', 'category': 'soft_skills', 'weight': 1.0},
        
        # Performance
        {'name': '업무 완성도', 'description': '할당된 업무의 완성도와 품질', 'category': 'performance', 'weight': 2.5},
        {'name': '생산성', 'description': '효율적인 업무 처리 능력', 'category': 'performance', 'weight': 2.0},
        {'name': '마감 준수', 'description': '프로젝트 일정 준수율', 'category': 'performance', 'weight': 1.5},
        {'name': '품질 관리', 'description': '결과물의 품질 수준', 'category': 'performance', 'weight': 2.0},
        
        # Contribution
        {'name': '프로젝트 기여', 'description': '프로젝트 성공에 대한 기여도', 'category': 'contribution', 'weight': 2.5},
        {'name': '혁신 제안', 'description': '새로운 아이디어와 개선 제안', 'category': 'contribution', 'weight': 1.5},
        {'name': '지식 공유', 'description': '팀내 지식 공유와 멘토링', 'category': 'contribution', 'weight': 1.5},
        {'name': '고객 만족', 'description': '내외부 고객 만족도', 'category': 'contribution', 'weight': 2.0},
        
        # Growth & Development
        {'name': '자기 개발', 'description': '지속적인 학습과 개선 노력', 'category': 'growth', 'weight': 1.5},
        {'name': '목표 달성', 'description': '설정된 개인 목표 달성률', 'category': 'growth', 'weight': 2.0},
        {'name': '적응력', 'description': '변화에 대한 적응과 유연성', 'category': 'growth', 'weight': 1.5},
        {'name': '성장 잠재력', 'description': '미래 성장 가능성', 'category': 'growth', 'weight': 1.5},
    ]
    
    created_count = 0
    for data in criteria_data:
        criterion, created = EvaluationCriterion.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"Created criterion: {criterion.name}")
    
    print(f"\nTotal criteria created: {created_count}")
    return created_count

def create_evaluation_period():
    """Create current evaluation period"""
    today = date.today()
    start_date = date(today.year, (today.month - 1) // 3 * 3 + 1, 1)
    end_date = start_date + timedelta(days=89)  # Approximately 3 months
    
    period, created = EvaluationPeriod.objects.get_or_create(
        name=f"{today.year}년 {(today.month - 1) // 3 + 1}분기",
        defaults={
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True
        }
    )
    
    if created:
        print(f"Created evaluation period: {period.name}")
    else:
        print(f"Evaluation period already exists: {period.name}")
    
    return period

def create_sample_users():
    """Create sample users for testing"""
    users_data = [
        {
            'username': 'employee1',
            'email': 'employee1@example.com',
            'first_name': '김',
            'last_name': '직원',
            'role': 'employee',
            'department': '개발팀',
            'position': '선임 개발자',
            'employee_id': 'EMP001'
        },
        {
            'username': 'employee2',
            'email': 'employee2@example.com',
            'first_name': '이',
            'last_name': '사원',
            'role': 'employee',
            'department': '개발팀',
            'position': '주니어 개발자',
            'employee_id': 'EMP002'
        },
        {
            'username': 'evaluator1',
            'email': 'evaluator1@example.com',
            'first_name': '박',
            'last_name': '팀장',
            'role': 'evaluator',
            'department': '개발팀',
            'position': '팀장',
            'employee_id': 'MGR001'
        },
        {
            'username': 'hr1',
            'email': 'hr1@example.com',
            'first_name': '최',
            'last_name': '인사',
            'role': 'hr',
            'department': '인사팀',
            'position': 'HR 매니저',
            'employee_id': 'HR001'
        }
    ]
    
    created_count = 0
    for data in users_data:
        username = data.pop('username')
        email = data.pop('email')
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                **data
            }
        )
        
        if created:
            user.set_password('password123')  # Default password for testing
            user.save()
            created_count += 1
            print(f"Created user: {username} (password: password123)")
    
    print(f"\nTotal users created: {created_count}")
    return created_count

def main():
    print("=" * 50)
    print("EHR Evaluation System - Initial Data Setup")
    print("=" * 50)
    
    print("\n1. Creating evaluation criteria...")
    create_evaluation_criteria()
    
    print("\n2. Creating evaluation period...")
    create_evaluation_period()
    
    print("\n3. Creating sample users...")
    create_sample_users()
    
    # Create superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='관리자',
            role='admin',
            department='시스템',
            position='시스템 관리자',
            employee_id='ADM001'
        )
        print("\n4. Created superuser: admin (password: admin123)")
    
    print("\n" + "=" * 50)
    print("Initial setup completed successfully!")
    print("You can now login with:")
    print("  - Admin: admin / admin123")
    print("  - Evaluator: evaluator1 / password123")
    print("  - Employee: employee1 / password123")
    print("=" * 50)

if __name__ == '__main__':
    main()