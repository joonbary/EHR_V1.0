
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
    role_responsibility: `${job.name} 관련 핵심 업무를 수행합니다.\n- 전략 수립 및 실행\n- 프로젝트 관리\n- 팀 협업 및 조율`,
    qualification: `${job.name} 분야 전문 지식과 경험이 필요합니다.\n- 관련 학과 졸업 또는 동등한 경력\n- 해당 분야 3년 이상 경험\n- 커뮤니케이션 및 리더십 역량`,
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
            {profile.role_responsibility.split('\n').map((line, index) => (
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
            {profile.qualification.split('\n').map((line, index) => (
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
