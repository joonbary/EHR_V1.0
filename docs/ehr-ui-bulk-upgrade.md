# 🚀 e-HR 시스템 전체 UI 일괄 업그레이드 작업지시서

## 📌 일괄 업그레이드 전략
**목표**: 기존 시스템 전체를 2-3일 내에 모던 UI로 전환

---

## 🎯 Step 1: 글로벌 디자인 시스템 구축 (30분)

### 1-1. 디자인 토큰 파일 생성
```css
/* src/styles/design-tokens.css */
:root {
  /* OK금융그룹 컬러 시스템 */
  --color-primary: #FF6B00;
  --color-primary-hover: #E55A00;
  --color-primary-light: #FFF4ED;
  
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;
  
  /* 그레이 스케일 */
  --color-gray-50: #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-300: #D1D5DB;
  --color-gray-400: #9CA3AF;
  --color-gray-500: #6B7280;
  --color-gray-600: #4B5563;
  --color-gray-700: #374151;
  --color-gray-800: #1F2937;
  --color-gray-900: #111827;
  
  /* 간격 시스템 */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
  
  /* 테두리 반경 */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;
  
  /* 그림자 */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
  
  /* 타이포그래피 */
  --font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
}
```

### 1-2. 글로벌 CSS 리셋
```css
/* src/styles/global.css */
@import './design-tokens.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  line-height: 1.5;
  color: var(--color-gray-900);
  background-color: var(--color-gray-50);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 기본 요소 스타일 */
button {
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

input, textarea, select {
  font-family: inherit;
  font-size: inherit;
  width: 100%;
  transition: all 0.2s ease;
}

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--color-primary-hover);
}
```

---

## 🎯 Step 2: Cursor AI 일괄 변환 명령어 (1시간)

### 2-1. 전체 컴포넌트 스타일 마이그레이션
Cursor AI에서 다음 명령어 실행:

```
"프로젝트 전체의 모든 React 컴포넌트를 다음 규칙으로 일괄 변경해줘:

1. 인라인 스타일을 CSS Modules로 변환
2. 하드코딩된 색상을 CSS 변수로 교체
3. px 단위를 rem 단위로 변환
4. 클래스명을 BEM 방식으로 통일

변경 예시:
- style={{color: '#FF6B00'}} → className={styles.primary}
- backgroundColor: '#F5F5F5' → var(--color-gray-100)
- padding: '16px' → padding: var(--spacing-md)
- className="button-primary" → className={styles['button--primary']}"
```

### 2-2. 공통 컴포넌트 라이브러리 생성
```typescript
/* src/components/ui/index.ts */
// Cursor AI 명령어:
"다음 공통 컴포넌트들을 생성해줘. 모든 컴포넌트는 design-tokens.css의 변수를 사용하고, TypeScript와 CSS Modules를 사용해야 해:

1. Button (primary, secondary, ghost, danger 변형)
2. Card (header, body, footer 섹션)
3. Input (text, password, number, date 타입)
4. Select (single, multi 선택)
5. Modal (header, content, actions)
6. Table (정렬, 필터, 페이지네이션)
7. Tabs (horizontal, vertical)
8. Badge (status, count)
9. Alert (info, success, warning, error)
10. Loader (spinner, skeleton, progress bar)"
```

---

## 🎯 Step 3: 레이아웃 통합 변환 (30분)

### 3-1. 마스터 레이아웃 템플릿
```tsx
/* src/layouts/MainLayout.tsx */
// Cursor AI 명령어:
"다음 사양으로 메인 레이아웃을 생성해줘:

1. 좌측 사이드바 (접기/펼치기, 아이콘+텍스트 메뉴)
2. 상단 헤더 (검색바, 알림, 프로필)
3. 메인 콘텐츠 영역 (패딩, 최대 너비 제한)
4. 반응형 디자인 (모바일에서 사이드바는 오버레이)
5. 다크모드 토글 기능

OK금융그룹 인사 메뉴 구조:
- 대시보드
- 인사정보 (기본정보, 성장레벨, 경력경로)
- 평가관리 (평가입력, 평가결과, Check-In)
- 보상관리 (급여명세서, 보상구조, 연봉계산기)
- 조직도
- 공지사항"
```

### 3-2. 페이지 템플릿 일괄 적용
```typescript
// Cursor AI 명령어:
"모든 페이지 컴포넌트를 다음 템플릿으로 감싸줘:

import MainLayout from '@/layouts/MainLayout';
import { PageHeader, PageContent } from '@/components/ui';

const [페이지명] = () => {
  return (
    <MainLayout>
      <PageHeader 
        title='[페이지 제목]'
        breadcrumb={[경로]}
        actions={[액션 버튼]}
      />
      <PageContent>
        {/* 기존 콘텐츠 */}
      </PageContent>
    </MainLayout>
  );
};"
```

---

## 🎯 Step 4: 일괄 UI 개선 스크립트 (2시간)

### 4-1. 자동 변환 스크립트
```javascript
/* scripts/ui-migration.js */
// Cursor AI에 다음 스크립트 생성 요청:
"프로젝트 전체 UI를 일괄 변경하는 Node.js 스크립트를 만들어줘:

1. 모든 .jsx/.tsx 파일 스캔
2. 다음 패턴을 찾아서 변경:
   - <div> → <Card>로 변환 (조건: className에 'box', 'panel', 'container' 포함)
   - <button> → <Button>로 변환
   - <input> → <Input>로 변환
   - <table> → <Table>로 변환
   - alert() → toast.show()로 변환
   - confirm() → modal.confirm()로 변환

3. 스타일 마이그레이션:
   - style={{ margin: '10px' }} → className={styles.spacing}
   - className='btn btn-primary' → <Button variant='primary'>
   - 하드코딩된 색상 → CSS 변수

4. 변경 사항 로그 파일 생성"
```

### 4-2. ESLint/Prettier 일괄 적용
```json
/* .eslintrc.json */
{
  "extends": ["react-app", "prettier"],
  "rules": {
    "no-inline-styles": "error",
    "prefer-css-modules": "warn",
    "consistent-naming": "error"
  }
}

/* .prettierrc */
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

Cursor AI 명령어:
```
"전체 프로젝트에 ESLint와 Prettier를 적용하고, 
자동으로 수정 가능한 모든 이슈를 고쳐줘"
```

---

## 🎯 Step 5: 데이터 시각화 일괄 개선 (1시간)

### 5-1. 차트 컴포넌트 통합
```typescript
// Cursor AI 명령어:
"프로젝트 내 모든 차트를 찾아서 다음과 같이 통합해줘:

1. 모든 차트를 Recharts로 통일
2. 공통 ChartWrapper 컴포넌트로 감싸기
3. OK금융그룹 컬러 팔레트 적용
4. 반응형 처리
5. 툴팁, 범례 스타일 통일

특히 다음 차트들을 우선 변환:
- 성장레벨 진행 차트 (ProgressChart)
- 평가 점수 레이더 차트 (RadarChart)
- 보상 구성 도넛 차트 (DonutChart)
- 조직도 트리 차트 (OrgChart)"
```

### 5-2. 테이블 일괄 개선
```typescript
// Cursor AI 명령어:
"모든 HTML table을 찾아서 DataTable 컴포넌트로 교체해줘:

기능 추가:
- 정렬 (모든 컬럼)
- 필터링 (텍스트, 날짜, 숫자)
- 페이지네이션
- 엑셀 다운로드
- 행 선택
- 반응형 (모바일에서 카드뷰)

OK금융 특화:
- 성장레벨 컬럼은 뱃지로 표시
- 평가점수는 별점으로 표시
- 금액은 천단위 콤마 자동 추가"
```

---

## 🎯 Step 6: 성능 최적화 일괄 적용 (30분)

### 6-1. 번들 최적화
```javascript
// Cursor AI 명령어:
"다음 성능 최적화를 전체 프로젝트에 적용해줘:

1. React.lazy()로 라우트 레벨 코드 스플리팅
2. 무거운 컴포넌트 동적 임포트
3. 이미지 lazy loading 적용
4. useMemo, useCallback으로 불필요한 리렌더링 방지
5. React.memo로 컴포넌트 메모이제이션"
```

### 6-2. 빌드 설정 최적화
```javascript
// webpack.config.js 또는 vite.config.js
// Cursor AI 명령어:
"빌드 설정을 최적화해줘:
- CSS 압축 및 퍼징
- 이미지 최적화
- 폰트 프리로드
- 번들 분석 리포트 생성"
```

---

## 🚀 실행 순서 (총 4-5시간)

### Day 1 (2-3시간)
1. **[30분]** Step 1: 디자인 시스템 구축
2. **[1시간]** Step 2: Cursor AI로 컴포넌트 일괄 변환
3. **[30분]** Step 3: 레이아웃 통합
4. **[1시간]** 테스트 및 버그 수정

### Day 2 (2시간)
1. **[1시간]** Step 4: UI 마이그레이션 스크립트 실행
2. **[30분]** Step 5: 데이터 시각화 개선
3. **[30분]** Step 6: 성능 최적화

---

## ⚡ Cursor AI 꿀팁

### 1. 멀티파일 편집
```
Cmd+Shift+L: 프로젝트 전체 검색/치환
"Apply to all files": 여러 파일 동시 수정
```

### 2. AI 컨텍스트 유지
```
"이전에 만든 디자인 시스템을 사용해서..."
"OK금융그룹 인사제도에 맞춰서..."
```

### 3. 일괄 리팩토링
```
"src/components 폴더의 모든 컴포넌트에 PropTypes를 TypeScript interface로 변환해줘"
```

---

## ✅ 체크리스트

### 변환 전
- [ ] 현재 프로젝트 백업
- [ ] 디자인 토큰 파일 생성
- [ ] 공통 컴포넌트 라이브러리 준비

### 변환 중
- [ ] 컴포넌트 일괄 변환 완료
- [ ] 레이아웃 템플릿 적용
- [ ] 스타일 마이그레이션 완료
- [ ] 차트/테이블 컴포넌트 교체

### 변환 후
- [ ] 전체 페이지 UI 일관성 확인
- [ ] 반응형 디자인 테스트
- [ ] 성능 메트릭 측정
- [ ] 접근성 검사

---

## 📊 예상 결과

### Before
- 일관성 없는 UI
- 하드코딩된 스타일
- 구식 디자인 패턴

### After
- 통일된 디자인 시스템
- 재사용 가능한 컴포넌트
- 모던하고 트렌디한 UI
- OK금융그룹 브랜드 반영

---

## 🔥 즉시 시작하기

터미널에서:
```bash
# 1. 디자인 시스템 파일 생성
mkdir -p src/styles && touch src/styles/design-tokens.css

# 2. Cursor AI 열기
cursor .

# 3. 전체 선택 후 AI에게 지시
"이 프로젝트의 모든 UI를 design-tokens.css를 사용하는 모던한 스타일로 일괄 변경해줘"
```

이렇게 하면 **2-3일 내에 전체 UI를 일괄 업그레이드** 할 수 있습니다!