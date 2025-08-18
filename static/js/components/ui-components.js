/**
 * OK Financial Group e-HR System - UI Components Library
 * Modern, accessible, and responsive UI components
 */

// ===== Button Component =====
class Button {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            variant: 'primary', // primary, secondary, ghost, destructive
            size: 'md', // sm, md, lg
            loading: false,
            disabled: false,
            icon: null,
            ...options
        };
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        const { variant, size, loading, disabled, icon } = this.options;
        
        // Base classes
        let classes = 'btn inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:pointer-events-none disabled:opacity-50';
        
        // Variant classes
        const variantClasses = {
            primary: 'bg-primary text-white hover:bg-primary-hover',
            secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600',
            ghost: 'hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-700 dark:hover:text-gray-100',
            destructive: 'bg-red-600 text-white hover:bg-red-700'
        };
        classes += ' ' + variantClasses[variant];
        
        // Size classes
        const sizeClasses = {
            sm: 'h-9 px-3 text-sm',
            md: 'h-10 px-4 py-2',
            lg: 'h-11 px-8 text-lg'
        };
        classes += ' ' + sizeClasses[size];
        
        this.element.className = classes;
        
        // Content
        let content = '';
        if (loading) {
            content = '<i class="fas fa-spinner fa-spin mr-2"></i>';
        } else if (icon) {
            content = `<i class="${icon} mr-2"></i>`;
        }
        content += this.element.textContent;
        
        this.element.innerHTML = content;
        this.element.disabled = disabled || loading;
    }

    attachEventListeners() {
        this.element.addEventListener('click', (e) => {
            if (this.options.loading) {
                e.preventDefault();
            }
        });
    }

    setLoading(loading) {
        this.options.loading = loading;
        this.render();
    }

    setDisabled(disabled) {
        this.options.disabled = disabled;
        this.render();
    }
}

// ===== Input Component =====
class Input {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            type: 'text',
            label: '',
            placeholder: '',
            value: '',
            error: '',
            required: false,
            disabled: false,
            icon: null,
            ...options
        };
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        const { type, label, placeholder, value, error, required, disabled, icon } = this.options;
        
        let html = '<div class="input-group">';
        
        // Label
        if (label) {
            html += `<label class="input-label text-sm font-medium leading-none mb-2 ${disabled ? 'opacity-70' : ''}">${label}${required ? ' <span class="text-red-500">*</span>' : ''}</label>`;
        }
        
        // Input wrapper
        html += '<div class="relative">';
        
        // Icon
        if (icon) {
            html += `<i class="${icon} absolute left-3 top-3 text-gray-400"></i>`;
        }
        
        // Input
        const inputClasses = `input flex h-10 w-full rounded-md border ${error ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'} bg-white dark:bg-gray-700 ${icon ? 'pl-10' : 'px-3'} py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 ${error ? 'focus:ring-red-500' : 'focus:ring-primary'} disabled:cursor-not-allowed disabled:opacity-50`;
        
        html += `<input type="${type}" class="${inputClasses}" placeholder="${placeholder}" value="${value}" ${required ? 'required' : ''} ${disabled ? 'disabled' : ''}>`;
        
        html += '</div>';
        
        // Error message
        if (error) {
            html += `<p class="input-error text-sm text-red-600 mt-1">${error}</p>`;
        }
        
        html += '</div>';
        
        this.container.innerHTML = html;
        this.input = this.container.querySelector('input');
    }

    attachEventListeners() {
        this.input.addEventListener('input', (e) => {
            this.options.value = e.target.value;
            if (this.options.onInput) {
                this.options.onInput(e.target.value);
            }
        });

        this.input.addEventListener('change', (e) => {
            if (this.options.onChange) {
                this.options.onChange(e.target.value);
            }
        });
    }

    getValue() {
        return this.input.value;
    }

    setValue(value) {
        this.options.value = value;
        this.input.value = value;
    }

    setError(error) {
        this.options.error = error;
        this.render();
        this.attachEventListeners();
    }

    clearError() {
        this.setError('');
    }
}

// ===== Select Component =====
class Select {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            label: '',
            placeholder: 'Select an option',
            options: [], // [{value: '', label: ''}]
            value: '',
            multiple: false,
            searchable: false,
            disabled: false,
            error: '',
            ...options
        };
        this.isOpen = false;
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        const { label, placeholder, options, value, multiple, error, disabled } = this.options;
        
        let html = '<div class="select-group">';
        
        // Label
        if (label) {
            html += `<label class="input-label text-sm font-medium leading-none mb-2">${label}</label>`;
        }
        
        // Select wrapper
        html += '<div class="relative">';
        
        // Selected value display
        const selectedOption = options.find(opt => opt.value === value);
        const displayText = selectedOption ? selectedOption.label : placeholder;
        
        html += `
            <button type="button" class="select-trigger w-full text-left px-3 py-2 rounded-md border ${error ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'} bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-primary ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}" ${disabled ? 'disabled' : ''}>
                <span class="${!selectedOption ? 'text-gray-400' : ''}">${displayText}</span>
                <i class="fas fa-chevron-down absolute right-3 top-3 text-gray-400"></i>
            </button>
        `;
        
        // Dropdown
        html += `
            <div class="select-dropdown hidden absolute top-full mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-dropdown">
                ${this.options.searchable ? '<input type="text" class="w-full px-3 py-2 border-b border-gray-200 dark:border-gray-700 focus:outline-none" placeholder="Search...">' : ''}
                <div class="select-options max-h-60 overflow-y-auto">
        `;
        
        options.forEach(option => {
            const isSelected = option.value === value;
            html += `
                <div class="select-option px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer ${isSelected ? 'bg-primary text-white' : ''}" data-value="${option.value}">
                    ${multiple ? `<input type="checkbox" class="mr-2" ${isSelected ? 'checked' : ''}>` : ''}
                    ${option.label}
                </div>
            `;
        });
        
        html += '</div></div>';
        html += '</div>';
        
        // Error message
        if (error) {
            html += `<p class="input-error text-sm text-red-600 mt-1">${error}</p>`;
        }
        
        html += '</div>';
        
        this.container.innerHTML = html;
        this.trigger = this.container.querySelector('.select-trigger');
        this.dropdown = this.container.querySelector('.select-dropdown');
    }

    attachEventListeners() {
        // Toggle dropdown
        this.trigger.addEventListener('click', () => {
            if (!this.options.disabled) {
                this.toggleDropdown();
            }
        });

        // Select option
        this.container.querySelectorAll('.select-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const value = e.currentTarget.dataset.value;
                this.selectOption(value);
            });
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Search functionality
        if (this.options.searchable) {
            const searchInput = this.container.querySelector('.select-dropdown input');
            searchInput.addEventListener('input', (e) => {
                this.filterOptions(e.target.value);
            });
        }
    }

    toggleDropdown() {
        this.isOpen = !this.isOpen;
        this.dropdown.classList.toggle('hidden');
        
        // Update chevron icon
        const chevron = this.trigger.querySelector('i');
        chevron.classList.toggle('fa-chevron-down');
        chevron.classList.toggle('fa-chevron-up');
    }

    closeDropdown() {
        this.isOpen = false;
        this.dropdown.classList.add('hidden');
        
        const chevron = this.trigger.querySelector('i');
        chevron.classList.add('fa-chevron-down');
        chevron.classList.remove('fa-chevron-up');
    }

    selectOption(value) {
        if (!this.options.multiple) {
            this.options.value = value;
            this.render();
            this.attachEventListeners();
            this.closeDropdown();
            
            if (this.options.onChange) {
                this.options.onChange(value);
            }
        }
    }

    filterOptions(searchTerm) {
        const options = this.container.querySelectorAll('.select-option');
        options.forEach(option => {
            const text = option.textContent.toLowerCase();
            if (text.includes(searchTerm.toLowerCase())) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        });
    }
}

// ===== Card Component =====
class Card {
    static create(options = {}) {
        const {
            title = '',
            description = '',
            content = '',
            icon = null,
            actions = null,
            className = ''
        } = options;
        
        let html = `<div class="card rounded-lg border bg-white dark:bg-gray-800 shadow-sm p-6 ${className}">`;
        
        // Header
        if (title || description) {
            html += '<div class="card-header flex flex-col space-y-1.5 mb-4">';
            
            if (icon) {
                html += `<i class="${icon} text-2xl text-primary mb-2"></i>`;
            }
            
            if (title) {
                html += `<h3 class="card-title text-2xl font-semibold leading-none tracking-tight">${title}</h3>`;
            }
            
            if (description) {
                html += `<p class="card-description text-sm text-gray-600 dark:text-gray-400">${description}</p>`;
            }
            
            html += '</div>';
        }
        
        // Content
        if (content) {
            html += `<div class="card-content">${content}</div>`;
        }
        
        // Actions
        if (actions) {
            html += `<div class="card-actions flex items-center justify-end space-x-2 mt-6">${actions}</div>`;
        }
        
        html += '</div>';
        
        return html;
    }
}

// ===== Modal/Dialog Component =====
class Modal {
    constructor(options = {}) {
        this.options = {
            title: '',
            content: '',
            size: 'md', // sm, md, lg, xl
            closable: true,
            actions: null,
            onClose: null,
            ...options
        };
        this.isOpen = false;
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        const { title, content, size, closable, actions } = this.options;
        
        // Create modal container
        this.modalContainer = document.createElement('div');
        this.modalContainer.className = 'modal fixed inset-0 z-modal hidden';
        
        // Size classes
        const sizeClasses = {
            sm: 'max-w-md',
            md: 'max-w-lg',
            lg: 'max-w-2xl',
            xl: 'max-w-4xl'
        };
        
        let html = `
            <!-- Backdrop -->
            <div class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 z-modal-backdrop"></div>
            
            <!-- Modal Content -->
            <div class="modal-content relative bg-white dark:bg-gray-800 rounded-lg shadow-xl z-modal mx-auto mt-20 ${sizeClasses[size]} animate-slide-in">
                <!-- Header -->
                <div class="modal-header flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                    <h2 class="text-xl font-semibold">${title}</h2>
                    ${closable ? '<button class="modal-close text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"><i class="fas fa-times text-xl"></i></button>' : ''}
                </div>
                
                <!-- Body -->
                <div class="modal-body p-6">
                    ${content}
                </div>
                
                ${actions ? `
                <!-- Footer -->
                <div class="modal-footer flex items-center justify-end space-x-2 p-6 border-t border-gray-200 dark:border-gray-700">
                    ${actions}
                </div>
                ` : ''}
            </div>
        `;
        
        this.modalContainer.innerHTML = html;
        document.body.appendChild(this.modalContainer);
    }

    attachEventListeners() {
        // Close button
        const closeBtn = this.modalContainer.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Backdrop click
        const backdrop = this.modalContainer.querySelector('.modal-backdrop');
        backdrop.addEventListener('click', () => {
            if (this.options.closable) {
                this.close();
            }
        });

        // ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen && this.options.closable) {
                this.close();
            }
        });
    }

    open() {
        this.isOpen = true;
        this.modalContainer.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.isOpen = false;
        this.modalContainer.classList.add('hidden');
        document.body.style.overflow = '';
        
        if (this.options.onClose) {
            this.options.onClose();
        }
        
        // Remove from DOM after animation
        setTimeout(() => {
            this.modalContainer.remove();
        }, 300);
    }

    setContent(content) {
        const body = this.modalContainer.querySelector('.modal-body');
        body.innerHTML = content;
    }
}

// ===== DataTable Component =====
class DataTable {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            columns: [], // [{key: '', label: '', sortable: true}]
            data: [],
            searchable: true,
            sortable: true,
            paginate: true,
            pageSize: 10,
            ...options
        };
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.searchTerm = '';
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        const { columns, searchable, paginate } = this.options;
        
        let html = '<div class="datatable-wrapper">';
        
        // Search and controls
        if (searchable || paginate) {
            html += '<div class="datatable-controls flex items-center justify-between mb-4">';
            
            if (searchable) {
                html += `
                    <div class="relative">
                        <input type="text" class="datatable-search pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary" placeholder="Search...">
                        <i class="fas fa-search absolute left-3 top-3 text-gray-400"></i>
                    </div>
                `;
            }
            
            if (paginate) {
                html += '<div class="datatable-pagination"></div>';
            }
            
            html += '</div>';
        }
        
        // Table
        html += `
            <div class="overflow-x-auto">
                <table class="table w-full">
                    <thead class="table-header border-b">
                        <tr>
        `;
        
        // Headers
        columns.forEach(column => {
            const sortable = column.sortable !== false && this.options.sortable;
            html += `
                <th class="table-head h-12 px-4 text-left align-middle font-medium text-gray-600 dark:text-gray-400 ${sortable ? 'cursor-pointer hover:text-gray-900 dark:hover:text-gray-200' : ''}" data-column="${column.key}">
                    ${column.label}
                    ${sortable ? '<i class="fas fa-sort ml-2 text-xs"></i>' : ''}
                </th>
            `;
        });
        
        html += `
                        </tr>
                    </thead>
                    <tbody class="table-body">
                    </tbody>
                </table>
            </div>
        `;
        
        html += '</div>';
        
        this.container.innerHTML = html;
        this.updateData();
    }

    attachEventListeners() {
        // Search
        const searchInput = this.container.querySelector('.datatable-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value;
                this.currentPage = 1;
                this.updateData();
            });
        }

        // Sort
        this.container.querySelectorAll('th[data-column]').forEach(th => {
            if (th.querySelector('.fa-sort')) {
                th.addEventListener('click', () => {
                    const column = th.dataset.column;
                    if (this.sortColumn === column) {
                        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
                    } else {
                        this.sortColumn = column;
                        this.sortDirection = 'asc';
                    }
                    this.updateData();
                });
            }
        });
    }

    updateData() {
        let filteredData = [...this.options.data];
        
        // Search
        if (this.searchTerm) {
            filteredData = filteredData.filter(row => {
                return Object.values(row).some(value => 
                    String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
                );
            });
        }
        
        // Sort
        if (this.sortColumn) {
            filteredData.sort((a, b) => {
                const aVal = a[this.sortColumn];
                const bVal = b[this.sortColumn];
                
                if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
                return 0;
            });
        }
        
        // Paginate
        const totalPages = Math.ceil(filteredData.length / this.options.pageSize);
        const start = (this.currentPage - 1) * this.options.pageSize;
        const paginatedData = filteredData.slice(start, start + this.options.pageSize);
        
        // Render rows
        const tbody = this.container.querySelector('tbody');
        tbody.innerHTML = '';
        
        paginatedData.forEach(row => {
            const tr = document.createElement('tr');
            tr.className = 'table-row border-b transition-colors hover:bg-gray-50 dark:hover:bg-gray-700';
            
            this.options.columns.forEach(column => {
                const td = document.createElement('td');
                td.className = 'table-cell p-4 align-middle';
                td.textContent = row[column.key] || '';
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
        
        // Update pagination
        if (this.options.paginate) {
            this.renderPagination(totalPages);
        }
        
        // Update sort icons
        this.updateSortIcons();
    }

    renderPagination(totalPages) {
        const pagination = this.container.querySelector('.datatable-pagination');
        if (!pagination) return;
        
        let html = '<div class="flex items-center space-x-2">';
        
        // Previous
        html += `<button class="pagination-btn px-3 py-1 rounded border ${this.currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}" data-page="${this.currentPage - 1}" ${this.currentPage === 1 ? 'disabled' : ''}><i class="fas fa-chevron-left"></i></button>`;
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                html += `<button class="pagination-btn px-3 py-1 rounded border ${i === this.currentPage ? 'bg-primary text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}" data-page="${i}">${i}</button>`;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                html += '<span class="px-2">...</span>';
            }
        }
        
        // Next
        html += `<button class="pagination-btn px-3 py-1 rounded border ${this.currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}" data-page="${this.currentPage + 1}" ${this.currentPage === totalPages ? 'disabled' : ''}><i class="fas fa-chevron-right"></i></button>`;
        
        html += '</div>';
        
        pagination.innerHTML = html;
        
        // Attach events
        pagination.querySelectorAll('.pagination-btn:not([disabled])').forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentPage = parseInt(btn.dataset.page);
                this.updateData();
            });
        });
    }

    updateSortIcons() {
        this.container.querySelectorAll('th[data-column] i').forEach(icon => {
            const column = icon.parentElement.dataset.column;
            
            icon.className = 'fas ml-2 text-xs';
            
            if (column === this.sortColumn) {
                icon.classList.add(this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down');
            } else {
                icon.classList.add('fa-sort');
            }
        });
    }
}

// ===== Badge Component =====
class Badge {
    static create(text, variant = 'primary') {
        const variantClasses = {
            primary: 'bg-primary text-white',
            secondary: 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-100',
            success: 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100',
            warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100',
            error: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100',
            info: 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
        };
        
        return `<span class="badge inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors ${variantClasses[variant]}">${text}</span>`;
    }
}

// ===== Tabs Component =====
class Tabs {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            tabs: [], // [{id: '', label: '', content: ''}]
            defaultTab: null,
            onChange: null,
            ...options
        };
        this.activeTab = this.options.defaultTab || (this.options.tabs[0]?.id || null);
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        const { tabs } = this.options;
        
        let html = '<div class="tabs-wrapper">';
        
        // Tab headers
        html += '<div class="tabs-header flex space-x-1 border-b border-gray-200 dark:border-gray-700">';
        
        tabs.forEach(tab => {
            const isActive = tab.id === this.activeTab;
            html += `
                <button class="tab-trigger px-4 py-2 text-sm font-medium transition-colors hover:text-primary ${isActive ? 'text-primary border-b-2 border-primary' : 'text-gray-600 dark:text-gray-400'}" data-tab="${tab.id}">
                    ${tab.label}
                </button>
            `;
        });
        
        html += '</div>';
        
        // Tab content
        html += '<div class="tabs-content mt-4">';
        
        tabs.forEach(tab => {
            const isActive = tab.id === this.activeTab;
            html += `
                <div class="tab-panel ${isActive ? '' : 'hidden'}" data-tab="${tab.id}">
                    ${tab.content}
                </div>
            `;
        });
        
        html += '</div>';
        html += '</div>';
        
        this.container.innerHTML = html;
    }

    attachEventListeners() {
        this.container.querySelectorAll('.tab-trigger').forEach(trigger => {
            trigger.addEventListener('click', () => {
                const tabId = trigger.dataset.tab;
                this.switchTab(tabId);
            });
        });
    }

    switchTab(tabId) {
        if (tabId === this.activeTab) return;
        
        this.activeTab = tabId;
        
        // Update triggers
        this.container.querySelectorAll('.tab-trigger').forEach(trigger => {
            const isActive = trigger.dataset.tab === tabId;
            if (isActive) {
                trigger.classList.add('text-primary', 'border-b-2', 'border-primary');
                trigger.classList.remove('text-gray-600', 'dark:text-gray-400');
            } else {
                trigger.classList.remove('text-primary', 'border-b-2', 'border-primary');
                trigger.classList.add('text-gray-600', 'dark:text-gray-400');
            }
        });
        
        // Update panels
        this.container.querySelectorAll('.tab-panel').forEach(panel => {
            const isActive = panel.dataset.tab === tabId;
            if (isActive) {
                panel.classList.remove('hidden');
            } else {
                panel.classList.add('hidden');
            }
        });
        
        if (this.options.onChange) {
            this.options.onChange(tabId);
        }
    }
}

// ===== Tooltip Component =====
class Tooltip {
    static init() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            new Tooltip(element);
        });
    }

    constructor(element) {
        this.element = element;
        this.text = element.dataset.tooltip;
        this.position = element.dataset.tooltipPosition || 'top';
        this.init();
    }

    init() {
        this.createTooltip();
        this.attachEventListeners();
    }

    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tooltip absolute z-tooltip bg-gray-900 text-white text-xs rounded px-2 py-1 pointer-events-none opacity-0 transition-opacity duration-200';
        this.tooltip.textContent = this.text;
        document.body.appendChild(this.tooltip);
    }

    attachEventListeners() {
        this.element.addEventListener('mouseenter', () => this.show());
        this.element.addEventListener('mouseleave', () => this.hide());
        this.element.addEventListener('focus', () => this.show());
        this.element.addEventListener('blur', () => this.hide());
    }

    show() {
        const rect = this.element.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();
        
        let top, left;
        
        switch (this.position) {
            case 'top':
                top = rect.top - tooltipRect.height - 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = rect.bottom + 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.left - tooltipRect.width - 8;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.right + 8;
                break;
        }
        
        this.tooltip.style.top = `${top}px`;
        this.tooltip.style.left = `${left}px`;
        this.tooltip.classList.remove('opacity-0');
        this.tooltip.classList.add('opacity-100');
    }

    hide() {
        this.tooltip.classList.remove('opacity-100');
        this.tooltip.classList.add('opacity-0');
    }
}

// ===== Loading Spinner =====
class LoadingSpinner {
    static show(container = document.body) {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-modal';
        spinner.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl">
                <i class="fas fa-spinner fa-spin text-4xl text-primary"></i>
                <p class="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
            </div>
        `;
        container.appendChild(spinner);
        return spinner;
    }

    static hide(spinner) {
        if (spinner && spinner.parentNode) {
            spinner.remove();
        }
    }
}

// Export components
window.UIComponents = {
    Button,
    Input,
    Select,
    Card,
    Modal,
    DataTable,
    Badge,
    Tabs,
    Tooltip,
    LoadingSpinner
};

// Initialize tooltips on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    Tooltip.init();
});