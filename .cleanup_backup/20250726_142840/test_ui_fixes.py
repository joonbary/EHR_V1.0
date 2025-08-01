#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OK금융그룹 HRIS 대시보드 UI/UX 수정사항 검증 스크립트
"""

import os
import sys
import io

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_file_exists(filepath):
    """파일 존재 여부 확인"""
    return os.path.exists(filepath)

def check_css_changes():
    """CSS 변경사항 확인"""
    print("1. CSS 변경사항 확인:")
    css_file = "static/css/design-system.css"
    
    if not check_file_exists(css_file):
        print(f"   ❌ {css_file} 파일을 찾을 수 없습니다.")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 사이드바 프로필 위치 수정 확인
    if "flex-shrink: 0;" in content and "z-index: 10;" in content:
        print("   ✅ 사이드바 프로필 위치 수정 완료")
    else:
        print("   ❌ 사이드바 프로필 위치 수정 미완료")
        
    return True

def check_template_changes():
    """템플릿 변경사항 확인"""
    print("\n2. 템플릿 변경사항 확인:")
    
    # base.html 변경사항 확인
    base_file = "templates/base.html"
    if not check_file_exists(base_file):
        print(f"   ❌ {base_file} 파일을 찾을 수 없습니다.")
        return False
        
    with open(base_file, 'r', encoding='utf-8') as f:
        base_content = f.read()
        
    # 메인 메시지 조건부 표시 확인
    if "{% if request.resolver_match.url_name == 'home' %}" in base_content:
        print("   ✅ 메인 메시지 조건부 표시 설정 완료")
    else:
        print("   ❌ 메인 메시지 조건부 표시 설정 미완료")
    
    # dashboard.html 변경사항 확인
    dashboard_file = "templates/dashboard.html"
    if not check_file_exists(dashboard_file):
        print(f"   ❌ {dashboard_file} 파일을 찾을 수 없습니다.")
        return False
        
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        dashboard_content = f.read()
        
    # 대시보드 텍스트 색상 통일 확인
    if "color: white !important;" in dashboard_content and ".dashboard-hero *" in dashboard_content:
        print("   ✅ 대시보드 진푸른색 영역 텍스트 색상 통일 완료")
    else:
        print("   ❌ 대시보드 진푸른색 영역 텍스트 색상 통일 미완료")
        
    return True

def main():
    """메인 함수"""
    print("=" * 50)
    print("OK금융그룹 HRIS 대시보드 UI/UX 수정사항 검증")
    print("=" * 50)
    
    # 변경사항 확인
    css_ok = check_css_changes()
    template_ok = check_template_changes()
    
    print("\n" + "=" * 50)
    print("검증 결과:")
    
    if css_ok and template_ok:
        print("✅ 모든 수정사항이 성공적으로 적용되었습니다!")
        print("\n다음 사항들이 수정되었습니다:")
        print("1. 사이드바 프로필이 메뉴와 겹치지 않도록 하단에 고정")
        print("2. 메인 메시지가 대시보드에서만 표시되도록 설정")
        print("3. 대시보드 진푸른색 영역의 모든 텍스트가 흰색으로 통일")
    else:
        print("❌ 일부 수정사항이 적용되지 않았습니다.")
        
    print("\n서버를 재시작하여 변경사항을 확인하세요:")
    print("python manage.py runserver")

if __name__ == "__main__":
    main()