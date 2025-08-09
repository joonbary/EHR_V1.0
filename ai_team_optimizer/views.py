"""
AI Team Optimizer Views - AI 팀 조합 최적화 뷰
"""
import json
import logging
from typing import Dict, List, Any
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from employees.models import Employee
from job_profiles.models import JobProfile
logger = logging.getLogger(__name__)

from .models import (
    Project, TeamComposition, TeamMember, SkillRequirement,
    TeamAnalytics, OptimizationHistory, TeamTemplate
)
# services import를 try-except로 감싸기
try:
    from .services import TeamOptimizer, TeamAnalyzer, SkillMatcher
except ImportError as e:
    logger.warning(f"Services import 실패: {e}")
    # 대체 클래스 정의
    class TeamAnalyzer:
        def get_team_statistics(self):
            return {
                'projects': {'total': 0, 'active': 0, 'completed': 0},
                'teams': {'total': 0, 'approved': 0, 'optimization_rate': 0}
            }
    class TeamOptimizer:
        pass
    class SkillMatcher:
        pass


class TeamOptimizerDashboardView(TemplateView):
    """팀 최적화 대시보드"""
    template_name = 'ai_team_optimizer/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # 기본 통계 - 안전한 초기화
            context.update({
                'stats': {
                    'projects': {
                        'total': 0,
                        'active': 0,
                        'completed': 0,
                    },
                    'teams': {
                        'total': 0,
                        'approved': 0,
                        'optimization_rate': 0
                    }
                },
                'recent_projects': [],
                'active_compositions': [],
                'optimization_suggestions': [],
                'templates': []
            })
            
            # TeamAnalyzer가 있으면 실제 데이터 로드
            try:
                analyzer = TeamAnalyzer()
                context['stats'] = analyzer.get_team_statistics()
            except:
                pass  # 기본값 사용
                
            context['recent_projects'] = self._get_recent_projects()
            context['active_compositions'] = self._get_active_compositions()
            context['optimization_suggestions'] = self._get_optimization_suggestions()
            
            try:
                context['templates'] = TeamTemplate.objects.filter(is_active=True)[:5]
            except:
                context['templates'] = []
            
        except Exception as e:
            logger.error(f"대시보드 데이터 로드 오류: {e}", exc_info=True)
            context['error'] = f"데이터베이스 초기화가 필요합니다: {str(e)}"
        
        return context
    
    def _get_recent_projects(self):
        """최근 프로젝트 조회"""
        try:
            return Project.objects.select_related().order_by('-created_at')[:5]
        except Exception as e:
            logger.error(f"최근 프로젝트 조회 오류: {e}")
            return []
    
    def _get_active_compositions(self):
        """활성 팀 구성 조회"""
        try:
            return TeamComposition.objects.filter(
                status__in=['PROPOSED', 'APPROVED', 'ACTIVE']
            ).select_related('project').order_by('-overall_score')[:5]
        except Exception as e:
            logger.error(f"활성 팀 구성 조회 오류: {e}")
            return []
    
    def _get_optimization_suggestions(self):
        """최적화 제안 조회"""
        try:
            suggestions = []
            
            # 낮은 점수의 팀 구성
            low_score_teams = TeamComposition.objects.filter(
                overall_score__lt=6.0,
                status__in=['PROPOSED', 'ACTIVE']
            )[:3]
            
            for team in low_score_teams:
                suggestions.append({
                    'type': 'LOW_PERFORMANCE',
                    'title': f'{team.project.name} 팀 성능 개선 필요',
                    'description': f'현재 점수: {team.overall_score:.1f}/10',
                    'priority': 'HIGH',
                    'team_id': team.id
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"최적화 제안 조회 오류: {e}")
            return []


class ProjectListView(TemplateView):
    """프로젝트 목록"""
    template_name = 'ai_team_optimizer/project_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            projects = Project.objects.all().order_by('-created_at')
            
            # 검색 필터
            search = self.request.GET.get('search', '')
            if search:
                projects = projects.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search)
                )
            
            # 상태 필터
            status = self.request.GET.get('status', '')
            if status:
                projects = projects.filter(status=status)
            
            # 페이지네이션
            paginator = Paginator(projects, 10)
            page = self.request.GET.get('page', 1)
            projects_page = paginator.get_page(page)
            
            context.update({
                'projects': projects_page,
                'search': search,
                'status': status,
                'status_choices': Project.PROJECT_STATUS_CHOICES
            })
            
        except Exception as e:
            logger.error(f"프로젝트 목록 조회 오류: {e}")
            context['error'] = str(e)
        
        return context


class ProjectDetailView(TemplateView):
    """프로젝트 상세"""
    template_name = 'ai_team_optimizer/project_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = kwargs.get('project_id')
        
        try:
            project = get_object_or_404(Project, id=project_id)
            context.update({
                'project': project,
                'compositions': project.team_compositions.all().order_by('-overall_score'),
                'skill_requirements': project.skill_requirements.all(),
                'can_optimize': project.status in ['PLANNING', 'ACTIVE']
            })
            
        except Exception as e:
            logger.error(f"프로젝트 상세 조회 오류: {e}")
            context['error'] = str(e)
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class OptimizeTeamView(View):
    """팀 최적화 API"""
    
    def post(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            
            # 최적화 실행
            optimizer = TeamOptimizer(project)
            compositions = optimizer.create_optimal_team(max_compositions=3)
            
            if compositions:
                response_data = {
                    'success': True,
                    'message': f'{len(compositions)}개의 최적 팀 구성을 생성했습니다.',
                    'compositions': [
                        {
                            'id': comp.id,
                            'name': comp.name,
                            'overall_score': comp.overall_score,
                            'team_size': comp.get_team_size(),
                            'total_cost': comp.get_total_cost()
                        }
                        for comp in compositions
                    ]
                }
            else:
                response_data = {
                    'success': False,
                    'message': '팀 구성 최적화에 실패했습니다.',
                    'error': '가용한 인력이 부족하거나 요구사항을 만족하는 구성을 찾을 수 없습니다.'
                }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"팀 최적화 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '팀 최적화 중 오류가 발생했습니다.',
                'error': str(e)
            })


class TeamCompositionDetailView(TemplateView):
    """팀 구성 상세"""
    template_name = 'ai_team_optimizer/composition_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        composition_id = kwargs.get('composition_id')
        
        try:
            composition = get_object_or_404(TeamComposition, id=composition_id)
            context.update({
                'composition': composition,
                'members': composition.team_members.select_related('employee').all(),
                'analytics': getattr(composition, 'analytics', None),
                'history': composition.optimization_history.all()[:10]
            })
            
        except Exception as e:
            logger.error(f"팀 구성 상세 조회 오류: {e}")
            context['error'] = str(e)
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class SkillMatchView(View):
    """스킬 매칭 API"""
    
    def post(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            
            matcher = SkillMatcher()
            matches = matcher.find_best_matches(project, limit=10)
            
            response_data = {
                'success': True,
                'matches': [
                    {
                        'employee_id': match['employee'].id,
                        'employee_name': match['employee'].name,
                        'department': match['employee'].department,
                        'years_experience': match['employee'].years_of_experience,
                        'match_score': match['score'],
                        'matched_skills': match['matched_skills'],
                        'recommended_roles': match['recommendations']
                    }
                    for match in matches
                ]
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"스킬 매칭 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '스킬 매칭 중 오류가 발생했습니다.',
                'error': str(e)
            })


@method_decorator(csrf_exempt, name='dispatch')
class ApproveCompositionView(View):
    """팀 구성 승인 API"""
    
    def post(self, request, composition_id):
        try:
            composition = get_object_or_404(TeamComposition, id=composition_id)
            
            # 상태 업데이트
            composition.status = 'APPROVED'
            composition.save()
            
            # 팀원 확정 처리
            composition.team_members.update(is_confirmed=True)
            
            # 최적화 기록 저장
            from .services import TeamOptimizer
            optimizer = TeamOptimizer(composition.project)
            optimizer._save_optimization_history(composition, 'APPROVE')
            
            return JsonResponse({
                'success': True,
                'message': '팀 구성이 승인되었습니다.',
                'composition': {
                    'id': composition.id,
                    'status': composition.get_status_display(),
                    'approved_at': composition.updated_at.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"팀 구성 승인 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '팀 구성 승인 중 오류가 발생했습니다.',
                'error': str(e)
            })


class AnalyticsView(TemplateView):
    """분석 대시보드"""
    template_name = 'ai_team_optimizer/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            analyzer = TeamAnalyzer()
            
            context.update({
                'statistics': analyzer.get_team_statistics(),
                'performance_data': self._get_performance_data(),
                'trend_data': self._get_trend_data(),
                'skill_analysis': self._get_skill_analysis()
            })
            
        except Exception as e:
            logger.error(f"분석 데이터 로드 오류: {e}")
            context['error'] = str(e)
        
        return context
    
    def _get_performance_data(self):
        """성과 데이터 조회"""
        try:
            compositions = TeamComposition.objects.filter(overall_score__gt=0)
            
            return {
                'score_distribution': {
                    'excellent': compositions.filter(overall_score__gte=8).count(),
                    'good': compositions.filter(overall_score__gte=6, overall_score__lt=8).count(),
                    'average': compositions.filter(overall_score__gte=4, overall_score__lt=6).count(),
                    'poor': compositions.filter(overall_score__lt=4).count()
                },
                'top_teams': compositions.order_by('-overall_score')[:5]
            }
            
        except Exception as e:
            logger.error(f"성과 데이터 조회 오류: {e}")
            return {}
    
    def _get_trend_data(self):
        """트렌드 데이터 조회"""
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            now = timezone.now()
            last_month = now - timedelta(days=30)
            
            return {
                'monthly_compositions': TeamComposition.objects.filter(
                    created_at__gte=last_month
                ).count(),
                'monthly_projects': Project.objects.filter(
                    created_at__gte=last_month
                ).count(),
                'average_scores': {
                    'current': TeamComposition.objects.filter(
                        created_at__gte=last_month
                    ).aggregate(Avg('overall_score'))['overall_score__avg'] or 0,
                    'previous': TeamComposition.objects.filter(
                        created_at__lt=last_month
                    ).aggregate(Avg('overall_score'))['overall_score__avg'] or 0
                }
            }
            
        except Exception as e:
            logger.error(f"트렌드 데이터 조회 오류: {e}")
            return {}
    
    def _get_skill_analysis(self):
        """스킬 분석 데이터"""
        try:
            # 가장 많이 요구되는 스킬 분석
            skill_requirements = SkillRequirement.objects.values('skill_name').annotate(
                count=Count('id'),
                avg_importance=Avg('weight')
            ).order_by('-count')[:10]
            
            return {
                'most_demanded_skills': list(skill_requirements),
                'skill_coverage': self._calculate_overall_skill_coverage()
            }
            
        except Exception as e:
            logger.error(f"스킬 분석 오류: {e}")
            return {}
    
    def _calculate_overall_skill_coverage(self):
        """전체 스킬 커버리지 계산"""
        try:
            total_requirements = SkillRequirement.objects.count()
            if total_requirements == 0:
                return 100.0
            
            # 간단한 커버리지 계산 (실제로는 더 복잡한 로직 필요)
            active_employees = Employee.objects.filter(status='ACTIVE').count()
            coverage = min((active_employees * 5) / total_requirements * 100, 100)
            
            return round(coverage, 1)
            
        except Exception as e:
            logger.error(f"스킬 커버리지 계산 오류: {e}")
            return 0.0


class TeamTemplatesView(TemplateView):
    """팀 템플릿 관리"""
    template_name = 'ai_team_optimizer/templates.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            templates = TeamTemplate.objects.filter(is_active=True).order_by('-usage_count')
            
            context.update({
                'templates': templates,
                'template_types': TeamTemplate.TEMPLATE_TYPE_CHOICES
            })
            
        except Exception as e:
            logger.error(f"팀 템플릿 조회 오류: {e}")
            context['error'] = str(e)
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class EmployeeAvailabilityView(View):
    """직원 가용성 조회 API"""
    
    def get(self, request):
        try:
            # 가용 직원 조회
            available_employees = Employee.objects.filter(
                status='ACTIVE'
            ).exclude(
                resignation_date__isnull=False
            )
            
            employees_data = []
            for emp in available_employees:
                employees_data.append({
                    'id': emp.id,
                    'name': emp.name,
                    'department': emp.department,
                    'position': emp.position,
                    'years_experience': emp.years_of_experience,
                    'current_projects': 0,  # 향후 구현
                    'availability_score': 8.0,  # 더미 데이터
                    'skills': []  # 향후 구현
                })
            
            return JsonResponse({
                'success': True,
                'employees': employees_data,
                'total_count': len(employees_data)
            })
            
        except Exception as e:
            logger.error(f"직원 가용성 조회 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '직원 가용성 조회 중 오류가 발생했습니다.',
                'error': str(e)
            })


@method_decorator(csrf_exempt, name='dispatch')
class ProjectSkillAnalysisView(View):
    """프로젝트 스킬 분석 API"""
    
    def get(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            
            # 스킬 요구사항 분석
            skill_requirements = SkillRequirement.objects.filter(project=project)
            
            analysis_data = {
                'project_name': project.name,
                'total_skills_required': skill_requirements.count(),
                'skill_breakdown': {},
                'critical_skills': [],
                'optional_skills': []
            }
            
            for req in skill_requirements:
                category = req.category or 'GENERAL'
                if category not in analysis_data['skill_breakdown']:
                    analysis_data['skill_breakdown'][category] = []
                
                skill_info = {
                    'name': req.skill_name,
                    'proficiency': req.get_required_proficiency_display(),
                    'importance': req.get_importance_display(),
                    'weight': req.weight
                }
                
                analysis_data['skill_breakdown'][category].append(skill_info)
                
                if req.importance in ['CRITICAL', 'REQUIRED']:
                    analysis_data['critical_skills'].append(skill_info)
                else:
                    analysis_data['optional_skills'].append(skill_info)
            
            return JsonResponse({
                'success': True,
                'analysis': analysis_data
            })
            
        except Exception as e:
            logger.error(f"프로젝트 스킬 분석 오류: {e}")
            return JsonResponse({
                'success': False,
                'message': '스킬 분석 중 오류가 발생했습니다.',
                'error': str(e)
            })
