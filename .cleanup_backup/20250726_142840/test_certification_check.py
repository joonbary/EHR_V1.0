"""
성장레벨 인증 체크 API 테스트
다양한 시나리오에 대한 인증 요건 충족 여부 테스트
"""

import json
from datetime import datetime, timedelta


def test_certification_check_api():
    """인증 체크 API 기본 테스트"""
    print("=" * 70)
    print("테스트 1: POST /api/growth-level-certification-check/")
    print("=" * 70)
    
    # 요청 데이터
    request_data = {
        "employee_id": "E1001",
        "target_level": "Lv.3",
        "target_job_id": "J-TM-01"
    }
    
    print("\n요청 데이터:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    # 응답 예시 - 부분 충족
    response = {
        "status": "success",
        "certification_result": "부분충족",
        "missing_courses": ["조직운영실무"],
        "missing_skills": ["전략수립"],
        "eval_ok": True,
        "current_level": "Lv.2",
        "required_level": "Lv.3",
        "expected_certification_date": "2025-10-01",
        "checks": {
            "evaluation": True,
            "training": False,
            "skills": False,
            "experience": True
        },
        "progress": {
            "evaluation": 100.0,
            "training": 66.7,
            "skills": 66.7,
            "experience": 100.0,
            "overall": 82.5
        },
        "evaluation_details": {
            "current_grade": "A",
            "required_grade": "B+",
            "message": "평가 요건을 충족합니다"
        },
        "recommendations": [
            "필수 교육 이수 필요: 조직운영실무",
            "스킬 개발 필요: 전략수립"
        ]
    }
    
    print("\nAPI 응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # 결과 요약
    print("\n결과 요약:")
    print(f"인증 결과: {response['certification_result']}")
    print(f"현재 레벨: {response['current_level']} → 목표 레벨: {response['required_level']}")
    print(f"전체 진행률: {response['progress']['overall']}%")
    print(f"예상 인증일: {response['expected_certification_date']}")


def test_fully_qualified_scenario():
    """완전 충족 시나리오"""
    print("\n\n" + "=" * 70)
    print("테스트 2: 모든 요건 충족 케이스")
    print("=" * 70)
    
    request_data = {
        "employee_id": "E2001",
        "target_level": "Lv.4",
        "target_job_id": "J-DIR-01"
    }
    
    response = {
        "status": "success",
        "certification_result": "충족",
        "missing_courses": [],
        "missing_skills": [],
        "eval_ok": True,
        "current_level": "Lv.3",
        "required_level": "Lv.4",
        "expected_certification_date": None,
        "checks": {
            "evaluation": True,
            "training": True,
            "skills": True,
            "experience": True
        },
        "progress": {
            "evaluation": 100.0,
            "training": 100.0,
            "skills": 100.0,
            "experience": 100.0,
            "overall": 100.0
        },
        "recommendations": []
    }
    
    print("\n요청:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    print("\n응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n[PASS] 모든 인증 요건을 충족하여 즉시 인증 신청이 가능합니다!")


def test_not_qualified_scenario():
    """미충족 시나리오"""
    print("\n\n" + "=" * 70)
    print("테스트 3: 대부분 요건 미충족 케이스")
    print("=" * 70)
    
    request_data = {
        "employee_id": "E3001",
        "target_level": "Lv.5",
        "target_job_id": None
    }
    
    response = {
        "status": "success",
        "certification_result": "미충족",
        "missing_courses": ["임원리더십", "경영전략", "글로벌비즈니스"],
        "missing_skills": ["경영전략", "의사결정", "조직운영"],
        "eval_ok": False,
        "current_level": "Lv.3",
        "required_level": "Lv.5",
        "expected_certification_date": "2027-01-15",
        "checks": {
            "evaluation": False,
            "training": False,
            "skills": False,
            "experience": False
        },
        "progress": {
            "evaluation": 60.0,
            "training": 0.0,
            "skills": 25.0,
            "experience": 50.0,
            "overall": 34.5
        },
        "evaluation_details": {
            "current_grade": "B+",
            "required_grade": "A+",
            "message": "3회 연속 A+ 이상 필요"
        },
        "recommendations": [
            "다음 평가에서 A+ 이상 획득 필요",
            "필수 교육 이수 필요: 임원리더십, 경영전략, 글로벌비즈니스 등",
            "스킬 개발 필요: 경영전략, 의사결정, 조직운영",
            "현 레벨에서 2.0년 더 경력 필요"
        ]
    }
    
    print("\n요청:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    print("\n응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n[FAIL] 많은 요건이 부족하여 장기적인 준비가 필요합니다.")


def test_my_growth_level_status():
    """내 성장레벨 상태 조회"""
    print("\n\n" + "=" * 70)
    print("테스트 4: GET /api/my-growth-level-status/")
    print("=" * 70)
    
    response = {
        "status": "success",
        "employee": {
            "id": "E1001",
            "name": "김과장",
            "position": "과장",
            "department": "전략기획팀"
        },
        "growth_level": {
            "current": "Lv.2",
            "target": "Lv.3",
            "certification_status": "부분충족"
        },
        "requirements": {
            "evaluation": True,
            "training": False,
            "skills": False,
            "experience": True
        },
        "missing": {
            "courses": ["조직운영실무"],
            "skills": ["전략수립"]
        },
        "progress": {
            "evaluation": 100.0,
            "training": 66.7,
            "skills": 66.7,
            "experience": 100.0,
            "overall": 82.5
        },
        "expected_certification_date": "2025-10-01",
        "recommendations": [
            "필수 교육 이수 필요: 조직운영실무",
            "스킬 개발 필요: 전략수립"
        ],
        "certification_history": [
            {
                "id": "CERT-001",
                "level": "Lv.2",
                "status": "CERTIFIED",
                "status_display": "인증완료",
                "applied_date": "2023-03-15T10:00:00",
                "certified_date": "2023-03-20T14:00:00",
                "checks": {
                    "evaluation": True,
                    "training": True,
                    "skills": True,
                    "experience": True
                }
            }
        ]
    }
    
    print("\nAPI 응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n내 성장레벨 요약:")
    print(f"현재: {response['growth_level']['current']} → 목표: {response['growth_level']['target']}")
    print(f"상태: {response['growth_level']['certification_status']}")
    print(f"진행률: {response['progress']['overall']}%")


def test_progress_api():
    """진행률 조회 API 테스트"""
    print("\n\n" + "=" * 70)
    print("테스트 5: GET /api/growth-level-progress/?target_level=Lv.4")
    print("=" * 70)
    
    response = {
        "status": "success",
        "employee": {
            "id": "E1001",
            "name": "김과장",
            "current_level": "Lv.3"
        },
        "target_level": "Lv.4",
        "progress": {
            "evaluation": 75.0,
            "training": 50.0,
            "skills": 60.0,
            "experience": 80.0,
            "overall": 65.3
        },
        "can_apply": False
    }
    
    print("\nAPI 응답:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # 진행률 시각화
    print("\n진행률 상세:")
    for key, value in response['progress'].items():
        if key != 'overall':
            bar = "█" * int(value / 10) + "░" * (10 - int(value / 10))
            print(f"{key:12} [{bar}] {value}%")
    
    print(f"\n종합 진행률: {response['progress']['overall']}%")
    print(f"인증 신청 가능: {'예' if response['can_apply'] else '아니오'}")


def test_certification_apply():
    """인증 신청 API 테스트"""
    print("\n\n" + "=" * 70)
    print("테스트 6: POST /api/growth-level-certification-apply/")
    print("=" * 70)
    
    # 성공 케이스
    request_data = {
        "target_level": "Lv.3",
        "notes": "모든 요건을 충족하여 인증 신청합니다."
    }
    
    success_response = {
        "status": "success",
        "certification_id": "CERT-2024-001",
        "message": "성장레벨 인증이 신청되었습니다."
    }
    
    print("\n[SUCCESS] 성공 케이스:")
    print("요청:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    print("\n응답:")
    print(json.dumps(success_response, indent=2, ensure_ascii=False))
    
    # 실패 케이스
    error_response = {
        "status": "error",
        "message": "인증 요건을 충족하지 못했습니다.",
        "missing_requirements": {
            "missing_courses": ["조직운영실무"],
            "missing_skills": ["전략수립"],
            "eval_ok": True,
            "current_level": "Lv.2",
            "required_level": "Lv.3"
        }
    }
    
    print("\n\n[ERROR] 실패 케이스:")
    print("응답:")
    print(json.dumps(error_response, indent=2, ensure_ascii=False))


def test_frontend_integration():
    """프론트엔드 통합 예시"""
    print("\n\n" + "=" * 70)
    print("테스트 7: 프론트엔드 JavaScript 통합 예시")
    print("=" * 70)
    
    js_code = """
// 1. 성장레벨 인증 체크
async function checkCertificationEligibility(targetLevel, targetJobId) {
    try {
        const response = await fetch('/api/growth-level-certification-check/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                employee_id: currentEmployeeId,
                target_level: targetLevel,
                target_job_id: targetJobId
            }),
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayCertificationResult(data);
        }
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// 2. 인증 결과 표시
function displayCertificationResult(data) {
    const resultContainer = document.getElementById('certificationResult');
    
    // 인증 상태 배지
    let statusBadge = '';
    if (data.certification_result === '충족') {
        statusBadge = '<span class="badge badge-success">인증 가능</span>';
    } else if (data.certification_result === '부분충족') {
        statusBadge = '<span class="badge badge-warning">부분 충족</span>';
    } else {
        statusBadge = '<span class="badge badge-danger">미충족</span>';
    }
    
    // 진행률 차트
    const progressChart = createProgressChart(data.progress);
    
    // 부족 요건 표시
    let missingRequirements = '';
    if (data.missing_courses.length > 0) {
        missingRequirements += `
            <div class="alert alert-warning">
                <strong>필수 교육 미이수:</strong> ${data.missing_courses.join(', ')}
            </div>
        `;
    }
    
    if (data.missing_skills.length > 0) {
        missingRequirements += `
            <div class="alert alert-info">
                <strong>개발 필요 스킬:</strong> ${data.missing_skills.join(', ')}
            </div>
        `;
    }
    
    resultContainer.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5>성장레벨 인증 체크 결과 ${statusBadge}</h5>
                <p>현재 레벨: ${data.current_level} → 목표 레벨: ${data.required_level}</p>
                
                <div class="progress-section">
                    ${progressChart}
                    <p class="text-center mt-2">
                        전체 진행률: ${data.progress.overall}%
                    </p>
                </div>
                
                ${missingRequirements}
                
                ${data.expected_certification_date ? `
                    <p class="text-muted">
                        예상 인증 가능일: ${data.expected_certification_date}
                    </p>
                ` : ''}
                
                ${data.certification_result === '충족' ? `
                    <button class="btn btn-primary" onclick="applyCertification('${data.required_level}')">
                        인증 신청하기
                    </button>
                ` : ''}
            </div>
        </div>
    `;
}

// 3. 진행률 차트 생성
function createProgressChart(progress) {
    return `
        <div class="progress-bars">
            <div class="mb-2">
                <label>평가</label>
                <div class="progress">
                    <div class="progress-bar" style="width: ${progress.evaluation}%">
                        ${progress.evaluation}%
                    </div>
                </div>
            </div>
            <div class="mb-2">
                <label>교육</label>
                <div class="progress">
                    <div class="progress-bar" style="width: ${progress.training}%">
                        ${progress.training}%
                    </div>
                </div>
            </div>
            <div class="mb-2">
                <label>스킬</label>
                <div class="progress">
                    <div class="progress-bar" style="width: ${progress.skills}%">
                        ${progress.skills}%
                    </div>
                </div>
            </div>
            <div class="mb-2">
                <label>경력</label>
                <div class="progress">
                    <div class="progress-bar" style="width: ${progress.experience}%">
                        ${progress.experience}%
                    </div>
                </div>
            </div>
        </div>
    `;
}
"""
    
    print("\n프론트엔드 JavaScript 예시:")
    print(js_code)


if __name__ == "__main__":
    print("=" * 70)
    print("성장레벨 인증 체크 API 테스트")
    print("=" * 70)
    
    # 모든 테스트 실행
    test_certification_check_api()
    test_fully_qualified_scenario()
    test_not_qualified_scenario()
    test_my_growth_level_status()
    test_progress_api()
    test_certification_apply()
    test_frontend_integration()
    
    print("\n" + "=" * 70)
    print("모든 테스트 완료!")
    print("=" * 70)