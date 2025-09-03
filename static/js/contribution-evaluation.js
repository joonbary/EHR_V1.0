/**
 * Contribution Evaluation JavaScript Module
 * Handles AI feedback generation and form interactions
 * Version: 1.0
 * Date: 2025-01-21
 */

class ContributionEvaluation {
    constructor() {
        this.evaluationId = null;
        this.csrfToken = null;
        this.init();
    }

    /**
     * Initialize the evaluation module
     */
    init() {
        // Get CSRF token
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        // Get evaluation ID from data attribute or global variable
        const evaluationElement = document.getElementById('evaluation-container');
        if (evaluationElement) {
            this.evaluationId = evaluationElement.dataset.evaluationId;
        }

        // Bind event listeners
        this.bindEvents();
        
        // Initialize tooltips if available
        this.initTooltips();
        
        console.log('✅ Contribution Evaluation Module Initialized');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // AI Feedback Generation Button
        const generateBtn = document.getElementById('generate-ai-feedback');
        if (generateBtn) {
            generateBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.generateAIFeedback();
            });
        }

        // Score calculation on input change
        document.querySelectorAll('select[name^="task_"][name$="_scope"], select[name^="task_"][name$="_method"]')
            .forEach(select => {
                select.addEventListener('change', () => this.calculateScore(select));
            });

        // Weight validation
        document.querySelectorAll('input[name^="task_"][name$="_weight"]').forEach(input => {
            input.addEventListener('change', () => this.validateWeights());
        });

        // Form submission validation
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => this.validateForm(e));
        }
    }

    /**
     * Generate AI feedback
     */
    async generateAIFeedback() {
        const button = document.getElementById('generate-ai-feedback');
        if (!button) return;
        
        const originalText = button.innerHTML;
        
        // Show loading state
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>생성 중...';
        
        // Prepare evaluation data
        const evaluationData = {
            type: 'contribution',
            evaluation_id: this.evaluationId,
            employee_id: document.getElementById('evaluation-container')?.dataset.employeeId,
            tasks: this.collectTaskData()
        };
        
        try {
            const response = await fetch('/evaluations/api/generate-feedback/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify(evaluationData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Display feedback
            this.displayFeedback(data.feedback);
            
            // Offer to add to comments field
            this.offerToAddToComments(data.feedback);
            
        } catch (error) {
            console.error('Error generating AI feedback:', error);
            this.displayDefaultFeedback();
        } finally {
            // Restore button state
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }

    /**
     * Collect task data from form
     */
    collectTaskData() {
        const tasks = [];
        document.querySelectorAll('.task-item').forEach((item, index) => {
            const taskId = item.dataset.taskId;
            tasks.push({
                id: taskId,
                title: item.querySelector(`input[name="task_${taskId}_title"]`)?.value || '',
                weight: parseFloat(item.querySelector(`input[name="task_${taskId}_weight"]`)?.value) || 0,
                scope: item.querySelector(`select[name="task_${taskId}_scope"]`)?.value || '',
                method: item.querySelector(`select[name="task_${taskId}_method"]`)?.value || '',
                description: item.querySelector(`textarea[name="task_${taskId}_description"]`)?.value || ''
            });
        });
        return tasks;
    }

    /**
     * Display AI feedback
     */
    displayFeedback(feedback) {
        const container = document.getElementById('ai-feedback-container');
        const content = document.getElementById('ai-feedback-content');
        
        if (container && content) {
            container.style.display = 'block';
            content.textContent = feedback;
            
            // Smooth scroll to feedback
            container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            // Add animation
            container.classList.add('fade-in');
        }
    }

    /**
     * Display default feedback when API fails
     */
    displayDefaultFeedback() {
        const defaultFeedback = `[AI 피드백 생성 실패 - 수동 작성 필요]

평가 항목별 기여도를 고려하여 다음 사항을 평가해 주세요:
- 업무 수행 능력과 성과에 대한 전반적인 평가
- Task 달성률과 기여 방법 분석
- 향후 개선 방향과 발전 가능성

※ AI 서비스가 일시적으로 사용 불가능합니다.
수동으로 피드백을 작성해 주시기 바랍니다.`;

        this.displayFeedback(defaultFeedback);
        
        // Show error toast if available
        if (window.Toast) {
            window.Toast.error('AI 피드백 생성에 실패했습니다. 수동으로 작성해 주세요.');
        }
    }

    /**
     * Offer to add feedback to comments field
     */
    offerToAddToComments(feedback) {
        const commentsField = document.querySelector('[name="comments"]');
        if (commentsField && !commentsField.value) {
            if (confirm('AI 피드백을 평가자 의견에 추가하시겠습니까?')) {
                commentsField.value = feedback;
                commentsField.focus();
                
                // Highlight the field briefly
                commentsField.style.borderColor = 'var(--primary-color)';
                setTimeout(() => {
                    commentsField.style.borderColor = '';
                }, 2000);
            }
        }
    }

    /**
     * Calculate score based on scope and method
     */
    calculateScore(changedElement) {
        const taskItem = changedElement.closest('.task-item');
        if (!taskItem) return;
        
        const taskId = taskItem.dataset.taskId;
        const scope = taskItem.querySelector(`select[name="task_${taskId}_scope"]`)?.value;
        const method = taskItem.querySelector(`select[name="task_${taskId}_method"]`)?.value;
        
        // Score matrix
        const scoreMatrix = {
            'strategic': { 'lead': 4.0, 'execute': 3.0, 'support': 2.0 },
            'collaborative': { 'lead': 3.0, 'execute': 2.0, 'support': 1.0 },
            'individual': { 'lead': 2.0, 'execute': 1.0, 'support': 1.0 }
        };
        
        const score = scoreMatrix[scope]?.[method] || 0;
        
        // Update score display
        const scoreDisplay = taskItem.querySelector('.task-score');
        if (scoreDisplay) {
            scoreDisplay.textContent = score.toFixed(1);
            scoreDisplay.className = `task-score score-badge score-${Math.floor(score)}`;
        }
        
        // Update total score
        this.updateTotalScore();
    }

    /**
     * Update total score calculation
     */
    updateTotalScore() {
        let totalScore = 0;
        let totalWeight = 0;
        
        document.querySelectorAll('.task-item').forEach(item => {
            const taskId = item.dataset.taskId;
            const weight = parseFloat(item.querySelector(`input[name="task_${taskId}_weight"]`)?.value) || 0;
            const scoreElement = item.querySelector('.task-score');
            const score = parseFloat(scoreElement?.textContent) || 0;
            
            totalScore += score * (weight / 100);
            totalWeight += weight;
        });
        
        // Display total score
        const totalScoreElement = document.getElementById('total-score');
        if (totalScoreElement) {
            totalScoreElement.textContent = totalScore.toFixed(1);
            
            // Update progress bar
            const progressBar = document.querySelector('.score-progress-bar');
            if (progressBar) {
                progressBar.style.width = `${(totalScore / 4) * 100}%`;
            }
        }
        
        // Display weight validation
        const weightStatus = document.getElementById('weight-status');
        if (weightStatus) {
            if (Math.abs(totalWeight - 100) < 0.01) {
                weightStatus.innerHTML = '<i class="fas fa-check-circle text-success"></i> 가중치 합계: 100%';
            } else {
                weightStatus.innerHTML = `<i class="fas fa-exclamation-circle text-warning"></i> 가중치 합계: ${totalWeight}% (100%가 되어야 합니다)`;
            }
        }
    }

    /**
     * Validate weights sum to 100%
     */
    validateWeights() {
        let totalWeight = 0;
        
        document.querySelectorAll('input[name$="_weight"]').forEach(input => {
            totalWeight += parseFloat(input.value) || 0;
        });
        
        const isValid = Math.abs(totalWeight - 100) < 0.01;
        
        // Update UI based on validation
        document.querySelectorAll('input[name$="_weight"]').forEach(input => {
            if (isValid) {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            } else {
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
            }
        });
        
        return isValid;
    }

    /**
     * Validate form before submission
     */
    validateForm(event) {
        const isWeightValid = this.validateWeights();
        
        if (!isWeightValid) {
            event.preventDefault();
            alert('가중치 합계가 100%가 되도록 조정해 주세요.');
            return false;
        }
        
        // Check required fields
        const requiredFields = document.querySelectorAll('[required]');
        let hasEmptyFields = false;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                hasEmptyFields = true;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        if (hasEmptyFields) {
            event.preventDefault();
            alert('필수 항목을 모두 입력해 주세요.');
            return false;
        }
        
        return true;
    }

    /**
     * Initialize tooltips
     */
    initTooltips() {
        // Bootstrap tooltips
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.contributionEvaluation = new ContributionEvaluation();
});