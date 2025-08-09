/* ==============================================
   THEME SYSTEM JAVASCRIPT
   ============================================== */

class ThemeManager {
    constructor() {
        this.themes = {
            revolutionary: {
                name: '🤖 Revolutionary',
                description: '사이버펑크 네온 테마'
            },
            professional: {
                name: '💼 Professional', 
                description: '깔끔한 비즈니스 테마'
            },
            nature: {
                name: '🌿 Nature',
                description: '자연친화적 그린 테마'
            },
            corporate: {
                name: '🏢 Corporate',
                description: '고급스러운 기업 테마'
            }
        };
        
        this.currentTheme = this.getSavedTheme() || 'revolutionary';
        this.init();
    }

    init() {
        this.createThemeToggle();
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
    }

    createThemeToggle() {
        // 기존 테마 토글이 있다면 제거
        const existingToggle = document.querySelector('.theme-toggle');
        if (existingToggle) {
            existingToggle.remove();
        }

        const themeToggle = document.createElement('div');
        themeToggle.className = 'theme-toggle';
        themeToggle.innerHTML = this.generateThemeButtons();
        
        document.body.appendChild(themeToggle);
    }

    generateThemeButtons() {
        return Object.keys(this.themes).map(themeKey => {
            const theme = this.themes[themeKey];
            return `
                <button 
                    class="theme-toggle-btn ${themeKey === this.currentTheme ? 'active' : ''}" 
                    data-theme="${themeKey}"
                    title="${theme.description}"
                >
                    ${theme.name.split(' ')[0]}
                </button>
            `;
        }).join('');
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('theme-toggle-btn')) {
                const selectedTheme = e.target.dataset.theme;
                this.switchTheme(selectedTheme);
            }
        });
    }

    switchTheme(themeName) {
        if (this.themes[themeName] && themeName !== this.currentTheme) {
            this.currentTheme = themeName;
            this.applyTheme(themeName);
            this.saveTheme(themeName);
            this.updateActiveButton(themeName);
            this.animateThemeChange();
        }
    }

    applyTheme(themeName) {
        document.documentElement.setAttribute('data-theme', themeName);
        
        // 테마별 특별한 처리
        switch(themeName) {
            case 'professional':
                this.applyProfessionalTheme();
                break;
            case 'nature':
                this.applyNatureTheme();
                break;
            case 'corporate':
                this.applyCorporateTheme();
                break;
            case 'revolutionary':
            default:
                this.applyRevolutionaryTheme();
                break;
        }
    }

    applyRevolutionaryTheme() {
        // 기존 Revolutionary 테마 유지
        document.body.style.background = 'linear-gradient(135deg, #0a0f1b 0%, #1a1f2e 100%)';
        this.updateMetaTheme('#00d4ff');
    }

    applyProfessionalTheme() {
        document.body.style.background = 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)';
        this.updateMetaTheme('#2563eb');
        
        // Professional 테마 전용 스타일 조정
        this.updateChatTheme('professional');
    }

    applyNatureTheme() {
        document.body.style.background = 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)';
        this.updateMetaTheme('#059669');
        
        // Nature 테마 전용 스타일 조정
        this.updateChatTheme('nature');
    }

    applyCorporateTheme() {
        document.body.style.background = 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)';
        this.updateMetaTheme('#1e40af');
        
        // Corporate 테마 전용 스타일 조정
        this.updateChatTheme('corporate');
    }

    updateChatTheme(themeName) {
        // 채팅 관련 특별한 테마 업데이트
        const chatHeader = document.querySelector('.chat-header h2');
        if (chatHeader) {
            switch(themeName) {
                case 'professional':
                    chatHeader.textContent = '💼 Professional HR Assistant';
                    break;
                case 'nature':
                    chatHeader.textContent = '🌿 Eco-Friendly HR Assistant';
                    break;
                case 'corporate':
                    chatHeader.textContent = '🏢 Corporate AI Assistant';
                    break;
                case 'revolutionary':
                default:
                    chatHeader.textContent = '🤖 HR AI 어시스턴트';
                    break;
            }
        }

        // 추천 질문도 테마에 맞게 업데이트
        this.updateSuggestedQuestions(themeName);
    }

    updateSuggestedQuestions(themeName) {
        const suggestions = document.querySelectorAll('.suggestion-chip');
        if (suggestions.length === 0) return;

        const themeQuestions = {
            professional: [
                '📊 성과 관리 시스템 안내',
                '📋 업무 효율성 개선',
                '💼 전문성 개발 프로그램',
                '🎯 목표 설정 가이드'
            ],
            nature: [
                '🌱 친환경 근무 환경',
                '🍃 워라밸 개선 방안', 
                '🌿 웰빙 프로그램',
                '🌳 지속가능한 성장'
            ],
            corporate: [
                '🏢 기업 정책 안내',
                '💎 리더십 개발',
                '📈 전략적 인사관리',
                '🎖️ 성과 인정 시스템'
            ],
            revolutionary: [
                '🎯 AI 성과평가 시스템',
                '💼 스마트 워크 정책', 
                '🚀 개인화 학습 추천',
                '⚡ 팀 시너지 분석'
            ]
        };

        const questions = themeQuestions[themeName] || themeQuestions.revolutionary;
        suggestions.forEach((chip, index) => {
            if (questions[index]) {
                chip.textContent = questions[index];
            }
        });
    }

    updateActiveButton(themeName) {
        document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.theme === themeName) {
                btn.classList.add('active');
            }
        });
    }

    updateMetaTheme(color) {
        let metaTheme = document.querySelector('meta[name="theme-color"]');
        if (!metaTheme) {
            metaTheme = document.createElement('meta');
            metaTheme.setAttribute('name', 'theme-color');
            document.head.appendChild(metaTheme);
        }
        metaTheme.setAttribute('content', color);
    }

    animateThemeChange() {
        // 테마 변경 애니메이션
        document.body.style.animation = 'themeTransition 0.5s ease-in-out';
        
        setTimeout(() => {
            document.body.style.animation = '';
        }, 500);
    }

    saveTheme(themeName) {
        localStorage.setItem('selectedTheme', themeName);
    }

    getSavedTheme() {
        return localStorage.getItem('selectedTheme');
    }

    // 외부에서 테마 변경할 수 있는 메서드
    setTheme(themeName) {
        this.switchTheme(themeName);
    }

    getCurrentTheme() {
        return this.currentTheme;
    }

    getAvailableThemes() {
        return this.themes;
    }
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes themeTransition {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }

    .theme-toggle {
        animation: slideInFromTop 0.5s ease-out;
    }

    @keyframes slideInFromTop {
        from {
            transform: translateY(-20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// 전역 테마 매니저 인스턴스 생성
window.themeManager = new ThemeManager();

// DOM이 로드되면 테마 시스템 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 이미 초기화되었다면 재초기화하지 않음
    if (!window.themeManager) {
        window.themeManager = new ThemeManager();
    }
});

// 테마 변경 이벤트 디스패치
document.addEventListener('themeChanged', (e) => {
    console.log('Theme changed to:', e.detail.theme);
});