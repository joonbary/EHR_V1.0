
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
