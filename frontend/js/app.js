/**
 * Otomasyon CRM - Main Application
 */

const App = {
    currentPage: null,

    /**
     * Initialize application
     */
    async init() {
        console.log('🚀 Betsan CRM Başlatılıyor...');

        // Initialize auth
        await Auth.init();

        // Check authentication for protected pages
        const publicPages = ['/pages/login.html', '/login.html'];
        const currentPath = window.location.pathname;

        if (!publicPages.some(p => currentPath.endsWith(p))) {
            if (!Auth.requireAuth()) {
                return;
            }
        }

        // Render layout if authenticated
        if (Auth.isAuthenticated()) {
            this.renderLayout();
        }

        console.log('✅ Betsan CRM Hazır!');
    },

    /**
     * Render main layout
     */
    renderLayout() {
        const app = document.getElementById('app');

        app.innerHTML = `
            <div class="app-layout">
                ${Sidebar.render()}
                <div class="sidebar-overlay" onclick="Sidebar.close()"></div>
                <div class="main-wrapper">
                    ${Header.render()}
                    <main class="main-content" id="main-content">
                        <!-- Page content will be loaded here -->
                    </main>
                </div>
            </div>
        `;

        // Initialize components
        Sidebar.init();
        Header.init();

        // Load current page content
        this.loadPage();
    },

    /**
     * Load page content based on URL
     */
    loadPage() {
        // This will be expanded with actual page loading logic
        const content = document.getElementById('main-content');

        content.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Dashboard</h1>
                    <p class="page-subtitle">Hoş geldiniz, ${Auth.currentUser?.email || 'Kullanıcı'}</p>
                </div>
                <div class="page-actions">
                    <button class="btn btn-primary">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        Yeni Proje
                    </button>
                </div>
            </div>

            <!-- Stat Cards -->
            <div class="stat-cards-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-lg);">
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-title">Aktif Projeler</span>
                        <div class="stat-card-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                            </svg>
                        </div>
                    </div>
                    <div class="stat-card-value">12</div>
                    <span class="stat-card-change positive">+2 bu ay</span>
                </div>
                
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-title">Bekleyen Teklifler</span>
                        <div class="stat-card-icon" style="background: var(--warning-bg); color: var(--warning);">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                            </svg>
                        </div>
                    </div>
                    <div class="stat-card-value">5</div>
                    <span class="stat-card-change">₺1.2M değerinde</span>
                </div>
                
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-title">Aylık Ciro</span>
                        <div class="stat-card-icon" style="background: var(--success-bg); color: var(--success);">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="1" x2="12" y2="23"></line>
                                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                            </svg>
                        </div>
                    </div>
                    <div class="stat-card-value">₺850K</div>
                    <span class="stat-card-change positive">+15% geçen aya göre</span>
                </div>
                
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-title">Düşük Stok Uyarısı</span>
                        <div class="stat-card-icon" style="background: var(--danger-bg); color: var(--danger);">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                                <line x1="12" y1="9" x2="12" y2="13"></line>
                                <line x1="12" y1="17" x2="12.01" y2="17"></line>
                            </svg>
                        </div>
                    </div>
                    <div class="stat-card-value">3</div>
                    <span class="stat-card-change negative">Acil sipariş gerekli</span>
                </div>
            </div>

            <!-- Recent Projects -->
            <div class="content-card">
                <div class="content-card-header">
                    <h3 class="content-card-title">Son Projeler</h3>
                    <button class="btn btn-ghost btn-sm">Tümünü Gör</button>
                </div>
                <div class="content-card-body p-0">
                    <div class="data-table-wrapper">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Proje Kodu</th>
                                    <th>Müşteri</th>
                                    <th>Durum</th>
                                    <th>Tutar</th>
                                    <th class="hide-mobile">Başlangıç</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>PRJ-2026-0012</strong></td>
                                    <td>ABC Fabrika GmbH</td>
                                    <td><span class="status-badge warning">Montaj</span></td>
                                    <td>€50,000</td>
                                    <td class="hide-mobile">15.12.2025</td>
                                </tr>
                                <tr>
                                    <td><strong>PRJ-2026-0011</strong></td>
                                    <td>XYZ Otomasyon A.Ş.</td>
                                    <td><span class="status-badge info">Devreye Alma</span></td>
                                    <td>₺350,000</td>
                                    <td class="hide-mobile">10.12.2025</td>
                                </tr>
                                <tr>
                                    <td><strong>PRJ-2026-0010</strong></td>
                                    <td>Delta Makine Ltd.</td>
                                    <td><span class="status-badge success">Tamamlandı</span></td>
                                    <td>$25,000</td>
                                    <td class="hide-mobile">01.12.2025</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Navigate to a page
     */
    navigate(path) {
        window.location.href = path;
    },

    /**
     * Show loading state
     */
    showLoading() {
        const content = document.getElementById('main-content');
        if (content) {
            content.innerHTML = `
                <div class="loading-screen" style="min-height: 400px;">
                    <div class="spinner"></div>
                    <p>Yükleniyor...</p>
                </div>
            `;
        }
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// Export for use
window.App = App;
