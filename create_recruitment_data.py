import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from recruitment.models import RecruitmentStage

# 채용 단계 생성
stages = [
    {'order': 1, 'name': '서류 접수', 'description': '지원서 및 이력서 접수'},
    {'order': 2, 'name': '서류 심사', 'description': '지원자 서류 검토 및 평가'},
    {'order': 3, 'name': '1차 면접', 'description': '실무진 면접'},
    {'order': 4, 'name': '2차 면접', 'description': '임원 면접'},
    {'order': 5, 'name': '최종 합격', 'description': '채용 확정'},
]

for stage_data in stages:
    stage, created = RecruitmentStage.objects.get_or_create(
        name=stage_data['name'],
        defaults={
            'order': stage_data['order'],
            'description': stage_data['description'],
            'is_active': True
        }
    )
    if created:
        print(f"Created stage: {stage.name}")
    else:
        print(f"Stage already exists: {stage.name}")

print("\n채용 단계 생성 완료!")