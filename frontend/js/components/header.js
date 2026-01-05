/**
 * Betsan CRM - Header Component
 */

const Header = {
    render() {
        const user = Auth.getUser();
        const initials = Utils.getInitials(user?.email || 'User');

        return `
            <header class="header">
                <div class="header-left">
                    <button class="header-toggle" onclick="Sidebar.open()" title="Menü">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="3" y1="12" x2="21" y2="12"></line>
                            <line x1="3" y1="6" x2="21" y2="6"></line>
                            <line x1="3" y1="18" x2="21" y2="18"></line>
                        </svg>
                    </button>
                    <nav class="breadcrumb">
                        <span class="breadcrumb-item">Betsan CRM</span>
                        <span class="breadcrumb-separator">/</span>
                        <span class="breadcrumb-item active">Dashboard</span>
                    </nav>
                </div>
                
                <div class="header-search">
                    <input type="text" class="form-input search-input" placeholder="Ara...">
                </div>
                
                <div class="header-right">
                    <button class="header-icon-btn" title="Bildirimler">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                        </svg>
                    </button>
                    <div class="user-menu" id="user-dropdown">
                        <div class="avatar">${initials}</div>
                        <div class="user-info">
                            <span class="user-name">${user?.email || 'Kullanıcı'}</span>
                        </div>
                    </div>
                </div>
            </header>
        `;
    },

    init() {
        const dropdown = document.getElementById('user-dropdown');
        if (dropdown) {
            dropdown.addEventListener('click', () => Auth.logout());
        }
    }
};

window.Header = Header;
