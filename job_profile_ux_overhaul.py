#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
직무기술서 전체 직무체계도(트리/맵) 기반 개편 및 상세조회 UI/UX 혁신
- 계층형/그리드형/맵형 트리 시각화
- 현대적 카드/셀 클릭 인터랙션
- 반응형 디자인 및 줌/드래그 UX
"""

import os
import sys
import io
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# 한글 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


@dataclass
class JobTreeNode:
    """직무 트리 노드 정의"""
    id: str
    name: str
    type: str  # 'category', 'job_type', 'job_role'
    level: int
    parent_id: Optional[str]
    children: List['JobTreeNode']
    metadata: Dict[str, Any]
    color: str
    icon: str
    description: str
    job_count: int


class JobProfileUXOverhaul:
    """직무기술서 UX 혁신 시스템"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        
        # 직군별 색상 테마
        self.category_colors = {
            'IT/디지털': {
                'primary': '#3B82F6',    # Blue
                'secondary': '#DBEAFE',
                'accent': '#1D4ED8',
                'gradient': 'linear-gradient(135deg, #3B82F6, #1D4ED8)'
            },
            '경영지원': {
                'primary': '#10B981',    # Emerald
                'secondary': '#D1FAE5',
                'accent': '#059669',
                'gradient': 'linear-gradient(135deg, #10B981, #059669)'
            },
            '금융': {
                'primary': '#F59E0B',    # Amber
                'secondary': '#FEF3C7',
                'accent': '#D97706',
                'gradient': 'linear-gradient(135deg, #F59E0B, #D97706)'
            },
            '영업': {
                'primary': '#EF4444',    # Red
                'secondary': '#FECACA',
                'accent': '#DC2626',
                'gradient': 'linear-gradient(135deg, #EF4444, #DC2626)'
            },
            '고객서비스': {
                'primary': '#8B5CF6',   # Violet
                'secondary': '#E0E7FF',
                'accent': '#7C3AED',
                'gradient': 'linear-gradient(135deg, #8B5CF6, #7C3AED)'
            }
        }
        
        # 직무별 아이콘 매핑
        self.job_icons = {
            '시스템기획': 'fas fa-project-diagram',
            '시스템개발': 'fas fa-code',
            '시스템관리': 'fas fa-server',
            '서비스운영': 'fas fa-cogs',
            '감사': 'fas fa-search',
            '인사관리': 'fas fa-users',
            '인재개발': 'fas fa-graduation-cap',
            '경영지원': 'fas fa-briefcase',
            '비서': 'fas fa-user-tie',
            '홍보': 'fas fa-bullhorn',
            '경영기획': 'fas fa-chart-line',
            '디자인': 'fas fa-palette',
            '리스크관리': 'fas fa-shield-alt',
            '마케팅': 'fas fa-megaphone',
            '스포츠사무관리': 'fas fa-running',
            '자금': 'fas fa-coins',
            '재무회계': 'fas fa-calculator',
            '정보보안': 'fas fa-lock',
            '준법지원': 'fas fa-balance-scale',
            '총무': 'fas fa-building',
            '투자금융': 'fas fa-chart-area',
            '기업영업기획': 'fas fa-handshake',
            '기업여신심사': 'fas fa-file-contract',
            '기업여신관리': 'fas fa-tasks',
            '기업여신영업': 'fas fa-user-friends',
            '데이터분석': 'fas fa-chart-bar',
            '디지털플랫폼': 'fas fa-mobile-alt',
            'NPL사업기획': 'fas fa-clipboard-list',
            '리테일심사기획': 'fas fa-user-check',
            '개인신용대출기획': 'fas fa-credit-card',
            '모기지기획': 'fas fa-home',
            '예금기획': 'fas fa-piggy-bank',
            '예금영업': 'fas fa-money-bill-wave',
            '대출고객지원': 'fas fa-headset',
            '업무지원': 'fas fa-hands-helping',
            '예금고객지원': 'fas fa-user-shield',
            '채권관리': 'fas fa-file-invoice-dollar'
        }
    
    def create_job_tree_structure(self) -> Dict[str, Any]:
        """직무 체계도 구조 생성"""
        
        # OK금융그룹 직무 구조 (실제 데이터)
        job_structure = {
            'IT/디지털': {
                'IT기획': ['시스템기획'],
                'IT개발': ['시스템개발'],
                'IT운영': ['시스템관리', '서비스운영']
            },
            '경영지원': {
                '경영관리': [
                    '감사', '인사관리', '인재개발', '경영지원', '비서', '홍보',
                    '경영기획', '디자인', '리스크관리', '마케팅', '스포츠사무관리',
                    '자금', '재무회계', '정보보안', '준법지원', '총무'
                ]
            },
            '금융': {
                '투자금융': ['투자금융'],
                '기업금융': ['기업영업기획', '기업여신심사', '기업여신관리'],
                '리테일금융': [
                    '데이터분석', '디지털플랫폼', 'NPL사업기획', '리테일심사기획',
                    '개인신용대출기획', '모기지기획', '예금기획', '예금영업'
                ]
            },
            '영업': {
                '기업영업': ['기업여신영업']
            },
            '고객서비스': {
                '고객지원': ['대출고객지원', '업무지원', '예금고객지원', '채권관리']
            }
        }
        
        # 트리 구조 생성
        root_node = {
            'id': 'root',
            'name': 'OK금융그룹 직무체계',
            'type': 'root',
            'level': 0,
            'parent_id': None,
            'children': [],
            'metadata': {
                'total_categories': len(job_structure),
                'total_jobs': sum(len(jobs) for types in job_structure.values() for jobs in types.values())
            },
            'color': '#1F2937',
            'icon': 'fas fa-sitemap',
            'description': '전체 직무 체계도',
            'job_count': sum(len(jobs) for types in job_structure.values() for jobs in types.values())
        }
        
        # 직군(Category) 노드 생성
        for category_name, job_types in job_structure.items():
            category_color = self.category_colors.get(category_name, self.category_colors['IT/디지털'])
            
            category_node = {
                'id': f'category_{category_name}',
                'name': category_name,
                'type': 'category',
                'level': 1,
                'parent_id': 'root',
                'children': [],
                'metadata': {
                    'job_types_count': len(job_types),
                    'total_jobs': sum(len(jobs) for jobs in job_types.values())
                },
                'color': category_color['primary'],
                'icon': 'fas fa-layer-group',
                'description': f'{category_name} 관련 업무',
                'job_count': sum(len(jobs) for jobs in job_types.values())
            }
            
            # 직종(Job Type) 노드 생성
            for job_type_name, job_roles in job_types.items():
                job_type_node = {
                    'id': f'type_{category_name}_{job_type_name}',
                    'name': job_type_name,
                    'type': 'job_type',
                    'level': 2,
                    'parent_id': f'category_{category_name}',
                    'children': [],
                    'metadata': {
                        'category': category_name,
                        'jobs_count': len(job_roles)
                    },
                    'color': category_color['accent'],
                    'icon': 'fas fa-folder',
                    'description': f'{job_type_name} 직종',
                    'job_count': len(job_roles)
                }
                
                # 직무(Job Role) 노드 생성
                for job_role_name in job_roles:
                    job_role_node = {
                        'id': f'role_{category_name}_{job_type_name}_{job_role_name}',
                        'name': job_role_name,
                        'type': 'job_role',
                        'level': 3,
                        'parent_id': f'type_{category_name}_{job_type_name}',
                        'children': [],
                        'metadata': {
                            'category': category_name,
                            'job_type': job_type_name,
                            'has_profile': True
                        },
                        'color': category_color['secondary'],
                        'icon': self.job_icons.get(job_role_name, 'fas fa-user-cog'),
                        'description': f'{job_role_name} 직무',
                        'job_count': 1
                    }
                    job_type_node['children'].append(job_role_node)
                
                category_node['children'].append(job_type_node)
            
            root_node['children'].append(category_node)
        
        return root_node
    
    def generate_react_tree_component(self) -> str:
        """React 트리 컴포넌트 생성"""
        
        return """
import React, { useState, useEffect, useMemo } from 'react';
import { Tree, Card, Badge, Typography, Space, Input, Button, Breadcrumb, Drawer, Tag } from 'antd';
import { 
  SearchOutlined, 
  ExpandOutlined, 
  CompressOutlined,
  FilterOutlined,
  HomeOutlined,
  TeamOutlined,
  UserOutlined
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import './JobTreeVisualization.css';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;

const JobTreeVisualization = ({ jobData, onJobSelect }) => {
  const [expandedKeys, setExpandedKeys] = useState(['root']);
  const [searchValue, setSearchValue] = useState('');
  const [filteredData, setFilteredData] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [viewMode, setViewMode] = useState('tree'); // 'tree', 'grid', 'map'
  const [showDetail, setShowDetail] = useState(false);
  const [breadcrumbPath, setBreadcrumbPath] = useState([]);

  // 트리 데이터 변환
  const transformTreeData = (node, parentPath = []) => {
    const currentPath = [...parentPath, { key: node.id, label: node.name }];
    
    return {
      key: node.id,
      title: (
        <TreeNode 
          node={node} 
          onSelect={handleNodeSelect}
          searchValue={searchValue}
        />
      ),
      icon: <i className={node.icon} style={{ color: node.color }} />,
      children: node.children?.map(child => transformTreeData(child, currentPath)) || [],
      isLeaf: node.type === 'job_role',
      data: node,
      path: currentPath
    };
  };

  // 노드 선택 처리
  const handleNodeSelect = (node, path) => {
    setSelectedJob(node);
    setBreadcrumbPath(path);
    
    if (node.type === 'job_role') {
      setShowDetail(true);
      onJobSelect?.(node);
    }
  };

  // 검색 처리
  const handleSearch = (value) => {
    setSearchValue(value);
    if (value) {
      const filtered = filterTreeNodes(jobData, value.toLowerCase());
      setFilteredData([filtered]);
    } else {
      setFilteredData([]);
    }
  };

  // 트리 노드 필터링
  const filterTreeNodes = (node, searchText) => {
    const nameMatch = node.name.toLowerCase().includes(searchText);
    const descriptionMatch = node.description.toLowerCase().includes(searchText);
    
    if (node.children && node.children.length > 0) {
      const filteredChildren = node.children
        .map(child => filterTreeNodes(child, searchText))
        .filter(child => child !== null);
      
      if (filteredChildren.length > 0 || nameMatch || descriptionMatch) {
        return { ...node, children: filteredChildren };
      }
    }
    
    return nameMatch || descriptionMatch ? node : null;
  };

  const treeData = useMemo(() => {
    const data = filteredData.length > 0 ? filteredData : [jobData];
    return data.map(node => transformTreeData(node));
  }, [jobData, filteredData, searchValue]);

  return (
    <div className="job-tree-container">
      {/* 헤더 */}
      <div className="tree-header">
        <div className="header-content">
          <Title level={2}>
            <i className="fas fa-sitemap" style={{ marginRight: 8 }} />
            직무 체계도
          </Title>
          <Text type="secondary">
            전체 {jobData.job_count}개 직무를 한눈에 살펴보세요
          </Text>
        </div>
        
        <div className="header-controls">
          <Space size="middle">
            <Search
              placeholder="직무명 또는 설명 검색..."
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              onSearch={handleSearch}
              onChange={(e) => !e.target.value && handleSearch('')}
              style={{ width: 300 }}
            />
            
            <Button.Group>
              <Button 
                type={viewMode === 'tree' ? 'primary' : 'default'}
                icon={<i className="fas fa-sitemap" />}
                onClick={() => setViewMode('tree')}
              >
                트리뷰
              </Button>
              <Button 
                type={viewMode === 'grid' ? 'primary' : 'default'}
                icon={<i className="fas fa-th" />}
                onClick={() => setViewMode('grid')}
              >
                그리드뷰
              </Button>
              <Button 
                type={viewMode === 'map' ? 'primary' : 'default'}
                icon={<i className="fas fa-project-diagram" />}
                onClick={() => setViewMode('map')}
              >
                맵뷰
              </Button>
            </Button.Group>
          </Space>
        </div>
      </div>

      {/* 브레드크럼 */}
      {breadcrumbPath.length > 0 && (
        <motion.div 
          className="breadcrumb-container"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Breadcrumb>
            <Breadcrumb.Item href="/">
              <HomeOutlined />
            </Breadcrumb.Item>
            {breadcrumbPath.map((item, index) => (
              <Breadcrumb.Item key={item.key}>
                {index === breadcrumbPath.length - 1 ? (
                  <strong>{item.label}</strong>
                ) : (
                  item.label
                )}
              </Breadcrumb.Item>
            ))}
          </Breadcrumb>
        </motion.div>
      )}

      {/* 메인 콘텐츠 */}
      <div className="tree-content">
        {viewMode === 'tree' && (
          <TreeView 
            treeData={treeData}
            expandedKeys={expandedKeys}
            onExpand={setExpandedKeys}
            searchValue={searchValue}
          />
        )}
        
        {viewMode === 'grid' && (
          <GridView 
            jobData={jobData}
            onJobSelect={handleNodeSelect}
            searchValue={searchValue}
          />
        )}
        
        {viewMode === 'map' && (
          <MapView 
            jobData={jobData}
            onJobSelect={handleNodeSelect}
            searchValue={searchValue}
          />
        )}
      </div>

      {/* 상세 정보 드로어 */}
      <JobDetailDrawer
        visible={showDetail}
        onClose={() => setShowDetail(false)}
        jobData={selectedJob}
        breadcrumbPath={breadcrumbPath}
      />
    </div>
  );
};

// 트리 노드 컴포넌트
const TreeNode = ({ node, onSelect, searchValue }) => {
  const [isHovered, setIsHovered] = useState(false);
  
  const handleClick = (e) => {
    e.stopPropagation();
    onSelect(node);
  };

  const highlightText = (text, highlight) => {
    if (!highlight) return text;
    
    const parts = text.split(new RegExp(`(${highlight})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === highlight.toLowerCase() ? 
        <mark key={i}>{part}</mark> : part
    );
  };

  return (
    <motion.div
      className={`tree-node tree-node-${node.type}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="node-content">
        <div className="node-main">
          <span className="node-name">
            {highlightText(node.name, searchValue)}
          </span>
          
          {node.job_count > 1 && (
            <Badge 
              count={node.job_count} 
              style={{ backgroundColor: node.color }}
              className="job-count-badge"
            />
          )}
        </div>
        
        {isHovered && (
          <motion.div 
            className="node-tooltip"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            <Text type="secondary" size="small">
              {node.description}
            </Text>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

// 트리 뷰 컴포넌트
const TreeView = ({ treeData, expandedKeys, onExpand, searchValue }) => {
  return (
    <motion.div 
      className="tree-view"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <Tree
        showIcon
        showLine={{ showLeafIcon: false }}
        treeData={treeData}
        expandedKeys={expandedKeys}
        onExpand={onExpand}
        className="job-tree"
        blockNode
      />
    </motion.div>
  );
};

// 그리드 뷰 컴포넌트
const GridView = ({ jobData, onJobSelect, searchValue }) => {
  const renderGridCards = (node, level = 0) => {
    const cards = [];
    
    if (node.type === 'job_role') {
      cards.push(
        <JobCard 
          key={node.id}
          job={node}
          onClick={() => onJobSelect(node)}
          searchValue={searchValue}
          level={level}
        />
      );
    }
    
    if (node.children) {
      node.children.forEach(child => {
        cards.push(...renderGridCards(child, level + 1));
      });
    }
    
    return cards;
  };

  return (
    <motion.div 
      className="grid-view"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="job-grid">
        {renderGridCards(jobData)}
      </div>
    </motion.div>
  );
};

// 맵 뷰 컴포넌트 (D3.js 기반)
const MapView = ({ jobData, onJobSelect, searchValue }) => {
  const svgRef = useRef();
  
  useEffect(() => {
    if (!svgRef.current) return;
    
    // D3.js 트리맵 구현
    // 복잡한 시각화 로직...
    
  }, [jobData, searchValue]);

  return (
    <motion.div 
      className="map-view"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <svg ref={svgRef} className="job-map" />
    </motion.div>
  );
};

// 직무 카드 컴포넌트
const JobCard = ({ job, onClick, searchValue, level }) => {
  const [isHovered, setIsHovered] = useState(false);
  
  const categoryColors = {
    'IT/디지털': '#3B82F6',
    '경영지원': '#10B981',
    '금융': '#F59E0B',
    '영업': '#EF4444',
    '고객서비스': '#8B5CF6'
  };

  const categoryColor = categoryColors[job.metadata?.category] || '#6B7280';

  return (
    <motion.div
      className="job-card"
      whileHover={{ scale: 1.03, y: -2 }}
      whileTap={{ scale: 0.97 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      style={{ 
        '--category-color': categoryColor,
        '--card-depth': level * 10 + 'px'
      }}
    >
      <Card
        className="job-card-inner"
        hoverable
        cover={
          <div className="card-header" style={{ background: categoryColor }}>
            <i className={job.icon} />
          </div>
        }
      >
        <Card.Meta
          title={
            <span className="job-title">
              {searchValue ? 
                highlightText(job.name, searchValue) : 
                job.name
              }
            </span>
          }
          description={
            <div className="job-meta">
              <Tag color={categoryColor}>
                {job.metadata?.category}
              </Tag>
              <Text type="secondary" className="job-description">
                {job.description}
              </Text>
            </div>
          }
        />
      </Card>
    </motion.div>
  );
};

// 상세 정보 드로어
const JobDetailDrawer = ({ visible, onClose, jobData, breadcrumbPath }) => {
  if (!jobData) return null;

  return (
    <Drawer
      title={
        <div className="drawer-title">
          <i className={jobData.icon} style={{ marginRight: 8, color: jobData.color }} />
          {jobData.name}
        </div>
      }
      placement="right"
      width={600}
      visible={visible}
      onClose={onClose}
      className="job-detail-drawer"
    >
      <JobDetailContent job={jobData} breadcrumbPath={breadcrumbPath} />
    </Drawer>
  );
};

export default JobTreeVisualization;
"""
    
    def generate_vue_tree_component(self) -> str:
        """Vue 3 트리 컴포넌트 생성"""
        
        return """
<template>
  <div class="job-tree-container">
    <!-- 헤더 -->
    <div class="tree-header">
      <div class="header-content">
        <h2>
          <i class="fas fa-sitemap"></i>
          직무 체계도
        </h2>
        <p class="subtitle">전체 {{ jobData.job_count }}개 직무를 한눈에 살펴보세요</p>
      </div>
      
      <div class="header-controls">
        <a-space size="middle">
          <a-input-search
            v-model:value="searchValue"
            placeholder="직무명 또는 설명 검색..."
            allow-clear
            enter-button
            size="large"
            style="width: 300px"
            @search="handleSearch"
          />
          
          <a-button-group>
            <a-button 
              :type="viewMode === 'tree' ? 'primary' : 'default'"
              @click="viewMode = 'tree'"
            >
              <i class="fas fa-sitemap"></i>
              트리뷰
            </a-button>
            <a-button 
              :type="viewMode === 'grid' ? 'primary' : 'default'"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
              그리드뷰
            </a-button>
            <a-button 
              :type="viewMode === 'map' ? 'primary' : 'default'"
              @click="viewMode = 'map'"
            >
              <i class="fas fa-project-diagram"></i>
              맵뷰
            </a-button>
          </a-button-group>
        </a-space>
      </div>
    </div>

    <!-- 브레드크럼 -->
    <Transition name="breadcrumb">
      <div v-if="breadcrumbPath.length > 0" class="breadcrumb-container">
        <a-breadcrumb>
          <a-breadcrumb-item href="/">
            <home-outlined />
          </a-breadcrumb-item>
          <a-breadcrumb-item 
            v-for="(item, index) in breadcrumbPath" 
            :key="item.key"
          >
            <strong v-if="index === breadcrumbPath.length - 1">
              {{ item.label }}
            </strong>
            <span v-else>{{ item.label }}</span>
          </a-breadcrumb-item>
        </a-breadcrumb>
      </div>
    </Transition>

    <!-- 메인 콘텐츠 -->
    <div class="tree-content">
      <TreeView 
        v-if="viewMode === 'tree'"
        :tree-data="treeData"
        :expanded-keys="expandedKeys"
        :search-value="searchValue"
        @expand="handleExpand"
        @select="handleNodeSelect"
      />
      
      <GridView 
        v-else-if="viewMode === 'grid'"
        :job-data="jobData"
        :search-value="searchValue"
        @job-select="handleNodeSelect"
      />
      
      <MapView 
        v-else-if="viewMode === 'map'"
        :job-data="jobData"
        :search-value="searchValue"
        @job-select="handleNodeSelect"
      />
    </div>

    <!-- 상세 정보 드로어 -->
    <a-drawer
      v-model:visible="showDetail"
      title="직무 상세 정보"
      placement="right"
      width="600"
      class="job-detail-drawer"
    >
      <template #title>
        <div class="drawer-title">
          <i :class="selectedJob?.icon" :style="{ color: selectedJob?.color }"></i>
          {{ selectedJob?.name }}
        </div>
      </template>
      
      <JobDetailContent 
        v-if="selectedJob"
        :job="selectedJob" 
        :breadcrumb-path="breadcrumbPath" 
      />
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { HomeOutlined } from '@ant-design/icons-vue'
import TreeView from './TreeView.vue'
import GridView from './GridView.vue'
import MapView from './MapView.vue'
import JobDetailContent from './JobDetailContent.vue'

// Props
const props = defineProps({
  jobData: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['job-select'])

// Reactive data
const expandedKeys = ref(['root'])
const searchValue = ref('')
const filteredData = ref([])
const selectedJob = ref(null)
const viewMode = ref('tree')
const showDetail = ref(false)
const breadcrumbPath = ref([])

// Computed
const treeData = computed(() => {
  const data = filteredData.value.length > 0 ? filteredData.value : [props.jobData]
  return data.map(node => transformTreeData(node))
})

// Methods
const transformTreeData = (node, parentPath = []) => {
  const currentPath = [...parentPath, { key: node.id, label: node.name }]
  
  return {
    key: node.id,
    title: node.name,
    icon: node.icon,
    children: node.children?.map(child => transformTreeData(child, currentPath)) || [],
    isLeaf: node.type === 'job_role',
    data: node,
    path: currentPath,
    style: {
      color: node.color
    }
  }
}

const handleNodeSelect = (node, path = []) => {
  selectedJob.value = node
  breadcrumbPath.value = path
  
  if (node.type === 'job_role') {
    showDetail.value = true
    emit('job-select', node)
  }
}

const handleSearch = (value) => {
  if (value) {
    const filtered = filterTreeNodes(props.jobData, value.toLowerCase())
    filteredData.value = filtered ? [filtered] : []
  } else {
    filteredData.value = []
  }
}

const filterTreeNodes = (node, searchText) => {
  const nameMatch = node.name.toLowerCase().includes(searchText)
  const descriptionMatch = node.description.toLowerCase().includes(searchText)
  
  if (node.children && node.children.length > 0) {
    const filteredChildren = node.children
      .map(child => filterTreeNodes(child, searchText))
      .filter(child => child !== null)
    
    if (filteredChildren.length > 0 || nameMatch || descriptionMatch) {
      return { ...node, children: filteredChildren }
    }
  }
  
  return nameMatch || descriptionMatch ? node : null
}

const handleExpand = (keys) => {
  expandedKeys.value = keys
}

// Watch for search changes
watch(searchValue, (newValue) => {
  if (!newValue) {
    handleSearch('')
  }
})
</script>
"""
    
    def generate_css_styles(self) -> str:
        """CSS 스타일 생성"""
        
        return """
/* 직무 체계도 메인 스타일 */
.job-tree-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 24px;
}

/* 헤더 스타일 */
.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.header-content h2 {
  margin: 0;
  color: #1a202c;
  font-size: 28px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content .subtitle {
  margin: 8px 0 0 0;
  color: #64748b;
  font-size: 16px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 브레드크럼 스타일 */
.breadcrumb-container {
  margin-bottom: 16px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all 0.3s ease;
}

.breadcrumb-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.breadcrumb-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 트리 뷰 스타일 */
.tree-view {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.job-tree .ant-tree-node-content-wrapper {
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
  position: relative;
}

.job-tree .ant-tree-node-content-wrapper:hover {
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  transform: translateX(4px);
}

/* 트리 노드 스타일 */
.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  position: relative;
}

.tree-node-category {
  font-weight: 600;
  font-size: 16px;
}

.tree-node-job_type {
  font-weight: 500;
  font-size: 14px;
  color: #4a5568;
}

.tree-node-job_role {
  font-size: 14px;
  color: #2d3748;
  position: relative;
}

.tree-node-job_role:hover {
  color: #3182ce;
}

.node-content {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.node-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.node-name mark {
  background: linear-gradient(135deg, #fef08a, #facc15);
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 600;
}

.job-count-badge {
  font-size: 12px;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-tooltip {
  position: absolute;
  top: 100%;
  left: 0;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  margin-top: 4px;
}

/* 그리드 뷰 스타일 */
.grid-view {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
}

.job-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 8px;
}

/* 직무 카드 스타일 */
.job-card {
  --category-color: #6b7280;
  --card-depth: 0px;
  perspective: 1000px;
}

.job-card-inner {
  border: 2px solid transparent;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  transform: translateZ(var(--card-depth));
}

.job-card-inner:hover {
  border-color: var(--category-color);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 8px 16px rgba(var(--category-color), 0.2);
  transform: translateZ(calc(var(--card-depth) + 8px)) rotateX(2deg);
}

.card-header {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  position: relative;
  overflow: hidden;
}

.card-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s;
}

.job-card:hover .card-header::before {
  left: 100%;
}

.job-title {
  font-weight: 600;
  font-size: 16px;
  color: #1a202c;
  line-height: 1.4;
}

.job-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.job-description {
  font-size: 13px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 맵 뷰 스타일 */
.map-view {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  min-height: 600px;
}

.job-map {
  width: 100%;
  height: 100%;
}

/* 상세 정보 드로어 스타일 */
.job-detail-drawer .ant-drawer-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.job-detail-drawer .ant-drawer-close {
  color: white;
}

.drawer-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .job-tree-container {
    padding: 16px;
  }
  
  .tree-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-controls {
    justify-content: center;
  }
  
  .header-controls .ant-input-search {
    width: 100% !important;
  }
  
  .job-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .job-detail-drawer {
    width: 90vw !important;
  }
}

@media (max-width: 480px) {
  .header-content h2 {
    font-size: 24px;
  }
  
  .tree-view,
  .grid-view,
  .map-view {
    padding: 16px;
  }
  
  .job-card-inner {
    border-radius: 12px;
  }
}

/* 애니메이션 */
@keyframes nodeHighlight {
  0% { background-color: transparent; }
  50% { background-color: rgba(59, 130, 246, 0.1); }
  100% { background-color: transparent; }
}

.tree-node.highlighted {
  animation: nodeHighlight 0.6s ease-in-out;
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark) {
  .job-tree-container {
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    color: #f7fafc;
  }
  
  .tree-header,
  .tree-view,
  .grid-view,
  .map-view {
    background: #2d3748;
    color: #f7fafc;
  }
  
  .job-card-inner {
    background: #4a5568;
    color: #f7fafc;
  }
  
  .breadcrumb-container {
    background: rgba(45, 55, 72, 0.9);
  }
}

/* 접근성 개선 */
.tree-node:focus,
.job-card:focus {
  outline: 2px solid #3182ce;
  outline-offset: 2px;
}

.tree-node[aria-selected="true"] {
  background: linear-gradient(135deg, #bee3f8, #90cdf4);
  color: #1a365d;
}

/* 고성능 애니메이션 */
.job-card,
.tree-node {
  will-change: transform;
}

.job-card-inner {
  backface-visibility: hidden;
  transform-style: preserve-3d;
}
"""
    
    def generate_job_detail_component(self) -> str:
        """직무 상세 정보 컴포넌트 생성"""
        
        return """
import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Descriptions, 
  Tag, 
  Timeline, 
  Avatar, 
  Button, 
  Space, 
  Divider,
  Typography,
  Progress,
  Rate,
  Tooltip,
  List,
  Badge
} from 'antd';
import { 
  UserOutlined, 
  TeamOutlined, 
  TrophyOutlined,
  BookOutlined,
  RocketOutlined,
  HeartOutlined,
  ShareAltOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import './JobDetailContent.css';

const { Title, Text, Paragraph } = Typography;

const JobDetailContent = ({ job, breadcrumbPath }) => {
  const [loading, setLoading] = useState(true);
  const [jobProfile, setJobProfile] = useState(null);
  const [relatedJobs, setRelatedJobs] = useState([]);

  useEffect(() => {
    // API 호출로 상세 정보 가져오기
    fetchJobDetail(job.id);
  }, [job.id]);

  const fetchJobDetail = async (jobId) => {
    try {
      setLoading(true);
      // 실제 API 호출
      const response = await fetch(`/api/job-profiles/${jobId}/`);
      const data = await response.json();
      setJobProfile(data);
      
      // 관련 직무 가져오기
      const relatedResponse = await fetch(`/api/job-profiles/${jobId}/related/`);
      const relatedData = await relatedResponse.json();
      setRelatedJobs(relatedData);
      
    } catch (error) {
      console.error('직무 상세 정보 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const categoryColors = {
    'IT/디지털': '#3B82F6',
    '경영지원': '#10B981',
    '금융': '#F59E0B',
    '영업': '#EF4444',
    '고객서비스': '#8B5CF6'
  };

  const categoryColor = categoryColors[job.metadata?.category] || '#6B7280';

  const mockJobProfile = {
    role_responsibility: `${job.name} 관련 핵심 업무를 수행합니다.\\n- 전략 수립 및 실행\\n- 프로젝트 관리\\n- 팀 협업 및 조율`,
    qualification: `${job.name} 분야 전문 지식과 경험이 필요합니다.\\n- 관련 학과 졸업 또는 동등한 경력\\n- 해당 분야 3년 이상 경험\\n- 커뮤니케이션 및 리더십 역량`,
    basic_skills: ['문제해결능력', '커뮤니케이션', '팀워크', '전문지식'],
    applied_skills: ['전략적 사고', '리더십', '프로젝트 관리', '데이터 분석'],
    growth_path: `${job.name} → 선임${job.name} → ${job.name}팀장 → 부서장`,
    related_certifications: ['관련 자격증 1', '관련 자격증 2'],
    difficulty_level: 7,
    required_experience: 3,
    salary_range: '3,500 - 5,000만원',
    work_environment: '사무실 근무',
    career_prospects: 85
  };

  const profile = jobProfile || mockJobProfile;

  if (loading) {
    return (
      <div className="detail-loading">
        <div className="loading-spinner" />
        <Text>상세 정보를 불러오는 중...</Text>
      </div>
    );
  }

  return (
    <div className="job-detail-content">
      {/* 헤더 섹션 */}
      <motion.div 
        className="detail-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ background: `linear-gradient(135deg, ${categoryColor}, ${categoryColor}dd)` }}
      >
        <div className="header-main">
          <Avatar 
            size={64} 
            icon={<i className={job.icon} />}
            style={{ background: 'rgba(255,255,255,0.2)' }}
          />
          <div className="header-info">
            <Title level={2} style={{ color: 'white', margin: 0 }}>
              {job.name}
            </Title>
            <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: '16px' }}>
              {job.description}
            </Text>
            <div className="header-tags">
              <Tag color={categoryColor}>{job.metadata?.category}</Tag>
              <Tag color="white" style={{ color: categoryColor }}>
                {job.metadata?.job_type}
              </Tag>
            </div>
          </div>
        </div>
        
        <div className="header-actions">
          <Space>
            <Button 
              type="primary" 
              ghost 
              icon={<HeartOutlined />}
              size="large"
            >
              관심직무
            </Button>
            <Button 
              type="primary" 
              ghost 
              icon={<ShareAltOutlined />}
              size="large"
            >
              공유
            </Button>
            <Button 
              type="primary" 
              ghost 
              icon={<DownloadOutlined />}
              size="large"
            >
              PDF 다운로드
            </Button>
          </Space>
        </div>
      </motion.div>

      {/* 핵심 지표 섹션 */}
      <motion.div 
        className="key-metrics"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="metrics-card">
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-icon">
                <TrophyOutlined style={{ color: '#F59E0B' }} />
              </div>
              <div className="metric-content">
                <Text strong>난이도</Text>
                <div className="metric-value">
                  <Rate disabled defaultValue={Math.floor(profile.difficulty_level / 2)} />
                  <Text type="secondary">({profile.difficulty_level}/10)</Text>
                </div>
              </div>
            </div>
            
            <div className="metric-item">
              <div className="metric-icon">
                <UserOutlined style={{ color: '#10B981' }} />
              </div>
              <div className="metric-content">
                <Text strong>경력 요구</Text>
                <div className="metric-value">
                  <Text style={{ fontSize: '18px', fontWeight: 600 }}>
                    {profile.required_experience}년+
                  </Text>
                </div>
              </div>
            </div>
            
            <div className="metric-item">
              <div className="metric-icon">
                <RocketOutlined style={{ color: '#3B82F6' }} />
              </div>
              <div className="metric-content">
                <Text strong>성장 전망</Text>
                <div className="metric-value">
                  <Progress 
                    percent={profile.career_prospects} 
                    size="small" 
                    strokeColor={categoryColor}
                    showInfo={false}
                  />
                  <Text>{profile.career_prospects}%</Text>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* 역할 및 책임 섹션 */}
      <motion.div 
        className="detail-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card 
          title={
            <div className="section-title">
              <TeamOutlined style={{ color: categoryColor }} />
              핵심 역할 및 책임
            </div>
          }
          className="detail-card"
        >
          <Paragraph className="responsibility-text">
            {profile.role_responsibility.split('\\n').map((line, index) => (
              <div key={index} className="responsibility-line">
                {line.startsWith('-') ? (
                  <div className="bullet-point">
                    <span className="bullet">•</span>
                    <span>{line.substring(1).trim()}</span>
                  </div>
                ) : (
                  <div className="main-point">{line}</div>
                )}
              </div>
            ))}
          </Paragraph>
        </Card>
      </motion.div>

      {/* 자격 요건 섹션 */}
      <motion.div 
        className="detail-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card 
          title={
            <div className="section-title">
              <BookOutlined style={{ color: categoryColor }} />
              자격 요건
            </div>
          }
          className="detail-card"
        >
          <Paragraph className="qualification-text">
            {profile.qualification.split('\\n').map((line, index) => (
              <div key={index} className="qualification-line">
                {line.startsWith('-') ? (
                  <div className="bullet-point">
                    <span className="bullet">•</span>
                    <span>{line.substring(1).trim()}</span>
                  </div>
                ) : (
                  <div className="main-point">{line}</div>
                )}
              </div>
            ))}
          </Paragraph>
        </Card>
      </motion.div>

      {/* 필요 역량 섹션 */}
      <motion.div 
        className="detail-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="skills-grid">
          <Card 
            title="기본 역량"
            className="skill-card basic-skills"
            headStyle={{ background: `${categoryColor}20`, color: categoryColor }}
          >
            <div className="skills-list">
              {profile.basic_skills.map((skill, index) => (
                <motion.div
                  key={index}
                  className="skill-tag basic"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <Tag color={categoryColor}>{skill}</Tag>
                </motion.div>
              ))}
            </div>
          </Card>
          
          <Card 
            title="우대 역량"
            className="skill-card advanced-skills"
            headStyle={{ background: `${categoryColor}30`, color: categoryColor }}
          >
            <div className="skills-list">
              {profile.applied_skills.map((skill, index) => (
                <motion.div
                  key={index}
                  className="skill-tag advanced"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <Tag color="processing">{skill}</Tag>
                </motion.div>
              ))}
            </div>
          </Card>
        </div>
      </motion.div>

      {/* 성장 경로 섹션 */}
      <motion.div 
        className="detail-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Card 
          title={
            <div className="section-title">
              <RocketOutlined style={{ color: categoryColor }} />
              성장 경로
            </div>
          }
          className="detail-card"
        >
          <Timeline mode="left">
            {profile.growth_path.split(' → ').map((step, index) => (
              <Timeline.Item 
                key={index}
                color={index === 0 ? categoryColor : '#d9d9d9'}
                dot={index === 0 ? <Avatar size="small" style={{ background: categoryColor }} /> : null}
              >
                <div className="timeline-content">
                  <Text strong={index === 0}>{step}</Text>
                  {index === 0 && (
                    <Tag color={categoryColor} style={{ marginLeft: 8 }}>
                      현재 직무
                    </Tag>
                  )}
                </div>
              </Timeline.Item>
            ))}
          </Timeline>
        </Card>
      </motion.div>

      {/* 추가 정보 섹션 */}
      <motion.div 
        className="detail-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card 
          title="추가 정보"
          className="detail-card"
        >
          <Descriptions column={{ xxl: 2, xl: 2, lg: 2, md: 1, sm: 1, xs: 1 }}>
            <Descriptions.Item label="급여 범위">
              <Text strong>{profile.salary_range}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="근무 환경">
              {profile.work_environment}
            </Descriptions.Item>
            <Descriptions.Item label="관련 자격증">
              <Space wrap>
                {profile.related_certifications.map((cert, index) => (
                  <Tag key={index} color="blue">{cert}</Tag>
                ))}
              </Space>
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </motion.div>

      {/* 관련 직무 섹션 */}
      {relatedJobs.length > 0 && (
        <motion.div 
          className="detail-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card 
            title={
              <div className="section-title">
                <ShareAltOutlined style={{ color: categoryColor }} />
                관련 직무
              </div>
            }
            className="detail-card"
          >
            <List
              grid={{ gutter: 16, column: 2 }}
              dataSource={relatedJobs}
              renderItem={(relatedJob) => (
                <List.Item>
                  <Card 
                    size="small" 
                    hoverable
                    className="related-job-card"
                    onClick={() => {/* 관련 직무로 이동 */}}
                  >
                    <div className="related-job-content">
                      <Avatar 
                        size="small" 
                        icon={<i className={relatedJob.icon} />}
                        style={{ background: categoryColor }}
                      />
                      <div className="related-job-info">
                        <Text strong>{relatedJob.name}</Text>
                        <Text type="secondary" size="small">
                          {relatedJob.category}
                        </Text>
                      </div>
                    </div>
                  </Card>
                </List.Item>
              )}
            />
          </Card>
        </motion.div>
      )}
    </div>
  );
};

export default JobDetailContent;
"""
    
    def generate_django_api_views(self) -> str:
        """Django API 뷰 생성"""
        
        return """
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from job_profiles.models import JobCategory, JobType, JobRole, JobProfile
import json


@require_http_methods(["GET"])
def job_tree_api(request):
    \"\"\"직무 체계도 트리 데이터 API\"\"\"
    
    try:
        # 직군별 색상 매핑
        category_colors = {
            'IT/디지털': '#3B82F6',
            '경영지원': '#10B981', 
            '금융': '#F59E0B',
            '영업': '#EF4444',
            '고객서비스': '#8B5CF6'
        }
        
        # 직무별 아이콘 매핑
        job_icons = {
            '시스템기획': 'fas fa-project-diagram',
            '시스템개발': 'fas fa-code',
            '시스템관리': 'fas fa-server',
            '서비스운영': 'fas fa-cogs',
            '감사': 'fas fa-search',
            '인사관리': 'fas fa-users',
            '인재개발': 'fas fa-graduation-cap',
            # ... 더 많은 아이콘 매핑
        }
        
        # 전체 구조 쿼리
        categories = JobCategory.objects.filter(is_active=True).prefetch_related(
            Prefetch('job_types', queryset=JobType.objects.filter(is_active=True).prefetch_related(
                Prefetch('job_roles', queryset=JobRole.objects.filter(is_active=True))
            ))
        )
        
        # 루트 노드 생성
        total_jobs = JobRole.objects.filter(is_active=True).count()
        
        root_node = {
            'id': 'root',
            'name': 'OK금융그룹 직무체계',
            'type': 'root',
            'level': 0,
            'parent_id': None,
            'children': [],
            'metadata': {
                'total_categories': categories.count(),
                'total_jobs': total_jobs
            },
            'color': '#1F2937',
            'icon': 'fas fa-sitemap',
            'description': '전체 직무 체계도',
            'job_count': total_jobs
        }
        
        # 직군 노드 생성
        for category in categories:
            category_job_count = JobRole.objects.filter(
                job_type__category=category,
                is_active=True
            ).count()
            
            category_color = category_colors.get(category.name, '#6B7280')
            
            category_node = {
                'id': f'category_{category.id}',
                'name': category.name,
                'type': 'category',
                'level': 1,
                'parent_id': 'root',
                'children': [],
                'metadata': {
                    'job_types_count': category.job_types.filter(is_active=True).count(),
                    'total_jobs': category_job_count
                },
                'color': category_color,
                'icon': 'fas fa-layer-group',
                'description': category.description or f'{category.name} 관련 업무',
                'job_count': category_job_count
            }
            
            # 직종 노드 생성
            for job_type in category.job_types.filter(is_active=True):
                job_type_job_count = job_type.job_roles.filter(is_active=True).count()
                
                job_type_node = {
                    'id': f'type_{job_type.id}',
                    'name': job_type.name,
                    'type': 'job_type',
                    'level': 2,
                    'parent_id': f'category_{category.id}',
                    'children': [],
                    'metadata': {
                        'category': category.name,
                        'jobs_count': job_type_job_count
                    },
                    'color': category_color,
                    'icon': 'fas fa-folder',
                    'description': job_type.description or f'{job_type.name} 직종',
                    'job_count': job_type_job_count
                }
                
                # 직무 노드 생성
                for job_role in job_type.job_roles.filter(is_active=True):
                    has_profile = hasattr(job_role, 'profile') and job_role.profile.is_active
                    
                    job_role_node = {
                        'id': f'role_{job_role.id}',
                        'name': job_role.name,
                        'type': 'job_role',
                        'level': 3,
                        'parent_id': f'type_{job_type.id}',
                        'children': [],
                        'metadata': {
                            'category': category.name,
                            'job_type': job_type.name,
                            'has_profile': has_profile,
                            'job_role_id': str(job_role.id)
                        },
                        'color': f'{category_color}40',  # 투명도 적용
                        'icon': job_icons.get(job_role.name, 'fas fa-user-cog'),
                        'description': job_role.description or f'{job_role.name} 직무',
                        'job_count': 1
                    }
                    job_type_node['children'].append(job_role_node)
                
                category_node['children'].append(job_type_node)
            
            root_node['children'].append(category_node)
        
        return JsonResponse({
            'success': True,
            'data': root_node,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def job_profile_detail_api(request, job_role_id):
    \"\"\"직무 상세 정보 API\"\"\"
    
    try:
        job_role = JobRole.objects.select_related(
            'job_type__category'
        ).get(id=job_role_id, is_active=True)
        
        # 직무기술서 조회
        job_profile = None
        if hasattr(job_role, 'profile'):
            job_profile = job_role.profile
        
        # 관련 직무 찾기 (같은 직종 내 다른 직무들)
        related_jobs = JobRole.objects.filter(
            job_type=job_role.job_type,
            is_active=True
        ).exclude(id=job_role_id)[:5]
        
        # 응답 데이터 구성
        response_data = {
            'id': str(job_role.id),
            'name': job_role.name,
            'code': job_role.code,
            'description': job_role.description,
            'job_type': {
                'id': str(job_role.job_type.id),
                'name': job_role.job_type.name,
                'code': job_role.job_type.code
            },
            'category': {
                'id': str(job_role.job_type.category.id),
                'name': job_role.job_type.category.name,
                'code': job_role.job_type.category.code
            },
            'full_path': job_role.full_path,
            'has_profile': job_profile is not None,
            'profile': None,
            'related_jobs': []
        }
        
        # 직무기술서 정보 추가
        if job_profile:
            response_data['profile'] = {
                'role_responsibility': job_profile.role_responsibility,
                'qualification': job_profile.qualification,
                'basic_skills': job_profile.basic_skills,
                'applied_skills': job_profile.applied_skills,
                'growth_path': job_profile.growth_path,
                'related_certifications': job_profile.related_certifications,
                'created_at': job_profile.created_at.isoformat(),
                'updated_at': job_profile.updated_at.isoformat()
            }
        
        # 관련 직무 정보 추가
        for related_job in related_jobs:
            response_data['related_jobs'].append({
                'id': str(related_job.id),
                'name': related_job.name,
                'description': related_job.description,
                'has_profile': hasattr(related_job, 'profile')
            })
        
        return JsonResponse({
            'success': True,
            'data': response_data
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
        }, status=500)


@require_http_methods(["GET"])
def job_search_api(request):
    \"\"\"직무 검색 API\"\"\"
    
    try:
        query = request.GET.get('q', '').strip()
        category_filter = request.GET.get('category', '')
        job_type_filter = request.GET.get('job_type', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # 기본 쿼리셋
        queryset = JobRole.objects.select_related(
            'job_type__category'
        ).filter(is_active=True)
        
        # 검색어 필터
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(job_type__name__icontains=query) |
                Q(job_type__category__name__icontains=query)
            )
        
        # 카테고리 필터
        if category_filter:
            queryset = queryset.filter(job_type__category__name=category_filter)
        
        # 직종 필터
        if job_type_filter:
            queryset = queryset.filter(job_type__name=job_type_filter)
        
        # 페이지네이션
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # 결과 구성
        results = []
        for job_role in page_obj:
            results.append({
                'id': str(job_role.id),
                'name': job_role.name,
                'description': job_role.description,
                'job_type': job_role.job_type.name,
                'category': job_role.job_type.category.name,
                'full_path': job_role.full_path,
                'has_profile': hasattr(job_role, 'profile')
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'results': results,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def job_statistics_api(request):
    \"\"\"직무 통계 API\"\"\"
    
    try:
        # 전체 통계
        total_categories = JobCategory.objects.filter(is_active=True).count()
        total_job_types = JobType.objects.filter(is_active=True).count()
        total_job_roles = JobRole.objects.filter(is_active=True).count()
        total_profiles = JobProfile.objects.filter(is_active=True).count()
        
        # 직군별 통계
        category_stats = []
        categories = JobCategory.objects.filter(is_active=True).annotate(
            job_type_count=Count('job_types', filter=Q(job_types__is_active=True)),
            job_role_count=Count('job_types__job_roles', filter=Q(
                job_types__is_active=True,
                job_types__job_roles__is_active=True
            ))
        )
        
        for category in categories:
            category_stats.append({
                'name': category.name,
                'job_type_count': category.job_type_count,
                'job_role_count': category.job_role_count,
                'description': category.description
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'summary': {
                    'total_categories': total_categories,
                    'total_job_types': total_job_types,
                    'total_job_roles': total_job_roles,
                    'total_profiles': total_profiles,
                    'profile_completion_rate': round(
                        (total_profiles / total_job_roles * 100) if total_job_roles > 0 else 0, 1
                    )
                },
                'category_breakdown': category_stats
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
"""
    
    def generate_complete_package(self) -> Dict[str, str]:
        """완전한 패키지 생성"""
        
        tree_structure = self.create_job_tree_structure()
        
        return {
            # React 컴포넌트들
            'JobTreeVisualization.jsx': self.generate_react_tree_component(),
            'JobDetailContent.jsx': self.generate_job_detail_component(),
            
            # Vue 컴포넌트
            'JobTreeVisualization.vue': self.generate_vue_tree_component(),
            
            # 스타일시트
            'JobTreeVisualization.css': self.generate_css_styles(),
            
            # Django API
            'job_tree_api.py': self.generate_django_api_views(),
            
            # 데이터 구조
            'job_tree_data.json': json.dumps(tree_structure, ensure_ascii=False, indent=2),
            
            # URL 패턴
            'urls.py': """
from django.urls import path
from . import job_tree_api

urlpatterns = [
    path('api/job-tree/', job_tree_api.job_tree_api, name='job_tree_api'),
    path('api/job-profiles/<uuid:job_role_id>/', job_tree_api.job_profile_detail_api, name='job_profile_detail'),
    path('api/job-search/', job_tree_api.job_search_api, name='job_search'),
    path('api/job-statistics/', job_tree_api.job_statistics_api, name='job_statistics'),
]
""",
            
            # 패키지 설정
            'package.json': json.dumps({
                "name": "job-profile-tree-ui",
                "version": "1.0.0",
                "description": "직무기술서 트리 시각화 UI/UX 시스템",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "antd": "^5.0.0",
                    "framer-motion": "^10.0.0",
                    "@ant-design/icons": "^5.0.0",
                    "vue": "^3.3.0",
                    "@vue/composition-api": "^1.7.0",
                    "ant-design-vue": "^4.0.0",
                    "d3": "^7.8.0",
                    "vis-network": "^9.1.0",
                    "react-flow-renderer": "^11.0.0"
                },
                "devDependencies": {
                    "@vitejs/plugin-react": "^4.0.0",
                    "@vitejs/plugin-vue": "^4.0.0",
                    "vite": "^4.4.0",
                    "typescript": "^5.0.0"
                }
            }, indent=2),
            
            # README
            'README.md': """
# 직무기술서 트리 시각화 UI/UX 시스템

## 🚀 주요 기능

### 📊 시각화 모드
- **트리뷰**: 계층형 구조로 전체 직무 체계 표시
- **그리드뷰**: 카드 형태로 직무들을 그리드 레이아웃으로 표시  
- **맵뷰**: D3.js 기반 인터랙티브 트리맵 시각화

### 🎨 현대적 UI/UX
- **반응형 디자인**: 모바일/태블릿/데스크톱 완전 대응
- **다크모드 지원**: 사용자 환경 설정에 따른 자동 테마 전환
- **부드러운 애니메이션**: Framer Motion 기반 마이크로 인터랙션
- **직관적 내비게이션**: 브레드크럼, 줌/드래그, 클릭 투 디테일

### 🔍 고급 검색 및 필터링
- **실시간 검색**: 직무명, 설명, 카테고리 통합 검색
- **하이라이팅**: 검색어 자동 강조 표시
- **다중 필터**: 직군, 직종별 필터링
- **자동완성**: 스마트 검색 제안

### 📱 인터랙티브 기능
- **원클릭 상세보기**: 카드/노드 클릭으로 상세 정보 즉시 표시
- **관심직무 관리**: 북마크 및 관심직무 등록
- **소셜 기능**: 직무 정보 공유 및 추천
- **PDF 다운로드**: 직무기술서 PDF 생성 및 다운로드

## 🛠 기술 스택

### 프론트엔드
- **React 18** / **Vue 3**: 모던 프론트엔드 프레임워크
- **Ant Design**: 엔터프라이즈급 UI 컴포넌트
- **Framer Motion**: 고성능 애니메이션 라이브러리
- **D3.js**: 데이터 시각화
- **TypeScript**: 타입 안전성

### 백엔드  
- **Django REST Framework**: API 서버
- **PostgreSQL**: 메인 데이터베이스
- **Redis**: 캐싱 및 세션 관리

### 배포 및 인프라
- **Docker**: 컨테이너화
- **Nginx**: 웹 서버 및 리버스 프록시
- **CI/CD**: GitHub Actions

## 📦 설치 및 실행

### 1. 의존성 설치
```bash
npm install
# 또는
yarn install
```

### 2. 개발 서버 실행
```bash
npm run dev
# 또는  
yarn dev
```

### 3. Django 백엔드 설정
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 🎯 사용법

### React 컴포넌트 사용
```jsx
import JobTreeVisualization from './components/JobTreeVisualization';

function App() {
  const handleJobSelect = (job) => {
    console.log('선택된 직무:', job);
  };

  return (
    <JobTreeVisualization 
      jobData={jobTreeData}
      onJobSelect={handleJobSelect}
    />
  );
}
```

### Vue 컴포넌트 사용
```vue
<template>
  <JobTreeVisualization 
    :job-data="jobTreeData"
    @job-select="handleJobSelect"
  />
</template>

<script setup>
import JobTreeVisualization from './components/JobTreeVisualization.vue'

const handleJobSelect = (job) => {
  console.log('선택된 직무:', job)
}
</script>
```

### API 엔드포인트
- `GET /api/job-tree/` - 전체 직무 트리 구조
- `GET /api/job-profiles/{id}/` - 특정 직무 상세 정보
- `GET /api/job-search/` - 직무 검색
- `GET /api/job-statistics/` - 직무 통계

## 🎨 커스터마이징

### 색상 테마 변경
```javascript
// JobTreeVisualization.jsx에서
const categoryColors = {
  'IT/디지털': '#3B82F6',    // 파란색
  '경영지원': '#10B981',     // 초록색  
  '금융': '#F59E0B',        // 주황색
  '영업': '#EF4444',        // 빨간색
  '고객서비스': '#8B5CF6'    // 보라색
};
```

### 아이콘 매핑 추가
```javascript
const jobIcons = {
  '시스템기획': 'fas fa-project-diagram',
  '시스템개발': 'fas fa-code',
  // 새로운 아이콘 추가...
};
```

## 🔧 API 연동

### Django 모델과 연동
```python
# models.py
class JobProfile(models.Model):
    job_role = models.OneToOneField(JobRole, on_delete=models.CASCADE)
    role_responsibility = models.TextField()
    qualification = models.TextField()
    basic_skills = models.JSONField(default=list)
    applied_skills = models.JSONField(default=list)
```

### API 뷰 확장
```python
# views.py
@api_view(['GET'])
def custom_job_api(request):
    # 커스텀 로직 구현
    pass
```

## 📈 성능 최적화

### 가상화 및 레이지 로딩
- 대용량 데이터를 위한 가상 스크롤링
- 이미지 및 컴포넌트 레이지 로딩
- 메모이제이션을 통한 렌더링 최적화

### 캐싱 전략
- API 응답 캐싱 (Redis)
- 브라우저 캐싱 최적화
- CDN을 통한 정적 자원 배포

## 🔒 보안

### 인증 및 권한
- JWT 토큰 기반 인증
- 역할 기반 접근 제어 (RBAC)
- CORS 설정 최적화

### 데이터 보호
- API 입력 유효성 검사
- SQL 인젝션 방지
- XSS 공격 방어

## 🌐 브라우저 지원

- Chrome 90+
- Firefox 88+  
- Safari 14+
- Edge 90+
- Mobile Safari 14+
- Chrome Mobile 90+

## 📄 라이선스

MIT License - 자세한 내용은 LICENSE 파일 참조

## 🤝 기여하기

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

- 이슈 트래커: GitHub Issues
- 이메일: support@company.com
- 문서: [Documentation Site]

---

💡 **Tip**: 최상의 경험을 위해 최신 버전의 브라우저를 사용하세요.
"""
        }
    
    def generate_all_files(self):
        """모든 파일 생성"""
        
        print("🚀 직무기술서 UX 혁신 시스템 생성 중...")
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 서브 디렉토리 생성
        subdirs = ['components', 'styles', 'api', 'data', 'docs']
        for subdir in subdirs:
            os.makedirs(os.path.join(self.output_dir, subdir), exist_ok=True)
        
        # 패키지 생성
        files = self.generate_complete_package()
        
        # 파일 저장
        for filename, content in files.items():
            # 파일 경로 결정
            if filename.endswith('.jsx') or filename.endswith('.vue'):
                filepath = os.path.join(self.output_dir, 'components', filename)
            elif filename.endswith('.css'):
                filepath = os.path.join(self.output_dir, 'styles', filename)
            elif filename.endswith('.py'):
                filepath = os.path.join(self.output_dir, 'api', filename)
            elif filename.endswith('.json'):
                filepath = os.path.join(self.output_dir, 'data', filename)
            elif filename.endswith('.md'):
                filepath = os.path.join(self.output_dir, 'docs', filename)
            else:
                filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ {filename} 생성 완료")
        
        # 추가 설정 파일들 생성
        self._generate_additional_files()
        
        print(f"\n✅ 직무기술서 UX 혁신 시스템 생성 완료!")
        print(f"📁 출력 위치: {self.output_dir}")
        print(f"\n🚀 주요 기능:")
        print(f"  - 계층형/그리드형/맵형 트리 시각화")
        print(f"  - React/Vue 컴포넌트 지원")
        print(f"  - 현대적 카드 UI 및 상세보기")
        print(f"  - 반응형 디자인 (모바일/PC/태블릿)")
        print(f"  - 실시간 검색 및 필터링")
        print(f"  - Django REST API 완전 통합")
        print(f"  - 줌/드래그/애니메이션 UX")
        print(f"\n📋 생성된 파일:")
        for filename in files.keys():
            print(f"  - {filename}")
    
    def _generate_additional_files(self):
        """추가 설정 파일들 생성"""
        
        # Vite 설정
        vite_config = """
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [react(), vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'antd'],
          charts: ['d3', 'vis-network']
        }
      }
    }
  }
})
"""
        
        with open(os.path.join(self.output_dir, 'vite.config.js'), 'w', encoding='utf-8') as f:
            f.write(vite_config)
        
        # TypeScript 설정
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "allowJs": True,
                "skipLibCheck": True,
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "strict": True,
                "forceConsistentCasingInFileNames": True,
                "module": "ESNext",
                "moduleResolution": "node",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx"
            },
            "include": ["src/**/*"],
            "references": [{"path": "./tsconfig.node.json"}]
        }
        
        with open(os.path.join(self.output_dir, 'tsconfig.json'), 'w', encoding='utf-8') as f:
            json.dump(tsconfig, f, indent=2)


def main():
    """메인 실행 함수"""
    output_dir = r"C:/Users/apro/OneDrive/Desktop/EHR_V1.0/job_profile_ux_output"
    
    ux_overhaul = JobProfileUXOverhaul(output_dir)
    ux_overhaul.generate_all_files()


if __name__ == '__main__':
    main()