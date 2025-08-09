"""
AI 모델 구성 및 프로바이더 관리
"""
import os
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import logging
from django.conf import settings
from django.core.cache import cache
import openai
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI 프로바이더 종류"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    LOCAL = "local"


@dataclass
class AIModelConfig:
    """AI 모델 구성"""
    provider: AIProvider
    model_name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 3


class AIConfigManager:
    """AI 구성 관리자"""
    
    def __init__(self):
        self.configs = self._load_configs()
        self.default_provider = self._get_default_provider()
        self.usage_tracker = AIUsageTracker()
    
    def _load_configs(self) -> Dict[str, AIModelConfig]:
        """환경 변수에서 AI 구성 로드"""
        configs = {}
        
        # OpenAI 구성
        if os.getenv('OPENAI_API_KEY'):
            configs['openai'] = AIModelConfig(
                provider=AIProvider.OPENAI,
                model_name=os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
                api_key=os.getenv('OPENAI_API_KEY'),
                temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
                max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
            )
        
        # Anthropic (Claude) 구성
        if os.getenv('ANTHROPIC_API_KEY'):
            configs['anthropic'] = AIModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name=os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229'),
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                max_tokens=int(os.getenv('ANTHROPIC_MAX_TOKENS', '2000'))
            )
        
        # Google (Gemini) 구성
        if os.getenv('GOOGLE_AI_API_KEY'):
            configs['google'] = AIModelConfig(
                provider=AIProvider.GOOGLE,
                model_name=os.getenv('GEMINI_MODEL', 'gemini-pro'),
                api_key=os.getenv('GOOGLE_AI_API_KEY')
            )
        
        # Azure OpenAI 구성
        if os.getenv('AZURE_OPENAI_API_KEY'):
            configs['azure'] = AIModelConfig(
                provider=AIProvider.AZURE,
                model_name=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4'),
                api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
            )
        
        # Local LLM 구성
        if os.getenv('LOCAL_LLM_ENABLED', 'false').lower() == 'true':
            configs['local'] = AIModelConfig(
                provider=AIProvider.LOCAL,
                model_name=os.getenv('LOCAL_LLM_MODEL', 'llama2'),
                endpoint=os.getenv('LOCAL_LLM_ENDPOINT', 'http://localhost:11434')
            )
        
        return configs
    
    def _get_default_provider(self) -> str:
        """기본 AI 프로바이더 가져오기"""
        return os.getenv('DEFAULT_AI_PROVIDER', 'openai')
    
    def get_config_for_module(self, module_name: str) -> Optional[AIModelConfig]:
        """특정 모듈에 대한 AI 구성 가져오기"""
        # 모듈별 오버라이드 확인
        override_key = f'AI_{module_name.upper()}_MODEL_OVERRIDE'
        override_model = os.getenv(override_key)
        
        if override_model:
            # 오버라이드된 모델 찾기
            for provider, config in self.configs.items():
                if config.model_name == override_model:
                    return config
        
        # 기본 프로바이더 사용
        return self.configs.get(self.default_provider)
    
    def is_module_enabled(self, module_name: str) -> bool:
        """모듈이 활성화되어 있는지 확인"""
        enabled_key = f'AI_{module_name.upper()}_ENABLED'
        return os.getenv(enabled_key, 'true').lower() == 'true'
    
    def get_available_providers(self) -> list:
        """사용 가능한 프로바이더 목록"""
        return list(self.configs.keys())


class AIServiceClient:
    """AI 서비스 클라이언트 - 실제 AI API 호출"""
    
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.cache_enabled = os.getenv('AI_ENABLE_CACHING', 'true').lower() == 'true'
        self.cache_ttl = int(os.getenv('AI_CACHE_TTL', '3600'))
    
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """AI 응답 생성"""
        # 캐시 확인
        if self.cache_enabled:
            cache_key = self._get_cache_key(prompt, system_prompt)
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.info(f"캐시에서 응답 반환: {cache_key[:20]}...")
                return cached_response
        
        try:
            response = self._call_api(prompt, system_prompt, **kwargs)
            
            # 캐시 저장
            if self.cache_enabled and response:
                cache.set(cache_key, response, self.cache_ttl)
            
            return response
            
        except Exception as e:
            logger.error(f"AI API 호출 실패: {e}")
            return self._get_fallback_response(prompt)
    
    def _call_api(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """실제 API 호출"""
        if self.config.provider == AIProvider.OPENAI:
            return self._call_openai(prompt, system_prompt, **kwargs)
        elif self.config.provider == AIProvider.ANTHROPIC:
            return self._call_anthropic(prompt, system_prompt, **kwargs)
        elif self.config.provider == AIProvider.GOOGLE:
            return self._call_google(prompt, system_prompt, **kwargs)
        elif self.config.provider == AIProvider.AZURE:
            return self._call_azure(prompt, system_prompt, **kwargs)
        elif self.config.provider == AIProvider.LOCAL:
            return self._call_local(prompt, system_prompt, **kwargs)
        else:
            raise ValueError(f"지원하지 않는 프로바이더: {self.config.provider}")
    
    def _call_openai(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """OpenAI API 호출 (v1.0+ 호환)"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.config.api_key)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                timeout=self.config.timeout
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            logger.error("OpenAI 라이브러리가 설치되지 않았습니다. pip install openai")
            return ""
        except Exception as e:
            logger.error(f"OpenAI API 호출 실패: {e}")
            raise
    
    def _call_anthropic(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Anthropic Claude API 호출"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.config.api_key)
            
            message = client.messages.create(
                model=self.config.model_name,
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                system=system_prompt if system_prompt else "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except ImportError:
            logger.error("Anthropic 라이브러리가 설치되지 않았습니다. pip install anthropic")
            return ""
        except Exception as e:
            logger.error(f"Anthropic API 호출 실패: {e}")
            raise
    
    def _call_google(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Google Gemini API 호출"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.config.api_key)
            model = genai.GenerativeModel(self.config.model_name)
            
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = model.generate_content(full_prompt)
            
            return response.text
            
        except ImportError:
            logger.error("Google AI 라이브러리가 설치되지 않았습니다. pip install google-generativeai")
            return ""
        except Exception as e:
            logger.error(f"Google AI API 호출 실패: {e}")
            raise
    
    def _call_azure(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Azure OpenAI API 호출 (v1.0+ 호환)"""
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=self.config.api_key,
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
                azure_endpoint=self.config.endpoint
            )
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Azure OpenAI API 호출 실패: {e}")
            raise
    
    def _call_local(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """로컬 LLM API 호출 (Ollama 등)"""
        try:
            import requests
            
            url = f"{self.config.endpoint}/api/generate"
            
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = requests.post(url, json={
                "model": self.config.model_name,
                "prompt": full_prompt,
                "stream": False
            }, timeout=self.config.timeout)
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                logger.error(f"Local LLM API 오류: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Local LLM API 호출 실패: {e}")
            raise
    
    def _get_cache_key(self, prompt: str, system_prompt: Optional[str]) -> str:
        """캐시 키 생성"""
        import hashlib
        content = f"{self.config.provider}:{self.config.model_name}:{system_prompt}:{prompt}"
        return f"ai_cache_{hashlib.md5(content.encode()).hexdigest()}"
    
    def _get_fallback_response(self, prompt: str) -> str:
        """폴백 응답 (API 실패 시)"""
        logger.warning("AI API 호출 실패, 폴백 응답 반환")
        return "AI 서비스가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요."


class AIUsageTracker:
    """AI 사용량 추적"""
    
    def __init__(self):
        self.monthly_budget = float(os.getenv('AI_MONTHLY_BUDGET_USD', '100'))
        self.alert_threshold = float(os.getenv('AI_ALERT_THRESHOLD', '80'))
    
    def track_usage(self, provider: str, tokens: int, cost: float):
        """사용량 기록"""
        cache_key = f"ai_usage_{datetime.now().strftime('%Y%m')}"
        current_usage = cache.get(cache_key, {
            'total_tokens': 0,
            'total_cost': 0,
            'by_provider': {}
        })
        
        current_usage['total_tokens'] += tokens
        current_usage['total_cost'] += cost
        
        if provider not in current_usage['by_provider']:
            current_usage['by_provider'][provider] = {
                'tokens': 0,
                'cost': 0,
                'requests': 0
            }
        
        current_usage['by_provider'][provider]['tokens'] += tokens
        current_usage['by_provider'][provider]['cost'] += cost
        current_usage['by_provider'][provider]['requests'] += 1
        
        cache.set(cache_key, current_usage, 60 * 60 * 24 * 31)  # 31일 보관
        
        # 예산 초과 체크
        if current_usage['total_cost'] > self.monthly_budget * (self.alert_threshold / 100):
            self._send_budget_alert(current_usage['total_cost'])
    
    def get_current_usage(self) -> Dict[str, Any]:
        """현재 월 사용량 조회"""
        cache_key = f"ai_usage_{datetime.now().strftime('%Y%m')}"
        return cache.get(cache_key, {
            'total_tokens': 0,
            'total_cost': 0,
            'by_provider': {}
        })
    
    def _send_budget_alert(self, current_cost: float):
        """예산 초과 알림"""
        logger.warning(f"AI 사용 예산 경고: ${current_cost:.2f} / ${self.monthly_budget:.2f}")
        # TODO: 이메일 또는 슬랙 알림 전송


# 싱글톤 인스턴스
ai_config_manager = AIConfigManager()


def get_ai_client(module_name: str) -> Optional[AIServiceClient]:
    """모듈에 대한 AI 클라이언트 가져오기"""
    if not ai_config_manager.is_module_enabled(module_name):
        logger.info(f"{module_name} 모듈이 비활성화되어 있습니다")
        return None
    
    config = ai_config_manager.get_config_for_module(module_name)
    if not config:
        logger.error(f"{module_name} 모듈에 대한 AI 구성을 찾을 수 없습니다")
        return None
    
    return AIServiceClient(config)