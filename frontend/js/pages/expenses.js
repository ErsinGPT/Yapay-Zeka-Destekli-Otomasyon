/**
 * Otomasyon CRM - Expenses Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let expenses = [];
let projects = [];

const EXPENSE_TYPES = {
    'TRAVEL': 'Yol',
    'ACCOMMODATION': 'Konaklama',
    'FOOD': 'Yemek',
    'TRANSPORT': 'Ulaşım',
    'MATERIAL': 'Malzeme',
    'OTHER': 'Diğer'
};

/**
 * Başlangıç verileri yükle
 */
async function loadInitialData() {
    try {
        projects = await API.projects.getAll();
    } catch (error) {
        console.error('Projeler yüklenemedi:', error);
    }
}

/**
 * Masrafları yükle
 */
async function loadExpenses() {
    const container = document.getElementById('table-container');

    try {
        const expenseType = document.getElementById('type-filter').value;
        const status = document.getElementById('status-filter').value;

        let params = {};
        if (expenseType) params.expense_type = expenseType;
        if (status) params.status = status;

        expenses = await API.expenses.getAll(params);
        renderTable(expenses);
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
 * Tabloyu render et
 */
function renderTable(data) {
    const container = document.getElementById('table-container');
    container.innerHTML = '';

    if (data.length === 0) {
        const emptyDiv = Utils.createElement('div', { class: 'empty-state' });
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '💳'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Henüz masraf yok'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, 'Yeni masraf ekleyerek başlayın'));

        const addBtn = Utils.createElement('button', {
            class: 'btn btn-primary',
            style: 'margin-top: var(--spacing-md);'
        }, 'Yeni Masraf');
        addBtn.addEventListener('click', openCreateModal);
        emptyDiv.appendChild(addBtn);

        container.appendChild(emptyDiv);
        return;
    }

    const table = Utils.createElement('table', { class: 'data-table' });

    // Thead
    const thead = Utils.createElement('thead');
    const headerRow = Utils.createElement('tr');
    ['Tarih', 'Tip', 'Açıklama', 'Proje', 'Tutar', 'Durum', 'İşlemler'].forEach(text => {
        headerRow.appendChild(Utils.createElement('th', {}, text));
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Tbody
    const tbody = Utils.createElement('tbody');

    data.forEach(expense => {
        const tr = Utils.createElement('tr');

        // Tarih
        const date = expense.expense_date ? new Date(expense.expense_date).toLocaleDateString('tr-TR') : '-';
        tr.appendChild(Utils.createElement('td', {}, date));

        // Tip
        tr.appendChild(Utils.createElement('td', {}, EXPENSE_TYPES[expense.expense_type] || expense.expense_type));

        // Açıklama
        const descTd = Utils.createElement('td');
        descTd.appendChild(Utils.createElement('div', {
            style: 'max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'
        }, expense.description || '-'));
        tr.appendChild(descTd);

        // Proje
        tr.appendChild(Utils.createElement('td', {}, expense.project_code || '-'));

        // Tutar
        const amount = parseFloat(expense.amount || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2 });
        tr.appendChild(Utils.createElement('td', {}, `${amount} ${expense.currency || 'TRY'}`));

        // Durum
        const statusTd = Utils.createElement('td');
        const statusMap = {
            'PENDING': { label: 'Bekliyor', class: 'warning' },
            'APPROVED': { label: 'Onaylandı', class: 'success' },
            'REJECTED': { label: 'Reddedildi', class: 'danger' }
        };
        const statusInfo = statusMap[expense.status] || { label: expense.status, class: 'default' };
        const statusBadge = Utils.createElement('span', {
            class: `status-badge ${statusInfo.class}`
        }, statusInfo.label);
        statusTd.appendChild(statusBadge);
        tr.appendChild(statusTd);

        // İşlemler
        const actionTd = Utils.createElement('td');
        const actionWrapper = Utils.createElement('div', { style: 'display: flex; gap: var(--spacing-xs);' });

        if (expense.status === 'PENDING') {
            const approveBtn = Utils.createElement('button', { class: 'btn btn-outline btn-sm' }, 'Onayla');
            approveBtn.addEventListener('click', () => approveExpense(expense.id));
            actionWrapper.appendChild(approveBtn);

            const rejectBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'Reddet');
            rejectBtn.addEventListener('click', () => rejectExpense(expense.id));
            actionWrapper.appendChild(rejectBtn);
        } else {
            const viewBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'Görüntüle');
            viewBtn.addEventListener('click', () => viewExpense(expense.id));
            actionWrapper.appendChild(viewBtn);
        }

        actionTd.appendChild(actionWrapper);
        tr.appendChild(actionTd);

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Yeni masraf modal
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

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Yeni Masraf'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', createExpense);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Masraf Tipi
    const typeGroup = Utils.createElement('div', { class: 'form-group' });
    typeGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Masraf Tipi'));
    const typeSelect = Utils.createElement('select', { class: 'form-select', name: 'expense_type', required: '' });
    Object.entries(EXPENSE_TYPES).forEach(([value, label]) => {
        typeSelect.appendChild(Utils.createElement('option', { value }, label));
    });
    typeGroup.appendChild(typeSelect);
    body.appendChild(typeGroup);

    // Proje
    const projectGroup = Utils.createElement('div', { class: 'form-group' });
    projectGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Proje'));
    const projectSelect = Utils.createElement('select', { class: 'form-select', name: 'project_id' });
    projectSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz (Opsiyonel)'));
    projects.forEach(p => {
        projectSelect.appendChild(Utils.createElement('option', { value: p.id }, `${p.project_code} - ${p.name}`));
    });
    projectGroup.appendChild(projectSelect);
    body.appendChild(projectGroup);

    // Tarih ve Tutar
    const row1 = Utils.createElement('div', { class: 'form-row' });

    const dateGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    dateGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Tarih'));
    const dateInput = Utils.createElement('input', { type: 'date', class: 'form-input', name: 'expense_date', required: '' });
    dateInput.value = new Date().toISOString().split('T')[0];
    dateGroup.appendChild(dateInput);
    row1.appendChild(dateGroup);

    const amountGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    amountGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Tutar'));
    amountGroup.appendChild(Utils.createElement('input', { type: 'number', step: '0.01', class: 'form-input', name: 'amount', required: '' }));
    row1.appendChild(amountGroup);

    body.appendChild(row1);

    // Para Birimi
    const currencyGroup = Utils.createElement('div', { class: 'form-group' });
    currencyGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Para Birimi'));
    const currencySelect = Utils.createElement('select', { class: 'form-select', name: 'currency' });
    ['TRY', 'USD', 'EUR'].forEach(c => {
        currencySelect.appendChild(Utils.createElement('option', { value: c }, c));
    });
    currencyGroup.appendChild(currencySelect);
    body.appendChild(currencyGroup);

    // Açıklama
    const descGroup = Utils.createElement('div', { class: 'form-group' });
    descGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Açıklama'));
    descGroup.appendChild(Utils.createElement('textarea', { class: 'form-input', name: 'description', rows: '3', required: '' }));
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

/**
 * Modal kapat
 */
function closeModal() {
    document.getElementById('modal-container').innerHTML = '';
    document.body.style.overflow = '';
}

/**
 * Masraf oluştur
 */
async function createExpense(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) {
            if (key === 'project_id') {
                data[key] = parseInt(value);
            } else if (key === 'amount') {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }
    });

    try {
        await API.expenses.create(data);
        closeModal();
        Utils.toast.success('Masraf kaydedildi');
        loadExpenses();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Masraf onayla
 */
async function approveExpense(id) {
    if (!confirm('Masraf onaylansın mı?')) return;
    try {
        await API.expenses.approve(id);
        Utils.toast.success('Masraf onaylandı');
        loadExpenses();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Masraf reddet
 */
async function rejectExpense(id) {
    const reason = prompt('Red nedeni:');
    if (!reason) return;

    try {
        await API.post(`/expenses/${id}/reject`, { rejection_reason: reason });
        Utils.toast.info('Masraf reddedildi');
        loadExpenses();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Masraf görüntüle
 */
async function viewExpense(id) {
    try {
        const expense = await API.expenses.get(id);

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

        const header = Utils.createElement('div', { class: 'modal-header' });
        header.appendChild(Utils.createElement('h3', {}, 'Masraf Detayı'));
        const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
        closeBtn.addEventListener('click', closeModal);
        header.appendChild(closeBtn);
        modal.appendChild(header);

        const body = Utils.createElement('div', { class: 'modal-body' });

        const details = [
            ['Tip', EXPENSE_TYPES[expense.expense_type] || expense.expense_type],
            ['Tarih', new Date(expense.expense_date).toLocaleDateString('tr-TR')],
            ['Tutar', `${parseFloat(expense.amount).toLocaleString('tr-TR')} ${expense.currency || 'TRY'}`],
            ['Proje', expense.project_code || '-'],
            ['Açıklama', expense.description],
            ['Durum', expense.status]
        ];

        if (expense.rejection_reason) {
            details.push(['Red Nedeni', expense.rejection_reason]);
        }

        details.forEach(([label, value]) => {
            const row = Utils.createElement('div', { style: 'display: flex; padding: var(--spacing-xs) 0; border-bottom: 1px solid var(--border-color);' });
            row.appendChild(Utils.createElement('strong', { style: 'flex: 1;' }, label));
            row.appendChild(Utils.createElement('span', { style: 'flex: 2;' }, value || '-'));
            body.appendChild(row);
        });

        modal.appendChild(body);

        const footer = Utils.createElement('div', { class: 'modal-footer' });
        const closeFooterBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'Kapat');
        closeFooterBtn.addEventListener('click', closeModal);
        footer.appendChild(closeFooterBtn);
        modal.appendChild(footer);

        overlay.appendChild(modal);
        modalContainer.appendChild(overlay);
    } catch (error) {
        Utils.toast.error('Masraf yüklenemedi: ' + error.message);
    }
}

// Global fonksiyonlar
window.openCreateModal = openCreateModal;
window.closeModal = closeModal;
window.loadExpenses = loadExpenses;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', async function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }
    await loadInitialData();
    loadExpenses();
});
