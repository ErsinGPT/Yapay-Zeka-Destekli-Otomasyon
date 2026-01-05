/**
 * Otomasyon CRM - Layout Loader
 * Dinamik olarak Sidebar ve Header bileşenlerini yükler
 */

const LayoutLoader = {
    /**
     * Layout bileşenlerini yükle ve initialize et
     */
    async init() {
        // Auth modülünü initialize et (kullanıcı bilgilerini yükle)
        if (typeof Auth !== 'undefined' && typeof Auth.init === 'function') {
            await Auth.init();
        }

        // Sidebar'ı yükle
        this.loadSidebar();

        // Header'ı yükle
        this.loadHeader();

        // Aktif sayfa menü öğesini işaretle
        this.setActivePage();
    },

    /**
     * Sidebar bileşenini yükle
     */
    loadSidebar() {
        const appLayout = document.querySelector('.app-layout');
        if (!appLayout) {
            console.error('LayoutLoader: .app-layout elementi bulunamadı');
            return;
        }

        // Sidebar HTML'ini render et ve en başa ekle
        const sidebarHtml = Sidebar.render();
        appLayout.insertAdjacentHTML('afterbegin', sidebarHtml);

        // Sidebar overlay ekle (mobil için)
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.onclick = () => Sidebar.close();
        appLayout.insertBefore(overlay, appLayout.querySelector('.main-wrapper'));

        // Sidebar event'lerini initialize et
        Sidebar.init();
    },

    /**
     * Header bileşenini yükle
     */
    loadHeader() {
        const mainWrapper = document.querySelector('.main-wrapper');
        if (!mainWrapper) {
            console.error('LayoutLoader: .main-wrapper elementi bulunamadı');
            return;
        }

        // Header HTML'ini render et ve main-wrapper'ın en başına ekle
        const headerHtml = Header.render();
        mainWrapper.insertAdjacentHTML('afterbegin', headerHtml);

        // Header event'lerini initialize et (eğer varsa)
        if (typeof Header.init === 'function') {
            Header.init();
        }
    },

    /**
     * Aktif sayfayı sidebar'da işaretle
     */
    setActivePage() {
        // body'deki data-page attribute'unu oku
        const currentPage = document.body.dataset.page;
        if (!currentPage) {
            console.warn('LayoutLoader: data-page attribute bulunamadı');
            return;
        }

        // Tüm nav-item'lardan active class'ını kaldır
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => item.classList.remove('active'));

        // İlgili nav-item'a active class'ını ekle
        const activeItem = document.querySelector(`.nav-item[data-page="${currentPage}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }
};

// Sayfa yüklendiğinde layout'u yükle
document.addEventListener('DOMContentLoaded', async () => {
    await LayoutLoader.init();
});

// Global erişim için export et
window.LayoutLoader = LayoutLoader;
