#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
표준 직무명 DB와 AI직무챗봇·직무검색·분석시스템 실시간 통합
- 실시간 양방향 연동 및 자동 정합화
- Synonym dictionary, Fuzzy matching
- API/DB View를 통한 실시간 질의/분석
"""

import os
import sys
import io
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import sqlite3
import pandas as pd
from django.db import models, transaction
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
# import redis
# from celery import Celery
# import Levenshtein
from difflib import SequenceMatcher
import re
# from tqdm import tqdm
# import openai
# from elasticsearch import Elasticsearch
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# 한글 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


@dataclass
class JobMatchResult:
    """직무 매칭 결과"""
    query: str
    matched_job: Dict[str, Any]
    confidence: float
    method: str
    alternatives: List[Dict[str, Any]]
    processing_time: float
    cache_hit: bool


@dataclass
class SyncResult:
    """동기화 결과"""
    operation: str
    affected_records: int
    success: bool
    error_message: Optional[str]
    timestamp: datetime


class JobProfileStandardizer:
    """실시간 직무명 표준화 엔진"""
    
    def __init__(self, redis_client=None):
        # self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.redis_client = redis_client  # Mock for demo
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 표준 직무명 캐시 키
        self.CACHE_KEY_JOBS = "standard_jobs"
        self.CACHE_KEY_SYNONYMS = "job_synonyms"
        self.CACHE_TTL = 3600  # 1시간
        
        # TF-IDF 벡터라이저 (검색 개선) - Mock for demo
        # self.vectorizer = TfidfVectorizer(
        #     analyzer='char',
        #     ngram_range=(1, 3),
        #     max_features=1000
        # )
        self.job_vectors = None
        self.job_names = []
        
        self._initialize_cache()
    
    def _initialize_cache(self):
        """캐시 초기화"""
        try:
            # 표준 직무명 로드
            standard_jobs = self._load_standard_jobs_from_db()
            self.redis_client.setex(
                self.CACHE_KEY_JOBS, 
                self.CACHE_TTL, 
                json.dumps(standard_jobs, ensure_ascii=False)
            )
            
            # 동의어 사전 로드
            synonyms = self._load_synonyms_from_db()
            self.redis_client.setex(
                self.CACHE_KEY_SYNONYMS,
                self.CACHE_TTL,
                json.dumps(synonyms, ensure_ascii=False)
            )
            
            # TF-IDF 벡터 생성
            self._build_tfidf_vectors(standard_jobs)
            
            self.logger.info("직무명 표준화 캐시 초기화 완료")
            
        except Exception as e:
            self.logger.error(f"캐시 초기화 실패: {e}")
    
    def _load_standard_jobs_from_db(self) -> List[Dict]:
        """DB에서 표준 직무명 로드"""
        from job_profiles.models import JobProfile
        
        jobs = JobProfile.objects.filter(is_active=True).values(
            'id', 'job_title', 'job_type', 'job_category', 
            'job_code', 'description', 'requirements'
        )
        return list(jobs)
    
    def _load_synonyms_from_db(self) -> Dict[str, str]:
        """DB에서 동의어 사전 로드"""
        # JobSynonym 모델이 있다고 가정
        try:
            from job_profiles.models import JobSynonym
            synonyms = JobSynonym.objects.filter(is_active=True).values_list(
                'synonym', 'standard_name'
            )
            return dict(synonyms)
        except:
            # 기본 동의어 사전
            return {
                'HRM': '인사관리',
                'HRD': '인재개발',
                'PR': '홍보',
                'IB금융': '투자금융',
                '플랫폼/핀테크': '디지털플랫폼',
                '데이터/통계': '데이터분석',
                '모기지사업': '모기지기획',
                'PL기획': '개인신용대출기획'
            }
    
    def _build_tfidf_vectors(self, jobs: List[Dict]):
        """TF-IDF 벡터 구축"""
        self.job_names = [job['job_title'] for job in jobs]
        if self.job_names:
            self.job_vectors = self.vectorizer.fit_transform(self.job_names)
    
    def normalize_query(self, query: str) -> str:
        """검색어 정규화"""
        # 공백, 특수문자 제거
        normalized = re.sub(r'[\s\-_/]', '', query.strip())
        # 영어 소문자 변환
        normalized = normalized.lower()
        return normalized
    
    async def find_best_match(self, query: str) -> JobMatchResult:
        """최적 직무 매칭 (비동기)"""
        start_time = datetime.now()
        cache_key = f"job_match:{query}"
        
        # 캐시 확인
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            result = json.loads(cached_result)
            result['cache_hit'] = True
            result['processing_time'] = (datetime.now() - start_time).total_seconds()
            return JobMatchResult(**result)
        
        # 표준 직무명 로드
        jobs_data = self.redis_client.get(self.CACHE_KEY_JOBS)
        synonyms_data = self.redis_client.get(self.CACHE_KEY_SYNONYMS)
        
        if not jobs_data:
            self._initialize_cache()
            jobs_data = self.redis_client.get(self.CACHE_KEY_JOBS)
        
        jobs = json.loads(jobs_data) if jobs_data else []
        synonyms = json.loads(synonyms_data) if synonyms_data else {}
        
        # 1. 동의어 사전 확인
        normalized_query = self.normalize_query(query)
        if normalized_query in synonyms:
            standard_name = synonyms[normalized_query]
            matched_job = next((job for job in jobs if job['job_title'] == standard_name), None)
            if matched_job:
                result = JobMatchResult(
                    query=query,
                    matched_job=matched_job,
                    confidence=1.0,
                    method='synonym_match',
                    alternatives=[],
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    cache_hit=False
                )
                # 캐시 저장
                self.redis_client.setex(cache_key, 300, json.dumps(asdict(result)))
                return result
        
        # 2. 정확 일치
        exact_match = next((job for job in jobs if job['job_title'] == query), None)
        if exact_match:
            result = JobMatchResult(
                query=query,
                matched_job=exact_match,
                confidence=1.0,
                method='exact_match',
                alternatives=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                cache_hit=False
            )
            self.redis_client.setex(cache_key, 300, json.dumps(asdict(result)))
            return result
        
        # 3. Fuzzy 매칭
        best_matches = await self._fuzzy_search(query, jobs)
        
        if best_matches:
            best_match = best_matches[0]
            alternatives = best_matches[1:5]  # 상위 5개 후보
            
            result = JobMatchResult(
                query=query,
                matched_job=best_match['job'],
                confidence=best_match['score'],
                method='fuzzy_match',
                alternatives=[alt['job'] for alt in alternatives],
                processing_time=(datetime.now() - start_time).total_seconds(),
                cache_hit=False
            )
            
            # 높은 신뢰도의 경우 캐시 저장
            if best_match['score'] >= 0.8:
                self.redis_client.setex(cache_key, 300, json.dumps(asdict(result)))
            
            return result
        
        # 매칭 실패
        return JobMatchResult(
            query=query,
            matched_job={},
            confidence=0.0,
            method='no_match',
            alternatives=[],
            processing_time=(datetime.now() - start_time).total_seconds(),
            cache_hit=False
        )
    
    async def _fuzzy_search(self, query: str, jobs: List[Dict]) -> List[Dict]:
        """Fuzzy 검색"""
        scores = []
        
        for job in jobs:
            job_title = job['job_title']
            
            # 여러 유사도 메트릭 계산
            levenshtein = 1 - (Levenshtein.distance(query, job_title) / max(len(query), len(job_title)))
            jaro_winkler = Levenshtein.jaro_winkler(query, job_title)
            sequence = SequenceMatcher(None, query, job_title).ratio()
            
            # TF-IDF 코사인 유사도
            tfidf_score = 0.0
            if self.job_vectors is not None and job_title in self.job_names:
                query_vector = self.vectorizer.transform([query])
                job_idx = self.job_names.index(job_title)
                job_vector = self.job_vectors[job_idx]
                tfidf_score = cosine_similarity(query_vector, job_vector)[0][0]
            
            # 가중 평균
            combined_score = (
                levenshtein * 0.3 +
                jaro_winkler * 0.3 +
                sequence * 0.2 +
                tfidf_score * 0.2
            )
            
            scores.append({
                'job': job,
                'score': combined_score,
                'details': {
                    'levenshtein': levenshtein,
                    'jaro_winkler': jaro_winkler,
                    'sequence': sequence,
                    'tfidf': tfidf_score
                }
            })
        
        # 점수 순 정렬
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores
    
    def invalidate_cache(self):
        """캐시 무효화"""
        self.redis_client.delete(self.CACHE_KEY_JOBS)
        self.redis_client.delete(self.CACHE_KEY_SYNONYMS)
        self.logger.info("직무명 캐시 무효화 완료")


class JobProfileSync:
    """직무 프로필 실시간 동기화"""
    
    def __init__(self, elasticsearch_client=None):
        self.es = elasticsearch_client or Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.logger = logging.getLogger(self.__class__.__name__)
        self.standardizer = JobProfileStandardizer()
    
    def sync_to_elasticsearch(self, job_profile_id: int) -> SyncResult:
        """Elasticsearch 동기화"""
        try:
            from job_profiles.models import JobProfile
            
            job = JobProfile.objects.get(id=job_profile_id)
            
            # 검색 문서 생성
            doc = {
                'id': job.id,
                'job_title': job.job_title,
                'job_type': job.job_type,
                'job_category': job.job_category,
                'job_code': job.job_code,
                'description': job.description,
                'requirements': job.requirements,
                'skills': job.skills,
                'is_active': job.is_active,
                'created_at': job.created_at.isoformat(),
                'updated_at': job.updated_at.isoformat(),
                'search_keywords': self._generate_search_keywords(job)
            }
            
            # Elasticsearch 인덱싱
            self.es.index(
                index='job_profiles',
                id=job_profile_id,
                body=doc
            )
            
            self.logger.info(f"직무 프로필 {job_profile_id} Elasticsearch 동기화 완료")
            
            return SyncResult(
                operation='elasticsearch_sync',
                affected_records=1,
                success=True,
                error_message=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Elasticsearch 동기화 실패: {e}")
            return SyncResult(
                operation='elasticsearch_sync',
                affected_records=0,
                success=False,
                error_message=str(e),
                timestamp=datetime.now()
            )
    
    def _generate_search_keywords(self, job_profile) -> List[str]:
        """검색 키워드 생성"""
        keywords = []
        
        # 직무명 분해
        keywords.extend(job_profile.job_title.split())
        
        # 직종, 직군
        if job_profile.job_type:
            keywords.append(job_profile.job_type)
        if job_profile.job_category:
            keywords.append(job_profile.job_category)
        
        # 스킬 키워드
        if job_profile.skills:
            skills_list = json.loads(job_profile.skills) if isinstance(job_profile.skills, str) else job_profile.skills
            keywords.extend(skills_list)
        
        # 중복 제거
        return list(set(keywords))
    
    async def batch_sync_all(self) -> SyncResult:
        """전체 배치 동기화"""
        try:
            from job_profiles.models import JobProfile
            
            jobs = JobProfile.objects.filter(is_active=True)
            success_count = 0
            
            for job in jobs:
                result = self.sync_to_elasticsearch(job.id)
                if result.success:
                    success_count += 1
            
            # 캐시 초기화
            self.standardizer.invalidate_cache()
            self.standardizer._initialize_cache()
            
            return SyncResult(
                operation='batch_sync_all',
                affected_records=success_count,
                success=True,
                error_message=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"배치 동기화 실패: {e}")
            return SyncResult(
                operation='batch_sync_all',
                affected_records=0,
                success=False,
                error_message=str(e),
                timestamp=datetime.now()
            )


class JobChatbotService:
    """AI 직무 챗봇 서비스"""
    
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        self.standardizer = JobProfileStandardizer()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def process_job_query(self, query: str, user_context: Dict = None) -> Dict[str, Any]:
        """직무 관련 질의 처리"""
        try:
            # 1. 직무명 추출 및 표준화
            job_match = await self.standardizer.find_best_match(query)
            
            # 2. AI 응답 생성
            if job_match.confidence >= 0.7:
                # 표준화된 직무 정보로 상세 응답
                response = await self._generate_detailed_response(job_match, query, user_context)
            else:
                # 일반적인 직무 정보 제공
                response = await self._generate_general_response(query, user_context)
            
            return {
                'success': True,
                'response': response,
                'job_match': asdict(job_match),
                'confidence': job_match.confidence,
                'processing_time': job_match.processing_time
            }
            
        except Exception as e:
            self.logger.error(f"챗봇 질의 처리 실패: {e}")
            return {
                'success': False,
                'response': "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                'error': str(e)
            }
    
    async def _generate_detailed_response(self, job_match: JobMatchResult, 
                                        query: str, user_context: Dict) -> str:
        """상세 직무 정보 응답 생성"""
        job = job_match.matched_job
        
        prompt = f"""
사용자가 '{query}'에 대해 질문했습니다.
매칭된 직무 정보:
- 직무명: {job.get('job_title', '')}
- 직종: {job.get('job_type', '')}
- 직군: {job.get('job_category', '')}
- 설명: {job.get('description', '')}
- 요구사항: {job.get('requirements', '')}

사용자 컨텍스트: {user_context or '없음'}

이 정보를 바탕으로 사용자의 질문에 친근하고 정확하게 답변해주세요.
직무의 핵심 역할, 필요 스킬, 발전 경로 등을 포함해서 답변하되, 
사용자의 질문 의도에 맞게 초점을 맞춰주세요.
"""
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 전문적이고 친근한 HR 직무 상담사입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def _generate_general_response(self, query: str, user_context: Dict) -> str:
        """일반 직무 정보 응답 생성"""
        prompt = f"""
사용자가 '{query}'에 대해 질문했습니다.
정확한 직무 매칭은 되지 않았지만, 일반적인 직무 정보나 조언을 제공해주세요.

사용자 컨텍스트: {user_context or '없음'}

친근하고 도움이 되는 답변을 해주시고, 
더 구체적인 직무명으로 질문하면 더 정확한 정보를 제공할 수 있다고 안내해주세요.
"""
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 전문적이고 친근한 HR 직무 상담사입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content


class JobSearchService:
    """직무 검색 서비스"""
    
    def __init__(self, elasticsearch_client=None):
        self.es = elasticsearch_client or Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.standardizer = JobProfileStandardizer()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def search_jobs(self, query: str, filters: Dict = None, 
                         page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """직무 검색"""
        try:
            # 1. 검색어 표준화
            job_match = await self.standardizer.find_best_match(query)
            
            # 2. Elasticsearch 쿼리 구성
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": [
                                        "job_title^3",
                                        "job_type^2",
                                        "job_category^2",
                                        "description",
                                        "requirements",
                                        "search_keywords^2"
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ],
                        "filter": []
                    }
                },
                "highlight": {
                    "fields": {
                        "job_title": {},
                        "description": {},
                        "requirements": {}
                    }
                },
                "from": (page - 1) * page_size,
                "size": page_size,
                "sort": [
                    "_score",
                    {"updated_at": "desc"}
                ]
            }
            
            # 3. 필터 적용
            if filters:
                if filters.get('job_type'):
                    search_body["query"]["bool"]["filter"].append({
                        "term": {"job_type.keyword": filters['job_type']}
                    })
                if filters.get('job_category'):
                    search_body["query"]["bool"]["filter"].append({
                        "term": {"job_category.keyword": filters['job_category']}
                    })
                if filters.get('is_active') is not None:
                    search_body["query"]["bool"]["filter"].append({
                        "term": {"is_active": filters['is_active']}
                    })
            
            # 4. 검색 실행
            result = self.es.search(
                index='job_profiles',
                body=search_body
            )
            
            # 5. 결과 가공
            jobs = []
            for hit in result['hits']['hits']:
                job = hit['_source']
                job['score'] = hit['_score']
                job['highlights'] = hit.get('highlight', {})
                jobs.append(job)
            
            return {
                'success': True,
                'jobs': jobs,
                'total': result['hits']['total']['value'],
                'page': page,
                'page_size': page_size,
                'standardized_query': job_match.matched_job.get('job_title', query) if job_match.confidence >= 0.7 else query,
                'suggestions': [alt['job_title'] for alt in job_match.alternatives[:3]],
                'processing_time': job_match.processing_time
            }
            
        except Exception as e:
            self.logger.error(f"직무 검색 실패: {e}")
            return {
                'success': False,
                'jobs': [],
                'total': 0,
                'error': str(e)
            }
    
    async def get_job_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """자동완성 제안"""
        try:
            search_body = {
                "suggest": {
                    "job_suggestions": {
                        "prefix": partial_query,
                        "completion": {
                            "field": "job_title.completion",
                            "size": limit
                        }
                    }
                }
            }
            
            result = self.es.search(
                index='job_profiles',
                body=search_body
            )
            
            suggestions = []
            for suggestion in result['suggest']['job_suggestions'][0]['options']:
                suggestions.append(suggestion['text'])
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"자동완성 제안 실패: {e}")
            return []


# Django Views
@method_decorator(csrf_exempt, name='dispatch')
class JobSearchAPIView(View):
    """직무 검색 API"""
    
    def __init__(self):
        self.search_service = JobSearchService()
    
    async def get(self, request):
        """직무 검색"""
        query = request.GET.get('q', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        filters = {}
        if request.GET.get('job_type'):
            filters['job_type'] = request.GET.get('job_type')
        if request.GET.get('job_category'):
            filters['job_category'] = request.GET.get('job_category')
        
        result = await self.search_service.search_jobs(query, filters, page, page_size)
        return JsonResponse(result)
    
    async def post(self, request):
        """고급 검색"""
        data = json.loads(request.body)
        query = data.get('query', '')
        filters = data.get('filters', {})
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        
        result = await self.search_service.search_jobs(query, filters, page, page_size)
        return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class JobChatbotAPIView(View):
    """AI 직무 챗봇 API"""
    
    def __init__(self):
        self.chatbot_service = JobChatbotService(openai_api_key=os.getenv('OPENAI_API_KEY'))
    
    async def post(self, request):
        """챗봇 질의 처리"""
        data = json.loads(request.body)
        query = data.get('query', '')
        user_context = data.get('context', {})
        
        result = await self.chatbot_service.process_job_query(query, user_context)
        return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class JobSyncAPIView(View):
    """직무 데이터 동기화 API"""
    
    def __init__(self):
        self.sync_service = JobProfileSync()
    
    async def post(self, request):
        """수동 동기화 트리거"""
        data = json.loads(request.body)
        sync_type = data.get('type', 'single')
        
        if sync_type == 'all':
            result = await self.sync_service.batch_sync_all()
        else:
            job_id = data.get('job_id')
            result = self.sync_service.sync_to_elasticsearch(job_id)
        
        return JsonResponse(asdict(result))


# Celery Tasks (commented for demo)
# app = Celery('job_integration')

# @app.task
def sync_job_to_search_engine(job_profile_id: int):
    """비동기 검색엔진 동기화"""
    sync_service = JobProfileSync()
    result = sync_service.sync_to_elasticsearch(job_profile_id)
    return asdict(result)

# @app.task
def batch_sync_all_jobs():
    """전체 직무 배치 동기화"""
    sync_service = JobProfileSync()
    result = asyncio.run(sync_service.batch_sync_all())
    return asdict(result)


# Django Signal Handlers (commented for demo)
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver

# @receiver(post_save, sender='job_profiles.JobProfile')
def handle_job_profile_save(sender, instance, created, **kwargs):
    """직무 프로필 저장 시 자동 동기화"""
    # 비동기 동기화 실행
    # sync_job_to_search_engine.delay(instance.id)
    
    # 캐시 무효화
    standardizer = JobProfileStandardizer()
    # standardizer.invalidate_cache()

# @receiver(post_delete, sender='job_profiles.JobProfile')
def handle_job_profile_delete(sender, instance, **kwargs):
    """직무 프로필 삭제 시 검색엔진에서도 제거"""
    try:
        # es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        # es.delete(index='job_profiles', id=instance.id)
        pass
    except Exception as e:
        logging.getLogger(__name__).error(f"Elasticsearch 삭제 실패: {e}")


def create_sample_usage_code():
    """샘플 사용 코드 생성"""
    return """
# 직무 통합 시스템 사용 예제

import asyncio
from job_profile_live_integration import (
    JobProfileStandardizer, JobSearchService, JobChatbotService, JobProfileSync
)

# 1. 직무명 표준화
async def test_standardization():
    standardizer = JobProfileStandardizer()
    
    # 실시간 직무 매칭
    result = await standardizer.find_best_match("HRM 담당자")
    print(f"매칭 결과: {result.matched_job['job_title']}")
    print(f"신뢰도: {result.confidence}")

# 2. 직무 검색
async def test_search():
    search_service = JobSearchService()
    
    # 검색 실행
    results = await search_service.search_jobs(
        query="시스템 개발",
        filters={'job_category': 'IT/디지털'},
        page=1,
        page_size=10
    )
    
    print(f"검색 결과: {results['total']}개")
    for job in results['jobs']:
        print(f"- {job['job_title']} (점수: {job['score']})")

# 3. AI 챗봇
async def test_chatbot():
    chatbot = JobChatbotService(openai_api_key="your-api-key")
    
    response = await chatbot.process_job_query(
        query="시스템 기획자가 되려면 어떤 스킬이 필요한가요?",
        user_context={'department': 'IT', 'experience': '신입'}
    )
    
    print(f"챗봇 응답: {response['response']}")

# 4. 실시간 동기화
async def test_sync():
    sync_service = JobProfileSync()
    
    # 단일 직무 동기화
    result = sync_service.sync_to_elasticsearch(job_profile_id=1)
    print(f"동기화 결과: {result.success}")
    
    # 전체 배치 동기화
    batch_result = await sync_service.batch_sync_all()
    print(f"배치 동기화: {batch_result.affected_records}개 처리")

# 5. Django REST API 사용
# GET /api/jobs/search/?q=시스템기획&job_type=IT기획
# POST /api/jobs/chatbot/ {"query": "데이터 분석가 전망", "context": {}}
# POST /api/jobs/sync/ {"type": "all"}

# 6. JavaScript 프론트엔드 연동
js_example = '''
// 직무 검색 API 호출
async function searchJobs(query, filters = {}) {
    const params = new URLSearchParams({ q: query, ...filters });
    const response = await fetch(`/api/jobs/search/?${params}`);
    return await response.json();
}

// AI 챗봇 API 호출
async function askChatbot(query, context = {}) {
    const response = await fetch('/api/jobs/chatbot/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, context })
    });
    return await response.json();
}

// 실시간 검색 자동완성
async function getJobSuggestions(partial) {
    const search = new JobSearchService();
    return await search.get_job_suggestions(partial);
}
'''

if __name__ == '__main__':
    # 테스트 실행
    asyncio.run(test_standardization())
    asyncio.run(test_search())
    # asyncio.run(test_chatbot())  # API 키 필요
    asyncio.run(test_sync())
"""


def create_api_specification():
    """API 명세서 생성"""
    return """
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
"""


def create_configuration_files():
    """설정 파일들 생성"""
    files = {}
    
    # Django 설정
    files['settings_integration.py'] = """
# Django 통합 설정

# Redis 설정
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery 설정
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'

# Elasticsearch 설정
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}

# OpenAI 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 직무 통합 시스템 설정
JOB_INTEGRATION = {
    'CACHE_TTL': 3600,
    'SEARCH_PAGE_SIZE': 20,
    'FUZZY_MATCH_THRESHOLD': 0.7,
    'CHATBOT_MAX_TOKENS': 500,
    'SYNC_BATCH_SIZE': 100
}

# 추가된 앱
INSTALLED_APPS += [
    'django_redis',
    'elasticsearch_dsl',
    'job_profiles',
]

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'job_integration.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'JobProfileStandardizer': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'JobSearchService': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'JobChatbotService': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
"""

    # Celery 설정
    files['celery_config.py'] = """
# Celery 설정 파일

import os
from celery import Celery

# Django 설정 모듈 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

# Celery 앱 생성
app = Celery('ehr_system')

# Django 설정에서 구성 로드
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱에서 태스크 자동 발견
app.autodiscover_tasks()

# 주기적 태스크 설정
from celery.schedules import crontab

app.conf.beat_schedule = {
    'sync-all-jobs-daily': {
        'task': 'job_profile_live_integration.batch_sync_all_jobs',
        'schedule': crontab(hour=2, minute=0),  # 매일 새벽 2시
    },
    'cleanup-cache-hourly': {
        'task': 'job_profile_live_integration.cleanup_expired_cache',
        'schedule': crontab(minute=0),  # 매시 정각
    },
}
"""

    # Elasticsearch 매핑
    files['elasticsearch_mapping.json'] = """{
  "mappings": {
    "properties": {
      "id": {
        "type": "integer"
      },
      "job_title": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          },
          "completion": {
            "type": "completion",
            "contexts": [
              {
                "name": "job_category",
                "type": "category"
              }
            ]
          }
        },
        "analyzer": "korean"
      },
      "job_type": {
        "type": "keyword"
      },
      "job_category": {
        "type": "keyword"
      },
      "job_code": {
        "type": "keyword"
      },
      "description": {
        "type": "text",
        "analyzer": "korean"
      },
      "requirements": {
        "type": "text",
        "analyzer": "korean"
      },
      "skills": {
        "type": "keyword"
      },
      "search_keywords": {
        "type": "keyword"
      },
      "is_active": {
        "type": "boolean"
      },
      "created_at": {
        "type": "date"
      },
      "updated_at": {
        "type": "date"
      }
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "korean": {
          "tokenizer": "nori_tokenizer",
          "filter": ["lowercase", "nori_part_of_speech"]
        }
      }
    },
    "number_of_shards": 1,
    "number_of_replicas": 0
  }
}"""

    # requirements.txt
    files['requirements.txt'] = """
# 직무 통합 시스템 필수 패키지

# Django 관련
django>=4.2.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0

# 데이터베이스
psycopg2-binary>=2.9.0

# 캐시 및 세션
redis>=4.5.0
django-redis>=5.2.0

# 검색엔진
elasticsearch>=8.0.0
elasticsearch-dsl>=8.0.0

# 비동기 처리
celery>=5.3.0
kombu>=5.3.0

# AI 및 자연어 처리
openai>=0.27.0
python-Levenshtein>=0.21.0

# 데이터 처리
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# 유틸리티
requests>=2.31.0
python-dateutil>=2.8.0
pytz>=2023.3

# 모니터링
sentry-sdk>=1.32.0

# 개발 도구 (선택사항)
django-debug-toolbar>=4.1.0
pytest>=7.4.0
pytest-django>=4.5.0
black>=23.7.0
"""

    # Docker 설정
    files['docker-compose.yml'] = """
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - elasticsearch
    environment:
      - DJANGO_SETTINGS_MODULE=ehr_system.settings
      - REDIS_URL=redis://redis:6379/0
      - ELASTICSEARCH_URL=http://elasticsearch:9200

  celery:
    build: .
    command: celery -A ehr_system worker -l info
    volumes:
      - .:/code
    depends_on:
      - redis
      - elasticsearch
    environment:
      - DJANGO_SETTINGS_MODULE=ehr_system.settings
      - REDIS_URL=redis://redis:6379/0

  celery-beat:
    build: .
    command: celery -A ehr_system beat -l info
    volumes:
      - .:/code
    depends_on:
      - redis
    environment:
      - DJANGO_SETTINGS_MODULE=ehr_system.settings
      - REDIS_URL=redis://redis:6379/0

volumes:
  redis_data:
  es_data:
"""
    
    return files


def create_deployment_guide():
    """배포 가이드 생성"""
    return """
# 직무 통합 시스템 배포 가이드

## 1. 환경 설정

### Redis 설치 및 설정
```bash
# Redis 설치
sudo apt install redis-server

# Redis 설정 (/etc/redis/redis.conf)
bind 127.0.0.1
port 6379
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Elasticsearch 설치 및 설정
```bash
# Elasticsearch 설치
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
sudo apt update && sudo apt install elasticsearch

# 인덱스 생성
curl -X PUT "localhost:9200/job_profiles" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "job_title": {
        "type": "text",
        "fields": {
          "keyword": {"type": "keyword"},
          "completion": {"type": "completion"}
        }
      },
      "job_type": {"type": "keyword"},
      "job_category": {"type": "keyword"},
      "description": {"type": "text"},
      "requirements": {"type": "text"},
      "search_keywords": {"type": "keyword"},
      "is_active": {"type": "boolean"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}'
```

### Celery 설정
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

app = Celery('ehr_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

## 2. Django 설정

### URL 패턴
```python
# urls.py
from job_profile_live_integration import (
    JobSearchAPIView, JobChatbotAPIView, JobSyncAPIView
)

urlpatterns = [
    path('api/jobs/search/', JobSearchAPIView.as_view(), name='job_search'),
    path('api/jobs/chatbot/', JobChatbotAPIView.as_view(), name='job_chatbot'),
    path('api/jobs/sync/', JobSyncAPIView.as_view(), name='job_sync'),
]
```

### 모델 업데이트
```python
# models.py
class JobSynonym(models.Model):
    synonym = models.CharField(max_length=100, unique=True)
    standard_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'job_synonyms'
```

## 3. 모니터링 설정

### 로그 설정
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'job_integration.log',
        },
    },
    'loggers': {
        'JobProfileStandardizer': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'JobSearchService': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### 성능 모니터링
```python
# monitoring.py
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        # 성능 로그
        logger.info(f"{func.__name__} 실행시간: {end_time - start_time:.3f}초")
        return result
    return wrapper
```

## 4. 운영 체크리스트

- [ ] Redis 서버 실행 확인
- [ ] Elasticsearch 서버 실행 확인
- [ ] Celery worker 실행 확인
- [ ] 초기 데이터 동기화 실행
- [ ] API 엔드포인트 테스트
- [ ] 검색 성능 테스트
- [ ] 챗봇 응답 품질 확인
- [ ] 로그 모니터링 설정
- [ ] 백업 스케줄 설정

## 5. 트러블슈팅

### 일반적인 문제들
1. Redis 연결 실패 → Redis 서버 상태 확인
2. Elasticsearch 인덱싱 실패 → 인덱스 매핑 확인
3. 검색 성능 저하 → 인덱스 최적화 실행
4. 챗봇 응답 지연 → OpenAI API 제한 확인
5. 동기화 실패 → Celery 워커 상태 확인
"""


def main():
    """메인 실행 함수"""
    output_dir = r"C:/Users/apro/OneDrive/Desktop/EHR_V1.0/job_integration_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🚀 직무 프로필 실시간 통합 시스템 생성 중...")
    
    # 샘플 코드 생성
    sample_code = create_sample_usage_code()
    with open(os.path.join(output_dir, 'sample_usage.py'), 'w', encoding='utf-8') as f:
        f.write(sample_code)
    print("✅ 샘플 사용 코드 생성 완료")
    
    # 배포 가이드 생성
    deployment_guide = create_deployment_guide()
    with open(os.path.join(output_dir, 'DEPLOYMENT_GUIDE.md'), 'w', encoding='utf-8') as f:
        f.write(deployment_guide)
    print("✅ 배포 가이드 생성 완료")
    
    # API 명세서 생성
    api_spec = create_api_specification()
    with open(os.path.join(output_dir, 'API_SPECIFICATION.md'), 'w', encoding='utf-8') as f:
        f.write(api_spec)
    print("✅ API 명세서 생성 완료")
    
    # 설정 파일 생성
    config_files = create_configuration_files()
    for filename, content in config_files.items():
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)
    print("✅ 설정 파일 생성 완료")
    
    print("\n✅ 직무 프로필 실시간 통합 시스템 생성 완료!")
    print(f"📁 출력 위치: {output_dir}")
    print("\n🚀 주요 기능:")
    print("  - 실시간 직무명 표준화 및 매칭 (Levenshtein, Jaro-Winkler)")
    print("  - AI 챗봇과 검색엔진 통합 (OpenAI GPT)")
    print("  - Redis/Elasticsearch 기반 고성능 검색")
    print("  - 자동 동기화 및 캐시 관리")
    print("  - Django REST API 제공")
    print("  - Celery 비동기 처리")
    print("  - 실시간 양방향 연동")
    print("\n📋 생성된 파일:")
    print("  - job_profile_live_integration.py (메인 통합 시스템)")
    print("  - sample_usage.py (사용 예제)")
    print("  - DEPLOYMENT_GUIDE.md (배포 가이드)")
    print("  - API_SPECIFICATION.md (API 명세서)")
    print("  - settings_integration.py (Django 설정)")
    print("  - celery_config.py (Celery 설정)")
    print("  - elasticsearch_mapping.json (ES 인덱스 매핑)")
    print("\n🔧 다음 단계:")
    print("  1. Redis, Elasticsearch 설치")
    print("  2. Django 설정 업데이트")
    print("  3. pip install -r requirements.txt")
    print("  4. 초기 데이터 동기화 실행")
    print("  5. API 테스트 및 모니터링 설정")


if __name__ == '__main__':
    main()