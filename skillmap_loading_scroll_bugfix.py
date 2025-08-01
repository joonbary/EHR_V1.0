"""
스킬맵 대시보드 로딩 무한 스크롤 버그 수정
Skillmap Dashboard Loading Infinite Scroll Bug Fix

목적: 스킬맵 대시보드의 무한 로딩 및 스크롤 문제 해결
작성자: Frontend Performance Specialist + Django Backend Expert
작성일: 2024-12-31
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SkillmapLoadingBugFixer:
    """스킬맵 대시보드 로딩 버그 수정"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues_found = []
        self.fixes_applied = []
        
    def diagnose_issues(self) -> Dict[str, Any]:
        """문제점 진단"""
        logger.info("=== 스킬맵 대시보드 로딩 문제 진단 시작 ===")
        
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'issues': [],
            'affected_files': [],
            'recommendations': []
        }
        
        # 1. JavaScript 무한 루프 체크
        js_issues = self._check_javascript_loops()
        if js_issues:
            diagnosis['issues'].extend(js_issues)
            
        # 2. API 호출 무한 반복 체크
        api_issues = self._check_api_calls()
        if api_issues:
            diagnosis['issues'].extend(api_issues)
            
        # 3. CSS 스크롤 충돌 체크
        css_issues = self._check_css_scroll_conflicts()
        if css_issues:
            diagnosis['issues'].extend(css_issues)
            
        # 4. 템플릿 렌더링 문제 체크
        template_issues = self._check_template_issues()
        if template_issues:
            diagnosis['issues'].extend(template_issues)
            
        # 5. 백엔드 데이터 페이징 문제 체크
        backend_issues = self._check_backend_pagination()
        if backend_issues:
            diagnosis['issues'].extend(backend_issues)
            
        # 권장사항 생성
        diagnosis['recommendations'] = self._generate_recommendations(diagnosis['issues'])
        
        return diagnosis
    
    def _check_javascript_loops(self) -> List[Dict[str, Any]]:
        """JavaScript 무한 루프 검사"""
        issues = []
        
        # 검사할 패턴들
        loop_patterns = [
            r'while\s*\(\s*true\s*\)',  # while(true)
            r'setInterval\s*\([^,]+,\s*\d{1,3}\s*\)',  # 너무 짧은 interval
            r'addEventListener\s*\(\s*[\'"]scroll[\'"].*?{[^}]*?\.scrollTo',  # scroll 이벤트 내 scrollTo
            r'useEffect\s*\(\s*\(\)\s*=>\s*{[^}]*?setState[^}]*?},\s*\[\s*\]\s*\)',  # 빈 deps의 setState
        ]
        
        js_files = list(self.project_root.glob('**/*.js'))
        js_files.extend(self.project_root.glob('**/*.jsx'))
        
        for js_file in js_files:
            if 'node_modules' in str(js_file):
                continue
                
            try:
                content = js_file.read_text(encoding='utf-8')
                
                for pattern in loop_patterns:
                    matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        issues.append({
                            'type': 'javascript_loop',
                            'file': str(js_file),
                            'line': line_no,
                            'pattern': pattern,
                            'snippet': match.group(0)[:100],
                            'severity': 'high'
                        })
            except Exception as e:
                logger.error(f"Error checking {js_file}: {e}")
                
        return issues
    
    def _check_api_calls(self) -> List[Dict[str, Any]]:
        """API 호출 무한 반복 검사"""
        issues = []
        
        # API 호출 패턴
        api_patterns = [
            r'fetch\s*\([^)]+\)(?![^{]*catch)',  # catch 없는 fetch
            r'axios\.[get|post|put|delete]+\s*\([^)]+\)(?![^{]*catch)',  # catch 없는 axios
            r'useEffect.*fetch.*\[\s*\]',  # 빈 dependency의 fetch
            r'componentDidMount.*setInterval.*fetch',  # mount시 반복 fetch
        ]
        
        for pattern in api_patterns:
            files = list(self.project_root.glob('**/*.js'))
            files.extend(self.project_root.glob('**/*.jsx'))
            files.extend(self.project_root.glob('**/*.ts'))
            files.extend(self.project_root.glob('**/*.tsx'))
            
            for file in files:
                if 'node_modules' in str(file):
                    continue
                    
                try:
                    content = file.read_text(encoding='utf-8')
                    matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
                    
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        issues.append({
                            'type': 'api_infinite_call',
                            'file': str(file),
                            'line': line_no,
                            'pattern': 'Potential infinite API call',
                            'snippet': match.group(0)[:100],
                            'severity': 'high'
                        })
                except Exception as e:
                    logger.error(f"Error checking API calls in {file}: {e}")
                    
        return issues
    
    def _check_css_scroll_conflicts(self) -> List[Dict[str, Any]]:
        """CSS 스크롤 충돌 검사"""
        issues = []
        
        # 문제가 될 수 있는 CSS 패턴
        problematic_css = [
            r'height:\s*100vh.*overflow:\s*scroll',  # 100vh with scroll
            r'position:\s*fixed.*overflow:\s*auto',  # fixed with auto overflow
            r'overflow:\s*hidden.*overflow-[xy]:\s*scroll',  # conflicting overflow
            r'body\s*{[^}]*overflow:\s*hidden',  # body overflow hidden
        ]
        
        css_files = list(self.project_root.glob('**/*.css'))
        css_files.extend(self.project_root.glob('**/*.scss'))
        css_files.extend(self.project_root.glob('**/*.sass'))
        
        for css_file in css_files:
            if 'node_modules' in str(css_file):
                continue
                
            try:
                content = css_file.read_text(encoding='utf-8')
                
                for pattern in problematic_css:
                    matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        issues.append({
                            'type': 'css_scroll_conflict',
                            'file': str(css_file),
                            'line': line_no,
                            'pattern': 'CSS scroll conflict',
                            'snippet': match.group(0)[:100],
                            'severity': 'medium'
                        })
            except Exception as e:
                logger.error(f"Error checking CSS in {css_file}: {e}")
                
        return issues
    
    def _check_template_issues(self) -> List[Dict[str, Any]]:
        """템플릿 렌더링 문제 검사"""
        issues = []
        
        # 스킬맵 관련 템플릿 찾기
        template_files = list(self.project_root.glob('**/templates/**/skillmap*.html'))
        template_files.extend(self.project_root.glob('**/templates/**/dashboard*.html'))
        
        for template in template_files:
            try:
                content = template.read_text(encoding='utf-8')
                
                # 무한 루프 가능성 있는 템플릿 태그
                if '{% for' in content:
                    # nested loops without limit
                    nested_loops = re.findall(r'{% for.*?%}.*?{% for.*?%}', content, re.DOTALL)
                    if nested_loops:
                        issues.append({
                            'type': 'template_nested_loop',
                            'file': str(template),
                            'pattern': 'Nested loops without pagination',
                            'severity': 'medium'
                        })
                
                # JavaScript 인라인 스크립트 체크
                inline_scripts = re.findall(r'<script[^>]*>.*?</script>', content, re.DOTALL)
                for script in inline_scripts:
                    if 'setInterval' in script or 'setTimeout' in script:
                        if not 'clearInterval' in script and not 'clearTimeout' in script:
                            issues.append({
                                'type': 'template_inline_timer',
                                'file': str(template),
                                'pattern': 'Timer without cleanup',
                                'severity': 'high'
                            })
                            
            except Exception as e:
                logger.error(f"Error checking template {template}: {e}")
                
        return issues
    
    def _check_backend_pagination(self) -> List[Dict[str, Any]]:
        """백엔드 페이지네이션 문제 검사"""
        issues = []
        
        # Django view 파일들 검사
        view_files = list(self.project_root.glob('**/views.py'))
        view_files.extend(self.project_root.glob('**/views/*.py'))
        view_files.extend(self.project_root.glob('**/dashboard_views.py'))
        
        for view_file in view_files:
            if 'skillmap' not in str(view_file).lower() and 'dashboard' not in str(view_file).lower():
                continue
                
            try:
                content = view_file.read_text(encoding='utf-8')
                
                # 페이지네이션 없는 대량 쿼리 체크
                if '.objects.all()' in content or '.objects.filter' in content:
                    if 'paginator' not in content.lower() and '[:' not in content:
                        issues.append({
                            'type': 'backend_no_pagination',
                            'file': str(view_file),
                            'pattern': 'Query without pagination',
                            'severity': 'high'
                        })
                        
                # N+1 쿼리 문제
                if 'for ' in content and '.objects.' in content:
                    if 'select_related' not in content and 'prefetch_related' not in content:
                        issues.append({
                            'type': 'backend_n_plus_one',
                            'file': str(view_file),
                            'pattern': 'Potential N+1 query',
                            'severity': 'medium'
                        })
                        
            except Exception as e:
                logger.error(f"Error checking backend in {view_file}: {e}")
                
        return issues
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """문제 해결 권장사항 생성"""
        recommendations = []
        
        issue_types = set(issue['type'] for issue in issues)
        
        if 'javascript_loop' in issue_types:
            recommendations.append({
                'category': 'JavaScript',
                'action': 'Add proper loop termination conditions and cleanup timers',
                'priority': 'high'
            })
            
        if 'api_infinite_call' in issue_types:
            recommendations.append({
                'category': 'API Calls',
                'action': 'Implement proper error handling and request debouncing',
                'priority': 'high'
            })
            
        if 'css_scroll_conflict' in issue_types:
            recommendations.append({
                'category': 'CSS',
                'action': 'Review and fix conflicting scroll styles',
                'priority': 'medium'
            })
            
        if 'backend_no_pagination' in issue_types:
            recommendations.append({
                'category': 'Backend',
                'action': 'Implement pagination for large querysets',
                'priority': 'high'
            })
            
        return recommendations
    
    def generate_fixes(self) -> Dict[str, str]:
        """버그 수정 코드 생성"""
        fixes = {}
        
        # 1. JavaScript 무한 스크롤 수정
        fixes['infinite_scroll_fix.js'] = """
// 스킬맵 대시보드 무한 스크롤 수정
(function() {
    'use strict';
    
    // 1. 스크롤 이벤트 디바운싱
    let scrollTimeout;
    const handleScroll = (e) => {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        scrollTimeout = setTimeout(() => {
            // 실제 스크롤 처리 로직
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight;
            const clientHeight = window.innerHeight;
            
            // 바닥 도달 체크 (100px 여유)
            if (scrollTop + clientHeight >= scrollHeight - 100) {
                loadMoreData();
            }
        }, 150); // 150ms 디바운스
    };
    
    // 2. 데이터 로딩 상태 관리
    let isLoading = false;
    let hasMoreData = true;
    let currentPage = 1;
    
    const loadMoreData = async () => {
        if (isLoading || !hasMoreData) return;
        
        isLoading = true;
        showLoadingIndicator();
        
        try {
            const response = await fetch(`/api/skillmap/data?page=${currentPage}`);
            if (!response.ok) throw new Error('Failed to load data');
            
            const data = await response.json();
            
            if (data.results.length === 0) {
                hasMoreData = false;
            } else {
                renderData(data.results);
                currentPage++;
            }
        } catch (error) {
            console.error('Error loading data:', error);
            showErrorMessage();
        } finally {
            isLoading = false;
            hideLoadingIndicator();
        }
    };
    
    // 3. 클린업 함수
    const cleanup = () => {
        window.removeEventListener('scroll', handleScroll);
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
    };
    
    // 4. 초기화
    const init = () => {
        // 기존 리스너 제거
        cleanup();
        
        // 새 리스너 추가
        window.addEventListener('scroll', handleScroll, { passive: true });
        
        // 페이지 언로드 시 클린업
        window.addEventListener('beforeunload', cleanup);
    };
    
    // DOM 준비 시 초기화
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
"""

        # 2. React 컴포넌트 수정 예시
        fixes['SkillmapDashboard.jsx'] = """
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { debounce } from 'lodash';

const SkillmapDashboard = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    
    const observerRef = useRef();
    const lastElementRef = useRef();
    
    // API 호출 함수
    const fetchData = useCallback(async (pageNum) => {
        if (loading) return;
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`/api/skillmap/data?page=${pageNum}`);
            if (!response.ok) throw new Error('Failed to fetch data');
            
            const result = await response.json();
            
            setData(prev => pageNum === 1 ? result.results : [...prev, ...result.results]);
            setHasMore(result.has_next);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [loading]);
    
    // Intersection Observer 설정
    useEffect(() => {
        const options = {
            root: null,
            rootMargin: '100px',
            threshold: 0.1
        };
        
        observerRef.current = new IntersectionObserver((entries) => {
            const target = entries[0];
            if (target.isIntersecting && hasMore && !loading) {
                setPage(prev => prev + 1);
            }
        }, options);
        
        if (lastElementRef.current) {
            observerRef.current.observe(lastElementRef.current);
        }
        
        return () => {
            if (observerRef.current) {
                observerRef.current.disconnect();
            }
        };
    }, [hasMore, loading]);
    
    // 페이지 변경 시 데이터 로드
    useEffect(() => {
        fetchData(page);
    }, [page, fetchData]);
    
    // 스크롤 위치 복원 방지
    useEffect(() => {
        window.history.scrollRestoration = 'manual';
        
        return () => {
            window.history.scrollRestoration = 'auto';
        };
    }, []);
    
    return (
        <div className="skillmap-dashboard">
            <div className="skillmap-content">
                {data.map((item, index) => (
                    <div 
                        key={item.id} 
                        ref={index === data.length - 1 ? lastElementRef : null}
                        className="skill-item"
                    >
                        {/* 스킬 아이템 렌더링 */}
                    </div>
                ))}
            </div>
            
            {loading && (
                <div className="loading-indicator">
                    <div className="spinner"></div>
                    <span>데이터 로딩 중...</span>
                </div>
            )}
            
            {error && (
                <div className="error-message">
                    <p>오류가 발생했습니다: {error}</p>
                    <button onClick={() => fetchData(page)}>다시 시도</button>
                </div>
            )}
            
            {!hasMore && data.length > 0 && (
                <div className="end-message">
                    모든 데이터를 불러왔습니다.
                </div>
            )}
        </div>
    );
};

export default SkillmapDashboard;
"""

        # 3. CSS 스크롤 수정
        fixes['skillmap_scroll_fix.css'] = """
/* 스킬맵 대시보드 스크롤 수정 */

/* 1. 전역 스크롤 리셋 */
html {
    scroll-behavior: smooth;
    overflow-y: auto;
}

body {
    overflow-x: hidden;
    /* overflow-y는 auto로 유지 */
    overflow-y: auto;
}

/* 2. 스킬맵 컨테이너 수정 */
.skillmap-dashboard {
    /* 고정 높이 제거 */
    min-height: 100vh;
    /* overflow 제거하여 자연스러운 스크롤 */
    overflow: visible;
    position: relative;
}

/* 3. 스크롤 가능 영역 명확히 정의 */
.skillmap-content {
    /* 최대 높이 설정 */
    max-height: calc(100vh - 200px);
    overflow-y: auto;
    overflow-x: hidden;
    /* 부드러운 스크롤 */
    scroll-behavior: smooth;
    /* iOS 관성 스크롤 */
    -webkit-overflow-scrolling: touch;
}

/* 4. 로딩 인디케이터 위치 수정 */
.loading-indicator {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    background: rgba(255, 255, 255, 0.95);
    padding: 10px 20px;
    border-radius: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* 5. 스크롤바 스타일링 */
.skillmap-content::-webkit-scrollbar {
    width: 8px;
}

.skillmap-content::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.skillmap-content::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

.skillmap-content::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* 6. 모바일 대응 */
@media (max-width: 768px) {
    .skillmap-content {
        max-height: calc(100vh - 150px);
        /* 모바일에서는 스크롤바 숨김 */
        scrollbar-width: none;
    }
    
    .skillmap-content::-webkit-scrollbar {
        display: none;
    }
}
"""

        # 4. Django View 페이지네이션 수정
        fixes['skillmap_views_pagination.py'] = """
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
import json

@require_http_methods(["GET"])
@cache_page(60 * 5)  # 5분 캐시
def skillmap_data_api(request):
    '''스킬맵 데이터 API with 페이지네이션'''
    
    try:
        # 페이지 파라미터
        page = request.GET.get('page', 1)
        per_page = int(request.GET.get('per_page', 20))
        
        # 최대 페이지당 항목 수 제한
        per_page = min(per_page, 100)
        
        # 쿼리 최적화
        queryset = (Employee.objects
                   .select_related('job_profile', 'department')
                   .prefetch_related('skills')
                   .filter(employment_status='재직')
                   .order_by('department', 'name'))
        
        # 페이지네이션
        paginator = Paginator(queryset, per_page)
        
        try:
            employees = paginator.page(page)
        except PageNotAnInteger:
            employees = paginator.page(1)
        except EmptyPage:
            return JsonResponse({
                'results': [],
                'has_next': False,
                'has_previous': False,
                'total_pages': paginator.num_pages,
                'current_page': page,
                'total_count': 0
            })
        
        # 데이터 직렬화
        results = []
        for employee in employees:
            results.append({
                'id': str(employee.id),
                'name': employee.name,
                'department': employee.department,
                'job_title': employee.job_title,
                'skills': [
                    {
                        'skill_name': skill.skill_name,
                        'proficiency_level': skill.proficiency_level,
                        'skill_category': skill.skill_category
                    }
                    for skill in employee.skills.all()
                ]
            })
        
        return JsonResponse({
            'results': results,
            'has_next': employees.has_next(),
            'has_previous': employees.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': employees.number,
            'total_count': paginator.count
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'results': []
        }, status=500)


class SkillmapDashboardView(LoginRequiredMixin, TemplateView):
    '''스킬맵 대시보드 뷰 with 최적화'''
    
    template_name = 'dashboards/skillmap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 초기 데이터만 로드 (첫 페이지)
        initial_employees = (Employee.objects
                           .select_related('job_profile', 'department')
                           .prefetch_related('skills')
                           .filter(employment_status='재직')
                           .order_by('department', 'name')[:20])
        
        # 요약 통계만 계산
        context['stats'] = {
            'total_employees': Employee.objects.filter(employment_status='재직').count(),
            'departments': Employee.objects.values('department').distinct().count(),
            'total_skills': Skill.objects.count(),
        }
        
        # 초기 데이터
        context['initial_data'] = [
            {
                'id': str(emp.id),
                'name': emp.name,
                'department': emp.department,
                'skills_count': emp.skills.count()
            }
            for emp in initial_employees
        ]
        
        return context
"""

        # 5. 통합 수정 가이드
        fixes['IMPLEMENTATION_GUIDE.md'] = """# 스킬맵 대시보드 무한 로딩/스크롤 버그 수정 가이드

## 문제점 요약
1. JavaScript 무한 루프로 인한 지속적인 API 호출
2. CSS 스크롤 충돌로 인한 스크롤 동작 이상
3. 페이지네이션 부재로 인한 대량 데이터 로딩
4. 메모리 누수 및 성능 저하

## 수정 방법

### 1. JavaScript 수정
- `infinite_scroll_fix.js` 파일을 static/js/ 디렉토리에 추가
- 기존 스크롤 이벤트 리스너를 디바운싱된 버전으로 교체
- 로딩 상태 관리 및 중복 요청 방지 로직 추가

### 2. React 컴포넌트 수정 (해당되는 경우)
- `SkillmapDashboard.jsx` 컴포넌트를 Intersection Observer 패턴으로 수정
- useEffect 의존성 배열 정확히 설정
- 클린업 함수로 메모리 누수 방지

### 3. CSS 수정
- `skillmap_scroll_fix.css`를 static/css/ 디렉토리에 추가
- 기존 CSS에서 충돌하는 overflow 속성 제거
- 명확한 스크롤 컨테이너 정의

### 4. Django View 수정
- `skillmap_views_pagination.py`의 코드를 기존 view에 적용
- Paginator 사용하여 데이터 페이징 구현
- select_related/prefetch_related로 쿼리 최적화

### 5. 템플릿 수정
```html
<!-- templates/dashboards/skillmap.html -->
<div class="skillmap-dashboard">
    <div class="skillmap-content" id="skillmap-content">
        <!-- 초기 데이터 렌더링 -->
        {% for item in initial_data %}
            <div class="skill-item">
                <!-- 아이템 내용 -->
            </div>
        {% endfor %}
    </div>
    
    <div class="loading-indicator" style="display: none;">
        <div class="spinner"></div>
        <span>Loading...</span>
    </div>
</div>

<script src="{% static 'js/infinite_scroll_fix.js' %}"></script>
```

## 테스트 방법

### 1. 로컬 테스트
```bash
# 개발 서버 시작
python manage.py runserver

# 브라우저 개발자 도구 열기
# Network 탭에서 API 호출 확인
# Console에서 에러 확인
```

### 2. 성능 테스트
```javascript
// 브라우저 콘솔에서 실행
performance.mark('scroll-start');
// 스크롤 동작 수행
performance.mark('scroll-end');
performance.measure('scroll-performance', 'scroll-start', 'scroll-end');
console.log(performance.getEntriesByName('scroll-performance'));
```

### 3. 메모리 누수 테스트
- Chrome DevTools > Memory > Heap Snapshot
- 스크롤 전후 스냅샷 비교
- Detached DOM nodes 확인

## 배포 전 체크리스트
- [ ] 모든 수정 파일 백업
- [ ] 로컬 환경에서 충분한 테스트
- [ ] API 엔드포인트 응답 시간 확인
- [ ] 브라우저 호환성 테스트 (Chrome, Firefox, Safari)
- [ ] 모바일 반응형 테스트
- [ ] 에러 로깅 설정 확인

## 롤백 계획
1. 수정 전 파일 백업 보관
2. Git 커밋으로 변경사항 추적
3. 문제 발생 시 즉시 이전 버전으로 복원

## 모니터링
- 서버 로그에서 API 호출 빈도 모니터링
- 클라이언트 에러 추적 (Sentry 등)
- 성능 메트릭 수집 및 분석
"""

        return fixes
    
    def apply_fixes(self, target_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """선택적으로 수정 사항 적용"""
        results = {
            'applied': [],
            'failed': [],
            'backup_created': False
        }
        
        # 백업 생성
        backup_dir = self.project_root / f'skillmap_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        try:
            backup_dir.mkdir(exist_ok=True)
            results['backup_created'] = True
            results['backup_dir'] = str(backup_dir)
            
            # TODO: 실제 파일 수정 로직
            # 여기서는 가이드만 제공하므로 실제 적용은 수동으로
            
        except Exception as e:
            logger.error(f"Error applying fixes: {e}")
            
        return results
    
    def generate_test_suite(self) -> str:
        """테스트 스위트 생성"""
        test_code = """
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SkillmapScrollTest(unittest.TestCase):
    '''스킬맵 무한 스크롤 테스트'''
    
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get('http://localhost:8000/dashboards/skillmap/')
        # 로그인 처리
        
    def tearDown(self):
        self.driver.quit()
        
    def test_scroll_loading(self):
        '''스크롤 시 추가 데이터 로딩 테스트'''
        # 초기 아이템 수 확인
        initial_items = len(self.driver.find_elements(By.CLASS_NAME, 'skill-item'))
        
        # 스크롤 다운
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 로딩 대기
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'loading-indicator')))
        
        # 새 아이템 로드 대기
        time.sleep(2)
        
        # 아이템 수 증가 확인
        new_items = len(self.driver.find_elements(By.CLASS_NAME, 'skill-item'))
        self.assertGreater(new_items, initial_items)
        
    def test_no_infinite_loop(self):
        '''무한 루프 방지 테스트'''
        # 네트워크 요청 수 모니터링
        self.driver.execute_script('''
            window.apiCallCount = 0;
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                window.apiCallCount++;
                return originalFetch.apply(this, args);
            };
        ''')
        
        # 빠른 스크롤 여러 번
        for _ in range(5):
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.1)
        
        # API 호출 수 확인
        api_calls = self.driver.execute_script("return window.apiCallCount;")
        self.assertLess(api_calls, 10, "Too many API calls detected")
        
    def test_scroll_to_bottom(self):
        '''끝까지 스크롤 테스트'''
        # 계속 스크롤하여 끝 도달
        last_height = 0
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight;")
            if new_height == last_height:
                break
            last_height = new_height
            
        # "더 이상 데이터 없음" 메시지 확인
        end_message = self.driver.find_element(By.CLASS_NAME, 'end-message')
        self.assertTrue(end_message.is_displayed())

if __name__ == '__main__':
    unittest.main()
"""
        return test_code

def main():
    """메인 실행 함수"""
    logger.info("스킬맵 대시보드 로딩 버그 수정 시작")
    
    fixer = SkillmapLoadingBugFixer()
    
    # 1. 문제 진단
    logger.info("\n=== 1단계: 문제 진단 ===")
    diagnosis = fixer.diagnose_issues()
    
    logger.info(f"발견된 문제: {len(diagnosis['issues'])}개")
    for issue in diagnosis['issues'][:5]:  # 처음 5개만 표시
        logger.info(f"- [{issue['severity']}] {issue['type']} in {issue['file']}")
    
    # 2. 수정 코드 생성
    logger.info("\n=== 2단계: 수정 코드 생성 ===")
    fixes = fixer.generate_fixes()
    
    # 수정 파일 저장
    output_dir = Path('skillmap_fixes')
    output_dir.mkdir(exist_ok=True)
    
    for filename, content in fixes.items():
        filepath = output_dir / filename
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"생성됨: {filepath}")
    
    # 3. 테스트 코드 생성
    logger.info("\n=== 3단계: 테스트 코드 생성 ===")
    test_code = fixer.generate_test_suite()
    test_file = output_dir / 'test_skillmap_scroll.py'
    test_file.write_text(test_code, encoding='utf-8')
    logger.info(f"테스트 파일 생성됨: {test_file}")
    
    # 4. 진단 보고서 저장
    report_file = output_dir / 'diagnosis_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(diagnosis, f, indent=2, ensure_ascii=False)
    logger.info(f"진단 보고서 저장됨: {report_file}")
    
    logger.info("\n=== 완료 ===")
    logger.info(f"모든 수정 파일이 {output_dir} 디렉토리에 생성되었습니다.")
    logger.info("IMPLEMENTATION_GUIDE.md 파일을 참고하여 수정사항을 적용하세요.")
    
    return diagnosis, fixes

if __name__ == "__main__":
    diagnosis, fixes = main()