"""
Improved SkillMap Dashboard with better error handling and performance optimization
"""

import json
import logging
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from skillmap_dashboard import SkillMapAnalytics

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class SkillMapAPIImproved(View):
    """Improved SkillMap API with better error handling and pagination"""
    
    def __init__(self):
        super().__init__()
        self.analytics = SkillMapAnalytics()
    
    def _serialize_metrics(self, metrics):
        """Convert SkillMapMetrics object to serializable dict"""
        if hasattr(metrics, '__dict__'):
            return {k: v for k, v in metrics.__dict__.items() if not k.startswith('_')}
        return metrics
    
    def _serialize_skillmap_data(self, data):
        """Convert skillmap data to JSON-serializable format"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == 'metrics':
                    result[key] = self._serialize_metrics(value)
                elif isinstance(value, dict):
                    result[key] = self._serialize_skillmap_data(value)
                elif isinstance(value, list):
                    result[key] = [self._serialize_skillmap_data(item) if isinstance(item, dict) else item for item in value]
                else:
                    result[key] = value
            return result
        return data
    
    def get(self, request):
        """
        GET /api/skillmap/
        
        Parameters:
            - department: 부서 필터
            - job_group: 직군 필터 (PL/Non-PL)
            - job_type: 직종 필터
            - growth_level: 성장레벨 필터
            - format: 응답 형식 (json, heatmap, summary)
            - page: 페이지 번호 (for employee list)
            - page_size: 페이지 크기 (default: 50)
        """
        try:
            # Log request details
            logger.info(f"SkillMap API request from user: {request.user.username}")
            logger.debug(f"Request parameters: {request.GET}")
            
            # 필터 파라미터 추출
            filters = {}
            for param in ['department', 'job_group', 'job_type', 'growth_level']:
                value = request.GET.get(param)
                if value:
                    if param == 'growth_level':
                        try:
                            filters[param] = int(value)
                        except ValueError:
                            logger.warning(f"Invalid growth_level value: {value}")
                            return JsonResponse({
                                'status': 'error',
                                'message': f'잘못된 성장레벨 값입니다: {value}'
                            }, status=400)
                    else:
                        filters[param] = value
            
            # 응답 형식
            response_format = request.GET.get('format', 'json')
            
            # 페이지네이션 파라미터
            page = request.GET.get('page', 1)
            page_size = min(int(request.GET.get('page_size', 50)), 200)  # Max 200 per page
            
            # 캐시 키 생성
            cache_key = f"skillmap:{hash(str(filters))}:{response_format}:{page}:{page_size}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                logger.info("Returning cached result")
                return JsonResponse(cached_result)
            
            # 데이터 조회
            logger.info(f"Fetching skillmap data with filters: {filters}")
            skillmap_data = self.analytics.get_organization_skill_map(filters)
            
            # 페이지네이션 처리 (employee profiles)
            if response_format == 'json' and 'employee_profiles' in skillmap_data:
                employee_profiles = skillmap_data['employee_profiles']
                paginator = Paginator(employee_profiles, page_size)
                
                try:
                    employees_page = paginator.page(page)
                    skillmap_data['employee_profiles'] = list(employees_page)
                    skillmap_data['pagination'] = {
                        'current_page': page,
                        'total_pages': paginator.num_pages,
                        'total_items': paginator.count,
                        'has_next': employees_page.has_next(),
                        'has_previous': employees_page.has_previous()
                    }
                except (EmptyPage, PageNotAnInteger):
                    logger.warning(f"Invalid page number: {page}")
                    skillmap_data['employee_profiles'] = []
                    skillmap_data['pagination'] = {
                        'current_page': 1,
                        'total_pages': 0,
                        'total_items': 0,
                        'has_next': False,
                        'has_previous': False
                    }
            
            # 형식별 응답
            if response_format == 'heatmap':
                result = {
                    'status': 'success',
                    'data': {
                        'heatmap_data': skillmap_data['skillmap_matrix']['heatmap_data'],
                        'employees': skillmap_data['skillmap_matrix']['employees'][:100],  # Limit for performance
                        'skills': skillmap_data['skillmap_matrix']['skills']
                    }
                }
            elif response_format == 'summary':
                metrics = skillmap_data['metrics']
                result = {
                    'status': 'success',
                    'data': {
                        'metrics': {
                            'total_employees': getattr(metrics, 'total_employees', 0),
                            'total_skills': getattr(metrics, 'total_skills', 0),
                            'avg_proficiency': getattr(metrics, 'avg_proficiency', 0),
                            'skill_gap_rate': getattr(metrics, 'skill_gap_rate', 0),
                            'top_skill_gaps': getattr(metrics, 'top_skill_gaps', [])[:5],
                            'department_summary': getattr(metrics, 'department_summary', {}),
                            'growth_level_distribution': getattr(metrics, 'growth_level_distribution', {})
                        }
                    }
                }
            else:
                # Full JSON response
                result = {
                    'status': 'success',
                    'data': self._serialize_skillmap_data(skillmap_data)
                }
            
            # 캐시에 저장 (5분)
            cache.set(cache_key, result, 300)
            
            logger.info(f"Successfully returned skillmap data for {skillmap_data['metrics'].total_employees} employees")
            return JsonResponse(result)
        
        except Exception as e:
            logger.error(f"SkillMap API error: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': '스킬맵 데이터 조회 중 오류가 발생했습니다.',
                'error': str(e) if request.user.is_staff else '내부 서버 오류'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class SkillMapDrillDownAPIImproved(View):
    """Improved SkillMap Drill-down API with better error handling"""
    
    def __init__(self):
        super().__init__()
        self.analytics = SkillMapAnalytics()
    
    def _serialize_metrics(self, metrics):
        """Convert SkillMapMetrics object to serializable dict"""
        if hasattr(metrics, '__dict__'):
            return {k: v for k, v in metrics.__dict__.items() if not k.startswith('_')}
        return metrics
    
    def _serialize_skillmap_data(self, data):
        """Convert skillmap data to JSON-serializable format"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == 'metrics':
                    result[key] = self._serialize_metrics(value)
                elif isinstance(value, dict):
                    result[key] = self._serialize_skillmap_data(value)
                elif isinstance(value, list):
                    result[key] = [self._serialize_skillmap_data(item) if isinstance(item, dict) else item for item in value]
                else:
                    result[key] = value
            return result
        return data
    
    def get(self, request, level, value):
        """
        GET /api/skillmap/drilldown/<level>/<value>/
        
        Parameters:
            - level: department, job_type, growth_level, skill
            - value: 해당 레벨의 값
        """
        try:
            logger.info(f"Drill-down request: level={level}, value={value}")
            
            # 유효한 레벨 확인
            valid_levels = ['department', 'job_type', 'growth_level', 'skill']
            if level not in valid_levels:
                return JsonResponse({
                    'status': 'error',
                    'message': f'잘못된 드릴다운 레벨입니다: {level}'
                }, status=400)
            
            # 기존 필터 유지
            filters = {}
            for param in ['department', 'job_group', 'job_type', 'growth_level']:
                filter_value = request.GET.get(param)
                if filter_value:
                    if param == 'growth_level':
                        try:
                            filters[param] = int(filter_value)
                        except ValueError:
                            continue
                    else:
                        filters[param] = filter_value
            
            # 캐시 확인
            cache_key = f"skillmap_drill:{level}:{value}:{hash(str(filters))}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                logger.info("Returning cached drill-down result")
                return JsonResponse(cached_result)
            
            # 드릴다운 데이터 조회
            drill_data = self.analytics.get_drill_down_data(level, value, filters)
            
            result = {
                'status': 'success',
                'level': level,
                'value': value,
                'data': self._serialize_skillmap_data(drill_data)
            }
            
            # 캐시에 저장 (5분)
            cache.set(cache_key, result, 300)
            
            logger.info(f"Successfully returned drill-down data for {level}={value}")
            return JsonResponse(result)
        
        except Exception as e:
            logger.error(f"DrillDown API error: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': '드릴다운 데이터 조회 중 오류가 발생했습니다.',
                'error': str(e) if request.user.is_staff else '내부 서버 오류'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class SkillMapExportAPIImproved(View):
    """Improved SkillMap Export API with progress tracking"""
    
    def __init__(self):
        super().__init__()
        self.analytics = SkillMapAnalytics()
    
    def _serialize_export_result(self, result):
        """Convert export result to JSON-serializable format"""
        if isinstance(result, dict):
            serialized = {}
            for key, value in result.items():
                if hasattr(value, '__dict__'):
                    serialized[key] = {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
                elif isinstance(value, dict):
                    serialized[key] = self._serialize_export_result(value)
                elif isinstance(value, list):
                    serialized[key] = [self._serialize_export_result(item) if isinstance(item, dict) else item for item in value]
                else:
                    serialized[key] = value
            return serialized
        return result
    
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
            # Parse request body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': '잘못된 요청 형식입니다. JSON 형식으로 전송해주세요.'
                }, status=400)
            
            export_format = data.get('format', 'excel').lower()
            filters = data.get('filters', {})
            
            # Validate export format
            valid_formats = ['excel', 'csv', 'pdf']
            if export_format not in valid_formats:
                return JsonResponse({
                    'status': 'error',
                    'message': f'지원하지 않는 형식입니다: {export_format}. 지원 형식: {", ".join(valid_formats)}'
                }, status=400)
            
            logger.info(f"Export request: format={export_format}, filters={filters}")
            
            # 데이터 내보내기
            export_result = self.analytics.export_skill_data(export_format, filters)
            
            if 'error' in export_result:
                return JsonResponse({
                    'status': 'error',
                    'message': export_result['error']
                }, status=400)
            
            # Create download URL (in real implementation, would save file and return URL)
            download_url = f'/api/skillmap/download/{export_result["filename"]}'
            
            logger.info(f"Export successful: {export_result['filename']}")
            
            return JsonResponse({
                'status': 'success',
                'export_info': self._serialize_export_result(export_result),
                'download_url': download_url,
                'message': f'{export_format.upper()} 파일이 성공적으로 생성되었습니다.'
            })
        
        except Exception as e:
            logger.error(f"Export API error: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': '내보내기 중 오류가 발생했습니다.',
                'error': str(e) if request.user.is_staff else '내부 서버 오류'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class SkillGapAnalysisAPIImproved(View):
    """Improved Skill Gap Analysis API with recommendations"""
    
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
            
            # Parse parameters with validation
            try:
                threshold = float(request.GET.get('threshold', 30.0))
                if not 0 <= threshold <= 100:
                    raise ValueError("Threshold must be between 0 and 100")
            except ValueError as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'잘못된 임계값입니다: {e}'
                }, status=400)
            
            try:
                top_n = int(request.GET.get('top_n', 10))
                if not 1 <= top_n <= 50:
                    raise ValueError("top_n must be between 1 and 50")
            except ValueError as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'잘못된 top_n 값입니다: {e}'
                }, status=400)
            
            logger.info(f"Skill gap analysis: threshold={threshold}, top_n={top_n}, filters={filters}")
            
            # 스킬맵 데이터 조회
            skillmap_data = self.analytics.get_organization_skill_map(filters)
            
            # 스킬 갭 분석
            skill_gaps = []
            skills_data = skillmap_data['skillmap_matrix']['skills']
            
            for skill_data in skills_data:
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
            from collections import defaultdict
            category_gaps = defaultdict(list)
            for gap in skill_gaps[:top_n]:
                category_gaps[gap['category']].append(gap)
            
            # Generate recommendations
            recommendations = self._generate_gap_recommendations(skill_gaps[:top_n])
            
            result = {
                'status': 'success',
                'analysis': {
                    'total_skills_analyzed': len(skills_data),
                    'skills_with_gaps': len(skill_gaps),
                    'avg_gap_rate': round(sum(s['gap_rate'] for s in skill_gaps) / len(skill_gaps), 1) if skill_gaps else 0,
                    'threshold_used': threshold
                },
                'top_skill_gaps': skill_gaps[:top_n],
                'category_breakdown': dict(category_gaps),
                'recommendations': recommendations
            }
            
            logger.info(f"Skill gap analysis completed: {len(skill_gaps)} gaps found")
            return JsonResponse(result)
        
        except Exception as e:
            logger.error(f"Skill gap analysis API error: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': '스킬 갭 분석 중 오류가 발생했습니다.',
                'error': str(e) if request.user.is_staff else '내부 서버 오류'
            }, status=500)
    
    def _generate_gap_recommendations(self, top_gaps):
        """스킬 갭 기반 추천사항 생성"""
        recommendations = []
        
        if not top_gaps:
            return ["현재 심각한 스킬 갭이 발견되지 않았습니다."]
        
        high_priority_gaps = [gap for gap in top_gaps if gap['priority'] == 'High']
        
        if high_priority_gaps:
            skills = ', '.join([gap['skill_name'] for gap in high_priority_gaps[:3]])
            recommendations.append(f"긴급: {skills} 스킬 집중 개발 필요")
        
        # 카테고리별 추천
        categories = set(gap['category'] for gap in top_gaps)
        for category in categories:
            category_gaps = [gap for gap in top_gaps if gap['category'] == category]
            if len(category_gaps) >= 2:
                recommendations.append(f"{category} 영역 전반적인 역량 강화 프로그램 운영")
        
        recommendations.append("정기적인 스킬 평가 및 개발 계획 수립 권장")
        
        return recommendations[:5]