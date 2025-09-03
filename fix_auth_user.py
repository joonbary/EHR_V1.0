#!/usr/bin/env python
"""
Fix auth.User references to use settings.AUTH_USER_MODEL
작업지시서에 따른 리팩토링 스크립트
"""
import os
import re
from pathlib import Path

def fix_auth_user_references():
    """auth.User를 settings.AUTH_USER_MODEL로 변경"""
    
    # 수정이 필요한 앱들
    apps_to_fix = [
        'ai_chatbot',
        'ai_insights', 
        'ai_predictions',
        'airiss',
        'certifications',
        'employees',
        'job_profiles',
        'organization',
        'permissions',
        'recruitment',
        'reports'
    ]
    
    fixed_files = []
    
    for app in apps_to_fix:
        models_file = Path(f'D:/EHR_project/{app}/models.py')
        
        if models_file.exists():
            print(f"Checking {models_file}...")
            
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # auth.User 참조 찾기
            if "'auth.User'" in content or '"auth.User"' in content:
                # Django 설정 import 추가 (없는 경우)
                if 'from django.conf import settings' not in content:
                    # models import 다음에 추가
                    content = content.replace(
                        'from django.db import models',
                        'from django.db import models\nfrom django.conf import settings'
                    )
                
                # auth.User를 settings.AUTH_USER_MODEL로 변경
                content = content.replace("'auth.User'", "settings.AUTH_USER_MODEL")
                content = content.replace('"auth.User"', "settings.AUTH_USER_MODEL")
                
                # 파일 저장
                with open(models_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files.append(str(models_file))
                print(f"  ✅ Fixed: {models_file}")
    
    return fixed_files

if __name__ == "__main__":
    print("=== auth.User 참조 수정 시작 ===")
    print("작업지시서 2.1절: 코드 스멜 식별 - 잘못된 참조 수정\n")
    
    fixed = fix_auth_user_references()
    
    print(f"\n=== 수정 완료 ===")
    print(f"총 {len(fixed)}개 파일 수정됨")
    for f in fixed:
        print(f"  - {f}")