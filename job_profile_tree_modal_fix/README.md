# OK금융그룹 직무 트리맵 단일화 및 인증 제거

## 개요

OK금융그룹 HRIS 시스템의 직무 트리맵을 심플 버전으로 단일화하고, 로그인 기능을 완전히 제거하여 접근성을 개선한 버전입니다.

## 주요 변경사항

### 1. 트리맵 단일화
- React 버전 제거, 순수 JavaScript 버전으로 통일
- 직관적인 카드형 UI
- 빠른 로딩 속도

### 2. 모달/전체화면 상세보기
- 직무 클릭시 모달 팝업으로 상세 정보 표시
- 전체화면 모드 지원
- 편집/삭제 기능 통합

### 3. UI 일관성 개선
- OK금융그룹 브랜드 컬러 시스템
- 통일된 폰트 (Pretendard)
- 일관된 여백과 둥글기
- 다크모드 지원

### 4. 로그인 기능 제거
- 모든 페이지 공개 접근 가능
- 인증 미들웨어 제거
- 루트 경로를 직무 트리맵으로 변경

### 5. 반응형 디자인
- 모바일, 태블릿, 데스크톱 완벽 지원
- 터치 제스처 지원
- 프린트 최적화

## 기술 스택

- **Frontend**: Vanilla JavaScript, CSS3
- **Backend**: Django 4.x
- **Icons**: Font Awesome 6.x
- **Font**: Pretendard

## 설치 방법

1. 파일 복사
```bash
cp -r job_profile_tree_modal_fix/* /path/to/your/project/
```

2. 설정 업데이트
- `settings.py` 파일 수정 (settings_update.py 참고)
- URL 패턴 변경 (root_urls.py 참고)

3. 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

4. 서버 실행
```bash
python manage.py runserver
```

## 사용 방법

1. **메인 화면**: 브라우저에서 `http://localhost:8000/` 접속
2. **직무 검색**: 상단 검색창에서 직무명 검색
3. **필터링**: 기술서 있음/없음 필터 사용
4. **상세보기**: 직무 카드 클릭
5. **편집**: 모달에서 편집 버튼 클릭
6. **전체화면**: 모달에서 전체화면 버튼 클릭

## 디렉토리 구조

```
job_profile_tree_modal_fix/
├── templates/
│   ├── base_modern.html          # 모던 베이스 템플릿
│   ├── job_tree_unified.html     # 통합 트리맵 템플릿
│   └── job_profile_edit.html     # 직무기술서 편집 템플릿
├── static/
│   ├── css/
│   │   └── job_tree_unified.css  # 통합 스타일시트
│   └── js/
│       └── job_tree_unified.js   # 통합 JavaScript
├── views.py                       # 인증 제거된 뷰
├── urls.py                        # 앱 URL 패턴
├── root_urls.py                   # 프로젝트 URL 패턴
├── settings_update.py             # 설정 파일 업데이트 가이드
└── MIGRATION_GUIDE.md             # 마이그레이션 가이드
```

## 브라우저 지원

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Safari 14+
- Chrome for Android 90+

## 라이선스

© 2025 OK금융그룹. All rights reserved.
