import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

print("="*60)
print("모델 필드 확인")
print("="*60)

try:
    from employees.models import Employee
    print("\nEmployee 모델 필드:")
    for field in Employee._meta.get_fields():
        if not field.many_to_many and not field.one_to_many:
            print(f"  - {field.name}: {field.get_internal_type()}")
    
    # employment_status 필드 확인
    print("\nemployment_status 필드 타입:")
    status_field = Employee._meta.get_field('employment_status')
    print(f"  타입: {status_field.get_internal_type()}")
    if hasattr(status_field, 'choices') and status_field.choices:
        print("  선택지:", dict(status_field.choices))
    
    # 테스트 쿼리
    print("\n테스트 쿼리:")
    active_count = Employee.objects.filter(employment_status='active').count()
    print(f"  활성 직원 수: {active_count}")
    
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
