# AIRISS-EHR 통합 구조 분석 보고서

## 1. 현재 구조 분석

### AIRISS 분석 결과 저장 구조 (airiss/models.py)

#### AIAnalysisResult 모델
- **주요 필드**:
  - `analysis_type`: 분석 유형 (승진가능성, 퇴사위험도, 팀성과 등)
  - `employee`: Employee 모델과 연결
  - `score`: 예측 점수 (0-100)
  - `confidence`: 신뢰도 (0-1)
  - `result_data`: JSON 형태의 상세 분석 결과
  - `recommendations`: 추천 사항
  - `insights`: 주요 인사이트

#### 분석 유형 (AIAnalysisType)
- `TURNOVER_RISK`: 퇴사 위험도 예측
- `PROMOTION_POTENTIAL`: 승진 가능성 분석
- `TEAM_PERFORMANCE`: 팀 성과 예측
- `TALENT_RECOMMENDATION`: 인재 추천
- `SKILL_GAP_ANALYSIS`: 역량 격차 분석

## 2. 새로운 인재 관리 구조 (employees/models_talent.py)

### 핵심 모델들

#### TalentCategory (인재 카테고리)
- **핵심인재** (CORE_TALENT)
- **고잠재인력** (HIGH_POTENTIAL)
- **승진후보자** (PROMOTION_CANDIDATE)
- **관리필요인력** (NEEDS_ATTENTION)
- **이직위험군** (RETENTION_RISK)

#### TalentPool (인재풀)
- AIRISS 분석 결과와 직접 연동
- `ai_analysis_result` 필드로 AIAnalysisResult와 연결
- AI 점수와 신뢰도를 직접 저장
- 강점, 개발영역, 추천사항 자동 동기화

#### 특화 모델들
1. **PromotionCandidate** (승진 후보자)
   - 현재/목표 직급
   - 준비도 레벨 (READY, NEAR_READY, DEVELOPING)
   - AI 추천 점수 활용

2. **RetentionRisk** (이직 위험 관리)
   - 위험 수준 (CRITICAL, HIGH, MEDIUM, LOW)
   - AIRISS 이직 위험도 점수 활용
   - 대응 전략 및 조치 사항

3. **TalentDevelopment** (인재 개발 계획)
   - 개발 목표 및 활동
   - 진행률 추적
   - 마일스톤 관리

## 3. 데이터 연동 방식

### 자동 연동 메커니즘

```python
# TalentPool 클래스의 update_from_airiss 메서드
@classmethod
def update_from_airiss(cls, analysis_result):
    """AIRISS 분석 결과로부터 인재풀 자동 업데이트"""
    
    # 1. AIRISS 분석 유형 → EHR 인재 카테고리 매핑
    category_mapping = {
        'PROMOTION_POTENTIAL': 'PROMOTION_CANDIDATE',
        'TURNOVER_RISK': 'RETENTION_RISK',
        'TALENT_RECOMMENDATION': 'CORE_TALENT',
    }
    
    # 2. 인재풀 생성 또는 업데이트
    talent_pool = cls.objects.update_or_create(
        employee=analysis_result.employee,
        category=category,
        defaults={
            'ai_analysis_result': analysis_result,
            'ai_score': analysis_result.score,
            'confidence_level': analysis_result.confidence,
            'strengths': analysis_result.result_data.get('strengths', []),
            'development_areas': analysis_result.result_data.get('weaknesses', []),
            'recommendations': analysis_result.recommendations,
        }
    )
```

## 4. 활용 가능한 기능

### 4.1 실시간 인재 분류
- AIRISS에서 분석 완료 시 자동으로 인재풀 업데이트
- AI 점수 기반 자동 분류 (핵심인재, 관리필요인력 등)

### 4.2 승진 후보자 관리
```python
# AIRISS 승진 가능성 분석 → 승진 후보자 자동 등록
if analysis_result.analysis_type.type_code == 'PROMOTION_POTENTIAL' and analysis_result.score >= 75:
    PromotionCandidate.objects.create(
        employee=analysis_result.employee,
        ai_recommendation_score=analysis_result.score,
        readiness_level='NEAR_READY'
    )
```

### 4.3 이직 위험 대응
```python
# AIRISS 이직 위험도 분석 → 즉시 대응 계획 수립
if analysis_result.analysis_type.type_code == 'TURNOVER_RISK' and analysis_result.score >= 70:
    RetentionRisk.objects.create(
        employee=analysis_result.employee,
        risk_score=analysis_result.score,
        risk_level='HIGH',
        retention_strategy='긴급 면담 및 보상 검토'
    )
```

## 5. Django Admin 통합

### 시각적 대시보드
- AI 점수를 색상으로 표시 (80점 이상: 녹색, 60-80: 주황, 60 미만: 빨강)
- 신뢰도를 퍼센트로 표시
- 상태별 배지 표시 (ACTIVE, MONITORING, PENDING)

### 필터링 및 검색
- 인재 카테고리별 필터
- AI 점수 범위 검색
- 부서별, 직급별 인재 현황

## 6. 추천 활용 시나리오

### 시나리오 1: 분기별 인재 검토
1. AIRISS에서 전직원 대상 분석 실행
2. 자동으로 TalentPool 업데이트
3. Django Admin에서 핵심인재 목록 확인
4. 개발 계획 수립 및 추적

### 시나리오 2: 승진 심사
1. AIRISS 승진 가능성 분석 실행
2. PromotionCandidate 자동 생성
3. 준비도 레벨별 후보자 검토
4. 개발 요구사항 추적

### 시나리오 3: 이직 방지
1. AIRISS 이직 위험도 모니터링
2. 위험 수준 HIGH 이상 자동 알림
3. RetentionRisk에서 대응 전략 수립
4. 개입 결과 추적

## 7. 구현 필요 사항

### 7.1 마이그레이션 생성
```bash
python manage.py makemigrations employees
python manage.py migrate
```

### 7.2 AIRISS 연동 신호(Signal) 추가
```python
# employees/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from airiss.models import AIAnalysisResult
from .models_talent import TalentPool

@receiver(post_save, sender=AIAnalysisResult)
def update_talent_pool(sender, instance, created, **kwargs):
    if created:
        TalentPool.update_from_airiss(instance)
```

### 7.3 배치 업데이트 커맨드
```python
# employees/management/commands/sync_airiss_talent.py
from django.core.management.base import BaseCommand
from airiss.models import AIAnalysisResult
from employees.models_talent import TalentPool

class Command(BaseCommand):
    def handle(self, *args, **options):
        for result in AIAnalysisResult.objects.filter(is_valid=True):
            TalentPool.update_from_airiss(result)
```

## 8. 결론

### 현재 상태
✅ **완전히 통합 가능한 구조**
- AIRISS의 AIAnalysisResult와 EHR의 TalentPool이 직접 연결
- 자동 업데이트 메커니즘 구현
- Django Admin에서 시각적 관리 가능

### 주요 이점
1. **자동화**: AIRISS 분석 → EHR 인재풀 자동 업데이트
2. **통합 관리**: 하나의 시스템에서 AI 분석과 인재 관리
3. **실시간성**: 분석 즉시 인재 분류 및 대응
4. **추적 가능**: 모든 변경사항과 이력 관리

### 다음 단계
1. 마이그레이션 실행
2. Django Admin 확인
3. 테스트 데이터로 연동 검증
4. 실제 AIRISS 분석 결과와 연동 테스트