#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OK금융그룹 직군-직종-직무 3단계 트리맵 UI/UX 혁신
Non-PL/PL 분할 컬럼형 카드 레이아웃 시스템

Features:
1. 최상단 Non-PL/PL직군 양쪽 컬럼 분할
2. 직군별 산하 직종 가로정렬
3. 직종별 직무를 카드/컬러/아이콘형으로 미려하게 배치
4. 클릭시 상세진입
5. 반응형, 드래그/확대축소, 조직도형 UI/UX
"""

import os
import json
from datetime import datetime

class JobProfileTreeOverhaul:
    """직무 트리맵 UI/UX 혁신 시스템"""
    
    def __init__(self):
        self.output_dir = r"C:\Users\apro\OneDrive\Desktop\EHR_V1.0\job_profile_tree_overhaul"
        self.job_structure = self.get_ok_financial_structure()
        self.color_scheme = self.define_color_scheme()
        self.icons = self.define_icon_mapping()
        
    def get_ok_financial_structure(self):
        """OK금융그룹 직무 체계 구조"""
        return {
            'Non-PL': {
                'IT/디지털': {
                    'color': '#3B82F6',
                    'icon': 'laptop',
                    'jobs': {
                        'IT기획': ['시스템기획'],
                        'IT개발': ['시스템개발'],
                        'IT운영': ['시스템관리', '서비스운영']
                    }
                },
                '경영지원': {
                    'color': '#8B5CF6',
                    'icon': 'briefcase',
                    'jobs': {
                        '경영관리': [
                            '감사', '인사관리', '인재개발', '경영지원', '비서', '홍보',
                            '경영기획', '디자인', '리스크관리', '마케팅', '스포츠사무관리',
                            '자금', '재무회계', '정보보안', '준법지원', '총무'
                        ]
                    }
                },
                '금융': {
                    'color': '#10B981',
                    'icon': 'dollar-sign',
                    'jobs': {
                        '투자금융': ['투자금융'],
                        '기업금융': ['기업영업기획', '기업여신심사', '기업여신관리'],
                        '리테일금융': [
                            '데이터분석', '디지털플랫폼', 'NPL사업기획', '리테일심사기획',
                            '개인신용대출기획', '모기지기획', '예금기획', '예금영업'
                        ]
                    }
                },
                '영업': {
                    'color': '#F59E0B',
                    'icon': 'users',
                    'jobs': {
                        '기업영업': ['기업여신영업']
                    }
                }
            },
            'PL': {
                '고객서비스': {
                    'color': '#EF4444',
                    'icon': 'headphones',
                    'jobs': {
                        '고객지원': ['대출고객지원', '업무지원', '예금고객지원', '채권관리']
                    }
                }
            }
        }
    
    def define_color_scheme(self):
        """직군별 색상 스키마 정의"""
        return {
            'primary': {
                'IT/디지털': '#3B82F6',
                '경영지원': '#8B5CF6',
                '금융': '#10B981',
                '영업': '#F59E0B',
                '고객서비스': '#EF4444'
            },
            'gradient': {
                'IT/디지털': 'linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)',
                '경영지원': 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)',
                '금융': 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
                '영업': 'linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%)',
                '고객서비스': 'linear-gradient(135deg, #EF4444 0%, #F87171 100%)'
            }
        }
    
    def define_icon_mapping(self):
        """직무별 아이콘 매핑"""
        return {
            # IT/디지털
            '시스템기획': 'sitemap',
            '시스템개발': 'code',
            '시스템관리': 'server',
            '서비스운영': 'cogs',
            
            # 경영지원
            '감사': 'shield-alt',
            '인사관리': 'user-tie',
            '인재개발': 'graduation-cap',
            '경영지원': 'hands-helping',
            '비서': 'user-clock',
            '홍보': 'bullhorn',
            '경영기획': 'chart-line',
            '디자인': 'palette',
            '리스크관리': 'exclamation-triangle',
            '마케팅': 'chart-pie',
            '스포츠사무관리': 'futbol',
            '자금': 'coins',
            '재무회계': 'calculator',
            '정보보안': 'lock',
            '준법지원': 'balance-scale',
            '총무': 'building',
            
            # 금융
            '투자금융': 'chart-bar',
            '기업영업기획': 'handshake',
            '기업여신심사': 'search-dollar',
            '기업여신관리': 'tasks',
            '데이터분석': 'database',
            '디지털플랫폼': 'mobile-alt',
            'NPL사업기획': 'file-invoice-dollar',
            '리테일심사기획': 'user-check',
            '개인신용대출기획': 'hand-holding-usd',
            '모기지기획': 'home',
            '예금기획': 'piggy-bank',
            '예금영업': 'store',
            
            # 영업
            '기업여신영업': 'briefcase',
            
            # 고객서비스
            '대출고객지원': 'headset',
            '업무지원': 'life-ring',
            '예금고객지원': 'comments',
            '채권관리': 'file-contract'
        }
    
    def generate_react_component(self):
        """React 트리맵 컴포넌트 생성"""
        return """import React, { useState, useEffect, useRef } from 'react';
import { Card, Typography, Box, Grid, Chip, IconButton, Zoom, Fade, Paper } from '@mui/material';
import { TreeView, TreeItem } from '@mui/lab';
import { motion, AnimatePresence } from 'framer-motion';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import * as Icons from '@fortawesome/free-solid-svg-icons';
import './JobProfileTreeMap.css';

const JobProfileTreeMap = ({ jobData, onJobSelect }) => {
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const containerRef = useRef(null);

  // 아이콘 매핑 객체
  const iconMap = """ + json.dumps(self.icons, ensure_ascii=False, indent=4) + """;

  // 색상 스키마
  const colorScheme = """ + json.dumps(self.color_scheme, ensure_ascii=False, indent=4) + """;

  // 직무 구조
  const jobStructure = """ + json.dumps(self.job_structure, ensure_ascii=False, indent=4) + """;

  // 아이콘 컴포넌트 렌더링
  const renderIcon = (iconName) => {
    const iconKey = `fa${iconName.split('-').map(part => 
      part.charAt(0).toUpperCase() + part.slice(1)
    ).join('')}`;
    
    return Icons[iconKey] ? (
      <FontAwesomeIcon icon={Icons[iconKey]} />
    ) : (
      <FontAwesomeIcon icon={Icons.faBriefcase} />
    );
  };

  // 직무 카드 컴포넌트
  const JobCard = ({ job, category, group, delay = 0 }) => {
    const [isHovered, setIsHovered] = useState(false);
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay }}
        whileHover={{ scale: 1.05, transition: { duration: 0.2 } }}
        whileTap={{ scale: 0.95 }}
        onHoverStart={() => setIsHovered(true)}
        onHoverEnd={() => setIsHovered(false)}
      >
        <Card
          className="job-card"
          onClick={() => handleJobClick(job, category, group)}
          sx={{
            cursor: 'pointer',
            background: isHovered ? colorScheme.gradient[category] : '#ffffff',
            border: `2px solid ${colorScheme.primary[category]}20`,
            borderRadius: '16px',
            padding: '20px',
            minHeight: '120px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            transition: 'all 0.3s ease',
            boxShadow: isHovered ? '0 8px 24px rgba(0,0,0,0.12)' : '0 2px 8px rgba(0,0,0,0.08)',
            '&:hover': {
              transform: 'translateY(-4px)',
              '& .job-icon': {
                transform: 'scale(1.2) rotate(5deg)',
              },
              '& .job-name': {
                color: '#ffffff',
              }
            }
          }}
        >
          <Box
            className="job-icon"
            sx={{
              fontSize: '32px',
              color: isHovered ? '#ffffff' : colorScheme.primary[category],
              marginBottom: '12px',
              transition: 'all 0.3s ease',
            }}
          >
            {renderIcon(iconMap[job] || 'briefcase')}
          </Box>
          <Typography
            className="job-name"
            variant="body1"
            sx={{
              fontWeight: 600,
              color: isHovered ? '#ffffff' : '#1f2937',
              transition: 'all 0.3s ease',
            }}
          >
            {job}
          </Typography>
        </Card>
      </motion.div>
    );
  };

  // 직종 섹션 컴포넌트
  const JobTypeSection = ({ jobType, jobs, category, group }) => {
    return (
      <Box className="job-type-section" sx={{ marginBottom: 4 }}>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              color: colorScheme.primary[category],
              marginBottom: 2,
              paddingLeft: 2,
              borderLeft: `4px solid ${colorScheme.primary[category]}`,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            {jobType}
            <Chip
              label={`${jobs.length}개 직무`}
              size="small"
              sx={{
                backgroundColor: `${colorScheme.primary[category]}20`,
                color: colorScheme.primary[category],
                fontWeight: 600,
              }}
            />
          </Typography>
        </motion.div>
        
        <Grid container spacing={2} sx={{ paddingLeft: 2 }}>
          {jobs.map((job, index) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={job}>
              <JobCard
                job={job}
                category={category}
                group={group}
                delay={index * 0.1}
              />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  };

  // 직군 카테고리 컴포넌트
  const CategorySection = ({ category, data, group }) => {
    const categoryIcon = data.icon;
    const categoryColor = data.color;
    
    return (
      <Paper
        elevation={0}
        sx={{
          padding: 4,
          marginBottom: 4,
          background: `linear-gradient(135deg, ${categoryColor}08 0%, ${categoryColor}04 100%)`,
          borderRadius: '24px',
          border: `1px solid ${categoryColor}20`,
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              marginBottom: 3,
            }}
          >
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: '16px',
                background: colorScheme.gradient[category],
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                fontSize: '24px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              }}
            >
              {renderIcon(categoryIcon)}
            </Box>
            <Box>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 800,
                  color: '#1f2937',
                  marginBottom: 0.5,
                }}
              >
                {category}
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: '#6b7280',
                  fontWeight: 500,
                }}
              >
                {Object.keys(data.jobs).length}개 직종 · {
                  Object.values(data.jobs).flat().length
                }개 직무
              </Typography>
            </Box>
          </Box>
          
          {Object.entries(data.jobs).map(([jobType, jobs]) => (
            <JobTypeSection
              key={jobType}
              jobType={jobType}
              jobs={jobs}
              category={category}
              group={group}
            />
          ))}
        </motion.div>
      </Paper>
    );
  };

  // 직무 클릭 핸들러
  const handleJobClick = (job, category, group) => {
    setSelectedJob(job);
    setSelectedCategory(category);
    setSelectedGroup(group);
    
    if (onJobSelect) {
      onJobSelect({
        job,
        category,
        group,
        jobType: findJobType(job, category, group),
      });
    }
  };

  // 직무의 직종 찾기
  const findJobType = (job, category, group) => {
    const categoryData = jobStructure[group][category];
    for (const [jobType, jobs] of Object.entries(categoryData.jobs)) {
      if (jobs.includes(job)) {
        return jobType;
      }
    }
    return null;
  };

  return (
    <Box className="job-profile-tree-map" ref={containerRef}>
      {/* 헤더 */}
      <Box className="tree-map-header" sx={{ marginBottom: 4 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 800,
            textAlign: 'center',
            background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #10B981 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: 2,
          }}
        >
          OK금융그룹 직무 체계도
        </Typography>
        <Typography
          variant="body1"
          sx={{
            textAlign: 'center',
            color: '#6b7280',
          }}
        >
          직군 → 직종 → 직무 구조를 한눈에 확인하세요
        </Typography>
      </Box>

      {/* 줌/팬 컨테이너 */}
      <TransformWrapper
        initialScale={1}
        minScale={0.5}
        maxScale={2}
        centerOnInit
      >
        <TransformComponent>
          <Grid container spacing={4} className="tree-map-container">
            {/* Non-PL 직군 */}
            <Grid item xs={12} lg={8}>
              <Paper
                elevation={0}
                sx={{
                  padding: 3,
                  background: '#f8fafc',
                  borderRadius: '24px',
                  border: '2px solid #e5e7eb',
                }}
              >
                <Typography
                  variant="h5"
                  sx={{
                    fontWeight: 800,
                    color: '#1f2937',
                    marginBottom: 3,
                    textAlign: 'center',
                    paddingBottom: 2,
                    borderBottom: '2px solid #e5e7eb',
                  }}
                >
                  Non-PL 직군
                </Typography>
                
                {Object.entries(jobStructure['Non-PL']).map(([category, data]) => (
                  <CategorySection
                    key={category}
                    category={category}
                    data={data}
                    group="Non-PL"
                  />
                ))}
              </Paper>
            </Grid>

            {/* PL 직군 */}
            <Grid item xs={12} lg={4}>
              <Paper
                elevation={0}
                sx={{
                  padding: 3,
                  background: '#fef3f2',
                  borderRadius: '24px',
                  border: '2px solid #fecaca',
                }}
              >
                <Typography
                  variant="h5"
                  sx={{
                    fontWeight: 800,
                    color: '#1f2937',
                    marginBottom: 3,
                    textAlign: 'center',
                    paddingBottom: 2,
                    borderBottom: '2px solid #fecaca',
                  }}
                >
                  PL 직군
                </Typography>
                
                {Object.entries(jobStructure['PL']).map(([category, data]) => (
                  <CategorySection
                    key={category}
                    category={category}
                    data={data}
                    group="PL"
                  />
                ))}
              </Paper>
            </Grid>
          </Grid>
        </TransformComponent>
      </TransformWrapper>

      {/* 플로팅 컨트롤 */}
      <Box
        className="floating-controls"
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          zIndex: 1000,
        }}
      >
        <Zoom in>
          <IconButton
            sx={{
              backgroundColor: '#ffffff',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              '&:hover': {
                backgroundColor: '#f3f4f6',
              },
            }}
            onClick={() => containerRef.current?.scrollIntoView({ behavior: 'smooth' })}
          >
            <FontAwesomeIcon icon={Icons.faArrowUp} />
          </IconButton>
        </Zoom>
      </Box>
    </Box>
  );
};

export default JobProfileTreeMap;"""

    def generate_css_styles(self):
        """CSS 스타일 생성"""
        return """/* JobProfileTreeMap.css */

.job-profile-tree-map {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* 스크롤바 스타일링 */
.job-profile-tree-map::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.job-profile-tree-map::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 6px;
}

.job-profile-tree-map::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 6px;
  transition: background 0.3s ease;
}

.job-profile-tree-map::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 트리맵 컨테이너 */
.tree-map-container {
  transition: transform 0.3s ease;
}

/* 직무 카드 애니메이션 */
.job-card {
  position: relative;
  overflow: hidden;
}

.job-card::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, transparent, rgba(255,255,255,0.5), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.job-card:hover::before {
  transform: translateX(100%);
}

/* 직종 섹션 애니메이션 */
.job-type-section {
  position: relative;
}

.job-type-section::after {
  content: '';
  position: absolute;
  bottom: -16px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
}

.job-type-section:last-child::after {
  display: none;
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .job-profile-tree-map {
    padding: 16px;
  }
  
  .tree-map-header h4 {
    font-size: 1.75rem;
  }
}

@media (max-width: 768px) {
  .job-profile-tree-map {
    padding: 12px;
  }
  
  .tree-map-header h4 {
    font-size: 1.5rem;
  }
  
  .job-card {
    min-height: 100px;
    padding: 16px !important;
  }
  
  .job-icon {
    font-size: 24px !important;
  }
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark) {
  .job-profile-tree-map {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  }
  
  .job-card {
    background: #1e293b !important;
    border-color: rgba(255,255,255,0.1) !important;
  }
  
  .job-name {
    color: #f1f5f9 !important;
  }
}

/* 프린트 스타일 */
@media print {
  .floating-controls {
    display: none !important;
  }
  
  .job-profile-tree-map {
    background: white;
    padding: 0;
  }
  
  .job-card {
    break-inside: avoid;
    page-break-inside: avoid;
  }
}

/* 접근성 향상 */
.job-card:focus-visible {
  outline: 3px solid #3B82F6;
  outline-offset: 2px;
}

.job-card[aria-selected="true"] {
  background: #dbeafe !important;
  border-color: #3B82F6 !important;
}

/* 로딩 애니메이션 */
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.loading-skeleton {
  background: linear-gradient(
    90deg,
    #f3f4f6 0%,
    #e5e7eb 50%,
    #f3f4f6 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite;
}

/* 드래그 인디케이터 */
.drag-indicator {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.8);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.drag-indicator.show {
  opacity: 1;
}

/* 줌 컨트롤 */
.zoom-controls {
  position: fixed;
  top: 50%;
  right: 24px;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 1000;
}

.zoom-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.zoom-button:hover {
  background: #f3f4f6;
  transform: scale(1.1);
}

.zoom-button:active {
  transform: scale(0.95);
}"""

    def generate_django_view(self):
        """Django 뷰 생성"""
        return """from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q
from job_profiles.models import JobCategory, JobType, JobRole, JobProfile

class JobProfileTreeMapView(LoginRequiredMixin, TemplateView):
    '''직무 트리맵 뷰'''
    template_name = 'job_profiles/job_tree_map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 정보
        context.update({
            'total_categories': JobCategory.objects.filter(is_active=True).count(),
            'total_job_types': JobType.objects.filter(is_active=True).count(),
            'total_job_roles': JobRole.objects.filter(is_active=True).count(),
            'total_profiles': JobProfile.objects.filter(is_active=True).count(),
            'page_title': 'OK금융그룹 직무 체계도',
            'page_description': '직군-직종-직무 3단계 트리맵 시각화'
        })
        
        return context


@login_required
def job_tree_map_data_api(request):
    '''트리맵 데이터 API'''
    try:
        # Non-PL, PL 분류를 위한 데이터 구조
        tree_data = {
            'Non-PL': {},
            'PL': {}
        }
        
        # PL 직군 정의 (고객서비스)
        pl_categories = ['고객서비스']
        
        # 모든 카테고리 조회
        categories = JobCategory.objects.filter(is_active=True).prefetch_related(
            Prefetch(
                'job_types',
                queryset=JobType.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        'job_roles',
                        queryset=JobRole.objects.filter(is_active=True).select_related('profile')
                    )
                )
            )
        )
        
        # 색상 및 아이콘 매핑
        category_meta = {
            'IT/디지털': {'color': '#3B82F6', 'icon': 'laptop'},
            '경영지원': {'color': '#8B5CF6', 'icon': 'briefcase'},
            '금융': {'color': '#10B981', 'icon': 'dollar-sign'},
            '영업': {'color': '#F59E0B', 'icon': 'users'},
            '고객서비스': {'color': '#EF4444', 'icon': 'headphones'}
        }
        
        for category in categories:
            # PL/Non-PL 분류
            group = 'PL' if category.name in pl_categories else 'Non-PL'
            
            # 카테고리 데이터 구조
            category_data = {
                'id': str(category.id),
                'name': category.name,
                'color': category_meta.get(category.name, {}).get('color', '#6B7280'),
                'icon': category_meta.get(category.name, {}).get('icon', 'folder'),
                'jobs': {}
            }
            
            # 직종별 직무 정리
            for job_type in category.job_types.all():
                jobs = []
                for job_role in job_type.job_roles.all():
                    job_info = {
                        'id': str(job_role.id),
                        'name': job_role.name,
                        'has_profile': hasattr(job_role, 'profile') and job_role.profile is not None,
                        'profile_id': str(job_role.profile.id) if hasattr(job_role, 'profile') and job_role.profile else None
                    }
                    jobs.append(job_info)
                
                if jobs:
                    category_data['jobs'][job_type.name] = jobs
            
            # 데이터 추가
            if category_data['jobs']:
                tree_data[group][category.name] = category_data
        
        # 통계 정보 추가
        statistics = {
            'Non-PL': {
                'categories': len(tree_data['Non-PL']),
                'job_types': sum(len(cat['jobs']) for cat in tree_data['Non-PL'].values()),
                'jobs': sum(len(jobs) for cat in tree_data['Non-PL'].values() for jobs in cat['jobs'].values())
            },
            'PL': {
                'categories': len(tree_data['PL']),
                'job_types': sum(len(cat['jobs']) for cat in tree_data['PL'].values()),
                'jobs': sum(len(jobs) for cat in tree_data['PL'].values() for jobs in cat['jobs'].values())
            }
        }
        
        return JsonResponse({
            'success': True,
            'data': tree_data,
            'statistics': statistics
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def job_detail_modal_api(request, job_role_id):
    '''직무 상세 정보 모달 API'''
    try:
        job_role = JobRole.objects.select_related(
            'job_type__category',
            'profile'
        ).get(id=job_role_id, is_active=True)
        
        # 관련 직무 조회
        related_jobs = JobRole.objects.filter(
            job_type=job_role.job_type,
            is_active=True
        ).exclude(id=job_role.id).select_related('profile')[:5]
        
        # 응답 데이터 구성
        data = {
            'job': {
                'id': str(job_role.id),
                'name': job_role.name,
                'description': job_role.description,
                'full_path': job_role.full_path,
                'category': job_role.job_type.category.name,
                'job_type': job_role.job_type.name,
            },
            'profile': None,
            'related_jobs': []
        }
        
        # 직무기술서 정보
        if hasattr(job_role, 'profile') and job_role.profile:
            profile = job_role.profile
            data['profile'] = {
                'id': str(profile.id),
                'role_responsibility': profile.role_responsibility,
                'qualification': profile.qualification,
                'basic_skills': profile.basic_skills,
                'applied_skills': profile.applied_skills,
                'growth_path': profile.growth_path,
                'related_certifications': profile.related_certifications
            }
        
        # 관련 직무 정보
        for related in related_jobs:
            data['related_jobs'].append({
                'id': str(related.id),
                'name': related.name,
                'has_profile': hasattr(related, 'profile') and related.profile is not None
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except JobRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '직무를 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)"""

    def generate_django_template(self):
        """Django 템플릿 생성"""
        return """{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<!-- Material-UI CSS -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700&display=swap" />
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />

<!-- Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Custom CSS -->
<link rel="stylesheet" href="{% static 'css/JobProfileTreeMap.css' %}">
{% endblock %}

{% block content %}
<div id="job-tree-map-root">
    <!-- React 컴포넌트가 마운트될 위치 -->
    <div class="loading-container" style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin fa-3x" style="color: #3B82F6;"></i>
            <p style="margin-top: 16px; color: #6b7280;">직무 체계도를 불러오는 중...</p>
        </div>
    </div>
</div>

<!-- 직무 상세 모달 -->
<div id="job-detail-modal" class="modal" style="display: none;">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="job-detail-title">직무 상세 정보</h5>
                <button type="button" class="btn-close" onclick="closeJobModal()"></button>
            </div>
            <div class="modal-body" id="job-detail-content">
                <!-- 동적으로 채워질 내용 -->
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<!-- React & Material-UI -->
<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script crossorigin src="https://unpkg.com/@mui/material@5.14.0/umd/material-ui.production.min.js"></script>

<!-- Framer Motion -->
<script src="https://unpkg.com/framer-motion@11.0.0/dist/framer-motion.js"></script>

<!-- React Zoom Pan Pinch -->
<script src="https://unpkg.com/react-zoom-pan-pinch@3.3.0/dist/index.min.js"></script>

<!-- Font Awesome -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>

<script>
// Django 컨텍스트
const djangoContext = {
    csrfToken: '{{ csrf_token }}',
    apiBaseUrl: '/job-profiles/api/',
    staticUrl: '{% static "" %}',
    statistics: {
        categories: {{ total_categories }},
        jobTypes: {{ total_job_types }},
        jobRoles: {{ total_job_roles }},
        profiles: {{ total_profiles }}
    }
};

// API 헬퍼
const api = {
    get: async (url) => {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': djangoContext.csrfToken
                }
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};

// 직무 트리맵 데이터 로드 및 컴포넌트 초기화
async function initializeTreeMap() {
    try {
        // 데이터 로드
        const response = await api.get('/job-profiles/api/tree-map-data/');
        if (!response.success) throw new Error(response.error);
        
        // React 컴포넌트 마운트
        const { createElement } = React;
        const root = ReactDOM.createRoot(document.getElementById('job-tree-map-root'));
        
        // JobProfileTreeMap 컴포넌트 (위에서 정의한 React 컴포넌트)
        root.render(
            createElement(JobProfileTreeMap, {
                jobData: response.data,
                onJobSelect: handleJobSelect
            })
        );
        
    } catch (error) {
        console.error('초기화 실패:', error);
        document.getElementById('job-tree-map-root').innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <i class="fas fa-exclamation-triangle fa-3x" style="color: #EF4444;"></i>
                <p style="margin-top: 16px; color: #6b7280;">
                    직무 체계도를 불러오는데 실패했습니다.<br>
                    <small>${error.message}</small>
                </p>
                <button class="btn btn-primary mt-3" onclick="location.reload()">
                    <i class="fas fa-redo me-2"></i>다시 시도
                </button>
            </div>
        `;
    }
}

// 직무 선택 핸들러
async function handleJobSelect(jobInfo) {
    console.log('Selected job:', jobInfo);
    
    try {
        // 직무 상세 정보 로드
        const response = await api.get(`/job-profiles/api/job-detail-modal/${jobInfo.jobId}/`);
        if (!response.success) throw new Error(response.error);
        
        // 모달 표시
        showJobDetailModal(response.data);
        
    } catch (error) {
        console.error('직무 상세 정보 로드 실패:', error);
        alert('직무 상세 정보를 불러올 수 없습니다.');
    }
}

// 직무 상세 모달 표시
function showJobDetailModal(data) {
    const modal = document.getElementById('job-detail-modal');
    const title = document.getElementById('job-detail-title');
    const content = document.getElementById('job-detail-content');
    
    // 제목 설정
    title.textContent = `${data.job.name} - ${data.job.full_path}`;
    
    // 내용 구성
    let html = `
        <div class="job-detail-container">
            <div class="row mb-4">
                <div class="col-md-8">
                    <h4>${data.job.name}</h4>
                    <p class="text-muted">${data.job.description || '설명이 없습니다.'}</p>
                    <div class="d-flex gap-2 mt-2">
                        <span class="badge bg-primary">${data.job.category}</span>
                        <span class="badge bg-secondary">${data.job.job_type}</span>
                    </div>
                </div>
                ${data.profile ? `
                <div class="col-md-4 text-end">
                    <a href="/job-profiles/${data.profile.id}/" class="btn btn-primary">
                        <i class="fas fa-eye me-1"></i>상세보기
                    </a>
                    <a href="/job-profiles/admin/${data.profile.id}/" class="btn btn-outline-secondary">
                        <i class="fas fa-edit me-1"></i>편집
                    </a>
                </div>
                ` : ''}
            </div>
    `;
    
    if (data.profile) {
        html += `
            <div class="profile-section">
                <h5><i class="fas fa-tasks me-2"></i>핵심 역할 및 책임</h5>
                <div class="card mb-3">
                    <div class="card-body">
                        <pre class="mb-0">${data.profile.role_responsibility}</pre>
                    </div>
                </div>
                
                <h5><i class="fas fa-check-circle me-2"></i>자격 요건</h5>
                <div class="card mb-3">
                    <div class="card-body">
                        <pre class="mb-0">${data.profile.qualification}</pre>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-star me-2"></i>기본 역량</h6>
                        <div class="skill-tags">
                            ${data.profile.basic_skills.map(skill => 
                                `<span class="badge bg-light text-dark me-1 mb-1">${skill}</span>`
                            ).join('')}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-star me-2"></i>우대 역량</h6>
                        <div class="skill-tags">
                            ${data.profile.applied_skills.map(skill => 
                                `<span class="badge bg-info text-white me-1 mb-1">${skill}</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        html += `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                이 직무의 상세 기술서가 아직 작성되지 않았습니다.
            </div>
        `;
    }
    
    if (data.related_jobs && data.related_jobs.length > 0) {
        html += `
            <hr class="my-4">
            <h5><i class="fas fa-link me-2"></i>관련 직무</h5>
            <div class="related-jobs">
                ${data.related_jobs.map(job => `
                    <span class="badge bg-light text-dark me-2 mb-2">
                        ${job.name} ${job.has_profile ? '<i class="fas fa-check-circle text-success"></i>' : ''}
                    </span>
                `).join('')}
            </div>
        `;
    }
    
    html += '</div>';
    content.innerHTML = html;
    
    // 모달 표시
    modal.style.display = 'block';
    document.body.classList.add('modal-open');
    
    // 배경 오버레이 추가
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop fade show';
    backdrop.onclick = closeJobModal;
    document.body.appendChild(backdrop);
}

// 모달 닫기
function closeJobModal() {
    const modal = document.getElementById('job-detail-modal');
    modal.style.display = 'none';
    document.body.classList.remove('modal-open');
    
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) backdrop.remove();
}

// ESC 키로 모달 닫기
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeJobModal();
});

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', initializeTreeMap);
</script>

<!-- 여기에 React 컴포넌트 코드 포함 -->
<script>
${REACT_COMPONENT_CODE}
</script>
{% endblock %}"""

    def generate_url_patterns(self):
        """URL 패턴 생성"""
        return """# job_profiles/urls.py에 추가할 URL 패턴

from .views import JobProfileTreeMapView, job_tree_map_data_api, job_detail_modal_api

urlpatterns += [
    # 트리맵 뷰
    path('tree-map/', JobProfileTreeMapView.as_view(), name='tree_map'),
    
    # 트리맵 API
    path('api/tree-map-data/', job_tree_map_data_api, name='tree_map_data_api'),
    path('api/job-detail-modal/<uuid:job_role_id>/', job_detail_modal_api, name='job_detail_modal_api'),
]"""

    def generate_all_files(self):
        """모든 파일 생성"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 파일 생성
        files = {
            'JobProfileTreeMap.jsx': self.generate_react_component(),
            'JobProfileTreeMap.css': self.generate_css_styles(),
            'tree_map_views.py': self.generate_django_view(),
            'job_tree_map.html': self.generate_django_template(),
            'url_patterns.py': self.generate_url_patterns(),
            'README.md': self.generate_readme()
        }
        
        for filename, content in files.items():
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"생성 완료: {filename}")
        
        print(f"\n모든 파일이 {self.output_dir}에 생성되었습니다!")
        
        # 구현 가이드 출력
        self.print_implementation_guide()

    def generate_readme(self):
        """README 파일 생성"""
        return """# OK금융그룹 직무 트리맵 UI/UX 혁신

## 🎯 개요
OK금융그룹의 직군-직종-직무 3단계 체계를 혁신적인 트리맵 UI로 시각화하는 시스템입니다.

## ✨ 주요 기능

### 1. Non-PL/PL 직군 분할 뷰
- 좌측: Non-PL 직군 (IT/디지털, 경영지원, 금융, 영업)
- 우측: PL 직군 (고객서비스)
- 시각적 구분과 색상 차별화

### 2. 직종별 가로 정렬
- 각 직군 아래 직종을 가로로 배치
- 직종별 직무 개수 표시
- 색상 코딩으로 직관적 구분

### 3. 직무 카드형 UI
- 아이콘과 함께 표시되는 직무 카드
- 호버 시 그라디언트 효과
- 클릭 시 상세 정보 모달

### 4. 인터랙티브 기능
- 드래그 & 줌 (확대/축소)
- 반응형 디자인
- 부드러운 애니메이션
- 키보드 네비게이션

### 5. 모던 디자인
- Material-UI 기반
- Framer Motion 애니메이션
- Font Awesome 아이콘
- 다크 모드 지원

## 🛠 기술 스택
- **Frontend**: React 18, Material-UI 5, Framer Motion
- **Backend**: Django 5.2
- **Icons**: Font Awesome 6
- **Zoom/Pan**: react-zoom-pan-pinch
- **Styling**: CSS3 with Flexbox/Grid

## 📦 설치 방법

### 1. Django 뷰 추가
```python
# job_profiles/views.py
from tree_map_views import JobProfileTreeMapView, job_tree_map_data_api, job_detail_modal_api
```

### 2. URL 패턴 등록
```python
# job_profiles/urls.py
path('tree-map/', JobProfileTreeMapView.as_view(), name='tree_map'),
path('api/tree-map-data/', job_tree_map_data_api, name='tree_map_data_api'),
path('api/job-detail-modal/<uuid:job_role_id>/', job_detail_modal_api, name='job_detail_modal_api'),
```

### 3. 정적 파일 배치
- `JobProfileTreeMap.css` → `static/css/`
- `JobProfileTreeMap.jsx` → `static/js/components/`

### 4. 템플릿 설치
- `job_tree_map.html` → `templates/job_profiles/`

## 🚀 사용법

### 접속 URL
```
http://localhost:8000/job-profiles/tree-map/
```

### 주요 조작법
- **마우스 드래그**: 화면 이동
- **마우스 휠**: 확대/축소
- **직무 카드 클릭**: 상세 정보 보기
- **ESC 키**: 모달 닫기

## 🎨 커스터마이징

### 색상 변경
```javascript
const colorScheme = {
    primary: {
        'IT/디지털': '#3B82F6',  // 원하는 색상으로 변경
        // ...
    }
}
```

### 아이콘 변경
```javascript
const iconMap = {
    '시스템기획': 'sitemap',  // Font Awesome 아이콘명
    // ...
}
```

## 📱 반응형 브레이크포인트
- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

## 🔧 문제 해결

### React 컴포넌트가 로드되지 않을 때
1. 브라우저 콘솔에서 에러 확인
2. React/Material-UI CDN 링크 확인
3. CSRF 토큰 확인

### API 호출 실패 시
1. Django 서버 실행 확인
2. URL 패턴 등록 확인
3. 로그인 상태 확인

## 📄 라이선스
OK금융그룹 내부 사용"""

    def print_implementation_guide(self):
        """구현 가이드 출력"""
        print("\n" + "="*60)
        print("OK금융그룹 직무 트리맵 UI/UX 혁신 시스템 구현 가이드")
        print("="*60)
        
        print("\n1. Django 뷰 추가")
        print("   - tree_map_views.py 내용을 job_profiles/views.py에 추가")
        
        print("\n2. URL 패턴 등록")
        print("   - url_patterns.py 내용을 job_profiles/urls.py에 추가")
        
        print("\n3. 템플릿 설치")
        print("   - job_tree_map.html을 templates/job_profiles/에 복사")
        
        print("\n4. 정적 파일 배치")
        print("   - JobProfileTreeMap.css를 static/css/에 복사")
        print("   - JobProfileTreeMap.jsx를 static/js/components/에 복사")
        
        print("\n5. 접속 URL")
        print("   - http://localhost:8000/job-profiles/tree-map/")
        
        print("\n주요 기능:")
        print("   - Non-PL/PL 직군 좌우 분할 레이아웃")
        print("   - 직종별 가로 정렬 + 직무 카드형 UI")
        print("   - 컬러 테마 + Font Awesome 아이콘")
        print("   - 드래그 & 줌 인터랙션")
        print("   - 반응형 + 모던 디자인")
        
        print("\n" + "="*60)


def main():
    """메인 실행 함수"""
    print("OK금융그룹 직무 트리맵 UI/UX 혁신 시스템 생성 시작...")
    
    overhaul = JobProfileTreeOverhaul()
    overhaul.generate_all_files()
    
    print("\n모든 작업이 완료되었습니다!")


if __name__ == "__main__":
    main()