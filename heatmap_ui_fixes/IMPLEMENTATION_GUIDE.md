
# 스킬맵 히트맵 UI 최적화 구현 가이드

## 🎯 목표
1. 세로 찌그러짐 해결
2. 레이블 겹침 방지
3. 반응형 레이아웃 구현
4. 사용자 경험 개선

## 📋 구현 체크리스트

### 1. Plotly 버전 구현
- [ ] plotly_heatmap.html 파일 생성
- [ ] 동적 높이 계산 로직 구현
- [ ] 레이블 회전 및 폰트 크기 적용
- [ ] 컬러 스케일 개선
- [ ] 다운로드 기능 추가

### 2. Chart.js 버전 구현
- [ ] Chart.js matrix 플러그인 설치
- [ ] OptimizedHeatmap 클래스 구현
- [ ] 동적 셀 크기 계산
- [ ] 반응형 대응

### 3. CSS 스타일링
- [ ] heatmap_optimized.css 적용
- [ ] 스크롤바 스타일링
- [ ] 다크 모드 지원
- [ ] 프린트 스타일

### 4. React 통합
- [ ] HeatmapOptimized.jsx 컴포넌트 생성
- [ ] 필터 기능 구현
- [ ] 로딩/에러 상태 처리
- [ ] 클릭 이벤트 핸들링

### 5. Django 통합
- [ ] 템플릿 파일 업데이트
- [ ] View 로직 수정
- [ ] JSON 데이터 전달
- [ ] 필터 파라미터 처리

## 🚀 적용 방법

### Step 1: 파일 복사
```bash
# CSS 파일
cp heatmap_optimized.css static/css/

# JavaScript 파일
cp OptimizedHeatmap.js static/js/

# 템플릿 파일
cp heatmap_template.html templates/skillmap/
```

### Step 2: Django View 수정
```python
def skillmap_heatmap_view(request):
    # 필터 파라미터
    department = request.GET.get('department')
    skill_category = request.GET.get('skill_category')
    
    # 데이터 조회 및 필터링
    data = get_heatmap_data(department, skill_category)
    
    # JSON 변환
    context = {
        'employees_json': json.dumps(data['employees']),
        'skills_json': json.dumps(data['skills']),
        'values_json': json.dumps(data['values']),
        'departments': Department.objects.all(),
        'skill_categories': Skill.CATEGORY_CHOICES
    }
    
    return render(request, 'skillmap/heatmap_template.html', context)
```

### Step 3: React 적용 (선택사항)
```bash
npm install react-plotly.js plotly.js
```

## 📊 성능 최적화

### 1. 데이터 제한
- 최대 100명 × 50개 스킬 권장
- 페이지네이션 고려
- 필터링으로 데이터 축소

### 2. 렌더링 최적화
- 디바운싱된 리사이즈 핸들러
- 메모이제이션 사용
- 가상 스크롤 고려 (대량 데이터)

### 3. 캐싱
- 서버 사이드 캐싱
- 클라이언트 사이드 캐싱
- CDN 활용

## 🐛 트러블슈팅

### 문제: 여전히 찌그러짐
- 해결: calculatedHeight 값 확인
- 최소 셀 높이 증가 (20px → 25px)

### 문제: 레이블 여전히 겹침
- 해결: 폰트 크기 더 축소
- tickangle 조정 (-45 → -90)

### 문제: 성능 저하
- 해결: 데이터 샘플링
- WebGL 렌더러 사용

## 📱 모바일 대응

### 터치 인터랙션
- 탭으로 상세 정보 표시
- 핀치 줌 지원
- 가로 모드 권장

### 레이아웃 조정
- 모바일에서 범례 위치 변경
- 필터 UI 간소화
- 여백 축소

## 🎨 커스터마이징

### 컬러 스케일 변경
```javascript
colorscale: [
    [0, 'rgb(255,255,255)'],      // 0% - 흰색
    [0.5, 'rgb(255,255,0)'],       // 50% - 노란색
    [1, 'rgb(255,0,0)']            // 100% - 빨간색
]
```

### 호버 템플릿 커스터마이징
```javascript
hovertemplate: 
    '<b>%{y}</b><br>' +
    'Skill: %{x}<br>' +
    'Level: %{z}%<br>' +
    'Department: ' + department + '<br>' +
    '<extra></extra>'
```

## 📝 테스트

### 단위 테스트
- 동적 크기 계산 함수
- 필터링 로직
- 데이터 변환

### E2E 테스트
- 다양한 데이터 크기
- 필터 동작
- 반응형 동작
- 다운로드 기능

## 🔗 참고 자료
- [Plotly Heatmap Documentation](https://plotly.com/javascript/heatmaps/)
- [Chart.js Matrix Plugin](https://github.com/kurkle/chartjs-chart-matrix)
- [ColorBrewer Color Schemes](https://colorbrewer2.org/)
