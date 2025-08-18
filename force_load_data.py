#!/usr/bin/env python
"""
Railway에서 강제로 데이터 로드 (마이그레이션 오류 무시)
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def force_load_data():
    """마이그레이션 상태와 관계없이 데이터 로드"""
    print("=" * 60)
    print("FORCE LOADING DATA (Ignoring migration errors)")
    print("=" * 60)
    
    try:
        from employees.models import Employee
        
        # 현재 데이터 확인
        try:
            current_count = Employee.objects.count()
            print(f"Current employees in database: {current_count}")
        except Exception as e:
            print(f"Cannot count current employees: {e}")
            current_count = 0
        
        # 100명 미만이면 데이터 로드
        if current_count < 100:
            json_file = 'employees_only.json'
            
            if os.path.exists(json_file):
                print(f"\nLoading data from {json_file}...")
                
                try:
                    # Django loaddata 대신 직접 로드
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    loaded = 0
                    skipped = 0
                    failed = 0
                    
                    for item in data:
                        if item['model'] == 'employees.employee':
                            fields = item['fields']
                            pk = item.get('pk')
                            
                            try:
                                # 이미 존재하는지 확인
                                if pk and Employee.objects.filter(pk=pk).exists():
                                    skipped += 1
                                    continue
                                
                                # 이메일 중복 확인
                                email = fields.get('email')
                                if email and Employee.objects.filter(email=email).exists():
                                    skipped += 1
                                    continue
                                
                                # 새 직원 생성
                                employee = Employee.objects.create(
                                    name=fields.get('name', 'Unknown'),
                                    email=email or f'temp{loaded}@okgroup.com',
                                    department=fields.get('department', 'IT'),
                                    position=fields.get('position', 'STAFF'),
                                    employment_status=fields.get('employment_status', '재직'),
                                    hire_date=fields.get('hire_date', '2024-01-01'),
                                    phone=fields.get('phone', '010-0000-0000'),
                                    growth_level=fields.get('growth_level', 1)
                                )
                                loaded += 1
                                
                                if loaded % 100 == 0:
                                    print(f"  Loaded {loaded} employees...")
                                    
                            except Exception as e:
                                failed += 1
                                if failed < 5:  # 처음 5개 오류만 출력
                                    print(f"  Failed to load employee: {e}")
                    
                    print(f"\nResults:")
                    print(f"  Loaded: {loaded}")
                    print(f"  Skipped: {skipped}")
                    print(f"  Failed: {failed}")
                    
                    # 최종 카운트
                    final_count = Employee.objects.count()
                    print(f"\nFinal employee count: {final_count}")
                    
                except Exception as e:
                    print(f"JSON parsing error: {e}")
                    # 대체 방법: 기본 데이터 생성
                    print("\nCreating sample employees...")
                    for i in range(10):
                        try:
                            Employee.objects.create(
                                name=f"Sample Employee {i+1}",
                                email=f"sample{i+1}@okgroup.com",
                                department="IT",
                                position="STAFF",
                                employment_status="재직",
                                hire_date="2024-01-01",
                                phone=f"010-0000-{i+1:04d}",
                                growth_level=1
                            )
                        except:
                            pass
                    print(f"Created sample employees. Total: {Employee.objects.count()}")
            else:
                print(f"{json_file} not found!")
                print("Creating minimal test data...")
                # 최소한의 테스트 데이터 생성
                for i in range(5):
                    try:
                        Employee.objects.get_or_create(
                            email=f"test{i+1}@okgroup.com",
                            defaults={
                                'name': f"Test User {i+1}",
                                'department': 'IT',
                                'position': 'STAFF',
                                'employment_status': '재직',
                                'hire_date': '2024-01-01',
                                'phone': f'010-1234-{i+1:04d}',
                                'growth_level': 1
                            }
                        )
                    except:
                        pass
                print(f"Test data created. Total: {Employee.objects.count()}")
        else:
            print(f"Already have {current_count} employees. Skipping load.")
            
    except Exception as e:
        print(f"Critical error: {e}")
        print("Unable to load data due to database issues")
    
    print("=" * 60)
    print("Process completed")
    print("=" * 60)

if __name__ == "__main__":
    force_load_data()