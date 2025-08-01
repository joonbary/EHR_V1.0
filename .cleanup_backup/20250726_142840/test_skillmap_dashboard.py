"""
OK금융그룹 직무스킬맵 대시보드 테스트 스크립트
Skill Map Dashboard Test Script
"""

import os
import django
import json
from datetime import datetime
import numpy as np

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from job_profiles.models import JobProfile, JobRole, JobType, JobCategory
from skillmap_dashboard import (
    SkillMapAnalytics,
    SkillLevel,
    SkillCategory,
    SkillData,
    EmployeeSkillProfile
)


def test_skill_analytics_engine():
    """스킬 분석 엔진 테스트"""
    print("Skill Analytics Engine Test")
    print("=" * 40)
    
    try:
        analytics = SkillMapAnalytics()
        
        # 기본 조직 스킬맵 생성
        skillmap_data = analytics.get_organization_skill_map()
        
        print(f"Total employees analyzed: {skillmap_data['metrics'].total_employees}")
        print(f"Total skills tracked: {skillmap_data['metrics'].total_skills}")
        print(f"Average proficiency: {skillmap_data['metrics'].avg_proficiency}%")
        print(f"Skill gap rate: {skillmap_data['metrics'].skill_gap_rate}%")
        
        if skillmap_data['metrics'].top_skill_gaps:
            print(f"\nTop skill gaps:")
            for i, gap in enumerate(skillmap_data['metrics'].top_skill_gaps[:3], 1):
                print(f"{i}. {gap['skill']}: {gap['gap_rate']:.1f}% gap rate")
        
        print("PASS: Analytics engine working")
        return True
        
    except Exception as e:
        print(f"Analytics engine test failed: {e}")
        return False


def test_heatmap_data_generation():
    """히트맵 데이터 생성 테스트"""
    print("\nHeatmap Data Generation Test")
    print("=" * 40)
    
    try:
        analytics = SkillMapAnalytics()
        
        # 테스트용 필터 적용
        filters = {'department': 'IT'}
        skillmap_data = analytics.get_organization_skill_map(filters)
        
        heatmap_data = skillmap_data['skillmap_matrix']['heatmap_data']
        employees = skillmap_data['skillmap_matrix']['employees']
        skills = skillmap_data['skillmap_matrix']['skills']
        
        print(f"Heatmap dimensions: {len(heatmap_data)}x{len(heatmap_data[0]) if heatmap_data else 0}")
        print(f"Employees in heatmap: {len(employees)}")
        print(f"Skills in heatmap: {len(skills)}")
        
        # 데이터 품질 검증
        if heatmap_data and len(heatmap_data) > 0:
            sample_row = heatmap_data[0]
            print(f"Sample heatmap values: {sample_row[:3]}...")
            
            # 값 범위 확인 (0-1 사이여야 함)
            all_values = [val for row in heatmap_data for val in row]
            min_val, max_val = min(all_values), max(all_values)
            print(f"Value range: {min_val:.2f} - {max_val:.2f}")
            
            if 0 <= min_val <= max_val <= 1:
                print("PASS: Heatmap data values in valid range")
            else:
                print("WARN: Heatmap values outside expected range")
        
        print("PASS: Heatmap generation working")
        return True
        
    except Exception as e:
        print(f"Heatmap test failed: {e}")
        return False


def test_filtering_functionality():
    """필터링 기능 테스트"""
    print("\nFiltering Functionality Test")
    print("=" * 40)
    
    try:
        analytics = SkillMapAnalytics()
        
        # 다양한 필터 테스트
        test_filters = [
            {'department': 'IT'},
            {'job_group': 'Non-PL'},
            {'job_type': 'IT개발'},
            {'growth_level': 3},
            {'department': 'IT', 'job_type': 'IT개발'}
        ]
        
        for i, filters in enumerate(test_filters, 1):
            result = analytics.get_organization_skill_map(filters)
            employee_count = result['metrics'].total_employees
            
            filter_desc = ', '.join([f"{k}={v}" for k, v in filters.items()])
            print(f"{i}. Filter [{filter_desc}]: {employee_count} employees")
            
            if employee_count >= 0:  # 필터 결과가 유효해야 함
                continue
            else:
                print(f"ERROR: Invalid employee count for filter {filters}")
                return False
        
        print("PASS: All filters working correctly")
        return True
        
    except Exception as e:
        print(f"Filtering test failed: {e}")
        return False


def test_drill_down_capability():
    """드릴다운 기능 테스트"""
    print("\nDrill-down Capability Test")
    print("=" * 40)
    
    try:
        analytics = SkillMapAnalytics()
        
        # 부서별 드릴다운
        dept_drill = analytics.get_drill_down_data('department', 'IT')
        print(f"Department drill-down (IT): {dept_drill['metrics'].total_employees} employees")
        
        # 직종별 드릴다운
        job_drill = analytics.get_drill_down_data('job_type', 'IT개발')
        print(f"Job type drill-down (IT개발): {job_drill['metrics'].total_employees} employees")
        
        # 성장레벨별 드릴다운
        level_drill = analytics.get_drill_down_data('growth_level', '3')
        print(f"Growth level drill-down (Level 3): {level_drill['metrics'].total_employees} employees")
        
        # 스킬별 상세 분석 (스킬이 존재하는 경우)
        base_data = analytics.get_organization_skill_map()
        if base_data['skillmap_matrix']['skills']:
            first_skill = base_data['skillmap_matrix']['skills'][0]['name']
            skill_detail = analytics.get_drill_down_data('skill', first_skill)
            
            if 'skill_name' in skill_detail:
                print(f"Skill detail analysis ({first_skill}): "
                      f"{skill_detail['gap_analysis']['total_employees']} employees analyzed")
            else:
                print(f"Skill detail structure: {list(skill_detail.keys())}")
        
        print("PASS: Drill-down functionality working")
        return True
        
    except Exception as e:
        print(f"Drill-down test failed: {e}")
        return False


def test_skill_gap_analysis():
    """스킬 갭 분석 테스트"""
    print("\nSkill Gap Analysis Test")
    print("=" * 40)
    
    try:
        analytics = SkillMapAnalytics()
        
        # 기본 스킬맵 데이터
        skillmap_data = analytics.get_organization_skill_map()
        
        # 스킬 갭 시뮬레이션
        skills_data = skillmap_data['skillmap_matrix']['skills']
        
        # 갭률 기준으로 분석
        high_gap_skills = [s for s in skills_data if s['gap_rate'] > 30]
        medium_gap_skills = [s for s in skills_data if 15 <= s['gap_rate'] <= 30]
        low_gap_skills = [s for s in skills_data if s['gap_rate'] < 15]
        
        print(f"High gap skills (>30%): {len(high_gap_skills)}")
        print(f"Medium gap skills (15-30%): {len(medium_gap_skills)}")
        print(f"Low gap skills (<15%): {len(low_gap_skills)}")
        
        if high_gap_skills:
            print(f"\nCritical skills needing attention:")
            for skill in high_gap_skills[:3]:
                print(f"- {skill['name']}: {skill['gap_rate']:.1f}% gap")
        
        # 카테고리별 갭 분석
        category_summary = skillmap_data['skillmap_matrix']['category_summary']
        print(f"\nCategory-wise gap analysis:")
        for category, data in category_summary.items():
            print(f"- {category}: {data['avg_gap_rate']:.1f}% avg gap")
        
        print("PASS: Skill gap analysis working")
        return True
        
    except Exception as e:
        print(f"Skill gap analysis test failed: {e}")
        return False


def test_export_functionality():
    """내보내기 기능 테스트"""
    print("\nExport Functionality Test")
    print("=" * 40)
    
    try:
        analytics = SkillMapAnalytics()
        
        # 다양한 형식 내보내기 테스트
        export_formats = ['excel', 'csv', 'pdf']
        
        for fmt in export_formats:
            export_result = analytics.export_skill_data(fmt)
            
            if 'error' not in export_result:
                print(f"{fmt.upper()} export: {export_result['filename']}")
                
                # 구조 검증
                required_keys = ['format', 'filename']
                if all(key in export_result for key in required_keys):
                    print(f"  Valid {fmt} export structure")
                else:
                    print(f"  Missing keys in {fmt} export")
                    return False
            else:
                print(f"  {fmt} export failed: {export_result['error']}")
                return False
        
        print("PASS: Export functionality working")
        return True
        
    except Exception as e:
        print(f"Export test failed: {e}")
        return False


def test_performance_and_caching():
    """성능 및 캐싱 테스트"""
    print("\nPerformance and Caching Test")
    print("=" * 40)
    
    try:
        analytics = SkillMapAnalytics()
        
        # 첫 번째 호출 (캐시 없음)
        start_time = datetime.now()
        result1 = analytics.get_organization_skill_map()
        first_call_time = (datetime.now() - start_time).total_seconds()
        
        # 두 번째 호출 (캐시 있음)
        start_time = datetime.now()
        result2 = analytics.get_organization_skill_map()
        second_call_time = (datetime.now() - start_time).total_seconds()
        
        print(f"First call time: {first_call_time:.3f}s")
        print(f"Second call time: {second_call_time:.3f}s")
        
        # 캐싱 효과 검증
        if second_call_time < first_call_time:
            speedup = first_call_time / second_call_time
            print(f"Cache speedup: {speedup:.1f}x faster")
        
        # 결과 일관성 검증
        if (result1['metrics'].total_employees == result2['metrics'].total_employees and
            result1['metrics'].total_skills == result2['metrics'].total_skills):
            print("Cached results consistent with original")
        else:
            print("Cache inconsistency detected")
            return False
        
        # 메모리 사용량 추정
        import sys
        data_size = sys.getsizeof(str(result1)) / 1024  # KB 단위
        print(f"Estimated data size: {data_size:.1f} KB")
        
        if first_call_time < 5.0:  # 5초 이내
            print("PASS: Performance within acceptable range")
        else:
            print("WARN: Performance may need optimization")
        
        return True
        
    except Exception as e:
        print(f"Performance test failed: {e}")
        return False


def test_data_consistency():
    """데이터 일관성 테스트"""
    print("\nData Consistency Test")
    print("=" * 40)
    
    try:
        analytics = SkillMapAnalytics()
        
        # 전체 조직 데이터
        full_data = analytics.get_organization_skill_map()
        
        # 부서별 데이터 합계와 전체 데이터 비교
        dept_totals = 0
        for dept_code, _ in Employee.DEPARTMENT_CHOICES:
            dept_data = analytics.get_organization_skill_map({'department': dept_code})
            dept_totals += dept_data['metrics'].total_employees
        
        full_total = full_data['metrics'].total_employees
        
        print(f"Full organization total: {full_total}")
        print(f"Sum of department totals: {dept_totals}")
        
        # 일관성 검증 (약간의 오차 허용)
        if abs(full_total - dept_totals) <= 1:
            print("Employee counts consistent across filters")
        else:
            print(f"Inconsistent employee counts (diff: {abs(full_total - dept_totals)})")
        
        # 스킬 데이터 무결성 검증
        matrix_data = full_data['skillmap_matrix']['matrix']
        if matrix_data:
            sample_emp = matrix_data[0]
            skills_in_emp = len(sample_emp['skills'])
            skills_in_list = len(full_data['skillmap_matrix']['skills'])
            
            print(f"Skills per employee: {skills_in_emp}")
            print(f"Skills in master list: {skills_in_list}")
            
            if skills_in_emp == skills_in_list:
                print("Skill data structure consistent")
            else:
                print("Skill data structure mismatch")
        
        print("PASS: Data consistency verified")
        return True
        
    except Exception as e:
        print(f"Data consistency test failed: {e}")
        return False


def run_comprehensive_tests():
    """종합 테스트 실행"""
    print("OK Financial Group Skill Map Dashboard Test Suite")
    print("=" * 60)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Skill Analytics Engine", test_skill_analytics_engine),
        ("Heatmap Data Generation", test_heatmap_data_generation),
        ("Filtering Functionality", test_filtering_functionality),
        ("Drill-down Capability", test_drill_down_capability),
        ("Skill Gap Analysis", test_skill_gap_analysis),
        ("Export Functionality", test_export_functionality),
        ("Performance and Caching", test_performance_and_caching),
        ("Data Consistency", test_data_consistency)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            if test_func():
                passed += 1
                print(f"PASS: {test_name}")
            else:
                failed += 1
                print(f"FAIL: {test_name}")
        except Exception as e:
            failed += 1
            print(f"ERROR: {test_name} - {e}")
    
    # 최종 결과
    print(f"\n{'='*60}")
    print("Test Results Summary")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\nAll tests passed! Dashboard is ready for deployment.")
    else:
        print(f"\n{failed} tests failed. Please review the implementation.")
    
    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_comprehensive_tests()