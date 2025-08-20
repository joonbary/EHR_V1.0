#!/usr/bin/env python
"""
Calibration 샘플 데이터 생성 스크립트
"""
import os
import sys
import django
from datetime import date, timedelta

# Django 환경 설정
sys.path.append('/d/EHR_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from evaluations.models import EvaluationPeriod, CalibrationSession
from employees.models import Employee

def create_sample_data():
    print("Calibration 샘플 데이터 생성 중...")
    
    try:
        # 평가기간 생성 또는 가져오기
        period, created = EvaluationPeriod.objects.get_or_create(
            year=2024,
            period_type='H2',
            defaults={
                'start_date': date(2024, 7, 1),
                'end_date': date(2024, 12, 31),
                'is_active': True,
                'status': 'ONGOING'
            }
        )
        print(f"평가기간: {period.year}년 {period.period_type} {'(생성)' if created else '(기존)'}")
        
        # Calibration 세션 생성
        sessions_data = [
            {
                'session_name': 'Q3 리더십 Calibration',
                'session_date': date.today() - timedelta(days=7),
                'agenda': '리더십 평가 기준 통일 및 등급 조정'
            },
            {
                'session_name': 'IT부서 전문성 Calibration',
                'session_date': date.today() - timedelta(days=3),
                'agenda': '기술직군 전문성 평가 기준 수립'
            },
            {
                'session_name': 'HR팀 기여도 Calibration',
                'session_date': date.today(),
                'agenda': '인사팀 기여도 측정 방법론 정립'
            }
        ]
        
        for data in sessions_data:
            session, created = CalibrationSession.objects.get_or_create(
                session_name=data['session_name'],
                defaults={
                    'evaluation_period': period,
                    'session_date': data['session_date'],
                    'agenda': data['agenda']
                }
            )
            print(f"세션: {session.session_name} {'(생성)' if created else '(기존)'}")
            
            # 참여자 추가 (임의로 첫 번째 직원들 선택)
            if created:
                employees = Employee.objects.filter(employment_status='재직')[:3]
                if employees:
                    session.participants.set(employees)
                    print(f"   참여자 {employees.count()}명 추가")
        
        print(f"\n총 {CalibrationSession.objects.count()}개의 Calibration 세션이 준비되었습니다!")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    create_sample_data()