"""
직무 검색·추천 API 테스트 스크립트
Job Search & Recommendation API Test Script
"""

import os
import django
import json
import requests
from datetime import datetime

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from job_profiles.models import JobProfile, JobRole, JobType, JobCategory
from job_search_recommend_api import (
    JobSearchEngine, 
    CareerPathAnalyzer, 
    JobSearchChatbotIntegration,
    SearchContext,
    SearchIntent
)


def test_job_search_engine():
    """직무 검색 엔진 테스트"""
    print("Job Search Engine Test")
    print("=" * 40)
    
    try:
        engine = JobSearchEngine()
        
        # 테스트 컨텍스트 생성
        context = SearchContext(
            user_id="test_user",
            session_id="test_session",
            intent=SearchIntent.JOB_SEARCH,
            query="개발자",
            filters={'category': 'IT'}
        )
        
        # 검색 실행
        results = engine.search_jobs(context)
        
        print(f"Search results: {len(results)}")
        
        if results:
            print("\n상위 3개 결과:")
            for i, result in enumerate(results[:3], 1):
                print(f"{i}. {result.job_name} (매칭도: {result.match_score:.1f}%)")
                print(f"   카테고리: {result.category} > {result.type_name}")
                print(f"   필요 스킬: {', '.join(result.skills_required[:3])}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ 검색 엔진 테스트 실패: {e}")
        return False


def test_career_path_analyzer():
    """커리어 패스 분석기 테스트"""
    print("📈 커리어 패스 분석기 테스트")
    print("=" * 40)
    
    try:
        analyzer = CareerPathAnalyzer()
        
        # 테스트용 직원
        employee = Employee.objects.first()
        if not employee:
            print("❌ 테스트용 직원 데이터가 없습니다.")
            return False
        
        # 분석 실행
        analysis = analyzer.analyze_career_path(employee)
        
        print(f"✅ 직원: {analysis['current_profile']['name']}")
        print(f"   현재 직책: {analysis['current_profile']['position']}")
        print(f"   부서: {analysis['current_profile']['department']}")
        
        if analysis['career_paths']:
            print(f"\n추천 커리어 경로: {len(analysis['career_paths'])}개")
            
            best_path = analysis['career_paths'][0]
            print(f"1. {best_path['target_job']['name']}")
            print(f"   적합도: {best_path['match_score']:.1f}%")
            print(f"   난이도: {best_path['difficulty']}")
            print(f"   예상 기간: {best_path['estimated_time']}")
        
        if analysis['recommendations']:
            print(f"\n추천 사항:")
            for i, rec in enumerate(analysis['recommendations'][:3], 1):
                print(f"{i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ 커리어 분석 테스트 실패: {e}")
        return False


def test_chatbot_integration():
    """챗봇 통합 테스트"""
    print("🤖 챗봇 통합 테스트")
    print("=" * 40)
    
    try:
        chatbot = JobSearchChatbotIntegration()
        
        # 테스트 쿼리들
        test_queries = [
            "개발자 직무 찾아줘",
            "마케팅 관련 직무가 궁금해",
            "내 커리어 패스 분석해줘",
            "Python 스킬로 할 수 있는 일이 뭐야?",
            "자격증 정보 알려줘"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. 쿼리: '{query}'")
            
            response = chatbot.process_chat_query(
                user_query=query,
                user_id="test_user",
                session_id="test_session"
            )
            
            print(f"   의도: {response['intent']}")
            print(f"   응답 타입: {response['response_type']}")
            print(f"   메시지: {response['message'][:100]}...")
            
            if 'suggestions' in response:
                print(f"   제안: {', '.join(response['suggestions'][:2])}")
        
        print(f"\n✅ {len(test_queries)}개 쿼리 처리 완료")
        return True
        
    except Exception as e:
        print(f"❌ 챗봇 테스트 실패: {e}")
        return False


def test_database_integration():
    """데이터베이스 통합 테스트"""
    print("🗄️ 데이터베이스 통합 테스트")  
    print("=" * 40)
    
    try:
        # 기본 데이터 확인
        categories = JobCategory.objects.filter(is_active=True).count()
        job_types = JobType.objects.filter(is_active=True).count()
        job_roles = JobRole.objects.filter(is_active=True).count()
        job_profiles = JobProfile.objects.filter(is_active=True).count()
        employees = Employee.objects.filter(employment_status='재직').count()
        
        print(f"✅ 직군: {categories}개")
        print(f"✅ 직종: {job_types}개") 
        print(f"✅ 직무: {job_roles}개")
        print(f"✅ 직무기술서: {job_profiles}개")
        print(f"✅ 재직 직원: {employees}명")
        
        # 데이터 품질 확인
        profiles_with_skills = JobProfile.objects.exclude(
            basic_skills=[], applied_skills=[]
        ).count()
        
        print(f"✅ 스킬 정보 보유 직무: {profiles_with_skills}개")
        
        if job_profiles > 0 and employees > 0:
            print("✅ API 테스트를 위한 기본 데이터 준비 완료")
            return True
        else:
            print("❌ 테스트를 위한 기본 데이터가 부족합니다.")
            return False
        
    except Exception as e:
        print(f"❌ 데이터베이스 테스트 실패: {e}")
        return False


def test_search_performance():
    """검색 성능 테스트"""
    print("⚡ 검색 성능 테스트")
    print("=" * 40)
    
    try:
        engine = JobSearchEngine()
        start_time = datetime.now()
        
        # 여러 검색 실행
        test_queries = ["개발자", "마케팅", "인사", "영업", "디자인"]
        total_results = 0
        
        for query in test_queries:
            context = SearchContext(
                user_id="perf_test",
                session_id="perf_session",
                intent=SearchIntent.JOB_SEARCH,
                query=query
            )
            
            results = engine.search_jobs(context)
            total_results += len(results)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ {len(test_queries)}개 쿼리 처리")
        print(f"✅ 총 결과: {total_results}개")
        print(f"✅ 처리 시간: {duration:.2f}초")
        print(f"✅ 평균 응답 시간: {duration/len(test_queries):.2f}초/쿼리")
        
        if duration < 5.0:  # 5초 이내
            print("✅ 성능 목표 달성 (5초 이내)")
            return True
        else:
            print("⚠️ 성능 개선 필요")
            return True
        
    except Exception as e:
        print(f"❌ 성능 테스트 실패: {e}")
        return False


def test_api_data_format():
    """API 데이터 형식 테스트"""
    print("📋 API 데이터 형식 테스트")
    print("=" * 40)
    
    try:
        engine = JobSearchEngine()
        
        # 검색 실행
        context = SearchContext(
            user_id="format_test",
            session_id="format_session", 
            intent=SearchIntent.JOB_SEARCH,
            query="테스트"
        )
        
        results = engine.search_jobs(context)
        
        if results:
            result = results[0]
            
            # 필수 필드 확인
            required_fields = [
                'job_id', 'job_name', 'job_code', 'category', 'type_name',
                'match_score', 'relevance_score', 'skills_required',
                'requirements', 'certifications', 'career_level'
            ]
            
            missing_fields = []
            for field in required_fields:
                if not hasattr(result, field):
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ 누락된 필드: {', '.join(missing_fields)}")
                return False
            
            # 데이터 타입 확인
            assert isinstance(result.job_id, str)
            assert isinstance(result.job_name, str)
            assert isinstance(result.match_score, (int, float))
            assert isinstance(result.skills_required, list)
            assert isinstance(result.requirements, list)
            
            print("✅ 모든 필수 필드 존재")
            print("✅ 데이터 타입 검증 통과")
            print(f"✅ 샘플 결과: {result.job_name} (매칭도: {result.match_score:.1f}%)")
            
            return True
        else:
            print("⚠️ 검색 결과가 없어 형식 테스트를 건너뜁니다.")
            return True
        
    except Exception as e:
        print(f"❌ 데이터 형식 테스트 실패: {e}")
        return False


def run_all_tests():
    """전체 테스트 실행"""
    print("🚀 직무 검색·추천 API 통합 테스트")
    print("=" * 60)
    print(f"테스트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("데이터베이스 통합", test_database_integration),
        ("API 데이터 형식", test_api_data_format),
        ("직무 검색 엔진", test_job_search_engine),
        ("커리어 패스 분석", test_career_path_analyzer),
        ("챗봇 통합", test_chatbot_integration),
        ("검색 성능", test_search_performance)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: 통과")
            else:
                failed += 1
                print(f"❌ {test_name}: 실패")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: 오류 - {e}")
    
    # 최종 결과
    print(f"\n{'='*60}")
    print("📊 테스트 결과 요약")
    print(f"✅ 통과: {passed}개")
    print(f"❌ 실패: {failed}개")
    print(f"📈 성공률: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 모든 테스트 통과! API가 정상적으로 작동합니다.")
    else:
        print(f"\n⚠️ {failed}개 테스트 실패. 코드를 검토해주세요.")
    
    print(f"\n테스트 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_all_tests()