// Sidebar Auto-Hide Functionality
class SidebarAutoHide {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.overlay = document.getElementById('sidebar-overlay');
        this.menuToggle = document.getElementById('menuToggle');
        this.hoverZone = null;
        this.isDesktop = window.innerWidth >= 1024; // lg breakpoint
        this.autoHideEnabled = true;
        this.mouseLeaveTimer = null;
        this.isHovering = false;
        
        this.init();
    }

    init() {
        if (!this.sidebar) return;
        
        // Create hover detection zone
        this.createHoverZone();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize sidebar state
        this.initializeSidebarState();
        
        // Handle window resize
        this.handleResize();
    }

    createHoverZone() {
        // Create an invisible hover zone on the left edge of the screen
        this.hoverZone = document.createElement('div');
        this.hoverZone.id = 'sidebar-hover-zone';
        this.hoverZone.style.cssText = `
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 20px;
            z-index: 35;
            cursor: pointer;
        `;
        document.body.appendChild(this.hoverZone);
    }

    setupEventListeners() {
        // Menu link clicks - auto-hide sidebar after navigation
        const menuLinks = this.sidebar.querySelectorAll('a[href]:not([href="#"])');
        menuLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // Don't prevent default - let the link work normally
                if (this.isDesktop && this.autoHideEnabled) {
                    // Hide sidebar after a short delay to allow navigation
                    setTimeout(() => {
                        this.hideSidebar();
                    }, 100);
                }
            });
        });

        // Hover zone events - show sidebar when mouse is near left edge
        this.hoverZone.addEventListener('mouseenter', () => {
            if (this.isDesktop && this.autoHideEnabled) {
                this.showSidebar();
            }
        });

        // Sidebar mouse events
        this.sidebar.addEventListener('mouseenter', () => {
            this.isHovering = true;
            // Clear any pending hide timer
            if (this.mouseLeaveTimer) {
                clearTimeout(this.mouseLeaveTimer);
                this.mouseLeaveTimer = null;
            }
        });

        this.sidebar.addEventListener('mouseleave', () => {
            this.isHovering = false;
            if (this.isDesktop && this.autoHideEnabled) {
                // Hide sidebar after mouse leaves with a delay
                this.mouseLeaveTimer = setTimeout(() => {
                    if (!this.isHovering) {
                        this.hideSidebar();
                    }
                }, 500); // 500ms delay before hiding
            }
        });

        // Toggle button for manual control
        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + B to toggle sidebar
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                this.toggleSidebar();
            }
            
            // Escape to hide sidebar
            if (e.key === 'Escape' && !this.sidebar.classList.contains('-translate-x-full')) {
                this.hideSidebar();
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    initializeSidebarState() {
        // Check localStorage for saved preference
        const savedState = localStorage.getItem('sidebarAutoHide');
        
        if (savedState !== null) {
            this.autoHideEnabled = savedState === 'true';
        }
        
        // On desktop, start with sidebar hidden if auto-hide is enabled
        if (this.isDesktop && this.autoHideEnabled) {
            this.hideSidebar();
        } else if (this.isDesktop) {
            this.showSidebar();
        }
        
        // On mobile, always start hidden
        if (!this.isDesktop) {
            this.hideSidebar();
        }
    }

    handleResize() {
        const wasDesktop = this.isDesktop;
        this.isDesktop = window.innerWidth >= 1024;
        
        // If switched from mobile to desktop
        if (!wasDesktop && this.isDesktop) {
            if (this.autoHideEnabled) {
                this.hideSidebar();
            } else {
                this.showSidebar();
            }
            this.hoverZone.style.display = 'block';
        }
        
        // If switched from desktop to mobile
        if (wasDesktop && !this.isDesktop) {
            this.hideSidebar();
            this.hoverZone.style.display = 'none';
        }
    }

    showSidebar() {
        this.sidebar.classList.remove('-translate-x-full');
        
        // Adjust main content margin
        const mainContent = document.querySelector('main');
        if (mainContent && this.isDesktop) {
            mainContent.style.marginLeft = '18rem'; // 72 * 0.25rem = 18rem
            mainContent.style.transition = 'margin-left 0.3s ease';
        }
        
        // Hide hover zone when sidebar is visible
        if (this.hoverZone) {
            this.hoverZone.style.pointerEvents = 'none';
        }
        
        // Update overlay for mobile
        if (!this.isDesktop && this.overlay) {
            this.overlay.classList.remove('opacity-0', 'pointer-events-none');
            this.overlay.classList.add('opacity-100');
        }
        
        // Update toggle button state
        if (this.menuToggle) {
            this.menuToggle.setAttribute('aria-expanded', 'true');
        }
    }

    hideSidebar() {
        this.sidebar.classList.add('-translate-x-full');
        
        // Adjust main content to full width
        const mainContent = document.querySelector('main');
        if (mainContent && this.isDesktop) {
            mainContent.style.marginLeft = '0';
            mainContent.style.transition = 'margin-left 0.3s ease';
        }
        
        // Show hover zone when sidebar is hidden
        if (this.hoverZone && this.isDesktop) {
            this.hoverZone.style.pointerEvents = 'auto';
        }
        
        // Update overlay for mobile
        if (!this.isDesktop && this.overlay) {
            this.overlay.classList.add('opacity-0', 'pointer-events-none');
            this.overlay.classList.remove('opacity-100');
        }
        
        // Update toggle button state
        if (this.menuToggle) {
            this.menuToggle.setAttribute('aria-expanded', 'false');
        }
    }

    toggleSidebar() {
        const isHidden = this.sidebar.classList.contains('-translate-x-full');
        
        if (isHidden) {
            this.showSidebar();
        } else {
            this.hideSidebar();
        }
    }

    setAutoHide(enabled) {
        this.autoHideEnabled = enabled;
        localStorage.setItem('sidebarAutoHide', enabled.toString());
        
        if (this.isDesktop) {
            if (enabled) {
                this.hideSidebar();
            } else {
                this.showSidebar();
            }
        }
    }

    // Public method to get current state
    getState() {
        return {
            isVisible: !this.sidebar.classList.contains('-translate-x-full'),
            autoHideEnabled: this.autoHideEnabled,
            isDesktop: this.isDesktop
        };
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sidebarAutoHide = new SidebarAutoHide();
    
    // Connect the toggle switch in the sidebar
    const sidebarToggle = document.getElementById('sidebarAutoHideToggle');
    if (sidebarToggle) {
        // Set initial state from localStorage
        const savedState = localStorage.getItem('sidebarAutoHide');
        if (savedState !== null) {
            sidebarToggle.checked = savedState === 'true';
        }
        
        // Handle toggle changes
        sidebarToggle.addEventListener('change', (e) => {
            window.sidebarAutoHide.setAutoHide(e.target.checked);
        });
    }
    
    // Add keyboard shortcut hint
    const shortcutHint = document.createElement('div');
    shortcutHint.className = 'fixed bottom-4 right-4 bg-gray-800 text-white px-3 py-2 rounded-lg text-xs opacity-0 transition-opacity duration-300 z-50';
    shortcutHint.innerHTML = 'Tip: Ctrl+B로 사이드바 토글';
    document.body.appendChild(shortcutHint);
    
    // Show hint on first visit
    if (!localStorage.getItem('sidebarHintShown')) {
        setTimeout(() => {
            shortcutHint.style.opacity = '1';
            setTimeout(() => {
                shortcutHint.style.opacity = '0';
                localStorage.setItem('sidebarHintShown', 'true');
            }, 3000);
        }, 1000);
    }
});