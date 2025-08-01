/**
 * 기여도 평가 Scoring Chart 로직
 */

// Scoring Chart 데이터
const CONTRIBUTION_SCORING_CHART = {
    'strategic': {
        'directing': 4,
        'leading': 4,
        'individual': 3,
        'support': 2
    },
    'mutual': {
        'directing': 3,
        'leading': 3,
        'individual': 3,
        'support': 2
    },
    'independent': {
        'directing': 2,
        'leading': 3,
        'individual': 2,
        'support': 1
    },
    'dependent': {
        'directing': 2,
        'leading': 2,
        'individual': 1,
        'support': 1
    }
};

// 달성률에 따른 점수 조정
function adjustScoreByAchievement(baseScore, achievementRate) {
    if (achievementRate >= 100) {
        return baseScore;
    } else if (achievementRate >= 90) {
        return baseScore - 0.5;
    } else if (achievementRate >= 80) {
        return baseScore - 1.0;
    } else if (achievementRate >= 70) {
        return baseScore - 1.5;
    } else {
        return Math.max(1.0, baseScore - 2.0);
    }
}

// Task 점수 실시간 업데이트
function updateTaskScore(taskId) {
    const methodSelect = document.querySelector(`select[name="task_${taskId}_method"]`);
    const scopeSelect = document.querySelector(`select[name="task_${taskId}_scope"]`);
    const achievementSpan = document.getElementById(`achievement_${taskId}`);
    
    if (!methodSelect || !scopeSelect) return;
    
    const method = methodSelect.value;
    const scope = scopeSelect.value;
    const achievementText = achievementSpan.textContent;
    const achievementRate = parseFloat(achievementText) || 0;
    
    // Scoring Chart에서 기본 점수 가져오기
    let baseScore = 2.0; // 기본값
    if (CONTRIBUTION_SCORING_CHART[scope] && CONTRIBUTION_SCORING_CHART[scope][method]) {
        baseScore = CONTRIBUTION_SCORING_CHART[scope][method];
    }
    
    // 달성률에 따른 점수 조정
    const finalScore = adjustScoreByAchievement(baseScore, achievementRate);
    
    // 점수 표시 업데이트
    const scoreSpan = document.getElementById(`score_${taskId}`);
    if (scoreSpan) {
        scoreSpan.textContent = finalScore.toFixed(1) + '점';
        
        // 점수에 따른 색상 변경
        if (finalScore >= 3.5) {
            scoreSpan.className = 'text-lg font-semibold text-green-600';
        } else if (finalScore >= 2.5) {
            scoreSpan.className = 'text-lg font-semibold text-blue-600';
        } else if (finalScore >= 1.5) {
            scoreSpan.className = 'text-lg font-semibold text-yellow-600';
        } else {
            scoreSpan.className = 'text-lg font-semibold text-red-600';
        }
    }
    
    // 종합 점수 업데이트
    updateTotalScore();
}

// 달성률 계산 및 점수 업데이트
function calculateAchievement(taskId) {
    const targetInput = document.querySelector(`input[name="task_${taskId}_target"]`);
    const actualInput = document.querySelector(`input[name="task_${taskId}_actual"]`);
    
    const target = parseFloat(targetInput.value) || 0;
    const actual = parseFloat(actualInput.value) || 0;
    
    if (target > 0) {
        const achievement = Math.round((actual / target) * 100);
        const achievementSpan = document.getElementById(`achievement_${taskId}`);
        achievementSpan.textContent = achievement + '%';
        
        // 달성률에 따른 색상 변경
        if (achievement >= 100) {
            achievementSpan.className = 'text-lg font-semibold text-green-600';
        } else if (achievement >= 80) {
            achievementSpan.className = 'text-lg font-semibold text-blue-600';
        } else if (achievement >= 60) {
            achievementSpan.className = 'text-lg font-semibold text-yellow-600';
        } else {
            achievementSpan.className = 'text-lg font-semibold text-red-600';
        }
        
        // 점수 재계산
        updateTaskScore(taskId);
    }
}

// 종합 점수 계산
function updateTotalScore() {
    const taskCards = document.querySelectorAll('.task-card');
    let totalWeight = 0;
    let weightedScore = 0;
    
    taskCards.forEach((card, index) => {
        const weightInput = card.querySelector(`input[name*="_weight"]`);
        const scoreSpan = card.querySelector(`span[id*="score_"]`);
        
        if (weightInput && scoreSpan) {
            const weight = parseFloat(weightInput.value) || 0;
            const score = parseFloat(scoreSpan.textContent) || 0;
            
            totalWeight += weight;
            weightedScore += (weight * score);
        }
    });
    
    // 전체 진행률 표시 업데이트
    const totalWeightDisplay = document.querySelector('.text-blue-600');
    if (totalWeightDisplay && totalWeightDisplay.previousElementSibling.textContent === '총 가중치') {
        totalWeightDisplay.textContent = totalWeight + '%';
    }
    
    // 종합 점수 계산
    if (totalWeight > 0) {
        const totalScore = (weightedScore / totalWeight).toFixed(1);
        // TODO: 종합 점수 표시 UI 추가
    }
}

// Scoring Chart 시각적 강조
function highlightScoringChart(scope, method) {
    // 모든 셀의 강조 제거
    document.querySelectorAll('.score-cell').forEach(cell => {
        cell.classList.remove('selected', 'highlighted');
    });
    
    // 선택된 셀 강조
    const selectedCell = document.querySelector(
        `.score-cell[data-scope="${scope}"][data-method="${method}"]`
    );
    
    if (selectedCell) {
        selectedCell.classList.add('selected');
        
        // 애니메이션 효과
        selectedCell.style.transform = 'scale(1.1)';
        setTimeout(() => {
            selectedCell.style.transform = 'scale(1)';
        }, 200);
    }
}

// Task 추가 기능
function addTask() {
    // TODO: 실제 구현시 모달 또는 동적 폼 추가
    const taskContainer = document.querySelector('.space-y-4');
    const newTaskHtml = createNewTaskHtml();
    
    // 임시 구현
    alert('Task 추가 기능은 추가 개발이 필요합니다.');
}

// 평가 데이터 검증
function validateEvaluation() {
    const taskCards = document.querySelectorAll('.task-card');
    let totalWeight = 0;
    let hasError = false;
    
    taskCards.forEach(card => {
        const weightInput = card.querySelector(`input[name*="_weight"]`);
        const weight = parseFloat(weightInput.value) || 0;
        totalWeight += weight;
    });
    
    // 가중치 합계 검증
    if (Math.abs(totalWeight - 100) > 0.01) {
        alert(`총 가중치가 100%가 아닙니다. 현재: ${totalWeight}%`);
        hasError = true;
    }
    
    return !hasError;
}

// 평가 저장
function saveEvaluation() {
    if (validateEvaluation()) {
        document.getElementById('evaluationForm').submit();
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 모든 Task의 점수 계산
    const taskCards = document.querySelectorAll('.task-card');
    taskCards.forEach((card, index) => {
        const taskId = index + 1; // 실제로는 data attribute에서 가져와야 함
        updateTaskScore(taskId);
    });
    
    // Lucide 아이콘 초기화
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});