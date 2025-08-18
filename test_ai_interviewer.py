#!/usr/bin/env python
"""
AI 면접관 기능 테스트 스크립트
"""
import os
import sys
import django
from datetime import date, timedelta
import uuid

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from ai_interviewer.models import InterviewSession, InterviewTemplate, InterviewQuestion
from ai_interviewer.services import AIInterviewer, InterviewTemplateManager, InterviewAnalyzer
from job_profiles.models import JobProfile
from employees.models import Employee

def create_test_data():
    """테스트 데이터 생성"""
    print("테스트 데이터 생성 중...")
    
    # 기본 템플릿 생성
    InterviewTemplateManager.create_default_templates()
    print("기본 템플릿 생성 완료")
    
    # 테스트용 채용공고 생성 (이미 있다면 사용)
    job_profile = JobProfile.objects.filter(status='ACTIVE').first()
    if not job_profile:
        print("활성 채용공고가 없습니다. 먼저 채용공고를 생성해주세요.")
        return None
        
    print(f"사용할 채용공고: {job_profile.title}")
    return job_profile

def test_create_session():
    """면접 세션 생성 테스트"""
    print("\n=== 면접 세션 생성 테스트 ===")
    
    job_profile = create_test_data()
    if not job_profile:
        return None
    
    # 면접 세션 생성
    session = InterviewSession.objects.create(
        title=f"{job_profile.title} AI 면접 테스트",
        job_profile=job_profile,
        candidate_name="테스트 응시자",
        candidate_email="test@example.com",
        session_type='BEHAVIORAL',
        difficulty_level='INTERMEDIATE',
        expected_duration=20,
        max_questions=5
    )
    
    print(f"세션 생성됨: {session.session_id}")
    print(f"응시자: {session.candidate_name}")
    print(f"채용공고: {session.job_profile.title}")
    
    return session

def test_start_interview(session):
    """면접 시작 테스트"""
    print(f"\n=== 면접 시작 테스트 ({session.session_id}) ===")
    
    try:
        interviewer = AIInterviewer(session)
        result = interviewer.start_interview()
        
        if result['success']:
            print("면접 시작 성공!")
            print(f"상태: {result['status']}")
            print(f"메시지: {result['message']}")
            
            # 첫 번째 질문 확인
            first_question = session.questions.first()
            if first_question:
                print(f"첫 번째 질문: {first_question.question_text}")
                return first_question
            
        else:
            print(f"면접 시작 실패: {result.get('error', '알 수 없는 오류')}")
            
    except Exception as e:
        print(f"면접 시작 오류: {e}")
    
    return None

def test_submit_response(session, question):
    """응답 제출 테스트"""
    print(f"\n=== 응답 제출 테스트 ===")
    
    from ai_interviewer.models import InterviewResponse
    from django.utils import timezone
    
    try:
        # 가상 응답 생성
        test_response = f"안녕하세요. {session.job_profile.title} 포지션에 지원한 {session.candidate_name}입니다. 이 직무에 대해 매우 관심이 있으며, 제가 가진 경험과 역량을 통해 회사에 기여할 수 있다고 생각합니다."
        
        response = InterviewResponse.objects.create(
            question=question,
            response_text=test_response,
            started_at=timezone.now() - timedelta(seconds=45),
            response_time_seconds=45.0
        )
        
        print(f"응답 제출됨: {len(test_response)}자")
        print(f"응답 시간: {response.response_time_seconds}초")
        
        # AI 평가 수행
        interviewer = AIInterviewer(session)
        evaluation_result = interviewer.evaluate_response(response)
        
        if evaluation_result['success']:
            print(f"AI 평가 완료!")
            print(f"평가 점수: {response.ai_score}/10")
            print(f"품질 등급: {response.quality_rating}")
            
            # 다음 질문 생성
            if evaluation_result['next_question_ready']:
                next_question = interviewer.generate_next_question(response)
                print(f"다음 질문: {next_question.question_text}")
                return next_question
        
        return response
        
    except Exception as e:
        print(f"응답 제출 오류: {e}")
        return None

def test_complete_interview(session):
    """면접 완료 테스트"""
    print(f"\n=== 면접 완료 테스트 ===")
    
    try:
        interviewer = AIInterviewer(session)
        completion_result = interviewer.complete_interview()
        
        if completion_result['success']:
            print("면접 완료 성공!")
            print(f"최종 점수: {completion_result['final_score']}/10")
            print(f"소요 시간: {completion_result['duration_minutes']}분")
            print(f"상태: {completion_result['status']}")
            
            # 세션 정보 업데이트 확인
            session.refresh_from_db()
            print(f"총 질문 수: {session.total_questions_asked}")
            print(f"총 응답 수: {session.total_responses}")
            
        else:
            print(f"면접 완료 실패: {completion_result.get('error')}")
        
        return completion_result
        
    except Exception as e:
        print(f"면접 완료 오류: {e}")
        return None

def test_statistics():
    """통계 조회 테스트"""
    print(f"\n=== 통계 조회 테스트 ===")
    
    try:
        stats = InterviewAnalyzer.get_session_statistics()
        print(f"총 세션 수: {stats['total_sessions']}")
        print(f"완료된 세션: {stats['completed_sessions']}")
        print(f"진행 중인 세션: {stats['in_progress_sessions']}")
        print(f"평균 점수: {stats['average_score']:.2f}")
        print(f"완료율: {stats['completion_rate']:.1f}%")
        
    except Exception as e:
        print(f"통계 조회 오류: {e}")

def run_full_test():
    """전체 테스트 실행"""
    print("AIRISS AI Quick Win Phase 4 - AI 면접관 테스트")
    print("=" * 60)
    
    # 1. 세션 생성
    session = test_create_session()
    if not session:
        print("테스트 중단: 세션 생성 실패")
        return
    
    # 2. 면접 시작
    first_question = test_start_interview(session)
    if not first_question:
        print("테스트 중단: 면접 시작 실패")
        return
    
    # 3. 첫 번째 응답
    response_or_next = test_submit_response(session, first_question)
    
    # 4. 추가 질문/응답 (간단히 1회만)
    if hasattr(response_or_next, 'question_text'):  # 다음 질문이 있는 경우
        test_submit_response(session, response_or_next)
    
    # 5. 면접 완료
    test_complete_interview(session)
    
    # 6. 통계 확인
    test_statistics()
    
    print(f"\n테스트 완료! 대시보드에서 확인하세요:")
    print(f"http://localhost:8000/ai-interviewer/")

if __name__ == "__main__":
    run_full_test()