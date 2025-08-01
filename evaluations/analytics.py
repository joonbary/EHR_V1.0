"""
평가 데이터 분석 및 인사이트 생성 서비스
OK금융그룹 평가 시스템 고급 분석 기능
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from datetime import date, timedelta
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import (
    EvaluationPeriod, 
    ContributionEvaluation, 
    ExpertiseEvaluation, 
    ImpactEvaluation,
    ComprehensiveEvaluation,
    EmployeeGrowthHistory,
    PerformanceTrend,
    GrowthLevel,
    CalibrationSession
)
from employees.models import Employee


class EvaluationAnalytics:
    """평가 데이터 종합 분석 서비스"""
    
    @staticmethod
    def get_organization_performance_summary(evaluation_period=None):
        """조직 전체 성과 요약"""
        if not evaluation_period:
            evaluation_period = EvaluationPeriod.get_active_period()
        
        if not evaluation_period:
            return {}
        
        # 전체 직원 수
        total_employees = Employee.objects.filter(
            employment_status='재직'
        ).count()
        
        # 평가 완료 현황
        comprehensive_evals = ComprehensiveEvaluation.objects.filter(
            evaluation_period=evaluation_period
        )
        
        completed_evaluations = comprehensive_evals.filter(
            status__in=['SUBMITTED', 'APPROVED']
        ).count()
        
        # 평가 등급 분포
        grade_distribution = comprehensive_evals.exclude(
            final_grade__isnull=True
        ).values('final_grade').annotate(
            count=Count('id')
        ).order_by('final_grade')
        
        # 3대 평가축 평균 점수
        contribution_avg = ContributionEvaluation.objects.filter(
            evaluation_period=evaluation_period
        ).aggregate(
            avg_score=Avg('contribution_score')
        )['avg_score'] or 0
        
        expertise_avg = ExpertiseEvaluation.objects.filter(
            evaluation_period=evaluation_period
        ).aggregate(
            avg_score=Avg('total_score')
        )['avg_score'] or 0
        
        impact_avg = ImpactEvaluation.objects.filter(
            evaluation_period=evaluation_period
        ).aggregate(
            avg_score=Avg('total_score')
        )['avg_score'] or 0
        
        # 달성률 현황
        achievement_stats = {
            'contribution': ContributionEvaluation.objects.filter(
                evaluation_period=evaluation_period,
                is_achieved=True
            ).count(),
            'expertise': ExpertiseEvaluation.objects.filter(
                evaluation_period=evaluation_period,
                is_achieved=True
            ).count(),
            'impact': ImpactEvaluation.objects.filter(
                evaluation_period=evaluation_period,
                is_achieved=True
            ).count(),
        }
        
        return {
            'evaluation_period': evaluation_period,
            'total_employees': total_employees,
            'completed_evaluations': completed_evaluations,
            'completion_rate': round((completed_evaluations / total_employees * 100), 1) if total_employees > 0 else 0,
            'grade_distribution': list(grade_distribution),
            'average_scores': {
                'contribution': round(float(contribution_avg), 1),
                'expertise': round(float(expertise_avg), 1),
                'impact': round(float(impact_avg), 1),
                'overall': round((contribution_avg + expertise_avg + impact_avg) / 3, 1)
            },
            'achievement_stats': achievement_stats,
            'achievement_rates': {
                'contribution': round((achievement_stats['contribution'] / total_employees * 100), 1) if total_employees > 0 else 0,
                'expertise': round((achievement_stats['expertise'] / total_employees * 100), 1) if total_employees > 0 else 0,
                'impact': round((achievement_stats['impact'] / total_employees * 100), 1) if total_employees > 0 else 0,
            }
        }
    
    @staticmethod
    def get_department_performance_analysis(evaluation_period=None):
        """부서별 성과 분석"""
        if not evaluation_period:
            evaluation_period = EvaluationPeriod.get_active_period()
        
        if not evaluation_period:
            return []
        
        # 부서별 데이터 수집
        departments = Employee.DEPARTMENT_CHOICES
        department_analysis = []
        
        for dept_code, dept_name in departments:
            dept_employees = Employee.objects.filter(
                employment_status='재직',
                department=dept_code
            )
            
            if not dept_employees.exists():
                continue
            
            employee_count = dept_employees.count()
            
            # 부서별 평균 점수
            dept_contribution = ContributionEvaluation.objects.filter(
                evaluation_period=evaluation_period,
                employee__in=dept_employees
            ).aggregate(avg_score=Avg('contribution_score'))['avg_score'] or 0
            
            dept_expertise = ExpertiseEvaluation.objects.filter(
                evaluation_period=evaluation_period,
                employee__in=dept_employees
            ).aggregate(avg_score=Avg('total_score'))['avg_score'] or 0
            
            dept_impact = ImpactEvaluation.objects.filter(
                evaluation_period=evaluation_period,
                employee__in=dept_employees
            ).aggregate(avg_score=Avg('total_score'))['avg_score'] or 0
            
            # 평가 완료율
            completed_count = ComprehensiveEvaluation.objects.filter(
                evaluation_period=evaluation_period,
                employee__in=dept_employees,
                status__in=['SUBMITTED', 'APPROVED']
            ).count()
            
            completion_rate = round((completed_count / employee_count * 100), 1) if employee_count > 0 else 0
            
            # 등급 분포
            grade_dist = ComprehensiveEvaluation.objects.filter(
                evaluation_period=evaluation_period,
                employee__in=dept_employees
            ).exclude(
                final_grade__isnull=True
            ).values('final_grade').annotate(
                count=Count('id')
            )
            
            department_analysis.append({
                'department_code': dept_code,
                'department_name': dept_name,
                'employee_count': employee_count,
                'completion_rate': completion_rate,
                'average_scores': {
                    'contribution': round(float(dept_contribution), 1),
                    'expertise': round(float(dept_expertise), 1),
                    'impact': round(float(dept_impact), 1),
                    'overall': round((dept_contribution + dept_expertise + dept_impact) / 3, 1)
                },
                'grade_distribution': list(grade_dist)
            })
        
        # 성과순으로 정렬
        department_analysis.sort(key=lambda x: x['average_scores']['overall'], reverse=True)
        
        return department_analysis
    
    @staticmethod
    def get_growth_level_insights(evaluation_period=None):
        """성장레벨 인사이트 분석"""
        if not evaluation_period:
            evaluation_period = EvaluationPeriod.get_active_period()
        
        if not evaluation_period:
            return {}
        
        # 레벨별 분포
        growth_histories = EmployeeGrowthHistory.objects.filter(
            evaluation_period=evaluation_period
        ).select_related('current_level', 'employee')
        
        level_distribution = {}
        promotion_candidates = []
        level_performance = {}
        
        for history in growth_histories:
            level = history.current_level.level
            level_name = history.current_level.name
            
            # 레벨별 분포
            if level not in level_distribution:
                level_distribution[level] = {
                    'level': level,
                    'name': level_name,
                    'count': 0,
                    'avg_score': 0,
                    'scores': []
                }
            
            level_distribution[level]['count'] += 1
            if history.overall_score:
                level_distribution[level]['scores'].append(float(history.overall_score))
            
            # 승급 후보자
            if history.is_promotion_eligible:
                promotion_candidates.append({
                    'employee': history.employee,
                    'current_level': history.current_level,
                    'overall_score': history.overall_score,
                    'consecutive_achievements': history.consecutive_achievements
                })
        
        # 레벨별 평균 점수 계산
        for level_data in level_distribution.values():
            if level_data['scores']:
                level_data['avg_score'] = round(sum(level_data['scores']) / len(level_data['scores']), 1)
        
        # 승급 후보자 정렬 (점수 높은 순)
        promotion_candidates.sort(key=lambda x: x['overall_score'] or 0, reverse=True)
        
        return {
            'level_distribution': list(level_distribution.values()),
            'promotion_candidates': promotion_candidates[:10],  # 상위 10명
            'total_promotion_eligible': len(promotion_candidates),
            'promotion_rate': round((len(promotion_candidates) / growth_histories.count() * 100), 1) if growth_histories.count() > 0 else 0
        }
    
    @staticmethod
    def get_performance_trends_analysis(periods_count=6):
        """성과 트렌드 분석 (최근 N개 기간)"""
        recent_periods = EvaluationPeriod.objects.filter(
            end_date__lte=timezone.now().date()
        ).order_by('-end_date')[:periods_count]
        
        if not recent_periods:
            return {}
        
        trend_data = {
            'periods': [],
            'organization_scores': {
                'contribution': [],
                'expertise': [],
                'impact': [],
                'overall': []
            },
            'completion_rates': [],
            'grade_distributions': []
        }
        
        for period in reversed(recent_periods):  # 시간순 정렬
            period_summary = EvaluationAnalytics.get_organization_performance_summary(period)
            
            trend_data['periods'].append({
                'name': str(period),
                'end_date': period.end_date
            })
            
            scores = period_summary.get('average_scores', {})
            trend_data['organization_scores']['contribution'].append(scores.get('contribution', 0))
            trend_data['organization_scores']['expertise'].append(scores.get('expertise', 0))
            trend_data['organization_scores']['impact'].append(scores.get('impact', 0))
            trend_data['organization_scores']['overall'].append(scores.get('overall', 0))
            
            trend_data['completion_rates'].append(period_summary.get('completion_rate', 0))
            trend_data['grade_distributions'].append(period_summary.get('grade_distribution', []))
        
        return trend_data
    
    @staticmethod
    def get_calibration_effectiveness_analysis(evaluation_period=None):
        """Calibration 효과성 분석"""
        if not evaluation_period:
            evaluation_period = EvaluationPeriod.get_active_period()
        
        if not evaluation_period:
            return {}
        
        calibration_sessions = CalibrationSession.objects.filter(
            evaluation_period=evaluation_period
        ).prefetch_related('participants')
        
        total_sessions = calibration_sessions.count()
        total_participants = 0
        grade_changes = 0
        
        # 전체 참여자 수 계산
        for session in calibration_sessions:
            total_participants += session.participants.count()
        
        # 등급 변경 사례 분석 (1차 vs 최종 등급)
        comprehensive_evals = ComprehensiveEvaluation.objects.filter(
            evaluation_period=evaluation_period
        ).exclude(
            manager_grade__isnull=True
        ).exclude(
            final_grade__isnull=True
        )
        
        for eval in comprehensive_evals:
            if eval.manager_grade != eval.final_grade:
                grade_changes += 1
        
        total_evaluations = comprehensive_evals.count()
        calibration_impact_rate = round((grade_changes / total_evaluations * 100), 1) if total_evaluations > 0 else 0
        
        return {
            'total_sessions': total_sessions,
            'total_participants': total_participants,
            'avg_participants_per_session': round(total_participants / total_sessions, 1) if total_sessions > 0 else 0,
            'total_evaluations': total_evaluations,
            'grade_changes': grade_changes,
            'calibration_impact_rate': calibration_impact_rate
        }
    
    @staticmethod
    def generate_ai_insights(analysis_data: Dict) -> Dict:
        """AI 기반 인사이트 생성"""
        insights = {
            'performance_insights': [],
            'recommendations': [],
            'risk_alerts': [],
            'opportunities': []
        }
        
        org_summary = analysis_data.get('organization_summary', {})
        dept_analysis = analysis_data.get('department_analysis', [])
        growth_insights = analysis_data.get('growth_insights', {})
        
        # 성과 인사이트
        completion_rate = org_summary.get('completion_rate', 0)
        if completion_rate < 80:
            insights['risk_alerts'].append({
                'type': 'completion_rate',
                'message': f'평가 완료율이 {completion_rate}%로 낮습니다. 미완료 평가에 대한 독려가 필요합니다.',
                'severity': 'high'
            })
        
        avg_scores = org_summary.get('average_scores', {})
        overall_score = avg_scores.get('overall', 0)
        
        if overall_score >= 3.5:
            insights['performance_insights'].append({
                'type': 'high_performance',
                'message': f'조직 전체 평균 점수가 {overall_score}점으로 우수한 성과를 보이고 있습니다.',
                'impact': 'positive'
            })
        elif overall_score < 2.5:
            insights['risk_alerts'].append({
                'type': 'low_performance',
                'message': f'조직 전체 평균 점수가 {overall_score}점으로 성과 개선이 필요합니다.',
                'severity': 'high'
            })
        
        # 부서별 격차 분석
        if dept_analysis:
            dept_scores = [dept['average_scores']['overall'] for dept in dept_analysis]
            if dept_scores:
                score_gap = max(dept_scores) - min(dept_scores)
                if score_gap > 1.0:
                    insights['risk_alerts'].append({
                        'type': 'department_gap',
                        'message': f'부서간 성과 격차가 {score_gap:.1f}점으로 큽니다. 성과가 낮은 부서에 대한 지원이 필요합니다.',
                        'severity': 'medium'
                    })
        
        # 승급 기회 분석
        promotion_rate = growth_insights.get('promotion_rate', 0)
        if promotion_rate > 20:
            insights['opportunities'].append({
                'type': 'promotion_opportunity',
                'message': f'승급 자격자가 {promotion_rate}%로 많습니다. 체계적인 승급 계획 수립을 고려해보세요.',
                'priority': 'high'
            })
        elif promotion_rate < 5:
            insights['risk_alerts'].append({
                'type': 'low_promotion',
                'message': f'승급 자격자가 {promotion_rate}%로 적습니다. 직원 성장 지원 프로그램 강화가 필요합니다.',
                'severity': 'medium'
            })
        
        # 추천사항 생성
        insights['recommendations'].extend([
            {
                'category': '성과 관리',
                'recommendation': '정기적인 1:1 면담을 통해 개인별 성과 향상 계획을 수립하세요.',
                'priority': 'medium'
            },
            {
                'category': '역량 개발',
                'recommendation': '부서별 맞춤형 교육 프로그램을 운영하여 전체적인 역량 향상을 도모하세요.',
                'priority': 'high'
            },
            {
                'category': '평가 품질',
                'recommendation': 'Calibration 세션을 정기적으로 운영하여 평가의 공정성과 일관성을 높이세요.',
                'priority': 'medium'
            }
        ])
        
        return insights


class EvaluationReportGenerator:
    """평가 리포트 생성 서비스"""
    
    @staticmethod
    def generate_comprehensive_report(evaluation_period=None):
        """종합 평가 리포트 생성"""
        if not evaluation_period:
            evaluation_period = EvaluationPeriod.get_active_period()
        
        if not evaluation_period:
            return None
        
        # 모든 분석 데이터 수집
        analysis_data = {
            'organization_summary': EvaluationAnalytics.get_organization_performance_summary(evaluation_period),
            'department_analysis': EvaluationAnalytics.get_department_performance_analysis(evaluation_period),
            'growth_insights': EvaluationAnalytics.get_growth_level_insights(evaluation_period),
            'performance_trends': EvaluationAnalytics.get_performance_trends_analysis(),
            'calibration_analysis': EvaluationAnalytics.get_calibration_effectiveness_analysis(evaluation_period)
        }
        
        # AI 인사이트 생성
        ai_insights = EvaluationAnalytics.generate_ai_insights(analysis_data)
        
        report = {
            'generated_at': timezone.now(),
            'evaluation_period': evaluation_period,
            'analysis_data': analysis_data,
            'ai_insights': ai_insights,
            'report_summary': {
                'total_employees': analysis_data['organization_summary'].get('total_employees', 0),
                'completion_rate': analysis_data['organization_summary'].get('completion_rate', 0),
                'overall_performance': analysis_data['organization_summary'].get('average_scores', {}).get('overall', 0),
                'promotion_eligible': analysis_data['growth_insights'].get('total_promotion_eligible', 0),
                'top_performing_department': analysis_data['department_analysis'][0]['department_name'] if analysis_data['department_analysis'] else None,
                'key_insights_count': len(ai_insights['performance_insights']) + len(ai_insights['opportunities']),
                'risk_alerts_count': len(ai_insights['risk_alerts'])
            }
        }
        
        return report