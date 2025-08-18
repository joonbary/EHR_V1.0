# OK금융그룹 e-HR 시스템 UI/UX 업그레이드 실행 계획

## 🎯 목표
- 일관성 있고 반응형이며 modern한 사용자 경험 제공
- shadcn/ui 기반 컴포넌트 시스템 구축
- Tailwind CSS 기반 스타일링

## 📅 실행 단계

### Phase 1: 기초 설정 (Day 1)
1. **디자인 시스템 정의**
   - Primary: #1443FF
   - Accent: #FFD700
   - Gray Scale: #F9FAFB ~ #111827
   - Font: Noto Sans KR (base 16px, heading 24px-32px)
   - Spacing: 8px grid system

2. **Tailwind CSS 설정**
   - 커스텀 색상 팔레트
   - 반응형 브레이크포인트
   - 다크모드 설정

### Phase 2: 레이아웃 시스템 (Day 2)
1. **MainLayout 컴포넌트**
   - 상단 헤더
   - 좌측 사이드바
   - 콘텐츠 그리드
   - 반응형 지원

2. **AdminLayout 컴포넌트**
   - 관리자용 헤더
   - 퀵탭 메뉴
   - 통계 영역

### Phase 3: UI 컴포넌트 라이브러리 (Day 3-4)
1. **기본 컴포넌트**
   - Button (primary/secondary/ghost/destructive)
   - Input (label, placeholder, error)
   - Select (단일/다중 선택)
   - Card (통계/정보 카드)

2. **고급 컴포넌트**
   - DataTable (필터/페이지네이션/정렬)
   - Toast (알림)
   - Dialog (모달)
   - Tabs, Accordion, Tooltip, Badge

### Phase 4: 페이지 템플릿 (Day 5-6)
1. **핵심 페이지**
   - DashboardPage: 주요 지표 위젯
   - ProfilePage: 직원 정보 관리
   - EvaluationPage: 평가 조회/입력
   - OrganizationPage: 조직도 탐색
   - HRAdminPage: 관리자 화면

### Phase 5: 상호작용 & 접근성 (Day 7)
1. **UX 강화**
   - 로딩 스피너
   - 슬라이드 애니메이션
   - 실시간 폼 검증

2. **접근성**
   - WCAG 기준 준수
   - aria-label, role 적용
   - 키보드 네비게이션

### Phase 6: 통합 & 테스트 (Day 8)
1. **Django 템플릿 통합**
   - 기존 템플릿 마이그레이션
   - 데이터 바인딩

2. **테스트 데이터**
   - 직원 3명
   - 평가 2건
   - 조직 구조

## 📁 폴더 구조
```
src/
├── components/
│   └── ui/
│       ├── button.tsx
│       ├── input.tsx
│       ├── select.tsx
│       ├── card.tsx
│       ├── data-table.tsx
│       ├── toast.tsx
│       ├── dialog.tsx
│       └── ...
├── layouts/
│   ├── MainLayout.tsx
│   └── AdminLayout.tsx
├── pages/
│   ├── DashboardPage.tsx
│   ├── ProfilePage.tsx
│   ├── EvaluationPage.tsx
│   ├── OrganizationPage.tsx
│   └── HRAdminPage.tsx
├── hooks/
│   ├── useTheme.ts
│   └── useWebSocket.ts
├── lib/
│   └── utils.ts
└── styles/
    └── globals.css
```

## 🛠 기술 스택
- React + TypeScript
- Tailwind CSS
- shadcn/ui
- Framer Motion
- WebSocket (Shrimp 연동)

## ✅ 완료 기준
- 모든 컴포넌트 WCAG 준수
- 다크모드 완벽 지원
- 반응형 디자인 구현
- 테스트 커버리지 80% 이상