"""
AI 팀 최적화 서비스
팀 구성 최적화 및 시너지 분석
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Avg, Count, Sum, F
from django.core.cache import cache
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

from .models import (
    Project, TeamComposition, TeamMember,
    TeamAnalytics, TeamRecommendation
)
from employees.models import Employee
from ai_services.base import AIServiceBase, AIAnalyzer

logger = logging.getLogger(__name__)


class TeamOptimizationService:
    """AI 기반 팀 최적화 서비스"""
    
    def __init__(self):
        self.ai_service = AIServiceBase()
        self.analyzer = AIAnalyzer()
        self.cache_timeout = 3600
        
    def optimize_team_composition(self, project: Project) -> Dict[str, Any]:
        """프로젝트에 최적화된 팀 구성 생성"""
        
        try:
            # 1. 프로젝트 요구사항 분석
            requirements = self._analyze_project_requirements(project)
            
            # 2. 사용 가능한 인재 풀 조회
            talent_pool = self._get_available_talent_pool(project)
            
            # 3. 최적 팀 구성 알고리즘 실행
            optimal_team = self._run_optimization_algorithm(
                project, requirements, talent_pool
            )
            
            # 4. 팀 구성 생성
            team_composition = self._create_team_composition(project, optimal_team)
            
            # 5. 팀 분석 수행
            analytics = self._analyze_team_composition(team_composition)
            
            # 6. AI 추천 생성
            recommendations = self._generate_team_recommendations(
                team_composition, analytics
            )
            
            return {
                'success': True,
                'team_composition_id': team_composition.id,
                'team_size': len(optimal_team),
                'predicted_success_rate': analytics.success_probability * 100,
                'skill_coverage': analytics.skill_coverage * 100,
                'synergy_score': analytics.communication_score * 100,
                'key_recommendations': [r.recommendation for r in recommendations[:3]],
                'team_members': [
                    {
                        'name': member['employee'].name,
                        'role': member['role'],
                        'fit_score': member['fit_score']
                    }
                    for member in optimal_team
                ]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing team composition: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_project_requirements(self, project: Project) -> Dict[str, Any]:
        """프로젝트 요구사항 분석"""
        
        requirements = {
            'technical_skills': [],
            'soft_skills': [],
            'experience_level': 'mixed',
            'team_size': {'min': 3, 'max': 10, 'optimal': 5},
            'diversity_requirements': {
                'gender': True,
                'experience': True,
                'department': True
            }
        }
        
        # 프로젝트 유형별 요구사항
        if project.project_type == 'DEVELOPMENT':
            requirements['technical_skills'] = ['개발', 'DevOps', '테스트']
            requirements['soft_skills'] = ['문제해결', '협업']
        elif project.project_type == 'RESEARCH':
            requirements['technical_skills'] = ['분석', '연구', '문서화']
            requirements['soft_skills'] = ['창의성', '비판적사고']
        elif project.project_type == 'MARKETING':
            requirements['technical_skills'] = ['마케팅', '데이터분석', '디자인']
            requirements['soft_skills'] = ['커뮤니케이션', '창의성']
        
        # 복잡도에 따른 팀 규모 조정
        if project.complexity == 'HIGH':
            requirements['team_size']['optimal'] = 8
            requirements['experience_level'] = 'senior'
        elif project.complexity == 'LOW':
            requirements['team_size']['optimal'] = 4
            requirements['experience_level'] = 'mixed'
        
        return requirements
    
    def _get_available_talent_pool(self, project: Project) -> List[Employee]:
        """사용 가능한 인재 풀 조회"""
        
        # 현재 프로젝트에 참여 중이지 않은 직원들
        busy_employees = TeamMember.objects.filter(
            team_composition__project__status='ACTIVE',
            team_composition__project__end_date__gte=project.start_date
        ).values_list('employee_id', flat=True)
        
        available_employees = Employee.objects.exclude(
            id__in=busy_employees
        ).filter(
            status='ACTIVE'
        )
        
        return list(available_employees)
    
    def _run_optimization_algorithm(
        self, project: Project, requirements: Dict, talent_pool: List[Employee]
    ) -> List[Dict]:
        """팀 구성 최적화 알고리즘"""
        
        if not talent_pool:
            return []
        
        # 각 직원의 적합도 점수 계산
        scored_employees = []
        
        for employee in talent_pool:
            score = self._calculate_employee_fit_score(employee, project, requirements)
            scored_employees.append({
                'employee': employee,
                'fit_score': score['total'],
                'skill_match': score['skill_match'],
                'experience_match': score['experience_match'],
                'availability': score['availability']
            })
        
        # 점수 기준 정렬
        scored_employees.sort(key=lambda x: x['fit_score'], reverse=True)
        
        # 최적 팀 구성
        optimal_team = []
        team_size = requirements['team_size']['optimal']
        
        # 필수 역할 채우기
        roles = self._get_required_roles(project)
        
        for role in roles:
            best_candidate = self._find_best_candidate_for_role(
                scored_employees, role, optimal_team
            )
            if best_candidate:
                best_candidate['role'] = role
                optimal_team.append(best_candidate)
                scored_employees.remove(best_candidate)
        
        # 남은 자리 채우기 (시너지 고려)
        while len(optimal_team) < team_size and scored_employees:
            best_synergy_candidate = self._find_best_synergy_candidate(
                scored_employees, optimal_team
            )
            if best_synergy_candidate:
                best_synergy_candidate['role'] = 'Team Member'
                optimal_team.append(best_synergy_candidate)
                scored_employees.remove(best_synergy_candidate)
            else:
                break
        
        return optimal_team
    
    def _calculate_employee_fit_score(
        self, employee: Employee, project: Project, requirements: Dict
    ) -> Dict[str, float]:
        """직원 적합도 점수 계산"""
        
        scores = {
            'skill_match': 0,
            'experience_match': 0,
            'availability': 0,
            'performance': 0
        }
        
        # 스킬 매칭 (실제로는 스킬 DB에서 조회)
        # 여기서는 더미 데이터 사용
        import random
        scores['skill_match'] = random.uniform(0.5, 1.0)
        
        # 경력 매칭
        if requirements['experience_level'] == 'senior':
            if employee.years_of_service > 5:
                scores['experience_match'] = 0.9
            else:
                scores['experience_match'] = 0.4
        else:
            scores['experience_match'] = 0.7
        
        # 가용성 (현재 프로젝트 참여 수 기반)
        current_projects = TeamMember.objects.filter(
            employee=employee,
            team_composition__project__status='ACTIVE'
        ).count()
        
        if current_projects == 0:
            scores['availability'] = 1.0
        elif current_projects == 1:
            scores['availability'] = 0.7
        else:
            scores['availability'] = 0.3
        
        # 성과 점수 (더미)
        scores['performance'] = random.uniform(0.6, 0.95)
        
        # 가중 평균
        weights = {
            'skill_match': 0.35,
            'experience_match': 0.25,
            'availability': 0.2,
            'performance': 0.2
        }
        
        scores['total'] = sum(
            scores[key] * weights[key] for key in weights
        )
        
        return scores
    
    def _get_required_roles(self, project: Project) -> List[str]:
        """프로젝트 필수 역할 목록"""
        
        base_roles = ['Project Lead', 'Technical Lead']
        
        if project.project_type == 'DEVELOPMENT':
            base_roles.extend(['Developer', 'QA Engineer'])
        elif project.project_type == 'RESEARCH':
            base_roles.extend(['Researcher', 'Data Analyst'])
        elif project.project_type == 'MARKETING':
            base_roles.extend(['Marketing Manager', 'Creative Director'])
        
        return base_roles
    
    def _find_best_candidate_for_role(
        self, candidates: List[Dict], role: str, current_team: List[Dict]
    ) -> Optional[Dict]:
        """특정 역할에 최적 후보 찾기"""
        
        if not candidates:
            return None
        
        # 역할별 가중치 조정
        role_candidates = []
        
        for candidate in candidates:
            # 역할 적합도 계산 (더미)
            import random
            role_fit = random.uniform(0.6, 1.0)
            
            # 팀과의 시너지
            synergy = self._calculate_synergy_with_team(candidate, current_team)
            
            total_score = candidate['fit_score'] * 0.6 + role_fit * 0.3 + synergy * 0.1
            
            role_candidates.append({
                **candidate,
                'role_score': total_score
            })
        
        # 최고 점수 후보 반환
        role_candidates.sort(key=lambda x: x['role_score'], reverse=True)
        return role_candidates[0] if role_candidates else None
    
    def _find_best_synergy_candidate(
        self, candidates: List[Dict], current_team: List[Dict]
    ) -> Optional[Dict]:
        """팀 시너지를 최대화하는 후보 찾기"""
        
        if not candidates:
            return None
        
        best_candidate = None
        best_synergy = 0
        
        for candidate in candidates:
            synergy = self._calculate_synergy_with_team(candidate, current_team)
            
            if synergy > best_synergy:
                best_synergy = synergy
                best_candidate = candidate
        
        return best_candidate
    
    def _calculate_synergy_with_team(
        self, candidate: Dict, team: List[Dict]
    ) -> float:
        """팀과의 시너지 계산"""
        
        if not team:
            return 0.7  # 기본값
        
        synergy_scores = []
        
        for member in team:
            # 부서 다양성
            dept_synergy = 0.8 if candidate['employee'].department != member['employee'].department else 0.5
            
            # 경력 보완성
            exp_diff = abs(candidate['employee'].years_of_service - member['employee'].years_of_service)
            exp_synergy = min(1.0, exp_diff / 10)  # 경력 차이가 클수록 좋음
            
            # 스킬 보완성 (더미)
            import random
            skill_synergy = random.uniform(0.5, 0.9)
            
            synergy = (dept_synergy + exp_synergy + skill_synergy) / 3
            synergy_scores.append(synergy)
        
        return np.mean(synergy_scores) if synergy_scores else 0.7
    
    def _create_team_composition(
        self, project: Project, optimal_team: List[Dict]
    ) -> TeamComposition:
        """팀 구성 생성"""
        
        composition = TeamComposition.objects.create(
            project=project,
            composition_name=f"{project.name} - Optimal Team",
            status='PROPOSED',
            created_by='AI_OPTIMIZER',
            approval_status='PENDING',
            notes=f"AI가 최적화한 {len(optimal_team)}명 팀 구성"
        )
        
        # 팀 멤버 추가
        for member_data in optimal_team:
            TeamMember.objects.create(
                team_composition=composition,
                employee=member_data['employee'],
                role=member_data['role'],
                contribution_score=member_data['fit_score'],
                fit_score=member_data['fit_score'],
                synergy_score=self._calculate_synergy_with_team(
                    member_data, 
                    [m for m in optimal_team if m != member_data]
                ),
                availability_percentage=member_data.get('availability', 1.0) * 100,
                assigned_at=timezone.now()
            )
        
        return composition
    
    def _analyze_team_composition(self, composition: TeamComposition) -> TeamAnalytics:
        """팀 구성 분석"""
        
        analytics, created = TeamAnalytics.objects.get_or_create(
            team_composition=composition
        )
        
        members = composition.team_members.all()
        
        if members:
            # 스킬 커버리지
            analytics.skill_coverage = members.aggregate(avg=Avg('fit_score'))['avg'] or 0
            
            # 커뮤니케이션 점수 (시너지 평균)
            analytics.communication_score = members.aggregate(avg=Avg('synergy_score'))['avg'] or 0
            
            # 다양성 점수
            departments = members.values('employee__department').distinct().count()
            total_members = members.count()
            analytics.diversity_index = min(1.0, departments / max(total_members * 0.5, 1))
            
            # 성공 확률
            analytics.success_probability = (
                analytics.skill_coverage * 0.4 +
                analytics.communication_score * 0.3 +
                analytics.diversity_index * 0.3
            )
            
            # 위험 요소
            analytics.risk_factors = self._identify_team_risks(composition, members)
            
            # SWOT 분석
            analytics.strengths = self._identify_team_strengths(members)
            analytics.weaknesses = self._identify_team_weaknesses(members)
            analytics.opportunities = ["AI 도구 활용", "크로스 트레이닝"]
            analytics.threats = ["일정 지연 가능성", "예산 초과 위험"]
            
            analytics.save()
        
        return analytics
    
    def _identify_team_risks(
        self, composition: TeamComposition, members
    ) -> List[str]:
        """팀 위험 요소 식별"""
        
        risks = []
        
        # 팀 규모 위험
        if members.count() < 3:
            risks.append("팀 규모가 너무 작음")
        elif members.count() > 10:
            risks.append("팀 규모가 너무 큼")
        
        # 경험 불균형
        avg_experience = members.aggregate(
            avg=Avg('employee__years_of_service')
        )['avg'] or 0
        
        if avg_experience < 2:
            risks.append("팀 전체 경험 부족")
        
        # 가용성 위험
        low_availability = members.filter(availability_percentage__lt=50).count()
        if low_availability > 0:
            risks.append(f"{low_availability}명의 멤버 가용성 낮음")
        
        return risks
    
    def _identify_team_strengths(self, members) -> List[str]:
        """팀 강점 식별"""
        
        strengths = []
        
        avg_fit = members.aggregate(avg=Avg('fit_score'))['avg'] or 0
        if avg_fit > 0.75:
            strengths.append("높은 역량 적합도")
        
        avg_synergy = members.aggregate(avg=Avg('synergy_score'))['avg'] or 0
        if avg_synergy > 0.7:
            strengths.append("우수한 팀 시너지")
        
        # 다양성
        departments = members.values('employee__department').distinct().count()
        if departments >= 3:
            strengths.append("부서 간 협업 시너지")
        
        return strengths
    
    def _identify_team_weaknesses(self, members) -> List[str]:
        """팀 약점 식별"""
        
        weaknesses = []
        
        avg_fit = members.aggregate(avg=Avg('fit_score'))['avg'] or 0
        if avg_fit < 0.5:
            weaknesses.append("역량 개발 필요")
        
        # 신입 비율
        juniors = members.filter(employee__years_of_service__lt=2).count()
        if juniors > members.count() * 0.5:
            weaknesses.append("경험 많은 멘토 부족")
        
        return weaknesses
    
    def _generate_team_recommendations(
        self, composition: TeamComposition, analytics: TeamAnalytics
    ) -> List[TeamRecommendation]:
        """팀 추천사항 생성"""
        
        recommendations = []
        
        # 성공 확률 기반 추천
        if analytics.success_probability < 0.6:
            rec = TeamRecommendation.objects.create(
                team_composition=composition,
                recommendation_type='IMPROVEMENT',
                priority='HIGH',
                recommendation="팀 구성 재검토 필요",
                rationale="성공 확률이 60% 미만",
                expected_impact="성공률 20% 향상",
                implementation_steps=[
                    "핵심 역량 보강",
                    "시니어 멤버 추가",
                    "팀 빌딩 활동"
                ]
            )
            recommendations.append(rec)
        
        # 위험 요소 기반 추천
        if analytics.risk_factors:
            for risk in analytics.risk_factors[:2]:
                rec = TeamRecommendation.objects.create(
                    team_composition=composition,
                    recommendation_type='RISK_MITIGATION',
                    priority='MEDIUM',
                    recommendation=f"{risk} 대응 방안 마련",
                    rationale=risk,
                    expected_impact="위험도 감소"
                )
                recommendations.append(rec)
        
        # 강점 활용 추천
        if analytics.strengths:
            rec = TeamRecommendation.objects.create(
                team_composition=composition,
                recommendation_type='OPTIMIZATION',
                priority='LOW',
                recommendation=f"강점 활용: {', '.join(analytics.strengths[:2])}",
                rationale="팀 강점 극대화",
                expected_impact="팀 성과 10% 향상"
            )
            recommendations.append(rec)
        
        return recommendations