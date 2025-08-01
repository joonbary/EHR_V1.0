
# 직무 통합 시스템 API 명세서

## 개요
직무 프로필 표준화, 검색, AI 챗봇 통합 REST API

## 인증
```
Authorization: Bearer <token>
Content-Type: application/json
```

## 엔드포인트

### 1. 직무 검색 API

#### GET /api/jobs/search/
기본 직무 검색

**Parameters:**
- `q` (string): 검색어
- `page` (int): 페이지 번호 (기본값: 1)
- `page_size` (int): 페이지 크기 (기본값: 20)
- `job_type` (string): 직종 필터
- `job_category` (string): 직군 필터

**Response:**
```json
{
  "success": true,
  "jobs": [
    {
      "id": 1,
      "job_title": "시스템기획",
      "job_type": "IT기획",
      "job_category": "IT/디지털",
      "description": "...",
      "score": 0.95,
      "highlights": {
        "job_title": ["<em>시스템</em>기획"]
      }
    }
  ],
  "total": 37,
  "page": 1,
  "page_size": 20,
  "standardized_query": "시스템기획",
  "suggestions": ["시스템개발", "시스템관리"],
  "processing_time": 0.045
}
```

#### POST /api/jobs/search/
고급 검색

**Request Body:**
```json
{
  "query": "시스템 개발",
  "filters": {
    "job_type": "IT개발",
    "job_category": "IT/디지털",
    "is_active": true
  },
  "page": 1,
  "page_size": 10
}
```

### 2. AI 챗봇 API

#### POST /api/jobs/chatbot/
AI 직무 상담

**Request Body:**
```json
{
  "query": "시스템 기획자가 되려면 어떤 스킬이 필요한가요?",
  "context": {
    "department": "IT",
    "experience": "신입",
    "user_id": 123
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "시스템 기획자가 되기 위해서는...",
  "job_match": {
    "query": "시스템 기획자",
    "matched_job": {
      "job_title": "시스템기획",
      "confidence": 0.95
    }
  },
  "confidence": 0.95,
  "processing_time": 1.23
}
```

### 3. 동기화 API

#### POST /api/jobs/sync/
데이터 동기화

**Request Body:**
```json
{
  "type": "single",  // "single" | "all"
  "job_id": 1        // type이 "single"인 경우
}
```

**Response:**
```json
{
  "operation": "elasticsearch_sync",
  "affected_records": 1,
  "success": true,
  "error_message": null,
  "timestamp": "2025-07-26T18:45:00Z"
}
```

### 4. 자동완성 API

#### GET /api/jobs/suggestions/
직무명 자동완성

**Parameters:**
- `q` (string): 부분 검색어
- `limit` (int): 최대 결과 수 (기본값: 10)

**Response:**
```json
{
  "suggestions": [
    "시스템기획",
    "시스템개발",
    "시스템관리"
  ]
}
```

## 에러 응답

**400 Bad Request:**
```json
{
  "success": false,
  "error": "Invalid query parameter",
  "details": "Query parameter 'q' is required"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Internal server error",
  "details": "Elasticsearch connection failed"
}
```

## 사용 예제

### JavaScript
```javascript
// 직무 검색
const searchJobs = async (query) => {
  const response = await fetch(`/api/jobs/search/?q=${encodeURIComponent(query)}`);
  return await response.json();
};

// AI 챗봇
const askChatbot = async (query, context) => {
  const response = await fetch('/api/jobs/chatbot/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, context })
  });
  return await response.json();
};
```

### Python
```python
import requests

# 직무 검색
response = requests.get('/api/jobs/search/', params={'q': '시스템기획'})
jobs = response.json()

# AI 챗봇
response = requests.post('/api/jobs/chatbot/', json={
  'query': '데이터 분석가가 되려면?',
  'context': {'experience': '신입'}
})
chatbot_response = response.json()
```
