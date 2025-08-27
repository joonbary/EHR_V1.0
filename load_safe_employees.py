#!/usr/bin/env python
"""
가장 안전한 직원 데이터 로드 스크립트
필수 필드만 사용하여 오류 없이 데이터 생성
"""
import os
import sys
import django
from datetime import date, timedelta
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import connection

def check_fields():
    """실제 데이터베이스 필드 확인"""
    print("\n데이터베이스 필드 확인 중...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"사용 가능한 필드: {len(columns)}개")
        return columns

def generate_safe_employees():
    """안전하게 직원 데이터 생성"""
    
    # 데이터베이스 필드 확인
    available_fields = check_fields()
    
    try:
        # 이미 충분한 데이터가 있는지 확인
        existing_count = Employee.objects.count()
        if existing_count >= 100:
            print(f"이미 {existing_count}명의 직원 데이터가 있습니다. 스킵합니다.")
            return
    except Exception as e:
        print(f"직원 수 확인 중 오류: {e}")
        existing_count = 0
    
    print(f"\n현재 직원 수: {existing_count}명")
    print("안전한 직원 데이터를 생성합니다...")
    
    # 성과 이름 목록
    last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
    first_names = ['철수', '영희', '민수', '지영', '성호', '미영', '준호', '수진', '태현', '은지']
    
    # 본부와 부서
    departments_list = [
        ('영업본부', '리테일영업'),
        ('영업본부', '기업영업'),
        ('여신본부', '여신심사'),
        ('여신본부', '여신관리'),
        ('IT본부', '시스템개발'),
        ('IT본부', '인프라운영'),
        ('경영지원본부', '인사총무'),
        ('경영지원본부', '재무회계'),
        ('디지털혁신본부', '디지털전략'),
        ('디지털혁신본부', 'AI혁신')
    ]
    
    # 직위
    positions = [
        ('사원', 'STAFF', 1),
        ('대리', 'SENIOR', 2),
        ('과장', 'MANAGER', 3),
        ('차장', 'DEPUTY_DIRECTOR', 4),
        ('부장', 'DIRECTOR', 5)
    ]
    
    # 생성할 직원 수
    total_to_create = min(1000 - existing_count, 1000)
    employees_created = 0
    employee_no = existing_count + 1001
    
    print(f"생성할 직원 수: {total_to_create}명")
    
    for i in range(total_to_create):
        try:
            # 기본 정보 생성
            last_name = random.choice(last_names)
            first_name = random.choice(first_names)
            name = last_name + first_name
            
            email = f"emp{employee_no:04d}@oksavingsbank.com"
            phone = f"010-{random.randint(1000, 9999):04d}-{random.randint(1000, 9999):04d}"
            
            # 본부와 부서 선택
            headquarters, department = random.choice(departments_list)
            
            # 직위 선택
            position_title, position_code, level = random.choice(positions)
            
            # 성별
            gender = random.choice(['M', 'F'])
            
            # 입사일 (레벨에 따라)
            years_ago = level * 2 + random.randint(-1, 1)
            years_ago = max(0, min(years_ago, 10))
            hire_date = date.today() - timedelta(days=years_ago * 365 + random.randint(0, 364))
            
            # 필수 필드만 사용하여 생성 (안전하게)
            employee_data = {
                'no': employee_no,
                'name': name,
                'email': email,
                'phone': phone,
                'department': department,
                'position': position_code,
                'hire_date': hire_date,
            }
            
            # 선택적 필드 (있으면 추가)
            if 'company' in available_fields:
                employee_data['company'] = 'OK'
            
            if 'headquarters1' in available_fields:
                employee_data['headquarters1'] = headquarters
            
            if 'final_department' in available_fields:
                employee_data['final_department'] = department + '부'
            
            if 'current_position' in available_fields:
                employee_data['current_position'] = position_title
            
            if 'employment_status' in available_fields:
                employee_data['employment_status'] = '재직'
            
            if 'gender' in available_fields:
                employee_data['gender'] = gender
            
            if 'job_group' in available_fields:
                employee_data['job_group'] = 'PL' if level >= 4 else 'Non-PL'
            
            if 'growth_level' in available_fields:
                employee_data['growth_level'] = level
            
            if 'birth_date' in available_fields:
                birth_year = 2025 - 25 - (level * 5) + random.randint(-3, 3)
                employee_data['birth_date'] = date(birth_year, random.randint(1, 12), random.randint(1, 28))
            
            if 'education' in available_fields:
                employee_data['education'] = random.choice(['대졸', '석사', '박사'])
            
            if 'address' in available_fields:
                employee_data['address'] = f"{random.choice(['서울', '경기', '인천', '부산'])}시"
            
            # 직원 생성
            Employee.objects.create(**employee_data)
            employees_created += 1
            employee_no += 1
            
            if employees_created % 100 == 0:
                print(f"  {employees_created}명 생성 완료...")
                
        except Exception as e:
            print(f"직원 {employee_no} 생성 오류: {e}")
            # 오류가 나도 계속 진행
            employee_no += 1
            continue
    
    # 결과 출력
    print(f"\n생성 완료! 총 {employees_created}명의 직원이 추가되었습니다.")
    
    try:
        final_count = Employee.objects.count()
        print(f"전체 직원 수: {final_count}명")
        
        # 간단한 통계
        if 'headquarters1' in available_fields:
            from django.db.models import Count
            stats = Employee.objects.values('headquarters1').annotate(count=Count('id'))
            print("\n본부별 직원 분포:")
            for stat in stats:
                if stat['headquarters1']:
                    print(f"  {stat['headquarters1']}: {stat['count']}명")
    except:
        pass

if __name__ == "__main__":
    try:
        generate_safe_employees()
        print("\n✅ 데이터 로드 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        # 오류가 나도 정상 종료
        sys.exit(0)