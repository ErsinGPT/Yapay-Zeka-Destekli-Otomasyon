/**
 * Betsan CRM - Sidebar Component
 */

const Sidebar = {
    isCollapsed: false,
    isMobileOpen: false,

    /**
     * Render sidebar HTML
     */
    render() {
        const user = Auth.getUser();

        return `
            <aside class="sidebar" id="sidebar">
                <div class="sidebar-header">
                    <div class="sidebar-logo">
                        <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                            <rect width="36" height="36" rx="8" fill="#3498DB"/>
                            <text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" fill="white" font-size="16" font-weight="bold">B</text>
                        </svg>
                        <span>Betsan CRM</span>
                    </div>
                </div>
                
                <nav class="sidebar-nav">
                    <div class="nav-section">
                        <div class="nav-section-title">Ana Menü</div>
                        <div class="nav-item active" data-page="dashboard">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="3" y="3" width="7" height="7"></rect>
                                    <rect x="14" y="3" width="7" height="7"></rect>
                                    <rect x="14" y="14" width="7" height="7"></rect>
                                    <rect x="3" y="14" width="7" height="7"></rect>
                                </svg>
                            </span>
                            <span class="nav-item-text">Dashboard</span>
                        </div>
                    </div>
                    
                    <div class="nav-section">
                        <div class="nav-section-title">CRM</div>
                        <div class="nav-item" data-page="customers">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                                    <circle cx="9" cy="7" r="4"></circle>
                                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                                </svg>
                            </span>
                            <span class="nav-item-text">Müşteriler</span>
                        </div>
                        <div class="nav-item" data-page="opportunities">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                                </svg>
                            </span>
                            <span class="nav-item-text">Fırsatlar</span>
                            <span class="nav-item-badge">5</span>
                        </div>
                        <div class="nav-item" data-page="projects">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                                </svg>
                            </span>
                            <span class="nav-item-text">Projeler</span>
                        </div>
                    </div>
                    
                    <div class="nav-section">
                        <div class="nav-section-title">Stok & Depo</div>
                        <div class="nav-item" data-page="products">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                                </svg>
                            </span>
                            <span class="nav-item-text">Ürünler</span>
                        </div>
                        <div class="nav-item" data-page="warehouses">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                                </svg>
                            </span>
                            <span class="nav-item-text">Depolar</span>
                        </div>
                        <div class="nav-item" data-page="stock-movements">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="17 1 21 5 17 9"></polyline>
                                    <path d="M3 11V9a4 4 0 0 1 4-4h14"></path>
                                    <polyline points="7 23 3 19 7 15"></polyline>
                                    <path d="M21 13v2a4 4 0 0 1-4 4H3"></path>
                                </svg>
                            </span>
                            <span class="nav-item-text">Stok Hareketleri</span>
                        </div>
                    </div>
                    
                    <div class="nav-section">
                        <div class="nav-section-title">Operasyon</div>
                        <div class="nav-item" data-page="service-forms">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                                </svg>
                            </span>
                            <span class="nav-item-text">Servis Formları</span>
                        </div>
                        <div class="nav-item" data-page="transfers">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="1" y="3" width="15" height="13"></rect>
                                    <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                                    <circle cx="5.5" cy="18.5" r="2.5"></circle>
                                    <circle cx="18.5" cy="18.5" r="2.5"></circle>
                                </svg>
                            </span>
                            <span class="nav-item-text">Transferler</span>
                        </div>
                    </div>
                    
                    <div class="nav-section">
                        <div class="nav-section-title">Finans</div>
                        <div class="nav-item" data-page="invoices">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                    <polyline points="14 2 14 8 20 8"></polyline>
                                    <line x1="16" y1="13" x2="8" y2="13"></line>
                                    <line x1="16" y1="17" x2="8" y2="17"></line>
                                    <polyline points="10 9 9 9 8 9"></polyline>
                                </svg>
                            </span>
                            <span class="nav-item-text">Faturalar</span>
                        </div>
                        <div class="nav-item" data-page="expenses">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                                    <line x1="1" y1="10" x2="23" y2="10"></line>
                                </svg>
                            </span>
                            <span class="nav-item-text">Masraflar</span>
                            <span class="nav-item-badge">3</span>
                        </div>
                    </div>
                    
                    <div class="nav-section">
                        <div class="nav-section-title">Raporlar</div>
                        <div class="nav-item" data-page="reports">
                            <span class="nav-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="18" y1="20" x2="18" y2="10"></line>
                                    <line x1="12" y1="20" x2="12" y2="4"></line>
                                    <line x1="6" y1="20" x2="6" y2="14"></line>
                                </svg>
                            </span>
                            <span class="nav-item-text">Raporlar</span>
                        </div>
                    </div>
                </nav>
                
                <div class="sidebar-footer">
                    <div class="nav-item" data-page="settings">
                        <span class="nav-item-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"></circle>
                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                            </svg>
                        </span>
                        <span class="nav-item-text">Ayarlar</span>
                    </div>
                </div>
            </aside>
        `;
    },

    /**
     * Initialize sidebar events
     */
    init() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        // Navigation click handlers
        const navItems = sidebar.querySelectorAll('.nav-item[data-page]');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;

                // Map page names to actual URLs
                const pageUrls = {
                    'dashboard': '/index.html',
                    'customers': '/pages/customers.html',
                    'opportunities': '/pages/opportunities.html',
                    'projects': '/pages/projects.html',
                    'products': '/pages/products.html',
                    'warehouses': '/pages/warehouses.html',
                    'stock-movements': '/pages/stock-movements.html',
                    'service-forms': '/pages/service-forms.html',
                    'transfers': '/pages/transfers.html',
                    'invoices': '/pages/invoices.html',
                    'expenses': '/pages/expenses.html',
                    'reports': '/pages/reports.html',
                    'settings': '/pages/settings.html'
                };

                if (pageUrls[page]) {
                    window.location.href = pageUrls[page];
                } else {
                    console.log('Page not implemented:', page);
                    alert('Bu sayfa henüz hazır değil.');
                }

                // Close mobile sidebar
                this.close();
            });
        });
    },

    /**
     * Toggle sidebar collapse
     */
    toggle() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        this.isCollapsed = !this.isCollapsed;
        sidebar.classList.toggle('collapsed', this.isCollapsed);
    },

    /**
     * Open mobile sidebar
     */
    open() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        this.isMobileOpen = true;
        sidebar.classList.add('mobile-open');
    },

    /**
     * Close mobile sidebar
     */
    close() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        this.isMobileOpen = false;
        sidebar.classList.remove('mobile-open');
    }
};

// Export for use
window.Sidebar = Sidebar;
