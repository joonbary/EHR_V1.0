# OK금융그룹 e-HR 시스템 디자인 가이드
*Corporate Identity Guidelines v2.0 기반*

---

## 🎯 프로젝트 개요

**프로젝트명**: e-HR 시스템 구축  
**브랜드**: OK금융그룹  
**디자인 원칙**: 혁신적이고 신뢰할 수 있는 금융 서비스 이미지  
**개발 방식**: Django + Bootstrap + AI 코딩  

---

## 🎨 브랜드 컬러 시스템

### Primary Colors (필수 사용)

```css
/* OK Orange - 메인 브랜드 컬러 */
--ok-orange: #F55000;
--ok-orange-rgb: rgb(245, 80, 0);
--ok-orange-hex: #F55000;
/* Pantone 2026 C | CMYK M87 Y100 K0 */

/* OK Dark Brown - 서브 컬러 */
--ok-dark-brown: #55474A;
--ok-dark-brown-rgb: rgb(85, 71, 74);
--ok-dark-brown-hex: #55474A;
/* Pantone 411 C | CMYK C30 M40 Y30 K65 */

/* OK Yellow - 서브 컬러 */
--ok-yellow: #FFAA00;
--ok-yellow-rgb: rgb(255, 170, 0);
--ok-yellow-hex: #FFAA00;
/* Pantone 130 C | CMYK C0 M40 Y100 K0 */

/* OK Bright Gray - 서브 컬러 */
--ok-bright-gray: #E3DFDA;
--ok-bright-gray-rgb: rgb(227, 223, 218);
--ok-bright-gray-hex: #E3DFDA;
/* Pantone Warm Gray 2 C | CMYK C5 M5 Y8 K5 */
```

### Color Tones (톤 바리에이션)

```css
/* Orange 톤 */
--ok-orange-20: rgba(245, 80, 0, 0.2);
--ok-orange-40: rgba(245, 80, 0, 0.4);
--ok-orange-60: rgba(245, 80, 0, 0.6);
--ok-orange-80: rgba(245, 80, 0, 0.8);
--ok-orange-100: rgba(245, 80, 0, 1.0);

/* Dark Brown 톤 */
--ok-brown-20: rgba(85, 71, 74, 0.2);
--ok-brown-40: rgba(85, 71, 74, 0.4);
--ok-brown-60: rgba(85, 71, 74, 0.6);
--ok-brown-80: rgba(85, 71, 74, 0.8);
--ok-brown-100: rgba(85, 71, 74, 1.0);

/* Gold 스페셜 컬러 (고급스러운 표현용) */
--ok-gold: #875C47;
/* Pantone 875 C (금색, 무광) */
```

### 색상 사용 규칙

**✅ 권장 사용**
- **Primary CTA 버튼**: OK Orange (#F55000)
- **텍스트 & 네비게이션**: OK Dark Brown (#55474A)
- **하이라이트 & 알림**: OK Yellow (#FFAA00)
- **배경 & 비활성**: OK Bright Gray (#E3DFDA)

**❌ 사용 금지**
- 로고 색상 임의 변경
- 그라데이션 남용
- 명도/채도 임의 조정
- 복잡한 패턴 배경 위 로고 배치

---

## 🏷️ 로고 시스템

### 로고 타입

1. **심볼마크**: `OK!` (오렌지 반원 + 빨간 느낌표)
2. **국문 로고**: `OK!금융그룹`
3. **영문 로고 A**: `OK! FINANCIAL GROUP` (가로형)
4. **영문 로고 B**: `OK! FINANCIAL GROUP` (세로형)

### 로고 사용 규격

```css
/* 최소 사용 크기 */
.logo-minimum {
    min-width: 15px;  /* 4mm = 약 15px */
    min-height: 15px;
}

/* Clear Space (여백 확보) */
.logo-clearspace {
    margin: 16.6mm; /* 로고 주변 최소 여백 */
    /* 웹에서는 약 63px */
}
```

### 로고 파일명 컨벤션

```
logo/
├── ok-symbol.svg              # 심볼마크
├── ok-symbol-white.svg        # 심볼마크 (흰색)
├── ok-korean.svg              # 국문 로고
├── ok-korean-white.svg        # 국문 로고 (흰색)
├── ok-english-horizontal.svg  # 영문 로고 (가로)
├── ok-english-vertical.svg    # 영문 로고 (세로)
└── ok-english-white.svg       # 영문 로고 (흰색)
```

---

## 📝 타이포그래피

### 웹폰트 스택

```css
/* 기본 서체 스택 */
font-family: 'OK Medium', 'Apple SD Gothic Neo', 'Malgun Gothic', '맑은 고딕', 'Noto Sans KR', sans-serif;

/* 제목용 */
.heading {
    font-family: 'OK Bold', 'Apple SD Gothic Neo', sans-serif;
    font-weight: 700;
    color: var(--ok-dark-brown);
}

/* 본문용 */
.body {
    font-family: 'OK Light', 'Apple SD Gothic Neo', sans-serif;
    font-weight: 300;
    color: #333;
    line-height: 1.6;
}

/* 강조용 */
.emphasis {
    font-family: 'OK Medium', 'Apple SD Gothic Neo', sans-serif;
    font-weight: 500;
    color: var(--ok-orange);
}
```

### 타이포그래피 스케일

```css
/* 제목 크기 */
.h1 { font-size: 2.5rem; font-weight: 700; }  /* 40px */
.h2 { font-size: 2rem; font-weight: 700; }    /* 32px */
.h3 { font-size: 1.5rem; font-weight: 500; }  /* 24px */
.h4 { font-size: 1.25rem; font-weight: 500; } /* 20px */
.h5 { font-size: 1rem; font-weight: 500; }    /* 16px */

/* 본문 크기 */
.body-large { font-size: 1.125rem; }  /* 18px */
.body { font-size: 1rem; }            /* 16px */
.body-small { font-size: 0.875rem; }  /* 14px */
.caption { font-size: 0.75rem; }      /* 12px */
```

---

## 🧩 UI 컴포넌트 스타일

### 버튼 시스템

```css
/* Primary Button - OK Orange */
.btn-primary {
    background-color: var(--ok-orange);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    font-family: 'OK Medium', sans-serif;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
    cursor: pointer;
}

.btn-primary:hover {
    background-color: var(--ok-orange-80);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(245, 80, 0, 0.3);
}

/* Secondary Button */
.btn-secondary {
    background-color: white;
    color: var(--ok-orange);
    border: 2px solid var(--ok-orange);
    padding: 10px 22px;
    border-radius: 4px;
    font-family: 'OK Medium', sans-serif;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    background-color: var(--ok-orange);
    color: white;
}

/* Outline Button */
.btn-outline {
    background-color: transparent;
    color: var(--ok-dark-brown);
    border: 1px solid var(--ok-bright-gray);
    padding: 10px 20px;
    border-radius: 4px;
}
```

### 카드 컴포넌트

```css
.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    border-top: 4px solid var(--ok-orange);
    padding: 24px;
    margin-bottom: 24px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
    border-bottom: 1px solid var(--ok-bright-gray);
    padding-bottom: 16px;
    margin-bottom: 16px;
}

.card-title {
    font-family: 'OK Medium', sans-serif;
    font-size: 1.125rem;
    color: var(--ok-dark-brown);
    margin: 0;
}
```

### 폼 요소

```css
.form-control {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid var(--ok-bright-gray);
    border-radius: 4px;
    font-family: 'OK Light', sans-serif;
    font-size: 14px;
    transition: border-color 0.3s ease;
}

.form-control:focus {
    outline: none;
    border-color: var(--ok-orange);
    box-shadow: 0 0 0 3px rgba(245, 80, 0, 0.1);
}

.form-label {
    font-family: 'OK Medium', sans-serif;
    font-size: 14px;
    color: var(--ok-dark-brown);
    margin-bottom: 8px;
    display: block;
}
```

---

## 📐 레이아웃 & 그리드

### 컨테이너 시스템

```css
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 16px;
}

.container-fluid {
    width: 100%;
    padding: 0 16px;
}

.container-sm { max-width: 576px; }
.container-md { max-width: 768px; }
.container-lg { max-width: 992px; }
.container-xl { max-width: 1200px; }
```

### 그리드 시스템 (12 Column)

```css
.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -8px;
}

.col { flex: 1 0 0%; padding: 0 8px; }
.col-1 { flex: 0 0 8.333333%; padding: 0 8px; }
.col-2 { flex: 0 0 16.666667%; padding: 0 8px; }
.col-3 { flex: 0 0 25%; padding: 0 8px; }
.col-4 { flex: 0 0 33.333333%; padding: 0 8px; }
.col-6 { flex: 0 0 50%; padding: 0 8px; }
.col-8 { flex: 0 0 66.666667%; padding: 0 8px; }
.col-9 { flex: 0 0 75%; padding: 0 8px; }
.col-12 { flex: 0 0 100%; padding: 0 8px; }
```

### 간격 시스템 (8px 기반)

```css
/* Margin */
.m-0 { margin: 0; }
.m-1 { margin: 8px; }
.m-2 { margin: 16px; }
.m-3 { margin: 24px; }
.m-4 { margin: 32px; }
.m-5 { margin: 48px; }

/* Padding */
.p-0 { padding: 0; }
.p-1 { padding: 8px; }
.p-2 { padding: 16px; }
.p-3 { padding: 24px; }
.p-4 { padding: 32px; }
.p-5 { padding: 48px; }

/* 방향별 적용 */
.mt-2 { margin-top: 16px; }
.mb-3 { margin-bottom: 24px; }
.pt-2 { padding-top: 16px; }
.pb-3 { padding-bottom: 24px; }
```

---

## 🎭 그래픽 요소

### 헤더 그래픽 모티브

```css
.header-graphic {
    background: linear-gradient(135deg, var(--ok-dark-brown) 0%, var(--ok-orange) 100%);
    position: relative;
    overflow: hidden;
}

.header-graphic::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 200px;
    height: 100%;
    background: var(--ok-yellow);
    clip-path: polygon(20% 0%, 100% 0%, 80% 100%, 0% 100%);
    opacity: 0.8;
}
```

### 아이콘 시스템

```css
.icon {
    width: 24px;
    height: 24px;
    fill: var(--ok-orange);
    stroke: none;
}

.icon-sm { width: 16px; height: 16px; }
.icon-lg { width: 32px; height: 32px; }
.icon-xl { width: 48px; height: 48px; }

/* 상태별 아이콘 색상 */
.icon-primary { fill: var(--ok-orange); }
.icon-secondary { fill: var(--ok-dark-brown); }
.icon-success { fill: #28a745; }
.icon-warning { fill: var(--ok-yellow); }
.icon-danger { fill: #dc3545; }
```

### 그래프/차트 색상

```css
/* 차트 색상 팔레트 */
:root {
    --chart-color-1: var(--ok-orange);     /* 주요 데이터 */
    --chart-color-2: var(--ok-dark-brown); /* 보조 데이터 */
    --chart-color-3: var(--ok-yellow);     /* 강조 데이터 */
    --chart-color-4: var(--ok-bright-gray); /* 배경 데이터 */
    --chart-color-5: #28a745;              /* 성공/증가 */
    --chart-color-6: #dc3545;              /* 위험/감소 */
}
```

---

## 📱 반응형 디자인

### 브레이크포인트

```css
/* Mobile First Approach */
@media (max-width: 575.98px) { /* xs */ }
@media (min-width: 576px) and (max-width: 767.98px) { /* sm */ }
@media (min-width: 768px) and (max-width: 991.98px) { /* md */ }
@media (min-width: 992px) and (max-width: 1199.98px) { /* lg */ }
@media (min-width: 1200px) { /* xl */ }
```

### 반응형 로고

```css
.logo-responsive {
    width: 120px; /* Desktop */
}

@media (max-width: 768px) {
    .logo-responsive {
        width: 80px; /* Mobile */
    }
}
```

---

## 🎨 테마 시스템

### Light Theme (기본)

```css
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: var(--ok-dark-brown);
    --text-secondary: #6c757d;
    --border-color: var(--ok-bright-gray);
}
```

### Dark Theme (선택사항)

```css
[data-theme="dark"] {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --text-primary: #ffffff;
    --text-secondary: #cccccc;
    --border-color: #404040;
}
```

---

## 🚀 Cursor AI 개발 지침

### 개발 시 필수 적용사항

1. **색상 우선순위**
   - Primary Action: OK Orange (#F55000)
   - Text/Navigation: OK Dark Brown (#55474A)
   - Highlight: OK Yellow (#FFAA00)

2. **컴포넌트 기본 구조**
   ```html
   <!-- 카드 컴포넌트 예시 -->
   <div class="card">
       <div class="card-header">
           <h3 class="card-title">제목</h3>
       </div>
       <div class="card-body">
           <p>내용...</p>
           <button class="btn-primary">확인</button>
       </div>
   </div>
   ```

3. **네이밍 컨벤션**
   - CSS 클래스: `kebab-case` (예: `.btn-primary`, `.card-header`)
   - 컴포넌트: `PascalCase` (예: `EmployeeCard`, `DashboardWidget`)

### Cursor AI 프롬프트 템플릿

```
"OK금융그룹 브랜딩에 맞는 Django 템플릿을 만들어주세요:
- 메인 컬러: #F55000 (OK Orange)
- 서브 컬러: #55474A (OK Dark Brown)  
- 하이라이트: #FFAA00 (OK Yellow)
- 카드: 상단 4px Orange 보더, 8px 모서리
- 버튼: Orange 배경, 흰색 텍스트, hover 효과
- 타이포그래피: OK Medium 폰트 우선, 시스템 폰트 fallback
- 레이아웃: 12컬럼 그리드, 8px 기반 간격
- 반응형: Mobile First, Bootstrap 스타일"
```

---

## ✅ 품질 체크리스트

### 디자인 검증

- [ ] **브랜드 컬러 정확성**: #F55000, #55474A, #FFAA00 정확히 적용
- [ ] **로고 규격**: 최소 크기(15px) 및 여백(63px) 확보
- [ ] **타이포그래피**: OK 폰트 패밀리 적용, fallback 폰트 설정
- [ ] **컴포넌트 일관성**: 카드, 버튼, 폼 스타일 통일
- [ ] **반응형**: 모든 디바이스에서 정상 동작

### 접근성 검증

- [ ] **색상 대비**: WCAG 2.1 AA 기준 (4.5:1) 준수
- [ ] **키보드 탐색**: Tab 순서 논리적 구성
- [ ] **대체 텍스트**: 이미지 alt 속성 설정
- [ ] **폰트 크기**: 최소 14px 이상 사용

### 성능 최적화

- [ ] **이미지**: SVG 로고, WebP 이미지 사용
- [ ] **CSS**: 압축 및 중복 제거
- [ ] **폰트**: 웹폰트 최적화 로딩

---

## 📁 파일 구조

```
assets/
├── css/
│   ├── brand.css           # 브랜드 스타일
│   ├── components.css      # 컴포넌트 스타일
│   └── utilities.css       # 유틸리티 클래스
├── images/
│   ├── logo/              # 로고 파일들
│   ├── icons/             # 아이콘 세트
│   └── graphics/          # 그래픽 모티브
└── fonts/
    ├── OK-Light.woff2
    ├── OK-Medium.woff2
    └── OK-Bold.woff2
```

---

*이 문서는 OK금융그룹 Corporate Identity Guidelines v2.0을 기반으로 e-HR 시스템 개발에 최적화하여 작성되었습니다.*

**최종 업데이트**: 2025년 1월  
**담당**: e-HR 개발팀  
**승인**: OK금융그룹 브랜드팀