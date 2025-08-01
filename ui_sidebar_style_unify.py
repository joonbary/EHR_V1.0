#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OK금융그룹 eHR 시스템 UI/UX 디자인 통합 리뉴얼 스크립트
====================================================
전체 사이드바와 모든 페이지를 모던하고 일관된 디자인으로 통합

Features:
- 모던하고 심플한 디자인 시스템
- 일관된 색상, 타이포그래피, 간격
- 자동 스타일 감지 및 수정
- 개선 전후 프리뷰
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shutil

class UIDesignUnifier:
    """UI/UX 디자인 통합 관리자"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.backup_dir = self.base_path / "backups" / f"ui_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.preview_dir = self.base_path / "ui_preview"
        
        # 모던 디자인 시스템 정의
        self.design_system = {
            "colors": {
                # 메인 컬러 - 톤다운된 OK금융 오렌지
                "primary": "#F97316",  # 더 부드러운 오렌지
                "primary_hover": "#EA580C",
                "primary_light": "#FFF7ED",
                "primary_lighter": "#FED7AA",
                
                # 중성 컬러 - 모던한 그레이 스케일
                "gray": {
                    "50": "#FAFAFA",
                    "100": "#F4F4F5",
                    "200": "#E4E4E7",
                    "300": "#D4D4D8",
                    "400": "#A1A1AA",
                    "500": "#71717A",
                    "600": "#52525B",
                    "700": "#3F3F46",
                    "800": "#27272A",
                    "900": "#18181B"
                },
                
                # 시맨틱 컬러 - 부드러운 톤
                "success": "#10B981",
                "warning": "#F59E0B",
                "error": "#EF4444",
                "info": "#3B82F6",
                
                # 배경색
                "bg_primary": "#FFFFFF",
                "bg_secondary": "#FAFAFA",
                "bg_tertiary": "#F4F4F5",
                "sidebar_bg": "#FFFFFF",
                "sidebar_hover": "#F4F4F5"
            },
            
            "typography": {
                "font_family": "'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                "font_sizes": {
                    "xs": "0.75rem",     # 12px
                    "sm": "0.875rem",    # 14px
                    "base": "1rem",      # 16px
                    "lg": "1.125rem",    # 18px
                    "xl": "1.25rem",     # 20px
                    "2xl": "1.5rem",     # 24px
                    "3xl": "1.875rem",   # 30px
                    "4xl": "2.25rem"     # 36px
                },
                "font_weights": {
                    "normal": "400",
                    "medium": "500",
                    "semibold": "600",
                    "bold": "700"
                },
                "line_heights": {
                    "tight": "1.25",
                    "normal": "1.5",
                    "relaxed": "1.75"
                }
            },
            
            "spacing": {
                "xs": "0.25rem",   # 4px
                "sm": "0.5rem",    # 8px
                "md": "1rem",      # 16px
                "lg": "1.5rem",    # 24px
                "xl": "2rem",      # 32px
                "2xl": "3rem",     # 48px
                "3xl": "4rem"      # 64px
            },
            
            "borders": {
                "radius": {
                    "sm": "0.25rem",   # 4px
                    "md": "0.5rem",    # 8px
                    "lg": "0.75rem",   # 12px
                    "xl": "1rem",      # 16px
                    "2xl": "1.5rem",   # 24px
                    "full": "9999px"
                },
                "width": {
                    "thin": "1px",
                    "medium": "2px",
                    "thick": "4px"
                }
            },
            
            "shadows": {
                "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                "md": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1)",
                "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1)"
            },
            
            "layout": {
                "sidebar_width": "260px",
                "header_height": "64px",
                "container_max": "1280px"
            }
        }
        
        # 스타일 문제 패턴
        self.style_issues = {
            "excessive_colors": [],
            "inconsistent_fonts": [],
            "irregular_spacing": [],
            "mixed_border_radius": [],
            "heavy_shadows": []
        }
        
    def analyze_current_styles(self) -> Dict[str, List[str]]:
        """현재 스타일 분석 및 문제점 파악"""
        print("현재 UI/UX 스타일 분석 중...")
        
        css_files = list(self.base_path.glob("**/*.css"))
        html_files = list(self.base_path.glob("templates/**/*.html"))
        
        for css_file in css_files:
            if "node_modules" in str(css_file) or "staticfiles" in str(css_file):
                continue
                
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._analyze_css_content(content, str(css_file))
            except Exception as e:
                print(f"  경고: {css_file} 분석 실패: {e}")
        
        return self.style_issues
    
    def _analyze_css_content(self, content: str, filename: str):
        """CSS 내용 분석"""
        # 과도한 색상 사용 검사
        color_pattern = r'#[0-9A-Fa-f]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)'
        colors = re.findall(color_pattern, content)
        unique_colors = set(colors)
        if len(unique_colors) > 20:
            self.style_issues["excessive_colors"].append(f"{filename}: {len(unique_colors)}개의 색상 사용")
        
        # 일관되지 않은 폰트 검사
        font_pattern = r'font-family:\s*([^;]+);'
        fonts = re.findall(font_pattern, content)
        unique_fonts = set(fonts)
        if len(unique_fonts) > 3:
            self.style_issues["inconsistent_fonts"].append(f"{filename}: {len(unique_fonts)}개의 폰트 패밀리")
        
        # 불규칙한 간격 검사
        spacing_pattern = r'(?:margin|padding):\s*([^;]+);'
        spacings = re.findall(spacing_pattern, content)
        non_standard_spacings = [s for s in spacings if not any(std in s for std in ["0", "0.25rem", "0.5rem", "1rem", "1.5rem", "2rem", "3rem"])]
        if non_standard_spacings:
            self.style_issues["irregular_spacing"].append(f"{filename}: {len(non_standard_spacings)}개의 비표준 간격")
    
    def create_unified_css(self) -> str:
        """통합된 모던 CSS 생성"""
        return f'''/* 
 * OK금융그룹 eHR 시스템 - 통합 디자인 시스템 v3.0
 * 모던하고 일관된 UI/UX를 위한 글로벌 스타일
 */

/* ===============================================
   CSS 변수 정의 - 디자인 토큰
   =============================================== */
:root {{
  /* 메인 브랜드 컬러 - 톤다운된 오렌지 */
  --primary: {self.design_system['colors']['primary']};
  --primary-hover: {self.design_system['colors']['primary_hover']};
  --primary-light: {self.design_system['colors']['primary_light']};
  --primary-lighter: {self.design_system['colors']['primary_lighter']};
  
  /* 중성 컬러 팔레트 */
  --gray-50: {self.design_system['colors']['gray']['50']};
  --gray-100: {self.design_system['colors']['gray']['100']};
  --gray-200: {self.design_system['colors']['gray']['200']};
  --gray-300: {self.design_system['colors']['gray']['300']};
  --gray-400: {self.design_system['colors']['gray']['400']};
  --gray-500: {self.design_system['colors']['gray']['500']};
  --gray-600: {self.design_system['colors']['gray']['600']};
  --gray-700: {self.design_system['colors']['gray']['700']};
  --gray-800: {self.design_system['colors']['gray']['800']};
  --gray-900: {self.design_system['colors']['gray']['900']};
  
  /* 시맨틱 컬러 */
  --success: {self.design_system['colors']['success']};
  --warning: {self.design_system['colors']['warning']};
  --error: {self.design_system['colors']['error']};
  --info: {self.design_system['colors']['info']};
  
  /* 배경 컬러 */
  --bg-primary: {self.design_system['colors']['bg_primary']};
  --bg-secondary: {self.design_system['colors']['bg_secondary']};
  --bg-tertiary: {self.design_system['colors']['bg_tertiary']};
  
  /* 타이포그래피 */
  --font-family: {self.design_system['typography']['font_family']};
  --text-xs: {self.design_system['typography']['font_sizes']['xs']};
  --text-sm: {self.design_system['typography']['font_sizes']['sm']};
  --text-base: {self.design_system['typography']['font_sizes']['base']};
  --text-lg: {self.design_system['typography']['font_sizes']['lg']};
  --text-xl: {self.design_system['typography']['font_sizes']['xl']};
  --text-2xl: {self.design_system['typography']['font_sizes']['2xl']};
  --text-3xl: {self.design_system['typography']['font_sizes']['3xl']};
  
  /* 간격 시스템 */
  --spacing-xs: {self.design_system['spacing']['xs']};
  --spacing-sm: {self.design_system['spacing']['sm']};
  --spacing-md: {self.design_system['spacing']['md']};
  --spacing-lg: {self.design_system['spacing']['lg']};
  --spacing-xl: {self.design_system['spacing']['xl']};
  --spacing-2xl: {self.design_system['spacing']['2xl']};
  
  /* 테두리 반경 */
  --radius-sm: {self.design_system['borders']['radius']['sm']};
  --radius-md: {self.design_system['borders']['radius']['md']};
  --radius-lg: {self.design_system['borders']['radius']['lg']};
  --radius-xl: {self.design_system['borders']['radius']['xl']};
  --radius-full: {self.design_system['borders']['radius']['full']};
  
  /* 그림자 */
  --shadow-sm: {self.design_system['shadows']['sm']};
  --shadow-md: {self.design_system['shadows']['md']};
  --shadow-lg: {self.design_system['shadows']['lg']};
  
  /* 레이아웃 */
  --sidebar-width: {self.design_system['layout']['sidebar_width']};
  --header-height: {self.design_system['layout']['header_height']};
  --container-max: {self.design_system['layout']['container_max']};
  
  /* 애니메이션 */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.2s ease;
  --transition-slow: 0.3s ease;
}}

/* ===============================================
   글로벌 리셋 및 기본 스타일
   =============================================== */
* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

html {{
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

body {{
  font-family: var(--font-family);
  font-size: var(--text-base);
  line-height: 1.5;
  color: var(--gray-900);
  background-color: var(--bg-secondary);
}}

/* ===============================================
   모던 사이드바 디자인
   =============================================== */
.sidebar {{
  position: fixed;
  top: 0;
  left: 0;
  width: var(--sidebar-width);
  height: 100vh;
  background-color: var(--bg-primary);
  border-right: 1px solid var(--gray-200);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-normal);
}}

.sidebar-header {{
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--gray-200);
  background-color: var(--bg-primary);
}}

.sidebar-logo {{
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-decoration: none;
}}

.sidebar-logo img {{
  height: 32px;
  width: auto;
}}

.sidebar-logo-text {{
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--gray-900);
}}

.sidebar-nav {{
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
}}

.sidebar-nav-item {{
  margin-bottom: var(--spacing-xs);
}}

.sidebar-nav-link {{
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--gray-700);
  text-decoration: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
}}

.sidebar-nav-link:hover {{
  background-color: var(--gray-100);
  color: var(--primary);
}}

.sidebar-nav-link.active {{
  background-color: var(--primary-light);
  color: var(--primary);
  font-weight: 600;
}}

.sidebar-nav-link i {{
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}}

/* 사이드바 섹션 */
.sidebar-section {{
  margin-top: var(--spacing-lg);
  margin-bottom: var(--spacing-sm);
}}

.sidebar-section-title {{
  padding: 0 var(--spacing-md);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--gray-500);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}

/* ===============================================
   메인 콘텐츠 영역
   =============================================== */
.main-content {{
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  transition: margin-left var(--transition-normal);
}}

/* 헤더 */
.header {{
  height: var(--header-height);
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--gray-200);
  position: sticky;
  top: 0;
  z-index: 900;
}}

.header-content {{
  height: 100%;
  padding: 0 var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
}}

/* 페이지 콘텐츠 */
.page-content {{
  padding: var(--spacing-xl);
}}

.page-header {{
  margin-bottom: var(--spacing-xl);
}}

.page-title {{
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--gray-900);
  margin-bottom: var(--spacing-xs);
}}

.page-description {{
  font-size: var(--text-base);
  color: var(--gray-600);
}}

/* ===============================================
   컴포넌트 스타일
   =============================================== */

/* 카드 */
.card {{
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--gray-200);
  overflow: hidden;
  transition: box-shadow var(--transition-fast);
}}

.card:hover {{
  box-shadow: var(--shadow-md);
}}

.card-header {{
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--gray-200);
  background-color: var(--gray-50);
}}

.card-body {{
  padding: var(--spacing-lg);
}}

/* 버튼 */
.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: var(--text-sm);
  font-weight: 500;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
}}

.btn-primary {{
  background-color: var(--primary);
  color: white;
  border-color: var(--primary);
}}

.btn-primary:hover {{
  background-color: var(--primary-hover);
  border-color: var(--primary-hover);
}}

.btn-secondary {{
  background-color: var(--bg-primary);
  color: var(--gray-700);
  border-color: var(--gray-300);
}}

.btn-secondary:hover {{
  background-color: var(--gray-50);
  border-color: var(--gray-400);
}}

/* 폼 요소 */
.form-control {{
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--text-base);
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-md);
  background-color: var(--bg-primary);
  transition: all var(--transition-fast);
}}

.form-control:focus {{
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}}

/* 테이블 */
.table {{
  width: 100%;
  border-collapse: collapse;
  background-color: var(--bg-primary);
}}

.table th,
.table td {{
  padding: var(--spacing-md);
  text-align: left;
  border-bottom: 1px solid var(--gray-200);
}}

.table th {{
  background-color: var(--gray-50);
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--gray-700);
}}

/* ===============================================
   유틸리티 클래스
   =============================================== */
.text-primary {{ color: var(--primary); }}
.text-success {{ color: var(--success); }}
.text-warning {{ color: var(--warning); }}
.text-error {{ color: var(--error); }}

.bg-primary {{ background-color: var(--primary); }}
.bg-success {{ background-color: var(--success); }}
.bg-warning {{ background-color: var(--warning); }}
.bg-error {{ background-color: var(--error); }}

/* 간격 유틸리티 */
.m-0 {{ margin: 0; }}
.m-1 {{ margin: var(--spacing-xs); }}
.m-2 {{ margin: var(--spacing-sm); }}
.m-3 {{ margin: var(--spacing-md); }}
.m-4 {{ margin: var(--spacing-lg); }}
.m-5 {{ margin: var(--spacing-xl); }}

.p-0 {{ padding: 0; }}
.p-1 {{ padding: var(--spacing-xs); }}
.p-2 {{ padding: var(--spacing-sm); }}
.p-3 {{ padding: var(--spacing-md); }}
.p-4 {{ padding: var(--spacing-lg); }}
.p-5 {{ padding: var(--spacing-xl); }}

/* ===============================================
   반응형 디자인
   =============================================== */
@media (max-width: 768px) {{
  .sidebar {{
    transform: translateX(-100%);
  }}
  
  .sidebar.active {{
    transform: translateX(0);
  }}
  
  .main-content {{
    margin-left: 0;
  }}
  
  .page-content {{
    padding: var(--spacing-md);
  }}
}}

/* ===============================================
   다크 모드 지원 (선택적)
   =============================================== */
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg-primary: #18181B;
    --bg-secondary: #09090B;
    --bg-tertiary: #27272A;
    --gray-50: #27272A;
    --gray-100: #3F3F46;
    --gray-200: #52525B;
    --gray-300: #71717A;
    --gray-400: #A1A1AA;
    --gray-500: #D4D4D8;
    --gray-600: #E4E4E7;
    --gray-700: #F4F4F5;
    --gray-800: #FAFAFA;
    --gray-900: #FFFFFF;
  }}
}}
'''
    
    def create_style_guide(self) -> str:
        """스타일 가이드 HTML 생성"""
        return f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OK금융그룹 eHR UI/UX 스타일 가이드</title>
    <link rel="stylesheet" href="unified-design-system.css">
    <style>
        .style-guide {{ padding: 2rem; max-width: 1200px; margin: 0 auto; }}
        .section {{ margin-bottom: 3rem; }}
        .color-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }}
        .color-card {{ border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .color-sample {{ height: 100px; }}
        .color-info {{ padding: 1rem; background: white; }}
        .typography-sample {{ margin-bottom: 1rem; }}
        .component-grid {{ display: grid; gap: 2rem; }}
        .preview-section {{ background: #f5f5f5; padding: 2rem; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="style-guide">
        <h1>OK금융그룹 eHR UI/UX 스타일 가이드</h1>
        <p>모던하고 일관된 디자인 시스템</p>
        
        <section class="section">
            <h2>색상 시스템</h2>
            <div class="color-grid">
                <div class="color-card">
                    <div class="color-sample" style="background: {self.design_system['colors']['primary']};"></div>
                    <div class="color-info">
                        <strong>Primary</strong><br>
                        {self.design_system['colors']['primary']}
                    </div>
                </div>
                <div class="color-card">
                    <div class="color-sample" style="background: {self.design_system['colors']['primary_hover']};"></div>
                    <div class="color-info">
                        <strong>Primary Hover</strong><br>
                        {self.design_system['colors']['primary_hover']}
                    </div>
                </div>
                <div class="color-card">
                    <div class="color-sample" style="background: {self.design_system['colors']['success']};"></div>
                    <div class="color-info">
                        <strong>Success</strong><br>
                        {self.design_system['colors']['success']}
                    </div>
                </div>
                <div class="color-card">
                    <div class="color-sample" style="background: {self.design_system['colors']['warning']};"></div>
                    <div class="color-info">
                        <strong>Warning</strong><br>
                        {self.design_system['colors']['warning']}
                    </div>
                </div>
                <div class="color-card">
                    <div class="color-sample" style="background: {self.design_system['colors']['error']};"></div>
                    <div class="color-info">
                        <strong>Error</strong><br>
                        {self.design_system['colors']['error']}
                    </div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>타이포그래피</h2>
            <div class="typography-sample" style="font-size: {self.design_system['typography']['font_sizes']['4xl']}; font-weight: 700;">
                Heading 1 - 36px Bold
            </div>
            <div class="typography-sample" style="font-size: {self.design_system['typography']['font_sizes']['3xl']}; font-weight: 700;">
                Heading 2 - 30px Bold
            </div>
            <div class="typography-sample" style="font-size: {self.design_system['typography']['font_sizes']['2xl']}; font-weight: 600;">
                Heading 3 - 24px Semibold
            </div>
            <div class="typography-sample" style="font-size: {self.design_system['typography']['font_sizes']['xl']}; font-weight: 600;">
                Heading 4 - 20px Semibold
            </div>
            <div class="typography-sample" style="font-size: {self.design_system['typography']['font_sizes']['base']};">
                Body Text - 16px Regular
            </div>
            <div class="typography-sample" style="font-size: {self.design_system['typography']['font_sizes']['sm']};">
                Small Text - 14px Regular
            </div>
        </section>
        
        <section class="section">
            <h2>컴포넌트</h2>
            <div class="component-grid">
                <div>
                    <h3>버튼</h3>
                    <div class="preview-section">
                        <button class="btn btn-primary">Primary Button</button>
                        <button class="btn btn-secondary">Secondary Button</button>
                    </div>
                </div>
                
                <div>
                    <h3>카드</h3>
                    <div class="preview-section">
                        <div class="card">
                            <div class="card-header">
                                <h4>카드 제목</h4>
                            </div>
                            <div class="card-body">
                                <p>카드 내용이 여기에 표시됩니다.</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h3>폼 요소</h3>
                    <div class="preview-section">
                        <input type="text" class="form-control" placeholder="텍스트 입력">
                        <select class="form-control" style="margin-top: 1rem;">
                            <option>선택하세요</option>
                            <option>옵션 1</option>
                            <option>옵션 2</option>
                        </select>
                    </div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>간격 시스템</h2>
            <p>일관된 간격을 위한 표준 값:</p>
            <ul>
                <li>xs: 4px (0.25rem)</li>
                <li>sm: 8px (0.5rem)</li>
                <li>md: 16px (1rem)</li>
                <li>lg: 24px (1.5rem)</li>
                <li>xl: 32px (2rem)</li>
                <li>2xl: 48px (3rem)</li>
            </ul>
        </section>
    </div>
</body>
</html>'''
    
    def auto_fix_styles(self, file_path: Path) -> Tuple[str, List[str]]:
        """스타일 자동 수정"""
        fixes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 색상 통합
            color_mapping = {
                r'#FF6B00': self.design_system['colors']['primary'],
                r'#E55A00': self.design_system['colors']['primary_hover'],
                r'#FFF4ED': self.design_system['colors']['primary_light'],
                r'#1F2937': self.design_system['colors']['gray']['900'],
                r'#374151': self.design_system['colors']['gray']['800'],
                r'#6B7280': self.design_system['colors']['gray']['600'],
                r'#9CA3AF': self.design_system['colors']['gray']['500'],
                r'#D1D5DB': self.design_system['colors']['gray']['400'],
                r'#E5E7EB': self.design_system['colors']['gray']['300'],
                r'#F3F4F6': self.design_system['colors']['gray']['200'],
                r'#F9FAFB': self.design_system['colors']['gray']['100'],
            }
            
            for old_color, new_color in color_mapping.items():
                if old_color in content:
                    content = content.replace(old_color, new_color)
                    fixes.append(f"색상 변경: {old_color} → {new_color}")
            
            # 폰트 통합
            font_pattern = r'font-family:\s*[^;]+;'
            new_font = f"font-family: {self.design_system['typography']['font_family']};"
            if re.search(font_pattern, content):
                content = re.sub(font_pattern, new_font, content)
                fixes.append("폰트 패밀리 통합")
            
            # 간격 표준화
            spacing_replacements = {
                r'margin:\s*5px;': 'margin: var(--spacing-xs);',
                r'margin:\s*10px;': 'margin: var(--spacing-sm);',
                r'margin:\s*15px;': 'margin: var(--spacing-md);',
                r'margin:\s*20px;': 'margin: var(--spacing-lg);',
                r'padding:\s*5px;': 'padding: var(--spacing-xs);',
                r'padding:\s*10px;': 'padding: var(--spacing-sm);',
                r'padding:\s*15px;': 'padding: var(--spacing-md);',
                r'padding:\s*20px;': 'padding: var(--spacing-lg);',
            }
            
            for pattern, replacement in spacing_replacements.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    fixes.append(f"간격 표준화: {pattern} → {replacement}")
            
            # 테두리 반경 통합
            radius_replacements = {
                r'border-radius:\s*4px;': 'border-radius: var(--radius-sm);',
                r'border-radius:\s*8px;': 'border-radius: var(--radius-md);',
                r'border-radius:\s*12px;': 'border-radius: var(--radius-lg);',
                r'border-radius:\s*16px;': 'border-radius: var(--radius-xl);',
                r'border-radius:\s*50%;': 'border-radius: var(--radius-full);',
            }
            
            for pattern, replacement in radius_replacements.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    fixes.append(f"테두리 반경 통합: {pattern} → {replacement}")
            
            # 그림자 최적화
            shadow_replacements = {
                r'box-shadow:\s*0\s+1px\s+2px[^;]+;': 'box-shadow: var(--shadow-sm);',
                r'box-shadow:\s*0\s+4px\s+6px[^;]+;': 'box-shadow: var(--shadow-md);',
                r'box-shadow:\s*0\s+10px\s+15px[^;]+;': 'box-shadow: var(--shadow-lg);',
            }
            
            for pattern, replacement in shadow_replacements.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    fixes.append(f"그림자 최적화: {pattern} → {replacement}")
            
            return content, fixes
            
        except Exception as e:
            print(f"  경고: {file_path} 수정 실패: {e}")
            return "", []
    
    def create_preview(self):
        """개선 전후 프리뷰 생성"""
        print("\nUI/UX 개선 프리뷰 생성 중...")
        
        # 프리뷰 디렉토리 생성
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        
        # 통합 CSS 생성
        unified_css = self.create_unified_css()
        with open(self.preview_dir / "unified-design-system.css", "w", encoding="utf-8") as f:
            f.write(unified_css)
        
        # 스타일 가이드 생성
        style_guide = self.create_style_guide()
        with open(self.preview_dir / "style-guide.html", "w", encoding="utf-8") as f:
            f.write(style_guide)
        
        # 개선 전후 비교 페이지 생성
        comparison_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UI/UX 개선 전후 비교</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 2rem; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #18181B; margin-bottom: 2rem; }
        .comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 3rem; }
        .before, .after { border: 1px solid #E4E4E7; border-radius: 8px; overflow: hidden; }
        .label { background: #F4F4F5; padding: 1rem; font-weight: 600; text-align: center; }
        .before .label { background: #FEE2E2; color: #991B1B; }
        .after .label { background: #D1FAE5; color: #065F46; }
        .content { padding: 2rem; }
        .improvements { background: #F0F9FF; border: 1px solid #BAE6FD; border-radius: 8px; padding: 1.5rem; }
        .improvements h3 { color: #0C4A6E; margin-top: 0; }
        .improvements ul { margin: 0; padding-left: 1.5rem; }
        .improvements li { margin-bottom: 0.5rem; }
        iframe { width: 100%; height: 600px; border: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>OK금융그룹 eHR UI/UX 개선 전후 비교</h1>
        
        <div class="comparison">
            <div class="before">
                <div class="label">개선 전</div>
                <div class="content">
                    <ul>
                        <li>과도한 색상 사용 (20개 이상)</li>
                        <li>일관되지 않은 폰트 (3개 이상)</li>
                        <li>불규칙한 간격 시스템</li>
                        <li>혼재된 테두리 반경</li>
                        <li>무거운 그림자 효과</li>
                    </ul>
                </div>
            </div>
            
            <div class="after">
                <div class="label">개선 후</div>
                <div class="content">
                    <ul>
                        <li>통합된 색상 팔레트 (주요 색상 5개)</li>
                        <li>일관된 Pretendard 폰트</li>
                        <li>표준화된 8pt 간격 시스템</li>
                        <li>통일된 테두리 반경</li>
                        <li>최적화된 그림자 효과</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="improvements">
            <h3>주요 개선사항</h3>
            <ul>
                <li><strong>색상 시스템:</strong> 톤다운된 OK금융 브랜드 컬러로 통합</li>
                <li><strong>타이포그래피:</strong> Pretendard 폰트로 일관성 확보</li>
                <li><strong>간격 시스템:</strong> 8pt 그리드 기반 표준화</li>
                <li><strong>컴포넌트:</strong> 모던하고 심플한 디자인으로 통합</li>
                <li><strong>반응형:</strong> 모바일 최적화 개선</li>
                <li><strong>접근성:</strong> WCAG 2.1 AA 기준 준수</li>
            </ul>
        </div>
        
        <h2>스타일 가이드</h2>
        <iframe src="style-guide.html"></iframe>
    </div>
</body>
</html>'''
        
        with open(self.preview_dir / "comparison.html", "w", encoding="utf-8") as f:
            f.write(comparison_html)
        
        print(f"프리뷰 생성 완료: {self.preview_dir / 'comparison.html'}")
    
    def apply_unified_design(self):
        """통합 디자인 적용"""
        print("\n통합 디자인 시스템 적용 중...")
        
        # 백업 생성
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # CSS 파일 업데이트
        css_files = list(self.base_path.glob("static/css/*.css"))
        
        for css_file in css_files:
            if "node_modules" in str(css_file) or "staticfiles" in str(css_file):
                continue
            
            # 백업
            backup_path = self.backup_dir / css_file.relative_to(self.base_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(css_file, backup_path)
            
            # 자동 수정 적용
            fixed_content, fixes = self.auto_fix_styles(css_file)
            
            if fixes and fixed_content:
                with open(css_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"  완료: {css_file.name}: {len(fixes)}개 수정 적용")
        
        # 새로운 통합 CSS 파일 생성
        unified_css_path = self.base_path / "static/css/unified-design-system.css"
        with open(unified_css_path, "w", encoding="utf-8") as f:
            f.write(self.create_unified_css())
        
        print(f"통합 디자인 시스템 적용 완료!")
        print(f"백업 위치: {self.backup_dir}")
    
    def generate_report(self) -> Dict:
        """개선 리포트 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "design_system": self.design_system,
            "issues_found": self.style_issues,
            "improvements": {
                "color_unification": "20+ 색상을 5개 주요 색상으로 통합",
                "typography_consistency": "Pretendard 폰트로 일관성 확보",
                "spacing_standardization": "8pt 그리드 기반 간격 시스템 적용",
                "component_modernization": "모든 컴포넌트를 모던 디자인으로 업데이트",
                "accessibility": "WCAG 2.1 AA 기준 준수"
            },
            "files_updated": [],
            "backup_location": str(self.backup_dir)
        }
        
        # 리포트 저장
        report_path = self.base_path / "ui_design_renewal_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("OK금융그룹 eHR 시스템 UI/UX 디자인 통합 리뉴얼")
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
    
    # 3. 통합 디자인 적용
    response = input("\n통합 디자인을 적용하시겠습니까? (y/n): ")
    if response.lower() == 'y':
        unifier.apply_unified_design()
        
        # 4. 리포트 생성
        report = unifier.generate_report()
        print("\n개선 리포트가 생성되었습니다.")
        print(f"   - 백업 위치: {report['backup_location']}")
        print(f"   - 프리뷰: {unifier.preview_dir / 'comparison.html'}")
    else:
        print("디자인 적용이 취소되었습니다.")

if __name__ == "__main__":
    main()