"""
임베딩 기반 직무-직원 프로파일 매칭 엔진
텍스트 임베딩을 활용한 의미적 유사도 계산
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os


class EmbeddingMatcher:
    """임베딩 기반 매칭 클래스"""
    
    def __init__(self, embedding_model: str = 'tfidf'):
        """
        Args:
            embedding_model: 사용할 임베딩 모델 ('tfidf', 'word2vec', 'bert' 등)
        """
        self.embedding_model = embedding_model
        self.vectorizer = None
        self.skill_embeddings = {}
        
        if embedding_model == 'tfidf':
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=1000,
                stop_words=None  # 한국어는 별도 처리 필요
            )
    
    def create_skill_embedding(self, skills: List[str]) -> np.ndarray:
        """스킬 리스트를 임베딩 벡터로 변환"""
        if not skills:
            return np.zeros(100)  # 기본 차원
        
        # 텍스트 결합
        skill_text = ' '.join(skills)
        
        if self.embedding_model == 'tfidf':
            # TF-IDF 벡터화
            if hasattr(self.vectorizer, 'vocabulary_'):
                vector = self.vectorizer.transform([skill_text]).toarray()[0]
            else:
                # 첫 호출시 fit 필요
                vector = self.vectorizer.fit_transform([skill_text]).toarray()[0]
            return vector
        
        elif self.embedding_model == 'average':
            # 간단한 평균 임베딩 (실제로는 사전 학습된 임베딩 사용)
            embeddings = []
            for skill in skills:
                # 실제로는 Word2Vec, FastText 등 사용
                # 여기서는 더미 임베딩 생성
                skill_vec = self._get_dummy_embedding(skill)
                embeddings.append(skill_vec)
            
            return np.mean(embeddings, axis=0) if embeddings else np.zeros(100)
        
        return np.zeros(100)
    
    def _get_dummy_embedding(self, text: str, dim: int = 100) -> np.ndarray:
        """더미 임베딩 생성 (실제로는 사전 학습 모델 사용)"""
        # 텍스트 해시를 시드로 사용하여 일관된 벡터 생성
        np.random.seed(hash(text) % 2**32)
        return np.random.randn(dim)
    
    def calculate_embedding_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """두 임베딩 벡터 간의 코사인 유사도 계산"""
        if vec1.shape != vec2.shape:
            raise ValueError("벡터 차원이 일치하지 않습니다")
        
        # 영벡터 처리
        if np.all(vec1 == 0) or np.all(vec2 == 0):
            return 0.0
        
        # 코사인 유사도 계산
        similarity = cosine_similarity([vec1], [vec2])[0][0]
        
        # 0-100 스케일로 변환
        return float(max(0, similarity) * 100)
    
    def create_profile_embedding(self, profile: dict) -> Dict[str, np.ndarray]:
        """프로파일 전체를 임베딩으로 변환"""
        embeddings = {}
        
        # 스킬 임베딩
        all_skills = (
            profile.get('basic_skills', []) + 
            profile.get('applied_skills', []) +
            profile.get('skills', []) +
            profile.get('certifications', [])
        )
        embeddings['skills'] = self.create_skill_embedding(all_skills)
        
        # 역할/책임 텍스트 임베딩
        if 'role_responsibility' in profile:
            embeddings['role'] = self._get_dummy_embedding(
                profile['role_responsibility']
            )
        
        # 자격요건 텍스트 임베딩
        if 'qualification' in profile:
            embeddings['qualification'] = self._get_dummy_embedding(
                profile['qualification']
            )
        
        return embeddings
    
    def match_profiles_with_embedding(self, job_profile: dict, employee_profile: dict) -> dict:
        """임베딩 기반 프로파일 매칭"""
        
        # 프로파일 임베딩 생성
        job_embeddings = self.create_profile_embedding(job_profile)
        emp_embeddings = self.create_profile_embedding(employee_profile)
        
        # 각 요소별 유사도 계산
        similarities = {}
        
        # 스킬 유사도
        if 'skills' in job_embeddings and 'skills' in emp_embeddings:
            similarities['skills'] = self.calculate_embedding_similarity(
                job_embeddings['skills'],
                emp_embeddings['skills']
            )
        
        # 역할 적합도 (직원의 경험과 직무 요구사항 매칭)
        if 'role' in job_embeddings:
            # 직원의 경력 설명이나 프로젝트 경험 텍스트가 있다면 비교
            emp_experience = employee_profile.get('experience_description', '')
            if emp_experience:
                exp_embedding = self._get_dummy_embedding(emp_experience)
                similarities['role_fit'] = self.calculate_embedding_similarity(
                    job_embeddings['role'],
                    exp_embedding
                )
        
        # 전체 매칭 점수 계산 (가중 평균)
        weights = {
            'skills': 0.7,
            'role_fit': 0.3
        }
        
        total_score = sum(
            similarities.get(key, 0) * weight 
            for key, weight in weights.items()
        )
        
        return {
            'embedding_match_score': round(total_score, 2),
            'similarity_details': similarities,
            'method': self.embedding_model
        }


class HybridMatcher:
    """규칙 기반과 임베딩 기반을 결합한 하이브리드 매처"""
    
    def __init__(self):
        self.embedding_matcher = EmbeddingMatcher(embedding_model='average')
    
    def hybrid_match(self, job_profile: dict, employee_profile: dict, 
                    rule_weight: float = 0.6, embedding_weight: float = 0.4) -> dict:
        """
        규칙 기반과 임베딩 기반 매칭을 결합
        
        Args:
            job_profile: 직무 프로파일
            employee_profile: 직원 프로파일
            rule_weight: 규칙 기반 매칭 가중치
            embedding_weight: 임베딩 기반 매칭 가중치
        """
        
        # 규칙 기반 매칭 (기존 match_profile 함수 import 필요)
        from .matching_engine import match_profile
        rule_result = match_profile(job_profile, employee_profile)
        
        # 임베딩 기반 매칭
        embedding_result = self.embedding_matcher.match_profiles_with_embedding(
            job_profile, employee_profile
        )
        
        # 결합 점수 계산
        hybrid_score = (
            rule_result['match_score'] * rule_weight +
            embedding_result['embedding_match_score'] * embedding_weight
        )
        
        # 통합 결과
        return {
            'hybrid_match_score': round(hybrid_score, 2),
            'rule_based': {
                'score': rule_result['match_score'],
                'weight': rule_weight,
                'details': rule_result
            },
            'embedding_based': {
                'score': embedding_result['embedding_match_score'],
                'weight': embedding_weight,
                'details': embedding_result
            },
            'recommendations': self._generate_hybrid_recommendations(
                rule_result, embedding_result
            )
        }
    
    def _generate_hybrid_recommendations(self, rule_result: dict, 
                                       embedding_result: dict) -> List[str]:
        """규칙 기반과 임베딩 기반 결과를 종합한 추천사항 생성"""
        recommendations = []
        
        # 규칙 기반 추천사항
        recommendations.extend(rule_result.get('recommendations', []))
        
        # 임베딩 기반 인사이트
        if embedding_result['similarity_details'].get('skills', 0) < 70:
            recommendations.append(
                "스킬 프로파일의 의미적 유사도가 낮습니다. 관련 분야 역량 강화 필요"
            )
        
        if embedding_result['similarity_details'].get('role_fit', 0) < 60:
            recommendations.append(
                "직무 역할과의 적합도를 높이기 위해 관련 프로젝트 경험 축적 권장"
            )
        
        return list(set(recommendations))  # 중복 제거


class SkillClusterAnalyzer:
    """스킬 클러스터 분석기"""
    
    def __init__(self):
        self.embedding_matcher = EmbeddingMatcher()
        self.skill_clusters = {}
    
    def analyze_skill_clusters(self, all_job_profiles: List[dict]) -> Dict[str, List[str]]:
        """모든 직무의 스킬을 분석하여 클러스터 생성"""
        
        # 모든 스킬 수집
        all_skills = set()
        for profile in all_job_profiles:
            all_skills.update(profile.get('basic_skills', []))
            all_skills.update(profile.get('applied_skills', []))
        
        # 스킬 임베딩 생성
        skill_embeddings = {}
        for skill in all_skills:
            skill_embeddings[skill] = self.embedding_matcher._get_dummy_embedding(skill)
        
        # 간단한 클러스터링 (실제로는 K-means, DBSCAN 등 사용)
        # 여기서는 유사도 기반 그룹핑
        clusters = self._simple_clustering(skill_embeddings, threshold=0.7)
        
        return clusters
    
    def _simple_clustering(self, embeddings: Dict[str, np.ndarray], 
                          threshold: float = 0.7) -> Dict[str, List[str]]:
        """간단한 유사도 기반 클러스터링"""
        clusters = {}
        clustered = set()
        
        skills = list(embeddings.keys())
        
        for i, skill1 in enumerate(skills):
            if skill1 in clustered:
                continue
                
            cluster = [skill1]
            clustered.add(skill1)
            
            for skill2 in skills[i+1:]:
                if skill2 in clustered:
                    continue
                    
                similarity = self.embedding_matcher.calculate_embedding_similarity(
                    embeddings[skill1],
                    embeddings[skill2]
                )
                
                if similarity >= threshold * 100:
                    cluster.append(skill2)
                    clustered.add(skill2)
            
            cluster_name = f"cluster_{len(clusters)}"
            clusters[cluster_name] = cluster
        
        return clusters


# 사용 예시
if __name__ == "__main__":
    # 샘플 데이터
    job_profile = {
        "job_id": "uuid-DATA-SCIENTIST",
        "job_name": "데이터 사이언티스트",
        "role_responsibility": "빅데이터 분석 및 머신러닝 모델 개발",
        "qualification": "통계학 또는 컴퓨터공학 전공, 3년 이상 경력",
        "basic_skills": ["Python", "SQL", "통계분석", "데이터시각화"],
        "applied_skills": ["머신러닝", "딥러닝", "빅데이터처리", "A/B테스팅"]
    }
    
    employee_profile = {
        "employee_id": "e002",
        "name": "이분석",
        "career_years": 4,
        "skills": ["Python", "R", "통계분석", "데이터분석"],
        "certifications": ["데이터분석전문가"],
        "experience_description": "마케팅 데이터 분석 및 고객 세그멘테이션 프로젝트 수행"
    }
    
    # 하이브리드 매칭 실행
    print("=== 하이브리드 매칭 결과 ===\n")
    
    hybrid_matcher = HybridMatcher()
    result = hybrid_matcher.hybrid_match(job_profile, employee_profile)
    
    print(f"하이브리드 매칭 점수: {result['hybrid_match_score']}%")
    print(f"- 규칙 기반 점수: {result['rule_based']['score']}% (가중치: {result['rule_based']['weight']})")
    print(f"- 임베딩 기반 점수: {result['embedding_based']['score']}% (가중치: {result['embedding_based']['weight']})")
    
    print("\n통합 추천사항:")
    for idx, rec in enumerate(result['recommendations'], 1):
        print(f"{idx}. {rec}")