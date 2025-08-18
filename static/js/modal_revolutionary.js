// Revolutionary Modal System
class RevolutionaryModal {
    constructor() {
        this.modals = [];
        this.activeModal = null;
    }

    // Create and show modal
    show(options = {}) {
        const modalId = options.id || `modal-${Date.now()}`;
        
        // Default options
        const settings = {
            id: modalId,
            title: options.title || '',
            content: options.content || '',
            size: options.size || 'md', // sm, md, lg, xl
            showClose: options.showClose !== false,
            backdrop: options.backdrop !== false,
            buttons: options.buttons || [],
            onShow: options.onShow || null,
            onClose: options.onClose || null,
            type: options.type || 'default' // default, alert, confirm, form, loading
        };

        // Create modal elements
        const backdrop = this.createBackdrop(modalId);
        const modal = this.createModal(settings);

        // Add to DOM
        document.body.appendChild(backdrop);
        document.body.appendChild(modal);

        // Show with animation
        setTimeout(() => {
            backdrop.classList.add('show');
            modal.classList.add('show');
        }, 10);

        // Store reference
        this.activeModal = {
            id: modalId,
            backdrop: backdrop,
            modal: modal,
            settings: settings
        };

        // Call onShow callback
        if (settings.onShow) {
            settings.onShow(modal);
        }

        return modalId;
    }

    // Create backdrop element
    createBackdrop(modalId) {
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop-revolutionary';
        backdrop.id = `${modalId}-backdrop`;
        backdrop.addEventListener('click', () => {
            if (this.activeModal && this.activeModal.settings.backdrop) {
                this.close();
            }
        });
        return backdrop;
    }

    // Create modal element
    createModal(settings) {
        const modal = document.createElement('div');
        modal.className = `modal-revolutionary modal-${settings.size}`;
        modal.id = settings.id;

        // Build modal content based on type
        let modalContent = '';
        
        if (settings.type === 'alert') {
            modalContent = this.createAlertContent(settings);
        } else if (settings.type === 'confirm') {
            modalContent = this.createConfirmContent(settings);
        } else if (settings.type === 'loading') {
            modalContent = this.createLoadingContent(settings);
        } else {
            modalContent = this.createDefaultContent(settings);
        }

        modal.innerHTML = modalContent;

        // Add event listeners
        this.addEventListeners(modal, settings);

        return modal;
    }

    // Create default modal content
    createDefaultContent(settings) {
        let html = '';
        
        // Header
        if (settings.title) {
            html += `
                <div class="modal-header-revolutionary">
                    <h3 class="modal-title-revolutionary">${settings.title}</h3>
                    ${settings.showClose ? '<button class="modal-close-revolutionary" data-action="close">&times;</button>' : ''}
                </div>
            `;
        }

        // Body
        html += `
            <div class="modal-body-revolutionary">
                ${settings.content}
            </div>
        `;

        // Footer with buttons
        if (settings.buttons && settings.buttons.length > 0) {
            html += '<div class="modal-footer-revolutionary">';
            settings.buttons.forEach(button => {
                const btnClass = button.class || 'btn btn-outline-primary';
                const btnAction = button.action || 'close';
                html += `
                    <button class="${btnClass}" data-action="${btnAction}">
                        ${button.icon ? `<i class="${button.icon} me-2"></i>` : ''}
                        ${button.text}
                    </button>
                `;
            });
            html += '</div>';
        }

        return html;
    }

    // Create alert modal content
    createAlertContent(settings) {
        const alertType = settings.alertType || 'info';
        const icons = {
            success: 'fas fa-check',
            error: 'fas fa-times',
            warning: 'fas fa-exclamation',
            info: 'fas fa-info'
        };

        return `
            <div class="modal-body-revolutionary modal-alert-revolutionary modal-alert-${alertType}">
                <div class="modal-alert-icon">
                    <i class="${icons[alertType]}"></i>
                </div>
                <h4 style="color: #fff; margin-bottom: 1rem;">${settings.title}</h4>
                <p style="color: #8892b0;">${settings.content}</p>
            </div>
            <div class="modal-footer-revolutionary">
                <button class="btn btn-gradient" data-action="close">확인</button>
            </div>
        `;
    }

    // Create confirm modal content
    createConfirmContent(settings) {
        return `
            <div class="modal-header-revolutionary">
                <h3 class="modal-title-revolutionary">${settings.title || '확인'}</h3>
            </div>
            <div class="modal-body-revolutionary">
                <div class="modal-confirm-message">${settings.content}</div>
            </div>
            <div class="modal-footer-revolutionary modal-confirm-buttons">
                <button class="btn btn-outline-secondary" data-action="cancel">취소</button>
                <button class="btn btn-gradient" data-action="confirm">확인</button>
            </div>
        `;
    }

    // Create loading modal content
    createLoadingContent(settings) {
        return `
            <div class="modal-body-revolutionary modal-loading-revolutionary">
                <div class="modal-loading-spinner"></div>
                <div class="modal-loading-text">${settings.content || '처리 중입니다...'}</div>
            </div>
        `;
    }

    // Add event listeners to modal
    addEventListeners(modal, settings) {
        // Close button
        const closeBtn = modal.querySelector('[data-action="close"]');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Cancel button
        const cancelBtn = modal.querySelector('[data-action="cancel"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                if (settings.onCancel) settings.onCancel();
                this.close();
            });
        }

        // Confirm button
        const confirmBtn = modal.querySelector('[data-action="confirm"]');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                if (settings.onConfirm) settings.onConfirm();
                this.close();
            });
        }

        // Custom action buttons
        settings.buttons?.forEach(button => {
            if (button.action && button.action !== 'close') {
                const btn = modal.querySelector(`[data-action="${button.action}"]`);
                if (btn && button.onClick) {
                    btn.addEventListener('click', () => button.onClick(modal));
                }
            }
        });
    }

    // Close active modal
    close() {
        if (!this.activeModal) return;

        const { backdrop, modal, settings } = this.activeModal;

        // Call onClose callback
        if (settings.onClose) {
            settings.onClose(modal);
        }

        // Hide with animation
        backdrop.classList.remove('show');
        modal.classList.remove('show');
        modal.classList.add('slide-out');

        // Remove from DOM
        setTimeout(() => {
            backdrop.remove();
            modal.remove();
            this.activeModal = null;
        }, 300);
    }

    // Alert modal shorthand
    alert(message, title = '알림', type = 'info') {
        return this.show({
            type: 'alert',
            title: title,
            content: message,
            alertType: type,
            size: 'sm'
        });
    }

    // Confirm modal shorthand
    confirm(message, onConfirm, onCancel = null, title = '확인') {
        return this.show({
            type: 'confirm',
            title: title,
            content: message,
            size: 'sm',
            onConfirm: onConfirm,
            onCancel: onCancel
        });
    }

    // Loading modal shorthand
    loading(message = '처리 중입니다...') {
        return this.show({
            type: 'loading',
            content: message,
            size: 'sm',
            backdrop: false,
            showClose: false
        });
    }

    // Update modal content
    updateContent(content) {
        if (!this.activeModal) return;
        
        const bodyElement = this.activeModal.modal.querySelector('.modal-body-revolutionary');
        if (bodyElement) {
            bodyElement.innerHTML = content;
        }
    }

    // Update loading text
    updateLoadingText(text) {
        if (!this.activeModal) return;
        
        const textElement = this.activeModal.modal.querySelector('.modal-loading-text');
        if (textElement) {
            textElement.textContent = text;
        }
    }
}

// Toast Notification System
class RevolutionaryToast {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.init();
    }

    init() {
        // Create toast container if not exists
        if (!document.getElementById('toast-container-revolutionary')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container-revolutionary';
            this.container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10001;';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container-revolutionary');
        }
    }

    show(message, type = 'info', duration = 3000) {
        const toastId = `toast-${Date.now()}`;
        const toast = document.createElement('div');
        toast.className = 'toast-revolutionary';
        toast.id = toastId;

        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        const colors = {
            success: '#00ff88',
            error: '#ff4444',
            warning: '#ffbb33',
            info: '#00d4ff'
        };

        toast.innerHTML = `
            <div class="toast-header-revolutionary">
                <span class="toast-title-revolutionary">
                    <i class="${icons[type]}" style="color: ${colors[type]}; margin-right: 0.5rem;"></i>
                    ${type.charAt(0).toUpperCase() + type.slice(1)}
                </span>
                <button class="toast-close-revolutionary">&times;</button>
            </div>
            <div class="toast-body-revolutionary">${message}</div>
        `;

        // Add to container
        this.container.appendChild(toast);

        // Show animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Close button
        toast.querySelector('.toast-close-revolutionary').addEventListener('click', () => {
            this.hide(toastId);
        });

        // Auto hide
        if (duration > 0) {
            setTimeout(() => this.hide(toastId), duration);
        }

        this.toasts.push({ id: toastId, element: toast });
        return toastId;
    }

    hide(toastId) {
        const toastIndex = this.toasts.findIndex(t => t.id === toastId);
        if (toastIndex === -1) return;

        const toast = this.toasts[toastIndex].element;
        toast.classList.remove('show');

        setTimeout(() => {
            toast.remove();
            this.toasts.splice(toastIndex, 1);
        }, 300);
    }

    success(message, duration = 3000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 3000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 3000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 3000) {
        return this.show(message, 'info', duration);
    }
}

// Initialize global instances
const revolutionaryModal = new RevolutionaryModal();
const revolutionaryToast = new RevolutionaryToast();

// Export for use
window.RevolutionaryModal = revolutionaryModal;
window.RevolutionaryToast = revolutionaryToast;