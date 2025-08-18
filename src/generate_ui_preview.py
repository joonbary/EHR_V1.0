#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI/UX 프리뷰 및 스타일 가이드 생성 스크립트
"""

from ui_sidebar_style_unify import UIDesignUnifier

def main():
    print("=" * 60)
    print("OK금융그룹 eHR 시스템 UI/UX 디자인 프리뷰 생성")
    print("=" * 60)
    
    unifier = UIDesignUnifier()
    
    # 1. 현재 스타일 분석
    issues = unifier.analyze_current_styles()
    print("\n분석 결과:")
    for issue_type, issue_list in issues.items():
        if issue_list:
            print(f"  - {issue_type}: {len(issue_list)}개 발견")
    
    # 2. 프리뷰 생성
    unifier.create_preview()
    
    # 3. 리포트 생성
    report = unifier.generate_report()
    print("\n개선 리포트가 생성되었습니다.")
    print(f"   - 프리뷰: {unifier.preview_dir / 'comparison.html'}")
    print(f"   - 스타일 가이드: {unifier.preview_dir / 'style-guide.html'}")
    print(f"   - 통합 CSS: {unifier.preview_dir / 'unified-design-system.css'}")

if __name__ == "__main__":
    main()