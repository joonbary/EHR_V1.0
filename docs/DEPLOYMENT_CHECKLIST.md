# 배포 체크리스트 - EHR Evaluation System

## 🚀 Railway 배포 전 체크리스트

### 1. 코드 준비
- [ ] **브랜치 확인**: main 브랜치에서 작업 중인지 확인
- [ ] **코드 리뷰**: 모든 변경사항 검토
- [ ] **테스트 실행**: 로컬에서 모든 기능 테스트
- [ ] **Lint 검사**: Python 코드 스타일 확인
```bash
python -m flake8 .
```

### 2. 의존성 관리
- [ ] **requirements.txt 업데이트**: 새로운 패키지 추가 확인
```bash
pip freeze > requirements.txt
```
- [ ] **필수 라이브러리 확인**:
  - ✅ Django==5.2.4
  - ✅ psycopg2-binary==2.9.9
  - ✅ gunicorn==21.2.0
  - ✅ faker==28.4.1 (직원 데이터 생성용)

### 3. 환경 변수
- [ ] **Railway 환경 변수 확인**:
```bash
railway variables
```
- [ ] **필수 환경 변수**:
  - `DATABASE_URL` - PostgreSQL 연결 문자열
  - `SECRET_KEY` - Django 시크릿 키
  - `OPENAI_API_KEY` - AI 피드백용 (선택)
  - `DEBUG=False` - 프로덕션 환경

### 4. 데이터베이스
- [ ] **마이그레이션 파일 확인**:
```bash
python manage.py makemigrations --dry-run
```
- [ ] **마이그레이션 종속성 확인**: 순서대로 적용되는지 확인
- [ ] **데이터 백업**: 중요 데이터 백업
- [ ] **초기화 스크립트 제거**: railway.toml에 reset 스크립트 없는지 확인

### 5. Railway 설정 파일
- [ ] **railway.toml 확인** (railway.json 아님!):
```toml
[deploy]
startCommand = "python fix_migration_dependency.py && python load_safe_employees.py && python manage.py collectstatic --noinput && gunicorn ..."
```
- [ ] **초기화 스크립트 없음**: `railway_complete_reset.py` 제거 확인
- [ ] **데이터 로드 스크립트**: `load_safe_employees.py` 포함 확인

### 6. 정적 파일
- [ ] **Static 파일 수집**:
```bash
python manage.py collectstatic --noinput
```
- [ ] **WhiteNoise 설정**: settings.py에서 확인
- [ ] **STATIC_ROOT 설정**: 올바른 경로 확인

## 📝 배포 프로세스

### 1단계: 로컬 테스트
```bash
# 1. 로컬 서버 실행
python manage.py runserver

# 2. 주요 기능 테스트
- 로그인: http://localhost:8000/
- 직원 목록: http://localhost:8000/employees/list/
- 평가 페이지: http://localhost:8000/evaluations/

# 3. 디버그 확인
http://localhost:8000/employees/system/debug/
```

### 2단계: Git 커밋
```bash
# 1. 상태 확인
git status

# 2. 변경사항 추가
git add -A

# 3. 커밋 (의미있는 메시지)
git commit -m "feat: 기능 설명" 
# 또는
git commit -m "fix: 버그 수정 설명"

# 4. 푸시
git push origin main
```

### 3단계: Railway 배포
```bash
# 1. Railway 로그 모니터링
railway logs

# 2. 배포 상태 확인
railway status

# 3. 필요시 재시작
railway restart
```

### 4단계: 배포 확인
- [ ] **사이트 접속**: https://ehrv10-production.up.railway.app/
- [ ] **직원 데이터 확인**: /employees/list/
- [ ] **시스템 상태**: /employees/system/debug/
- [ ] **오류 로그 확인**: Railway 대시보드

## 🔴 문제 발생 시

### 1. 직원 데이터 0명
```bash
# 1. 디버그 엔드포인트 확인
https://ehrv10-production.up.railway.app/employees/system/debug/

# 2. Railway 로그 확인
railway logs | grep "직원"

# 3. 강제 데이터 로드
https://ehrv10-production.up.railway.app/employees/system/force-load/
```

### 2. 500 에러
```bash
# 1. Railway 로그 확인
railway logs

# 2. 일반적인 원인
- 마이그레이션 오류
- 환경 변수 누락
- 모듈 import 오류
```

### 3. 데이터베이스 연결 실패
```bash
# 1. DATABASE_URL 확인
railway variables

# 2. PostgreSQL 연결 테스트
python manage.py dbshell
```

## ✅ 배포 후 체크리스트

### 기능 확인
- [ ] **로그인/로그아웃** 작동
- [ ] **직원 목록** 표시 (1000명)
- [ ] **직원 검색** 기능
- [ ] **평가 생성** 가능
- [ ] **AI 피드백** 생성 (API 키 있는 경우)

### 성능 확인
- [ ] **페이지 로딩** 시간 (3초 이내)
- [ ] **API 응답** 속도
- [ ] **데이터베이스 쿼리** 최적화

### 보안 확인
- [ ] **DEBUG=False** 설정
- [ ] **SECRET_KEY** 환경 변수 사용
- [ ] **ALLOWED_HOSTS** 올바르게 설정
- [ ] **HTTPS** 사용 중

## 📊 모니터링

### Railway 대시보드
- **메트릭스**: CPU, 메모리, 네트워크 사용량
- **로그**: 실시간 애플리케이션 로그
- **배포 히스토리**: 이전 배포 기록

### 커스텀 모니터링
- `/employees/system/debug/` - 시스템 상태
- `/api/health/` - 헬스 체크 (구현 필요)

## 🔄 롤백 절차

### Git 롤백
```bash
# 1. 이전 커밋으로 되돌리기
git log --oneline  # 커밋 히스토리 확인
git revert HEAD    # 마지막 커밋 취소
git push origin main

# 2. 특정 커밋으로 리셋 (주의!)
git reset --hard <commit-hash>
git push --force origin main
```

### Railway 롤백
```bash
# Railway 대시보드에서 이전 배포로 롤백
# Settings > Deployments > Rollback
```

## 📋 일일 체크리스트

### 매일 확인
- [ ] Railway 로그 확인 (오류 없는지)
- [ ] 직원 데이터 수 확인
- [ ] 시스템 리소스 사용량
- [ ] 백업 상태

### 주간 확인
- [ ] 데이터베이스 최적화
- [ ] 로그 파일 정리
- [ ] 보안 업데이트 확인
- [ ] 성능 메트릭 분석

## 🔗 참고 문서
- [RAILWAY_DEPLOYMENT_TROUBLESHOOTING.md](../RAILWAY_DEPLOYMENT_TROUBLESHOOTING.md)
- [CLAUDE.md](../CLAUDE.md)
- [Railway 공식 문서](https://docs.railway.app/)

---
문서 버전: 1.0
최종 수정: 2025-01-27