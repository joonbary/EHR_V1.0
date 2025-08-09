# AI 모델 연결 설정 가이드

## 📋 목차
1. [개요](#개요)
2. [지원 AI 프로바이더](#지원-ai-프로바이더)
3. [빠른 시작](#빠른-시작)
4. [상세 설정](#상세-설정)
5. [모듈별 설정](#모듈별-설정)
6. [비용 관리](#비용-관리)
7. [문제 해결](#문제-해결)

## 개요

OK금융그룹 HRM AI Quick Win 시스템은 다양한 AI 모델을 지원합니다. 이 가이드는 AI 모델을 연결하고 설정하는 방법을 설명합니다.

## 지원 AI 프로바이더

### 1. OpenAI (GPT-4, GPT-3.5)
- **장점**: 높은 성능, 안정적인 서비스
- **추천 용도**: 일반적인 분석, 인사이트 생성
- **API 키 발급**: https://platform.openai.com/api-keys

### 2. Claude (Anthropic)
- **장점**: 긴 컨텍스트, 안전한 응답
- **추천 용도**: 코칭, 상담, 민감한 정보 처리
- **API 키 발급**: https://console.anthropic.com/

### 3. Google Gemini
- **장점**: 무료 티어 제공, 멀티모달 지원
- **추천 용도**: 이미지 분석, 대량 처리
- **API 키 발급**: https://makersuite.google.com/app/apikey

### 4. Azure OpenAI
- **장점**: 엔터프라이즈 보안, SLA 보장
- **추천 용도**: 기업 환경, 규정 준수 필요
- **설정**: https://azure.microsoft.com/en-us/products/ai-services/openai-service

### 5. Local LLM (Ollama)
- **장점**: 데이터 프라이버시, 오프라인 사용
- **추천 용도**: 민감 데이터, 내부망 환경
- **설치**: https://ollama.ai/

## 빠른 시작

### 1단계: 환경 변수 파일 생성
```bash
cp .env.example .env
```

### 2단계: API 키 설정
`.env` 파일을 열고 사용할 AI 프로바이더의 API 키를 입력합니다:

```env
# OpenAI 사용 시
OPENAI_API_KEY=sk-...your-api-key...
DEFAULT_AI_PROVIDER=openai

# Claude 사용 시
ANTHROPIC_API_KEY=sk-ant-...your-api-key...
DEFAULT_AI_PROVIDER=anthropic

# Google Gemini 사용 시
GOOGLE_AI_API_KEY=AIza...your-api-key...
DEFAULT_AI_PROVIDER=google
```

### 3단계: 서버 재시작
```bash
python manage.py runserver
```

### 4단계: 설정 확인
브라우저에서 `/ai/settings/` 페이지로 이동하여 연결 상태를 확인합니다.

## 상세 설정

### OpenAI 설정

```env
# 필수 설정
OPENAI_API_KEY=your-api-key-here

# 선택 설정
OPENAI_MODEL=gpt-4-turbo-preview  # 모델 선택
OPENAI_TEMPERATURE=0.7             # 0.0-1.0, 낮을수록 일관성 높음
OPENAI_MAX_TOKENS=2000             # 최대 응답 길이
```

**모델 옵션**:
- `gpt-4-turbo-preview`: 최신 GPT-4 모델 (추천)
- `gpt-4`: 표준 GPT-4
- `gpt-3.5-turbo`: 빠르고 저렴한 옵션

### Claude 설정

```env
# 필수 설정
ANTHROPIC_API_KEY=your-api-key-here

# 선택 설정
ANTHROPIC_MODEL=claude-3-opus-20240229  # 모델 선택
ANTHROPIC_MAX_TOKENS=2000               # 최대 응답 길이
```

**모델 옵션**:
- `claude-3-opus-20240229`: 최고 성능 (추천)
- `claude-3-sonnet-20240229`: 균형잡힌 성능
- `claude-3-haiku-20240307`: 빠르고 저렴

### Google Gemini 설정

```env
# 필수 설정
GOOGLE_AI_API_KEY=your-api-key-here

# 선택 설정
GEMINI_MODEL=gemini-pro  # 모델 선택
```

**모델 옵션**:
- `gemini-pro`: 텍스트 생성
- `gemini-pro-vision`: 이미지 + 텍스트

### Local LLM (Ollama) 설정

1. Ollama 설치:
```bash
# Windows
winget install Ollama.Ollama

# Mac
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

2. 모델 다운로드:
```bash
ollama pull llama2
ollama pull mistral
```

3. 환경 변수 설정:
```env
LOCAL_LLM_ENABLED=true
LOCAL_LLM_MODEL=llama2
LOCAL_LLM_ENDPOINT=http://localhost:11434
DEFAULT_AI_PROVIDER=local
```

## 모듈별 설정

각 AI 모듈은 서로 다른 AI 모델을 사용할 수 있습니다:

```env
# AI 인사이트 - GPT-4 사용
AI_INSIGHTS_ENABLED=true
AI_INSIGHTS_MODEL_OVERRIDE=gpt-4-turbo-preview

# 코칭 어시스턴트 - Claude 사용 (공감능력)
AI_COACHING_ENABLED=true
AI_COACHING_MODEL_OVERRIDE=claude-3-opus-20240229

# 이직 예측 - Gemini 사용 (빠른 처리)
AI_PREDICTIONS_ENABLED=true
AI_PREDICTIONS_MODEL_OVERRIDE=gemini-pro
```

## 비용 관리

### 예산 설정
```env
# 월간 예산 (USD)
AI_MONTHLY_BUDGET_USD=100

# 경고 임계값 (%)
AI_ALERT_THRESHOLD=80
```

### 캐싱 설정
```env
# 응답 캐싱으로 비용 절감
AI_ENABLE_CACHING=true
AI_CACHE_TTL=3600  # 1시간
```

### 비용 절감 팁
1. **캐싱 활용**: 반복되는 요청은 캐시에서 처리
2. **모델 선택**: 용도에 맞는 적절한 모델 사용
   - 간단한 작업: GPT-3.5 또는 Gemini
   - 복잡한 분석: GPT-4 또는 Claude Opus
3. **토큰 제한**: `MAX_TOKENS` 설정으로 응답 길이 제한
4. **모듈별 설정**: 중요하지 않은 모듈은 저렴한 모델 사용

## 문제 해결

### 연결 테스트
웹 인터페이스에서 각 프로바이더의 "연결 테스트" 버튼을 클릭하여 확인

### 일반적인 문제

#### 1. "API 키가 유효하지 않습니다"
- API 키가 올바른지 확인
- 키 앞뒤 공백 제거
- 결제 정보가 등록되어 있는지 확인

#### 2. "할당량 초과"
- API 사용량 한도 확인
- 결제 한도 증가 필요
- 다른 프로바이더로 전환 고려

#### 3. "연결 시간 초과"
- 네트워크 연결 확인
- 프록시/방화벽 설정 확인
- `AI_TIMEOUT` 값 증가

#### 4. "모델을 찾을 수 없습니다"
- 모델 이름이 정확한지 확인
- 해당 모델에 대한 액세스 권한 확인
- 최신 모델 목록 확인

### 로그 확인
```bash
# Django 로그 확인
tail -f logs/django.log

# AI 사용량 확인
python manage.py shell
>>> from ai_quickwin.ai_config import ai_config_manager
>>> ai_config_manager.usage_tracker.get_current_usage()
```

## 보안 주의사항

1. **API 키 보호**:
   - `.env` 파일을 절대 Git에 커밋하지 마세요
   - 프로덕션 환경에서는 환경 변수 사용
   - 정기적으로 API 키 교체

2. **데이터 프라이버시**:
   - 민감한 데이터는 Local LLM 사용 고려
   - API 로깅 설정 확인
   - GDPR/개인정보보호법 준수

3. **접근 제어**:
   - AI 설정 페이지는 관리자만 접근
   - 모듈별 권한 설정
   - 사용량 모니터링

## 지원

문제가 있으시면 다음 채널로 문의하세요:
- 기술 지원: tech-support@okfn.com
- 문서: https://docs.okfn.com/ai-quickwin
- GitHub Issues: https://github.com/okfn/ehr-ai-quickwin/issues