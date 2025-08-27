# API Documentation - EHR Evaluation System

## 🔌 API 엔드포인트 전체 목록

### 인증 (Authentication)
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/api/auth/login/` | 사용자 로그인 | `{username, password}` | `{token, user_info}` |
| POST | `/api/auth/logout/` | 로그아웃 | - | `{message}` |
| GET | `/api/auth/me/` | 현재 사용자 정보 | - | `{user_data}` |

### 직원 관리 (Employees)
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/employees/` | 직원 목록 조회 | `?page=1&search=김` | `{count, results[]}` |
| GET | `/api/employees/{id}/` | 직원 상세 정보 | - | `{employee_data}` |
| POST | `/api/employees/` | 직원 생성 | `{name, email, department...}` | `{employee_data}` |
| PUT | `/api/employees/{id}/` | 직원 정보 수정 | `{updated_fields}` | `{employee_data}` |
| DELETE | `/api/employees/{id}/` | 직원 삭제 | - | `{message}` |
| POST | `/api/employees/bulk-upload/` | 대량 업로드 | `FormData(file)` | `{success_count, errors[]}` |

### 평가 관리 (Evaluations)
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/evaluations/` | 평가 목록 | `?status=pending` | `{count, results[]}` |
| GET | `/api/evaluations/{id}/` | 평가 상세 | - | `{evaluation_data}` |
| POST | `/api/evaluations/` | 평가 생성 | `{employee_id, period...}` | `{evaluation_data}` |
| POST | `/api/evaluations/{id}/submit/` | 평가 제출 | `{scores, feedback}` | `{evaluation_data}` |
| POST | `/api/evaluations/{id}/approve/` | 평가 승인 | `{comments}` | `{evaluation_data}` |
| POST | `/api/evaluations/feedbacks/generate_ai/` | AI 피드백 생성 | `{evaluation_id}` | `{feedback_text}` |

### 평가 유형별 API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/evaluations/contribution/` | 기여도 평가 목록 |
| GET | `/api/evaluations/expertise/` | 전문성 평가 목록 |
| GET | `/api/evaluations/impact/` | 임팩트 평가 목록 |
| GET | `/api/evaluations/comprehensive/` | 종합 평가 목록 |

### 조직도 (Organization)
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/organization/org/units/` | 조직 단위 목록 | - | `{units[]}` |
| GET | `/api/organization/org/units/tree/` | 조직도 트리 구조 | - | `{tree_data}` |
| GET | `/api/organization/org/units/group/matrix/` | 기능×리더 매트릭스 | - | `{matrix_data}` |
| POST | `/api/organization/org/whatif/reassign/` | What-if 분석 | `{changes[]}` | `{preview}` |
| POST | `/api/organization/org/scenarios/` | 시나리오 저장 | `{name, data}` | `{scenario}` |
| POST | `/api/organization/org/io/import/` | Excel 임포트 | `FormData(file)` | `{result}` |
| GET | `/api/organization/org/io/export/` | Excel 익스포트 | - | `File download` |

### 보상 관리 (Compensation)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/compensation/salary-tables/` | 급여 테이블 조회 |
| GET | `/api/compensation/employee/{id}/` | 직원별 보상 정보 |
| POST | `/api/compensation/calculate/` | 보상 계산 |

### 알림 (Notifications)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/` | 알림 목록 |
| PUT | `/api/notifications/{id}/read/` | 알림 읽음 처리 |
| DELETE | `/api/notifications/{id}/` | 알림 삭제 |

### AI 서비스
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chatbot/` | AI 챗봇 대화 |
| POST | `/api/ai/insights/generate/` | AI 인사이트 생성 |
| POST | `/api/ai/predictions/turnover/` | 이직 예측 |
| POST | `/api/ai/coaching/session/` | AI 코칭 세션 |

## 🔐 인증 및 권한

### 인증 방식
```python
# Token Authentication
headers = {
    'Authorization': 'Token {your_token}'
}

# Session Authentication (웹 브라우저)
# Django 세션 쿠키 자동 사용
```

### 권한 레벨
- **Admin**: 모든 API 접근 가능
- **HR**: 직원 관리, 평가 승인, 보상 관리
- **Evaluator**: 평가 생성 및 제출
- **Employee**: 자신의 정보 조회, 자기 평가

## 📊 공통 응답 형식

### 성공 응답
```json
{
    "status": "success",
    "data": {
        // 실제 데이터
    },
    "message": "작업이 성공적으로 완료되었습니다."
}
```

### 오류 응답
```json
{
    "status": "error",
    "error": {
        "code": "INVALID_INPUT",
        "message": "잘못된 입력값입니다.",
        "details": {
            "field": ["오류 메시지"]
        }
    }
}
```

### 페이지네이션
```json
{
    "count": 100,
    "next": "http://api/employees/?page=2",
    "previous": null,
    "results": [...]
}
```

## 🔍 필터링 및 검색

### 직원 검색 예시
```
GET /api/employees/?search=김&department=IT&position=MANAGER&page=1
```

### 평가 필터링 예시
```
GET /api/evaluations/?status=pending&evaluator_id=123&period=2025Q1
```

## 📝 주요 Request/Response 예시

### 직원 생성
**Request:**
```json
POST /api/employees/
{
    "name": "김철수",
    "email": "kim@company.com",
    "department": "IT",
    "position": "MANAGER",
    "phone": "010-1234-5678",
    "hire_date": "2025-01-01"
}
```

**Response:**
```json
{
    "id": 1001,
    "name": "김철수",
    "email": "kim@company.com",
    "department": "IT",
    "position": "MANAGER",
    "created_at": "2025-01-27T10:00:00Z"
}
```

### AI 피드백 생성
**Request:**
```json
POST /api/evaluations/feedbacks/generate_ai/
{
    "evaluation_id": 123,
    "criteria": "technical_skills",
    "score": 4
}
```

**Response:**
```json
{
    "feedback": "직원의 기술적 역량이 우수합니다. 특히 시스템 설계와 구현 능력이 뛰어나며...",
    "suggestions": ["리더십 역량 강화", "멘토링 활동 참여"]
}
```

## 🚨 오류 코드

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTH_REQUIRED` | 인증이 필요합니다 | 401 |
| `PERMISSION_DENIED` | 권한이 없습니다 | 403 |
| `NOT_FOUND` | 리소스를 찾을 수 없습니다 | 404 |
| `VALIDATION_ERROR` | 유효성 검사 실패 | 400 |
| `SERVER_ERROR` | 서버 내부 오류 | 500 |
| `RATE_LIMIT` | 요청 제한 초과 | 429 |

## 🔧 개발/테스트 환경

### 로컬 개발
```
http://localhost:8000/api/
```

### Railway 프로덕션
```
https://ehrv10-production.up.railway.app/api/
```

### Postman Collection
프로젝트 루트의 `postman_collection.json` 파일 임포트

## 📚 관련 문서
- [CLAUDE.md](../CLAUDE.md) - 프로젝트 개요
- [RAILWAY_DEPLOYMENT_TROUBLESHOOTING.md](../RAILWAY_DEPLOYMENT_TROUBLESHOOTING.md) - 배포 문제 해결

---
문서 버전: 1.0
최종 수정: 2025-01-27