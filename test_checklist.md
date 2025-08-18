# Revolutionary 템플릿 테스트 체크리스트

## 1. 기본 조직도 (/employees/org-chart/)
- [ ] 페이지 접속 가능
- [ ] 다크 배경 표시 확인
- [ ] 시안색 (#00d4ff) 강조 색상 확인
- [ ] 버튼 호버 효과 동작
- [ ] 조직도 데이터 로딩
- [ ] 전체 펼치기/접기 버튼 동작
- [ ] 원본 크기/중앙 정렬 버튼 동작

## 2. 고급 조직도 관리 (/organization/chart/)
- [ ] 페이지 접속 가능
- [ ] Revolutionary 테마 적용 확인
- [ ] 상단 애니메이션 글로우 효과
- [ ] 기능 카드 호버 효과
- [ ] "기본 조직도" 버튼으로 이동 가능
- [ ] "React 앱에서 열기" 버튼 표시

## 3. 공통 확인사항
- [ ] 네비게이션 바 Revolutionary 스타일
- [ ] 폰트 및 아이콘 정상 표시
- [ ] 반응형 디자인 (모바일/태블릿)
- [ ] 콘솔 에러 없음
- [ ] 페이지 로딩 속도 적절

## 4. 크로스 브라우저 테스트
- [ ] Chrome
- [ ] Firefox  
- [ ] Safari
- [ ] Edge

## 5. 시크릿/프라이빗 모드 테스트
- [ ] 캐시 없이도 스타일 정상 적용
- [ ] 모든 리소스 정상 로딩

## 테스트 명령어

### 캐시 강제 새로고침
- Windows/Linux: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### 개발자 도구 열기
- Windows/Linux: `F12` 또는 `Ctrl + Shift + I`
- Mac: `Cmd + Option + I`

### 콘솔 에러 확인
```javascript
// 개발자 도구 콘솔에서 실행
console.clear();
// 페이지 새로고침 후 에러 확인
```

## 문제 해결

### 스타일이 적용되지 않는 경우
1. 브라우저 캐시 삭제
2. Django 서버 재시작: `python manage.py runserver`
3. Static 파일 재수집: `python manage.py collectstatic --noinput`

### 404 에러가 발생하는 경우
1. URL 경로 확인
2. Django urls.py 설정 확인
3. 서버 로그 확인

### 데이터가 표시되지 않는 경우
1. Employee 모델에 데이터 존재 확인
2. API 엔드포인트 응답 확인
3. 브라우저 콘솔에서 네트워크 탭 확인