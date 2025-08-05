// JobProfileTreeMap Component
const JobProfileTreeMap = ({ jobData, onJobSelect }) => {
  const [selectedGroup, setSelectedGroup] = React.useState(null);
  const [selectedCategory, setSelectedCategory] = React.useState(null);
  const [selectedJob, setSelectedJob] = React.useState(null);
  const [zoomLevel, setZoomLevel] = React.useState(1);
  const containerRef = React.useRef(null);

  // 아이콘 매핑 객체
  const iconMap = {
    "laptop": "fa-laptop",
    "briefcase": "fa-briefcase",
    "dollar-sign": "fa-dollar-sign",
    "users": "fa-users",
    "headphones": "fa-headphones",
    "folder": "fa-folder"
  };

  // 직무별 아이콘 매핑
  const jobIconMap = {
    "시스템기획": "fa-sitemap",
    "시스템개발": "fa-code",
    "시스템관리": "fa-server",
    "서비스운영": "fa-cogs",
    "감사": "fa-shield-alt",
    "인사관리": "fa-user-tie",
    "인재개발": "fa-graduation-cap",
    "경영지원": "fa-hands-helping",
    "비서": "fa-user-clock",
    "홍보": "fa-bullhorn",
    "경영기획": "fa-chart-line",
    "디자인": "fa-palette",
    "리스크관리": "fa-exclamation-triangle",
    "마케팅": "fa-chart-pie",
    "스포츠사무관리": "fa-futbol",
    "자금": "fa-coins",
    "재무회계": "fa-calculator",
    "정보보안": "fa-lock",
    "준법지원": "fa-balance-scale",
    "총무": "fa-building",
    "투자금융": "fa-chart-bar",
    "기업영업기획": "fa-handshake",
    "기업여신심사": "fa-search-dollar",
    "기업여신관리": "fa-tasks",
    "데이터분석": "fa-database",
    "디지털플랫폼": "fa-mobile-alt",
    "NPL사업기획": "fa-file-invoice-dollar",
    "리테일심사기획": "fa-user-check",
    "개인신용대출기획": "fa-hand-holding-usd",
    "모기지기획": "fa-home",
    "예금기획": "fa-piggy-bank",
    "예금영업": "fa-store",
    "기업여신영업": "fa-briefcase",
    "대출고객지원": "fa-headset",
    "업무지원": "fa-life-ring",
    "예금고객지원": "fa-comments",
    "채권관리": "fa-file-contract"
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

  // 직무 카드 컴포넌트
  const JobCard = ({ job, category, group, hasProfile }) => {
    const [isHovered, setIsHovered] = React.useState(false);
    
    return React.createElement(
      MaterialUI.Card,
      {
        className: "job-card",
        onClick: () => onJobSelect && onJobSelect({ 
          jobId: job.id,
          jobName: job.name,
          category,
          group,
          hasProfile
        }),
        onMouseEnter: () => setIsHovered(true),
        onMouseLeave: () => setIsHovered(false),
        sx: {
          cursor: 'pointer',
          background: isHovered ? colorScheme.gradient[category] : '#ffffff',
          border: `2px solid ${hasProfile ? colorScheme.primary[category] : '#e5e7eb'}`,
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
          opacity: hasProfile ? 1 : 0.7,
          '&:hover': {
            transform: 'translateY(-4px)',
          }
        }
      },
      React.createElement(
        MaterialUI.Box,
        {
          className: "job-icon",
          sx: {
            fontSize: '32px',
            color: isHovered ? '#ffffff' : colorScheme.primary[category],
            marginBottom: '12px',
            transition: 'all 0.3s ease',
          }
        },
        React.createElement('i', { 
          className: `fas ${jobIconMap[job.name] || 'fa-briefcase'}` 
        })
      ),
      React.createElement(
        MaterialUI.Typography,
        {
          className: "job-name",
          variant: "body1",
          sx: {
            fontWeight: 600,
            color: isHovered ? '#ffffff' : '#1f2937',
            transition: 'all 0.3s ease',
          }
        },
        job.name
      ),
      !hasProfile && React.createElement(
        MaterialUI.Typography,
        {
          variant: "caption",
          sx: {
            color: isHovered ? '#ffffff' : '#9ca3af',
            marginTop: '4px'
          }
        },
        '미작성'
      )
    );
  };

  // 직종 섹션 컴포넌트
  const JobTypeSection = ({ jobType, jobs, category, group }) => {
    return React.createElement(
      MaterialUI.Box,
      { className: "job-type-section", sx: { marginBottom: 4 } },
      React.createElement(
        MaterialUI.Typography,
        {
          variant: "h6",
          sx: {
            fontWeight: 700,
            color: colorScheme.primary[category],
            marginBottom: 2,
            paddingLeft: 2,
            borderLeft: `4px solid ${colorScheme.primary[category]}`,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }
        },
        jobType,
        React.createElement(
          MaterialUI.Chip,
          {
            label: `${jobs.length}개 직무`,
            size: "small",
            sx: {
              backgroundColor: `${colorScheme.primary[category]}20`,
              color: colorScheme.primary[category],
              fontWeight: 600,
            }
          }
        )
      ),
      React.createElement(
        MaterialUI.Grid,
        { container: true, spacing: 2, sx: { paddingLeft: 2 } },
        jobs.map((job) => 
          React.createElement(
            MaterialUI.Grid,
            { item: true, xs: 12, sm: 6, md: 4, lg: 3, key: job.id },
            React.createElement(JobCard, {
              job,
              category,
              group,
              hasProfile: job.has_profile
            })
          )
        )
      )
    );
  };

  // 직군 카테고리 컴포넌트
  const CategorySection = ({ category, data }) => {
    const categoryIcon = iconMap[data.icon] || 'fa-folder';
    const categoryColor = data.color;
    
    return React.createElement(
      MaterialUI.Paper,
      {
        elevation: 0,
        sx: {
          padding: 4,
          marginBottom: 4,
          background: `linear-gradient(135deg, ${categoryColor}08 0%, ${categoryColor}04 100%)`,
          borderRadius: '24px',
          border: `1px solid ${categoryColor}20`,
        }
      },
      React.createElement(
        MaterialUI.Box,
        {
          sx: {
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            marginBottom: 3,
          }
        },
        React.createElement(
          MaterialUI.Box,
          {
            sx: {
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
            }
          },
          React.createElement('i', { className: `fas ${categoryIcon}` })
        ),
        React.createElement(
          MaterialUI.Box,
          null,
          React.createElement(
            MaterialUI.Typography,
            {
              variant: "h5",
              sx: {
                fontWeight: 800,
                color: '#1f2937',
                marginBottom: 0.5,
              }
            },
            category
          ),
          React.createElement(
            MaterialUI.Typography,
            {
              variant: "body2",
              sx: {
                color: '#6b7280',
                fontWeight: 500,
              }
            },
            `${Object.keys(data.jobs).length}개 직종 · ${
              Object.values(data.jobs).flat().length
            }개 직무`
          )
        )
      ),
      Object.entries(data.jobs).map(([jobType, jobs]) =>
        React.createElement(JobTypeSection, {
          key: jobType,
          jobType,
          jobs,
          category,
          group: category === '고객서비스' ? 'PL' : 'Non-PL'
        })
      )
    );
  };

  // 메인 렌더링
  return React.createElement(
    MaterialUI.Box,
    { className: "job-profile-tree-map", ref: containerRef },
    // 헤더
    React.createElement(
      MaterialUI.Box,
      { className: "tree-map-header", sx: { marginBottom: 4 } },
      React.createElement(
        MaterialUI.Typography,
        {
          variant: "h4",
          sx: {
            fontWeight: 800,
            textAlign: 'center',
            background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #10B981 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: 2,
          }
        },
        'OK금융그룹 직무 체계도'
      ),
      React.createElement(
        MaterialUI.Typography,
        {
          variant: "body1",
          sx: {
            textAlign: 'center',
            color: '#6b7280',
          }
        },
        '직군 → 직종 → 직무 구조를 한눈에 확인하세요'
      )
    ),
    // 통계 카드
    React.createElement(
      MaterialUI.Grid,
      { container: true, spacing: 2, sx: { marginBottom: 4 } },
      [
        { label: '직군', value: djangoContext.statistics.categories },
        { label: '직종', value: djangoContext.statistics.jobTypes },
        { label: '직무', value: djangoContext.statistics.jobRoles },
        { label: '직무기술서', value: djangoContext.statistics.profiles }
      ].map((stat) =>
        React.createElement(
          MaterialUI.Grid,
          { item: true, xs: 6, md: 3, key: stat.label },
          React.createElement(
            MaterialUI.Paper,
            {
              elevation: 0,
              sx: {
                padding: 3,
                textAlign: 'center',
                background: '#ffffff',
                borderRadius: '16px',
                border: '1px solid #e5e7eb',
              }
            },
            React.createElement(
              MaterialUI.Typography,
              {
                variant: "h4",
                sx: { fontWeight: 700, color: '#1f2937', marginBottom: 1 }
              },
              stat.value
            ),
            React.createElement(
              MaterialUI.Typography,
              {
                variant: "body2",
                sx: { color: '#6b7280', fontWeight: 500 }
              },
              stat.label
            )
          )
        )
      )
    ),
    // 메인 컨텐츠
    React.createElement(
      MaterialUI.Grid,
      { container: true, spacing: 4, className: "tree-map-container" },
      // Non-PL 직군
      React.createElement(
        MaterialUI.Grid,
        { item: true, xs: 12, lg: 8 },
        React.createElement(
          MaterialUI.Paper,
          {
            elevation: 0,
            sx: {
              padding: 3,
              background: '#f8fafc',
              borderRadius: '24px',
              border: '2px solid #e5e7eb',
            }
          },
          React.createElement(
            MaterialUI.Typography,
            {
              variant: "h5",
              sx: {
                fontWeight: 800,
                color: '#1f2937',
                marginBottom: 3,
                textAlign: 'center',
                paddingBottom: 2,
                borderBottom: '2px solid #e5e7eb',
              }
            },
            'Non-PL 직군'
          ),
          jobData['Non-PL'] && Object.entries(jobData['Non-PL']).map(([category, data]) =>
            React.createElement(CategorySection, {
              key: category,
              category,
              data
            })
          )
        )
      ),
      // PL 직군
      React.createElement(
        MaterialUI.Grid,
        { item: true, xs: 12, lg: 4 },
        React.createElement(
          MaterialUI.Paper,
          {
            elevation: 0,
            sx: {
              padding: 3,
              background: '#fef3f2',
              borderRadius: '24px',
              border: '2px solid #fecaca',
            }
          },
          React.createElement(
            MaterialUI.Typography,
            {
              variant: "h5",
              sx: {
                fontWeight: 800,
                color: '#1f2937',
                marginBottom: 3,
                textAlign: 'center',
                paddingBottom: 2,
                borderBottom: '2px solid #fecaca',
              }
            },
            'PL 직군'
          ),
          jobData['PL'] && Object.entries(jobData['PL']).map(([category, data]) =>
            React.createElement(CategorySection, {
              key: category,
              category,
              data
            })
          )
        )
      )
    ),
    // 플로팅 컨트롤
    React.createElement(
      MaterialUI.Box,
      {
        className: "floating-controls",
        sx: {
          position: 'fixed',
          bottom: 24,
          right: 24,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          zIndex: 1000,
        }
      },
      React.createElement(
        MaterialUI.IconButton,
        {
          sx: {
            backgroundColor: '#ffffff',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            '&:hover': {
              backgroundColor: '#f3f4f6',
            },
          },
          onClick: () => containerRef.current?.scrollIntoView({ behavior: 'smooth' })
        },
        React.createElement('i', { className: 'fas fa-arrow-up' })
      )
    )
  );
};