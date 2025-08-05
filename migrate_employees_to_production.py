"""
로컬 데이터를 Railway 프로덕션으로 마이그레이션하는 스크립트
"""
import os
import sys
import json
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.core import serializers
from datetime import datetime

def export_local_data():
    """로컬 데이터를 JSON으로 내보내기"""
    print("=" * 50)
    print("로컬 데이터 내보내기 시작")
    print("=" * 50)
    
    # 모든 직원 데이터 가져오기
    employees = Employee.objects.all()
    total_count = employees.count()
    
    print(f"총 {total_count}명의 직원 데이터를 내보냅니다...")
    
    # JSON으로 직렬화
    data = serializers.serialize('json', employees, indent=2, use_natural_foreign_keys=True)
    
    # 파일로 저장
    filename = f'employees_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(data)
    
    print(f"✅ 데이터 내보내기 완료: {filename}")
    print(f"   - 총 {total_count}명의 직원 데이터")
    print(f"   - 파일 크기: {os.path.getsize(filename) / 1024:.2f} KB")
    
    # 샘플 데이터 출력
    sample_employees = employees[:5]
    print("\n📋 샘플 데이터 (처음 5명):")
    for emp in sample_employees:
        print(f"   - {emp.name} ({emp.email}) - {emp.department}/{emp.position}")
    
    return filename

def import_production_data(filename):
    """프로덕션 환경에서 데이터 가져오기"""
    print("=" * 50)
    print("프로덕션 데이터 가져오기 시작")
    print("=" * 50)
    
    if not os.path.exists(filename):
        print(f"❌ 파일을 찾을 수 없습니다: {filename}")
        return
    
    # 기존 데이터 확인
    existing_count = Employee.objects.count()
    print(f"현재 직원 수: {existing_count}명")
    
    if existing_count > 100:
        response = input("이미 많은 데이터가 있습니다. 계속하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("작업을 취소합니다.")
            return
    
    # JSON 파일 읽기
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"총 {len(data)}개의 레코드를 가져옵니다...")
    
    # 데이터 임포트
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for item in data:
        fields = item['fields']
        email = fields.get('email')
        
        # 이메일 중복 체크
        if Employee.objects.filter(email=email).exists():
            skip_count += 1
            print(f"⏭️  건너뛰기 (이미 존재): {email}")
            continue
        
        try:
            # 새 직원 생성
            employee = Employee.objects.create(
                name=fields.get('name'),
                email=email,
                department=fields.get('department'),
                position=fields.get('position'),
                new_position=fields.get('new_position', ''),
                job_group=fields.get('job_group', ''),
                job_type=fields.get('job_type', ''),
                job_role=fields.get('job_role', ''),
                growth_level=fields.get('growth_level', 1),
                employment_status=fields.get('employment_status', '재직'),
                hire_date=fields.get('hire_date'),
                phone=fields.get('phone', ''),
                address=fields.get('address', ''),
                emergency_contact=fields.get('emergency_contact', ''),
                emergency_relationship=fields.get('emergency_relationship', ''),
                manager_id=fields.get('manager')
            )
            success_count += 1
            print(f"✅ 생성됨: {employee.name} ({employee.email})")
            
        except Exception as e:
            error_count += 1
            print(f"❌ 오류: {email} - {str(e)}")
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("마이그레이션 완료!")
    print("=" * 50)
    print(f"✅ 성공: {success_count}명")
    print(f"⏭️  건너뛰기: {skip_count}명")
    print(f"❌ 실패: {error_count}명")
    print(f"📊 현재 총 직원 수: {Employee.objects.count()}명")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'import':
        # 프로덕션에서 실행: python migrate_employees_to_production.py import employees_export_xxx.json
        if len(sys.argv) > 2:
            import_production_data(sys.argv[2])
        else:
            print("사용법: python migrate_employees_to_production.py import <filename>")
    else:
        # 로컬에서 실행: python migrate_employees_to_production.py
        export_local_data()
        print("\n🚀 Railway에서 실행할 명령어:")
        print("   python migrate_employees_to_production.py import <생성된_파일명>")