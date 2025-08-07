// 직무 상세 정보 표시 - 매우 풍부한 현대적 버전
function displayJobDetail(job) {
    const profile = job.profile || {};
    
    // 모달 제목 설정
    const modalTitle = document.getElementById('modalTitle');
    const fullscreenTitle = document.getElementById('fullscreenTitle');
    
    if (modalTitle) {
        modalTitle.innerHTML = `
            <div class="modal-title-modern">
                <span class="job-badge ${job.category === 'PL' ? 'badge-pl' : 'badge-non-pl'}">${job.category || 'Non-PL'}</span>
                <span class="job-name">${job.name}</span>
                ${job.level ? `<span class="level-badge">${job.level}</span>` : ''}
            </div>
        `;
    }
    if (fullscreenTitle) fullscreenTitle.innerHTML = modalTitle ? modalTitle.innerHTML : job.name;
    
    // 상세 내용 HTML 생성 - 매우 풍부한 버전
    const detailHTML = `
        <div class="job-detail-modern">
            <!-- 요약 카드 -->
            ${job.summary ? `
            <div class="summary-card">
                <div class="summary-icon">
                    <i class="fas fa-lightbulb"></i>
                </div>
                <div class="summary-content">
                    <h4>직무 개요</h4>
                    <p>${job.summary}</p>
                </div>
            </div>
            ` : ''}

            <!-- 기본 정보 그리드 -->
            <div class="info-grid-modern">
                <div class="info-card">
                    <i class="fas fa-sitemap"></i>
                    <div>
                        <label>직군</label>
                        <span>${job.category || '-'}</span>
                    </div>
                </div>
                <div class="info-card">
                    <i class="fas fa-layer-group"></i>
                    <div>
                        <label>직종</label>
                        <span>${job.type || '-'}</span>
                    </div>
                </div>
            </div>

            ${profile && Object.keys(profile).length > 0 ? `
                
                <!-- 핵심 역할 및 책임 -->
                ${profile.role_responsibility ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-clipboard-list"></i>
                        <h3>핵심 역할 및 책임</h3>
                    </div>
                    <div class="section-content">
                        ${formatModernText(profile.role_responsibility)}
                    </div>
                </section>
                ` : ''}

                <!-- 자격 요건 -->
                ${(profile.required_qualifications || profile.preferred_qualifications) ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-user-check"></i>
                        <h3>자격 요건</h3>
                    </div>
                    <div class="qualification-grid">
                        ${profile.required_qualifications ? `
                        <div class="qualification-card required">
                            <div class="qualification-header">
                                <i class="fas fa-check-circle"></i>
                                <h4>필수 자격</h4>
                            </div>
                            ${formatModernText(profile.required_qualifications)}
                        </div>
                        ` : ''}
                        ${profile.preferred_qualifications ? `
                        <div class="qualification-card preferred">
                            <div class="qualification-header">
                                <i class="fas fa-star"></i>
                                <h4>우대 자격</h4>
                            </div>
                            ${formatModernText(profile.preferred_qualifications)}
                        </div>
                        ` : ''}
                    </div>
                </section>
                ` : ''}

                <!-- 필요 역량 -->
                ${(profile.basic_skills || profile.applied_skills) ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-award"></i>
                        <h3>필요 역량</h3>
                    </div>
                    <div class="skills-modern">
                        ${profile.basic_skills ? `
                        <div class="skill-category">
                            <h4><i class="fas fa-layer-group"></i> 기본 역량</h4>
                            <div class="skill-tags">
                                ${profile.basic_skills.map(skill => 
                                    `<span class="skill-tag basic">${skill}</span>`
                                ).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${profile.applied_skills ? `
                        <div class="skill-category">
                            <h4><i class="fas fa-rocket"></i> 우대 역량</h4>
                            <div class="skill-tags">
                                ${profile.applied_skills.map(skill => 
                                    `<span class="skill-tag advanced">${skill}</span>`
                                ).join('')}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </section>
                ` : ''}

                <!-- 활용 도구 -->
                ${profile.tools && profile.tools.length > 0 ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-tools"></i>
                        <h3>활용 도구</h3>
                    </div>
                    <div class="tools-grid">
                        ${profile.tools.map(tool => 
                            `<span class="tool-tag"><i class="fas fa-wrench"></i> ${tool}</span>`
                        ).join('')}
                    </div>
                </section>
                ` : ''}

                <!-- 성장 경로 -->
                ${profile.growth_path ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-route"></i>
                        <h3>커리어 성장 경로</h3>
                    </div>
                    <div class="growth-path">
                        ${profile.growth_path.split('→').map((step, index) => `
                            <div class="path-step">
                                <div class="step-number">${index + 1}</div>
                                <div class="step-content">${step.trim()}</div>
                            </div>
                        `).join('<div class="path-arrow"><i class="fas fa-chevron-right"></i></div>')}
                    </div>
                </section>
                ` : ''}

                <!-- 경력 개발 계획 -->
                ${profile.career_development ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-graduation-cap"></i>
                        <h3>경력 개발 계획</h3>
                    </div>
                    <div class="career-timeline">
                        ${profile.career_development.short_term ? `
                        <div class="timeline-item">
                            <div class="timeline-badge short">단기</div>
                            <div class="timeline-content">
                                <h4>1-2년</h4>
                                <p>${profile.career_development.short_term}</p>
                            </div>
                        </div>
                        ` : ''}
                        ${profile.career_development.mid_term ? `
                        <div class="timeline-item">
                            <div class="timeline-badge mid">중기</div>
                            <div class="timeline-content">
                                <h4>3-5년</h4>
                                <p>${profile.career_development.mid_term}</p>
                            </div>
                        </div>
                        ` : ''}
                        ${profile.career_development.long_term ? `
                        <div class="timeline-item">
                            <div class="timeline-badge long">장기</div>
                            <div class="timeline-content">
                                <h4>5년 이상</h4>
                                <p>${profile.career_development.long_term}</p>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </section>
                ` : ''}

                <!-- 관련 자격증 -->
                ${profile.related_certifications && profile.related_certifications.length > 0 ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-certificate"></i>
                        <h3>관련 자격증</h3>
                    </div>
                    <div class="certification-grid">
                        ${profile.related_certifications.map(cert => 
                            `<div class="cert-card">
                                <i class="fas fa-medal"></i>
                                <span>${cert}</span>
                            </div>`
                        ).join('')}
                    </div>
                </section>
                ` : ''}

                <!-- 성과 지표 -->
                ${profile.kpi_metrics && profile.kpi_metrics.length > 0 ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-chart-bar"></i>
                        <h3>주요 성과 지표 (KPI)</h3>
                    </div>
                    <div class="kpi-grid">
                        ${profile.kpi_metrics.map(kpi => 
                            `<div class="kpi-item">
                                <i class="fas fa-bullseye"></i>
                                <span>${kpi}</span>
                            </div>`
                        ).join('')}
                    </div>
                </section>
                ` : ''}

                <!-- 주요 이해관계자 -->
                ${profile.key_stakeholders && profile.key_stakeholders.length > 0 ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-users"></i>
                        <h3>주요 이해관계자</h3>
                    </div>
                    <div class="stakeholder-grid">
                        ${profile.key_stakeholders.map(stakeholder => 
                            `<div class="stakeholder-card">
                                <i class="fas fa-user-tie"></i>
                                <span>${stakeholder}</span>
                            </div>`
                        ).join('')}
                    </div>
                </section>
                ` : ''}

                <!-- 대표 프로젝트 -->
                ${profile.typical_projects && profile.typical_projects.length > 0 ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-project-diagram"></i>
                        <h3>대표 프로젝트</h3>
                    </div>
                    <div class="project-list">
                        ${profile.typical_projects.map(project => 
                            `<div class="project-item">
                                <i class="fas fa-folder-open"></i>
                                <span>${project}</span>
                            </div>`
                        ).join('')}
                    </div>
                </section>
                ` : ''}

                <!-- 근무 환경 -->
                ${profile.work_environment ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-laptop-house"></i>
                        <h3>근무 환경</h3>
                    </div>
                    <div class="environment-content">
                        ${formatModernText(profile.work_environment)}
                    </div>
                </section>
                ` : ''}

                <!-- 보상 범위 -->
                ${profile.compensation_range ? `
                <section class="detail-section-modern">
                    <div class="section-header">
                        <i class="fas fa-coins"></i>
                        <h3>예상 연봉 범위</h3>
                    </div>
                    <div class="compensation-content">
                        <div class="compensation-badge">
                            <i class="fas fa-won-sign"></i>
                            <span>${profile.compensation_range}</span>
                        </div>
                    </div>
                </section>
                ` : ''}

            ` : `
                <div class="empty-profile">
                    <i class="fas fa-file-circle-plus fa-3x"></i>
                    <p>아직 작성된 직무기술서가 없습니다.</p>
                </div>
            `}
        </div>
    `;
    
    // 모달과 전체화면 모두에 내용 설정
    const modalBody = document.getElementById('modalBody');
    const fullscreenBody = document.getElementById('fullscreenBody');
    
    if (modalBody) {
        modalBody.innerHTML = detailHTML;
    }
    if (fullscreenBody) {
        fullscreenBody.innerHTML = detailHTML;
    }
    
    // 모달 표시
    openModal();
}

// 텍스트 포맷팅 헬퍼 함수 - 현대적 스타일
function formatModernText(text) {
    if (!text) return '';
    return text.split('\n').map(line => {
        if (line.startsWith('•')) {
            return `<li>${line.substring(1).trim()}</li>`;
        }
        return `<p>${line}</p>`;
    }).join('').replace(/<li>/g, '<ul><li>').replace(/<\/li>(?!<li>)/g, '</li></ul>');
}