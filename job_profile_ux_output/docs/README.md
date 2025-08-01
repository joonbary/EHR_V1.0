
# 직무기술서 트리 시각화 UI/UX 시스템

## 🚀 주요 기능

### 📊 시각화 모드
- **트리뷰**: 계층형 구조로 전체 직무 체계 표시
- **그리드뷰**: 카드 형태로 직무들을 그리드 레이아웃으로 표시  
- **맵뷰**: D3.js 기반 인터랙티브 트리맵 시각화

### 🎨 현대적 UI/UX
- **반응형 디자인**: 모바일/태블릿/데스크톱 완전 대응
- **다크모드 지원**: 사용자 환경 설정에 따른 자동 테마 전환
- **부드러운 애니메이션**: Framer Motion 기반 마이크로 인터랙션
- **직관적 내비게이션**: 브레드크럼, 줌/드래그, 클릭 투 디테일

### 🔍 고급 검색 및 필터링
- **실시간 검색**: 직무명, 설명, 카테고리 통합 검색
- **하이라이팅**: 검색어 자동 강조 표시
- **다중 필터**: 직군, 직종별 필터링
- **자동완성**: 스마트 검색 제안

### 📱 인터랙티브 기능
- **원클릭 상세보기**: 카드/노드 클릭으로 상세 정보 즉시 표시
- **관심직무 관리**: 북마크 및 관심직무 등록
- **소셜 기능**: 직무 정보 공유 및 추천
- **PDF 다운로드**: 직무기술서 PDF 생성 및 다운로드

## 🛠 기술 스택

### 프론트엔드
- **React 18** / **Vue 3**: 모던 프론트엔드 프레임워크
- **Ant Design**: 엔터프라이즈급 UI 컴포넌트
- **Framer Motion**: 고성능 애니메이션 라이브러리
- **D3.js**: 데이터 시각화
- **TypeScript**: 타입 안전성

### 백엔드  
- **Django REST Framework**: API 서버
- **PostgreSQL**: 메인 데이터베이스
- **Redis**: 캐싱 및 세션 관리

### 배포 및 인프라
- **Docker**: 컨테이너화
- **Nginx**: 웹 서버 및 리버스 프록시
- **CI/CD**: GitHub Actions

## 📦 설치 및 실행

### 1. 의존성 설치
```bash
npm install
# 또는
yarn install
```

### 2. 개발 서버 실행
```bash
npm run dev
# 또는  
yarn dev
```

### 3. Django 백엔드 설정
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 🎯 사용법

### React 컴포넌트 사용
```jsx
import JobTreeVisualization from './components/JobTreeVisualization';

function App() {
  const handleJobSelect = (job) => {
    console.log('선택된 직무:', job);
  };

  return (
    <JobTreeVisualization 
      jobData={jobTreeData}
      onJobSelect={handleJobSelect}
    />
  );
}
```

### Vue 컴포넌트 사용
```vue
<template>
  <JobTreeVisualization 
    :job-data="jobTreeData"
    @job-select="handleJobSelect"
  />
</template>

<script setup>
import JobTreeVisualization from './components/JobTreeVisualization.vue'

const handleJobSelect = (job) => {
  console.log('선택된 직무:', job)
}
</script>
```

### API 엔드포인트
- `GET /api/job-tree/` - 전체 직무 트리 구조
- `GET /api/job-profiles/{id}/` - 특정 직무 상세 정보
- `GET /api/job-search/` - 직무 검색
- `GET /api/job-statistics/` - 직무 통계

## 🎨 커스터마이징

### 색상 테마 변경
```javascript
// JobTreeVisualization.jsx에서
const categoryColors = {
  'IT/디지털': '#3B82F6',    // 파란색
  '경영지원': '#10B981',     // 초록색  
  '금융': '#F59E0B',        // 주황색
  '영업': '#EF4444',        // 빨간색
  '고객서비스': '#8B5CF6'    // 보라색
};
```

### 아이콘 매핑 추가
```javascript
const jobIcons = {
  '시스템기획': 'fas fa-project-diagram',
  '시스템개발': 'fas fa-code',
  // 새로운 아이콘 추가...
};
```

## 🔧 API 연동

### Django 모델과 연동
```python
# models.py
class JobProfile(models.Model):
    job_role = models.OneToOneField(JobRole, on_delete=models.CASCADE)
    role_responsibility = models.TextField()
    qualification = models.TextField()
    basic_skills = models.JSONField(default=list)
    applied_skills = models.JSONField(default=list)
```

### API 뷰 확장
```python
# views.py
@api_view(['GET'])
def custom_job_api(request):
    # 커스텀 로직 구현
    pass
```

## 📈 성능 최적화

### 가상화 및 레이지 로딩
- 대용량 데이터를 위한 가상 스크롤링
- 이미지 및 컴포넌트 레이지 로딩
- 메모이제이션을 통한 렌더링 최적화

### 캐싱 전략
- API 응답 캐싱 (Redis)
- 브라우저 캐싱 최적화
- CDN을 통한 정적 자원 배포

## 🔒 보안

### 인증 및 권한
- JWT 토큰 기반 인증
- 역할 기반 접근 제어 (RBAC)
- CORS 설정 최적화

### 데이터 보호
- API 입력 유효성 검사
- SQL 인젝션 방지
- XSS 공격 방어

## 🌐 브라우저 지원

- Chrome 90+
- Firefox 88+  
- Safari 14+
- Edge 90+
- Mobile Safari 14+
- Chrome Mobile 90+

## 📄 라이선스

MIT License - 자세한 내용은 LICENSE 파일 참조

## 🤝 기여하기

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

- 이슈 트래커: GitHub Issues
- 이메일: support@company.com
- 문서: [Documentation Site]

---

💡 **Tip**: 최상의 경험을 위해 최신 버전의 브라우저를 사용하세요.
