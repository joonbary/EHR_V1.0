# 📌 SuperClaude 작업 지시서 (OK금융 보상체계 개발용 최종)

```
/sc:implement --persona-backend -plan -seq -c7

# 🎯 목표
OK금융그룹 e-HR 시스템 내 보상(Compensation) 모듈 개발.
기본급·고정OT·직책급·직무역량급·변동급(PI, 월성과급, 추석상여)까지 반영.
데이터 스키마·산식 엔진·검증로직·API를 체계적으로 구현.

---

## 1) 스키마 정의 (SQLModel/SQLAlchemy)

### employee_master
- employee_id (PK)
- name, org_unit, grade, job_profile_id, position_code
- employment_type (정규/PL/Non-PL/별정직)
- hire_date, term_date

### grade_master
- grade_code (GRDxx, 성장레벨+급호)
- level, step, title
- valid_from, valid_to

### position_master
- position_code (POSxx, 예: POS13 지점장, POS16 RM지점장)
- position_name
- domain (HQ/Non-PL/PL)
- manager_level
- valid_from, valid_to

### position_allowance
- position_code FK
- allowance_tier (A/B+/B or N/A for 영업)
- monthly_amount
- allowance_rate (초임 0.8, 일반 1.0)
- valid_from, valid_to

### competency_allowance
- job_profile_id FK
- competency_tier (T1/T2/T3)
- monthly_amount
- valid_from, valid_to

### compensation_snapshot
- employee_id FK
- pay_period (YYYY-MM)
- base_salary, fixed_ot, position_allowance, competency_allowance
- pi_amount, monthly_pi_amount, holiday_bonus
- calc_run_id

### calc_run_log
- run_id, timestamp, formula_version, changes, errors

---

## 2) 고정급 및 고정OT 산식

- **기본급**: 성장레벨 × 급호별 테이블 (Non-PL, PL, 별정직 매니저)
- **고정OT (20시간)**:
  ```
  통상시급 = (기본급 + 직책급 + 직무역량급 [+추석상여]) ÷ 209
  고정OT = 통상시급 × 20 × 1.5
  ```
  - 실적급(NPL매니저 회수실적, SI)은 통상임금 제외

---

## 3) 직책급 정책

- 동일 직책이라도 A/B+/B 티어 구분
  - 기준: 난이도, 외부시장가치, 내부 중요도, 직책 속성
- 초임: 직책 부여 후 1년간 80% 지급
- 영업조직(POS11~POS16, POS21~POS23)은 단일 테이블(allowance_tier=N/A)

---

## 4) 직무역량급 정책

- Job Profile + Competency Tier 조합으로 산정
- 통상임금 포함 항목

---

## 5) 변동급 산식

### PI (Non-PL 전용)
- 지급주기: 연 1회 (성과 1/1~12/31, 지급 익년 설 전)
- 기준: 기본급 + 직책급 + 직무역량급
- 평가등급: S, A+, A, B+, B, C, D (7단계)
- 지급률: 본사 vs 영업, 팀원 vs 직책자 차등 (CSV Seed: PI_table.csv)
- PL 직군은 PI 미적용

### 월성과급 (PL 전용)
- 지급주기: 월 단위
- 평가등급: S ~ D (9단계)
- 센터장/팀장/Lv.2~3(프로·책임/선임)/Lv.1(전임·주임) 구분
- 지급액: CSV Seed: monthly_PI_table.csv
- 통상임금 제외

### 추석상여
- 지급일: 추석 명절 2영업일 전
- 산식:
  ```
  추석상여 = 통상임금 × 100% × (실근무일 ÷ (1/1~지급일 총 근무일수))
  ```
- 성과와 무관, 통상임금 포함

---

## 6) 검증 규칙

- 등급/직책/직무 변경 시 전월 대비 ±X% 이상 변동 경보
- PI/SI/PS 합계가 풀/예산 대비 초과 시 오류
- 동일 기간 다중 직책/역량급 배정 불가
- POS13(지점장) vs POS16(RM지점장) 혼용 금지
- 추석상여 일할 계산: 중도 입/퇴사자 처리 확인

---

## 7) API 초안 (FastAPI)

- GET /comp/employee/{id}/statement?period=YYYY-MM
- GET /comp/kpi/mix-ratio
- GET /comp/kpi/variance-alerts
- POST /comp/snapshot/run (계산 엔진 실행)
- GET /positions/allowance
- POST /employees/{id}/position/assign

---

## 8) 운영 캘린더

- 월 급여 기산: 전월 21일 ~ 당월 20일
- 월 급여 지급일: 매월 25일 (휴일은 직전 영업일)
- PI/SI/PS 지급일: 익년 설명절 2영업일 전
- 추석상여 지급일: 추석 2영업일 전

---

## 9) 데이터 Seed 관리

- **기본급 테이블**: 관리테이블.pdf → seed_base_salary.csv
- **직책급 테이블**: Position_allowance_table.csv
- **직무역량급 테이블**: Competency_allowance_table.csv
- **PI 지급률**: PI_table.csv
- **월성과급 지급액**: monthly_PI_table.csv

👉 모든 상세 금액 테이블은 **CSV Seed 파일 기반**으로 로딩하여, 규정 개정 시 CSV 업데이트만으로 반영 가능하도록 설계.

---

# 🛠️ 실행 지시
1. models.py 및 마이그레이션 정의 (위 스키마 반영)
2. ETL 로더 작성 (CSV Seed: base/position/competency/PI/monthly_PI)
3. 계산 엔진 서비스 구현 (순서: 기본급 → 고정OT → 직책급 → 직무역량급 → PI/월성과급/추석상여)
4. 검증 유닛테스트 추가 (일할, 초임 80%, PI 지급률, 월성과급 지급액)
5. API 엔드포인트 구현 (보상 조회·스냅샷·KPI 대시보드)
```

