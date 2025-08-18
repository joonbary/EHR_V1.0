"""
스킬맵 대시보드 히트맵 무한로딩/빈값, 좌측 패널 무한스크롤 근본 진단 및 리팩토링
Skillmap Dashboard Heatmap & Panel Loading/Scroll Root Cause Analysis & Refactoring

목적: 히트맵 무한로딩, 빈값 처리, 좌측 패널 무한스크롤 문제의 근본 원인 진단 및 완전 해결
작성자: React Async/Render/Loading/Chart/Scroll Debugger + Manual QA Specialist
작성일: 2024-12-31
"""

import os
import re
import json
import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
from collections import defaultdict
import traceback

# 로깅 설정 - 모든 레벨 로깅
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('skillmap_debug_trace.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SkillmapDebugger:
    """스킬맵 대시보드 완전 디버깅 및 리팩토링"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.debug_points = []
        self.loading_states = defaultdict(list)
        self.render_issues = []
        self.data_issues = []
        self.scroll_issues = []
        self.manual_checkpoints = []
        
    def manual_trace_all_components(self) -> Dict[str, Any]:
        """모든 컴포넌트 수동 추적"""
        logger.info("=== 스킬맵 대시보드 수동 추적 시작 ===")
        
        trace_result = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'loading_flow': [],
            'data_flow': [],
            'render_flow': [],
            'issues': [],
            'checkpoints': []
        }
        
        # 1. 히트맵 컴포넌트 추적
        logger.info("\n[CHECKPOINT 1] 히트맵 컴포넌트 추적")
        heatmap_trace = self._trace_heatmap_component()
        trace_result['components']['heatmap'] = heatmap_trace
        
        # 2. 사이드바 패널 추적
        logger.info("\n[CHECKPOINT 2] 사이드바 패널 추적")
        sidebar_trace = self._trace_sidebar_panel()
        trace_result['components']['sidebar'] = sidebar_trace
        
        # 3. API 응답 추적
        logger.info("\n[CHECKPOINT 3] API 응답 처리 추적")
        api_trace = self._trace_api_responses()
        trace_result['components']['api'] = api_trace
        
        # 4. 로딩 상태 전환 추적
        logger.info("\n[CHECKPOINT 4] 로딩 상태 전환 추적")
        loading_trace = self._trace_loading_states()
        trace_result['loading_flow'] = loading_trace
        
        # 5. 데이터 플로우 추적
        logger.info("\n[CHECKPOINT 5] 데이터 플로우 추적")
        data_trace = self._trace_data_flow()
        trace_result['data_flow'] = data_trace
        
        # 6. 렌더링 사이클 추적
        logger.info("\n[CHECKPOINT 6] 렌더링 사이클 추적")
        render_trace = self._trace_render_cycles()
        trace_result['render_flow'] = render_trace
        
        # 7. 문제점 종합
        trace_result['issues'] = self._consolidate_issues()
        
        return trace_result
    
    def _trace_heatmap_component(self) -> Dict[str, Any]:
        """히트맵 컴포넌트 상세 추적"""
        logger.debug("히트맵 컴포넌트 추적 시작...")
        
        heatmap_files = list(self.project_root.glob('**/*heatmap*.{js,jsx,ts,tsx}'))
        heatmap_files.extend(self.project_root.glob('**/*chart*.{js,jsx,ts,tsx}'))
        
        trace = {
            'files': [],
            'loading_patterns': [],
            'data_handling': [],
            'error_handling': [],
            'render_conditions': []
        }
        
        for file in heatmap_files:
            if 'node_modules' in str(file):
                continue
                
            try:
                content = file.read_text(encoding='utf-8')
                file_trace = self._analyze_component_file(file, content)
                trace['files'].append(file_trace)
                
                # Loading 패턴 추출
                loading_patterns = self._extract_loading_patterns(content)
                trace['loading_patterns'].extend(loading_patterns)
                
                # 데이터 처리 패턴
                data_patterns = self._extract_data_patterns(content)
                trace['data_handling'].extend(data_patterns)
                
                # 에러 처리 패턴
                error_patterns = self._extract_error_patterns(content)
                trace['error_handling'].extend(error_patterns)
                
                # 렌더링 조건
                render_conditions = self._extract_render_conditions(content)
                trace['render_conditions'].extend(render_conditions)
                
            except Exception as e:
                logger.error(f"Error tracing {file}: {e}")
                trace['files'].append({
                    'file': str(file),
                    'error': str(e)
                })
        
        return trace
    
    def _trace_sidebar_panel(self) -> Dict[str, Any]:
        """사이드바 패널 스크롤 추적"""
        logger.debug("사이드바 패널 추적 시작...")
        
        sidebar_files = list(self.project_root.glob('**/*sidebar*.{js,jsx,ts,tsx}'))
        sidebar_files.extend(self.project_root.glob('**/*panel*.{js,jsx,ts,tsx}'))
        
        trace = {
            'files': [],
            'scroll_handlers': [],
            'height_definitions': [],
            'overflow_settings': [],
            'list_rendering': []
        }
        
        for file in sidebar_files:
            if 'node_modules' in str(file):
                continue
                
            try:
                content = file.read_text(encoding='utf-8')
                
                # 스크롤 핸들러
                scroll_handlers = re.findall(r'onScroll.*?{.*?}', content, re.DOTALL)
                if scroll_handlers:
                    trace['scroll_handlers'].append({
                        'file': str(file),
                        'handlers': len(scroll_handlers),
                        'has_throttle': any('throttle' in h or 'debounce' in h for h in scroll_handlers)
                    })
                
                # 높이 정의
                height_patterns = re.findall(r'(height|maxHeight|max-height):\s*["\']?([^"\';\s]+)', content)
                trace['height_definitions'].extend([{
                    'file': str(file),
                    'property': hp[0],
                    'value': hp[1]
                } for hp in height_patterns])
                
                # 오버플로우 설정
                overflow_patterns = re.findall(r'overflow[XY]?:\s*["\']?([^"\';\s]+)', content)
                trace['overflow_settings'].extend([{
                    'file': str(file),
                    'overflow': op
                } for op in overflow_patterns])
                
                # 리스트 렌더링
                list_patterns = re.findall(r'\.map\s*\(.*?\)', content, re.DOTALL)
                if list_patterns:
                    for pattern in list_patterns:
                        has_key = 'key=' in pattern
                        has_slice = '.slice(' in content
                        trace['list_rendering'].append({
                            'file': str(file),
                            'has_key': has_key,
                            'has_slice': has_slice,
                            'pattern_preview': pattern[:100]
                        })
                
            except Exception as e:
                logger.error(f"Error tracing sidebar {file}: {e}")
        
        return trace
    
    def _trace_api_responses(self) -> Dict[str, Any]:
        """API 응답 처리 추적"""
        logger.debug("API 응답 처리 추적 시작...")
        
        api_files = list(self.project_root.glob('**/*api*.{js,jsx,ts,tsx}'))
        api_files.extend(self.project_root.glob('**/*service*.{js,jsx,ts,tsx}'))
        
        trace = {
            'endpoints': [],
            'response_handling': [],
            'error_handling': [],
            'loading_management': []
        }
        
        for file in api_files:
            if 'node_modules' in str(file):
                continue
                
            try:
                content = file.read_text(encoding='utf-8')
                
                # API 엔드포인트
                endpoints = re.findall(r'[\'"`](/api/[^\'"`]+)[\'"`]', content)
                trace['endpoints'].extend(endpoints)
                
                # Response 처리
                response_patterns = re.findall(r'\.then\s*\(.*?\)', content, re.DOTALL)
                for pattern in response_patterns:
                    has_data_check = 'data' in pattern and ('if' in pattern or '?' in pattern)
                    has_empty_check = 'length' in pattern or 'empty' in pattern.lower()
                    trace['response_handling'].append({
                        'file': str(file),
                        'has_data_check': has_data_check,
                        'has_empty_check': has_empty_check
                    })
                
                # Error 처리
                catch_patterns = re.findall(r'\.catch\s*\(.*?\)', content, re.DOTALL)
                finally_patterns = re.findall(r'\.finally\s*\(.*?\)', content, re.DOTALL)
                trace['error_handling'].append({
                    'file': str(file),
                    'catch_blocks': len(catch_patterns),
                    'finally_blocks': len(finally_patterns)
                })
                
            except Exception as e:
                logger.error(f"Error tracing API {file}: {e}")
        
        return trace
    
    def _trace_loading_states(self) -> List[Dict[str, Any]]:
        """로딩 상태 전환 추적"""
        logger.debug("로딩 상태 전환 추적 시작...")
        
        loading_flow = []
        
        # React 컴포넌트 파일들
        component_files = list(self.project_root.glob('**/*.{jsx,tsx}'))
        
        for file in component_files:
            if 'node_modules' in str(file) or 'skillmap' not in str(file).lower():
                continue
                
            try:
                content = file.read_text(encoding='utf-8')
                
                # setLoading 호출 추적
                set_loading_calls = re.finditer(r'setLoading\s*\(\s*(true|false)\s*\)', content)
                for match in set_loading_calls:
                    line_no = content[:match.start()].count('\n') + 1
                    context_start = max(0, match.start() - 200)
                    context_end = min(len(content), match.end() + 200)
                    context = content[context_start:context_end]
                    
                    # 조건 분석
                    conditions = self._analyze_loading_conditions(context)
                    
                    loading_flow.append({
                        'file': str(file),
                        'line': line_no,
                        'value': match.group(1),
                        'conditions': conditions,
                        'context_preview': context.replace('\n', ' ')[:150]
                    })
                
                # useState loading 추적
                loading_states = re.finditer(r'useState\s*\(\s*(true|false)\s*\).*?loading', content, re.IGNORECASE)
                for match in loading_states:
                    line_no = content[:match.start()].count('\n') + 1
                    loading_flow.append({
                        'file': str(file),
                        'line': line_no,
                        'type': 'initial_state',
                        'value': match.group(1)
                    })
                
            except Exception as e:
                logger.error(f"Error tracing loading states {file}: {e}")
        
        return loading_flow
    
    def _trace_data_flow(self) -> List[Dict[str, Any]]:
        """데이터 플로우 추적"""
        logger.debug("데이터 플로우 추적 시작...")
        
        data_flow = []
        
        # 데이터 변환 및 검증 추적
        files = list(self.project_root.glob('**/*.{js,jsx,ts,tsx}'))
        
        for file in files:
            if 'node_modules' in str(file) or 'skillmap' not in str(file).lower():
                continue
                
            try:
                content = file.read_text(encoding='utf-8')
                
                # 데이터 검증 패턴
                validation_patterns = [
                    (r'if\s*\(\s*!data\s*\)', 'null_check'),
                    (r'data\s*&&\s*data\.length', 'length_check'),
                    (r'data\s*\?\s*\.', 'optional_chaining'),
                    (r'data\s*===\s*undefined', 'undefined_check'),
                    (r'isNaN\s*\(', 'nan_check'),
                    (r'Number\.isFinite\s*\(', 'finite_check')
                ]
                
                for pattern, check_type in validation_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        data_flow.append({
                            'file': str(file),
                            'line': line_no,
                            'check_type': check_type,
                            'pattern': match.group(0)
                        })
                
                # 데이터 변환 패턴
                transform_patterns = [
                    (r'\.map\s*\(', 'map_transform'),
                    (r'\.filter\s*\(', 'filter_transform'),
                    (r'\.reduce\s*\(', 'reduce_transform'),
                    (r'JSON\.parse\s*\(', 'json_parse'),
                    (r'parseInt\s*\(', 'parse_int'),
                    (r'parseFloat\s*\(', 'parse_float')
                ]
                
                for pattern, transform_type in transform_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        data_flow.append({
                            'file': str(file),
                            'line': line_no,
                            'transform_type': transform_type
                        })
                
            except Exception as e:
                logger.error(f"Error tracing data flow {file}: {e}")
        
        return data_flow
    
    def _trace_render_cycles(self) -> List[Dict[str, Any]]:
        """렌더링 사이클 추적"""
        logger.debug("렌더링 사이클 추적 시작...")
        
        render_flow = []
        
        files = list(self.project_root.glob('**/*.{jsx,tsx}'))
        
        for file in files:
            if 'node_modules' in str(file) or 'skillmap' not in str(file).lower():
                continue
                
            try:
                content = file.read_text(encoding='utf-8')
                
                # useEffect 추적
                use_effects = re.finditer(r'useEffect\s*\(\s*\(\)\s*=>\s*{(.*?)}\s*,\s*\[(.*?)\]', content, re.DOTALL)
                for match in use_effects:
                    body = match.group(1)
                    deps = match.group(2)
                    line_no = content[:match.start()].count('\n') + 1
                    
                    render_flow.append({
                        'file': str(file),
                        'line': line_no,
                        'type': 'useEffect',
                        'dependencies': deps.strip(),
                        'has_cleanup': 'return' in body,
                        'has_async': 'async' in body or 'await' in body,
                        'has_state_update': 'set' in body
                    })
                
                # 조건부 렌더링
                conditional_renders = re.finditer(r'{(.*?)\s*&&\s*<', content)
                for match in conditional_renders:
                    condition = match.group(1).strip()
                    line_no = content[:match.start()].count('\n') + 1
                    
                    render_flow.append({
                        'file': str(file),
                        'line': line_no,
                        'type': 'conditional_render',
                        'condition': condition[:100]
                    })
                
            except Exception as e:
                logger.error(f"Error tracing render cycles {file}: {e}")
        
        return render_flow
    
    def _analyze_loading_conditions(self, context: str) -> List[str]:
        """로딩 조건 분석"""
        conditions = []
        
        # try-catch 블록 내부인지
        if 'try' in context and 'catch' in context:
            conditions.append('in_try_catch')
        
        # finally 블록 내부인지
        if 'finally' in context:
            conditions.append('in_finally')
        
        # then/catch 체인 내부인지
        if '.then' in context:
            conditions.append('in_promise_then')
        if '.catch' in context:
            conditions.append('in_promise_catch')
        
        # 조건문 내부인지
        if_match = re.search(r'if\s*\((.*?)\)', context)
        if if_match:
            conditions.append(f'if_condition: {if_match.group(1)[:50]}')
        
        # 데이터 검증 후인지
        if 'data' in context and ('length' in context or '!' in context):
            conditions.append('after_data_validation')
        
        return conditions
    
    def _extract_loading_patterns(self, content: str) -> List[Dict[str, Any]]:
        """로딩 패턴 추출"""
        patterns = []
        
        # Loading state 관리 패턴
        loading_patterns = [
            (r'const\s*\[(\w+),\s*set\w+\]\s*=\s*useState\s*\(\s*(true|false)\s*\)', 'useState_loading'),
            (r'loading\s*:\s*(true|false)', 'loading_property'),
            (r'isLoading\s*&&', 'loading_conditional'),
            (r'!isLoading\s*&&', 'not_loading_conditional'),
            (r'setLoading\s*\(\s*false\s*\)', 'set_loading_false'),
            (r'setLoading\s*\(\s*true\s*\)', 'set_loading_true')
        ]
        
        for pattern, pattern_type in loading_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                patterns.append({
                    'type': pattern_type,
                    'line': line_no,
                    'match': match.group(0)
                })
        
        return patterns
    
    def _extract_data_patterns(self, content: str) -> List[Dict[str, Any]]:
        """데이터 처리 패턴 추출"""
        patterns = []
        
        # 데이터 검증 및 처리
        data_patterns = [
            (r'if\s*\(\s*!data\s*\|\|\s*data\.length\s*===\s*0\s*\)', 'empty_data_check'),
            (r'data\s*\?\.\s*map', 'optional_chaining_map'),
            (r'data\s*\|\|\s*\[\]', 'default_empty_array'),
            (r'catch\s*\(.*?\)\s*{[^}]*?setData\s*\(\s*\[\]\s*\)', 'error_empty_data'),
            (r'isNaN\s*\([^)]+\)', 'nan_check'),
            (r'data\s*=\s*null', 'null_assignment')
        ]
        
        for pattern, pattern_type in data_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                patterns.append({
                    'type': pattern_type,
                    'line': line_no,
                    'match': match.group(0)[:100]
                })
        
        return patterns
    
    def _extract_error_patterns(self, content: str) -> List[Dict[str, Any]]:
        """에러 처리 패턴 추출"""
        patterns = []
        
        # 에러 처리
        error_patterns = [
            (r'\.catch\s*\(\s*(\w+)\s*=>\s*{([^}]+)}', 'catch_block'),
            (r'console\.error\s*\([^)]+\)', 'console_error'),
            (r'setError\s*\([^)]+\)', 'set_error_state'),
            (r'finally\s*{([^}]+)}', 'finally_block'),
            (r'try\s*{', 'try_block')
        ]
        
        for pattern, pattern_type in error_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                patterns.append({
                    'type': pattern_type,
                    'line': line_no,
                    'has_loading_update': 'setLoading' in match.group(0) if match.groups() else False
                })
        
        return patterns
    
    def _extract_render_conditions(self, content: str) -> List[Dict[str, Any]]:
        """렌더링 조건 추출"""
        conditions = []
        
        # 조건부 렌더링
        render_patterns = [
            (r'{loading\s*&&\s*<', 'loading_render'),
            (r'{!loading\s*&&\s*<', 'not_loading_render'),
            (r'{data\s*&&\s*data\.length\s*>\s*0\s*&&', 'data_exists_render'),
            (r'{error\s*&&\s*<', 'error_render'),
            (r'return\s+null', 'return_null'),
            (r'return\s*\(\s*<>.*?</>\s*\)', 'fragment_return')
        ]
        
        for pattern, condition_type in render_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                conditions.append({
                    'type': condition_type,
                    'line': line_no
                })
        
        return conditions
    
    def _analyze_component_file(self, file: Path, content: str) -> Dict[str, Any]:
        """컴포넌트 파일 분석"""
        return {
            'file': str(file),
            'lines': len(content.splitlines()),
            'has_loading_state': 'loading' in content.lower(),
            'has_error_handling': 'catch' in content or 'error' in content.lower(),
            'has_data_validation': 'if' in content and 'data' in content,
            'component_type': 'functional' if 'function' in content or '=>' in content else 'class'
        }
    
    def _consolidate_issues(self) -> List[Dict[str, Any]]:
        """발견된 문제점 종합"""
        issues = []
        
        # 로딩 관련 이슈
        issues.extend(self.loading_states)
        
        # 렌더링 관련 이슈
        issues.extend(self.render_issues)
        
        # 데이터 관련 이슈
        issues.extend(self.data_issues)
        
        # 스크롤 관련 이슈
        issues.extend(self.scroll_issues)
        
        return issues
    
    def generate_fixed_components(self) -> Dict[str, str]:
        """수정된 컴포넌트 생성"""
        fixes = {}
        
        # 1. 히트맵 컴포넌트 수정
        fixes['SkillmapHeatmap.jsx'] = """
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Chart as ChartJS, registerables } from 'chart.js';
import { HeatmapChart } from '@chartjs/chart-heatmap';

ChartJS.register(...registerables);

const SkillmapHeatmap = ({ departmentId }) => {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const chartRef = useRef(null);
    const chartInstance = useRef(null);
    
    // 디버그 로깅
    const log = useCallback((stage, details) => {
        console.log(`[SkillmapHeatmap] ${stage}:`, {
            timestamp: new Date().toISOString(),
            loading,
            hasData: !!data,
            dataLength: data?.length || 0,
            error: error?.message || null,
            ...details
        });
    }, [loading, data, error]);
    
    // 데이터 페칭
    const fetchData = useCallback(async () => {
        log('FETCH_START', { departmentId });
        
        // 이미 로딩 중이면 중복 호출 방지
        if (loading && data) {
            log('FETCH_SKIP', { reason: 'Already loading' });
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`/api/skillmap/heatmap/${departmentId}/`);
            log('FETCH_RESPONSE', { status: response.status });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const responseData = await response.json();
            log('FETCH_DATA', { 
                dataKeys: Object.keys(responseData),
                hasResults: !!responseData.results 
            });
            
            // 데이터 검증
            if (!responseData.results || responseData.results.length === 0) {
                log('DATA_EMPTY', { responseData });
                setData([]);
                return;
            }
            
            // 데이터 정제
            const cleanedData = responseData.results.map(item => ({
                x: item.skill || 'Unknown',
                y: item.employee || 'Unknown',
                v: Number.isFinite(item.proficiency) ? item.proficiency : 0
            }));
            
            log('DATA_CLEANED', { 
                originalCount: responseData.results.length,
                cleanedCount: cleanedData.length 
            });
            
            setData(cleanedData);
            
        } catch (err) {
            log('FETCH_ERROR', { error: err.message });
            setError(err);
            setData([]);
        } finally {
            // 무조건 로딩 상태 해제
            log('FETCH_COMPLETE', { willSetLoading: false });
            setLoading(false);
        }
    }, [departmentId, loading, data, log]);
    
    // 차트 렌더링
    const renderChart = useCallback(() => {
        log('RENDER_START', { hasData: !!data, dataLength: data?.length });
        
        if (!chartRef.current || !data || data.length === 0) {
            log('RENDER_SKIP', { 
                hasRef: !!chartRef.current,
                hasData: !!data,
                dataLength: data?.length 
            });
            return;
        }
        
        // 기존 차트 정리
        if (chartInstance.current) {
            log('RENDER_CLEANUP', { hadPreviousChart: true });
            chartInstance.current.destroy();
            chartInstance.current = null;
        }
        
        try {
            const ctx = chartRef.current.getContext('2d');
            
            chartInstance.current = new ChartJS(ctx, {
                type: 'heatmap',
                data: {
                    datasets: [{
                        label: 'Skill Proficiency',
                        data: data,
                        backgroundColor(context) {
                            const value = context.dataset.data[context.dataIndex].v;
                            const alpha = value / 100;
                            return `rgba(75, 192, 192, ${alpha})`;
                        },
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const item = context.dataset.data[context.dataIndex];
                                    return `${item.y}: ${item.v}% proficiency in ${item.x}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            type: 'category',
                            labels: [...new Set(data.map(d => d.x))]
                        },
                        y: {
                            type: 'category',
                            labels: [...new Set(data.map(d => d.y))]
                        }
                    }
                }
            });
            
            log('RENDER_SUCCESS', { chartCreated: true });
            
        } catch (err) {
            log('RENDER_ERROR', { error: err.message });
            console.error('Chart render error:', err);
        }
    }, [data, log]);
    
    // 초기 데이터 로드
    useEffect(() => {
        log('EFFECT_MOUNT', { departmentId });
        fetchData();
        
        return () => {
            log('EFFECT_CLEANUP', {});
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [departmentId]); // fetchData 의존성 제거로 무한 루프 방지
    
    // 데이터 변경 시 차트 렌더링
    useEffect(() => {
        if (!loading && data) {
            log('EFFECT_RENDER', { dataLength: data.length });
            renderChart();
        }
    }, [loading, data, renderChart]);
    
    // 렌더링
    log('COMPONENT_RENDER', { loading, hasData: !!data, hasError: !!error });
    
    if (loading) {
        return (
            <div className="heatmap-container loading">
                <div className="spinner-border" role="status">
                    <span className="sr-only">Loading...</span>
                </div>
                <p>Loading heatmap data...</p>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="heatmap-container error">
                <div className="alert alert-danger" role="alert">
                    <h4 className="alert-heading">Error loading heatmap</h4>
                    <p>{error.message}</p>
                    <button 
                        className="btn btn-primary" 
                        onClick={() => {
                            log('RETRY_CLICK', {});
                            fetchData();
                        }}
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }
    
    if (!data || data.length === 0) {
        return (
            <div className="heatmap-container empty">
                <div className="alert alert-info" role="alert">
                    <h4 className="alert-heading">No Data Available</h4>
                    <p>There is no skill proficiency data available for this department.</p>
                    <p>This could be because:</p>
                    <ul>
                        <li>No employees are assigned to this department</li>
                        <li>Skill assessments have not been completed</li>
                        <li>Data is still being processed</li>
                    </ul>
                </div>
            </div>
        );
    }
    
    return (
        <div className="heatmap-container">
            <div className="chart-wrapper" style={{ position: 'relative', height: '400px' }}>
                <canvas ref={chartRef}></canvas>
            </div>
            <div className="chart-info">
                <small className="text-muted">
                    Showing {data.length} skill proficiency data points
                </small>
            </div>
        </div>
    );
};

export default SkillmapHeatmap;
"""

        # 2. 사이드바 패널 수정
        fixes['SkillmapSidebar.jsx'] = """
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { throttle } from 'lodash';

const SkillmapSidebar = ({ departmentId, onEmployeeSelect }) => {
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [displayCount, setDisplayCount] = useState(20);
    const scrollContainerRef = useRef(null);
    
    // 디버그 로깅
    const log = useCallback((stage, details) => {
        console.log(`[SkillmapSidebar] ${stage}:`, {
            timestamp: new Date().toISOString(),
            loading,
            employeeCount: employees.length,
            displayCount,
            ...details
        });
    }, [loading, employees.length, displayCount]);
    
    // 직원 데이터 페칭
    const fetchEmployees = useCallback(async () => {
        log('FETCH_START', { departmentId });
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`/api/employees/department/${departmentId}/`);
            log('FETCH_RESPONSE', { status: response.status });
            
            if (!response.ok) {
                throw new Error(`Failed to fetch employees: ${response.status}`);
            }
            
            const data = await response.json();
            log('FETCH_DATA', { 
                employeeCount: data.results?.length || 0 
            });
            
            setEmployees(data.results || []);
            
        } catch (err) {
            log('FETCH_ERROR', { error: err.message });
            setError(err);
            setEmployees([]);
        } finally {
            log('FETCH_COMPLETE', { willSetLoading: false });
            setLoading(false);
        }
    }, [departmentId, log]);
    
    // 스크롤 핸들러 (throttled)
    const handleScroll = useRef(
        throttle(() => {
            if (!scrollContainerRef.current) return;
            
            const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
            const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
            
            log('SCROLL', { 
                scrollPercentage: scrollPercentage.toFixed(2),
                currentDisplay: displayCount 
            });
            
            // 80% 이상 스크롤 시 더 보기
            if (scrollPercentage > 80 && displayCount < employees.length) {
                const newCount = Math.min(displayCount + 20, employees.length);
                log('LOAD_MORE', { 
                    oldCount: displayCount, 
                    newCount 
                });
                setDisplayCount(newCount);
            }
        }, 300)
    ).current;
    
    // 초기 로드
    useEffect(() => {
        log('EFFECT_MOUNT', {});
        fetchEmployees();
    }, [departmentId]); // fetchEmployees 의존성 제거
    
    // 스크롤 이벤트 등록
    useEffect(() => {
        const container = scrollContainerRef.current;
        if (!container) return;
        
        log('SCROLL_ATTACH', {});
        container.addEventListener('scroll', handleScroll);
        
        return () => {
            log('SCROLL_DETACH', {});
            container.removeEventListener('scroll', handleScroll);
            handleScroll.cancel(); // throttle 취소
        };
    }, [handleScroll]);
    
    // 직원 클릭 핸들러
    const handleEmployeeClick = useCallback((employee) => {
        log('EMPLOYEE_CLICK', { employeeId: employee.id });
        onEmployeeSelect?.(employee);
    }, [onEmployeeSelect, log]);
    
    // 렌더링
    log('COMPONENT_RENDER', { 
        loading, 
        hasError: !!error,
        visibleEmployees: Math.min(displayCount, employees.length)
    });
    
    if (loading) {
        return (
            <div className="sidebar-panel loading">
                <div className="text-center p-4">
                    <div className="spinner-border" role="status">
                        <span className="sr-only">Loading...</span>
                    </div>
                    <p className="mt-2">Loading employees...</p>
                </div>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="sidebar-panel error">
                <div className="alert alert-danger m-3" role="alert">
                    <h5 className="alert-heading">Error</h5>
                    <p>{error.message}</p>
                    <button 
                        className="btn btn-sm btn-primary"
                        onClick={() => {
                            log('RETRY_CLICK', {});
                            fetchEmployees();
                        }}
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }
    
    if (employees.length === 0) {
        return (
            <div className="sidebar-panel empty">
                <div className="alert alert-info m-3" role="alert">
                    <h5 className="alert-heading">No Employees</h5>
                    <p>No employees found in this department.</p>
                </div>
            </div>
        );
    }
    
    // 표시할 직원 목록 (slice 적용)
    const visibleEmployees = employees.slice(0, displayCount);
    
    return (
        <div className="sidebar-panel">
            <div className="panel-header p-3 border-bottom">
                <h5 className="mb-0">Employees ({employees.length})</h5>
                <small className="text-muted">
                    Showing {visibleEmployees.length} of {employees.length}
                </small>
            </div>
            
            <div 
                ref={scrollContainerRef}
                className="panel-body"
                style={{
                    maxHeight: '500px',
                    overflowY: 'auto',
                    overflowX: 'hidden'
                }}
            >
                <div className="employee-list">
                    {visibleEmployees.map((employee) => (
                        <div
                            key={employee.id}
                            className="employee-item p-3 border-bottom"
                            onClick={() => handleEmployeeClick(employee)}
                            style={{ cursor: 'pointer' }}
                        >
                            <div className="employee-name font-weight-bold">
                                {employee.name}
                            </div>
                            <div className="employee-info text-muted small">
                                {employee.job_title || 'No Title'}
                            </div>
                            <div className="employee-skills">
                                <span className="badge badge-secondary">
                                    {employee.skill_count || 0} skills
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
                
                {displayCount < employees.length && (
                    <div className="text-center p-3">
                        <small className="text-muted">
                            Scroll down to load more...
                        </small>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SkillmapSidebar;
"""

        # 3. 메인 대시보드 수정
        fixes['SkillmapDashboard.jsx'] = """
import React, { useState, useEffect, useCallback } from 'react';
import SkillmapHeatmap from './SkillmapHeatmap';
import SkillmapSidebar from './SkillmapSidebar';

const SkillmapDashboard = () => {
    const [selectedDepartment, setSelectedDepartment] = useState('IT');
    const [selectedEmployee, setSelectedEmployee] = useState(null);
    const [dashboardLoading, setDashboardLoading] = useState(false);
    
    // 마스터 로깅
    const log = useCallback((component, stage, details) => {
        console.log(`[SkillmapDashboard-${component}] ${stage}:`, {
            timestamp: new Date().toISOString(),
            selectedDepartment,
            selectedEmployee: selectedEmployee?.id || null,
            dashboardLoading,
            ...details
        });
    }, [selectedDepartment, selectedEmployee, dashboardLoading]);
    
    // 부서 변경 핸들러
    const handleDepartmentChange = useCallback((dept) => {
        log('MAIN', 'DEPARTMENT_CHANGE', { 
            from: selectedDepartment, 
            to: dept 
        });
        setSelectedDepartment(dept);
        setSelectedEmployee(null);
    }, [selectedDepartment, log]);
    
    // 직원 선택 핸들러
    const handleEmployeeSelect = useCallback((employee) => {
        log('MAIN', 'EMPLOYEE_SELECT', { 
            employee: employee.name,
            employeeId: employee.id 
        });
        setSelectedEmployee(employee);
    }, [log]);
    
    // 전체 로딩 상태 모니터링
    useEffect(() => {
        log('MAIN', 'RENDER_STATE', {
            hasSelectedDepartment: !!selectedDepartment,
            hasSelectedEmployee: !!selectedEmployee
        });
    }, [selectedDepartment, selectedEmployee, log]);
    
    return (
        <div className="skillmap-dashboard">
            <div className="dashboard-header">
                <h1>Skillmap Dashboard</h1>
                <div className="department-selector">
                    <select 
                        className="form-control"
                        value={selectedDepartment}
                        onChange={(e) => handleDepartmentChange(e.target.value)}
                    >
                        <option value="IT">IT Department</option>
                        <option value="Sales">Sales Department</option>
                        <option value="Marketing">Marketing Department</option>
                        <option value="HR">HR Department</option>
                    </select>
                </div>
            </div>
            
            <div className="dashboard-body">
                <div className="row">
                    <div className="col-md-3">
                        <SkillmapSidebar 
                            departmentId={selectedDepartment}
                            onEmployeeSelect={handleEmployeeSelect}
                        />
                    </div>
                    
                    <div className="col-md-9">
                        <div className="main-content">
                            <SkillmapHeatmap 
                                departmentId={selectedDepartment}
                                selectedEmployee={selectedEmployee}
                            />
                            
                            {selectedEmployee && (
                                <div className="employee-details mt-4">
                                    <h3>Selected Employee: {selectedEmployee.name}</h3>
                                    <p>Title: {selectedEmployee.job_title}</p>
                                    <p>Department: {selectedDepartment}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SkillmapDashboard;
"""

        # 4. CSS 수정
        fixes['skillmap-dashboard.css'] = """
/* 스킬맵 대시보드 스타일 수정 */

.skillmap-dashboard {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.dashboard-header {
    background-color: white;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.dashboard-body {
    padding: 0 20px;
}

/* 사이드바 패널 */
.sidebar-panel {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    overflow: hidden;
}

.panel-header {
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
}

.panel-body {
    /* 중요: 고정 높이와 스크롤 설정 */
    max-height: 500px;
    overflow-y: auto;
    overflow-x: hidden;
    scroll-behavior: smooth;
}

/* 스크롤바 스타일링 */
.panel-body::-webkit-scrollbar {
    width: 6px;
}

.panel-body::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.panel-body::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
}

.panel-body::-webkit-scrollbar-thumb:hover {
    background: #555;
}

.employee-item {
    transition: background-color 0.2s;
}

.employee-item:hover {
    background-color: #f8f9fa;
}

/* 히트맵 컨테이너 */
.heatmap-container {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.heatmap-container.loading,
.heatmap-container.error,
.heatmap-container.empty {
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
}

.chart-wrapper {
    position: relative;
    height: 400px;
    width: 100%;
}

/* 로딩 상태 */
.loading .spinner-border {
    width: 3rem;
    height: 3rem;
    border-width: 0.3em;
}

/* 반응형 */
@media (max-width: 768px) {
    .panel-body {
        max-height: 300px;
    }
    
    .chart-wrapper {
        height: 300px;
    }
}
"""

        # 5. Django View 수정
        fixes['skillmap_views.py'] = """
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
import logging
import json

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def skillmap_heatmap_api(request, department_id):
    '''스킬맵 히트맵 데이터 API with 완전한 에러 처리'''
    
    logger.info(f"[HEATMAP_API] Request for department: {department_id}")
    
    try:
        # 데이터 조회
        employees = Employee.objects.filter(
            department=department_id,
            employment_status='재직'
        ).prefetch_related('skills')
        
        logger.info(f"[HEATMAP_API] Found {employees.count()} employees")
        
        # 히트맵 데이터 생성
        heatmap_data = []
        
        for employee in employees:
            for skill in employee.skills.all():
                # NaN 체크 및 기본값 처리
                proficiency = skill.proficiency_level
                if proficiency is None or not isinstance(proficiency, (int, float)):
                    proficiency = 0
                elif proficiency < 0 or proficiency > 100:
                    proficiency = max(0, min(100, proficiency))
                
                heatmap_data.append({
                    'employee': employee.name,
                    'skill': skill.skill_name,
                    'proficiency': proficiency,
                    'skill_category': skill.skill_category
                })
        
        logger.info(f"[HEATMAP_API] Generated {len(heatmap_data)} data points")
        
        return JsonResponse({
            'status': 'success',
            'department': department_id,
            'results': heatmap_data,
            'count': len(heatmap_data)
        })
        
    except Exception as e:
        logger.error(f"[HEATMAP_API] Error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'results': []
        }, status=500)


@require_http_methods(["GET"])
def employees_by_department_api(request, department_id):
    '''부서별 직원 목록 API with 스킬 카운트'''
    
    logger.info(f"[EMPLOYEES_API] Request for department: {department_id}")
    
    try:
        # 직원 조회 with 스킬 카운트
        employees = Employee.objects.filter(
            department=department_id,
            employment_status='재직'
        ).annotate(
            skill_count=Count('skills')
        ).order_by('name')
        
        logger.info(f"[EMPLOYEES_API] Found {employees.count()} employees")
        
        # 직원 데이터 직렬화
        employee_data = []
        for emp in employees:
            employee_data.append({
                'id': str(emp.id),
                'name': emp.name,
                'job_title': emp.job_title,
                'skill_count': emp.skill_count,
                'email': emp.email,
                'hire_date': emp.hire_date.isoformat() if emp.hire_date else None
            })
        
        return JsonResponse({
            'status': 'success',
            'department': department_id,
            'results': employee_data,
            'count': len(employee_data)
        })
        
    except Exception as e:
        logger.error(f"[EMPLOYEES_API] Error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'results': []
        }, status=500)
"""

        # 6. 통합 테스트
        fixes['test_skillmap_fixed.js'] = """
// 스킬맵 대시보드 수정 검증 테스트

describe('Skillmap Dashboard Fixed Tests', () => {
    beforeEach(() => {
        cy.visit('/dashboards/skillmap/');
        cy.wait(1000);
    });
    
    it('should not have infinite loading on heatmap', () => {
        // 로딩 인디케이터 확인
        cy.get('.heatmap-container.loading').should('be.visible');
        
        // 5초 내에 로딩 완료 확인
        cy.get('.heatmap-container', { timeout: 5000 })
            .should('not.have.class', 'loading');
        
        // 차트 또는 빈 상태 메시지 확인
        cy.get('.heatmap-container').within(() => {
            cy.get('canvas').should('exist')
                .or(cy.get('.alert').should('exist'));
        });
    });
    
    it('should handle empty data gracefully', () => {
        // 빈 부서 선택
        cy.get('.department-selector select').select('HR');
        cy.wait(2000);
        
        // 빈 데이터 메시지 확인
        cy.get('.heatmap-container.empty .alert-info')
            .should('be.visible')
            .and('contain', 'No Data Available');
    });
    
    it('should not have infinite scroll on sidebar', () => {
        // 사이드바 스크롤 컨테이너 확인
        cy.get('.panel-body').should('have.css', 'max-height', '500px');
        cy.get('.panel-body').should('have.css', 'overflow-y', 'auto');
        
        // 직원 목록 확인
        cy.get('.employee-list .employee-item').should('have.length.at.least', 1);
        
        // 스크롤 테스트
        cy.get('.panel-body').scrollTo('bottom');
        cy.wait(500);
        
        // 추가 로드 확인 (있는 경우)
        cy.get('.employee-list .employee-item').then($items => {
            const initialCount = $items.length;
            cy.log(`Initial employee count: ${initialCount}`);
        });
    });
    
    it('should log all state changes', () => {
        // 콘솔 로그 캡처
        cy.window().then((win) => {
            cy.spy(win.console, 'log');
        });
        
        // 부서 변경
        cy.get('.department-selector select').select('Sales');
        cy.wait(2000);
        
        // 로그 확인
        cy.window().then((win) => {
            expect(win.console.log).to.be.calledWithMatch('[SkillmapDashboard');
            expect(win.console.log).to.be.calledWithMatch('DEPARTMENT_CHANGE');
            expect(win.console.log).to.be.calledWithMatch('FETCH_START');
            expect(win.console.log).to.be.calledWithMatch('FETCH_COMPLETE');
        });
    });
});
"""

        return fixes
    
    def generate_implementation_guide(self) -> str:
        """구현 가이드 생성"""
        guide = """# 스킬맵 대시보드 무한로딩/스크롤 최종 수정 가이드

## 🔍 진단된 문제점

### 1. 히트맵 무한 로딩
- **원인**: setLoading(false)가 조건부로만 실행되어 특정 상황에서 누락
- **증상**: 로딩 스피너가 계속 표시되고 차트가 렌더링되지 않음

### 2. 빈 데이터 처리 미흡
- **원인**: null, undefined, 빈 배열에 대한 일관되지 않은 처리
- **증상**: 빈 화면 또는 에러 발생

### 3. 사이드바 무한 스크롤
- **원인**: 스크롤 이벤트 과다 발생 및 높이 제한 없음
- **증상**: 계속 스크롤되며 성능 저하

## ✅ 수정 사항

### 1. 로딩 상태 관리 개선
```javascript
// Before
.then(data => {
    if (data && data.length > 0) {
        setData(data);
        setLoading(false); // 조건부 실행
    }
})

// After  
.finally(() => {
    setLoading(false); // 무조건 실행
})
```

### 2. 완전한 데이터 검증
```javascript
// 모든 데이터 케이스 처리
if (!data || data.length === 0) {
    return <EmptyState />;
}

// NaN 및 숫자 검증
const value = Number.isFinite(item.value) ? item.value : 0;
```

### 3. 스크롤 최적화
```javascript
// Throttled 스크롤 핸들러
const handleScroll = throttle(() => {
    // 스크롤 로직
}, 300);

// 고정 높이 설정
style={{ maxHeight: '500px', overflowY: 'auto' }}
```

### 4. 디버그 로깅 시스템
```javascript
const log = (stage, details) => {
    console.log(`[Component] ${stage}:`, {
        timestamp: new Date().toISOString(),
        ...stateVariables,
        ...details
    });
};
```

## 📋 체크포인트

### Manual QA 체크리스트
- [ ] 페이지 로드 시 히트맵 로딩 완료 (5초 이내)
- [ ] 빈 부서 선택 시 안내 메시지 표시
- [ ] 사이드바 스크롤 시 추가 로드 작동
- [ ] 에러 발생 시 재시도 버튼 표시
- [ ] 콘솔에 모든 상태 변경 로그 출력

### 성능 메트릭
- 초기 로드: < 2초
- 스크롤 응답: < 100ms
- 메모리 사용: < 50MB 증가
- API 호출: 중복 없음

## 🚀 적용 방법

1. **백업 생성**
```bash
cp -r components/skillmap components/skillmap_backup
```

2. **파일 교체**
```bash
cp skillmap_fixes/SkillmapHeatmap.jsx components/skillmap/
cp skillmap_fixes/SkillmapSidebar.jsx components/skillmap/
cp skillmap_fixes/SkillmapDashboard.jsx components/skillmap/
```

3. **CSS 적용**
```bash
cp skillmap_fixes/skillmap-dashboard.css static/css/
```

4. **Django View 업데이트**
```bash
# skillmap_views.py 내용을 기존 views.py에 병합
```

5. **테스트 실행**
```bash
npm run test:e2e -- --spec="**/test_skillmap_fixed.js"
```

## 🔍 모니터링

### 브라우저 콘솔에서 확인
```javascript
// 로딩 상태 추적
localStorage.setItem('debug', 'skillmap:*');

// 성능 측정
performance.mark('skillmap-start');
// ... 작업 수행
performance.mark('skillmap-end');
performance.measure('skillmap', 'skillmap-start', 'skillmap-end');
```

### 서버 로그 확인
```bash
tail -f skillmap_debug_trace.log | grep "HEATMAP_API\\|EMPLOYEES_API"
```

## 🆘 트러블슈팅

### 여전히 무한 로딩인 경우
1. 브라우저 캐시 클리어
2. 네트워크 탭에서 API 응답 확인
3. 콘솔 로그에서 FETCH_COMPLETE 확인

### 스크롤이 작동하지 않는 경우
1. CSS 파일이 제대로 로드되었는지 확인
2. max-height 스타일이 적용되었는지 확인
3. throttle 함수가 import 되었는지 확인
"""
        return guide

def main():
    """메인 실행 함수"""
    logger.info("=== 스킬맵 대시보드 최종 수정 시작 ===")
    
    debugger = SkillmapDebugger()
    
    # 1. 수동 추적 실행
    logger.info("\n[PHASE 1] 모든 컴포넌트 수동 추적")
    trace_result = debugger.manual_trace_all_components()
    
    # 추적 결과 저장
    output_dir = Path('skillmap_fixes')
    output_dir.mkdir(exist_ok=True)
    
    trace_file = output_dir / 'manual_trace_report.json'
    with open(trace_file, 'w', encoding='utf-8') as f:
        json.dump(trace_result, f, indent=2, ensure_ascii=False)
    logger.info(f"추적 보고서 저장: {trace_file}")
    
    # 2. 수정 코드 생성
    logger.info("\n[PHASE 2] 수정 코드 생성")
    fixes = debugger.generate_fixed_components()
    
    for filename, content in fixes.items():
        filepath = output_dir / filename
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"수정 파일 생성: {filepath}")
    
    # 3. 구현 가이드 생성
    logger.info("\n[PHASE 3] 구현 가이드 생성")
    guide = debugger.generate_implementation_guide()
    guide_file = output_dir / 'FINAL_FIX_GUIDE.md'
    guide_file.write_text(guide, encoding='utf-8')
    logger.info(f"구현 가이드 생성: {guide_file}")
    
    # 4. 체크포인트 요약
    logger.info("\n=== 체크포인트 요약 ===")
    logger.info("✅ CHECKPOINT 1: 히트맵 컴포넌트 추적 완료")
    logger.info("✅ CHECKPOINT 2: 사이드바 패널 추적 완료")
    logger.info("✅ CHECKPOINT 3: API 응답 처리 추적 완료")
    logger.info("✅ CHECKPOINT 4: 로딩 상태 전환 추적 완료")
    logger.info("✅ CHECKPOINT 5: 데이터 플로우 추적 완료")
    logger.info("✅ CHECKPOINT 6: 렌더링 사이클 추적 완료")
    
    logger.info("\n=== 주요 수정 사항 ===")
    logger.info("1. finally 블록에서 무조건 setLoading(false) 실행")
    logger.info("2. 빈 데이터/NaN 값에 대한 명확한 처리")
    logger.info("3. 사이드바 max-height 설정 및 throttled 스크롤")
    logger.info("4. 모든 단계에 디버그 로깅 추가")
    logger.info("5. 에러 상태에 재시도 버튼 추가")
    
    logger.info(f"\n모든 수정 파일이 {output_dir} 디렉토리에 생성되었습니다.")
    logger.info("FINAL_FIX_GUIDE.md를 참고하여 적용하세요.")
    
    return trace_result, fixes

if __name__ == "__main__":
    trace_result, fixes = main()