# OK금융그룹 HR 분석 대시보드 구성 명세서

## 1. 대시보드 개요
OK금융그룹의 HR 분석 대시보드는 계열사, 직군, 직급, 연령, 신분 등을 기준으로 다양한 HR 지표를 표와 차트로 시각화하며, AI 인사이트도 함께 제공합니다. 본 문서는 해당 대시보드의 영역 구성과 각 위젯의 데이터, 인터랙션 구조 및 API 명세를 포함합니다.

---

## 2. 전체 레이아웃 구조

- 상단 필터바: 공통 조건 선택 영역
  - 계열사, 부서, 직군, 직급, 연령대, 신분, 기간(년/월 선택 가능)
- 주요 대시보드 영역 (왼→오른쪽 2열 or full-width)
  - 인력현황 요약 표
  - 입/퇴사 추이 및 리스트
  - 관리자 현황
  - 생산성 지표
  - AI 기반 인사이트

---

## 3. 위젯별 정의 및 API 스펙

### 3.1 인력현황 위젯
- 타입: 표 (Table)
- 데이터 항목:
  - 구분: 계열사 / 직군 / 직급 / 신분 / 연령대
  - 현월 인원수, 전월대비 증감, 전년말 대비, 전년동기 대비
- API: `GET /api/dashboard/headcount-summary`
  - Params: { org_unit, rank_group, contract_type, age_range, year, month }

---

### 3.2 입/퇴사 현황 위젯
- 타입: 추이차트 (LineChart) + 테이블
- 데이터 항목:
  - 월별 입사/퇴사자 수, 누적 수치
  - 입퇴사자 리스트: 이름, 나이, 입사일/퇴사일, 직급, 경력(입사자), 최종등급(퇴사자)
- API:
  - `GET /api/dashboard/join-leave-trend`
    - Params: { from_date, to_date, group_by (day/week/month) }
  - `GET /api/dashboard/join-leave-list`
    - Params: { type (join|leave), limit, offset }

---

### 3.3 관리자 현황 위젯
- 타입: 카드 리스트 + 상세 모달
- 데이터 항목:
  - 관리자 이름, 직급, 소속, 핵심 R&R, 평균 평가등급, 보유 역량 키워드
  - 예상 경로 및 Succession 후보
- API:
  - `GET /api/dashboard/leaders`
  - `GET /api/employees/{id}/succession`

---

### 3.4 생산성 지표 위젯
- 타입: 카드 + 라인차트 + 막대차트
- 지표 항목:
  - HCROI, 인건비 비율, 인당 자산/성과
  - 연도별/계열사별 비교
- API:
  - `GET /api/dashboard/productivity-metrics`
  - `GET /api/dashboard/productivity-trend`

---

### 3.5 AI 인사이트 위젯
- 타입: 인사이트 카드 + 경고 배너 + 예측 그래프
- 주요 인사이트:
  - 이상치 탐지 (고퇴사율 부서, 저성과자 집중팀 등)
  - 인력 감소 예측
  - 공석 시 대체인력 추천
- API:
  - `GET /api/airiss/alerts`
  - `GET /api/airiss/forecast`
  - `GET /api/airiss/substitute-suggestion`

---

## 4. 사용자 인터랙션 설계

| 인터랙션 | 설명 |
|-----------|------|
| 필터 변경 | 모든 위젯이 선택 조건에 따라 동기화되어 갱신됨 |
| 관리자 클릭 | 상세 모달로 평가이력, 경력경로, 추천 교육, Succession 정보 확인 |
| AI 인사이트 클릭 | 해당 경고에 대한 상세 리포트 또는 분석 화면으로 drill-down |
| 테이블 항목 클릭 | 개별 직원 프로필로 이동하거나 평가 상세로 전환 |

---

## 5. 반응형 및 UX 설계 기준

- 대시보드는 2열 그리드 기반 (min 1440px), 모바일에서는 1열 스택 방식
- 주요 수치는 강조 스타일(Card + 아이콘 + 배경 컬러), 표와 그래프는 배경 white
- Figma 기준 8px grid / Tailwind 기반 shadcn/ui 컴포넌트 적용 기준

---

## 6. 향후 확장 고려 사항

- 교육 이수 및 이탈률 분석 연동 (LMS 데이터 필요)
- 조직개편 시뮬레이션 기능 (예측 인력, R&R 재배치 모델)
- 경영진 Only AI 리포트 모드 추가 (리더 어시스턴트 통합)

---

이 문서는 HRIS 프론트/백엔드 개발팀 및 데이터 분석 파트가 협업하여 AIRISS 기반 HR 대시보드를 구현하기 위한 핵심 명세서입니다.

