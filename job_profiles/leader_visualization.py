"""
리더 추천 결과 시각화 모듈
추천 결과를 다양한 형태로 시각화
"""

from typing import List, Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import font_manager, rc
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class LeaderVisualization:
    """리더 추천 시각화 클래스"""
    
    def __init__(self):
        # 색상 팔레트 설정
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#5EB344',
            'warning': '#F18F01',
            'danger': '#C73E1D',
            'neutral': '#6C757D'
        }
        
        # 스타일 설정
        sns.set_style("whitegrid")
        
    def plot_candidate_comparison(
        self,
        candidates: List[dict],
        save_path: Optional[str] = None
    ):
        """후보자 비교 차트"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 데이터 준비
        names = [c['name'] for c in candidates[:5]]
        scores = [c['match_score'] for c in candidates[:5]]
        skill_rates = [c['skill_match_rate'] * 100 for c in candidates[:5]]
        
        # 1. 종합 점수 막대 차트
        bars = ax1.bar(names, scores, color=self.colors['primary'], alpha=0.8)
        ax1.set_title('Leadership Readiness Score', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Score', fontsize=12)
        ax1.set_ylim(0, 110)
        
        # 점수 표시
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{score:.1f}', ha='center', va='bottom', fontsize=10)
        
        # 2. 스킬 매칭률 수평 막대 차트
        y_pos = np.arange(len(names))
        bars2 = ax2.barh(y_pos, skill_rates, color=self.colors['secondary'], alpha=0.8)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(names)
        ax2.set_xlabel('Skill Match Rate (%)', fontsize=12)
        ax2.set_title('Required Skills Coverage', fontsize=14, fontweight='bold')
        ax2.set_xlim(0, 105)
        
        # 퍼센트 표시
        for i, (bar, rate) in enumerate(zip(bars2, skill_rates)):
            ax2.text(rate + 1, i, f'{rate:.0f}%', 
                    ha='left', va='center', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def plot_organization_talent_heatmap(
        self,
        talent_pool: dict,
        save_path: Optional[str] = None
    ):
        """조직별 인재 풀 히트맵"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 데이터 준비
        departments = list(talent_pool['department_details'].keys())
        categories = ['Team Lead Ready', 'High Potentials', 'Total Employees']
        
        # 매트릭스 생성
        data_matrix = []
        for dept in departments:
            dept_data = talent_pool['department_details'][dept]
            row = [
                len(dept_data['team_lead_candidates']),
                len(dept_data['high_potentials']),
                dept_data['total_employees']
            ]
            data_matrix.append(row)
        
        # 정규화 (각 카테고리별로)
        data_matrix = np.array(data_matrix)
        normalized_matrix = data_matrix.copy().astype(float)
        for i in range(len(categories)):
            col_max = data_matrix[:, i].max()
            if col_max > 0:
                normalized_matrix[:, i] = data_matrix[:, i] / col_max
        
        # 히트맵 그리기
        im = ax.imshow(normalized_matrix.T, cmap='YlOrRd', aspect='auto')
        
        # 축 설정
        ax.set_xticks(np.arange(len(departments)))
        ax.set_yticks(np.arange(len(categories)))
        ax.set_xticklabels(departments, rotation=45, ha='right')
        ax.set_yticklabels(categories)
        
        # 값 표시
        for i in range(len(departments)):
            for j in range(len(categories)):
                text = ax.text(i, j, int(data_matrix[i, j]),
                             ha='center', va='center', color='black' 
                             if normalized_matrix[i, j] < 0.5 else 'white')
        
        # 컬러바
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Relative Strength', rotation=270, labelpad=20)
        
        ax.set_title('Organization Talent Pool Heatmap', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def plot_succession_pipeline(
        self,
        succession_plan: dict,
        save_path: Optional[str] = None
    ):
        """승계 파이프라인 시각화"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 타임라인 설정
        months = succession_plan['months_ahead']
        candidates = succession_plan['candidates'][:5]  # 상위 5명
        
        # Y축 위치
        y_positions = list(range(len(candidates)))
        
        # 각 후보자의 준비 기간 표시
        for i, candidate in enumerate(candidates):
            prep_months = candidate['preparation_months']
            readiness = candidate['readiness_score']
            
            # 준비 기간 막대
            color = self.colors['success'] if candidate['is_ready'] else self.colors['warning']
            bar = ax.barh(i, prep_months, left=0, height=0.6, 
                         color=color, alpha=0.7, 
                         label='Ready' if i == 0 and candidate['is_ready'] else 
                               'In Progress' if i == 0 else '')
            
            # 후보자 이름과 점수
            emp_name = candidate['employee'].name
            ax.text(-1, i, f"{emp_name}\n({readiness:.0f}pts)", 
                   ha='right', va='center', fontsize=10)
            
            # 준비 기간 텍스트
            ax.text(prep_months/2, i, f"{prep_months}m", 
                   ha='center', va='center', fontsize=9, 
                   color='white' if prep_months > 3 else 'black')
        
        # 목표 시점 표시
        ax.axvline(x=months, color=self.colors['danger'], 
                  linestyle='--', linewidth=2, label='Target Date')
        
        # 축 설정
        ax.set_xlim(-2, months + 2)
        ax.set_ylim(-0.5, len(candidates) - 0.5)
        ax.set_xlabel('Months', fontsize=12)
        ax.set_title(f'Succession Pipeline - {succession_plan["retiring_position"]}', 
                    fontsize=16, fontweight='bold')
        
        # Y축 숨기기
        ax.set_yticks([])
        
        # 범례
        ax.legend(loc='upper right')
        
        # 그리드
        ax.grid(True, axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def plot_leadership_pipeline_funnel(
        self,
        pipeline_analysis: dict,
        save_path: Optional[str] = None
    ):
        """리더십 파이프라인 퍼널 차트"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 데이터 준비
        levels = list(pipeline_analysis['leadership_levels'].keys())
        counts = [pipeline_analysis['leadership_levels'][level]['total_count'] 
                 for level in levels]
        ready_counts = [pipeline_analysis['leadership_levels'][level]['next_level_ready'] 
                       for level in levels]
        
        # 퍼널 너비 계산
        max_count = max(counts)
        widths = [count / max_count for count in counts]
        
        # 퍼널 그리기
        y_pos = 0
        for i, (level, width, count, ready) in enumerate(zip(levels, widths, counts, ready_counts)):
            # 전체 인원 (밝은 색)
            rect = patches.Rectangle((0.5 - width/2, y_pos), width, 0.8,
                                   facecolor=self.colors['neutral'], 
                                   alpha=0.3, edgecolor='black')
            ax.add_patch(rect)
            
            # 준비된 인원 (진한 색)
            if count > 0:
                ready_width = width * (ready / count)
                rect_ready = patches.Rectangle((0.5 - ready_width/2, y_pos), 
                                             ready_width, 0.8,
                                             facecolor=self.colors['primary'], 
                                             alpha=0.8)
                ax.add_patch(rect_ready)
            
            # 레이블
            ax.text(0.5, y_pos + 0.4, f"{level}\n{count} ({ready} ready)", 
                   ha='center', va='center', fontsize=11, fontweight='bold')
            
            y_pos += 1
        
        # 축 설정
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, len(levels) - 0.5)
        ax.axis('off')
        
        ax.set_title('Leadership Pipeline Funnel', fontsize=16, fontweight='bold', pad=20)
        
        # 범례
        legend_elements = [
            patches.Patch(facecolor=self.colors['neutral'], alpha=0.3, 
                         edgecolor='black', label='Total Employees'),
            patches.Patch(facecolor=self.colors['primary'], alpha=0.8, 
                         label='Next Level Ready')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def plot_skill_gap_analysis(
        self,
        candidates: List[dict],
        target_job: dict,
        save_path: Optional[str] = None
    ):
        """스킬 갭 분석 차트"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 필수 스킬 목록
        required_skills = target_job.get('required_skills', [])[:8]  # 최대 8개
        
        # 데이터 매트릭스 생성
        skill_matrix = []
        candidate_names = []
        
        for candidate in candidates[:5]:  # 상위 5명
            candidate_names.append(candidate['name'])
            matched_skills = set(candidate.get('matched_skills', []))
            
            row = [1 if skill in matched_skills else 0 for skill in required_skills]
            skill_matrix.append(row)
        
        # 히트맵 그리기
        skill_matrix = np.array(skill_matrix)
        im = ax.imshow(skill_matrix.T, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # 축 설정
        ax.set_xticks(np.arange(len(candidate_names)))
        ax.set_yticks(np.arange(len(required_skills)))
        ax.set_xticklabels(candidate_names, rotation=45, ha='right')
        ax.set_yticklabels(required_skills)
        
        # 체크마크 또는 X 표시
        for i in range(len(candidate_names)):
            for j in range(len(required_skills)):
                if skill_matrix[i, j] == 1:
                    ax.text(i, j, '✓', ha='center', va='center', 
                           color='white', fontsize=16, fontweight='bold')
                else:
                    ax.text(i, j, '✗', ha='center', va='center', 
                           color='white', fontsize=16, fontweight='bold')
        
        ax.set_title(f'Skill Gap Analysis - {target_job.get("name", "Leadership Position")}', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def create_candidate_summary_card(
        self,
        candidate: dict,
        save_path: Optional[str] = None
    ):
        """후보자 요약 카드 생성"""
        fig = plt.figure(figsize=(8, 10))
        
        # 메인 정보 영역
        ax_main = plt.subplot2grid((4, 2), (0, 0), colspan=2, rowspan=1)
        ax_main.axis('off')
        
        # 이름과 직책
        ax_main.text(0.5, 0.7, candidate['name'], 
                    ha='center', va='center', fontsize=20, fontweight='bold')
        ax_main.text(0.5, 0.3, f"{candidate['current_position']} | {candidate['department']}", 
                    ha='center', va='center', fontsize=14)
        
        # 점수 게이지
        ax_score = plt.subplot2grid((4, 2), (1, 0), colspan=2, rowspan=1)
        self._draw_score_gauge(ax_score, candidate['match_score'])
        
        # 상세 정보
        ax_details = plt.subplot2grid((4, 2), (2, 0), colspan=2, rowspan=2)
        ax_details.axis('off')
        
        # 정보 텍스트
        info_text = f"""
평가 등급: {candidate['evaluation_grade']}
성장 레벨: {candidate['growth_level']}
경력: {candidate['experience_years']}년
자격증: {len(candidate.get('qualifications', []))}개

추천 사유:
{candidate['recommendation_reason']}

핵심 역량:
{', '.join(candidate.get('matched_skills', [])[:5])}
"""
        
        if candidate.get('risk_factors'):
            info_text += f"\n주의사항:\n{', '.join(candidate['risk_factors'])}"
        
        ax_details.text(0.1, 0.9, info_text, 
                       ha='left', va='top', fontsize=11,
                       wrap=True, transform=ax_details.transAxes)
        
        plt.suptitle('Leadership Candidate Profile', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def _draw_score_gauge(self, ax, score):
        """점수 게이지 그리기"""
        ax.axis('off')
        
        # 게이지 배경
        circle_bg = plt.Circle((0.5, 0.5), 0.4, color='lightgray', 
                              fill=False, linewidth=15)
        ax.add_patch(circle_bg)
        
        # 점수에 따른 색상
        if score >= 80:
            color = self.colors['success']
        elif score >= 60:
            color = self.colors['warning']
        else:
            color = self.colors['danger']
        
        # 게이지 채우기
        theta = (score / 100) * 360
        wedge = patches.Wedge((0.5, 0.5), 0.4, 90, 90-theta, 
                            width=0.15, facecolor=color)
        ax.add_patch(wedge)
        
        # 점수 텍스트
        ax.text(0.5, 0.5, f"{score:.0f}", 
               ha='center', va='center', fontsize=28, fontweight='bold')
        ax.text(0.5, 0.3, "Leadership\nReadiness", 
               ha='center', va='center', fontsize=10)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)


# 사용 예시
if __name__ == "__main__":
    # 샘플 데이터
    sample_candidates = [
        {
            'name': 'Kim Sung-kwa',
            'current_position': 'Manager',
            'department': 'Sales Team 1',
            'match_score': 85.5,
            'skill_match_rate': 0.8,
            'evaluation_grade': 'A',
            'growth_level': 'Lv.4',
            'experience_years': 8,
            'matched_skills': ['Leadership', 'Performance Mgmt', 'Communication'],
            'recommendation_reason': 'Strong evaluation and leadership experience',
            'risk_factors': None
        },
        {
            'name': 'Lee Woo-soo',
            'current_position': 'Deputy Manager',
            'department': 'Sales Team 2',
            'match_score': 72.3,
            'skill_match_rate': 0.6,
            'evaluation_grade': 'B+',
            'growth_level': 'Lv.3',
            'experience_years': 5,
            'matched_skills': ['Performance Mgmt', 'Data Analysis'],
            'recommendation_reason': 'Good performance record',
            'risk_factors': ['Needs leadership experience']
        }
    ]
    
    sample_target_job = {
        'name': 'Team Leader',
        'required_skills': ['Leadership', 'Performance Mgmt', 'Strategy', 'Communication', 'Coaching']
    }
    
    # 시각화 객체 생성
    viz = LeaderVisualization()
    
    # 후보자 비교 차트
    print("Creating candidate comparison chart...")
    viz.plot_candidate_comparison(sample_candidates)
    
    # 스킬 갭 분석
    print("Creating skill gap analysis...")
    viz.plot_skill_gap_analysis(sample_candidates, sample_target_job)