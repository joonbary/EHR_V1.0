"""
리더 추천 PDF 리포트 생성 테스트
다양한 시나리오에서 PDF 리포트 생성 테스트
"""

from job_profiles.leader_report_generator import LeaderReportGenerator
import os
import tempfile
from datetime import datetime


def test_single_candidate_report():
    """단일 후보자 리포트 생성 테스트"""
    print("=" * 70)
    print("테스트 1: 단일 후보자 리더십 추천 리포트")
    print("=" * 70)
    
    # 고성과자 데이터
    high_performer = {
        'employee_id': 'emp001',
        'name': 'Kim Sung-kwa',
        'current_position': 'Manager',
        'department': 'Sales Team 1',
        'growth_level': 'Lv.4',
        'evaluation_grade': 'A+',
        'experience_years': 9,
        'match_score': 88.5,
        'skill_match_rate': 0.85,
        'qualifications': ['PMP', 'Six Sigma Black Belt', 'Leadership Academy'],
        'matched_skills': [
            'Organizational Leadership', 'Performance Management', 
            'Strategic Execution', 'Communication', 'Team Building'
        ],
        'missing_skills': ['Budget Management', 'Executive Presentation'],
        'recommendation_reason': '3 consecutive years of A+ evaluation, proven strategic project leadership, growth level 4 achieved',
        'risk_factors': None
    }
    
    # 목표 직무
    target_job = {
        'name': 'Sales Team Leader',
        'required_skills': [
            'Organizational Leadership', 'Performance Management', 
            'Strategic Execution', 'Customer Relationship', 
            'Budget Management', 'Communication', 'Executive Presentation'
        ],
        'qualification': 'Sales experience 7+ years, leadership experience required'
    }
    
    # 평가 이력
    evaluation_history = [
        {
            'period': '2022 Q4',
            'overall_grade': 'A',
            'professionalism': 'A',
            'contribution': 'Top 20%',
            'impact': 'Cross-team'
        },
        {
            'period': '2023 Q1',
            'overall_grade': 'A',
            'professionalism': 'A+',
            'contribution': 'Top 20%',
            'impact': 'Cross-team'
        },
        {
            'period': '2023 Q2',
            'overall_grade': 'A+',
            'professionalism': 'A+',
            'contribution': 'Top 10%',
            'impact': 'Company-wide'
        },
        {
            'period': '2023 Q3',
            'overall_grade': 'A+',
            'professionalism': 'S',
            'contribution': 'Top 10%',
            'impact': 'Company-wide'
        },
        {
            'period': '2023 Q4',
            'overall_grade': 'A+',
            'professionalism': 'S',
            'contribution': 'Top 10%',
            'impact': 'Company-wide'
        }
    ]
    
    # 성장 경로
    growth_path = {
        'target_job': 'Sales Team Leader',
        'total_years': 2.0,
        'success_probability': 0.90,
        'difficulty_score': 35,
        'stages': [
            {
                'job_name': 'Senior Manager',
                'expected_years': 0.5,
                'required_skills': ['Advanced Leadership', 'Strategic Planning']
            },
            {
                'job_name': 'Sales Team Leader',
                'expected_years': 1.5,
                'required_skills': ['Executive Leadership', 'P&L Management', 'Team Development']
            }
        ]
    }
    
    # 리포트 생성
    generator = LeaderReportGenerator()
    
    output_dir = tempfile.gettempdir()
    output_path = os.path.join(
        output_dir, 
        f"leader_report_{high_performer['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    )
    
    print(f"\nGenerating report for {high_performer['name']}...")
    
    report_path = generator.generate_leader_recommendation_report(
        candidate=high_performer,
        target_job=target_job,
        growth_path=growth_path,
        evaluation_history=evaluation_history,
        output_path=output_path
    )
    
    print(f"✅ Report generated successfully!")
    print(f"   Path: {report_path}")
    print(f"   Size: {os.path.getsize(report_path) / 1024:.1f} KB")


def test_development_needed_candidate():
    """개발이 필요한 후보자 리포트 테스트"""
    print("\n" + "=" * 70)
    print("테스트 2: 개발 필요 후보자 리포트")
    print("=" * 70)
    
    # 중간 성과자 데이터
    mid_performer = {
        'employee_id': 'emp002',
        'name': 'Lee Potential',
        'current_position': 'Assistant Manager',
        'department': 'Marketing Team',
        'growth_level': 'Lv.3',
        'evaluation_grade': 'B+',
        'experience_years': 5,
        'match_score': 65.2,
        'skill_match_rate': 0.60,
        'qualifications': ['Digital Marketing Certificate'],
        'matched_skills': [
            'Communication', 'Data Analysis', 'Project Management'
        ],
        'missing_skills': [
            'Leadership', 'Strategic Planning', 'Budget Management', 'Team Building'
        ],
        'recommendation_reason': 'Good performance record, high potential identified, needs leadership development',
        'risk_factors': ['Limited leadership experience', 'Skill gaps in core areas']
    }
    
    target_job = {
        'name': 'Marketing Team Leader',
        'required_skills': [
            'Leadership', 'Strategic Planning', 'Marketing Strategy',
            'Budget Management', 'Team Building', 'Data Analysis', 'Communication'
        ]
    }
    
    evaluation_history = [
        {
            'period': '2023 H1',
            'overall_grade': 'B',
            'professionalism': 'B+',
            'contribution': 'Top 50%',
            'impact': 'Team'
        },
        {
            'period': '2023 H2',
            'overall_grade': 'B+',
            'professionalism': 'B+',
            'contribution': 'Top 30%',
            'impact': 'Team'
        },
        {
            'period': '2024 H1',
            'overall_grade': 'B+',
            'professionalism': 'A',
            'contribution': 'Top 30%',
            'impact': 'Cross-team'
        }
    ]
    
    growth_path = {
        'target_job': 'Marketing Team Leader',
        'total_years': 4.5,
        'success_probability': 0.65,
        'difficulty_score': 72,
        'stages': [
            {
                'job_name': 'Manager',
                'expected_years': 2.0,
                'required_skills': ['Basic Leadership', 'Team Coordination']
            },
            {
                'job_name': 'Senior Manager',
                'expected_years': 1.5,
                'required_skills': ['Advanced Leadership', 'Strategic Thinking']
            },
            {
                'job_name': 'Marketing Team Leader',
                'expected_years': 1.0,
                'required_skills': ['Executive Leadership', 'Organizational Management']
            }
        ]
    }
    
    generator = LeaderReportGenerator()
    
    output_dir = tempfile.gettempdir()
    output_path = os.path.join(
        output_dir, 
        f"leader_report_{mid_performer['name'].replace(' ', '_')}.pdf"
    )
    
    print(f"\nGenerating report for {mid_performer['name']}...")
    
    report_path = generator.generate_leader_recommendation_report(
        candidate=mid_performer,
        target_job=target_job,
        growth_path=growth_path,
        evaluation_history=evaluation_history,
        output_path=output_path
    )
    
    print(f"✅ Report generated successfully!")
    print(f"   Path: {report_path}")
    print(f"   Recommendation: RECOMMEND WITH DEVELOPMENT")


def test_batch_report_generation():
    """배치 리포트 생성 테스트"""
    print("\n" + "=" * 70)
    print("테스트 3: 배치 리포트 생성 (팀장 후보 5명)")
    print("=" * 70)
    
    # 다양한 후보자들
    candidates = [
        {
            'employee_id': 'emp001',
            'name': 'Kim Excellence',
            'current_position': 'Manager',
            'department': 'Sales',
            'growth_level': 'Lv.4',
            'evaluation_grade': 'S',
            'experience_years': 10,
            'match_score': 92.5,
            'skill_match_rate': 0.90,
            'matched_skills': ['Leadership', 'Strategy', 'Performance Mgmt'],
            'missing_skills': ['Global Business'],
            'recommendation_reason': 'Exceptional leader with proven track record'
        },
        {
            'employee_id': 'emp002',
            'name': 'Park Ready',
            'current_position': 'Senior Manager',
            'department': 'Operations',
            'growth_level': 'Lv.4',
            'evaluation_grade': 'A+',
            'experience_years': 8,
            'match_score': 85.3,
            'skill_match_rate': 0.85,
            'matched_skills': ['Leadership', 'Process Improvement', 'Team Building'],
            'missing_skills': ['Strategic Planning', 'Budget Management'],
            'recommendation_reason': 'Strong operational excellence and team leadership'
        },
        {
            'employee_id': 'emp003',
            'name': 'Lee Growth',
            'current_position': 'Manager',
            'department': 'IT',
            'growth_level': 'Lv.3',
            'evaluation_grade': 'A',
            'experience_years': 6,
            'match_score': 72.8,
            'skill_match_rate': 0.70,
            'matched_skills': ['Technical Leadership', 'Project Management'],
            'missing_skills': ['Business Strategy', 'Financial Management', 'Org Development'],
            'recommendation_reason': 'Technical expert transitioning to business leadership'
        },
        {
            'employee_id': 'emp004',
            'name': 'Choi Potential',
            'current_position': 'Assistant Manager',
            'department': 'HR',
            'growth_level': 'Lv.3',
            'evaluation_grade': 'B+',
            'experience_years': 5,
            'match_score': 68.5,
            'skill_match_rate': 0.65,
            'matched_skills': ['HR Management', 'Communication'],
            'missing_skills': ['Leadership', 'Strategic Planning', 'Performance Management'],
            'recommendation_reason': 'High potential with HR expertise'
        },
        {
            'employee_id': 'emp005',
            'name': 'Jung Development',
            'current_position': 'Manager',
            'department': 'Finance',
            'growth_level': 'Lv.3',
            'evaluation_grade': 'B+',
            'experience_years': 7,
            'match_score': 61.2,
            'skill_match_rate': 0.55,
            'matched_skills': ['Financial Analysis', 'Risk Management'],
            'missing_skills': ['Leadership', 'Team Building', 'Communication', 'Strategy'],
            'recommendation_reason': 'Strong technical skills, needs leadership development'
        }
    ]
    
    target_job = {
        'name': 'Department Head',
        'required_skills': [
            'Leadership', 'Strategic Planning', 'Performance Management',
            'Budget Management', 'Team Building', 'Communication',
            'Business Development', 'Change Management'
        ]
    }
    
    # 배치 리포트 생성
    generator = LeaderReportGenerator()
    
    output_dir = os.path.join(tempfile.gettempdir(), f"batch_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    print(f"\nGenerating batch reports for {len(candidates)} candidates...")
    print(f"Output directory: {output_dir}")
    
    generated_files = generator.generate_batch_reports(
        candidates=candidates,
        target_job=target_job,
        output_dir=output_dir,
        include_growth_path=False,  # 간단히 하기 위해 생략
        include_evaluation_history=False
    )
    
    print(f"\n✅ Batch generation completed!")
    print(f"   Total files generated: {len(generated_files)}")
    
    # 생성된 파일 목록
    print("\n   Generated reports:")
    for i, file_path in enumerate(generated_files, 1):
        file_size = os.path.getsize(file_path) / 1024
        print(f"   {i}. {os.path.basename(file_path)} ({file_size:.1f} KB)")


def test_executive_succession_report():
    """임원 승계 리포트 테스트"""
    print("\n" + "=" * 70)
    print("테스트 4: 임원 승계 후보 리포트")
    print("=" * 70)
    
    # 임원 후보 데이터
    executive_candidate = {
        'employee_id': 'exec001',
        'name': 'Kim Executive',
        'current_position': 'Vice President',
        'department': 'Strategic Planning',
        'growth_level': 'Lv.5',
        'evaluation_grade': 'S',
        'experience_years': 18,
        'match_score': 94.8,
        'skill_match_rate': 0.92,
        'qualifications': [
            'MBA', 'CPA', 'Executive Leadership Program', 
            'Board Governance Certificate'
        ],
        'matched_skills': [
            'Executive Leadership', 'Strategic Planning', 'Financial Management',
            'M&A', 'Board Reporting', 'Global Business', 'Change Management'
        ],
        'missing_skills': ['Digital Transformation'],
        'recommendation_reason': 'Proven C-level executive with exceptional strategic and financial acumen, ready for CEO succession',
        'risk_factors': None
    }
    
    target_job = {
        'name': 'Chief Executive Officer',
        'required_skills': [
            'Executive Leadership', 'Strategic Vision', 'Financial Management',
            'Board Management', 'M&A', 'Global Business', 'Digital Transformation',
            'Stakeholder Management', 'Crisis Management'
        ],
        'qualification': 'C-level experience 5+ years, proven P&L responsibility'
    }
    
    # 임원급 평가 이력
    evaluation_history = [
        {
            'period': '2023 Annual',
            'overall_grade': 'S',
            'professionalism': 'S',
            'contribution': 'Top 5%',
            'impact': 'Enterprise-wide'
        }
    ]
    
    # 임원 성장 경로
    growth_path = {
        'target_job': 'Chief Executive Officer',
        'total_years': 1.5,
        'success_probability': 0.95,
        'difficulty_score': 25,
        'stages': [
            {
                'job_name': 'CEO Succession Pool',
                'expected_years': 0.5,
                'required_skills': ['Board Exposure', 'External Stakeholder Management']
            },
            {
                'job_name': 'Chief Executive Officer',
                'expected_years': 1.0,
                'required_skills': ['CEO Transition', 'Strategic Reset']
            }
        ]
    }
    
    generator = LeaderReportGenerator()
    
    output_path = os.path.join(
        tempfile.gettempdir(), 
        f"executive_succession_report_{executive_candidate['name'].replace(' ', '_')}.pdf"
    )
    
    print(f"\nGenerating executive succession report for {executive_candidate['name']}...")
    
    report_path = generator.generate_leader_recommendation_report(
        candidate=executive_candidate,
        target_job=target_job,
        growth_path=growth_path,
        evaluation_history=evaluation_history,
        output_path=output_path
    )
    
    print(f"✅ Executive succession report generated!")
    print(f"   Path: {report_path}")
    print(f"   Succession readiness: IMMEDIATE")


if __name__ == "__main__":
    print("리더 추천 PDF 리포트 생성 테스트")
    print("=" * 70)
    print()
    
    # 모든 테스트 실행
    test_single_candidate_report()
    test_development_needed_candidate()
    test_batch_report_generation()
    test_executive_succession_report()
    
    print("\n" + "=" * 70)
    print("모든 PDF 리포트 생성 테스트 완료!")
    print("=" * 70)
    
    # 생성된 파일 위치 안내
    print(f"\n📁 Generated reports are saved in: {tempfile.gettempdir()}")
    print("   You can open the PDF files to view the formatted reports.")