#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
base_simple.html에서 누락된 URL 참조 제거
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent

def fix_missing_urls():
    """base_simple.html에서 정의되지 않은 URL 제거"""
    base_simple_path = BASE_DIR / 'templates' / 'base_simple.html'
    
    if not base_simple_path.exists():
        print("✗ base_simple.html 파일을 찾을 수 없습니다.")
        return
    
    # 백업
    backup_path = str(base_simple_path) + '.bak'
    with open(base_simple_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    lines = content.split('\n')
    new_lines = []
    in_dashboard_section = False
    in_ai_section = False
    skip_until_close_li = False
    
    for i, line in enumerate(lines):
        # 대시보드 섹션 시작
        if '대시보드 섹션' in line and 'sidebar-nav-section' in line:
            in_dashboard_section = True
            new_lines.append(line)
            # 다음 라인도 추가 (섹션 타이틀)
            if i + 1 < len(lines):
                new_lines.append(lines[i + 1])
            new_lines.append('                <!-- 대시보드 메뉴 임시 제거')
            continue
            
        # AI 도구 섹션 시작
        if 'AI 도구 섹션' in line and 'sidebar-nav-section' in line:
            in_ai_section = True
            new_lines.append(line)
            # 다음 라인도 추가 (섹션 타이틀)
            if i + 1 < len(lines):
                new_lines.append(lines[i + 1])
            new_lines.append('                <!-- AI 도구 메뉴 임시 제거')
            continue
            
        # 섹션 종료
        if (in_dashboard_section or in_ai_section) and '</ul>' in line:
            new_lines.append('                -->')
            in_dashboard_section = False
            in_ai_section = False
            new_lines.append(line)
            continue
            
        # 대시보드 섹션이나 AI 섹션 내의 메뉴 아이템은 주석 처리
        if in_dashboard_section or in_ai_section:
            if '<li class="sidebar-nav-item">' in line:
                new_lines.append('                ' + line.strip())
            else:
                new_lines.append('                ' + line.strip() if line.strip() else '')
        else:
            new_lines.append(line)
    
    # 저장
    with open(base_simple_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✓ base_simple.html 수정 완료")
    print("  - 대시보드 섹션 메뉴 주석 처리")
    print("  - AI 도구 섹션 메뉴 주석 처리")

def main():
    print("="*60)
    print("누락된 URL 참조 제거")
    print("="*60)
    
    fix_missing_urls()
    
    print("\n완료!")
    print("서버를 재시작하세요: python manage.py runserver")
    print("="*60)

if __name__ == '__main__':
    main()