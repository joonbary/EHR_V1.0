# EHR V1.0 메뉴 구조 점검 보고서

## 1. 현재 메뉴 구조 분석

### 1.1 메인 메뉴 구조
```
/
├── 대시보드 (Dashboard)
│   ├── executive/ - 경영진 대시보드
│   ├── hr/ - HR 분석 대시보드
│   ├── workforce/ - 인력 현황
│   ├── performance/ - 성과 분석
│   └── compensation/ - 보상 분석
│
├── 직무 관리 (Job Profiles) ✅
│   ├── 직무 체계도
│   ├── 직무 트리맵
│   └── 직무기술서 관리
│
├── 인사관리 (Employees)
│   ├── 직원 관리 ✅
│   ├── 조직도 ✅
│   ├── 계층 조직도 ✅
│   ├── HR 대시보드 ✅
│   ├── 외주인력 관리 ✅
│   ├── 해외인력 관리 ✅
│   └── 근태관리 ❌ (under_construction)
│
├── 평가관리 (Evaluations)
│   ├── 기여도 평가 ⚠️ (일부 구현)
│   ├── 전문성 평가 ⚠️ (일부 구현)
│   ├── 영향력 평가 ⚠️ (일부 구현)
│   ├── 종합평가 ⚠️ (일부 구현)
│   ├── Calibration ✅
│   ├── 성장레벨 ❌ (대부분 under_construction)
│   ├── 피평가자 화면 ✅
│   ├── 평가자 화면 ✅
│   └── 인사담당자 화면 ✅
│
├── 보상관리 (Compensation)
│   └── 대시보드 ✅ (API 구현)
│
├── 승진관리 (Promotions)
│   └── [URL 확인 필요]
│
├── 셀프서비스 (SelfService)
│   ├── 내 대시보드 ✅
│   ├── 프로필 수정 ✅
│   ├── 비밀번호 변경 ✅
│   ├── 평가 이력 ✅
│   ├── 보상 명세서 ✅
│   ├── 경력 경로 ✅
│   ├── 내 평가 ❌ (under_construction)
│   └── 내 보상 ❌ (under_construction)
│
├── 채용관리 (Recruitment)
│   ├── 대시보드 ✅
│   ├── 채용공고 관리 ✅
│   ├── 지원자 관리 ✅
│   ├── 지원서 관리 ✅
│   └── 면접 관리 ✅
│
├── 교육훈련 (Trainings)
│   └── [URL 확인 필요]
│
├── 자격증 (Certifications)
│   └── [URL 확인 필요]
│
├── 조직관리 (Organization)
│   └── [URL 확인 필요]
│
├── 보고서 (Reports)
│   └── [URL 확인 필요]
│
├── AI 도구
│   ├── AI 챗봇 ⚠️ (템플릿만 존재)
│   └── 리더 AI 어시스턴트 ⚠️ (템플릿만 존재)
│
└── AIRISS
    └── [URL 확인 필요]
```

## 2. 문제점 분석

### 2.1 중복 메뉴
1. **대시보드 중복**
   - `/dashboard/hr/` vs `/employees/hr/dashboard/`
   - `/dashboard/workforce/` vs `/employees/hr/full/`
   - `/dashboard/compensation/` vs `/compensation/dashboard/`
   - 해결방안: 통합된 대시보드 체계 구축

2. **평가 관련 중복**
   - `/selfservice/evaluations/` vs `/evaluations/my/`
   - `/selfservice/my-evaluation/` vs `/evaluations/my/`
   - 해결방안: selfservice는 읽기 전용, evaluations는 입력/수정용으로 구분

3. **보상 관련 중복**
   - `/selfservice/compensation/` vs `/compensation/dashboard/`
   - `/selfservice/my-compensation/` (미구현)
   - 해결방안: selfservice는 개인 명세서, compensation은 전체 관리

### 2.2 목업 데이터만 있는 메뉴
1. **완전 미구현 (under_construction)**
   - 근태관리 (`/employees/attendance/`)
   - 성장레벨 대부분 기능
   - 내 평가 (`/selfservice/my-evaluation/`)
   - 내 보상 (`/selfservice/my-compensation/`)

2. **템플릿만 존재**
   - AI 챗봇 (`/ai-chatbot/`)
   - 리더 AI 어시스턴트 (`/leader-ai-assistant/`)
   - 스킬맵 대시보드 (`/skillmap-dashboard/`)

3. **실제 구현 상태 확인**
   - 승진관리 (Promotions) ✅ - 구현됨 (대시보드, 승진요청, 인사이동)
   - 교육훈련 (Trainings) ⚠️ - API만 구현 (UI 없음)
   - 자격증 (Certifications) ❌ - URL 파일 없음
   - 조직관리 (Organization) ✅ - 구현됨 (부서, 직위, 조직도, 인사이동)
   - 보고서 (Reports) ✅ - 구현됨 (각종 리포트 View)
   - AIRISS ✅ - 구현됨 (AI 분석, 파일 업로드, API 프록시)

### 2.3 메뉴 간 연동 필요 부분

#### 필수 연동 항목
1. **직원-평가 연동**
   - 현재: 부분적 연동
   - 필요: 직원 상세 페이지에서 평가 이력 직접 접근

2. **평가-보상 연동**
   - 현재: 연동 없음
   - 필요: 평가 결과가 보상에 자동 반영

3. **직무-직원 연동**
   - 현재: 부분적 연동
   - 필요: 직무별 인원 현황, 직무 변경 이력

4. **채용-직원 연동**
   - 현재: 연동 없음
   - 필요: 채용 확정 시 직원 데이터 자동 생성

5. **평가-승진 연동**
   - 현재: 승진 모듈 미구현
   - 필요: 평가 결과 기반 승진 대상자 자동 추천

## 3. 개선 제안

### 3.1 즉시 조치 필요
1. **중복 메뉴 정리**
   - 대시보드 통합: 하나의 대시보드 앱으로 통합
   - URL 리다이렉션 설정

2. **미구현 메뉴 처리**
   - 메뉴에서 임시 제거 또는
   - "준비 중" 명확히 표시

### 3.2 단기 개선 (1-2주)
1. **핵심 연동 구현**
   - 직원-평가 완전 연동
   - 평가-보상 연동
   - 채용-직원 데이터 연동

2. **누락 기능 구현**
   - 승진관리 기본 기능
   - 교육훈련 기본 기능
   - 보고서 생성 기능

### 3.3 중장기 개선 (1개월+)
1. **AI 기능 구현**
   - AIRISS 통합
   - AI 챗봇 실제 구현
   - 리더 AI 어시스턴트 구현

2. **고급 기능**
   - 근태관리 시스템
   - 성장레벨 체계
   - 자격증 관리

## 4. 메뉴 구조 개선안

### 4.1 통합 메뉴 구조
```
홈
├── 대시보드 (통합)
│   ├── 경영진 대시보드
│   ├── HR 통계
│   └── 개인 대시보드
│
├── 인사관리
│   ├── 직원 정보
│   ├── 조직도
│   ├── 직무 체계
│   └── 인력 현황 (국내/해외/외주)
│
├── 평가/성과
│   ├── 평가 관리
│   ├── 평가 실시
│   └── 성과 분석
│
├── 보상/승진
│   ├── 보상 관리
│   ├── 승진 관리
│   └── 보상 분석
│
├── 채용/교육
│   ├── 채용 관리
│   ├── 교육 훈련
│   └── 자격증 관리
│
├── 셀프서비스
│   ├── 내 정보
│   ├── 내 평가
│   ├── 내 보상
│   └── 경력 개발
│
├── 보고서
│   ├── 정기 보고서
│   └── 맞춤 보고서
│
└── AI 도구 (준비 중)
    ├── AI 어시스턴트
    └── 분석 도구
```

## 5. 실제 데이터 연동 상태

### 5.1 현재 연동 상태
✅ **연동 완료**
- Employee ← Evaluation (직원-평가)
- Employee ← Compensation (직원-보상)
- Employee ← Training (직원-교육)
- Employee ← Certification (직원-자격증)
- Employee ← AIRISS (직원-AI분석)
- Employee ← Interview (직원-면접관)

❌ **연동 미완료**
- Evaluation → Compensation (평가결과 → 보상반영)
- Application → Employee (채용확정 → 직원등록)
- Evaluation → Promotion (평가결과 → 승진추천)

### 5.2 데이터 흐름 문제점
1. **평가-보상 단절**: 평가 결과가 보상에 자동 반영되지 않음
2. **채용-직원 단절**: 채용 확정 후 수동으로 직원 등록 필요
3. **승진 프로세스 미완**: 평가 기반 승진 추천 시스템 없음

## 6. 구현 우선순위 (수정)

### Phase 1 (즉시 - 1일)
- [x] 메뉴 구조 분석 완료
- [ ] 중복 메뉴 통합 (대시보드 통합)
- [ ] 미구현 메뉴 숨김 처리
- [ ] 메인 네비게이션 정리

### Phase 2 (단기 - 3일)
- [ ] 평가-보상 자동 연동 구현
- [ ] 채용-직원 자동 전환 기능
- [ ] 교육훈련 UI 구현 (API는 이미 존재)

### Phase 3 (중기 - 1주)
- [ ] 승진 추천 시스템 구현
- [ ] 자격증 관리 모듈 완성
- [ ] 통합 대시보드 개선

### Phase 4 (장기 - 2주)
- [ ] AI 챗봇 실제 구현
- [ ] 근태관리 시스템
- [ ] 성장레벨 완전 구현

## 7. 즉시 조치 사항

### 7.1 메뉴 정리 스크립트
```python
# 중복 URL 리다이렉션 설정
REDIRECT_URLS = {
    '/dashboard/hr/': '/employees/hr/dashboard/',
    '/dashboard/workforce/': '/employees/hr/full/',
    '/dashboard/compensation/': '/compensation/dashboard/',
    '/selfservice/evaluations/': '/evaluations/my/',
}

# 숨김 처리할 메뉴
HIDDEN_MENUS = [
    'AI 챗봇',
    '리더 AI 어시스턴트',
    '근태관리',
    '성장레벨',
]
```

### 7.2 데이터 연동 구현
```python
# 평가-보상 연동
def apply_evaluation_to_compensation(evaluation):
    """평가 결과를 보상에 자동 반영"""
    pass

# 채용-직원 연동  
def convert_applicant_to_employee(application):
    """채용 확정자를 직원으로 자동 전환"""
    pass
```