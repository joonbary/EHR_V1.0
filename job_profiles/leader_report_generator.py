"""
리더 추천 PDF 리포트 자동 생성 모듈
추천 대상자의 종합 리더십 성장 리포트를 PDF로 생성
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, HRFlowable
)
from reportlab.graphics.shapes import Drawing, Line, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import base64
import tempfile


class LeaderReportGenerator:
    """리더 추천 PDF 리포트 생성기"""
    
    def __init__(self):
        # 스타일 설정
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # 색상 팔레트
        self.colors = {
            'primary': colors.HexColor('#2E86AB'),
            'secondary': colors.HexColor('#A23B72'),
            'success': colors.HexColor('#5EB344'),
            'warning': colors.HexColor('#F18F01'),
            'danger': colors.HexColor('#C73E1D'),
            'neutral': colors.HexColor('#6C757D'),
            'light': colors.HexColor('#F8F9FA'),
            'dark': colors.HexColor('#212529')
        }
    
    def _setup_custom_styles(self):
        """커스텀 스타일 설정"""
        # 제목 스타일
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=1  # 중앙 정렬
        ))
        
        # 섹션 헤더 스타일
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2E86AB'),
            spaceBefore=20,
            spaceAfter=10,
            borderWidth=2,
            borderColor=colors.HexColor('#2E86AB'),
            borderPadding=5
        ))
        
        # 서브헤더 스타일
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#495057'),
            spaceBefore=15,
            spaceAfter=8
        ))
        
        # 본문 스타일
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#212529')
        ))
    
    def generate_leader_recommendation_report(
        self,
        candidate: dict,
        target_job: dict,
        growth_path: Optional[dict] = None,
        evaluation_history: Optional[List[dict]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        리더 추천 종합 리포트 생성
        
        Args:
            candidate: 추천 대상자 정보
            target_job: 목표 직무 정보
            growth_path: 성장 경로 정보
            evaluation_history: 평가 이력
            output_path: 저장 경로 (None이면 임시 파일)
        
        Returns:
            생성된 PDF 파일 경로
        """
        # 출력 경로 설정
        if not output_path:
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix='.pdf',
                prefix=f"leader_report_{candidate['name']}_"
            )
            output_path = temp_file.name
            temp_file.close()
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # 콘텐츠 생성
        story = []
        
        # 1. 표지
        story.extend(self._create_cover_page(candidate, target_job))
        story.append(PageBreak())
        
        # 2. 추천자 기본정보
        story.extend(self._create_candidate_info_section(candidate))
        
        # 3. 추천사유 요약
        story.extend(self._create_recommendation_summary(candidate, target_job))
        
        # 4. 직무 적합도 분석
        story.extend(self._create_job_fit_analysis(candidate, target_job))
        
        # 5. 평가 이력 및 추이
        if evaluation_history:
            story.extend(self._create_evaluation_history(evaluation_history))
        
        # 6. 성장 경로 분석
        if growth_path:
            story.extend(self._create_growth_path_analysis(growth_path))
        
        # 7. 시각화 차트
        story.extend(self._create_visualization_section(
            candidate, target_job, evaluation_history, growth_path
        ))
        
        # 8. 결론 및 추천
        story.extend(self._create_conclusion_section(candidate, target_job))
        
        # PDF 빌드
        doc.build(story, onFirstPage=self._add_header_footer, 
                 onLaterPages=self._add_header_footer)
        
        return output_path
    
    def _create_cover_page(self, candidate: dict, target_job: dict) -> List:
        """표지 생성"""
        elements = []
        
        # 상단 여백
        elements.append(Spacer(1, 2*inch))
        
        # 제목
        title = Paragraph(
            "Leadership Recommendation Report",
            self.styles['CustomTitle']
        )
        elements.append(title)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # 부제목
        subtitle = Paragraph(
            f"<b>{candidate['name']}</b><br/>",
            self.styles['SubHeader']
        )
        elements.append(subtitle)
        
        # 목표 직무
        target = Paragraph(
            f"Target Position: <b>{target_job.get('name', 'Leadership Position')}</b>",
            self.styles['CustomBody']
        )
        elements.append(target)
        
        elements.append(Spacer(1, 1*inch))
        
        # 생성 정보
        date_info = Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d')}<br/>" +
            f"Department: {candidate.get('department', 'N/A')}",
            self.styles['CustomBody']
        )
        elements.append(date_info)
        
        return elements
    
    def _create_candidate_info_section(self, candidate: dict) -> List:
        """추천자 기본정보 섹션"""
        elements = []
        
        elements.append(Paragraph("1. Candidate Information", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 기본 정보 테이블
        data = [
            ["Name", candidate.get('name', 'N/A')],
            ["Current Position", candidate.get('current_position', 'N/A')],
            ["Department", candidate.get('department', 'N/A')],
            ["Growth Level", candidate.get('growth_level', 'N/A')],
            ["Recent Evaluation", candidate.get('evaluation_grade', 'N/A')],
            ["Years of Experience", f"{candidate.get('experience_years', 0)} years"],
            ["Leadership Score", f"{candidate.get('match_score', 0):.1f} / 100"]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.colors['light']),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['dark']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # 자격증 정보
        if candidate.get('qualifications'):
            elements.append(Paragraph("Certifications:", self.styles['SubHeader']))
            cert_text = " • ".join(candidate['qualifications'])
            elements.append(Paragraph(cert_text, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_recommendation_summary(self, candidate: dict, target_job: dict) -> List:
        """추천사유 요약 섹션"""
        elements = []
        
        elements.append(Paragraph("2. Recommendation Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 추천 사유
        recommendation_text = candidate.get(
            'recommendation_reason',
            'Comprehensive evaluation indicates strong leadership potential.'
        )
        
        elements.append(Paragraph(
            f"<b>Primary Recommendation Reason:</b><br/>{recommendation_text}",
            self.styles['CustomBody']
        ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # 주요 강점
        if candidate.get('matched_skills'):
            elements.append(Paragraph("<b>Key Strengths:</b>", self.styles['CustomBody']))
            
            strengths_data = []
            for skill in candidate['matched_skills'][:5]:
                strengths_data.append([f"• {skill}"])
            
            if strengths_data:
                strengths_table = Table(strengths_data, colWidths=[6*inch])
                strengths_table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('LEFTPADDING', (0, 0), (-1, -1), 20),
                ]))
                elements.append(strengths_table)
        
        # 리스크 요인
        if candidate.get('risk_factors'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("<b>Risk Factors:</b>", self.styles['CustomBody']))
            
            for risk in candidate['risk_factors']:
                elements.append(Paragraph(f"• {risk}", self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_job_fit_analysis(self, candidate: dict, target_job: dict) -> List:
        """직무 적합도 분석 섹션"""
        elements = []
        
        elements.append(Paragraph("3. Job Fit Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 적합도 점수
        match_score = candidate.get('match_score', 0)
        skill_match_rate = candidate.get('skill_match_rate', 0) * 100
        
        # 점수 테이블
        score_data = [
            ["Overall Readiness Score", f"{match_score:.1f} / 100"],
            ["Skill Match Rate", f"{skill_match_rate:.0f}%"],
            ["Required Skills", f"{len(target_job.get('required_skills', []))}"],
            ["Matched Skills", f"{len(candidate.get('matched_skills', []))}"],
            ["Missing Skills", f"{len(candidate.get('missing_skills', []))}"]
        ]
        
        score_table = Table(score_data, colWidths=[3*inch, 2*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(score_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # 스킬 갭 분석
        if candidate.get('missing_skills'):
            elements.append(Paragraph("<b>Skill Gap Analysis:</b>", self.styles['CustomBody']))
            
            gap_data = [["Required Skill", "Status"]]
            
            all_skills = set(target_job.get('required_skills', []))
            matched_skills = set(candidate.get('matched_skills', []))
            
            for skill in all_skills:
                if skill in matched_skills:
                    gap_data.append([skill, "✓ Possessed"])
                else:
                    gap_data.append([skill, "✗ Missing"])
            
            gap_table = Table(gap_data, colWidths=[4*inch, 2*inch])
            gap_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['neutral']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light']]),
            ]))
            
            elements.append(gap_table)
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_evaluation_history(self, evaluation_history: List[dict]) -> List:
        """평가 이력 섹션"""
        elements = []
        
        elements.append(Paragraph("4. Evaluation History", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 평가 이력 테이블
        eval_data = [["Period", "Overall Grade", "Professionalism", "Contribution", "Impact"]]
        
        for eval in evaluation_history[-5:]:  # 최근 5개
            eval_data.append([
                eval.get('period', 'N/A'),
                eval.get('overall_grade', 'N/A'),
                eval.get('professionalism', 'N/A'),
                eval.get('contribution', 'N/A'),
                eval.get('impact', 'N/A')
            ])
        
        eval_table = Table(eval_data, colWidths=[1.2*inch, 1.2*inch, 1.4*inch, 1.6*inch, 1.2*inch])
        eval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light']]),
        ]))
        
        elements.append(eval_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_growth_path_analysis(self, growth_path: dict) -> List:
        """성장 경로 분석 섹션"""
        elements = []
        
        elements.append(Paragraph("5. Growth Path Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 경로 요약
        summary_text = f"""
        <b>Target Position:</b> {growth_path.get('target_job', 'N/A')}<br/>
        <b>Estimated Timeline:</b> {growth_path.get('total_years', 0):.1f} years<br/>
        <b>Success Probability:</b> {growth_path.get('success_probability', 0)*100:.0f}%<br/>
        <b>Overall Difficulty:</b> {growth_path.get('difficulty_score', 0):.0f}/100
        """
        
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 단계별 경로
        if growth_path.get('stages'):
            elements.append(Paragraph("<b>Growth Stages:</b>", self.styles['CustomBody']))
            
            stage_data = [["Stage", "Position", "Duration", "Key Requirements"]]
            
            for i, stage in enumerate(growth_path['stages'], 1):
                requirements = ", ".join(stage.get('required_skills', [])[:3])
                stage_data.append([
                    f"Stage {i}",
                    stage.get('job_name', 'N/A'),
                    f"{stage.get('expected_years', 0):.1f} years",
                    requirements or "N/A"
                ])
            
            stage_table = Table(stage_data, colWidths=[0.8*inch, 2*inch, 1.2*inch, 2.6*inch])
            stage_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light']]),
            ]))
            
            elements.append(stage_table)
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_visualization_section(
        self,
        candidate: dict,
        target_job: dict,
        evaluation_history: Optional[List[dict]],
        growth_path: Optional[dict]
    ) -> List:
        """시각화 차트 섹션"""
        elements = []
        
        elements.append(Paragraph("6. Visual Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 평가 추이 차트
        if evaluation_history and len(evaluation_history) > 1:
            elements.append(Paragraph("Evaluation Trend", self.styles['SubHeader']))
            chart_path = self._create_evaluation_trend_chart(evaluation_history)
            if chart_path:
                elements.append(Image(chart_path, width=5*inch, height=3*inch))
                elements.append(Spacer(1, 0.2*inch))
        
        # 스킬 매칭 차트
        elements.append(Paragraph("Skill Match Analysis", self.styles['SubHeader']))
        skill_chart_path = self._create_skill_match_chart(candidate, target_job)
        if skill_chart_path:
            elements.append(Image(skill_chart_path, width=5*inch, height=3*inch))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_conclusion_section(self, candidate: dict, target_job: dict) -> List:
        """결론 및 추천 섹션"""
        elements = []
        
        elements.append(Paragraph("7. Conclusion and Recommendation", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 추천 등급 결정
        match_score = candidate.get('match_score', 0)
        if match_score >= 80:
            recommendation = "STRONGLY RECOMMEND"
            rec_color = self.colors['success']
        elif match_score >= 60:
            recommendation = "RECOMMEND WITH DEVELOPMENT"
            rec_color = self.colors['warning']
        else:
            recommendation = "NOT RECOMMENDED AT THIS TIME"
            rec_color = self.colors['danger']
        
        # 추천 등급 박스
        rec_table = Table(
            [[recommendation]],
            colWidths=[6*inch]
        )
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), rec_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(rec_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # 상세 결론
        if match_score >= 80:
            conclusion_text = f"""
            <b>{candidate['name']}</b> demonstrates exceptional readiness for the 
            <b>{target_job.get('name', 'leadership position')}</b>. With a leadership 
            readiness score of <b>{match_score:.1f}</b>, the candidate shows strong 
            alignment with required competencies and has a proven track record of success.
            """
        elif match_score >= 60:
            conclusion_text = f"""
            <b>{candidate['name']}</b> shows good potential for the 
            <b>{target_job.get('name', 'leadership position')}</b> with a readiness 
            score of <b>{match_score:.1f}</b>. With targeted development in key areas, 
            particularly {', '.join(candidate.get('missing_skills', ['identified gaps'])[:2])}, 
            the candidate can successfully transition to this role.
            """
        else:
            conclusion_text = f"""
            While <b>{candidate['name']}</b> shows some potential, the current readiness 
            score of <b>{match_score:.1f}</b> indicates significant gaps that need to be 
            addressed before considering for the <b>{target_job.get('name', 'leadership position')}</b>.
            A comprehensive development plan is recommended.
            """
        
        elements.append(Paragraph(conclusion_text, self.styles['CustomBody']))
        
        # 다음 단계 제안
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("<b>Recommended Next Steps:</b>", self.styles['CustomBody']))
        
        if match_score >= 80:
            next_steps = [
                "Proceed with formal nomination process",
                "Arrange transition planning meetings",
                "Identify mentoring opportunities for the new role"
            ]
        elif match_score >= 60:
            next_steps = [
                "Create targeted development plan for skill gaps",
                "Assign stretch projects in weak areas",
                "Re-evaluate readiness in 6-12 months"
            ]
        else:
            next_steps = [
                "Comprehensive skills assessment",
                "Long-term development program enrollment",
                "Regular progress monitoring"
            ]
        
        for step in next_steps:
            elements.append(Paragraph(f"• {step}", self.styles['CustomBody']))
        
        return elements
    
    def _create_evaluation_trend_chart(self, evaluation_history: List[dict]) -> Optional[str]:
        """평가 추이 차트 생성"""
        try:
            # 데이터 준비
            periods = [eval.get('period', f'Period {i+1}') 
                      for i, eval in enumerate(evaluation_history[-5:])]
            
            # 등급을 숫자로 변환
            grade_map = {'S': 5, 'A+': 4.5, 'A': 4, 'B+': 3.5, 'B': 3, 'C': 2, 'D': 1}
            grades = [grade_map.get(eval.get('overall_grade', 'B'), 3) 
                     for eval in evaluation_history[-5:]]
            
            # 차트 생성
            plt.figure(figsize=(8, 5))
            plt.bar(periods, grades, color='#2E86AB', alpha=0.8)
            plt.ylim(0, 5.5)
            plt.ylabel('Evaluation Grade')
            plt.title('Evaluation History Trend')
            
            # 등급 레이블 추가
            for i, (period, grade) in enumerate(zip(periods, grades)):
                grade_label = next((k for k, v in grade_map.items() if v == grade), 'N/A')
                plt.text(i, grade + 0.1, grade_label, ha='center', va='bottom')
            
            # Y축 등급 표시
            plt.yticks([1, 2, 3, 3.5, 4, 4.5, 5], 
                      ['D', 'C', 'B', 'B+', 'A', 'A+', 'S'])
            
            plt.grid(True, axis='y', alpha=0.3)
            plt.tight_layout()
            
            # 임시 파일로 저장
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
            plt.close()
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error creating evaluation trend chart: {e}")
            return None
    
    def _create_skill_match_chart(self, candidate: dict, target_job: dict) -> Optional[str]:
        """스킬 매칭 차트 생성"""
        try:
            # 데이터 준비
            required_skills = target_job.get('required_skills', [])[:8]
            matched_skills = set(candidate.get('matched_skills', []))
            
            # 매칭 여부 확인
            match_status = [1 if skill in matched_skills else 0 for skill in required_skills]
            
            # 차트 생성
            plt.figure(figsize=(10, 6))
            
            # 색상 설정
            colors_list = ['#5EB344' if status == 1 else '#C73E1D' 
                          for status in match_status]
            
            # 수평 막대 차트
            y_pos = range(len(required_skills))
            plt.barh(y_pos, [1]*len(required_skills), color=colors_list, alpha=0.8)
            
            # 스킬 이름 표시
            plt.yticks(y_pos, required_skills)
            
            # 상태 텍스트 추가
            for i, (skill, status) in enumerate(zip(required_skills, match_status)):
                text = "Possessed" if status == 1 else "Missing"
                color = 'white'
                plt.text(0.5, i, text, ha='center', va='center', 
                        color=color, fontweight='bold', fontsize=10)
            
            plt.xlim(0, 1)
            plt.xlabel('Skill Match Status')
            plt.title('Required Skills Coverage Analysis')
            plt.tight_layout()
            
            # 임시 파일로 저장
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
            plt.close()
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error creating skill match chart: {e}")
            return None
    
    def _add_header_footer(self, canvas_obj, doc):
        """헤더와 푸터 추가"""
        canvas_obj.saveState()
        
        # 헤더
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawString(
            doc.leftMargin,
            doc.height + doc.topMargin + 20,
            "Leadership Recommendation Report - Confidential"
        )
        
        # 푸터
        canvas_obj.drawString(
            doc.leftMargin,
            doc.bottomMargin - 20,
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        # 페이지 번호
        canvas_obj.drawRightString(
            doc.width + doc.leftMargin,
            doc.bottomMargin - 20,
            f"Page {canvas_obj.getPageNumber()}"
        )
        
        canvas_obj.restoreState()
    
    def generate_batch_reports(
        self,
        candidates: List[dict],
        target_job: dict,
        output_dir: str,
        include_growth_path: bool = True,
        include_evaluation_history: bool = True
    ) -> List[str]:
        """
        배치 처리로 여러 후보자의 리포트 생성
        
        Args:
            candidates: 후보자 리스트
            target_job: 목표 직무
            output_dir: 출력 디렉토리
            include_growth_path: 성장 경로 포함 여부
            include_evaluation_history: 평가 이력 포함 여부
        
        Returns:
            생성된 PDF 파일 경로 리스트
        """
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        
        for candidate in candidates:
            # 파일명 생성
            safe_name = "".join(c for c in candidate['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"leader_report_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
            output_path = os.path.join(output_dir, filename)
            
            # 더미 데이터 생성 (실제로는 DB에서 조회)
            growth_path = None
            if include_growth_path:
                growth_path = {
                    'target_job': target_job.get('name'),
                    'total_years': 3.5,
                    'success_probability': 0.75,
                    'difficulty_score': 65,
                    'stages': [
                        {
                            'job_name': 'Senior Manager',
                            'expected_years': 1.5,
                            'required_skills': ['Strategic Planning', 'Team Leadership']
                        },
                        {
                            'job_name': target_job.get('name'),
                            'expected_years': 2.0,
                            'required_skills': target_job.get('required_skills', [])[:3]
                        }
                    ]
                }
            
            evaluation_history = None
            if include_evaluation_history:
                evaluation_history = [
                    {'period': '2023 Q4', 'overall_grade': 'A', 'professionalism': 'A+'},
                    {'period': '2024 Q1', 'overall_grade': 'A', 'professionalism': 'A'},
                    {'period': '2024 Q2', 'overall_grade': 'A+', 'professionalism': 'A+'},
                ]
            
            # 리포트 생성
            try:
                report_path = self.generate_leader_recommendation_report(
                    candidate=candidate,
                    target_job=target_job,
                    growth_path=growth_path,
                    evaluation_history=evaluation_history,
                    output_path=output_path
                )
                generated_files.append(report_path)
                print(f"Generated report for {candidate['name']}: {report_path}")
                
            except Exception as e:
                print(f"Error generating report for {candidate['name']}: {e}")
        
        return generated_files


# 사용 예시
if __name__ == "__main__":
    # 샘플 데이터
    sample_candidate = {
        'name': 'Kim Sung-kwa',
        'current_position': 'Manager',
        'department': 'Sales Team 1',
        'growth_level': 'Lv.4',
        'evaluation_grade': 'A',
        'experience_years': 8,
        'match_score': 85.5,
        'skill_match_rate': 0.8,
        'qualifications': ['PMP', 'Leadership Certificate'],
        'matched_skills': ['Leadership', 'Performance Management', 'Communication', 'Strategic Planning'],
        'missing_skills': ['Budget Management', 'Coaching'],
        'recommendation_reason': '3 consecutive years of A grade evaluation, strategic project experience, growth level 3+ satisfied',
        'risk_factors': None
    }
    
    sample_target_job = {
        'name': 'Team Leader',
        'required_skills': ['Leadership', 'Performance Management', 'Strategic Planning', 
                           'Communication', 'Budget Management', 'Coaching', 'Decision Making']
    }
    
    sample_evaluation_history = [
        {'period': '2022 H2', 'overall_grade': 'B+', 'professionalism': 'A', 
         'contribution': 'Top 20%', 'impact': 'Department'},
        {'period': '2023 H1', 'overall_grade': 'A', 'professionalism': 'A', 
         'contribution': 'Top 20%', 'impact': 'Cross-team'},
        {'period': '2023 H2', 'overall_grade': 'A', 'professionalism': 'A+', 
         'contribution': 'Top 10%', 'impact': 'Cross-team'},
        {'period': '2024 H1', 'overall_grade': 'A', 'professionalism': 'A+', 
         'contribution': 'Top 10%', 'impact': 'Company-wide'},
    ]
    
    sample_growth_path = {
        'target_job': 'Team Leader',
        'total_years': 2.5,
        'success_probability': 0.85,
        'difficulty_score': 45,
        'stages': [
            {
                'job_name': 'Senior Manager',
                'expected_years': 1.0,
                'required_skills': ['Advanced Leadership', 'Strategic Planning', 'Team Building']
            },
            {
                'job_name': 'Team Leader',
                'expected_years': 1.5,
                'required_skills': ['Executive Leadership', 'Organizational Management', 'P&L Responsibility']
            }
        ]
    }
    
    # 리포트 생성
    generator = LeaderReportGenerator()
    
    print("Generating leadership recommendation report...")
    report_path = generator.generate_leader_recommendation_report(
        candidate=sample_candidate,
        target_job=sample_target_job,
        growth_path=sample_growth_path,
        evaluation_history=sample_evaluation_history
    )
    
    print(f"Report generated successfully: {report_path}")