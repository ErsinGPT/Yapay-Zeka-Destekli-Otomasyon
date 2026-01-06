/**
 * Otomasyon CRM - Projects Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let projects = [];

const statusLabels = {
    'OPPORTUNITY': 'Fırsat',
    'WON': 'Kazanıldı',
    'ENGINEERING': 'Mühendislik',
    'PROCUREMENT': 'Tedarik',
    'ASSEMBLY': 'Montaj',
    'TESTING': 'Test',
    'SHIPPING': 'Sevkiyat',
    'COMMISSIONING': 'Devreye Alma',
    'COMPLETED': 'Tamamlandı',
    'INVOICED': 'Faturalandı'
};

const statusColors = {
    'OPPORTUNITY': 'info',
    'WON': 'success',
    'ENGINEERING': 'warning',
    'PROCUREMENT': 'warning',
    'ASSEMBLY': 'warning',
    'TESTING': 'warning',
    'SHIPPING': 'info',
    'COMMISSIONING': 'info',
    'COMPLETED': 'success',
    'INVOICED': 'success'
};

const statusOrder = ['OPPORTUNITY', 'WON', 'ENGINEERING', 'PROCUREMENT', 'ASSEMBLY', 'TESTING', 'SHIPPING', 'COMMISSIONING', 'COMPLETED', 'INVOICED'];

/**
 * Projeleri yükle
 */
async function loadProjects() {
    const container = document.getElementById('table-container');

    try {
        const search = document.getElementById('search-input').value;
        const statusFilter = document.getElementById('status-filter').value;

        let params = {};
        if (search) params.search = search;
        if (statusFilter) params.status = statusFilter;

        projects = await API.get('/projects', params);
        renderTable(projects);
    } catch (error) {
        container.innerHTML = '';
        const errorDiv = Utils.createElement('div', { class: 'empty-state' });
        errorDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '⚠️'));
        errorDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Yüklenemedi'));
        errorDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, error.message));
        container.appendChild(errorDiv);
    }
}

/**
 * Tabloyu güvenli şekilde render et
 */
function renderTable(data) {
    const container = document.getElementById('table-container');
    container.innerHTML = '';

    if (data.length === 0) {
        const emptyDiv = Utils.createElement('div', { class: 'empty-state' });
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '📁'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Henüz proje yok'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, 'Projeler, fırsatlar "Kazanıldı" olarak işaretlendiğinde otomatik oluşturulur'));

        const link = Utils.createElement('a', {
            href: 'opportunities.html',
            class: 'btn btn-primary',
            style: 'margin-top: var(--spacing-md);'
        }, 'Fırsatlara Git');
        emptyDiv.appendChild(link);

        container.appendChild(emptyDiv);
        return;
    }

    // Tablo oluştur
    const table = Utils.createElement('table', { class: 'data-table' });

    // Thead
    const thead = Utils.createElement('thead');
    const headerRow = Utils.createElement('tr');
    ['Proje Kodu', 'Proje Adı', 'Müşteri', 'Sözleşme Tutarı', 'Durum'].forEach(text => {
        headerRow.appendChild(Utils.createElement('th', {}, text));
    });
    const actionTh = Utils.createElement('th', { style: 'text-align: right;' }, 'İşlemler');
    headerRow.appendChild(actionTh);
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Tbody
    const tbody = Utils.createElement('tbody');

    data.forEach(project => {
        const tr = Utils.createElement('tr');

        // Proje kodu
        const codeTd = Utils.createElement('td');
        codeTd.appendChild(Utils.createElement('strong', {}, project.project_code));
        tr.appendChild(codeTd);

        // Proje adı
        tr.appendChild(Utils.createElement('td', {}, project.title));

        // Müşteri
        tr.appendChild(Utils.createElement('td', {}, project.customer_name || '-'));

        // Sözleşme tutarı
        const amountTd = Utils.createElement('td');
        amountTd.textContent = project.contract_amount
            ? Utils.formatCurrency(project.contract_amount, project.currency)
            : '-';
        tr.appendChild(amountTd);

        // Durum badge
        const statusTd = Utils.createElement('td');
        const badge = Utils.createElement('span', {
            class: `status-badge ${statusColors[project.status] || 'info'}`
        }, statusLabels[project.status] || project.status);
        statusTd.appendChild(badge);
        tr.appendChild(statusTd);

        // İşlemler
        const actionTd = Utils.createElement('td', { style: 'text-align: right;' });

        const viewBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'Görüntüle');
        viewBtn.addEventListener('click', () => viewProject(project.id));
        actionTd.appendChild(viewBtn);

        const statusBtn = Utils.createElement('button', { class: 'btn btn-outline btn-sm' }, 'Durum');
        statusBtn.addEventListener('click', () => changeStatus(project.id));
        actionTd.appendChild(statusBtn);

        tr.appendChild(actionTd);
        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Proje detaylarını görüntüle
 */
function viewProject(id) {
    const project = projects.find(p => p.id === id);
    if (!project) return;

    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    const modal = Utils.createElement('div', {
        class: 'modal-content',
        style: 'max-width: 600px;'
    });
    modal.addEventListener('click', (e) => e.stopPropagation());

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, project.project_code));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Body
    const body = Utils.createElement('div', { class: 'modal-body' });

    // Proje başlığı
    body.appendChild(Utils.createElement('h4', { style: 'margin-bottom: var(--spacing-md);' }, project.title));

    // Bilgi grid
    const grid = Utils.createElement('div', {
        style: 'display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--spacing-md);'
    });

    // Müşteri
    const customerInfo = Utils.createElement('div');
    customerInfo.appendChild(Utils.createElement('div', {
        style: 'font-size: var(--font-size-xs); color: var(--text-muted);'
    }, 'Müşteri'));
    customerInfo.appendChild(Utils.createElement('div', {
        style: 'font-weight: var(--font-weight-medium);'
    }, project.customer_name || '-'));
    grid.appendChild(customerInfo);

    // Sözleşme tutarı
    const amountInfo = Utils.createElement('div');
    amountInfo.appendChild(Utils.createElement('div', {
        style: 'font-size: var(--font-size-xs); color: var(--text-muted);'
    }, 'Sözleşme Tutarı'));
    amountInfo.appendChild(Utils.createElement('div', {
        style: 'font-weight: var(--font-weight-medium);'
    }, project.contract_amount ? Utils.formatCurrency(project.contract_amount, project.currency) : '-'));
    grid.appendChild(amountInfo);

    // Durum
    const statusInfo = Utils.createElement('div');
    statusInfo.appendChild(Utils.createElement('div', {
        style: 'font-size: var(--font-size-xs); color: var(--text-muted);'
    }, 'Durum'));
    const badge = Utils.createElement('span', {
        class: `status-badge ${statusColors[project.status]}`
    }, statusLabels[project.status]);
    statusInfo.appendChild(badge);
    grid.appendChild(statusInfo);

    // Başlangıç tarihi
    const dateInfo = Utils.createElement('div');
    dateInfo.appendChild(Utils.createElement('div', {
        style: 'font-size: var(--font-size-xs); color: var(--text-muted);'
    }, 'Başlangıç'));
    dateInfo.appendChild(Utils.createElement('div', {},
        project.start_date ? Utils.formatDate(project.start_date) : '-'
    ));
    grid.appendChild(dateInfo);

    body.appendChild(grid);

    // Progress bar
    const progressSection = Utils.createElement('div', { style: 'margin-top: var(--spacing-lg);' });
    progressSection.appendChild(Utils.createElement('div', {
        style: 'font-size: var(--font-size-xs); color: var(--text-muted); margin-bottom: var(--spacing-sm);'
    }, 'Proje İlerlemesi'));

    const progressBar = Utils.createElement('div', { style: 'display: flex; gap: 2px;' });
    const currentIndex = statusOrder.indexOf(project.status);

    statusOrder.slice(1).forEach((status, idx) => {
        const segment = Utils.createElement('div', {
            style: `flex: 1; height: 8px; border-radius: 4px; background: ${currentIndex >= idx + 1 ? 'var(--success)' : 'var(--gray-200)'}`
        });
        progressBar.appendChild(segment);
    });
    progressSection.appendChild(progressBar);
    body.appendChild(progressSection);

    // Açıklama
    if (project.description) {
        const descSection = Utils.createElement('div', { style: 'margin-top: var(--spacing-lg);' });
        descSection.appendChild(Utils.createElement('div', {
            style: 'font-size: var(--font-size-xs); color: var(--text-muted);'
        }, 'Açıklama'));
        descSection.appendChild(Utils.createElement('div', {}, project.description));
        body.appendChild(descSection);
    }

    modal.appendChild(body);

    // Footer
    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const closeFooterBtn = Utils.createElement('button', { class: 'btn btn-ghost' }, 'Kapat');
    closeFooterBtn.addEventListener('click', closeModal);
    footer.appendChild(closeFooterBtn);

    const changeStatusBtn = Utils.createElement('button', { class: 'btn btn-primary' }, 'Durum Değiştir');
    changeStatusBtn.addEventListener('click', () => {
        closeModal();
        changeStatus(project.id);
    });
    footer.appendChild(changeStatusBtn);
    modal.appendChild(footer);

    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

/**
 * Durum değiştirme modal'ı
 */
function changeStatus(id) {
    const project = projects.find(p => p.id === id);
    if (!project) return;

    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    const modal = Utils.createElement('div', {
        class: 'modal-content',
        style: 'max-width: 400px;'
    });
    modal.addEventListener('click', (e) => e.stopPropagation());

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Durum Değiştir'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', (e) => updateStatus(e, id));

    const body = Utils.createElement('div', { class: 'modal-body' });
    body.appendChild(Utils.createElement('p', { style: 'margin-bottom: var(--spacing-md);' }));
    body.querySelector('p').appendChild(Utils.createElement('strong', {}, project.project_code));

    const statusGroup = Utils.createElement('div', { class: 'form-group' });
    statusGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Yeni Durum'));

    const statusSelect = Utils.createElement('select', { class: 'form-select', name: 'status' });
    statusSelect.setAttribute('required', '');
    statusOrder.slice(1).forEach(status => {
        const option = Utils.createElement('option', { value: status }, statusLabels[status]);
        if (project.status === status) option.setAttribute('selected', '');
        statusSelect.appendChild(option);
    });
    statusGroup.appendChild(statusSelect);
    body.appendChild(statusGroup);

    form.appendChild(body);

    // Footer
    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const cancelBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'İptal');
    cancelBtn.addEventListener('click', closeModal);
    footer.appendChild(cancelBtn);
    footer.appendChild(Utils.createElement('button', { type: 'submit', class: 'btn btn-primary' }, 'Güncelle'));
    form.appendChild(footer);

    modal.appendChild(form);
    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

function closeModal() {
    document.getElementById('modal-container').innerHTML = '';
    document.body.style.overflow = '';
}

async function updateStatus(event, id) {
    event.preventDefault();
    const form = event.target;
    const status = form.status.value;

    try {
        await API.put(`/projects/${id}/status`, { status });
        closeModal();
        alert('Proje durumu güncellendi');
        loadProjects();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

// Global fonksiyonlar
window.closeModal = closeModal;
window.loadProjects = loadProjects;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }
    loadProjects();

    // Enter key search
    document.getElementById('search-input').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') loadProjects();
    });
});
