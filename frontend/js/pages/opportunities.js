/**
 * Otomasyon CRM - Opportunities Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let opportunities = [];
let customers = [];

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
 * Müşterileri yükle
 */
async function loadCustomers() {
    try {
        customers = await API.get('/customers');
    } catch (error) {
        console.error('Failed to load customers:', error);
    }
}

/**
 * Fırsatları yükle
 */
async function loadOpportunities() {
    const container = document.getElementById('table-container');

    try {
        const statusFilter = document.getElementById('status-filter').value;
        let params = {};
        if (statusFilter) params.status = statusFilter;

        opportunities = await API.get('/opportunities', params);
        renderTable(opportunities);
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
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '⭐'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Henüz fırsat yok'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, 'Yeni fırsat ekleyerek başlayın'));

        const addBtn = Utils.createElement('button', {
            class: 'btn btn-primary',
            style: 'margin-top: var(--spacing-md);'
        }, 'Yeni Fırsat Ekle');
        addBtn.addEventListener('click', openCreateModal);
        emptyDiv.appendChild(addBtn);

        container.appendChild(emptyDiv);
        return;
    }

    // Tablo oluştur
    const table = Utils.createElement('table', { class: 'data-table' });

    // Thead
    const thead = Utils.createElement('thead');
    const headerRow = Utils.createElement('tr');
    ['Fırsat', 'Müşteri', 'Beklenen Gelir', 'Olasılık', 'Durum'].forEach(text => {
        headerRow.appendChild(Utils.createElement('th', {}, text));
    });
    const actionTh = Utils.createElement('th', { style: 'text-align: right;' }, 'İşlemler');
    headerRow.appendChild(actionTh);
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Tbody
    const tbody = Utils.createElement('tbody');

    data.forEach(opp => {
        const tr = Utils.createElement('tr');

        // Fırsat adı + açıklama
        const titleTd = Utils.createElement('td');
        titleTd.appendChild(Utils.createElement('strong', {}, opp.title));
        if (opp.description) {
            titleTd.appendChild(Utils.createElement('div', {
                style: 'font-size: var(--font-size-xs); color: var(--text-muted);'
            }, Utils.truncate(opp.description, 40)));
        }
        tr.appendChild(titleTd);

        // Müşteri
        tr.appendChild(Utils.createElement('td', {}, opp.customer_name || '-'));

        // Beklenen gelir
        const revenueTd = Utils.createElement('td');
        revenueTd.textContent = opp.expected_revenue
            ? Utils.formatCurrency(opp.expected_revenue, opp.currency)
            : '-';
        tr.appendChild(revenueTd);

        // Olasılık bar
        const probTd = Utils.createElement('td');
        const probWrapper = Utils.createElement('div', {
            style: 'display: flex; align-items: center; gap: var(--spacing-xs);'
        });
        const barContainer = Utils.createElement('div', {
            style: 'flex: 1; height: 6px; background: var(--gray-200); border-radius: 3px; max-width: 60px;'
        });
        const barFill = Utils.createElement('div', {
            style: `width: ${opp.probability}%; height: 100%; background: var(--secondary); border-radius: 3px;`
        });
        barContainer.appendChild(barFill);
        probWrapper.appendChild(barContainer);
        probWrapper.appendChild(Utils.createElement('span', {
            style: 'font-size: var(--font-size-xs);'
        }, `${opp.probability}%`));
        probTd.appendChild(probWrapper);
        tr.appendChild(probTd);

        // Durum badge
        const statusTd = Utils.createElement('td');
        const badge = Utils.createElement('span', {
            class: `status-badge ${statusColors[opp.status] || 'info'}`
        }, statusLabels[opp.status] || opp.status);
        statusTd.appendChild(badge);
        tr.appendChild(statusTd);

        // İşlemler
        const actionTd = Utils.createElement('td', { style: 'text-align: right;' });

        if (opp.status !== 'WON' && opp.status !== 'LOST') {
            const wonBtn = Utils.createElement('button', {
                class: 'btn btn-success btn-sm',
                title: 'Kazanıldı'
            }, '✓');
            wonBtn.addEventListener('click', () => markWon(opp.id));
            actionTd.appendChild(wonBtn);

            const lostBtn = Utils.createElement('button', {
                class: 'btn btn-danger btn-sm',
                title: 'Kaybedildi'
            }, '✗');
            lostBtn.addEventListener('click', () => markLost(opp.id));
            actionTd.appendChild(lostBtn);
        }

        const editBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'Düzenle');
        editBtn.addEventListener('click', () => editOpportunity(opp.id));
        actionTd.appendChild(editBtn);

        const deleteBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm', style: 'color: var(--danger);' }, 'Sil');
        deleteBtn.addEventListener('click', () => deleteOpportunity(opp.id, opp.title, opp.status, opp.project_id));
        actionTd.appendChild(deleteBtn);

        tr.appendChild(actionTd);
        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Yeni fırsat modal'ı
 */
function openCreateModal() {
    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    const modal = Utils.createElement('div', {
        class: 'modal-content',
        style: 'max-width: 500px;'
    });
    modal.addEventListener('click', (e) => e.stopPropagation());

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Yeni Fırsat'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', createOpportunity);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Fırsat Adı
    const titleGroup = Utils.createElement('div', { class: 'form-group' });
    titleGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Fırsat Adı'));
    const titleInput = Utils.createElement('input', { type: 'text', class: 'form-input', name: 'title' });
    titleInput.setAttribute('required', '');
    titleGroup.appendChild(titleInput);
    body.appendChild(titleGroup);

    // Müşteri Select
    const customerGroup = Utils.createElement('div', { class: 'form-group' });
    customerGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Müşteri'));
    const customerSelect = Utils.createElement('select', { class: 'form-select', name: 'customer_id' });
    customerSelect.setAttribute('required', '');
    customerSelect.appendChild(Utils.createElement('option', { value: '' }, 'Müşteri seçin'));
    customers.forEach(c => {
        customerSelect.appendChild(Utils.createElement('option', { value: c.id }, c.name));
    });
    customerGroup.appendChild(customerSelect);
    body.appendChild(customerGroup);

    // Beklenen Gelir
    const revenueGroup = Utils.createElement('div', { class: 'form-group' });
    revenueGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Beklenen Gelir'));
    revenueGroup.appendChild(Utils.createElement('input', {
        type: 'number', class: 'form-input', name: 'expected_revenue', step: '0.01'
    }));
    body.appendChild(revenueGroup);

    // Para Birimi
    const currencyGroup = Utils.createElement('div', { class: 'form-group' });
    currencyGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Para Birimi'));
    const currencySelect = Utils.createElement('select', { class: 'form-select', name: 'currency' });
    ['TRY', 'USD', 'EUR'].forEach(cur => {
        currencySelect.appendChild(Utils.createElement('option', { value: cur }, cur));
    });
    currencyGroup.appendChild(currencySelect);
    body.appendChild(currencyGroup);

    // Olasılık
    const probGroup = Utils.createElement('div', { class: 'form-group' });
    probGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Olasılık (%)'));
    const probInput = Utils.createElement('input', {
        type: 'number', class: 'form-input', name: 'probability',
        min: '0', max: '100', value: '50'
    });
    probGroup.appendChild(probInput);
    body.appendChild(probGroup);

    // Açıklama
    const descGroup = Utils.createElement('div', { class: 'form-group' });
    descGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Açıklama'));
    descGroup.appendChild(Utils.createElement('textarea', {
        class: 'form-textarea', name: 'description', rows: '2'
    }));
    body.appendChild(descGroup);

    form.appendChild(body);

    // Footer
    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const cancelBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'İptal');
    cancelBtn.addEventListener('click', closeModal);
    footer.appendChild(cancelBtn);
    footer.appendChild(Utils.createElement('button', { type: 'submit', class: 'btn btn-primary' }, 'Kaydet'));
    form.appendChild(footer);

    modal.appendChild(form);
    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

function closeModal() {
    document.getElementById('modal-container').innerHTML = '';
    document.body.style.overflow = '';
}

async function createOpportunity(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) {
            if (key === 'customer_id' || key === 'probability') {
                data[key] = parseInt(value);
            } else if (key === 'expected_revenue') {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }
    });

    try {
        await API.post('/opportunities', data);
        closeModal();
        alert('Fırsat oluşturuldu');
        loadOpportunities();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

async function markWon(id) {
    if (!confirm('Bu fırsatı "Kazanıldı" olarak işaretlemek istiyor musunuz? Otomatik proje oluşturulacak.')) return;

    try {
        const project = await API.post(`/opportunities/${id}/won`);
        alert(`Tebrikler! Proje oluşturuldu: ${project.project_code}`);
        loadOpportunities();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

async function markLost(id) {
    if (!confirm('Bu fırsatı "Kaybedildi" olarak işaretlemek istiyor musunuz?')) return;

    try {
        await API.post(`/opportunities/${id}/lost`);
        alert('Fırsat kaybedildi olarak işaretlendi');
        loadOpportunities();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

function editOpportunity(id) {
    const opp = opportunities.find(o => o.id === id);
    if (!opp) return;

    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    const modal = Utils.createElement('div', {
        class: 'modal-content',
        style: 'max-width: 500px;'
    });
    modal.addEventListener('click', (e) => e.stopPropagation());

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Fırsat Düzenle'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', (e) => updateOpportunity(e, id));

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Fırsat Adı
    const titleGroup = Utils.createElement('div', { class: 'form-group' });
    titleGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Fırsat Adı'));
    const titleInput = Utils.createElement('input', {
        type: 'text', class: 'form-input', name: 'title', value: opp.title
    });
    titleInput.setAttribute('required', '');
    titleGroup.appendChild(titleInput);
    body.appendChild(titleGroup);

    // Beklenen Gelir
    const revenueGroup = Utils.createElement('div', { class: 'form-group' });
    revenueGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Beklenen Gelir'));
    revenueGroup.appendChild(Utils.createElement('input', {
        type: 'number', class: 'form-input', name: 'expected_revenue',
        step: '0.01', value: opp.expected_revenue || ''
    }));
    body.appendChild(revenueGroup);

    // Durum
    const statusGroup = Utils.createElement('div', { class: 'form-group' });
    statusGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Durum'));
    const statusSelect = Utils.createElement('select', { class: 'form-select', name: 'status' });
    if (opp.status === 'WON' || opp.status === 'LOST') {
        statusSelect.setAttribute('disabled', '');
    }
    Object.entries(statusLabels)
        .filter(([key]) => key !== 'WON' && key !== 'LOST')
        .forEach(([key, label]) => {
            const option = Utils.createElement('option', { value: key }, label);
            if (opp.status === key) option.setAttribute('selected', '');
            statusSelect.appendChild(option);
        });
    statusGroup.appendChild(statusSelect);

    // Uyarı mesajı
    const warningText = opp.status === 'WON' || opp.status === 'LOST'
        ? '⚠️ Kazanıldı/Kaybedildi durumları değiştirilemez'
        : '💡 Kazanıldı/Kaybedildi için tablodaki özel butonları kullanın';
    const warning = Utils.createElement('small', {
        style: 'color: var(--text-muted); margin-top: 4px; display: block;'
    }, warningText);
    statusGroup.appendChild(warning);
    body.appendChild(statusGroup);

    // Olasılık
    const probGroup = Utils.createElement('div', { class: 'form-group' });
    probGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Olasılık (%)'));
    probGroup.appendChild(Utils.createElement('input', {
        type: 'number', class: 'form-input', name: 'probability',
        min: '0', max: '100', value: opp.probability
    }));
    body.appendChild(probGroup);

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

async function updateOpportunity(event, id) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) {
            if (key === 'probability') {
                data[key] = parseInt(value);
            } else if (key === 'expected_revenue') {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }
    });

    try {
        await API.put(`/opportunities/${id}`, data);
        closeModal();
        alert('Fırsat güncellendi');
        loadOpportunities();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

/**
 * Fırsat sil
 */
async function deleteOpportunity(id, title, status, projectId) {
    // Kazanılan veya kaybedilen fırsatlar için ekstra onay
    if (status === 'WON' || status === 'LOST') {
        const statusLabel = status === 'WON' ? 'KAZANILMIŞ' : 'KAYBEDILMIŞ';
        const extraWarning = status === 'WON' && projectId
            ? '\n\n⚠️ UYARI: Bu fırsat bir projeye dönüştürülmüştür! Silindiğinde ilgili proje de silinecektir!'
            : '';

        if (!confirm(`⚠️ DİKKAT! Bu fırsat "${statusLabel}" durumundadır.${extraWarning}\n\n"${title}" fırsatını silmek istediğinize EMiN misiniz?`)) return;

        // İkinci onay
        if (!confirm(`SON ONAY: "${title}" fırsatını ve ilişkili tüm verileri silmek istediğinizi tekrar onaylıyor musunuz?`)) return;
    } else {
        if (!confirm(`"${title}" fırsatını silmek istediğinize emin misiniz?`)) return;
    }

    try {
        await API.delete(`/opportunities/${id}`);
        alert('Fırsat silindi');
        loadOpportunities();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

// Global fonksiyonlar
window.openCreateModal = openCreateModal;
window.closeModal = closeModal;
window.loadOpportunities = loadOpportunities;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }
    loadCustomers();
    loadOpportunities();
});
