/**
 * Otomasyon CRM - Dashboard Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

// Status label tanımları
const statusLabels = {
    'NEW': 'Yeni',
    'CONTACTED': 'İletişime Geçildi',
    'QUALIFIED': 'Nitelikli',
    'PROPOSAL': 'Teklif Verildi',
    'NEGOTIATION': 'Müzakere',
    'WON': 'Kazanıldı',
    'LOST': 'Kaybedildi'
};

const statusColors = {
    'NEW': 'info',
    'CONTACTED': 'info',
    'QUALIFIED': 'warning',
    'PROPOSAL': 'warning',
    'NEGOTIATION': 'warning',
    'WON': 'success',
    'LOST': 'danger'
};

/**
 * Dashboard verilerini yükle
 */
async function loadDashboardData() {
    try {
        // Load customers count
        const customers = await API.get('/customers');
        document.getElementById('stat-customers').textContent = customers.length;

        // Load opportunities
        const opportunities = await API.get('/opportunities');
        const activeOpps = opportunities.filter(o => !['WON', 'LOST'].includes(o.status));
        document.getElementById('stat-opportunities').textContent = activeOpps.length;

        // Calculate expected revenue
        const totalRevenue = activeOpps.reduce((sum, o) => sum + (o.expected_revenue || 0), 0);
        document.getElementById('stat-revenue').textContent = Utils.formatCurrency(totalRevenue, 'TRY');

        // Load projects
        const projects = await API.get('/projects');
        const activeProjects = projects.filter(p => !['COMPLETED', 'INVOICED'].includes(p.status));
        document.getElementById('stat-projects').textContent = activeProjects.length;

        // Render recent opportunities
        renderRecentOpportunities(opportunities.slice(0, 5));

    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        document.getElementById('stat-customers').textContent = '0';
        document.getElementById('stat-opportunities').textContent = '0';
        document.getElementById('stat-projects').textContent = '0';
        document.getElementById('stat-revenue').textContent = '₺0';

        const recentContainer = document.getElementById('recent-opportunities');
        recentContainer.innerHTML = '';
        const errorDiv = Utils.createElement('div', {
            style: 'padding: var(--spacing-lg); text-align: center; color: var(--text-muted);'
        }, 'Veri yüklenemedi');
        recentContainer.appendChild(errorDiv);
    }
}

/**
 * Son fırsatları güvenli şekilde render et
 */
function renderRecentOpportunities(opportunities) {
    const container = document.getElementById('recent-opportunities');
    container.innerHTML = '';

    if (opportunities.length === 0) {
        const emptyDiv = Utils.createElement('div', {
            style: 'padding: var(--spacing-lg); text-align: center; color: var(--text-muted);'
        }, 'Henüz fırsat yok');
        container.appendChild(emptyDiv);
        return;
    }

    // Tablo oluştur
    const table = Utils.createElement('table', { class: 'data-table' });

    // Thead
    const thead = Utils.createElement('thead');
    const headerRow = Utils.createElement('tr');
    ['Fırsat', 'Müşteri', 'Değer', 'Durum'].forEach(text => {
        headerRow.appendChild(Utils.createElement('th', {}, text));
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Tbody
    const tbody = Utils.createElement('tbody');

    opportunities.forEach(opp => {
        const tr = Utils.createElement('tr');

        // Fırsat adı
        const titleTd = Utils.createElement('td');
        titleTd.appendChild(Utils.createElement('strong', {}, opp.title));
        tr.appendChild(titleTd);

        // Müşteri
        tr.appendChild(Utils.createElement('td', {}, opp.customer_name || '-'));

        // Değer
        const valueTd = Utils.createElement('td');
        valueTd.textContent = opp.expected_revenue
            ? Utils.formatCurrency(opp.expected_revenue, opp.currency)
            : '-';
        tr.appendChild(valueTd);

        // Durum badge
        const statusTd = Utils.createElement('td');
        const badge = Utils.createElement('span', {
            class: `status-badge ${statusColors[opp.status] || 'info'}`
        }, statusLabels[opp.status] || opp.status);
        statusTd.appendChild(badge);
        tr.appendChild(statusTd);

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Sidebar toggle (mobile)
 */
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('show');
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) overlay.classList.toggle('show');
}

function closeSidebar() {
    document.getElementById('sidebar').classList.remove('show');
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) overlay.classList.remove('show');
}

/**
 * Modal kapat
 */
function closeModal(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('modal-container').innerHTML = '';
}

// Global fonksiyonlar (onclick handler'lar için)
window.toggleSidebar = toggleSidebar;
window.closeSidebar = closeSidebar;
window.closeModal = closeModal;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function () {
    if (!API.getToken()) {
        window.location.href = 'pages/login.html';
        return;
    }
    loadDashboardData();
});
