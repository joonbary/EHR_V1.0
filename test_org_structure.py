#!/usr/bin/env python
"""조직 구조 테스트"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import OrganizationStructure

print("=" * 60)
print("조직 구조 데이터 확인")
print("=" * 60)

# 조직 수 확인
count = OrganizationStructure.objects.count()
print(f"\n전체 조직 수: {count}개\n")

# 조직 목록
for org in OrganizationStructure.objects.all().order_by('org_level', 'sort_order'):
    parent_name = org.parent.org_name if org.parent else "없음"
    print(f"[{org.org_level}] {org.org_code}: {org.org_name}")
    print(f"    상위조직: {parent_name}")
    print(f"    상태: {org.status}")
    print(f"    경로: {org.full_path}")
    print()

print("=" * 60)