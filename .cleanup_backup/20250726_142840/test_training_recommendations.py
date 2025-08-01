"""
교육 추천 API 테스트
다양한 시나리오에 대한 교육 추천 및 수강 신청 테스트
"""

import json
from datetime import datetime, timedelta


def test_growth_training_recommendations():
    """개인 성장 교육 추천 API 테스트"""
    print("=" * 70)
    print("테스트 1: GET /api/my-growth-training-recommendations/")
    print("=" * 70)
    
    # API 응답 예시
    response = {
        "status": "success",
        "employee": {
            "id": "E1007",
            "name": "김과장",
            "position": "과장",
            "department": "전략기획팀",
            "current_level": "Lv.3"
        },
        "context": {
            "target_job": "전략기획팀장",
            "missing_skills": ["전략수립", "조직운영", "예산관리"]
        },
        "recommendations": [
            {
                "course_id": "C-203",
                "course_code": "STR-ADV-001",
                "title": "전략적 사고와 비즈니스 기획",
                "category": "리더십",
                "provider": "한국생산성본부",
                "course_type": "BLENDED",
                "duration_hours": 24,
                "cost": 600000,
                "match_score": 85.5,
                "priority": 90,
                "skill_coverage": 33.3,
                "matched_skills": ["전략수립"],
                "recommendation_reason": "전략기획팀장 직무에 필요한 전략수립 스킬을 습득할 수 있습니다. 성장레벨 인증에 도움이 되는 교육입니다. 온라인으로 편리하게 수강 가능합니다.",
                "expected_completion_time": "3주",
                "can_enroll": True,
                "enrollment_message": "",
                "next_session": {
                    "start_date": "2024-03-01",
                    "end_date": "2024-03-15",
                    "enrollment_deadline": "2024-02-20",
                    "seats_available": 15,
                    "location": "온라인 + 오프라인"
                },
                "completion_rate": 87.5,
                "average_satisfaction": 4.5,
                "growth_impact": {
                    "level_progress": 0.2,
                    "certification_eligible": True,
                    "next_level_contribution": 0.15
                }
            },
            {
                "course_id": "C-157",
                "course_code": "ORG-INT-002",
                "title": "조직관리와 성과창출",
                "category": "리더십",
                "provider": "사내교육",
                "course_type": "ONLINE",
                "duration_hours": 16,
                "cost": 0,
                "match_score": 82.3,
                "priority": 85,
                "skill_coverage": 33.3,
                "matched_skills": ["조직운영"],
                "recommendation_reason": "전략기획팀장 직무에 필요한 조직운영 스킬을 습득할 수 있습니다. 이 과정은 필수 이수 교육입니다. 온라인으로 편리하게 수강 가능합니다.",
                "expected_completion_time": "2주",
                "can_enroll": True,
                "enrollment_message": "",
                "next_session": {
                    "start_date": "2024-02-15",
                    "end_date": "2024-02-28",
                    "enrollment_deadline": "2024-02-10",
                    "seats_available": 30,
                    "location": "온라인"
                },
                "completion_rate": 92.3,
                "average_satisfaction": 4.3,
                "growth_impact": {
                    "level_progress": 0.15,
                    "certification_eligible": False,
                    "next_level_contribution": 0.1
                }
            },
            {
                "course_id": "C-089",
                "course_code": "FIN-INT-003",
                "title": "예산편성과 재무관리 실무",
                "category": "직무역량",
                "provider": "외부교육기관",
                "course_type": "OFFLINE",
                "duration_hours": 32,
                "cost": 800000,
                "match_score": 78.9,
                "priority": 75,
                "skill_coverage": 33.3,
                "matched_skills": ["예산관리"],
                "recommendation_reason": "전략기획팀장 직무에 필요한 예산관리 스킬을 습득할 수 있습니다. 부족한 스킬의 33%를 커버합니다.",
                "expected_completion_time": "1개월",
                "can_enroll": True,
                "enrollment_message": "",
                "next_session": {
                    "start_date": "2024-03-10",
                    "end_date": "2024-04-10",
                    "enrollment_deadline": "2024-03-01",
                    "seats_available": 20,
                    "location": "서울 교육장"
                },
                "completion_rate": 85.2,
                "average_satisfaction": 4.4,
                "growth_impact": {
                    "level_progress": 0.1,
                    "certification_eligible": False,
                    "next_level_contribution": 0.1
                }
            }
        ],
        "roadmap": [
            {
                "month": 1,
                "courses": [
                    {
                        "course_id": "C-157",
                        "title": "조직관리와 성과창출",
                        "duration_hours": 16
                    }
                ],
                "total_hours": 16,
                "skills_covered": ["조직운영"]
            },
            {
                "month": 2,
                "courses": [
                    {
                        "course_id": "C-203",
                        "title": "전략적 사고와 비즈니스 기획",
                        "duration_hours": 24
                    }
                ],
                "total_hours": 24,
                "skills_covered": ["전략수립"]
            },
            {
                "month": 3,
                "courses": [
                    {
                        "course_id": "C-089",
                        "title": "예산편성과 재무관리 실무",
                        "duration_hours": 32
                    }
                ],
                "total_hours": 32,
                "skills_covered": ["예산관리"]
            }
        ],
        "summary": {
            "total_courses": 3,
            "total_hours": 72,
            "total_cost": 1400000,
            "skill_coverage": 1.0,
            "covered_skills": ["전략수립", "조직운영", "예산관리"],
            "uncovered_skills": [],
            "estimated_completion_months": 3,
            "priority_courses": [
                {
                    "course_id": "C-203",
                    "title": "전략적 사고와 비즈니스 기획",
                    "priority": 90
                },
                {
                    "course_id": "C-157",
                    "title": "조직관리와 성과창출",
                    "priority": 85
                }
            ]
        },
        "generated_at": datetime.now().isoformat()
    }
    
    print("\nAPI 응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # 요약 출력
    print("\n추천 요약:")
    print(f"직원: {response['employee']['name']} ({response['employee']['position']})")
    print(f"목표 직무: {response['context']['target_job']}")
    print(f"부족 스킬: {', '.join(response['context']['missing_skills'])}")
    print(f"\n총 {response['summary']['total_courses']}개 과정 추천")
    print(f"총 교육시간: {response['summary']['total_hours']}시간")
    print(f"총 비용: {response['summary']['total_cost']:,}원")
    print(f"예상 완료기간: {response['summary']['estimated_completion_months']}개월")
    
    print("\n우선순위 TOP 과정:")
    for course in response['recommendations'][:2]:
        print(f"  - [{course['course_code']}] {course['title']}")
        print(f"    매칭점수: {course['match_score']}% | 우선순위: {course['priority']}")
        print(f"    이수율: {course['completion_rate']}% | 만족도: {course['average_satisfaction']}")


def test_training_enrollment():
    """교육 수강 신청 API 테스트"""
    print("\n\n" + "=" * 70)
    print("테스트 2: POST /api/training-enrollment/")
    print("=" * 70)
    
    # 요청 데이터
    request_data = {
        "course_id": "C-203",
        "notes": "전략기획팀장 승진 준비를 위한 스킬 개발"
    }
    
    print("\n요청 데이터:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    # 성공 응답
    success_response = {
        "status": "success",
        "enrollment_id": "ENR-2024-0312",
        "message": "수강 신청이 완료되었습니다."
    }
    
    print("\n성공 응답:")
    print(json.dumps(success_response, indent=2, ensure_ascii=False))
    
    # 실패 응답 (중복 신청)
    error_response = {
        "status": "error",
        "message": "이미 신청한 교육입니다."
    }
    
    print("\n실패 응답 (중복 신청):")
    print(json.dumps(error_response, indent=2, ensure_ascii=False))


def test_no_recommendations_scenario():
    """추천 교육이 없는 시나리오"""
    print("\n\n" + "=" * 70)
    print("테스트 3: 추천 교육이 없는 경우")
    print("=" * 70)
    
    response = {
        "status": "no_recommendations",
        "message": "현재 추천할 교육이 없습니다.",
        "employee": {
            "id": "E2001",
            "name": "이부장",
            "position": "부장",
            "department": "재무팀",
            "current_level": "Lv.4"
        },
        "context": {
            "target_job": None,
            "missing_skills": []
        },
        "recommendations": [],
        "roadmap": [],
        "summary": {
            "total_courses": 0,
            "total_hours": 0,
            "total_cost": 0,
            "skill_coverage": 0,
            "covered_skills": [],
            "uncovered_skills": []
        },
        "generated_at": datetime.now().isoformat()
    }
    
    print("\nAPI 응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))


def test_training_history():
    """교육 이력 조회 테스트"""
    print("\n\n" + "=" * 70)
    print("테스트 4: GET /api/my-training-history/?status=COMPLETED")
    print("=" * 70)
    
    response = {
        "status": "success",
        "total_count": 5,
        "history": [
            {
                "enrollment_id": "ENR-2023-0892",
                "course": {
                    "id": "C-045",
                    "code": "LDR-BAS-001",
                    "title": "신임 리더 기본과정",
                    "category": "리더십"
                },
                "status": "COMPLETED",
                "status_display": "이수",
                "enrolled_date": "2023-11-01T09:00:00",
                "start_date": "2023-11-15",
                "completion_date": "2023-11-30T17:00:00",
                "attendance_rate": 95.0,
                "test_score": 88.5,
                "satisfaction_score": 5
            },
            {
                "enrollment_id": "ENR-2023-0654",
                "course": {
                    "id": "C-078",
                    "code": "COM-INT-002",
                    "title": "효과적인 커뮤니케이션",
                    "category": "공통역량"
                },
                "status": "COMPLETED",
                "status_display": "이수",
                "enrolled_date": "2023-08-01T10:00:00",
                "start_date": "2023-08-10",
                "completion_date": "2023-08-20T17:00:00",
                "attendance_rate": 100.0,
                "test_score": 92.0,
                "satisfaction_score": 4
            }
        ]
    }
    
    print("\nAPI 응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n이수 교육 요약:")
    for history in response['history']:
        print(f"  - {history['course']['title']}")
        print(f"    이수일: {history['completion_date'][:10]}")
        print(f"    출석률: {history['attendance_rate']}% | 점수: {history['test_score']}")


def test_course_detail():
    """교육과정 상세 조회 테스트"""
    print("\n\n" + "=" * 70)
    print("테스트 5: GET /api/training-course/C-203/")
    print("=" * 70)
    
    response = {
        "status": "success",
        "course": {
            "id": "C-203",
            "course_code": "STR-ADV-001",
            "title": "전략적 사고와 비즈니스 기획",
            "category": "리더십",
            "description": "조직의 전략 수립과 실행을 위한 체계적인 사고 프레임워크를 학습하고, 실제 비즈니스 사례를 통해 전략 기획 역량을 개발합니다.",
            "objectives": [
                "전략적 사고의 기본 개념과 프레임워크 이해",
                "환경 분석 및 전략 수립 방법론 습득",
                "전략 실행 계획 수립 및 모니터링 방법 학습",
                "실제 사례 분석을 통한 전략 기획 실습"
            ],
            "target_audience": "팀장 및 차/부장급 관리자, 전략기획 담당자",
            "related_skills": ["전략수립", "비즈니스분석", "의사결정", "기획력"],
            "skill_level": "ADVANCED",
            "duration_hours": 24,
            "course_type": "BLENDED",
            "provider": "한국생산성본부",
            "cost": 600000,
            "is_mandatory": False,
            "certification_eligible": True,
            "statistics": {
                "total_enrollments": 156,
                "completion_rate": 87.5,
                "average_satisfaction": 4.5
            }
        }
    }
    
    print("\nAPI 응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))


def test_frontend_integration():
    """프론트엔드 통합 예시"""
    print("\n\n" + "=" * 70)
    print("테스트 6: 프론트엔드 통합 JavaScript 예시")
    print("=" * 70)
    
    js_code = """
// 1. 교육 추천 조회
async function getTrainingRecommendations() {
    try {
        const response = await fetch('/api/my-growth-training-recommendations/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch recommendations');
        }
        
        const data = await response.json();
        displayRecommendations(data);
        
    } catch (error) {
        console.error('Error:', error);
        showErrorMessage('교육 추천을 불러올 수 없습니다.');
    }
}

// 2. 교육 신청
async function enrollInCourse(courseId) {
    try {
        const response = await fetch('/api/training-enrollment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                course_id: courseId,
                notes: '성장 목표 달성을 위한 교육 신청'
            }),
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showSuccessMessage('수강 신청이 완료되었습니다.');
            refreshRecommendations();
        } else {
            showErrorMessage(data.message);
        }
        
    } catch (error) {
        console.error('Error:', error);
        showErrorMessage('수강 신청 중 오류가 발생했습니다.');
    }
}

// 3. 추천 교육 표시
function displayRecommendations(data) {
    const container = document.getElementById('training-recommendations');
    container.innerHTML = '';
    
    // 컨텍스트 정보 표시
    document.getElementById('targetJob').textContent = data.context.target_job || '미정';
    document.getElementById('missingSkills').textContent = 
        data.context.missing_skills.join(', ') || '없음';
    
    // 추천 교육 카드 생성
    data.recommendations.forEach(course => {
        const card = createCourseCard(course);
        container.appendChild(card);
    });
    
    // 로드맵 차트 그리기
    if (data.roadmap.length > 0) {
        drawRoadmapChart(data.roadmap);
    }
}

// 4. 교육 카드 생성
function createCourseCard(course) {
    const card = document.createElement('div');
    card.className = 'course-card';
    
    const priorityBadge = course.priority >= 80 
        ? '<span class="badge badge-danger">우선순위 높음</span>'
        : '<span class="badge badge-secondary">일반</span>';
    
    card.innerHTML = `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <h5 class="card-title">${course.title}</h5>
                    ${priorityBadge}
                </div>
                <p class="text-muted">${course.course_code} | ${course.provider}</p>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <small class="text-muted">매칭점수</small>
                        <div class="progress">
                            <div class="progress-bar" style="width: ${course.match_score}%">
                                ${course.match_score}%
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <small class="text-muted">이수율</small>
                        <div class="progress">
                            <div class="progress-bar bg-success" style="width: ${course.completion_rate}%">
                                ${course.completion_rate}%
                            </div>
                        </div>
                    </div>
                </div>
                
                <p class="card-text">${course.recommendation_reason}</p>
                
                <div class="course-meta">
                    <span class="badge badge-light">${course.duration_hours}시간</span>
                    <span class="badge badge-light">${course.course_type}</span>
                    <span class="badge badge-light">₩${course.cost.toLocaleString()}</span>
                </div>
                
                <div class="mt-3">
                    ${course.can_enroll 
                        ? `<button class="btn btn-primary" onclick="enrollInCourse('${course.course_id}')">
                            수강 신청
                           </button>`
                        : `<button class="btn btn-secondary" disabled>
                            ${course.enrollment_message}
                           </button>`
                    }
                    <button class="btn btn-outline-secondary" 
                            onclick="viewCourseDetail('${course.course_id}')">
                        상세보기
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return card;
}
"""
    
    print("\n프론트엔드 JavaScript 예시:")
    print(js_code)
    
    html_template = """
<!-- 교육 추천 페이지 -->
<div class="container mt-4">
    <h2>나의 성장 교육 추천</h2>
    
    <!-- 추천 컨텍스트 -->
    <div class="card mb-4">
        <div class="card-body">
            <h5>추천 기준</h5>
            <div class="row">
                <div class="col-md-6">
                    <strong>목표 직무:</strong> <span id="targetJob"></span>
                </div>
                <div class="col-md-6">
                    <strong>개발 필요 스킬:</strong> <span id="missingSkills"></span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 추천 교육 목록 -->
    <h4>추천 교육과정</h4>
    <div id="training-recommendations">
        <!-- 동적으로 생성됨 -->
    </div>
    
    <!-- 학습 로드맵 -->
    <div class="mt-4">
        <h4>학습 로드맵</h4>
        <canvas id="roadmapChart"></canvas>
    </div>
</div>
"""
    
    print("\nHTML 템플릿:")
    print(html_template)


if __name__ == "__main__":
    print("=" * 70)
    print("교육 추천 API 테스트")
    print("=" * 70)
    
    # 모든 테스트 실행
    test_growth_training_recommendations()
    test_training_enrollment()
    test_no_recommendations_scenario()
    test_training_history()
    test_course_detail()
    test_frontend_integration()
    
    print("\n" + "=" * 70)
    print("모든 테스트 완료!")
    print("=" * 70)