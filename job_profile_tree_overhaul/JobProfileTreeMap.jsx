import React, { useState, useEffect, useRef } from 'react';
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
  const iconMap = {
    "시스템기획": "sitemap",
    "시스템개발": "code",
    "시스템관리": "server",
    "서비스운영": "cogs",
    "감사": "shield-alt",
    "인사관리": "user-tie",
    "인재개발": "graduation-cap",
    "경영지원": "hands-helping",
    "비서": "user-clock",
    "홍보": "bullhorn",
    "경영기획": "chart-line",
    "디자인": "palette",
    "리스크관리": "exclamation-triangle",
    "마케팅": "chart-pie",
    "스포츠사무관리": "futbol",
    "자금": "coins",
    "재무회계": "calculator",
    "정보보안": "lock",
    "준법지원": "balance-scale",
    "총무": "building",
    "투자금융": "chart-bar",
    "기업영업기획": "handshake",
    "기업여신심사": "search-dollar",
    "기업여신관리": "tasks",
    "데이터분석": "database",
    "디지털플랫폼": "mobile-alt",
    "NPL사업기획": "file-invoice-dollar",
    "리테일심사기획": "user-check",
    "개인신용대출기획": "hand-holding-usd",
    "모기지기획": "home",
    "예금기획": "piggy-bank",
    "예금영업": "store",
    "기업여신영업": "briefcase",
    "대출고객지원": "headset",
    "업무지원": "life-ring",
    "예금고객지원": "comments",
    "채권관리": "file-contract"
};

  // 색상 스키마
  const colorScheme = {
    "primary": {
        "IT/디지털": "#3B82F6",
        "경영지원": "#8B5CF6",
        "금융": "#10B981",
        "영업": "#F59E0B",
        "고객서비스": "#EF4444"
    },
    "gradient": {
        "IT/디지털": "linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)",
        "경영지원": "linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)",
        "금융": "linear-gradient(135deg, #10B981 0%, #34D399 100%)",
        "영업": "linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%)",
        "고객서비스": "linear-gradient(135deg, #EF4444 0%, #F87171 100%)"
    }
};

  // 직무 구조
  const jobStructure = {
    "Non-PL": {
        "IT/디지털": {
            "color": "#3B82F6",
            "icon": "laptop",
            "jobs": {
                "IT기획": [
                    "시스템기획"
                ],
                "IT개발": [
                    "시스템개발"
                ],
                "IT운영": [
                    "시스템관리",
                    "서비스운영"
                ]
            }
        },
        "경영지원": {
            "color": "#8B5CF6",
            "icon": "briefcase",
            "jobs": {
                "경영관리": [
                    "감사",
                    "인사관리",
                    "인재개발",
                    "경영지원",
                    "비서",
                    "홍보",
                    "경영기획",
                    "디자인",
                    "리스크관리",
                    "마케팅",
                    "스포츠사무관리",
                    "자금",
                    "재무회계",
                    "정보보안",
                    "준법지원",
                    "총무"
                ]
            }
        },
        "금융": {
            "color": "#10B981",
            "icon": "dollar-sign",
            "jobs": {
                "투자금융": [
                    "투자금융"
                ],
                "기업금융": [
                    "기업영업기획",
                    "기업여신심사",
                    "기업여신관리"
                ],
                "리테일금융": [
                    "데이터분석",
                    "디지털플랫폼",
                    "NPL사업기획",
                    "리테일심사기획",
                    "개인신용대출기획",
                    "모기지기획",
                    "예금기획",
                    "예금영업"
                ]
            }
        },
        "영업": {
            "color": "#F59E0B",
            "icon": "users",
            "jobs": {
                "기업영업": [
                    "기업여신영업"
                ]
            }
        }
    },
    "PL": {
        "고객서비스": {
            "color": "#EF4444",
            "icon": "headphones",
            "jobs": {
                "고객지원": [
                    "대출고객지원",
                    "업무지원",
                    "예금고객지원",
                    "채권관리"
                ]
            }
        }
    }
};

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

export default JobProfileTreeMap;