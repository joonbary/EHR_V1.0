
# 직무 통합 시스템 사용 예제

import asyncio
from job_profile_live_integration import (
    JobProfileStandardizer, JobSearchService, JobChatbotService, JobProfileSync
)

# 1. 직무명 표준화
async def test_standardization():
    standardizer = JobProfileStandardizer()
    
    # 실시간 직무 매칭
    result = await standardizer.find_best_match("HRM 담당자")
    print(f"매칭 결과: {result.matched_job['job_title']}")
    print(f"신뢰도: {result.confidence}")

# 2. 직무 검색
async def test_search():
    search_service = JobSearchService()
    
    # 검색 실행
    results = await search_service.search_jobs(
        query="시스템 개발",
        filters={'job_category': 'IT/디지털'},
        page=1,
        page_size=10
    )
    
    print(f"검색 결과: {results['total']}개")
    for job in results['jobs']:
        print(f"- {job['job_title']} (점수: {job['score']})")

# 3. AI 챗봇
async def test_chatbot():
    chatbot = JobChatbotService(openai_api_key="your-api-key")
    
    response = await chatbot.process_job_query(
        query="시스템 기획자가 되려면 어떤 스킬이 필요한가요?",
        user_context={'department': 'IT', 'experience': '신입'}
    )
    
    print(f"챗봇 응답: {response['response']}")

# 4. 실시간 동기화
async def test_sync():
    sync_service = JobProfileSync()
    
    # 단일 직무 동기화
    result = sync_service.sync_to_elasticsearch(job_profile_id=1)
    print(f"동기화 결과: {result.success}")
    
    # 전체 배치 동기화
    batch_result = await sync_service.batch_sync_all()
    print(f"배치 동기화: {batch_result.affected_records}개 처리")

# 5. Django REST API 사용
# GET /api/jobs/search/?q=시스템기획&job_type=IT기획
# POST /api/jobs/chatbot/ {"query": "데이터 분석가 전망", "context": {}}
# POST /api/jobs/sync/ {"type": "all"}

# 6. JavaScript 프론트엔드 연동
js_example = '''
// 직무 검색 API 호출
async function searchJobs(query, filters = {}) {
    const params = new URLSearchParams({ q: query, ...filters });
    const response = await fetch(`/api/jobs/search/?${params}`);
    return await response.json();
}

// AI 챗봇 API 호출
async function askChatbot(query, context = {}) {
    const response = await fetch('/api/jobs/chatbot/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, context })
    });
    return await response.json();
}

// 실시간 검색 자동완성
async function getJobSuggestions(partial) {
    const search = new JobSearchService();
    return await search.get_job_suggestions(partial);
}
'''

if __name__ == '__main__':
    # 테스트 실행
    asyncio.run(test_standardization())
    asyncio.run(test_search())
    # asyncio.run(test_chatbot())  # API 키 필요
    asyncio.run(test_sync())
