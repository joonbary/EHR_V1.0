"""
ESS 리더 성장 상태 API 테스트
개인별 리더십 추천 및 성장 경로 API 테스트
"""

import json
from datetime import datetime


def test_my_leader_growth_status():
    """개인 리더 성장 상태 API 응답 예시"""
    print("=" * 70)
    print("테스트 1: GET /api/my-leader-growth-status/")
    print("=" * 70)
    
    # API 응답 예시
    response = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "employee_info": {
            "employee_id": "123",
            "name": "홍길동",
            "current_position": "과장",
            "department": "영업팀",
            "career_years": 7,
            "growth_level": "Lv.3",
            "recent_evaluation": {
                "overall_grade": "A",
                "evaluation_date": "2024-01-15T10:00:00"
            }
        },
        "leadership_recommendations": [
            {
                "job_id": "job001",
                "job_name": "영업팀장",
                "match_score": 85.5,
                "skill_match_rate": 0.75,
                "matched_skills": ["영업전략", "성과관리", "고객관리", "협상"],
                "missing_skills": ["조직운영", "예산관리"],
                "recommendation_comment": "최근 3개 분기 연속 A등급을 받은 고성과자로, 탁월한 기여도이(가) 검증되었습니다. 영업전략, 성과관리, 고객관리 등 핵심 역량을 보유하여 영업팀장 직무에 85.5% 적합합니다. 현재 성장레벨 Lv.3을(를) 달성하여 영업팀장 보임 조건을 충족하였습니다.",
                "promotion_ready": True,
                "rank_among_candidates": 2,
                "total_candidates": 15
            },
            {
                "job_id": "job002",
                "job_name": "영업기획팀장",
                "match_score": 78.2,
                "skill_match_rate": 0.67,
                "matched_skills": ["영업전략", "데이터분석", "기획"],
                "missing_skills": ["전략수립", "조직운영", "예산관리"],
                "recommendation_comment": "평가 결과 A 전문성과 Top 20% 기여도를 보여주며, 조직 간 수준의 영향력을 발휘하고 있습니다. 전략수립와 조직운영, 예산관리 역량 보완이 필요하나, 우수한 평가 결과으로 성장 가능성이 높습니다.",
                "promotion_ready": False,
                "rank_among_candidates": 4,
                "total_candidates": 12
            },
            {
                "job_id": "job003",
                "job_name": "고객서비스팀장",
                "match_score": 72.3,
                "skill_match_rate": 0.60,
                "matched_skills": ["고객관리", "커뮤니케이션", "문제해결"],
                "missing_skills": ["서비스전략", "팀관리", "프로세스개선"],
                "recommendation_comment": "7년의 경력과 리더십 경험을(를) 바탕으로 리더십 역량이 입증되었습니다. 현재 72.3%의 적합도를 보이며, 서비스전략 개발 시 우수한 고객서비스팀장이(가) 될 것으로 기대됩니다.",
                "promotion_ready": False,
                "rank_among_candidates": 5,
                "total_candidates": 10
            }
        ],
        "growth_paths": [
            {
                "target_job": "영업팀장",
                "total_years": 2.5,
                "difficulty_score": 45,
                "success_probability": 0.82,
                "stages": [
                    {
                        "job_name": "영업파트장",
                        "expected_years": 1.0,
                        "required_skills": ["팀관리", "영업전략실행"]
                    },
                    {
                        "job_name": "영업팀장",
                        "expected_years": 1.5,
                        "required_skills": ["조직운영", "예산관리", "전략수립"]
                    }
                ]
            },
            {
                "target_job": "영업기획팀장",
                "total_years": 3.5,
                "difficulty_score": 65,
                "success_probability": 0.68,
                "stages": [
                    {
                        "job_name": "영업기획 담당",
                        "expected_years": 1.5,
                        "required_skills": ["기획력", "데이터분석"]
                    },
                    {
                        "job_name": "영업기획파트장",
                        "expected_years": 1.0,
                        "required_skills": ["전략수립", "프로젝트관리"]
                    },
                    {
                        "job_name": "영업기획팀장",
                        "expected_years": 1.0,
                        "required_skills": ["조직운영", "비즈니스전략"]
                    }
                ]
            }
        ],
        "development_needs": {
            "priority_skills": ["조직운영", "예산관리", "전략수립", "팀관리", "서비스전략"],
            "development_recommendations": [
                {
                    "skill": "조직운영",
                    "priority": "높음",
                    "required_by_jobs": 3,
                    "suggested_actions": ["조직관리 교육", "팀빌딩 활동 주도", "HR 기초 과정"]
                },
                {
                    "skill": "예산관리",
                    "priority": "높음",
                    "required_by_jobs": 2,
                    "suggested_actions": ["재무관리 기초", "예산편성 실무", "원가관리 교육"]
                },
                {
                    "skill": "전략수립",
                    "priority": "보통",
                    "required_by_jobs": 1,
                    "suggested_actions": ["전략기획 과정", "사업계획 수립 참여", "전략 사례 연구"]
                }
            ],
            "estimated_preparation_time": "6-12개월"
        },
        "report_available": True
    }
    
    print("\nAPI 응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # 주요 정보 요약
    print("\n요약:")
    print(f"직원: {response['employee_info']['name']} ({response['employee_info']['current_position']})")
    print(f"평가: {response['employee_info']['recent_evaluation']['overall_grade']} / 레벨: {response['employee_info']['growth_level']}")
    
    print("\n추천 직무:")
    for rec in response['leadership_recommendations']:
        status = "[즉시가능]" if rec['promotion_ready'] else "[준비필요]"
        print(f"  {status} {rec['job_name']} - {rec['match_score']}% (후보 순위: {rec['rank_among_candidates']}/{rec['total_candidates']})")
    
    print("\n우선 개발 필요 스킬:")
    for skill in response['development_needs']['priority_skills'][:3]:
        print(f"  - {skill}")


def test_my_leader_report_json():
    """개인 리더십 리포트 JSON API 테스트"""
    print("\n\n" + "=" * 70)
    print("테스트 2: GET /api/my-leader-report/?job_id=job001")
    print("=" * 70)
    
    response = {
        "status": "success",
        "report_data": {
            "employee": {
                "name": "홍길동",
                "position": "과장",
                "department": "영업팀"
            },
            "target_job": {
                "id": "job001",
                "name": "영업팀장"
            },
            "assessment": {
                "match_score": 85.5,
                "skill_match_rate": 0.75,
                "recommendation_comment": "최근 3개 분기 연속 A등급을 받은 고성과자로, 탁월한 기여도이(가) 검증되었습니다. 영업전략, 성과관리, 고객관리 등 핵심 역량을 보유하여 영업팀장 직무에 85.5% 적합합니다. 7년의 경력과 리더십 경험을(를) 바탕으로 리더십 역량이 입증되었습니다.",
                "matched_skills": ["영업전략", "성과관리", "고객관리", "협상", "데이터분석"],
                "missing_skills": ["조직운영", "예산관리"]
            },
            "evaluation_history": [
                {
                    "period": "2024 Q1",
                    "overall_grade": "A",
                    "professionalism": "A+",
                    "contribution": "Top 20%",
                    "impact": "조직 간"
                },
                {
                    "period": "2023 Q4",
                    "overall_grade": "A",
                    "professionalism": "A",
                    "contribution": "Top 20%",
                    "impact": "조직 간"
                },
                {
                    "period": "2023 Q3",
                    "overall_grade": "A",
                    "professionalism": "A",
                    "contribution": "Top 30%",
                    "impact": "조직 내"
                }
            ],
            "growth_path": {
                "total_years": 2.5,
                "success_probability": 0.82,
                "stages": [
                    {
                        "job_name": "영업파트장",
                        "expected_years": 1.0,
                        "required_skills": ["팀관리", "영업전략실행", "성과모니터링"]
                    },
                    {
                        "job_name": "영업팀장",
                        "expected_years": 1.5,
                        "required_skills": ["조직운영", "예산관리", "전략수립", "대외협력"]
                    }
                ]
            },
            "pdf_available": True
        }
    }
    
    print("\nAPI 응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n리포트 요약:")
    print(f"대상 직무: {response['report_data']['target_job']['name']}")
    print(f"적합도: {response['report_data']['assessment']['match_score']}%")
    print(f"예상 준비 기간: {response['report_data']['growth_path']['total_years']}년")
    print(f"성공 가능성: {response['report_data']['growth_path']['success_probability']*100:.0f}%")


def test_no_recommendation_scenario():
    """추천 불가 시나리오"""
    print("\n\n" + "=" * 70)
    print("테스트 3: 추천 불가 직원 (평가 B, 레벨 Lv.2)")
    print("=" * 70)
    
    response = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "employee_info": {
            "employee_id": "456",
            "name": "김신입",
            "current_position": "대리",
            "department": "마케팅팀",
            "career_years": 3,
            "growth_level": "Lv.2",
            "recent_evaluation": {
                "overall_grade": "B",
                "evaluation_date": "2024-01-15T10:00:00"
            }
        },
        "leadership_recommendations": [],  # 추천 없음
        "growth_paths": [
            {
                "target_job": "마케팅팀장",
                "total_years": 6.5,
                "difficulty_score": 78,
                "success_probability": 0.45,
                "stages": [
                    {
                        "job_name": "마케팅 과장",
                        "expected_years": 2.5,
                        "required_skills": ["마케팅전략", "프로젝트관리", "데이터분석"]
                    },
                    {
                        "job_name": "마케팅 차장",
                        "expected_years": 2.0,
                        "required_skills": ["팀관리", "전략수립", "예산관리"]
                    },
                    {
                        "job_name": "마케팅팀장",
                        "expected_years": 2.0,
                        "required_skills": ["조직운영", "비즈니스전략", "리더십"]
                    }
                ]
            }
        ],
        "development_needs": {
            "priority_skills": ["마케팅전략", "프로젝트관리", "데이터분석", "팀관리", "전략수립"],
            "development_recommendations": [
                {
                    "skill": "마케팅전략",
                    "priority": "높음",
                    "required_by_jobs": 1,
                    "suggested_actions": ["마케팅 전문 과정", "케이스 스터디", "실무 프로젝트"]
                }
            ],
            "estimated_preparation_time": "18개월 이상"
        },
        "report_available": False  # 리포트 생성 불가
    }
    
    print("\nAPI 응답 (추천 불가 케이스):")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n추천 불가 사유:")
    print(f"- 평가 등급 미달: {response['employee_info']['recent_evaluation']['overall_grade']} (B+ 이상 필요)")
    print(f"- 성장 레벨 미달: {response['employee_info']['growth_level']} (Lv.3 이상 필요)")
    print(f"- 예상 준비 기간: {response['growth_paths'][0]['total_years']}년 (너무 김)")
    print(f"- PDF 리포트: {'생성 가능' if response['report_available'] else '생성 불가'}")


def test_api_error_scenarios():
    """API 오류 시나리오"""
    print("\n\n" + "=" * 70)
    print("테스트 4: API 오류 응답")
    print("=" * 70)
    
    # 직원 정보 없음
    error_response_1 = {
        "status": "error",
        "message": "직원 정보를 찾을 수 없습니다."
    }
    
    print("\n1. 404 Error - 직원 정보 없음:")
    print(json.dumps(error_response_1, indent=2, ensure_ascii=False))
    
    # 서버 오류
    error_response_2 = {
        "status": "error",
        "message": "서버 오류가 발생했습니다."
    }
    
    print("\n2. 500 Error - 서버 오류:")
    print(json.dumps(error_response_2, indent=2, ensure_ascii=False))
    
    # 직무 찾을 수 없음
    error_response_3 = {
        "status": "error",
        "message": "적합한 리더 직무를 찾을 수 없습니다."
    }
    
    print("\n3. 404 Error - 적합 직무 없음:")
    print(json.dumps(error_response_3, indent=2, ensure_ascii=False))


def test_frontend_integration_example():
    """프론트엔드 통합 예시"""
    print("\n\n" + "=" * 70)
    print("테스트 5: 프론트엔드 통합 예시 (JavaScript)")
    print("=" * 70)
    
    js_code = """
// 1. 리더 성장 상태 조회
async function getMyLeaderGrowthStatus() {
    try {
        const response = await fetch('/api/my-leader-growth-status/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch growth status');
        }
        
        const data = await response.json();
        
        // UI 업데이트
        updateGrowthStatusUI(data);
        
    } catch (error) {
        console.error('Error:', error);
        showErrorMessage('성장 상태를 불러올 수 없습니다.');
    }
}

// 2. PDF 리포트 다운로드
function downloadLeaderReport(jobId) {
    const url = jobId 
        ? `/api/my-leader-report/pdf/?job_id=${jobId}`
        : '/api/my-leader-report/pdf/';
    
    // 새 창에서 다운로드
    window.open(url, '_blank');
}

// 3. UI 업데이트 함수
function updateGrowthStatusUI(data) {
    // 기본 정보 표시
    document.getElementById('employeeName').textContent = data.employee_info.name;
    document.getElementById('currentPosition').textContent = data.employee_info.current_position;
    document.getElementById('evaluationGrade').textContent = data.employee_info.recent_evaluation.overall_grade;
    
    // 추천 직무 카드 생성
    const recommendationsContainer = document.getElementById('recommendations');
    recommendationsContainer.innerHTML = '';
    
    data.leadership_recommendations.forEach(rec => {
        const card = createRecommendationCard(rec);
        recommendationsContainer.appendChild(card);
    });
    
    // 성장 경로 차트 그리기
    if (data.growth_paths.length > 0) {
        drawGrowthPathChart(data.growth_paths[0]);
    }
    
    // PDF 다운로드 버튼 활성화
    const downloadBtn = document.getElementById('downloadReportBtn');
    downloadBtn.disabled = !data.report_available;
    
    if (!data.report_available) {
        downloadBtn.title = '평가 B+ 이상, 성장레벨 Lv.3 이상일 때 생성 가능합니다.';
    }
}

// 4. 추천 직무 카드 생성
function createRecommendationCard(recommendation) {
    const card = document.createElement('div');
    card.className = 'recommendation-card';
    
    const statusBadge = recommendation.promotion_ready 
        ? '<span class="badge badge-success">즉시 가능</span>'
        : '<span class="badge badge-warning">준비 필요</span>';
    
    card.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">
                    ${recommendation.job_name} 
                    ${statusBadge}
                </h5>
                <div class="progress mb-2">
                    <div class="progress-bar" style="width: ${recommendation.match_score}%">
                        ${recommendation.match_score}%
                    </div>
                </div>
                <p class="card-text">${recommendation.recommendation_comment}</p>
                <div class="skills-section">
                    <strong>보유 역량:</strong> ${recommendation.matched_skills.join(', ')}<br>
                    <strong>개발 필요:</strong> ${recommendation.missing_skills.join(', ')}
                </div>
                <button class="btn btn-primary mt-2" 
                        onclick="downloadLeaderReport('${recommendation.job_id}')">
                    리포트 다운로드
                </button>
            </div>
        </div>
    `;
    
    return card;
}
"""
    
    print("\n프론트엔드 JavaScript 예시:")
    print(js_code)
    
    html_template = """
<!-- ESS 리더 성장 현황 페이지 -->
<div class="container mt-4">
    <h2>나의 리더십 성장 현황</h2>
    
    <!-- 기본 정보 카드 -->
    <div class="card mb-4">
        <div class="card-body">
            <h5 class="card-title">기본 정보</h5>
            <div class="row">
                <div class="col-md-3">
                    <strong>이름:</strong> <span id="employeeName"></span>
                </div>
                <div class="col-md-3">
                    <strong>직급:</strong> <span id="currentPosition"></span>
                </div>
                <div class="col-md-3">
                    <strong>평가등급:</strong> <span id="evaluationGrade"></span>
                </div>
                <div class="col-md-3">
                    <button id="downloadReportBtn" class="btn btn-primary">
                        종합 리포트 다운로드
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 추천 직무 섹션 -->
    <h4>추천 리더 직무</h4>
    <div id="recommendations" class="row">
        <!-- 동적으로 생성됨 -->
    </div>
    
    <!-- 성장 경로 차트 -->
    <div class="mt-4">
        <h4>성장 경로</h4>
        <canvas id="growthPathChart"></canvas>
    </div>
</div>
"""
    
    print("\nHTML 템플릿:")
    print(html_template)


if __name__ == "__main__":
    print("=" * 70)
    print("ESS 리더 성장 상태 API 테스트")
    print("=" * 70)
    
    # 모든 테스트 실행
    test_my_leader_growth_status()
    test_my_leader_report_json()
    test_no_recommendation_scenario()
    test_api_error_scenarios()
    test_frontend_integration_example()
    
    print("\n" + "=" * 70)
    print("모든 API 테스트 완료!")
    print("=" * 70)