"""
AI Team Optimizer Services - AI 팀 조합 최적화 서비스
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from django.db.models import Q, Avg, Count, F
from django.utils import timezone
from django.conf import settings
from employees.models import Employee
from job_profiles.models import JobProfile
from .models import (
    Project, TeamComposition, TeamMember, SkillRequirement, 
    TeamAnalytics, OptimizationHistory, TeamTemplate
)

logger = logging.getLogger(__name__)


class TeamOptimizer:
    """AI 기반 팀 조합 최적화"""
    
    def __init__(self, project: Project):
        self.project = project
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def create_optimal_team(self, max_compositions: int = 3) -> List[TeamComposition]:
        """최적의 팀 구성 생성"""
        try:
            self.logger.info(f"프로젝트 '{self.project.name}'의 최적 팀 구성 생성 시작")
            
            # 1. 가용 인력 조회
            available_employees = self._get_available_employees()
            if not available_employees:
                self.logger.warning("가용 인력이 없습니다.")
                return []
            
            # 2. 스킬 요구사항 분석
            skill_requirements = self._analyze_skill_requirements()
            
            # 3. 여러 팀 조합 생성
            compositions = []
            for i in range(max_compositions):
                composition = self._generate_team_composition(
                    available_employees, skill_requirements, version=i+1
                )
                if composition:
                    compositions.append(composition)
            
            # 4. 순위별 정렬
            compositions.sort(key=lambda x: x.overall_score, reverse=True)
            
            self.logger.info(f"{len(compositions)}개의 팀 구성 생성 완료")
            return compositions
            
        except Exception as e:
            self.logger.error(f"팀 구성 생성 오류: {e}")
            return []
    
    def _get_available_employees(self) -> List[Employee]:
        """가용 인력 조회"""
        try:
            # 활성 직원만 조회 (퇴직자 제외)
            available = Employee.objects.filter(
                status='ACTIVE'
            ).exclude(
                resignation_date__isnull=False,
                resignation_date__lte=timezone.now().date()
            )
            
            self.logger.info(f"가용 인력: {available.count()}명")
            return list(available)
            
        except Exception as e:
            self.logger.error(f"가용 인력 조회 오류: {e}")
            return []
    
    def _analyze_skill_requirements(self) -> Dict[str, Any]:
        """스킬 요구사항 분석"""
        try:
            requirements = {}
            
            # 프로젝트의 스킬 요구사항
            skill_reqs = SkillRequirement.objects.filter(project=self.project)
            
            for req in skill_reqs:
                requirements[req.skill_name] = {
                    'proficiency': req.required_proficiency,
                    'importance': req.importance,
                    'weight': req.weight,
                    'description': req.description
                }
            
            # JSON 필드의 required_skills도 처리
            if self.project.required_skills:
                for skill in self.project.required_skills:
                    if isinstance(skill, dict):
                        skill_name = skill.get('name', skill.get('skill'))
                        if skill_name and skill_name not in requirements:
                            requirements[skill_name] = {
                                'proficiency': skill.get('level', 'INTERMEDIATE'),
                                'importance': skill.get('importance', 'REQUIRED'),
                                'weight': skill.get('weight', 1.0),
                                'description': skill.get('description', '')
                            }
                    elif isinstance(skill, str):
                        if skill not in requirements:
                            requirements[skill] = {
                                'proficiency': 'INTERMEDIATE',
                                'importance': 'REQUIRED',
                                'weight': 1.0,
                                'description': ''
                            }
            
            self.logger.info(f"스킬 요구사항 분석 완료: {len(requirements)}개 스킬")
            return requirements
            
        except Exception as e:
            self.logger.error(f"스킬 요구사항 분석 오류: {e}")
            return {}
    
    def _generate_team_composition(self, available_employees: List[Employee], 
                                 skill_requirements: Dict[str, Any], version: int = 1) -> Optional[TeamComposition]:
        """팀 구성 생성"""
        try:
            # 팀 구성 기본 정보 생성
            composition = TeamComposition.objects.create(
                project=self.project,
                name=f"AI 추천 팀 구성 #{version}",
                description=f"AI가 분석한 최적 팀 구성안 (버전 {version})",
                status='PROPOSED'
            )
            
            # 팀원 선정 알고리즘
            selected_members = self._select_team_members(
                available_employees, skill_requirements, composition
            )
            
            if not selected_members:
                composition.delete()
                return None
            
            # AI 분석 수행
            self._analyze_team_composition(composition)
            
            # 최적화 기록 저장
            self._save_optimization_history(composition, 'CREATE')
            
            return composition
            
        except Exception as e:
            self.logger.error(f"팀 구성 생성 오류: {e}")
            return None
    
    def _select_team_members(self, available_employees: List[Employee], 
                           skill_requirements: Dict[str, Any], 
                           composition: TeamComposition) -> List[TeamMember]:
        """팀원 선정 알고리즘"""
        try:
            selected_members = []
            team_size_target = (self.project.team_size_min + self.project.team_size_max) // 2
            
            # 스킬별 점수 계산
            employee_scores = {}
            for employee in available_employees:
                score = self._calculate_employee_fit_score(employee, skill_requirements)
                employee_scores[employee.id] = {
                    'employee': employee,
                    'score': score,
                    'skills': self._get_employee_skills(employee)
                }
            
            # 점수 순으로 정렬
            sorted_employees = sorted(
                employee_scores.values(), 
                key=lambda x: x['score'], 
                reverse=True
            )
            
            # 최적의 팀원 선정
            selected_count = 0
            covered_skills = set()
            
            for emp_data in sorted_employees:
                if selected_count >= team_size_target:
                    break
                
                employee = emp_data['employee']
                
                # 팀원 역할 결정
                role = self._determine_member_role(employee, selected_count, team_size_target)
                
                # 팀 멤버 생성
                member = TeamMember.objects.create(
                    team_composition=composition,
                    employee=employee,
                    role=role,
                    allocation_type='FULL_TIME',
                    allocation_percentage=100.0,
                    fit_score=emp_data['score'],
                    responsibilities=self._generate_responsibilities(employee, role, skill_requirements),
                    key_skills_utilized=emp_data['skills'][:5],  # 상위 5개 스킬
                    daily_rate=self._estimate_daily_rate(employee)
                )
                
                selected_members.append(member)
                selected_count += 1
                covered_skills.update(emp_data['skills'])
            
            self.logger.info(f"팀원 선정 완료: {len(selected_members)}명")
            return selected_members
            
        except Exception as e:
            self.logger.error(f"팀원 선정 오류: {e}")
            return []
    
    def _calculate_employee_fit_score(self, employee: Employee, 
                                    skill_requirements: Dict[str, Any]) -> float:
        """직원의 프로젝트 적합도 점수 계산"""
        try:
            total_score = 0.0
            total_weight = 0.0
            
            employee_skills = self._get_employee_skills(employee)
            
            # 스킬 매칭 점수 (60%)
            skill_score = 0.0
            skill_weight = 0.6
            
            for skill_name, requirement in skill_requirements.items():
                if skill_name.lower() in [s.lower() for s in employee_skills]:
                    # 보유 스킬에 대한 점수
                    importance_multiplier = {
                        'CRITICAL': 1.0,
                        'REQUIRED': 0.8,
                        'PREFERRED': 0.6,
                        'OPTIONAL': 0.4
                    }.get(requirement.get('importance', 'REQUIRED'), 0.8)
                    
                    skill_score += requirement.get('weight', 1.0) * importance_multiplier
                
                total_weight += requirement.get('weight', 1.0)
            
            if total_weight > 0:
                skill_score = (skill_score / total_weight) * skill_weight
                total_score += skill_score
            
            # 경험 점수 (25%)
            experience_score = min(employee.years_of_experience / 10.0, 1.0) * 0.25
            total_score += experience_score
            
            # 성과 점수 (15%) - 더미 데이터를 위한 기본값
            performance_score = getattr(employee, 'performance_rating', 0.7) * 0.15
            total_score += performance_score
            
            # 가용성 점수 (더미 데이터용 기본값)
            availability_score = 0.8  # 80% 가용성 가정
            
            return min(total_score * 10, 10.0)  # 0-10 스케일로 변환
            
        except Exception as e:
            self.logger.error(f"적합도 점수 계산 오류: {e}")
            return 0.0
    
    def _get_employee_skills(self, employee: Employee) -> List[str]:
        """직원의 스킬 목록 조회"""
        try:
            skills = []
            
            # 직무 프로필에서 스킬 추출
            if hasattr(employee, 'job_profile') and employee.job_profile:
                job_skills = getattr(employee.job_profile, 'required_skills', [])
                if isinstance(job_skills, list):
                    skills.extend(job_skills)
            
            # 부서/직책 기반 기본 스킬
            dept_skills = {
                'IT': ['Python', 'JavaScript', 'SQL', '데이터분석', '시스템개발'],
                'HR': ['인사관리', '채용', '교육훈련', '노무관리', '조직개발'],
                '마케팅': ['디지털마케팅', 'SNS관리', '광고기획', '시장조사', '브랜딩'],
                '영업': ['고객관리', '영업전략', '협상', '프레젠테이션', '시장개발'],
                '기획': ['사업기획', '전략수립', '프로젝트관리', '분석', '기획서작성']
            }.get(employee.department, [])
            
            skills.extend(dept_skills)
            
            # 중복 제거
            return list(set(skills))
            
        except Exception as e:
            self.logger.error(f"직원 스킬 조회 오류: {e}")
            return []
    
    def _determine_member_role(self, employee: Employee, current_count: int, team_size: int) -> str:
        """팀원 역할 결정"""
        try:
            if current_count == 0:
                return 'LEAD'
            elif employee.years_of_experience >= 7:
                return 'SENIOR'
            elif employee.years_of_experience >= 3:
                return 'JUNIOR'
            else:
                return 'SUPPORT'
                
        except Exception as e:
            self.logger.error(f"역할 결정 오류: {e}")
            return 'JUNIOR'
    
    def _generate_responsibilities(self, employee: Employee, role: str, 
                                 skill_requirements: Dict[str, Any]) -> List[str]:
        """담당 업무 생성"""
        try:
            base_responsibilities = {
                'LEAD': [
                    '프로젝트 전반 관리 및 일정 조율',
                    '팀원 업무 분배 및 진행 상황 관리',
                    '이해관계자와의 커뮤니케이션',
                    '기술적 의사결정 및 아키텍처 설계'
                ],
                'SENIOR': [
                    '핵심 기능 개발 및 구현',
                    '주니어 개발자 멘토링',
                    '코드 리뷰 및 품질 관리',
                    '기술적 문제 해결'
                ],
                'JUNIOR': [
                    '할당된 개발 업무 수행',
                    '단위 테스트 작성 및 실행',
                    '문서화 작업 지원',
                    '버그 수정 및 유지보수'
                ],
                'SUPPORT': [
                    '개발 환경 구축 및 관리',
                    '테스트 케이스 작성',
                    '문서 작성 및 정리',
                    '기타 지원 업무'
                ]
            }
            
            return base_responsibilities.get(role, base_responsibilities['JUNIOR'])
            
        except Exception as e:
            self.logger.error(f"담당 업무 생성 오류: {e}")
            return []
    
    def _estimate_daily_rate(self, employee: Employee) -> float:
        """일당 추정"""
        try:
            # 경력에 따른 기본 일당 (단순 추정)
            base_rate = {
                'LEAD': 300000,
                'SENIOR': 250000,
                'JUNIOR': 200000,
                'SUPPORT': 150000
            }
            
            # 경력 년수에 따른 조정
            experience_multiplier = min(1 + (employee.years_of_experience * 0.05), 2.0)
            
            # 부서별 조정
            dept_multiplier = {
                'IT': 1.2,
                'HR': 1.0,
                '마케팅': 1.1,
                '영업': 1.1,
                '기획': 1.0
            }.get(employee.department, 1.0)
            
            estimated_rate = 200000 * experience_multiplier * dept_multiplier
            return round(estimated_rate, -3)  # 천원 단위로 반올림
            
        except Exception as e:
            self.logger.error(f"일당 추정 오류: {e}")
            return 200000.0
    
    def _analyze_team_composition(self, composition: TeamComposition):
        """팀 구성 AI 분석"""
        try:
            # 호환성 점수 계산
            compatibility_score = self._calculate_compatibility_score(composition)
            
            # 효율성 점수 계산
            efficiency_score = self._calculate_efficiency_score(composition)
            
            # 리스크 점수 계산
            risk_score = self._calculate_risk_score(composition)
            
            # 종합 점수 계산
            overall_score = (compatibility_score * 0.4 + 
                           efficiency_score * 0.4 + 
                           (10 - risk_score) * 0.2)
            
            # AI 분석 결과 저장
            ai_analysis = {
                'analysis_timestamp': timezone.now().isoformat(),
                'team_strengths': self._identify_team_strengths(composition),
                'potential_risks': self._identify_potential_risks(composition),
                'skill_coverage': self._analyze_skill_coverage(composition),
                'cost_efficiency': self._analyze_cost_efficiency(composition)
            }
            
            # 최적화 제안 생성
            optimization_suggestions = self._generate_optimization_suggestions(composition)
            
            # 결과 업데이트
            composition.compatibility_score = compatibility_score
            composition.efficiency_score = efficiency_score
            composition.risk_score = risk_score
            composition.overall_score = overall_score
            composition.ai_analysis = ai_analysis
            composition.optimization_suggestions = optimization_suggestions
            composition.save()
            
            # 팀 분석 데이터 생성
            self._create_team_analytics(composition)
            
            self.logger.info(f"팀 구성 분석 완료: 종합점수 {overall_score:.2f}")
            
        except Exception as e:
            self.logger.error(f"팀 구성 분석 오류: {e}")
    
    def _calculate_compatibility_score(self, composition: TeamComposition) -> float:
        """팀 호환성 점수 계산"""
        try:
            score = 5.0  # 기본 점수
            members = composition.team_members.all()
            
            if not members:
                return score
            
            # 경력 균형도 평가
            experience_levels = [m.employee.years_of_experience for m in members]
            if len(set(experience_levels)) > 1:  # 다양한 경력 레벨
                score += 1.5
            
            # 팀 크기 적정성 평가
            team_size = len(members)
            optimal_size = (self.project.team_size_min + self.project.team_size_max) / 2
            if abs(team_size - optimal_size) <= 1:
                score += 1.0
            
            # 역할 균형도 평가
            roles = [m.role for m in members]
            if 'LEAD' in roles and len(set(roles)) > 1:
                score += 1.5
            
            return min(score, 10.0)
            
        except Exception as e:
            self.logger.error(f"호환성 점수 계산 오류: {e}")
            return 5.0
    
    def _calculate_efficiency_score(self, composition: TeamComposition) -> float:
        """팀 효율성 점수 계산"""
        try:
            score = 5.0  # 기본 점수
            members = composition.team_members.all()
            
            if not members:
                return score
            
            # 평균 적합도 점수
            avg_fit_score = members.aggregate(Avg('fit_score'))['fit_score__avg'] or 0
            score += (avg_fit_score / 10.0) * 3.0  # 최대 3점 추가
            
            # 스킬 커버리지 평가
            coverage_score = self._calculate_skill_coverage(composition)
            score += coverage_score * 2.0  # 최대 2점 추가
            
            return min(score, 10.0)
            
        except Exception as e:
            self.logger.error(f"효율성 점수 계산 오류: {e}")
            return 5.0
    
    def _calculate_risk_score(self, composition: TeamComposition) -> float:
        """팀 리스크 점수 계산 (높을수록 위험)"""
        try:
            risk_score = 0.0
            members = composition.team_members.all()
            
            if not members:
                return 5.0
            
            # 팀 크기 리스크
            if len(members) < self.project.team_size_min:
                risk_score += 3.0
            elif len(members) > self.project.team_size_max:
                risk_score += 2.0
            
            # 경력 불균형 리스크
            experience_levels = [m.employee.years_of_experience for m in members]
            if max(experience_levels) - min(experience_levels) > 10:
                risk_score += 1.5
            
            # 리더 부재 리스크
            roles = [m.role for m in members]
            if 'LEAD' not in roles:
                risk_score += 2.0
            
            return min(risk_score, 10.0)
            
        except Exception as e:
            self.logger.error(f"리스크 점수 계산 오류: {e}")
            return 5.0
    
    def _calculate_skill_coverage(self, composition: TeamComposition) -> float:
        """스킬 커버리지 계산"""
        try:
            skill_requirements = self._analyze_skill_requirements()
            if not skill_requirements:
                return 1.0
            
            covered_skills = 0
            total_skills = len(skill_requirements)
            
            # 팀 전체 보유 스킬 수집
            team_skills = set()
            for member in composition.team_members.all():
                member_skills = self._get_employee_skills(member.employee)
                team_skills.update([s.lower() for s in member_skills])
            
            # 요구 스킬과 매칭
            for skill_name in skill_requirements:
                if skill_name.lower() in team_skills:
                    covered_skills += 1
            
            return covered_skills / total_skills if total_skills > 0 else 1.0
            
        except Exception as e:
            self.logger.error(f"스킬 커버리지 계산 오류: {e}")
            return 0.5
    
    def _identify_team_strengths(self, composition: TeamComposition) -> List[str]:
        """팀 강점 식별"""
        try:
            strengths = []
            members = composition.team_members.all()
            
            # 경력 다양성
            experience_levels = [m.employee.years_of_experience for m in members]
            if len(set(experience_levels)) > 1:
                strengths.append("다양한 경력 레벨로 구성된 균형잡힌 팀")
            
            # 높은 적합도
            avg_fit_score = members.aggregate(Avg('fit_score'))['fit_score__avg'] or 0
            if avg_fit_score >= 7.0:
                strengths.append("프로젝트 요구사항에 높은 적합도를 보이는 팀")
            
            # 스킬 커버리지
            coverage = self._calculate_skill_coverage(composition)
            if coverage >= 0.8:
                strengths.append("요구 스킬의 80% 이상을 커버하는 전문성")
            
            return strengths
            
        except Exception as e:
            self.logger.error(f"팀 강점 식별 오류: {e}")
            return []
    
    def _identify_potential_risks(self, composition: TeamComposition) -> List[str]:
        """잠재적 리스크 식별"""
        try:
            risks = []
            members = composition.team_members.all()
            
            # 팀 크기 문제
            if len(members) < self.project.team_size_min:
                risks.append(f"팀 크기가 최소 요구사항({self.project.team_size_min}명)보다 작음")
            
            # 리더 부재
            roles = [m.role for m in members]
            if 'LEAD' not in roles:
                risks.append("프로젝트 리더가 지정되지 않음")
            
            # 스킬 부족
            coverage = self._calculate_skill_coverage(composition)
            if coverage < 0.6:
                risks.append("필수 스킬 커버리지가 60% 미만으로 낮음")
            
            return risks
            
        except Exception as e:
            self.logger.error(f"잠재적 리스크 식별 오류: {e}")
            return []
    
    def _analyze_skill_coverage(self, composition: TeamComposition) -> Dict[str, Any]:
        """스킬 커버리지 상세 분석"""
        try:
            skill_requirements = self._analyze_skill_requirements()
            team_skills = set()
            
            for member in composition.team_members.all():
                member_skills = self._get_employee_skills(member.employee)
                team_skills.update([s.lower() for s in member_skills])
            
            coverage_detail = {
                'total_required': len(skill_requirements),
                'covered_count': 0,
                'coverage_percentage': 0.0,
                'covered_skills': [],
                'missing_skills': []
            }
            
            for skill_name, requirement in skill_requirements.items():
                if skill_name.lower() in team_skills:
                    coverage_detail['covered_count'] += 1
                    coverage_detail['covered_skills'].append({
                        'skill': skill_name,
                        'importance': requirement.get('importance', 'REQUIRED')
                    })
                else:
                    coverage_detail['missing_skills'].append({
                        'skill': skill_name,
                        'importance': requirement.get('importance', 'REQUIRED')
                    })
            
            if coverage_detail['total_required'] > 0:
                coverage_detail['coverage_percentage'] = (
                    coverage_detail['covered_count'] / coverage_detail['total_required'] * 100
                )
            
            return coverage_detail
            
        except Exception as e:
            self.logger.error(f"스킬 커버리지 분석 오류: {e}")
            return {}
    
    def _analyze_cost_efficiency(self, composition: TeamComposition) -> Dict[str, Any]:
        """비용 효율성 분석"""
        try:
            total_cost = composition.get_total_cost()
            team_size = composition.get_team_size()
            
            efficiency_analysis = {
                'total_estimated_cost': total_cost,
                'cost_per_member': total_cost / team_size if team_size > 0 else 0,
                'budget_utilization': 0.0,
                'cost_efficiency_rating': 'MODERATE'
            }
            
            if self.project.budget:
                efficiency_analysis['budget_utilization'] = (
                    total_cost / float(self.project.budget) * 100
                )
                
                if efficiency_analysis['budget_utilization'] < 80:
                    efficiency_analysis['cost_efficiency_rating'] = 'EXCELLENT'
                elif efficiency_analysis['budget_utilization'] < 100:
                    efficiency_analysis['cost_efficiency_rating'] = 'GOOD'
                else:
                    efficiency_analysis['cost_efficiency_rating'] = 'OVER_BUDGET'
            
            return efficiency_analysis
            
        except Exception as e:
            self.logger.error(f"비용 효율성 분석 오류: {e}")
            return {}
    
    def _generate_optimization_suggestions(self, composition: TeamComposition) -> List[Dict[str, Any]]:
        """최적화 제안 생성"""
        try:
            suggestions = []
            
            # 스킬 부족 개선 제안
            skill_coverage = self._calculate_skill_coverage(composition)
            if skill_coverage < 0.8:
                suggestions.append({
                    'type': 'SKILL_IMPROVEMENT',
                    'priority': 'HIGH',
                    'title': '스킬 커버리지 개선',
                    'description': '부족한 스킬을 보유한 추가 팀원 영입 검토',
                    'action_required': True
                })
            
            # 팀 크기 조정 제안
            team_size = composition.get_team_size()
            if team_size < self.project.team_size_min:
                suggestions.append({
                    'type': 'TEAM_SIZE',
                    'priority': 'HIGH',
                    'title': '팀 크기 확대',
                    'description': f'최소 {self.project.team_size_min - team_size}명 추가 필요',
                    'action_required': True
                })
            
            # 비용 최적화 제안
            total_cost = composition.get_total_cost()
            if self.project.budget and total_cost > float(self.project.budget):
                suggestions.append({
                    'type': 'COST_OPTIMIZATION',
                    'priority': 'MEDIUM',
                    'title': '비용 최적화',
                    'description': '예산 범위 내 조정을 위한 팀 구성 재검토',
                    'action_required': True
                })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"최적화 제안 생성 오류: {e}")
            return []
    
    def _create_team_analytics(self, composition: TeamComposition):
        """팀 분석 데이터 생성"""
        try:
            analytics, created = TeamAnalytics.objects.get_or_create(
                team_composition=composition,
                defaults={
                    'diversity_score': self._calculate_diversity_score(composition),
                    'experience_balance': self._calculate_experience_balance(composition),
                    'skill_coverage': self._calculate_skill_coverage(composition),
                    'communication_score': self._estimate_communication_score(composition),
                    'success_probability': self._predict_success_probability(composition),
                    'timeline_risk': self._assess_timeline_risk(composition),
                    'budget_risk': self._assess_budget_risk(composition),
                    'quality_score': self._estimate_quality_score(composition),
                    'strengths': self._identify_team_strengths(composition),
                    'weaknesses': self._identify_team_weaknesses(composition),
                    'ai_recommendations': self._generate_ai_recommendations(composition)
                }
            )
            
            self.logger.info(f"팀 분석 데이터 {'생성' if created else '업데이트'} 완료")
            
        except Exception as e:
            self.logger.error(f"팀 분석 데이터 생성 오류: {e}")
    
    def _calculate_diversity_score(self, composition: TeamComposition) -> float:
        """다양성 점수 계산"""
        try:
            members = composition.team_members.all()
            if not members:
                return 0.0
            
            # 경력 다양성
            experience_levels = [m.employee.years_of_experience for m in members]
            experience_diversity = len(set(experience_levels)) / len(members)
            
            # 부서 다양성
            departments = [m.employee.department for m in members]
            dept_diversity = len(set(departments)) / len(members)
            
            # 역할 다양성
            roles = [m.role for m in members]
            role_diversity = len(set(roles)) / len(members)
            
            return (experience_diversity + dept_diversity + role_diversity) / 3 * 10
            
        except Exception as e:
            self.logger.error(f"다양성 점수 계산 오류: {e}")
            return 5.0
    
    def _calculate_experience_balance(self, composition: TeamComposition) -> float:
        """경험 균형도 계산"""
        try:
            members = composition.team_members.all()
            if not members:
                return 0.0
            
            experience_levels = [m.employee.years_of_experience for m in members]
            avg_experience = sum(experience_levels) / len(experience_levels)
            
            # 경험의 표준편차가 낮을수록 균형잡힌 팀
            variance = sum((x - avg_experience) ** 2 for x in experience_levels) / len(experience_levels)
            std_dev = variance ** 0.5
            
            # 표준편차를 점수로 변환 (낮을수록 높은 점수)
            balance_score = max(0, 10 - std_dev)
            return min(balance_score, 10.0)
            
        except Exception as e:
            self.logger.error(f"경험 균형도 계산 오류: {e}")
            return 5.0
    
    def _estimate_communication_score(self, composition: TeamComposition) -> float:
        """소통 점수 추정"""
        try:
            members = composition.team_members.all()
            if not members:
                return 0.0
            
            # 팀 크기에 따른 소통 복잡도 (작을수록 소통이 원활)
            team_size = len(members)
            if team_size <= 5:
                size_score = 10.0
            elif team_size <= 8:
                size_score = 8.0
            else:
                size_score = 6.0
            
            # 경력 균형도가 높을수록 소통이 원활
            balance_score = self._calculate_experience_balance(composition)
            
            return (size_score + balance_score) / 2
            
        except Exception as e:
            self.logger.error(f"소통 점수 추정 오류: {e}")
            return 5.0
    
    def _predict_success_probability(self, composition: TeamComposition) -> float:
        """성공 확률 예측"""
        try:
            # 종합 점수를 기반으로 성공 확률 예측
            overall_score = composition.overall_score
            
            # 스킬 커버리지
            skill_coverage = self._calculate_skill_coverage(composition)
            
            # 경험 균형도
            experience_balance = self._calculate_experience_balance(composition)
            
            # 가중 평균으로 성공 확률 계산
            success_prob = (
                overall_score * 0.5 +
                skill_coverage * 10 * 0.3 +
                experience_balance * 0.2
            ) / 10
            
            return min(success_prob, 1.0)
            
        except Exception as e:
            self.logger.error(f"성공 확률 예측 오류: {e}")
            return 0.5
    
    def _assess_timeline_risk(self, composition: TeamComposition) -> float:
        """일정 리스크 평가"""
        try:
            members = composition.team_members.all()
            if not members:
                return 8.0
            
            # 평균 적합도 점수가 높을수록 일정 리스크 낮음
            avg_fit_score = members.aggregate(Avg('fit_score'))['fit_score__avg'] or 0
            
            # 팀 크기 적정성
            team_size = len(members)
            optimal_size = (self.project.team_size_min + self.project.team_size_max) / 2
            size_deviation = abs(team_size - optimal_size) / optimal_size
            
            # 리스크 점수 계산 (0-10, 높을수록 위험)
            timeline_risk = 5.0 - (avg_fit_score / 2) + (size_deviation * 3)
            
            return max(0, min(timeline_risk, 10.0))
            
        except Exception as e:
            self.logger.error(f"일정 리스크 평가 오류: {e}")
            return 5.0
    
    def _assess_budget_risk(self, composition: TeamComposition) -> float:
        """예산 리스크 평가"""
        try:
            if not self.project.budget:
                return 5.0
            
            total_cost = composition.get_total_cost()
            budget_utilization = total_cost / float(self.project.budget)
            
            # 예산 사용률에 따른 리스크 점수
            if budget_utilization < 0.8:
                return 2.0  # 낮은 리스크
            elif budget_utilization < 1.0:
                return 5.0  # 중간 리스크
            else:
                return 9.0  # 높은 리스크
            
        except Exception as e:
            self.logger.error(f"예산 리스크 평가 오류: {e}")
            return 5.0
    
    def _estimate_quality_score(self, composition: TeamComposition) -> float:
        """품질 점수 추정"""
        try:
            members = composition.team_members.all()
            if not members:
                return 0.0
            
            # 평균 적합도와 경험 균형도를 기반으로 품질 점수 추정
            avg_fit_score = members.aggregate(Avg('fit_score'))['fit_score__avg'] or 0
            balance_score = self._calculate_experience_balance(composition)
            
            return (avg_fit_score + balance_score) / 2
            
        except Exception as e:
            self.logger.error(f"품질 점수 추정 오류: {e}")
            return 5.0
    
    def _identify_team_weaknesses(self, composition: TeamComposition) -> List[str]:
        """팀 약점 식별"""
        try:
            weaknesses = []
            
            # 스킬 커버리지 부족
            skill_coverage = self._calculate_skill_coverage(composition)
            if skill_coverage < 0.7:
                weaknesses.append("필수 스킬 커버리지가 부족함")
            
            # 경험 불균형
            balance_score = self._calculate_experience_balance(composition)
            if balance_score < 6.0:
                weaknesses.append("팀원 간 경험 수준의 편차가 큼")
            
            # 팀 크기 문제
            team_size = composition.get_team_size()
            if team_size < self.project.team_size_min:
                weaknesses.append("최소 팀 크기 요구사항 미달")
            
            return weaknesses
            
        except Exception as e:
            self.logger.error(f"팀 약점 식별 오류: {e}")
            return []
    
    def _generate_ai_recommendations(self, composition: TeamComposition) -> List[Dict[str, Any]]:
        """AI 추천사항 생성"""
        try:
            recommendations = []
            
            # 성공 확률이 낮은 경우
            success_prob = self._predict_success_probability(composition)
            if success_prob < 0.7:
                recommendations.append({
                    'type': 'TEAM_OPTIMIZATION',
                    'priority': 'HIGH',
                    'title': '팀 구성 최적화 필요',
                    'description': '현재 구성으로는 프로젝트 성공 확률이 낮습니다. 추가 인력 보강을 검토하세요.',
                    'expected_impact': '성공 확률 15-20% 개선'
                })
            
            # 스킬 부족 개선
            skill_coverage = self._calculate_skill_coverage(composition)
            if skill_coverage < 0.8:
                recommendations.append({
                    'type': 'SKILL_ENHANCEMENT',
                    'priority': 'MEDIUM',
                    'title': '스킬 보강',
                    'description': '부족한 스킬 영역에 대한 교육 또는 전문가 영입을 고려하세요.',
                    'expected_impact': '프로젝트 품질 향상'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"AI 추천사항 생성 오류: {e}")
            return []
    
    def _save_optimization_history(self, composition: TeamComposition, action: str):
        """최적화 기록 저장"""
        try:
            OptimizationHistory.objects.create(
                team_composition=composition,
                action=action,
                description=f"AI가 {action}한 팀 구성",
                changes_made=[{
                    'action': action,
                    'timestamp': timezone.now().isoformat(),
                    'team_size': composition.get_team_size(),
                    'total_cost': composition.get_total_cost()
                }],
                score_after=composition.overall_score,
                ai_reasoning=f"프로젝트 '{self.project.name}'에 대한 AI 기반 팀 구성 {action}",
                confidence_level=0.85
            )
            
        except Exception as e:
            self.logger.error(f"최적화 기록 저장 오류: {e}")


class TeamAnalyzer:
    """팀 분석 전문 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get_team_statistics(self) -> Dict[str, Any]:
        """팀 통계 조회"""
        try:
            total_projects = Project.objects.count()
            active_projects = Project.objects.filter(status='ACTIVE').count()
            completed_projects = Project.objects.filter(status='COMPLETED').count()
            
            total_compositions = TeamComposition.objects.count()
            approved_compositions = TeamComposition.objects.filter(status='APPROVED').count()
            
            stats = {
                'projects': {
                    'total': total_projects,
                    'active': active_projects,
                    'completed': completed_projects,
                    'completion_rate': completed_projects / total_projects * 100 if total_projects > 0 else 0
                },
                'compositions': {
                    'total': total_compositions,
                    'approved': approved_compositions,
                    'approval_rate': approved_compositions / total_compositions * 100 if total_compositions > 0 else 0
                },
                'average_scores': self._get_average_scores(),
                'top_performers': self._get_top_performing_teams()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"팀 통계 조회 오류: {e}")
            return {}
    
    def _get_average_scores(self) -> Dict[str, float]:
        """평균 점수 조회"""
        try:
            compositions = TeamComposition.objects.filter(overall_score__gt=0)
            
            if not compositions.exists():
                return {}
            
            return {
                'overall_score': compositions.aggregate(Avg('overall_score'))['overall_score__avg'] or 0,
                'compatibility_score': compositions.aggregate(Avg('compatibility_score'))['compatibility_score__avg'] or 0,
                'efficiency_score': compositions.aggregate(Avg('efficiency_score'))['efficiency_score__avg'] or 0,
                'risk_score': compositions.aggregate(Avg('risk_score'))['risk_score__avg'] or 0
            }
            
        except Exception as e:
            self.logger.error(f"평균 점수 조회 오류: {e}")
            return {}
    
    def _get_top_performing_teams(self, limit: int = 5) -> List[Dict[str, Any]]:
        """상위 성과 팀 조회"""
        try:
            top_teams = TeamComposition.objects.filter(
                overall_score__gt=0
            ).order_by('-overall_score')[:limit]
            
            results = []
            for team in top_teams:
                results.append({
                    'id': team.id,
                    'name': team.name,
                    'project': team.project.name,
                    'overall_score': team.overall_score,
                    'team_size': team.get_team_size(),
                    'status': team.status
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"상위 성과 팀 조회 오류: {e}")
            return []


class SkillMatcher:
    """스킬 매칭 전문 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def find_best_matches(self, project: Project, limit: int = 10) -> List[Dict[str, Any]]:
        """프로젝트에 가장 적합한 직원 찾기"""
        try:
            skill_requirements = self._get_project_skill_requirements(project)
            available_employees = Employee.objects.filter(status='ACTIVE')
            
            matches = []
            for employee in available_employees:
                match_score = self._calculate_match_score(employee, skill_requirements)
                if match_score > 0:
                    matches.append({
                        'employee': employee,
                        'score': match_score,
                        'matched_skills': self._get_matched_skills(employee, skill_requirements),
                        'recommendations': self._get_role_recommendations(employee, project)
                    })
            
            # 점수 순으로 정렬
            matches.sort(key=lambda x: x['score'], reverse=True)
            
            return matches[:limit]
            
        except Exception as e:
            self.logger.error(f"최적 매칭 찾기 오류: {e}")
            return []
    
    def _get_project_skill_requirements(self, project: Project) -> Dict[str, Any]:
        """프로젝트 스킬 요구사항 조회"""
        try:
            requirements = {}
            
            # SkillRequirement 모델에서 조회
            skill_reqs = SkillRequirement.objects.filter(project=project)
            for req in skill_reqs:
                requirements[req.skill_name] = {
                    'proficiency': req.required_proficiency,
                    'importance': req.importance,
                    'weight': req.weight
                }
            
            # JSON 필드의 required_skills도 추가
            if project.required_skills:
                for skill in project.required_skills:
                    if isinstance(skill, dict):
                        skill_name = skill.get('name', skill.get('skill'))
                        if skill_name and skill_name not in requirements:
                            requirements[skill_name] = skill
                    elif isinstance(skill, str) and skill not in requirements:
                        requirements[skill] = {
                            'proficiency': 'INTERMEDIATE',
                            'importance': 'REQUIRED',
                            'weight': 1.0
                        }
            
            return requirements
            
        except Exception as e:
            self.logger.error(f"프로젝트 스킬 요구사항 조회 오류: {e}")
            return {}
    
    def _calculate_match_score(self, employee: Employee, skill_requirements: Dict[str, Any]) -> float:
        """매칭 점수 계산"""
        try:
            if not skill_requirements:
                return 5.0
            
            employee_skills = self._get_employee_skills(employee)
            employee_skills_lower = [s.lower() for s in employee_skills]
            
            total_score = 0.0
            total_weight = 0.0
            
            for skill_name, requirement in skill_requirements.items():
                weight = requirement.get('weight', 1.0)
                importance = requirement.get('importance', 'REQUIRED')
                
                if skill_name.lower() in employee_skills_lower:
                    # 스킬 보유 시 점수 부여
                    importance_score = {
                        'CRITICAL': 10,
                        'REQUIRED': 8,
                        'PREFERRED': 6,
                        'OPTIONAL': 4
                    }.get(importance, 8)
                    
                    total_score += importance_score * weight
                else:
                    # 중요한 스킬 미보유 시 감점
                    if importance in ['CRITICAL', 'REQUIRED']:
                        total_score -= 2 * weight
                
                total_weight += weight
            
            if total_weight == 0:
                return 5.0
            
            # 0-10 스케일로 정규화
            normalized_score = (total_score / total_weight) + 5
            return max(0, min(normalized_score, 10))
            
        except Exception as e:
            self.logger.error(f"매칭 점수 계산 오류: {e}")
            return 0.0
    
    def _get_employee_skills(self, employee: Employee) -> List[str]:
        """직원 스킬 조회"""
        try:
            skills = []
            
            # 부서별 기본 스킬
            dept_skills = {
                'IT': ['Python', 'JavaScript', 'SQL', 'Java', 'React', 'Django', '데이터베이스', '웹개발'],
                'HR': ['인사관리', '채용', '교육훈련', '노무관리', '조직개발', '성과관리'],
                '마케팅': ['디지털마케팅', 'SNS관리', '광고기획', '시장조사', '브랜딩', 'SEO'],
                '영업': ['고객관리', '영업전략', '협상', '프레젠테이션', '시장개발', 'CRM'],
                '기획': ['사업기획', '전략수립', '프로젝트관리', '분석', '기획서작성', '컨설팅']
            }.get(employee.department, [])
            
            skills.extend(dept_skills)
            
            # 경력에 따른 추가 스킬
            if employee.years_of_experience >= 5:
                skills.extend(['리더십', '팀관리', '프로젝트관리'])
            
            if employee.years_of_experience >= 10:
                skills.extend(['전략기획', '비즈니스분석', '조직관리'])
            
            return list(set(skills))
            
        except Exception as e:
            self.logger.error(f"직원 스킬 조회 오류: {e}")
            return []
    
    def _get_matched_skills(self, employee: Employee, skill_requirements: Dict[str, Any]) -> List[str]:
        """매칭된 스킬 목록 조회"""
        try:
            employee_skills = [s.lower() for s in self._get_employee_skills(employee)]
            matched = []
            
            for skill_name in skill_requirements:
                if skill_name.lower() in employee_skills:
                    matched.append(skill_name)
            
            return matched
            
        except Exception as e:
            self.logger.error(f"매칭된 스킬 조회 오류: {e}")
            return []
    
    def _get_role_recommendations(self, employee: Employee, project: Project) -> List[str]:
        """역할 추천"""
        try:
            recommendations = []
            
            if employee.years_of_experience >= 10:
                recommendations.append('LEAD')
            elif employee.years_of_experience >= 5:
                recommendations.append('SENIOR')
            else:
                recommendations.append('JUNIOR')
            
            # 부서별 특화 역할
            if employee.department == 'IT':
                recommendations.extend(['SPECIALIST'])
            elif employee.department == '기획':
                recommendations.extend(['CONSULTANT'])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"역할 추천 오류: {e}")
            return ['JUNIOR']