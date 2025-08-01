
# OK금융그룹 평가관리 시스템 구현 가이드

## 🎯 핵심 개념
- **3대 평가축**: 기여도(Contribution), 전문성(Expertise), 영향력(Impact)
- **Calibration Session**: 평가 위원회를 통한 최종 등급 조정
- **성장레벨**: 직무별 요구 수준에 따른 성장 단계

## 📊 평가 등급 체계
### 1차 평가 (A/B/C)
- A: 3대 평가 중 2개 이상 달성
- B: 3대 평가 중 1개 달성
- C: 3대 평가 모두 미달성

### 최종 등급 (7단계)
- S, A+, A, B+, B, C, D
- Calibration Session을 통해 최종 결정

## 🔧 기술 스택
- Backend: Django 3.2+
- Frontend: Tailwind CSS + Alpine.js
- Database: PostgreSQL
- Task Queue: Celery (선택사항)

## 📁 프로젝트 구조
```
evaluations/
├── models.py          # 평가 관련 모델
├── views.py           # 기본 뷰
├── views_advanced.py  # 고급 기능 뷰
├── services.py        # 비즈니스 로직
├── urls.py           # URL 라우팅
└── templates/
    └── evaluations/  # 평가 템플릿
```
