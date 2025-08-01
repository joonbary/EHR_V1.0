#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django 템플릿 및 뷰 통합 예제
기존 EHR 시스템에 새로운 UX를 통합하는 방법
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from job_profiles.models import JobCategory, JobType, JobRole, JobProfile


class JobTreeView(LoginRequiredMixin, TemplateView):
    """직무 체계도 메인 뷰"""
    template_name = 'job_profiles/job_tree.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 기본 통계 정보
        context.update({
            'total_categories': JobCategory.objects.filter(is_active=True).count(),
            'total_job_types': JobType.objects.filter(is_active=True).count(),
            'total_job_roles': JobRole.objects.filter(is_active=True).count(),
            'total_profiles': JobProfile.objects.filter(is_active=True).count(),
            'page_title': '직무 체계도',
            'page_description': 'OK금융그룹 전체 직무를 한눈에 살펴보세요'
        })
        
        return context


def generate_django_template():
    """Django 템플릿 생성"""
    
    return """
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/JobTreeVisualization.css' %}">
<!-- Ant Design CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/antd@5.0.0/dist/reset.css">
<!-- Font Awesome Icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
{% endblock %}

{% block content %}
<div class="page-header">
    <div class="container-fluid">
        <div class="row align-items-center">
            <div class="col">
                <nav aria-label="breadcrumb">
                    <ol class="breadcrumb">
                        <li class="breadcrumb-item"><a href="{% url 'dashboard' %}">홈</a></li>
                        <li class="breadcrumb-item"><a href="{% url 'job_profiles:list' %}">직무관리</a></li>
                        <li class="breadcrumb-item active" aria-current="page">직무 체계도</li>
                    </ol>
                </nav>
                <h1 class="page-title">
                    <i class="fas fa-sitemap me-2"></i>
                    {{ page_title }}
                </h1>
                <p class="page-subtitle text-muted">{{ page_description }}</p>
            </div>
            <div class="col-auto">
                <div class="btn-toolbar" role="toolbar">
                    <div class="btn-group me-2">
                        <a href="{% url 'job_profiles:list' %}" class="btn btn-outline-primary">
                            <i class="fas fa-list me-1"></i>
                            목록보기
                        </a>
                        <a href="{% url 'job_profiles:add' %}" class="btn btn-primary">
                            <i class="fas fa-plus me-1"></i>
                            직무 추가
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 통계 카드 -->
<div class="container-fluid mb-4">
    <div class="row">
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-primary shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                직군</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ total_categories }}개</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-layer-group fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-success shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                직종</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ total_job_types }}개</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-folder fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-info shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                직무</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ total_job_roles }}개</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-user-cog fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-warning shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                직무기술서</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ total_profiles }}개</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-file-alt fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- React/Vue 컴포넌트가 마운트될 영역 -->
<div id="job-tree-app" class="container-fluid">
    <!-- 로딩 스피너 -->
    <div id="loading-spinner" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">직무 체계도를 불러오는 중...</p>
    </div>
</div>

<!-- 모달 영역 (직무 상세 정보용) -->
<div class="modal fade" id="jobDetailModal" tabindex="-1" aria-labelledby="jobDetailModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="jobDetailModalLabel">직무 상세 정보</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" id="jobDetailContent">
                <!-- 상세 정보가 동적으로 로드됩니다 -->
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<!-- React/Vue 라이브러리 -->
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/antd@5.0.0/dist/antd.min.js"></script>

<!-- 또는 Vue.js 사용 시 -->
<!--
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script src="https://unpkg.com/ant-design-vue@4.0.0/dist/antd.min.js"></script>
-->

<!-- D3.js (맵 뷰용) -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<!-- 커스텀 스크립트 -->
<script>
// Django에서 전달받은 데이터
const djangoContext = {
    csrfToken: '{{ csrf_token }}',
    userId: '{{ request.user.id }}',
    isAuthenticated: {{ request.user.is_authenticated|yesno:"true,false" }},
    apiBaseUrl: '/api/',
    staticUrl: '{% static "" %}',
    totalStats: {
        categories: {{ total_categories }},
        jobTypes: {{ total_job_types }},
        jobRoles: {{ total_job_roles }},
        profiles: {{ total_profiles }}
    }
};

// API 헬퍼 함수
const api = {
    get: async (url) => {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': djangoContext.csrfToken
            }
        });
        return response.json();
    },
    
    post: async (url, data) => {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': djangoContext.csrfToken
            },
            body: JSON.stringify(data)
        });
        return response.json();
    }
};

// 직무 트리 데이터 로드
async function loadJobTreeData() {
    try {
        const response = await api.get('/api/job-tree/');
        if (response.success) {
            return response.data;
        } else {
            throw new Error(response.error);
        }
    } catch (error) {
        console.error('직무 트리 데이터 로드 실패:', error);
        showError('직무 트리 데이터를 불러오는데 실패했습니다.');
        return null;
    }
}

// 직무 상세 정보 로드
async function loadJobDetail(jobRoleId) {
    try {
        const response = await api.get(`/api/job-profiles/${jobRoleId}/`);
        if (response.success) {
            return response.data;
        } else {
            throw new Error(response.error);
        }
    } catch (error) {
        console.error('직무 상세 정보 로드 실패:', error);
        showError('직무 상세 정보를 불러오는데 실패했습니다.');
        return null;
    }
}

// 에러 표시 함수
function showError(message) {
    const errorHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.getElementById('job-tree-app').innerHTML = errorHtml;
}

// React 컴포넌트 마운트 (React 사용 시)
async function initializeReactApp() {
    const jobTreeData = await loadJobTreeData();
    if (!jobTreeData) return;
    
    // 로딩 스피너 제거
    document.getElementById('loading-spinner').style.display = 'none';
    
    // React 컴포넌트 마운트
    const JobTreeVisualization = window.JobTreeVisualization; // 번들된 컴포넌트
    
    ReactDOM.render(
        React.createElement(JobTreeVisualization, {
            jobData: jobTreeData,
            onJobSelect: handleJobSelect
        }),
        document.getElementById('job-tree-app')
    );
}

// Vue 앱 초기화 (Vue 사용 시)
async function initializeVueApp() {
    const jobTreeData = await loadJobTreeData();
    if (!jobTreeData) return;
    
    const { createApp } = Vue;
    
    createApp({
        data() {
            return {
                jobData: jobTreeData,
                loading: false
            };
        },
        methods: {
            handleJobSelect(job) {
                handleJobSelect(job);
            }
        },
        template: `
            <job-tree-visualization 
                :job-data="jobData"
                @job-select="handleJobSelect"
                v-if="!loading"
            />
        `
    }).mount('#job-tree-app');
}

// 직무 선택 핸들러
async function handleJobSelect(job) {
    if (job.type === 'job_role') {
        const jobDetail = await loadJobDetail(job.metadata.job_role_id);
        if (jobDetail) {
            showJobDetailModal(jobDetail);
        }
    }
}

// 직무 상세 정보 모달 표시
function showJobDetailModal(jobDetail) {
    const modal = new bootstrap.Modal(document.getElementById('jobDetailModal'));
    const modalTitle = document.getElementById('jobDetailModalLabel');
    const modalContent = document.getElementById('jobDetailContent');
    
    modalTitle.textContent = `${jobDetail.name} 상세 정보`;
    
    // 상세 정보 HTML 생성
    const detailHtml = generateJobDetailHtml(jobDetail);
    modalContent.innerHTML = detailHtml;
    
    modal.show();
}

// 직무 상세 정보 HTML 생성
function generateJobDetailHtml(jobDetail) {
    return `
        <div class="job-detail-content">
            <!-- 기본 정보 -->
            <div class="row mb-4">
                <div class="col-md-8">
                    <h4>${jobDetail.name}</h4>
                    <p class="text-muted">${jobDetail.description}</p>
                    <div class="d-flex gap-2">
                        <span class="badge bg-primary">${jobDetail.category.name}</span>
                        <span class="badge bg-secondary">${jobDetail.job_type.name}</span>
                    </div>
                </div>
                <div class="col-md-4 text-end">
                    <div class="btn-group">
                        <button class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-heart"></i> 관심직무
                        </button>
                        <button class="btn btn-outline-secondary btn-sm">
                            <i class="fas fa-share"></i> 공유
                        </button>
                    </div>
                </div>
            </div>
            
            ${jobDetail.profile ? `
            <!-- 역할 및 책임 -->
            <div class="mb-4">
                <h5><i class="fas fa-tasks me-2 text-primary"></i>핵심 역할 및 책임</h5>
                <div class="card">
                    <div class="card-body">
                        <pre class="mb-0">${jobDetail.profile.role_responsibility}</pre>
                    </div>
                </div>
            </div>
            
            <!-- 자격 요건 -->
            <div class="mb-4">
                <h5><i class="fas fa-check-circle me-2 text-success"></i>자격 요건</h5>
                <div class="card">
                    <div class="card-body">
                        <pre class="mb-0">${jobDetail.profile.qualification}</pre>
                    </div>
                </div>
            </div>
            
            <!-- 필요 역량 -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <h6><i class="fas fa-star me-2 text-warning"></i>기본 역량</h6>
                    <div class="d-flex flex-wrap gap-1">
                        ${jobDetail.profile.basic_skills.map(skill => 
                            `<span class="badge bg-light text-dark">${skill}</span>`
                        ).join('')}
                    </div>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-star me-2 text-info"></i>우대 역량</h6>
                    <div class="d-flex flex-wrap gap-1">
                        ${jobDetail.profile.applied_skills.map(skill => 
                            `<span class="badge bg-info">${skill}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
            ` : `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                아직 직무기술서가 작성되지 않았습니다.
                <a href="/admin/job_profiles/jobprofile/add/" class="alert-link">지금 작성하기</a>
            </div>
            `}
            
            <!-- 관련 직무 -->
            ${jobDetail.related_jobs.length > 0 ? `
            <div class="mb-4">
                <h5><i class="fas fa-link me-2 text-secondary"></i>관련 직무</h5>
                <div class="row">
                    ${jobDetail.related_jobs.map(relatedJob => `
                        <div class="col-md-6 mb-2">
                            <div class="card border-0 bg-light">
                                <div class="card-body py-2">
                                    <small class="text-muted">${relatedJob.name}</small>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // React 또는 Vue 중 선택하여 초기화
    initializeReactApp(); // React 사용 시
    // initializeVueApp(); // Vue 사용 시
});
</script>
{% endblock %}
"""


def generate_django_urls():
    """Django URL 패턴 생성"""
    
    return """
from django.urls import path, include
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # 기존 URL 패턴들
    path('', views.JobProfileListView.as_view(), name='list'),
    path('add/', views.JobProfileCreateView.as_view(), name='add'),
    path('<uuid:pk>/', views.JobProfileDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.JobProfileUpdateView.as_view(), name='edit'),
    
    # 새로운 트리 뷰
    path('tree/', views.JobTreeView.as_view(), name='tree'),
    
    # API 엔드포인트
    path('api/', include([
        path('job-tree/', views.job_tree_api, name='job_tree_api'),
        path('job-profiles/<uuid:job_role_id>/', views.job_profile_detail_api, name='job_profile_detail_api'),
        path('job-search/', views.job_search_api, name='job_search_api'),
        path('job-statistics/', views.job_statistics_api, name='job_statistics_api'),
    ])),
]
"""


def generate_integration_guide():
    """통합 가이드 생성"""
    
    return """
# EHR 시스템 직무 체계도 UX 통합 가이드

## 🚀 빠른 시작

### 1. Django 뷰 추가

```python
# job_profiles/views.py에 추가
from .django_integration import JobTreeView

# 또는 기존 views.py에 클래스 복사
```

### 2. URL 패턴 업데이트

```python
# job_profiles/urls.py에 추가
path('tree/', JobTreeView.as_view(), name='tree'),
```

### 3. 템플릿 파일 생성

```bash
# templates/job_profiles/ 디렉토리에 job_tree.html 생성
cp job_tree_template.html templates/job_profiles/job_tree.html
```

### 4. 정적 파일 배치

```bash
# CSS 파일 복사
cp JobTreeVisualization.css static/css/

# JavaScript 컴포넌트 배치
cp components/*.jsx static/js/components/
cp components/*.vue static/js/components/
```

### 5. 메뉴 추가

기존 대시보드 메뉴에 직무 체계도 링크 추가:

```html
<!-- templates/base.html 또는 sidebar.html에 추가 -->
<li class="nav-item">
    <a class="nav-link" href="{% url 'job_profiles:tree' %}">
        <i class="fas fa-sitemap me-2"></i>
        직무 체계도
    </a>
</li>
```

## 🔧 고급 설정

### React 번들링 (권장)

1. **Webpack 설정**:
```javascript
// webpack.config.js
module.exports = {
  entry: './static/js/job-tree-app.jsx',
  output: {
    path: path.resolve(__dirname, 'static/js/dist'),
    filename: 'job-tree-bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-react']
          }
        }
      }
    ]
  }
};
```

2. **번들 빌드**:
```bash
npm run build
```

3. **템플릿에서 번들 사용**:
```html
<script src="{% static 'js/dist/job-tree-bundle.js' %}"></script>
```

### Vue.js 통합

1. **Vue CLI 프로젝트 생성**:
```bash
vue create job-tree-ui
cd job-tree-ui
npm install ant-design-vue
```

2. **컴포넌트 통합**:
```javascript
// src/main.js
import { createApp } from 'vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/antd.css'

import JobTreeApp from './JobTreeApp.vue'

createApp(JobTreeApp).use(Antd).mount('#job-tree-app')
```

### API 인증 설정

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## 🎨 커스터마이징

### 색상 테마 변경

```css
/* static/css/custom-job-tree.css */
:root {
  --primary-color: #your-brand-color;
  --secondary-color: #your-secondary-color;
}

.job-tree-container {
  --category-it: var(--primary-color);
  --category-management: var(--secondary-color);
  /* ... */
}
```

### 아이콘 추가

```javascript
// static/js/job-icons.js
const customJobIcons = {
  '새로운직무': 'fas fa-custom-icon',
  // 추가 아이콘 매핑...
};
```

### 브랜딩 적용

```html
<!-- 로고 및 브랜딩 요소 추가 -->
<div class="brand-header">
    <img src="{% static 'images/company-logo.png' %}" alt="Company Logo">
    <h1>{{ company_name }} 직무 체계도</h1>
</div>
```

## 📱 모바일 최적화

### 반응형 중단점 조정

```css
/* 회사 디자인 시스템에 맞춘 중단점 */
@media (max-width: 576px) {
  .job-tree-container {
    padding: 8px;
  }
  
  .tree-header {
    flex-direction: column;
    gap: 12px;
  }
}
```

### 터치 인터랙션 개선

```css
.job-card, .tree-node {
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

@media (hover: none) {
  .job-card:active {
    transform: scale(0.95);
  }
}
```

## 🔐 보안 설정

### CSRF 보호

```javascript
// API 요청 시 CSRF 토큰 포함
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/api/job-tree/', {
  headers: {
    'X-CSRFToken': csrfToken,
    'Content-Type': 'application/json'
  }
});
```

### 권한 기반 접근 제어

```python
# views.py
class JobTreeView(LoginRequiredMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('job_profiles.view_jobprofile'):
            return redirect('no_permission')
        return super().dispatch(request, *args, **kwargs)
```

## 📊 성능 최적화

### 캐싱 전략

```python
# views.py
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15분 캐싱
def job_tree_api(request):
    # API 로직...
```

### 데이터베이스 최적화

```python
# 쿼리 최적화
categories = JobCategory.objects.filter(is_active=True).prefetch_related(
    Prefetch('job_types', 
        queryset=JobType.objects.filter(is_active=True).select_related('category')
    )
).select_related('created_by')
```

### 정적 파일 압축

```python
# settings.py
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# 또는 WhiteNoise 사용
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]
```

## 🧪 테스트

### API 테스트

```python
# tests/test_job_tree_api.py
from django.test import TestCase
from django.urls import reverse

class JobTreeAPITest(TestCase):
    def test_job_tree_data(self):
        response = self.client.get(reverse('job_profiles:job_tree_api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('data', data)
```

### 프론트엔드 테스트

```javascript
// tests/job-tree.test.js
import { render, screen } from '@testing-library/react';
import JobTreeVisualization from '../components/JobTreeVisualization';

test('renders job tree', () => {
  render(<JobTreeVisualization jobData={mockData} />);
  expect(screen.getByText('직무 체계도')).toBeInTheDocument();
});
```

## 🚀 배포

### 프로덕션 빌드

```bash
# React
npm run build

# Vue
npm run build

# Django 정적 파일 수집
python manage.py collectstatic
```

### 환경별 설정

```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# 정적 파일 CDN 설정
STATIC_URL = 'https://cdn.your-domain.com/static/'
```

## 📈 모니터링

### 성능 모니터링

```javascript
// 페이지 로드 성능 측정
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Performance:', entry.name, entry.duration);
  }
});
observer.observe({entryTypes: ['measure']});
```

### 에러 추적

```javascript
// 에러 보고
window.addEventListener('error', (e) => {
  // 에러 추적 서비스로 전송
  console.error('Job Tree Error:', e.error);
});
```

이 가이드를 따라하면 기존 EHR 시스템에 현대적인 직무 체계도 UX를 완벽하게 통합할 수 있습니다.
"""


def main():
    """Django 통합 파일들 생성"""
    output_dir = r"C:/Users/apro/OneDrive/Desktop/EHR_V1.0/job_profile_ux_output"
    
    # Django 템플릿 생성
    template_content = generate_django_template()
    with open(os.path.join(output_dir, 'job_tree_template.html'), 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    # URL 패턴 생성
    urls_content = generate_django_urls()
    with open(os.path.join(output_dir, 'django_urls.py'), 'w', encoding='utf-8') as f:
        f.write(urls_content)
    
    # 통합 가이드 생성
    guide_content = generate_integration_guide()
    with open(os.path.join(output_dir, 'INTEGRATION_GUIDE.md'), 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Django 통합 파일들 추가 생성 완료!")


if __name__ == '__main__':
    main()