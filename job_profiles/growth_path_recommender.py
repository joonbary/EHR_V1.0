"""
직무 성장경로 추천 시스템
직원의 현재 프로파일과 역사적 전환 데이터를 기반으로 미래 성장 경로 추천
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import networkx as nx
from collections import defaultdict, Counter
import numpy as np


@dataclass
class GrowthStage:
    """성장 단계 정보"""
    job_id: str
    job_name: str
    required_skills: List[str]
    expected_years: float
    difficulty_score: float
    match_score: float
    skill_gap: int
    is_achievable: bool
    blockers: List[str] = None


@dataclass
class GrowthPath:
    """성장 경로 정보"""
    path_id: str
    current_job: str
    target_job: str
    stages: List[GrowthStage]
    total_years: float
    difficulty_score: float
    success_probability: float
    recommended_actions: List[str]
    historical_examples: int


class GrowthPathRecommender:
    """성장 경로 추천 엔진"""
    
    def __init__(self):
        self.transition_graph = nx.DiGraph()
        self.transition_patterns = defaultdict(list)
        self.skill_progression = defaultdict(set)
        
    def build_transition_graph(self, historical_transitions: Dict[str, List[str]]):
        """역사적 전환 데이터로 전환 그래프 구축"""
        for from_job, to_jobs in historical_transitions.items():
            job_counter = Counter(to_jobs)
            for to_job, count in job_counter.items():
                # 전환 확률 = 해당 전환 횟수 / 전체 전환 횟수
                probability = count / len(to_jobs)
                self.transition_graph.add_edge(
                    from_job, 
                    to_job, 
                    weight=probability,
                    count=count
                )
                
    def analyze_skill_progression(self, job_profiles: List[dict]):
        """직무 간 스킬 진화 패턴 분석"""
        # 직무별 스킬셋 저장
        job_skills = {}
        for profile in job_profiles:
            job_id = profile.get('job_id', profile.get('job_name'))
            all_skills = set(
                profile.get('basic_skills', []) + 
                profile.get('applied_skills', [])
            )
            job_skills[job_id] = all_skills
            
        # 전환 관계에서 스킬 증가 패턴 분석
        for edge in self.transition_graph.edges():
            from_job, to_job = edge
            if from_job in job_skills and to_job in job_skills:
                from_skills = job_skills[from_job]
                to_skills = job_skills[to_job]
                
                # 새로 추가된 스킬
                new_skills = to_skills - from_skills
                # 유지된 스킬
                maintained_skills = from_skills & to_skills
                
                self.skill_progression[(from_job, to_job)] = {
                    'new_skills': list(new_skills),
                    'maintained_skills': list(maintained_skills),
                    'skill_growth_rate': len(new_skills) / max(len(from_skills), 1)
                }
    
    def calculate_transition_difficulty(self, from_profile: dict, to_profile: dict) -> float:
        """두 직무 간 전환 난이도 계산"""
        # 스킬 갭
        from_skills = set(
            from_profile.get('skills', []) + 
            from_profile.get('basic_skills', []) + 
            from_profile.get('applied_skills', [])
        )
        to_skills = set(
            to_profile.get('basic_skills', []) + 
            to_profile.get('applied_skills', [])
        )
        
        skill_gap = len(to_skills - from_skills)
        skill_overlap = len(from_skills & to_skills)
        
        # 경력 요구사항 갭
        from_years = from_profile.get('career_years', 0)
        to_min_years = self._extract_min_years(to_profile.get('qualification', ''))
        year_gap = max(0, to_min_years - from_years)
        
        # 난이도 점수 계산 (0-100)
        difficulty = (
            (skill_gap * 10) +  # 각 스킬 갭당 10점
            (year_gap * 5) +    # 각 년도 갭당 5점
            (20 if skill_overlap < 2 else 0)  # 공통 스킬이 적으면 추가 20점
        )
        
        return min(100, difficulty)
    
    def _extract_min_years(self, qualification: str) -> int:
        """자격요건 텍스트에서 최소 경력 년수 추출"""
        import re
        # 숫자 + 년 패턴 찾기
        pattern = r'(\d+)년'
        match = re.search(pattern, qualification)
        if match:
            return int(match.group(1))
        return 0
    
    def find_reachable_jobs(
        self, 
        employee_profile: dict, 
        job_profiles: List[dict],
        max_years: int = 10,
        min_probability: float = 0.3
    ) -> List[dict]:
        """도달 가능한 직무 찾기"""
        current_job = employee_profile.get('current_job', 'Unknown')
        current_skills = set(
            employee_profile.get('skills', []) + 
            employee_profile.get('certifications', [])
        )
        current_years = employee_profile.get('career_years', 0)
        
        reachable_jobs = []
        
        for job_profile in job_profiles:
            job_id = job_profile.get('job_id', job_profile.get('job_name'))
            
            # 직접 전환 가능성 확인
            if self.transition_graph.has_edge(current_job, job_id):
                transition_prob = self.transition_graph[current_job][job_id]['weight']
            else:
                # 간접 경로 확인
                try:
                    # 최단 경로 찾기
                    path = nx.shortest_path(self.transition_graph, current_job, job_id)
                    # 경로상의 전환 확률 곱
                    transition_prob = 1.0
                    for i in range(len(path)-1):
                        if self.transition_graph.has_edge(path[i], path[i+1]):
                            transition_prob *= self.transition_graph[path[i]][path[i+1]]['weight']
                        else:
                            transition_prob = 0
                            break
                except nx.NetworkXNoPath:
                    transition_prob = 0
            
            if transition_prob >= min_probability:
                # 난이도 계산
                difficulty = self.calculate_transition_difficulty(
                    employee_profile, 
                    job_profile
                )
                
                # 예상 소요 시간
                skill_gap = len(set(job_profile.get('basic_skills', [])) - current_skills)
                expected_years = skill_gap * 0.5 + difficulty / 20  # 휴리스틱
                
                if expected_years <= max_years:
                    reachable_jobs.append({
                        'job_profile': job_profile,
                        'probability': transition_prob,
                        'difficulty': difficulty,
                        'expected_years': expected_years,
                        'skill_gap': skill_gap
                    })
        
        # 확률과 난이도 기준으로 정렬
        reachable_jobs.sort(
            key=lambda x: (x['probability'] * (100 - x['difficulty']) / 100), 
            reverse=True
        )
        
        return reachable_jobs
    
    def simulate_growth_path(
        self,
        employee_profile: dict,
        target_job_profile: dict,
        intermediate_jobs: List[dict] = None
    ) -> GrowthPath:
        """성장 경로 시뮬레이션"""
        current_job = employee_profile.get('current_job', 'Unknown')
        target_job = target_job_profile.get('job_id', target_job_profile.get('job_name'))
        
        # 경로 찾기
        try:
            if intermediate_jobs:
                # 제공된 중간 직무 사용
                path_jobs = [current_job] + [j.get('job_id', j.get('job_name')) 
                            for j in intermediate_jobs] + [target_job]
            else:
                # 최적 경로 자동 탐색
                path_jobs = nx.shortest_path(
                    self.transition_graph, 
                    current_job, 
                    target_job
                )
        except nx.NetworkXNoPath:
            # 직접 경로가 없는 경우 가상 경로 생성
            path_jobs = [current_job, target_job]
        
        # 각 단계별 성장 스테이지 생성
        stages = []
        accumulated_skills = set(employee_profile.get('skills', []))
        accumulated_years = employee_profile.get('career_years', 0)
        
        for i in range(1, len(path_jobs)):
            from_job = path_jobs[i-1]
            to_job = path_jobs[i]
            
            # 해당 직무 프로파일 찾기
            to_profile = None
            if to_job == target_job:
                to_profile = target_job_profile
            elif intermediate_jobs:
                to_profile = next((j for j in intermediate_jobs 
                                 if j.get('job_id', j.get('job_name')) == to_job), None)
            
            if not to_profile:
                # 기본 프로파일 생성
                to_profile = {
                    'job_id': to_job,
                    'job_name': to_job,
                    'basic_skills': [],
                    'applied_skills': []
                }
            
            # 필요 스킬 계산
            required_skills = set(
                to_profile.get('basic_skills', []) + 
                to_profile.get('applied_skills', [])
            )
            skill_gap = len(required_skills - accumulated_skills)
            
            # 예상 소요 시간
            if (from_job, to_job) in self.skill_progression:
                skill_growth = self.skill_progression[(from_job, to_job)]
                expected_years = max(1, skill_gap * 0.5)
            else:
                expected_years = max(1.5, skill_gap * 0.75)
            
            # 달성 가능성 평가
            difficulty = self.calculate_transition_difficulty(
                {'skills': list(accumulated_skills), 'career_years': accumulated_years},
                to_profile
            )
            
            is_achievable = difficulty < 80 and skill_gap < 10
            blockers = []
            if difficulty >= 80:
                blockers.append(f"높은 전환 난이도 ({difficulty:.0f}/100)")
            if skill_gap >= 10:
                blockers.append(f"많은 스킬 갭 ({skill_gap}개)")
            
            stage = GrowthStage(
                job_id=to_job,
                job_name=to_profile.get('job_name', to_job),
                required_skills=list(required_skills - accumulated_skills)[:5],  # 상위 5개
                expected_years=expected_years,
                difficulty_score=difficulty,
                match_score=100 - difficulty,  # 간단한 변환
                skill_gap=skill_gap,
                is_achievable=is_achievable,
                blockers=blockers if blockers else None
            )
            
            stages.append(stage)
            
            # 스킬과 경력 누적
            accumulated_skills.update(required_skills)
            accumulated_years += expected_years
        
        # 성장 경로 객체 생성
        total_years = sum(s.expected_years for s in stages)
        avg_difficulty = np.mean([s.difficulty_score for s in stages]) if stages else 0
        
        # 성공 확률 계산
        if path_jobs[0] in self.transition_graph and path_jobs[-1] in self.transition_graph:
            historical_count = sum(1 for _, to in self.transition_graph.edges(path_jobs[0]) 
                                 if to == path_jobs[-1])
        else:
            historical_count = 0
        
        success_probability = max(
            0.1,  # 최소 10%
            min(
                0.9,  # 최대 90%
                (100 - avg_difficulty) / 100 * (0.5 + 0.5 * min(1, historical_count / 10))
            )
        )
        
        # 추천 액션 생성
        recommended_actions = self._generate_growth_actions(stages, employee_profile)
        
        growth_path = GrowthPath(
            path_id=f"{current_job}_to_{target_job}",
            current_job=current_job,
            target_job=target_job,
            stages=stages,
            total_years=total_years,
            difficulty_score=avg_difficulty,
            success_probability=success_probability,
            recommended_actions=recommended_actions,
            historical_examples=historical_count
        )
        
        return growth_path
    
    def _generate_growth_actions(
        self, 
        stages: List[GrowthStage], 
        employee_profile: dict
    ) -> List[str]:
        """성장 경로에 따른 추천 액션 생성"""
        actions = []
        
        # 첫 번째 단계 스킬 갭 기반 액션
        if stages:
            first_stage = stages[0]
            if first_stage.required_skills:
                actions.append(
                    f"우선 습득 필요 스킬: {', '.join(first_stage.required_skills[:3])}"
                )
            
            if first_stage.difficulty_score > 70:
                actions.append("전환 난이도가 높으므로 단계적 준비 필요")
            
            # 경력 년수 부족시
            current_years = employee_profile.get('career_years', 0)
            if current_years < 3 and len(stages) > 2:
                actions.append("경력을 쌓으며 단계적으로 성장하는 것을 권장")
        
        # 전체 경로 기반 액션
        total_skill_gap = sum(s.skill_gap for s in stages)
        if total_skill_gap > 15:
            actions.append("장기적인 학습 계획 수립 필요")
        
        if len(stages) > 3:
            actions.append("다단계 경로이므로 중간 목표 설정 권장")
        
        # 인증/자격증 추천
        all_required_skills = set()
        for stage in stages:
            all_required_skills.update(stage.required_skills)
        
        cert_keywords = ['관리', '분석', '개발', 'AWS', 'PMP', '데이터']
        relevant_certs = [skill for skill in all_required_skills 
                         if any(keyword in skill for keyword in cert_keywords)]
        if relevant_certs:
            actions.append(f"관련 자격증 취득 고려: {', '.join(relevant_certs[:2])}")
        
        return actions

    def find_reverse_path(
        self,
        target_job_profile: dict,
        job_profiles: List[dict],
        max_depth: int = 3
    ) -> List[List[str]]:
        """목표 직무로부터 역방향 경로 탐색"""
        target_job = target_job_profile.get('job_id', target_job_profile.get('job_name'))
        
        # 목표 직무로 전환 가능한 이전 직무들 찾기
        reverse_paths = []
        
        def find_predecessors(job: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            # 해당 직무로 전환한 이전 직무들
            predecessors = [
                source for source, target in self.transition_graph.edges() 
                if target == job
            ]
            
            if not predecessors and path:
                # 경로 완성
                reverse_paths.append(path[::-1])  # 역순으로 저장
            else:
                for pred in predecessors:
                    if pred not in path:  # 순환 방지
                        find_predecessors(pred, path + [pred], depth + 1)
        
        find_predecessors(target_job, [target_job], 0)
        
        # 경로별 확률 계산하여 정렬
        path_with_probs = []
        for path in reverse_paths:
            total_prob = 1.0
            for i in range(len(path)-1):
                if self.transition_graph.has_edge(path[i], path[i+1]):
                    total_prob *= self.transition_graph[path[i]][path[i+1]]['weight']
            
            path_with_probs.append((path, total_prob))
        
        # 확률 높은 순으로 정렬
        path_with_probs.sort(key=lambda x: x[1], reverse=True)
        
        return [path for path, _ in path_with_probs[:5]]  # 상위 5개 경로


def recommend_growth_path(
    employee_profile: dict,
    job_profiles: List[dict],
    historical_transitions: Dict[str, List[str]],
    top_n: int = 3
) -> List[dict]:
    """
    직무 성장경로 추천 메인 함수
    
    Args:
        employee_profile: 직원 프로파일
        job_profiles: 전체 직무 프로파일 리스트
        historical_transitions: 과거 직무 전환 이력
        top_n: 추천할 경로 수
    
    Returns:
        추천 성장 경로 리스트
    """
    recommender = GrowthPathRecommender()
    
    # 전환 그래프 구축
    recommender.build_transition_graph(historical_transitions)
    
    # 스킬 진화 패턴 분석
    recommender.analyze_skill_progression(job_profiles)
    
    # 도달 가능한 직무 찾기
    reachable_jobs = recommender.find_reachable_jobs(
        employee_profile, 
        job_profiles,
        max_years=10,
        min_probability=0.2
    )
    
    # 상위 N개 직무에 대한 성장 경로 생성
    growth_paths = []
    for job_info in reachable_jobs[:top_n]:
        job_profile = job_info['job_profile']
        
        # 성장 경로 시뮬레이션
        growth_path = recommender.simulate_growth_path(
            employee_profile,
            job_profile
        )
        
        # 역방향 경로 탐색 (어떤 경로로 왔는지)
        reverse_paths = recommender.find_reverse_path(
            job_profile,
            job_profiles,
            max_depth=3
        )
        
        growth_paths.append({
            'target_job': job_profile.get('job_name'),
            'match_info': job_info,
            'growth_path': growth_path,
            'alternative_paths': reverse_paths[:3],  # 대안 경로
            'priority_score': (
                job_info['probability'] * 0.4 +
                (100 - job_info['difficulty']) / 100 * 0.3 +
                (10 - min(10, job_info['expected_years'])) / 10 * 0.3
            )
        })
    
    # 우선순위 점수로 정렬
    growth_paths.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return growth_paths


# 사용 예시
if __name__ == "__main__":
    # 직원 프로파일
    employee = {
        "employee_id": "e001",
        "name": "김개발",
        "current_job": "주니어 개발자",
        "career_years": 3,
        "skills": ["Python", "SQL", "Git", "Django"],
        "certifications": ["정보처리기사"]
    }
    
    # 직무 프로파일들
    job_profiles = [
        {
            "job_id": "j001",
            "job_name": "시니어 개발자",
            "basic_skills": ["Python", "Java", "SQL", "설계패턴", "코드리뷰"],
            "applied_skills": ["성능최적화", "멘토링", "기술문서작성"],
            "qualification": "개발 경력 5년 이상"
        },
        {
            "job_id": "j002",
            "job_name": "테크 리드",
            "basic_skills": ["아키텍처설계", "프로젝트관리", "기술리더십", "코드리뷰"],
            "applied_skills": ["팀관리", "기술전략", "이해관계자소통"],
            "qualification": "개발 경력 7년 이상, 리더십 경험"
        },
        {
            "job_id": "j003",
            "job_name": "데이터 엔지니어",
            "basic_skills": ["Python", "SQL", "ETL", "빅데이터처리"],
            "applied_skills": ["Spark", "Airflow", "클라우드"],
            "qualification": "데이터 처리 경력 3년 이상"
        }
    ]
    
    # 과거 전환 이력
    historical_transitions = {
        "주니어 개발자": ["시니어 개발자", "시니어 개발자", "데이터 엔지니어", "QA 엔지니어"],
        "시니어 개발자": ["테크 리드", "테크 리드", "아키텍트", "프로덕트 매니저"],
        "데이터 엔지니어": ["데이터 아키텍트", "ML 엔지니어", "데이터 팀장"]
    }
    
    # 성장 경로 추천
    recommendations = recommend_growth_path(
        employee,
        job_profiles,
        historical_transitions,
        top_n=2
    )
    
    print("=== 성장 경로 추천 결과 ===\n")
    
    for idx, rec in enumerate(recommendations, 1):
        print(f"{idx}. {rec['target_job']} 경로")
        growth_path = rec['growth_path']
        
        print(f"   총 예상 기간: {growth_path.total_years:.1f}년")
        print(f"   성공 확률: {growth_path.success_probability*100:.0f}%")
        print(f"   난이도: {growth_path.difficulty_score:.0f}/100")
        
        print("\n   단계별 성장 경로:")
        for stage_idx, stage in enumerate(growth_path.stages, 1):
            print(f"   {stage_idx}단계: {stage.job_name}")
            print(f"      - 예상 기간: {stage.expected_years:.1f}년")
            print(f"      - 필요 스킬: {', '.join(stage.required_skills[:3])}")
            if stage.blockers:
                print(f"      - 주의사항: {', '.join(stage.blockers)}")
        
        print("\n   추천 액션:")
        for action in growth_path.recommended_actions[:3]:
            print(f"   - {action}")
        
        print()