#!/usr/bin/env python
import os
import sys
import django

# Django 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def reset_admin_password():
    try:
        # admin 계정 찾기
        admin_user = User.objects.get(username='admin')
        
        # 비밀번호를 'admin123'으로 변경
        admin_user.password = make_password('admin123')
        admin_user.save()
        
        print("✅ 관리자 계정 비밀번호가 성공적으로 재설정되었습니다!")
        print("📋 로그인 정보:")
        print("   사용자명: admin")
        print("   비밀번호: admin123")
        
    except User.DoesNotExist:
        print("❌ admin 계정을 찾을 수 없습니다.")
        print("새로운 관리자 계정을 생성합니다...")
        
        # 새로운 관리자 계정 생성
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@okfinancial.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        print("✅ 새로운 관리자 계정이 생성되었습니다!")
        print("📋 로그인 정보:")
        print("   사용자명: admin")
        print("   비밀번호: admin123")
        
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    reset_admin_password() 