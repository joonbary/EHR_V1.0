"""
OK금융그룹 직무스킬맵 대시보드 설계·구축
Job Skill Map Dashboard for OK Financial Group

HR analytics dashboard designer + LLM skillmap expert + frontend integrator 통합 설계
- 스킬 갭 분석 (skillgap)
- 조직 필터링 (orgfilter)
- 드릴다운 가능 (drillable)
- 컨텍스트 인식 (contextaware)
- 내보내기 가능 (exportable)
"""

import json
import uuid
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.db.models import Q, Count, Avg, Max, Min, F, Case, When
from django.utils import timezone
from django.template.loader import render_to_string

# eHR System Models
from employees.models import Employee
from job_profiles.models import JobProfile, JobRole, JobType, JobCategory
from certifications.models import GrowthLevelCertification, CertificationCheckLog
from evaluations.models import ComprehensiveEvaluation, EvaluationPeriod

logger = logging.getLogger(__name__)


class SkillLevel(Enum):
    """스킬 레벨 정의"""
    NONE = 0        # 없음
    BASIC = 1       # 기초
    INTERMEDIATE = 2 # 중급
    ADVANCED = 3    # 고급
    EXPERT = 4      # 전문가


class SkillCategory(Enum):
    """스킬 카테고리"""
    TECHNICAL = "technical"         # 기술 스킬
    BUSINESS = "business"          # 비즈니스 스킬
    LEADERSHIP = "leadership"      # 리더십
    COMMUNICATION = "communication" # 커뮤니케이션
    FINANCIAL = "financial"        # 금융 전문
    COMPLIANCE = "compliance"      # 컴플라이언스
    DIGITAL = "digital"           # 디지털 역량


@dataclass
class SkillData:
    """스킬 데이터"""
    skill_name: str
    category: SkillCategory
    required_level: SkillLevel
    current_level: SkillLevel
    proficiency_score: float = 0.0
    certification_required: bool = False
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class EmployeeSkillProfile:
    """직원 스킬 프로파일"""
    employee_id: str
    name: str
    department: str
    position: str
    job_group: str
    job_type: str
    growth_level: int
    skills: List[SkillData] = field(default_factory=list)
    skill_gap_score: float = 0.0
    last_assessment: Optional[datetime] = None


@dataclass
class SkillMapMetrics:
    """스킬맵 메트릭스"""
    total_employees: int
    total_skills: int
    avg_proficiency: float
    skill_gap_rate: float
    top_skill_gaps: List[Dict[str, Any]]
    department_summary: Dict[str, Any]
    growth_level_distribution: Dict[str, int]


class SkillMapAnalytics:
    """스킬맵 분석 엔진"""
    
    def __init__(self):
        self.cache_timeout = 600  # 10분
        self.skill_categories = {
            # 금융업무 스킬
            '여신관리': SkillCategory.FINANCIAL,
            '수신업무': SkillCategory.FINANCIAL,
            '외환업무': SkillCategory.FINANCIAL,
            '투자상품': SkillCategory.FINANCIAL,
            '리스크관리': SkillCategory.FINANCIAL,
            '자산관리': SkillCategory.FINANCIAL,
            
            # IT 스킬
            'Python': SkillCategory.TECHNICAL,
            'Java': SkillCategory.TECHNICAL,
            'SQL': SkillCategory.TECHNICAL,
            '데이터분석': SkillCategory.TECHNICAL,
            '시스템분석': SkillCategory.TECHNICAL,
            'AI/ML': SkillCategory.TECHNICAL,
            
            # 비즈니스 스킬
            '프로젝트관리': SkillCategory.BUSINESS,
            '업무분석': SkillCategory.BUSINESS,
            '프로세스개선': SkillCategory.BUSINESS,
            '고객관리': SkillCategory.BUSINESS,
            
            # 리더십 스킬
            '팀관리': SkillCategory.LEADERSHIP,
            '의사결정': SkillCategory.LEADERSHIP,
            '코칭': SkillCategory.LEADERSHIP,
            '변화관리': SkillCategory.LEADERSHIP,
            
            # 컴플라이언스
            '금융법규': SkillCategory.COMPLIANCE,
            '내부통제': SkillCategory.COMPLIANCE,
            '감사': SkillCategory.COMPLIANCE,
            
            # 디지털 역량
            '디지털뱅킹': SkillCategory.DIGITAL,
            'RPA': SkillCategory.DIGITAL,
            '블록체인': SkillCategory.DIGITAL,
            '디지털마케팅': SkillCategory.DIGITAL
        }
    
    def get_organization_skill_map(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """조직 전체 스킬맵 생성"""
        cache_key = f"org_skillmap:{hash(str(filters or {}))}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # 직원 데이터 조회
        employees_query = Employee.objects.filter(
            employment_status='재직'
        ).select_related('user')
        
        # 필터 적용
        if filters:
            if filters.get('department'):
                employees_query = employees_query.filter(department=filters['department'])
            if filters.get('job_group'):
                employees_query = employees_query.filter(job_group=filters['job_group'])
            if filters.get('job_type'):
                employees_query = employees_query.filter(job_type=filters['job_type'])
            if filters.get('growth_level'):
                employees_query = employees_query.filter(growth_level=filters['growth_level'])
        
        employees = list(employees_query)
        
        # 스킬 프로파일 생성
        skill_profiles = []
        for employee in employees:
            profile = self._create_employee_skill_profile(employee)
            skill_profiles.append(profile)
        
        # 스킬맵 데이터 생성
        skillmap_data = self._generate_skillmap_matrix(skill_profiles)
        
        # 메트릭스 계산
        metrics = self._calculate_metrics(skill_profiles)
        
        result = {
            'skillmap_matrix': skillmap_data,
            'metrics': metrics,
            'employee_profiles': [
                {
                    'employee_id': p.employee_id,
                    'name': p.name,
                    'department': p.department,
                    'position': p.position,
                    'job_type': p.job_type,
                    'growth_level': p.growth_level,
                    'skill_gap_score': round(p.skill_gap_score, 2),
                    'skill_count': len(p.skills)
                }
                for p in skill_profiles
            ],
            'filters_applied': filters or {},
            'generated_at': datetime.now().isoformat()
        }
        
        cache.set(cache_key, result, self.cache_timeout)
        return result
    
    def _create_employee_skill_profile(self, employee: Employee) -> EmployeeSkillProfile:
        """직원 스킬 프로파일 생성"""
        try:
            # 직무 기술서에서 필요 스킬 추출
            job_profiles = JobProfile.objects.filter(
                job_role__job_type__name=employee.job_type,
                is_active=True
            )
            
            required_skills = set()
            for jp in job_profiles:
                required_skills.update(jp.basic_skills or [])
                required_skills.update(jp.applied_skills or [])
            
            # 직원 현재 스킬 (평가 데이터에서 추론)
            current_skills = self._infer_employee_skills(employee)
            
            # 스킬 데이터 생성
            skills = []
            total_gap = 0
            
            for skill_name in required_skills:
                category = self.skill_categories.get(skill_name, SkillCategory.BUSINESS)
                required_level = self._determine_required_level(skill_name, employee.growth_level)
                current_level = current_skills.get(skill_name, SkillLevel.NONE)
                
                # 프로피시언시 점수 계산 (0-100)
                proficiency = self._calculate_proficiency_score(current_level, required_level)
                
                skill_data = SkillData(
                    skill_name=skill_name,
                    category=category,
                    required_level=required_level,
                    current_level=current_level,
                    proficiency_score=proficiency,
                    certification_required=skill_name in ['금융법규', '내부통제', '리스크관리']
                )
                
                skills.append(skill_data)
                
                # 갭 점수 누적
                if required_level.value > current_level.value:
                    total_gap += (required_level.value - current_level.value)
            
            # 스킬 갭 점수 (0-100, 낮을수록 좋음)
            skill_gap_score = (total_gap / len(skills) / 4.0 * 100) if skills else 0
            
            return EmployeeSkillProfile(
                employee_id=str(employee.id),
                name=employee.name,
                department=employee.department,
                position=employee.position,
                job_group=employee.job_group,
                job_type=employee.job_type,
                growth_level=employee.growth_level,
                skills=skills,
                skill_gap_score=skill_gap_score,
                last_assessment=datetime.now()
            )
        except Exception as e:
            logger.error(f"Employee skill profile creation error for {employee.id}: {str(e)}")
            # 기본 프로파일 반환
            return EmployeeSkillProfile(
                employee_id=str(employee.id),
                name=employee.name,
                department=employee.department,
                position=employee.position,
                job_group=employee.job_group,
                job_type=employee.job_type,
                growth_level=employee.growth_level,
                skills=[],
                skill_gap_score=0,
                last_assessment=datetime.now()
            )
    
    def _infer_employee_skills(self, employee: Employee) -> Dict[str, SkillLevel]:
        """직원의 현재 스킬 레벨 추론"""
        skills = {}
        
        # 1. 직무 타입 기반 기본 스킬
        job_type_skills = {
            'IT개발': {'Python': SkillLevel.INTERMEDIATE, 'Java': SkillLevel.BASIC, 'SQL': SkillLevel.INTERMEDIATE},
            'IT기획': {'프로젝트관리': SkillLevel.INTERMEDIATE, '업무분석': SkillLevel.ADVANCED, '시스템분석': SkillLevel.INTERMEDIATE},
            'IT운영': {'시스템분석': SkillLevel.ADVANCED, 'SQL': SkillLevel.INTERMEDIATE, '내부통제': SkillLevel.BASIC},
            '고객지원': {'고객관리': SkillLevel.ADVANCED, '수신업무': SkillLevel.INTERMEDIATE, '여신관리': SkillLevel.BASIC},
            '기업영업': {'고객관리': SkillLevel.ADVANCED, '여신관리': SkillLevel.INTERMEDIATE, '프로젝트관리': SkillLevel.BASIC},
            '기업금융': {'여신관리': SkillLevel.ADVANCED, '리스크관리': SkillLevel.INTERMEDIATE, '자산관리': SkillLevel.INTERMEDIATE},
            '리테일금융': {'수신업무': SkillLevel.ADVANCED, '투자상품': SkillLevel.INTERMEDIATE, '고객관리': SkillLevel.INTERMEDIATE},
            '투자금융': {'투자상품': SkillLevel.ADVANCED, '자산관리': SkillLevel.ADVANCED, '리스크관리': SkillLevel.INTERMEDIATE},
            '경영관리': {'프로젝트관리': SkillLevel.INTERMEDIATE, '업무분석': SkillLevel.INTERMEDIATE, '프로세스개선': SkillLevel.BASIC}
        }
        
        base_skills = job_type_skills.get(employee.job_type, {})
        skills.update(base_skills)
        
        # 2. 성장레벨 기반 조정
        level_multiplier = {
            1: 0.6,  # Level 1: 기본 스킬의 60%
            2: 0.8,  # Level 2: 기본 스킬의 80%
            3: 1.0,  # Level 3: 기본 스킬 유지
            4: 1.2,  # Level 4: 기본 스킬의 120%
            5: 1.4   # Level 5: 기본 스킬의 140%
        }
        
        multiplier = level_multiplier.get(employee.growth_level, 1.0)
        
        # 스킬 레벨 조정
        adjusted_skills = {}
        for skill, level in skills.items():
            adjusted_value = int(level.value * multiplier)
            adjusted_value = max(0, min(4, adjusted_value))  # 0-4 범위 제한
            adjusted_skills[skill] = SkillLevel(adjusted_value)
        
        # 3. 직급 기반 리더십 스킬 추가
        if employee.position in ['MANAGER', 'DIRECTOR', 'EXECUTIVE']:
            adjusted_skills.update({
                '팀관리': SkillLevel.INTERMEDIATE,
                '의사결정': SkillLevel.INTERMEDIATE,
                '코칭': SkillLevel.BASIC
            })
        
        # 4. 부서별 공통 스킬
        if employee.department in ['FINANCE', 'SALES']:
            adjusted_skills.update({
                '금융법규': SkillLevel.BASIC,
                '내부통제': SkillLevel.BASIC
            })
        
        return adjusted_skills
    
    def _determine_required_level(self, skill_name: str, growth_level: int) -> SkillLevel:
        """성장레벨별 필요 스킬 레벨 결정"""
        # 기본 필요 레벨
        base_requirements = {
            # 금융 전문 스킬
            '여신관리': SkillLevel.INTERMEDIATE,
            '수신업무': SkillLevel.INTERMEDIATE,
            '투자상품': SkillLevel.INTERMEDIATE,
            '리스크관리': SkillLevel.ADVANCED,
            '자산관리': SkillLevel.INTERMEDIATE,
            
            # IT 스킬
            'Python': SkillLevel.INTERMEDIATE,
            'Java': SkillLevel.INTERMEDIATE,
            'SQL': SkillLevel.INTERMEDIATE,
            '데이터분석': SkillLevel.ADVANCED,
            '시스템분석': SkillLevel.ADVANCED,
            
            # 비즈니스 스킬
            '프로젝트관리': SkillLevel.INTERMEDIATE,
            '업무분석': SkillLevel.INTERMEDIATE,
            '고객관리': SkillLevel.INTERMEDIATE,
            
            # 리더십 (고성장레벨에서 필요)
            '팀관리': SkillLevel.ADVANCED,
            '의사결정': SkillLevel.ADVANCED,
            '코칭': SkillLevel.INTERMEDIATE,
            
            # 컴플라이언스
            '금융법규': SkillLevel.INTERMEDIATE,
            '내부통제': SkillLevel.INTERMEDIATE
        }
        
        base_level = base_requirements.get(skill_name, SkillLevel.BASIC)
        
        # 성장레벨별 조정
        if growth_level <= 2:
            # Level 1-2: 기본 스킬 위주
            return SkillLevel(max(1, base_level.value - 1))
        elif growth_level <= 3:
            # Level 3: 표준 스킬
            return base_level
        else:
            # Level 4-5: 고급 스킬
            return SkillLevel(min(4, base_level.value + 1))
    
    def _calculate_proficiency_score(self, current: SkillLevel, required: SkillLevel) -> float:
        """프로피시언시 점수 계산 (0-100)"""
        if required.value == 0:
            return 100.0
        
        ratio = current.value / required.value
        return min(100.0, ratio * 100.0)
    
    def _generate_skillmap_matrix(self, profiles: List[EmployeeSkillProfile]) -> Dict[str, Any]:
        """스킬맵 매트릭스 생성"""
        if not profiles:
            return {'employees': [], 'skills': [], 'matrix': []}
        
        # 모든 스킬 수집
        all_skills = set()
        for profile in profiles:
            for skill in profile.skills:
                all_skills.add(skill.skill_name)
        
        skills_list = sorted(list(all_skills))
        
        # 매트릭스 데이터 생성
        matrix_data = []
        for profile in profiles:
            employee_data = {
                'employee_id': profile.employee_id,
                'name': profile.name,
                'department': profile.department,
                'job_type': profile.job_type,
                'growth_level': profile.growth_level,
                'skills': {}
            }
            
            # 스킬별 데이터
            skill_dict = {skill.skill_name: skill for skill in profile.skills}
            
            for skill_name in skills_list:
                if skill_name in skill_dict:
                    skill = skill_dict[skill_name]
                    employee_data['skills'][skill_name] = {
                        'current_level': skill.current_level.value,
                        'required_level': skill.required_level.value,
                        'proficiency_score': skill.proficiency_score,
                        'gap': skill.required_level.value - skill.current_level.value,
                        'category': skill.category.value
                    }
                else:
                    # 스킬 없음
                    employee_data['skills'][skill_name] = {
                        'current_level': 0,
                        'required_level': 1,
                        'proficiency_score': 0.0,
                        'gap': 1,
                        'category': 'business'
                    }
            
            matrix_data.append(employee_data)
        
        # 스킬별 통계
        skill_stats = {}
        for skill_name in skills_list:
            scores = []
            gaps = []
            for emp_data in matrix_data:
                skill_data = emp_data['skills'][skill_name]
                scores.append(skill_data['proficiency_score'])
                gaps.append(skill_data['gap'])
            
            skill_stats[skill_name] = {
                'avg_proficiency': np.mean(scores),
                'avg_gap': np.mean(gaps),
                'gap_rate': sum(1 for g in gaps if g > 0) / len(gaps) * 100,
                'category': matrix_data[0]['skills'][skill_name]['category'] if matrix_data else 'business'
            }
        
        return {
            'employees': [
                {
                    'id': emp['employee_id'],
                    'name': emp['name'],
                    'department': emp['department'],
                    'job_type': emp['job_type'],
                    'growth_level': emp['growth_level']
                }
                for emp in matrix_data
            ],
            'skills': [
                {
                    'name': skill,
                    'category': stats['category'],
                    'avg_proficiency': round(stats['avg_proficiency'], 1),
                    'gap_rate': round(stats['gap_rate'], 1)
                }
                for skill, stats in skill_stats.items()
            ],
            'matrix': matrix_data,
            'heatmap_data': self._generate_heatmap_data(matrix_data, skills_list),
            'category_summary': self._generate_category_summary(skill_stats)
        }
    
    def _generate_heatmap_data(self, matrix_data: List[Dict], skills_list: List[str]) -> List[List[float]]:
        """히트맵용 데이터 생성"""
        heatmap = []
        
        for emp_data in matrix_data:
            emp_row = []
            for skill_name in skills_list:
                skill_data = emp_data['skills'][skill_name]
                # 갭이 클수록 빨간색 (높은 값), 갭이 없으면 초록색 (낮은 값)
                gap_score = skill_data['gap']
                normalized_score = min(4.0, max(0.0, gap_score)) / 4.0  # 0-1 정규화
                emp_row.append(normalized_score)
            
            heatmap.append(emp_row)
        
        return heatmap
    
    def _generate_category_summary(self, skill_stats: Dict[str, Any]) -> Dict[str, Any]:
        """카테고리별 요약 생성"""
        category_data = defaultdict(list)
        
        for skill_name, stats in skill_stats.items():
            category = stats['category']
            category_data[category].extend([
                stats['avg_proficiency'],
                stats['gap_rate']
            ])
        
        category_summary = {}
        for category, values in category_data.items():
            proficiencies = values[::2]  # 짝수 인덱스
            gap_rates = values[1::2]     # 홀수 인덱스
            
            category_summary[category] = {
                'avg_proficiency': round(np.mean(proficiencies), 1),
                'avg_gap_rate': round(np.mean(gap_rates), 1),
                'skill_count': len(proficiencies)
            }
        
        return category_summary
    
    def _calculate_metrics(self, profiles: List[EmployeeSkillProfile]) -> SkillMapMetrics:
        """메트릭스 계산"""
        if not profiles:
            return SkillMapMetrics(0, 0, 0.0, 0.0, [], {}, {})
        
        # 기본 메트릭스
        total_employees = len(profiles)
        all_skills = set()
        proficiency_scores = []
        gap_scores = []
        
        for profile in profiles:
            for skill in profile.skills:
                all_skills.add(skill.skill_name)
                proficiency_scores.append(skill.proficiency_score)
                if skill.required_level.value > skill.current_level.value:
                    gap_scores.append(1)
                else:
                    gap_scores.append(0)
        
        total_skills = len(all_skills)
        avg_proficiency = np.mean(proficiency_scores) if proficiency_scores else 0.0
        skill_gap_rate = np.mean(gap_scores) * 100 if gap_scores else 0.0
        
        # 상위 스킬 갭
        skill_gaps = defaultdict(int)
        for profile in profiles:
            for skill in profile.skills:
                if skill.required_level.value > skill.current_level.value:
                    skill_gaps[skill.skill_name] += 1
        
        top_skill_gaps = [
            {'skill': skill, 'gap_count': count, 'gap_rate': count/total_employees*100}
            for skill, count in sorted(skill_gaps.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # 부서별 요약
        dept_summary = defaultdict(lambda: {'employees': 0, 'avg_gap_score': []})
        for profile in profiles:
            dept_summary[profile.department]['employees'] += 1
            dept_summary[profile.department]['avg_gap_score'].append(profile.skill_gap_score)
        
        department_summary = {}
        for dept, data in dept_summary.items():
            department_summary[dept] = {
                'employee_count': data['employees'],
                'avg_gap_score': round(np.mean(data['avg_gap_score']), 1)
            }
        
        # 성장레벨 분포
        growth_level_dist = Counter(profile.growth_level for profile in profiles)
        
        return SkillMapMetrics(
            total_employees=total_employees,
            total_skills=total_skills,
            avg_proficiency=round(avg_proficiency, 1),
            skill_gap_rate=round(skill_gap_rate, 1),
            top_skill_gaps=top_skill_gaps,
            department_summary=department_summary,
            growth_level_distribution=dict(growth_level_dist)
        )
    
    def get_drill_down_data(self, level: str, value: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """드릴다운 데이터 조회"""
        base_filters = filters or {}
        
        if level == 'department':
            base_filters['department'] = value
        elif level == 'job_type':
            base_filters['job_type'] = value
        elif level == 'growth_level':
            base_filters['growth_level'] = int(value)
        elif level == 'skill':
            # 특정 스킬에 대한 상세 분석
            return self._get_skill_detail_analysis(value, base_filters)
        
        return self.get_organization_skill_map(base_filters)
    
    def _get_skill_detail_analysis(self, skill_name: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """특정 스킬에 대한 상세 분석"""
        org_data = self.get_organization_skill_map(filters)
        
        skill_analysis = {
            'skill_name': skill_name,
            'employees_with_skill': [],
            'proficiency_distribution': defaultdict(int),
            'gap_analysis': {
                'employees_with_gap': 0,
                'total_employees': 0,
                'avg_gap_size': 0.0
            },
            'department_breakdown': defaultdict(lambda: {'total': 0, 'with_gap': 0}),
            'recommendations': []
        }
        
        gaps = []
        
        for emp_data in org_data['skillmap_matrix']['matrix']:
            if skill_name in emp_data['skills']:
                skill_data = emp_data['skills'][skill_name]
                
                skill_analysis['employees_with_skill'].append({
                    'employee_id': emp_data['employee_id'],
                    'name': emp_data['name'],
                    'department': emp_data['department'],
                    'current_level': skill_data['current_level'],
                    'required_level': skill_data['required_level'],
                    'gap': skill_data['gap'],
                    'proficiency_score': skill_data['proficiency_score']
                })
                
                # 프로피시언시 분포
                level_name = ['없음', '기초', '중급', '고급', '전문가'][skill_data['current_level']]
                skill_analysis['proficiency_distribution'][level_name] += 1
                
                # 갭 분석
                if skill_data['gap'] > 0:
                    skill_analysis['gap_analysis']['employees_with_gap'] += 1
                    gaps.append(skill_data['gap'])
                
                skill_analysis['gap_analysis']['total_employees'] += 1
                
                # 부서별 분석
                dept = emp_data['department']
                skill_analysis['department_breakdown'][dept]['total'] += 1
                if skill_data['gap'] > 0:
                    skill_analysis['department_breakdown'][dept]['with_gap'] += 1
        
        # 갭 평균 계산
        if gaps:
            skill_analysis['gap_analysis']['avg_gap_size'] = round(np.mean(gaps), 2)
        
        # 추천사항 생성
        gap_rate = (skill_analysis['gap_analysis']['employees_with_gap'] / 
                   skill_analysis['gap_analysis']['total_employees'] * 100)
        
        if gap_rate > 50:
            skill_analysis['recommendations'].append(f"{skill_name} 집중 교육 프로그램 필요")
        if gap_rate > 30:
            skill_analysis['recommendations'].append(f"{skill_name} 관련 자격증 취득 지원")
        if len(skill_analysis['employees_with_skill']) < 5:
            skill_analysis['recommendations'].append(f"{skill_name} 전문가 채용 고려")
        
        return skill_analysis
    
    def calcSkillScoreForDeptSkill(self, department: str, employees: List[Employee], 
                                    skill_requirements: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        부서별 스킬 점수 계산 함수 (개선 버전)
        
        Args:
            department: 부서명
            employees: 직원 리스트 (Employee 모델 인스턴스)
            skill_requirements: 스킬별 요구사항 (None일 경우 자동 생성)
            
        Returns:
            부서 스킬 점수 분석 결과
        """
        try:
            logger.info(f"=== 부서 '{department}' 스킬 점수 계산 시작 ===")
            
            if not employees:
                logger.warning(f"부서 '{department}'에 직원이 없습니다.")
                return {
                    'status': 'warning',
                    'department': department,
                    'message': '직원 데이터가 없습니다.',
                    'data': None
                }
            
            # 스킬 요구사항이 없으면 자동 생성
            if skill_requirements is None:
                skill_requirements = self._generate_skill_requirements()
            
            # 부서 프로파일 생성
            skill_profiles = []
            for employee in employees:
                profile = self._create_employee_skill_profile(employee)
                skill_profiles.append(profile)
            
            # 스킬별 집계 데이터
            skill_aggregates = defaultdict(lambda: {
                'current_levels': [],
                'required_levels': [],
                'proficiencies': [],
                'gaps': [],
                'category': 'business'
            })
            
            # 각 직원의 스킬 데이터 수집
            for profile in skill_profiles:
                for skill in profile.skills:
                    skill_name = skill.skill_name
                    skill_aggregates[skill_name]['current_levels'].append(skill.current_level.value)
                    skill_aggregates[skill_name]['required_levels'].append(skill.required_level.value)
                    skill_aggregates[skill_name]['proficiencies'].append(skill.proficiency_score)
                    skill_aggregates[skill_name]['gaps'].append(
                        (skill.required_level.value - skill.current_level.value) / 4.0 * 100
                    )
                    skill_aggregates[skill_name]['category'] = skill.category.value
            
            # 스킬별 평균 계산
            skill_scores = []
            for skill_name, aggregates in skill_aggregates.items():
                if not aggregates['current_levels']:
                    continue
                    
                skill_score = {
                    'skill_name': skill_name,
                    'category': aggregates['category'],
                    'current_level': round(np.mean(aggregates['current_levels']), 1),
                    'required_level': round(np.mean(aggregates['required_levels']), 1),
                    'proficiency_score': round(np.mean(aggregates['proficiencies']), 2),
                    'gap_score': round(np.mean(aggregates['gaps']), 2),
                    'weight': skill_requirements.get(skill_name, {}).get('weight', 1.0)
                }
                skill_scores.append(skill_score)
                logger.debug(f"스킬 '{skill_name}' 계산 완료: {skill_score}")
            
            # 부서 평균 계산
            if skill_scores:
                avg_proficiency = np.mean([s['proficiency_score'] for s in skill_scores])
                avg_gap = np.mean([s['gap_score'] for s in skill_scores])
            else:
                avg_proficiency = 0.0
                avg_gap = 0.0
            
            # 상위 갭 스킬 식별
            sorted_skills = sorted(skill_scores, key=lambda x: x['gap_score'], reverse=True)
            top_gaps = sorted_skills[:5]
            
            # 추천사항 생성
            recommendations = self._generate_department_recommendations(
                department, avg_gap, skill_scores
            )
            
            # 결과 생성
            result = {
                'status': 'success',
                'department': department,
                'summary': {
                    'total_employees': len(employees),
                    'total_skills': len(skill_scores),
                    'avg_proficiency': round(avg_proficiency, 2),
                    'avg_gap': round(avg_gap, 2)
                },
                'skill_scores': skill_scores,
                'top_gaps': top_gaps,
                'recommendations': recommendations
            }
            
            logger.info(f"부서 '{department}' 계산 완료: {result['summary']}")
            return result
            
        except Exception as e:
            logger.error(f"calcSkillScoreForDeptSkill 오류: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'status': 'error',
                'department': department,
                'message': f'계산 중 오류 발생: {str(e)}',
                'data': None
            }
    
    def _generate_skill_requirements(self) -> Dict[str, Dict[str, Any]]:
        """기본 스킬 요구사항 생성"""
        requirements = {}
        
        # 기술 스킬
        for skill in ['Python', 'Java', 'SQL', '데이터분석', '시스템분석', 'AI/ML']:
            requirements[skill] = {
                'required_level': 3,
                'category': 'technical',
                'weight': 1.2
            }
        
        # 비즈니스 스킬
        for skill in ['프로젝트관리', '업무분석', '프로세스개선', '고객관리']:
            requirements[skill] = {
                'required_level': 2,
                'category': 'business',
                'weight': 1.0
            }
        
        # 금융 스킬
        for skill in ['여신관리', '수신업무', '리스크관리', '자산관리']:
            requirements[skill] = {
                'required_level': 3,
                'category': 'financial',
                'weight': 1.1
            }
        
        return requirements
    
    def _generate_department_recommendations(self, department: str, avg_gap: float, 
                                           skill_scores: List[Dict[str, Any]]) -> List[str]:
        """부서별 추천사항 생성"""
        recommendations = []
        
        if avg_gap > 50:
            recommendations.append(f"{department} 전반적인 스킬 향상 프로그램이 시급히 필요합니다.")
        elif avg_gap > 30:
            recommendations.append(f"{department} 중점 스킬 교육 계획 수립이 필요합니다.")
        
        # 카테고리별 분석
        category_gaps = defaultdict(list)
        for skill in skill_scores:
            if skill['gap_score'] > 30:
                category_gaps[skill['category']].append(skill)
        
        for category, skills in category_gaps.items():
            if len(skills) >= 2:
                recommendations.append(f"{category} 영역 집중 교육이 필요합니다.")
        
        # 긴급 스킬
        urgent_skills = [s for s in skill_scores if s['gap_score'] > 60]
        if urgent_skills:
            skill_names = ', '.join([s['skill_name'] for s in urgent_skills[:3]])
            recommendations.append(f"긴급 교육 필요: {skill_names}")
        
        return recommendations[:5]
    
    def export_skill_data(self, format: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """스킬 데이터 내보내기"""
        data = self.get_organization_skill_map(filters)
        
        if format.lower() == 'excel':
            return self._export_to_excel(data)
        elif format.lower() == 'csv':
            return self._export_to_csv(data)
        elif format.lower() == 'pdf':
            return self._export_to_pdf(data)
        else:
            return {'error': 'Unsupported format'}
    
    def _export_to_excel(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Excel 형식으로 내보내기"""
        # 실제 구현에서는 pandas를 사용하여 Excel 파일 생성
        export_data = {
            'format': 'excel',
            'filename': f'skillmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            'sheets': {
                'overview': data['metrics'],
                'skillmap': data['skillmap_matrix']['matrix'],
                'skill_summary': data['skillmap_matrix']['skills']
            }
        }
        return export_data
    
    def _export_to_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """CSV 형식으로 내보내기"""
        return {
            'format': 'csv',
            'filename': f'skillmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'data': data['skillmap_matrix']['matrix']
        }
    
    def _export_to_pdf(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """PDF 보고서 생성"""
        return {
            'format': 'pdf',
            'filename': f'skillmap_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            'report_data': {
                'title': 'OK금융그룹 직무스킬맵 분석 보고서',
                'generated_at': datetime.now().isoformat(),
                'summary': data['metrics'],
                'top_gaps': data['metrics'].top_skill_gaps,
                'department_analysis': data['metrics'].department_summary
            }
        }


# Django Views

@method_decorator(login_required, name='dispatch')
class SkillMapDashboardView(TemplateView):
    """스킬맵 대시보드 메인 화면"""
    template_name = 'skillmap/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 기본 필터 옵션
        context['departments'] = Employee.DEPARTMENT_CHOICES
        context['job_groups'] = [('PL', 'PL직군'), ('Non-PL', 'Non-PL직군')]
        context['job_types'] = [
            ('IT기획', 'IT기획'), ('IT개발', 'IT개발'), ('IT운영', 'IT운영'),
            ('경영관리', '경영관리'), ('기업영업', '기업영업'), ('기업금융', '기업금융'),
            ('리테일금융', '리테일금융'), ('투자금융', '투자금융'), ('고객지원', '고객지원')
        ]
        context['growth_levels'] = [(i, f'Level {i}') for i in range(1, 6)]
        
        return context


@method_decorator(login_required, name='dispatch')
class SkillMapAPI(View):
    """스킬맵 데이터 API"""
    
    def __init__(self):
        super().__init__()
        self.analytics = SkillMapAnalytics()
    
    def get(self, request):
        """
        GET /api/skillmap/
        
        Parameters:
            - department: 부서 필터
            - job_group: 직군 필터 (PL/Non-PL)
            - job_type: 직종 필터
            - growth_level: 성장레벨 필터
            - format: 응답 형식 (json, heatmap, summary)
        """
        try:
            # 필터 파라미터 추출
            filters = {}
            for param in ['department', 'job_group', 'job_type', 'growth_level']:
                value = request.GET.get(param)
                if value:
                    if param == 'growth_level':
                        filters[param] = int(value)
                    else:
                        filters[param] = value
            
            # 응답 형식
            response_format = request.GET.get('format', 'json')
            
            # 데이터 조회
            skillmap_data = self.analytics.get_organization_skill_map(filters)
            
            # 형식별 응답
            if response_format == 'heatmap':
                return JsonResponse({
                    'status': 'success',
                    'heatmap_data': skillmap_data['skillmap_matrix']['heatmap_data'],
                    'employees': skillmap_data['skillmap_matrix']['employees'],
                    'skills': skillmap_data['skillmap_matrix']['skills']
                })
            elif response_format == 'summary':
                return JsonResponse({
                    'status': 'success',
                    'metrics': {
                        'total_employees': skillmap_data['metrics'].total_employees,
                        'total_skills': skillmap_data['metrics'].total_skills,
                        'avg_proficiency': skillmap_data['metrics'].avg_proficiency,
                        'skill_gap_rate': skillmap_data['metrics'].skill_gap_rate,
                        'top_skill_gaps': skillmap_data['metrics'].top_skill_gaps[:5],
                        'department_summary': skillmap_data['metrics'].department_summary
                    }
                })
            else:
                return JsonResponse({
                    'status': 'success',
                    'data': skillmap_data
                })
        
        except Exception as e:
            logger.error(f"SkillMap API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '스킬맵 데이터 조회 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class SkillMapDrillDownAPI(View):
    """스킬맵 드릴다운 API"""
    
    def __init__(self):
        super().__init__()
        self.analytics = SkillMapAnalytics()
    
    def get(self, request, level, value):
        """
        GET /api/skillmap/drilldown/<level>/<value>/
        
        Parameters:
            - level: department, job_type, growth_level, skill
            - value: 해당 레벨의 값
        """
        try:
            # 기존 필터 유지
            filters = {}
            for param in ['department', 'job_group', 'job_type', 'growth_level']:
                filter_value = request.GET.get(param)
                if filter_value:
                    if param == 'growth_level':
                        filters[param] = int(filter_value)
                    else:
                        filters[param] = filter_value
            
            # 드릴다운 데이터 조회
            drill_data = self.analytics.get_drill_down_data(level, value, filters)
            
            return JsonResponse({
                'status': 'success',
                'level': level,
                'value': value,
                'data': drill_data
            })
        
        except Exception as e:
            logger.error(f"DrillDown API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '드릴다운 데이터 조회 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class SkillMapExportAPI(View):
    """스킬맵 데이터 내보내기 API"""
    
    def __init__(self):
        super().__init__()
        self.analytics = SkillMapAnalytics()
    
    def post(self, request):
        """
        POST /api/skillmap/export/
        
        Request Body:
        {
            "format": "excel|csv|pdf",
            "filters": {
                "department": "IT",
                "job_type": "IT개발"
            }
        }
        """
        try:
            data = json.loads(request.body)
            export_format = data.get('format', 'excel')
            filters = data.get('filters', {})
            
            # 데이터 내보내기
            export_result = self.analytics.export_skill_data(export_format, filters)
            
            if 'error' in export_result:
                return JsonResponse({
                    'status': 'error',
                    'message': export_result['error']
                }, status=400)
            
            return JsonResponse({
                'status': 'success',
                'export_info': export_result,
                'download_url': f'/api/skillmap/download/{export_result["filename"]}'
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '잘못된 요청 형식입니다.'
            }, status=400)
        
        except Exception as e:
            logger.error(f"Export API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '내보내기 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class DepartmentSkillScoreAPI(View):
    """부서별 스킬 점수 계산 API"""
    
    def __init__(self):
        super().__init__()
        self.analytics = SkillMapAnalytics()
    
    def get(self, request, department=None):
        """
        GET /api/skillmap/department-skill-score/<department>/
        
        Parameters:
            - department: 부서명 (URL parameter)
            - include_details: 상세 정보 포함 여부 (기본 true)
        """
        try:
            # 부서가 지정되지 않은 경우 현재 사용자의 부서 사용
            if not department:
                try:
                    employee = Employee.objects.get(user=request.user)
                    department = employee.department
                except Employee.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': '직원 정보를 찾을 수 없습니다.'
                    }, status=404)
            
            # 부서 직원 조회
            employees = Employee.objects.filter(
                department=department,
                employment_status='재직'
            ).select_related('user')
            
            if not employees.exists():
                return JsonResponse({
                    'status': 'warning',
                    'department': department,
                    'message': f"부서 '{department}'에 재직 중인 직원이 없습니다."
                })
            
            # 스킬 점수 계산
            result = self.analytics.calcSkillScoreForDeptSkill(
                department=department,
                employees=list(employees)
            )
            
            # 상세 정보 포함 여부
            include_details = request.GET.get('include_details', 'true').lower() == 'true'
            if not include_details and result['status'] == 'success':
                # 요약 정보만 반환
                return JsonResponse({
                    'status': 'success',
                    'department': department,
                    'summary': result['summary'],
                    'top_gaps': result['top_gaps'][:3],
                    'recommendations': result['recommendations'][:3]
                })
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"Department skill score API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '부서 스킬 점수 계산 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """
        POST /api/skillmap/department-skill-score/
        
        Request Body:
        {
            "departments": ["IT개발팀", "IT기획팀"],
            "skill_requirements": {
                "Python": {"required_level": 3, "category": "technical", "weight": 1.5}
            }
        }
        """
        try:
            data = json.loads(request.body)
            departments = data.get('departments', [])
            skill_requirements = data.get('skill_requirements')
            
            if not departments:
                return JsonResponse({
                    'status': 'error',
                    'message': '부서를 지정해주세요.'
                }, status=400)
            
            results = {}
            for dept in departments:
                employees = Employee.objects.filter(
                    department=dept,
                    employment_status='재직'
                ).select_related('user')
                
                if employees.exists():
                    result = self.analytics.calcSkillScoreForDeptSkill(
                        department=dept,
                        employees=list(employees),
                        skill_requirements=skill_requirements
                    )
                    results[dept] = result
                else:
                    results[dept] = {
                        'status': 'warning',
                        'message': '재직 중인 직원이 없습니다.'
                    }
            
            return JsonResponse({
                'status': 'success',
                'results': results,
                'calculated_at': datetime.now().isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '잘못된 요청 형식입니다.'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Department skill score batch API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '부서별 스킬 점수 계산 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class SkillGapAnalysisAPI(View):
    """스킬 갭 분석 API"""
    
    def __init__(self):
        super().__init__()
        self.analytics = SkillMapAnalytics()
    
    def get(self, request):
        """
        GET /api/skillmap/skill-gaps/
        
        Parameters:
            - department: 부서 필터
            - threshold: 갭 임계값 (기본 30%)
            - top_n: 상위 N개 (기본 10)
        """
        try:
            filters = {}
            for param in ['department', 'job_group', 'job_type']:
                value = request.GET.get(param)
                if value:
                    filters[param] = value
            
            threshold = float(request.GET.get('threshold', 30.0))
            top_n = int(request.GET.get('top_n', 10))
            
            # 스킬맵 데이터 조회
            skillmap_data = self.analytics.get_organization_skill_map(filters)
            
            # 스킬 갭 분석
            skill_gaps = []
            for skill_data in skillmap_data['skillmap_matrix']['skills']:
                if skill_data['gap_rate'] >= threshold:
                    skill_gaps.append({
                        'skill_name': skill_data['name'],
                        'category': skill_data['category'],
                        'gap_rate': skill_data['gap_rate'],
                        'avg_proficiency': skill_data['avg_proficiency'],
                        'priority': 'High' if skill_data['gap_rate'] > 50 else 'Medium'
                    })
            
            # 갭률 기준 정렬
            skill_gaps.sort(key=lambda x: x['gap_rate'], reverse=True)
            
            # 카테고리별 갭 분석
            category_gaps = defaultdict(list)
            for gap in skill_gaps[:top_n]:
                category_gaps[gap['category']].append(gap)
            
            return JsonResponse({
                'status': 'success',
                'analysis': {
                    'total_skills_analyzed': len(skillmap_data['skillmap_matrix']['skills']),
                    'skills_with_gaps': len(skill_gaps),
                    'avg_gap_rate': round(np.mean([s['gap_rate'] for s in skill_gaps]), 1) if skill_gaps else 0,
                    'threshold_used': threshold
                },
                'top_skill_gaps': skill_gaps[:top_n],
                'category_breakdown': dict(category_gaps),
                'recommendations': self._generate_gap_recommendations(skill_gaps[:top_n])
            })
        
        except Exception as e:
            logger.error(f"Skill gap analysis API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '스킬 갭 분석 중 오류가 발생했습니다.',
                'error': str(e)
            }, status=500)
    
    def _generate_gap_recommendations(self, top_gaps: List[Dict[str, Any]]) -> List[str]:
        """스킬 갭 기반 추천사항 생성"""
        recommendations = []
        
        if not top_gaps:
            return ["현재 심각한 스킬 갭이 발견되지 않았습니다."]
        
        high_priority_gaps = [gap for gap in top_gaps if gap['priority'] == 'High']
        
        if high_priority_gaps:
            recommendations.append(f"긴급: {', '.join([gap['skill_name'] for gap in high_priority_gaps[:3]])} 스킬 집중 개발 필요")
        
        # 카테고리별 추천
        categories = set(gap['category'] for gap in top_gaps)
        for category in categories:
            category_gaps = [gap for gap in top_gaps if gap['category'] == category]
            if len(category_gaps) >= 2:
                recommendations.append(f"{category} 영역 전반적인 역량 강화 프로그램 운영")
        
        recommendations.append("정기적인 스킬 평가 및 개발 계획 수립 권장")
        
        return recommendations[:5]


# HTML Template (skillmap/dashboard.html에 저장)
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OK금융그룹 직무스킬맵 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Noto Sans KR', sans-serif; background: #f5f6fa; color: #2c3e50; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
        .filters { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .filter-group { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
        .filter-group select { padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .metric-card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2.5rem; font-weight: bold; color: #667eea; margin-bottom: 0.5rem; }
        .metric-label { color: #64748b; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; }
        .dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; }
        .heatmap-container { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .sidebar { display: flex; flex-direction: column; gap: 1.5rem; }
        .chart-container { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .loading { text-align: center; padding: 3rem; color: #64748b; }
        .export-btn { background: #10b981; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-size: 1rem; }
        .export-btn:hover { background: #059669; }
        .skill-gap-item { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; border-bottom: 1px solid #e2e8f0; }
        .gap-rate { background: #fee2e2; color: #dc2626; padding: 0.25rem 0.75rem; border-radius: 16px; font-size: 0.8rem; font-weight: bold; }
        .gap-rate.medium { background: #fef3c7; color: #d97706; }
        .gap-rate.low { background: #dcfce7; color: #16a34a; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🏦 OK금융그룹 직무스킬맵</h1>
            <p>조직 전체 스킬 현황과 갭 분석을 한눈에 확인하세요</p>
        </div>
    </div>

    <div class="container">
        <!-- 필터 섹션 -->
        <div class="filters">
            <div class="filter-group">
                <select id="departmentFilter">
                    <option value="">전체 부서</option>
                    {% for dept_code, dept_name in departments %}
                    <option value="{{ dept_code }}">{{ dept_name }}</option>
                    {% endfor %}
                </select>
                
                <select id="jobGroupFilter">
                    <option value="">전체 직군</option>
                    {% for group_code, group_name in job_groups %}
                    <option value="{{ group_code }}">{{ group_name }}</option>
                    {% endfor %}
                </select>
                
                <select id="jobTypeFilter">
                    <option value="">전체 직종</option>
                    {% for type_code, type_name in job_types %}
                    <option value="{{ type_code }}">{{ type_name }}</option>
                    {% endfor %}
                </select>
                
                <select id="growthLevelFilter">
                    <option value="">전체 성장레벨</option>
                    {% for level_code, level_name in growth_levels %}
                    <option value="{{ level_code }}">{{ level_name }}</option>
                    {% endfor %}
                </select>
                
                <button class="export-btn" onclick="exportData()">📊 데이터 내보내기</button>
            </div>
        </div>

        <!-- 메트릭스 카드 -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value" id="totalEmployees">-</div>
                <div class="metric-label">총 직원 수</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="totalSkills">-</div>
                <div class="metric-label">분석된 스킬</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="avgProficiency">-</div>
                <div class="metric-label">평균 숙련도</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="skillGapRate">-</div>
                <div class="metric-label">스킬 갭률</div>
            </div>
        </div>

        <!-- 대시보드 그리드 -->
        <div class="dashboard-grid">
            <!-- 스킬맵 히트맵 -->
            <div class="heatmap-container">
                <h3 style="margin-bottom: 1rem;">📈 조직 스킬맵 히트맵</h3>
                <div id="skillHeatmap" class="loading">데이터를 불러오는 중...</div>
            </div>

            <!-- 사이드바 -->
            <div class="sidebar">
                <!-- 상위 스킬 갭 -->
                <div class="chart-container">
                    <h4 style="margin-bottom: 1rem;">🎯 주요 스킬 갭</h4>
                    <div id="skillGapsList"></div>
                </div>

                <!-- 부서별 분포 -->
                <div class="chart-container">
                    <h4 style="margin-bottom: 1rem;">🏢 부서별 분포</h4>
                    <canvas id="departmentChart" width="300" height="200"></canvas>
                </div>

                <!-- 카테고리별 현황 -->
                <div class="chart-container">
                    <h4 style="margin-bottom: 1rem;">📚 스킬 카테고리별 현황</h4>
                    <canvas id="categoryChart" width="300" height="200"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentData = null;
        
        // 페이지 로드 시 초기 데이터 로드
        document.addEventListener('DOMContentLoaded', function() {
            loadSkillMapData();
            
            // 필터 변경 이벤트 리스너
            document.querySelectorAll('select').forEach(select => {
                select.addEventListener('change', loadSkillMapData);
            });
        });
        
        async function loadSkillMapData() {
            try {
                // 필터 값 수집
                const filters = {
                    department: document.getElementById('departmentFilter').value,
                    job_group: document.getElementById('jobGroupFilter').value,
                    job_type: document.getElementById('jobTypeFilter').value,
                    growth_level: document.getElementById('growthLevelFilter').value
                };
                
                // API 호출
                const params = new URLSearchParams();
                Object.entries(filters).forEach(([key, value]) => {
                    if (value) params.append(key, value);
                });
                
                const response = await fetch(`/api/skillmap/?${params}`);
                const result = await response.json();
                
                if (result.status === 'success') {
                    currentData = result.data;
                    updateDashboard(currentData);
                } else {
                    console.error('API Error:', result.message);
                    showError('데이터를 불러오는 중 오류가 발생했습니다.');
                }
            } catch (error) {
                console.error('Network Error:', error);
                showError('네트워크 오류가 발생했습니다.');
            }
        }
        
        function updateDashboard(data) {
            // 메트릭스 업데이트
            document.getElementById('totalEmployees').textContent = data.metrics.total_employees.toLocaleString();
            document.getElementById('totalSkills').textContent = data.metrics.total_skills;
            document.getElementById('avgProficiency').textContent = data.metrics.avg_proficiency + '%';
            document.getElementById('skillGapRate').textContent = data.metrics.skill_gap_rate + '%';
            
            // 히트맵 생성
            createHeatmap(data.skillmap_matrix);
            
            // 스킬 갭 리스트 업데이트
            updateSkillGapsList(data.metrics.top_skill_gaps);
            
            // 차트 업데이트
            updateDepartmentChart(data.metrics.department_summary);
            updateCategoryChart(data.skillmap_matrix.category_summary);
        }
        
        function createHeatmap(matrixData) {
            const employees = matrixData.employees.map(emp => emp.name);
            const skills = matrixData.skills.map(skill => skill.name);
            const heatmapData = matrixData.heatmap_data;
            
            const data = [{
                z: heatmapData,
                x: skills,
                y: employees,
                type: 'heatmap',
                colorscale: [
                    [0, '#22c55e'],    // 녹색 (갭 없음)
                    [0.5, '#fbbf24'],  // 노란색 (중간 갭)
                    [1, '#ef4444']     // 빨간색 (큰 갭)
                ],
                hovertemplate: '직원: %{y}<br>스킬: %{x}<br>갭 수준: %{z}<extra></extra>'
            }];
            
            const layout = {
                title: '',
                xaxis: {
                    title: '스킬',
                    tickangle: -45
                },
                yaxis: {
                    title: '직원'
                },
                margin: { l: 100, r: 50, t: 50, b: 100 }
            };
            
            Plotly.newPlot('skillHeatmap', data, layout, {
                responsive: true,
                displayModeBar: false
            });
            
            // 히트맵 클릭 이벤트
            document.getElementById('skillHeatmap').on('plotly_click', function(data) {
                const skill = data.points[0].x;
                drillDownToSkill(skill);
            });
        }
        
        function updateSkillGapsList(skillGaps) {
            const container = document.getElementById('skillGapsList');
            container.innerHTML = '';
            
            skillGaps.slice(0, 8).forEach(gap => {
                const item = document.createElement('div');
                item.className = 'skill-gap-item';
                
                const gapClass = gap.gap_rate > 50 ? 'high' : gap.gap_rate > 30 ? 'medium' : 'low';
                
                item.innerHTML = `
                    <span>${gap.skill}</span>
                    <span class="gap-rate ${gapClass}">${gap.gap_rate.toFixed(1)}%</span>
                `;
                
                item.style.cursor = 'pointer';
                item.onclick = () => drillDownToSkill(gap.skill);
                
                container.appendChild(item);
            });
        }
        
        function updateDepartmentChart(deptSummary) {
            const ctx = document.getElementById('departmentChart').getContext('2d');
            
            const departments = Object.keys(deptSummary);
            const employeeCounts = departments.map(dept => deptSummary[dept].employee_count);
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: departments,
                    datasets: [{
                        data: employeeCounts,
                        backgroundColor: [
                            '#667eea', '#764ba2', '#f093fb', '#f5576c',
                            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        function updateCategoryChart(categorySummary) {
            const ctx = document.getElementById('categoryChart').getContext('2d');
            
            const categories = Object.keys(categorySummary);
            const proficiencies = categories.map(cat => categorySummary[cat].avg_proficiency);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: categories,
                    datasets: [{
                        label: '평균 숙련도',
                        data: proficiencies,
                        backgroundColor: '#667eea',
                        borderColor: '#764ba2',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
        
        async function drillDownToSkill(skillName) {
            try {
                const response = await fetch(`/api/skillmap/drilldown/skill/${encodeURIComponent(skillName)}/`);
                const result = await response.json();
                
                if (result.status === 'success') {
                    showSkillDetailModal(result.data);
                }
            } catch (error) {
                console.error('Drill-down error:', error);
            }
        }
        
        function showSkillDetailModal(skillData) {
            // 모달 창으로 스킬 상세 정보 표시
            alert(`${skillData.skill_name} 스킬 상세 분석\\n\\n` +
                  `총 직원: ${skillData.gap_analysis.total_employees}명\\n` +
                  `갭 보유 직원: ${skillData.gap_analysis.employees_with_gap}명\\n` +
                  `평균 갭 크기: ${skillData.gap_analysis.avg_gap_size}`);
        }
        
        async function exportData() {
            try {
                const filters = {
                    department: document.getElementById('departmentFilter').value,
                    job_group: document.getElementById('jobGroupFilter').value,
                    job_type: document.getElementById('jobTypeFilter').value,
                    growth_level: document.getElementById('growthLevelFilter').value
                };
                
                const response = await fetch('/api/skillmap/export/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        format: 'excel',
                        filters: filters
                    })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    alert('데이터 내보내기가 준비되었습니다.');
                    // 실제로는 다운로드 링크 제공
                }
            } catch (error) {
                console.error('Export error:', error);
                alert('내보내기 중 오류가 발생했습니다.');
            }
        }
        
        function showError(message) {
            document.getElementById('skillHeatmap').innerHTML = `<div class="loading">❌ ${message}</div>`;
        }
        
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    </script>
</body>
</html>
"""

# URL 패턴
"""
Django urls.py에 추가할 URL 패턴:

from django.urls import path
from .skillmap_dashboard import (
    SkillMapDashboardView,
    SkillMapAPI,
    SkillMapDrillDownAPI,
    SkillMapExportAPI,
    SkillGapAnalysisAPI
)

urlpatterns = [
    # 대시보드 메인 화면
    path('skillmap/', SkillMapDashboardView.as_view(), name='skillmap_dashboard'),
    
    # API 엔드포인트
    path('api/skillmap/', SkillMapAPI.as_view(), name='skillmap_api'),
    path('api/skillmap/drilldown/<str:level>/<str:value>/', SkillMapDrillDownAPI.as_view(), name='skillmap_drilldown'),
    path('api/skillmap/export/', SkillMapExportAPI.as_view(), name='skillmap_export'),
    path('api/skillmap/skill-gaps/', SkillGapAnalysisAPI.as_view(), name='skillmap_skill_gaps'),
]
"""

if __name__ == "__main__":
    print("OK Financial Group Job Skill Map Dashboard")
    print("=" * 60)
    print("Features:")
    print("✓ Skill gap analysis (skillgap)")
    print("✓ Organizational filtering (orgfilter)")
    print("✓ Drill-down navigation (drillable)")
    print("✓ Context-aware insights (contextaware)")
    print("✓ Data export capabilities (exportable)")
    print("✓ Interactive heatmap visualization")
    print("✓ Real-time KPI dashboard")
    print("✓ Department and role-based analytics")