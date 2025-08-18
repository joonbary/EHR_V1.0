# OK금융그룹 직무 트리맵 UI/UX 혁신

## 🎯 개요
OK금융그룹의 직군-직종-직무 3단계 체계를 혁신적인 트리맵 UI로 시각화하는 시스템입니다.

## ✨ 주요 기능

### 1. Non-PL/PL 직군 분할 뷰
- 좌측: Non-PL 직군 (IT/디지털, 경영지원, 금융, 영업)
- 우측: PL 직군 (고객서비스)
- 시각적 구분과 색상 차별화

### 2. 직종별 가로 정렬
- 각 직군 아래 직종을 가로로 배치
- 직종별 직무 개수 표시
- 색상 코딩으로 직관적 구분

### 3. 직무 카드형 UI
- 아이콘과 함께 표시되는 직무 카드
- 호버 시 그라디언트 효과
- 클릭 시 상세 정보 모달

### 4. 인터랙티브 기능
- 드래그 & 줌 (확대/축소)
- 반응형 디자인
- 부드러운 애니메이션
- 키보드 네비게이션

### 5. 모던 디자인
- Material-UI 기반
- Framer Motion 애니메이션
- Font Awesome 아이콘
- 다크 모드 지원

## 🛠 기술 스택
- **Frontend**: React 18, Material-UI 5, Framer Motion
- **Backend**: Django 5.2
- **Icons**: Font Awesome 6
- **Zoom/Pan**: react-zoom-pan-pinch
- **Styling**: CSS3 with Flexbox/Grid

## 📦 설치 방법

### 1. Django 뷰 추가
```python
# job_profiles/views.py
from tree_map_views import JobProfileTreeMapView, job_tree_map_data_api, job_detail_modal_api
```

### 2. URL 패턴 등록
```python
# job_profiles/urls.py
path('tree-map/', JobProfileTreeMapView.as_view(), name='tree_map'),
path('api/tree-map-data/', job_tree_map_data_api, name='tree_map_data_api'),
path('api/job-detail-modal/<uuid:job_role_id>/', job_detail_modal_api, name='job_detail_modal_api'),
```

### 3. 정적 파일 배치
- `JobProfileTreeMap.css` → `static/css/`
- `JobProfileTreeMap.jsx` → `static/js/components/`

### 4. 템플릿 설치
- `job_tree_map.html` → `templates/job_profiles/`

## 🚀 사용법

### 접속 URL
```
http://localhost:8000/job-profiles/tree-map/
```

### 주요 조작법
- **마우스 드래그**: 화면 이동
- **마우스 휠**: 확대/축소
- **직무 카드 클릭**: 상세 정보 보기
- **ESC 키**: 모달 닫기

## 🎨 커스터마이징

### 색상 변경
```javascript
const colorScheme = {
    primary: {
        'IT/디지털': '#3B82F6',  // 원하는 색상으로 변경
        // ...
    }
}
```

### 아이콘 변경
```javascript
const iconMap = {
    '시스템기획': 'sitemap',  // Font Awesome 아이콘명
    // ...
}
```

## 📱 반응형 브레이크포인트
- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

## 🔧 문제 해결

### React 컴포넌트가 로드되지 않을 때
1. 브라우저 콘솔에서 에러 확인
2. React/Material-UI CDN 링크 확인
3. CSRF 토큰 확인

### API 호출 실패 시
1. Django 서버 실행 확인
2. URL 패턴 등록 확인
3. 로그인 상태 확인

## 📄 라이선스
OK금융그룹 내부 사용