# 성과평가 모듈 구현 실행 계획

## 🗓️ **3주 개발 일정**

### **Week 1: Core 데이터 모델 & 기본 UI**
#### Day 1-2: 데이터베이스 설계
```bash
# Cursor AI 작업 지시서
1. Django models.py 작성 (8개 주요 모델)
2. 마이그레이션 생성 및 적용
3. Admin 페이지 기본 설정
4. 테스트 데이터 생성 스크립트
```

#### Day 3-4: 기본 View & URL 구성
```bash
# 핵심 View 클래스 구현
- PerformanceMainView (대시보드)
- TaskManagementView (Task 등록/수정)
- ContributionEvaluationView (기여도 평가)
- ExpertiseEvaluationView (전문성 평가)
- ImpactEvaluationView (영향력 평가)
```

#### Day 5-7: 기본 템플릿 구조
```bash
# 템플릿 계층 구조
templates/
├── performance/
│   ├── base.html (공통 레이아웃)
│   ├── dashboard.html (메인 대시보드)
│   ├── task_management.html
│   ├── contribution_eval.html
│   └── calibration_session.html
```

---

### **Week 2: 핵심 기능 구현**
#### Day 8-10: Task 관리 기능
```python
# 구현할 핵심 기능들
1. Task 등록/수정/삭제 (CRUD)
2. 부서장 승인 워크플로우
3. 진행률 실시간 업데이트
4. 분기별 Task 조회 필터링
```

#### Day 11-12: 기여도 평가 로직
```python
# 자동 계산 로직 구현
def calculate_achievement_rate(target, actual):
    return (actual / target) * 100 if target > 0 else 0

def determine_contribution_score(achievement_rate, contribution_type):
    # OK금융그룹 Scoring Chart 기반 점수 산출
    scoring_matrix = {
        '충분': {80: 2, 90: 3, 100: 4},
        '리딩': {70: 2, 80: 3, 90: 4},
        # ... 기타 매트릭스
    }
    return calculate_score(achievement_rate, contribution_type, scoring_matrix)
```

#### Day 13-14: 평가 결과 도출
```python
# 1차 등급 자동 산출
def calculate_manager_grade(contribution, expertise, impact):
    achieved_count = sum([contribution, expertise, impact])
    if achieved_count >= 2:
        return 'A'
    elif achieved_count == 1:
        return 'B'
    else:
        return 'C'
```

---

### **Week 3: 고급 기능 & 최적화**
#### Day 15-17: Calibration Session
```python
# 복잡한 집단 의사결정 시스템
class CalibrationSessionView:
    def get_discussion_targets(self):
        # A등급자 → S/A+/A 결정 대상
        # B등급자 → B+ 승격 검토 대상
        # C등급자 → D 강등 검토 대상
        pass
    
    def update_final_grades(self, decisions):
        # 위원회 결정사항 일괄 업데이트
        pass
```

#### Day 18-19: 대시보드 & 분석
```python
# 시각화 및 통계 기능
1. 개인별 평가 현황 차트
2. 조직별 성과 분포도
3. 연도별 평가 트렌드
4. 승진 예측 알고리즘
```

#### Day 20-21: 테스트 & 최적화
```python
# 품질 보증
1. Unit Test 작성 (모든 핵심 로직)
2. Integration Test (워크플로우 테스트)
3. Performance Test (대용량 데이터)
4. UI/UX 테스트 (크로스 브라우저)
```

---

## 🔧 **Cursor AI 작업 지시서 예시**

### Day 1 작업 지시서
```markdown
# 성과평가 모델 구현 작업

## 목표
OK금융그룹 신인사제도에 맞는 성과평가 데이터 모델 8개 구현

## 구현 사항
1. Employee 모델 확장 (직군, 직종, 성장레벨 추가)
2. GrowthLevelStandard 모델 (성장레벨별 평가기준)
3. Task 모델 (업무 등록 및 관리)
4. 3대 평가 모델 (기여도/전문성/영향력)
5. 종합평가 모델 (1차+2차 평가결과)

## 주의사항
- 모든 필드에 적절한 validation 추가
- __str__ 메서드로 가독성 확보
- Meta 클래스로 정렬 및 제약조건 설정
- 삭제 시 CASCADE/SET_NULL 적절히 설정

## 참고
- 기존 Employee 모델과 호환성 유지
- OK금융그룹 평가 양식 이미지 참조
```

---

## 📊 **진도 체크 포인트**

### 주간 검토 미팅
```markdown
# 매주 금요일 17:00 Claude 리뷰

## Week 1 체크포인트
- [ ] 모든 모델 생성 완료
- [ ] 기본 CRUD 동작 테스트
- [ ] Admin 페이지에서 데이터 입력 가능
- [ ] 기본 템플릿 렌더링 확인

## Week 2 체크포인트  
- [ ] Task 등록/승인 워크플로우 완료
- [ ] 기여도 점수 자동 계산 로직 구현
- [ ] 1차 등급 산출 알고리즘 테스트
- [ ] 사용자 권한별 화면 분기 완료

## Week 3 체크포인트
- [ ] Calibration Session 완전 구현
- [ ] 대시보드 차트 및 통계 표시
- [ ] 모든 핵심 기능 통합 테스트
- [ ] 성능 최적화 및 보안 검토
```

---

## 🚨 **위험 요소 및 대응 방안**

### 기술적 위험
1. **복잡한 평가 로직**: 단계적 구현, 충분한 테스트
2. **성능 이슈**: 쿼리 최적화, 캐싱 전략
3. **데이터 정합성**: 트랜잭션 처리, 검증 로직 강화

### 비즈니스 위험  
1. **요구사항 변경**: 모듈화 설계로 유연성 확보
2. **사용자 경험**: 지속적인 피드백 수렴 및 개선
3. **보안 이슈**: 권한 관리, 데이터 암호화

---

## 🎯 **다음 단계 예고**

### Phase 4: AI 기능 통합 (1-2주)
- **ChatGPT API 연동**: 평가 코멘트 감성 분석
- **자동 피드백 생성**: AI 기반 발전방안 제시
- **성과 예측 모델**: 머신러닝 기반 승진 확률 계산

### Phase 5: 모바일 최적화 (1주)
- **PWA 구현**: 오프라인 지원, 푸시 알림
- **반응형 개선**: 터치 인터페이스 최적화
- **앱 스토어 배포**: 네이티브 앱 변환

### Phase 6: 고도화 (2-3주)
- **실시간 알림**: WebSocket 기반 즉시 피드백
- **고급 분석**: 조직 차원의 인사 인사이트
- **API 구축**: 외부 시스템 연동 대비

---

## 💪 **성공 기준**

### 기능적 요구사항
- ✅ OK금융그룹 신인사제도 100% 반영
- ✅ 3대 평가축 완전 자동화
- ✅ Calibration Session 지원
- ✅ 실시간 진도 추적

### 비기능적 요구사항
- ✅ 응답시간 2초 이내 (일반 조회)
- ✅ 동시 사용자 100명 지원
- ✅ 99% 업타임 보장
- ✅ 모바일 친화적 UX

6개월 MVP 목표 달성을 위해 **집중적이고 체계적인 개발**을 진행합니다! 🚀