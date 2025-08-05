# e-HR 시스템 개발 참조 문서 구조

## 📁 /docs 폴더 구성

```
e-hr-system/
├── docs/
│   ├── 01-project-overview.md     # 프로젝트 전체 개요
│   ├── 02-technical-stack.md      # 기술 스택 및 아키텍처
│   ├── 03-requirements.md         # 상세 요구사항
│   ├── 04-database-design.md      # 데이터베이스 설계
│   ├── 05-security-guidelines.md  # 보안 요구사항
│   ├── 06-ui-ux-guidelines.md     # UI/UX 가이드라인
│   ├── 07-development-workflow.md # 개발 워크플로우
│   ├── 08-testing-strategy.md     # 테스트 전략
│   └── 99-cursor-ai-prompts.md    # Cursor AI 프롬프트 모음
├── README.md                      # 프로젝트 메인 가이드
└── CHANGELOG.md                   # 개발 진행 로그
```

## 🎯 각 문서의 목적

### 01-project-overview.md
- 6개월 MVP 목표
- 주차별 마일스톤
- 핵심 기능 우선순위
- 성공 지표

### 02-technical-stack.md  
- Django 5.2.4 + Python
- Bootstrap 5 UI
- SQLite → PostgreSQL 마이그레이션 계획
- AI 통합 계획 (OpenAI API)

### 03-requirements.md
- 사용자 역할별 기능 명세
- 직원/관리자/HR담당자 권한
- 필수 vs 선택 기능

### 04-database-design.md
- ERD 다이어그램
- 모델 관계도
- 필드 정의 및 제약사항

### 05-security-guidelines.md
- 개인정보보호 요구사항
- RBAC 권한 설계
- 암호화 정책

### 06-ui-ux-guidelines.md
- 디자인 시스템
- 반응형 레이아웃 원칙
- 접근성 가이드라인

### 07-development-workflow.md
- Git 브랜치 전략
- 코드 리뷰 프로세스
- 배포 파이프라인

### 08-testing-strategy.md
- 단위 테스트 가이드
- 통합 테스트 시나리오
- 사용자 수용 테스트 계획

### 99-cursor-ai-prompts.md
- 자주 사용하는 프롬프트 템플릿
- 모듈별 개발 지침
- 오류 해결 패턴

## 💡 Cursor AI 활용 팁

1. **프로젝트 시작 시:** `@docs` 멘션으로 전체 문서 참조
2. **기능 개발 시:** 해당 요구사항 문서 참조
3. **오류 발생 시:** 개발 워크플로우 문서 참조
4. **UI 작업 시:** 디자인 가이드라인 참조

## 🔄 문서 업데이트 주기

- **매일:** 개발 진행 상황 CHANGELOG 업데이트
- **매주:** 요구사항 및 우선순위 재검토
- **매월:** 전체 문서 일관성 점검
